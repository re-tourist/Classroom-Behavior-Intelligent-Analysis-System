from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import numpy as np

from ..services.face_ops import FacePipeline
from .head_rate import HeadUpRateAnalyzer


class IndividualBehaviorAnalyzer:
    def __init__(
        self,
        window_size: int = 15,
        head_region_ratio: float = 0.2,
        brightness_threshold: float = 0.35,
        face_gallery_dir: Path = Path("data/face_gallery"),
        face_model_path: Path = Path("output/face_lbph.xml"),
        face_labels_path: Path = Path("output/face_labels.json"),
        unknown_threshold: float = 60.0,
        enable_face: bool = True,
    ) -> None:
        self.overall = HeadUpRateAnalyzer(
            window_size, head_region_ratio, brightness_threshold
        )
        self.face = (
            FacePipeline(
                gallery_dir=face_gallery_dir,
                model_path=face_model_path,
                labels_path=face_labels_path,
                unknown_threshold=unknown_threshold,
            )
            if enable_face
            else None
        )
        self.enable_face = enable_face
        self.histories: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=window_size)
        )

    def analyze_frame(
        self, img_rgb: np.ndarray, detections: list[dict[str, Any]], frame_id: int
    ) -> dict[str, Any]:
        persons = [
            d for d in detections if d.get("name") == "person" or d.get("cls") == 0
        ]
        records: list[dict[str, Any]] = []

        for idx, p in enumerate(persons):
            box = p["xyxy"]
            head_cls = self.overall._classify_head(img_rgb, box)
            if not self.face:
                identity = f"Unknown_{frame_id}_{idx}"
            else:
                identity = self.face.assign_identity(img_rgb, box)
                if identity == "Unknown":
                    identity = f"Unknown_{frame_id}_{idx}"
            rate = 1.0 if head_cls == "up" else 0.0
            self.histories[identity].append(rate)
            smooth = (
                float(np.mean(self.histories[identity]))
                if self.histories[identity]
                else rate
            )
            records.append(
                {
                    "frame": frame_id,
                    "id": identity,
                    "head": head_cls,
                    "head_up_rate": rate,
                    "head_up_rate_smooth": smooth,
                    "xyxy": box,
                }
            )

        overall_stats = self.overall.analyze_frame(img_rgb, detections)
        return {
            "frame": frame_id,
            "overall": overall_stats,
            "individuals": records,
            "identities_count": len(self.histories),
        }

    @staticmethod
    def export_csv_per_person(path: Path, rows: list[dict[str, Any]]) -> None:
        import csv

        path.parent.mkdir(parents=True, exist_ok=True)
        keys = ["frame", "id", "head", "head_up_rate", "head_up_rate_smooth"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for r in rows:
                writer.writerow({k: r.get(k) for k in keys})
