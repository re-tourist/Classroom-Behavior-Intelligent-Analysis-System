from collections import deque
from pathlib import Path
from typing import Any

import cv2
import numpy as np


class HeadUpRateAnalyzer:
    def __init__(
        self,
        window_size: int = 15,
        head_region_ratio: float = 0.2,
        brightness_threshold: float = 0.35,
    ) -> None:
        self.window_size = window_size
        self.head_region_ratio = head_region_ratio
        self.brightness_threshold = brightness_threshold
        self._history = deque(maxlen=window_size)

    def _classify_head(self, img_rgb: np.ndarray, person_box: list[int]) -> str:
        x1, y1, x2, y2 = person_box
        h = max(1, y2 - y1)
        head_h = max(1, int(h * self.head_region_ratio))
        hx1, hy1, hx2, hy2 = x1, y1, x2, y1 + head_h
        roi = img_rgb[hy1:hy2, hx1:hx2]
        if roi.size == 0:
            return "unknown"
        hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
        v = hsv[:, :, 2].astype(np.float32) / 255.0
        score = float(v.mean())
        return "up" if score >= self.brightness_threshold else "down"

    def analyze_frame(
        self, img_rgb: np.ndarray, detections: list[dict[str, Any]]
    ) -> dict[str, Any]:
        persons = [
            d for d in detections if d.get("name") == "person" or d.get("cls") == 0
        ]
        head_up = 0
        head_down = 0
        for p in persons:
            cls = self._classify_head(img_rgb, p["xyxy"])
            if cls == "up":
                head_up += 1
            elif cls == "down":
                head_down += 1
        total = max(1, len(persons))
        rate = head_up / total
        self._history.append(rate)
        return {
            "persons": len(persons),
            "head_up": head_up,
            "head_down": head_down,
            "head_up_rate": rate,
            "head_up_rate_smooth": (
                float(np.mean(self._history)) if self._history else rate
            ),
        }

    @staticmethod
    def export_json(path: Path, data: dict[str, Any]) -> None:
        import json

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def export_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        import csv

        path.parent.mkdir(parents=True, exist_ok=True)
        keys = [
            "frame",
            "persons",
            "head_up",
            "head_down",
            "head_up_rate",
            "head_up_rate_smooth",
        ]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for r in rows:
                writer.writerow({k: r.get(k) for k in keys})
