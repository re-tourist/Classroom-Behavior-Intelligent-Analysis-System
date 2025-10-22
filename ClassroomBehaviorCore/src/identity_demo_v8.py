import argparse
from pathlib import Path

from src.analytics.individual_behavior import IndividualBehaviorAnalyzer
from src.services.yolov8_inference import Yolov8Inference


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
    parser = argparse.ArgumentParser(
        description="Identity behavior demo (YOLOv8) over image directory"
    )
    parser.add_argument(
        "--images_dir",
        type=str,
        default="./data/SCBehavior_Dataset/SCBehavior_YOLO/images/val",
    )
    parser.add_argument(
        "--weights", type=str, default="./output/scb_yolov8n/weights/best.pt"
    )
    parser.add_argument("--output_csv", type=str, default="./output/identity_v8.csv")
    parser.add_argument("--save_anno_dir", type=str, default="")
    parser.add_argument(
        "--no_face",
        action="store_true",
        help="Disable face recognition and use anonymous IDs",
    )
    args = parser.parse_args()

    images_dir = Path(args.images_dir)
    imgs = collect_images(images_dir)
    if not imgs:
        print(f"[error] No images under {images_dir}.")
        return

    # Init detector (person-only by default)
    det = Yolov8Inference(
        weights=args.weights,
        device="",
        imgsz=640,
        conf=0.25,
        iou=0.45,
        classes=[0],
        max_det=1000,
    )

    # Init analyzer
    analyzer = IndividualBehaviorAnalyzer(
        window_size=15,
        head_region_ratio=0.2,
        brightness_threshold=0.35,
        enable_face=(not args.no_face),
    )

    rows: list[dict] = []
    anno_dir = Path(args.save_anno_dir) if args.save_anno_dir else None
    if anno_dir:
        anno_dir.mkdir(parents=True, exist_ok=True)

    for i, img_path in enumerate(imgs, start=1):
        res = det.predict_image(str(img_path), annotate=bool(anno_dir))
        stats = analyzer.analyze_frame(res["image"], res["detections"], frame_id=i)
        rows.extend(stats["individuals"])

        if anno_dir and res.get("annotated") is not None:
            import cv2

            rgb = res["annotated"]
            bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            out_path = anno_dir / img_path.name
            cv2.imwrite(str(out_path), bgr)

        print(
            f"Processed {img_path.name}: {len(stats['individuals'])} identities, overall={stats['overall']['head_up_rate']:.2f}"
        )

    out_csv = Path(args.output_csv)
    IndividualBehaviorAnalyzer.export_csv_per_person(out_csv, rows)
    print(f"Saved per-identity CSV to: {out_csv}")


if __name__ == "__main__":
    main()
