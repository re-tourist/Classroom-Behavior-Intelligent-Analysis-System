import argparse
from pathlib import Path

import yaml

from .analytics.individual_behavior import IndividualBehaviorAnalyzer
from .services.yolov5_inference import Yolov5Inference

APP_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = APP_ROOT / "configs" / "config.yaml"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def default_repo_dir() -> Path:
    # Try to use local repo: <group_project>/head_up_rate_detection_project/yolov5
    p = (
        Path(__file__).resolve().parents[3]
        / "head_up_rate_detection_project"
        / "yolov5"
    )
    return p if p.exists() else Path()


def collect_images(images_dir: Path) -> list[Path]:
    if images_dir.exists():
        return sorted(
            [
                p
                for p in images_dir.rglob("*")
                if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
            ]
        )
    return []


def main():
    cfg = load_config()
    inf_v8 = cfg.get("inference", {})
    face_cfg = cfg.get("face", {})
    v5_cfg = cfg.get("inference_v5", {})

    parser = argparse.ArgumentParser(
        description="Identity behavior demo over image directory"
    )
    parser.add_argument(
        "--images_dir",
        type=str,
        default=str(
            APP_ROOT
            / "data"
            / "SCBehavior_Dataset"
            / "SCBehavior_YOLO"
            / "images"
            / "val"
        ),
    )
    parser.add_argument(
        "--weights", type=str, default=v5_cfg.get("weights", "yolov5s.pt")
    )
    parser.add_argument(
        "--repo_dir", type=str, default=str(v5_cfg.get("repo_dir", default_repo_dir()))
    )
    parser.add_argument(
        "--output_csv", type=str, default=str(APP_ROOT / "output" / "identity_demo.csv")
    )
    parser.add_argument(
        "--no_face",
        action="store_true",
        help="Disable face recognition and use anonymous IDs",
    )
    args = parser.parse_args()

    images_dir = Path(args.images_dir)
    imgs = collect_images(images_dir)
    if not imgs:
        fallback = APP_ROOT / "data" / "samples"
        print(f"[warn] No images found under {images_dir}. Falling back to {fallback}.")
        images_dir = fallback
        imgs = collect_images(images_dir)
        if not imgs:
            print("[error] No images available to process.")
            return

    repo_dir = Path(args.repo_dir)
    if not repo_dir.exists():
        repo_dir = None

    # Init detector
    det = Yolov5Inference(
        weights=args.weights,
        repo_dir=repo_dir,
        device=inf_v8.get("device", ""),
        imgsz=int(inf_v8.get("imgsz", 640)),
        conf=float(inf_v8.get("conf", 0.25)),
        iou=float(inf_v8.get("iou", 0.45)),
        classes=v5_cfg.get("classes", [0]),  # person-only by default
        max_det=int(inf_v8.get("max_det", 1000)),
    )

    # Init analyzer
    analyzer = IndividualBehaviorAnalyzer(
        window_size=int(cfg.get("analytics", {}).get("window_size", 15)),
        head_region_ratio=float(cfg.get("analytics", {}).get("head_region_ratio", 0.2)),
        brightness_threshold=float(
            cfg.get("analytics", {}).get("brightness_threshold", 0.35)
        ),
        face_gallery_dir=APP_ROOT / face_cfg.get("gallery_dir", "data/face_gallery"),
        face_model_path=APP_ROOT / face_cfg.get("model_path", "output/face_lbph.xml"),
        face_labels_path=APP_ROOT
        / face_cfg.get("labels_path", "output/face_labels.json"),
        unknown_threshold=float(face_cfg.get("unknown_threshold", 60.0)),
        enable_face=(not args.no_face),
    )

    rows: list[dict] = []
    for i, img_path in enumerate(imgs, start=1):
        res = det.predict_image(str(img_path), annotate=False)
        stats = analyzer.analyze_frame(res["image"], res["detections"], frame_id=i)
        rows.extend(stats["individuals"])
        print(
            f"Processed {img_path.name}: {len(stats['individuals'])} identities, overall rate={stats['overall']['head_up_rate']:.2f}"
        )

    out_csv = Path(args.output_csv)
    IndividualBehaviorAnalyzer.export_csv_per_person(out_csv, rows)
    print(f"Saved per-identity CSV to: {out_csv}")


if __name__ == "__main__":
    main()
