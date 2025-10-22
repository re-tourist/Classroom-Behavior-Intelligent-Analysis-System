from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch


class Yolov5Inference:
    """
    Lightweight YOLOv5 inference wrapper.

    It prefers a local YOLOv5 repo if available (for offline usage),
    and falls back to the official torch.hub repo.
    """

    def __init__(
        self,
        weights: str | Path,
        repo_dir: str | Path | None = None,
        device: str = "",
        imgsz: int = 640,
        conf: float = 0.25,
        iou: float = 0.45,
        classes: list[int] | None = None,
        max_det: int = 1000,
    ) -> None:
        self.imgsz = imgsz
        self.device = device
        self._model = self._load_model(weights, repo_dir)
        # Configure detection hyper-params
        self._model.conf = conf
        self._model.iou = iou
        self._model.max_det = max_det
        self._model.classes = classes  # e.g. [0] for person-only
        if device:
            self._model.to(device)

    def _load_model(self, weights: str | Path, repo_dir: str | Path | None):
        weights = str(weights)
        if repo_dir:
            repo_dir = Path(repo_dir)
            if repo_dir.exists():
                try:
                    return torch.hub.load(
                        str(repo_dir), "custom", path=weights, source="local"
                    )
                except Exception:
                    pass
        # Fallback to remote hub (requires internet)
        return torch.hub.load("ultralytics/yolov5", "custom", path=weights)

    @staticmethod
    def _ensure_rgb(img: str | np.ndarray) -> np.ndarray:
        if isinstance(img, str):
            bgr = cv2.imread(img)
            if bgr is None:
                raise FileNotFoundError(f"Image not found: {img}")
            return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        # Assume caller passes RGB np.ndarray when not a path
        if img.ndim == 3 and img.shape[2] == 3:
            return img
        raise ValueError("Unsupported image format for YOLOv5 inference.")

    def predict_image(
        self,
        img: str | np.ndarray,
        annotate: bool = True,
    ) -> dict[str, Any]:
        """
        Run detection on a single image.

        Returns dict with keys: `image`, `detections`, `annotated` (if annotate).
        - `detections` is a list of dicts with keys: xyxy, conf, cls, name
        - `image` and `annotated` are RGB numpy arrays
        """
        img_rgb = self._ensure_rgb(img)
        results = self._model(img_rgb, size=self.imgsz)
        df = results.pandas().xyxy[0]
        detections: list[dict[str, Any]] = []
        for _, row in df.iterrows():
            xmin = int(row.get("xmin", row.get("left", 0)))
            ymin = int(row.get("ymin", row.get("top", 0)))
            xmax = int(row.get("xmax", row.get("right", 0)))
            ymax = int(row.get("ymax", row.get("bottom", 0)))
            detections.append(
                {
                    "xyxy": [xmin, ymin, xmax, ymax],
                    "conf": float(row["confidence"]),
                    "cls": int(row["class"]),
                    "name": str(row.get("name", row.get("class", ""))),
                }
            )
        annotated = None
        if annotate:
            # results.render() modifies internal images list (BGR). Convert to RGB.
            _ = results.render()
            if hasattr(results, "imgs") and results.imgs:
                annotated_bgr = results.imgs[0]
                annotated = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
        return {
            "image": img_rgb,
            "detections": detections,
            "annotated": annotated,
        }

    def predict_video_frame(
        self, frame_rgb: np.ndarray, annotate: bool = False
    ) -> dict[str, Any]:
        """Convenience wrapper for passing RGB frames from a video pipeline."""
        return self.predict_image(frame_rgb, annotate=annotate)
