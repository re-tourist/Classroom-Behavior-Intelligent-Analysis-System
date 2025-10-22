from pathlib import Path
from typing import Any

import cv2
import numpy as np

try:
    from ultralytics import YOLO
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "Ultralytics 未安装或不可用，请先安装 'ultralytics' 依赖。"
    ) from e


class Yolov8Inference:
    def __init__(
        self,
        weights: str | Path = "yolov8n.pt",
        device: str = "",
        imgsz: int = 640,
        conf: float = 0.25,
        iou: float = 0.45,
        classes: list[int] | None = None,
        max_det: int = 1000,
        half: bool = False,
    ) -> None:
        self.model = YOLO(str(weights))
        self.device = device
        self.imgsz = imgsz
        self.conf = conf
        self.iou = iou
        self.classes = classes
        self.max_det = max_det
        self.half = half
        self.names = self.model.names

    @staticmethod
    def _load_image_rgb(img: str | Path | np.ndarray) -> np.ndarray:
        if isinstance(img, (str, Path)):
            bgr = cv2.imread(str(img))
            if bgr is None:
                raise FileNotFoundError(f"无法读取图像: {img}")
            return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        elif isinstance(img, np.ndarray):
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            return img
        else:
            raise TypeError("img 必须是路径或 numpy 数组")

    def _predict(self, bgr: np.ndarray):
        return self.model.predict(
            source=bgr,
            imgsz=self.imgsz,
            conf=self.conf,
            iou=self.iou,
            device=self.device,
            half=self.half,
            classes=self.classes,
            max_det=self.max_det,
            verbose=False,
        )

    def predict_image(
        self, img: str | Path | np.ndarray, annotate: bool = True
    ) -> dict[str, Any]:
        rgb = self._load_image_rgb(img)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        results = self._predict(bgr)
        r = results[0]
        detections: list[dict[str, Any]] = []
        for i in range(len(r.boxes)):
            b = r.boxes[i]
            xyxy = b.xyxy[0].cpu().numpy().astype(int).tolist()
            conf = float(b.conf[0])
            cls_id = int(b.cls[0])
            name = (
                self.names.get(cls_id, str(cls_id))
                if isinstance(self.names, dict)
                else self.names[cls_id]
            )
            detections.append({"xyxy": xyxy, "conf": conf, "cls": cls_id, "name": name})

        annotated_rgb = None
        if annotate:
            anno_bgr = r.plot()
            annotated_rgb = cv2.cvtColor(anno_bgr, cv2.COLOR_BGR2RGB)

        return {"image": rgb, "annotated": annotated_rgb, "detections": detections}

    def predict_video(
        self,
        video_path: str | Path,
        max_frames: int | None = None,
        sample_stride: int = 1,
        annotate: bool = True,
    ) -> dict[str, Any]:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise FileNotFoundError(f"无法打开视频: {video_path}")

        frame_idx = 0
        frames: list[np.ndarray] = []
        annos: list[np.ndarray] = []
        per_frame: list[list[dict[str, Any]]] = []

        while True:
            ret, bgr = cap.read()
            if not ret:
                break
            if frame_idx % sample_stride != 0:
                frame_idx += 1
                continue

            results = self._predict(bgr)
            r = results[0]
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

            detections: list[dict[str, Any]] = []
            for i in range(len(r.boxes)):
                b = r.boxes[i]
                xyxy = b.xyxy[0].cpu().numpy().astype(int).tolist()
                conf = float(b.conf[0])
                cls_id = int(b.cls[0])
                name = (
                    self.names.get(cls_id, str(cls_id))
                    if isinstance(self.names, dict)
                    else self.names[cls_id]
                )
                detections.append(
                    {"xyxy": xyxy, "conf": conf, "cls": cls_id, "name": name}
                )

            im_anno = None
            if annotate:
                anno_bgr = r.plot()
                im_anno = cv2.cvtColor(anno_bgr, cv2.COLOR_BGR2RGB)

            frames.append(rgb)
            annos.append(im_anno)
            per_frame.append(detections)

            frame_idx += 1
            if max_frames is not None and len(frames) >= max_frames:
                break

        cap.release()
        return {
            "frames": frames,
            "annotated_frames": annos if annotate else None,
            "per_frame_detections": per_frame,
        }
