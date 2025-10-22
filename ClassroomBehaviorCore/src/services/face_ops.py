from pathlib import Path

import cv2
import numpy as np


class FaceDetector:
    def __init__(self, scale_factor: float = 1.2, min_neighbors: int = 5):
        cascade_path = (
            Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
        )
        self._detector = cv2.CascadeClassifier(str(cascade_path))
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors

    def detect(self, img_gray: np.ndarray) -> list[tuple[int, int, int, int]]:
        faces = self._detector.detectMultiScale(
            img_gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            flags=cv2.CASCADE_SCALE_IMAGE,
            minSize=(30, 30),
        )
        return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]


class FaceRecognizer:
    """
    OpenCV LBPH-based face recognizer.

    - Trains using a gallery directory: gallery_dir/<person_name>/*.jpg
    - Saves model and label mapping to given paths
    """

    def __init__(
        self,
        gallery_dir: Path,
        model_path: Path,
        labels_path: Path,
        unknown_threshold: float = 60.0,
    ) -> None:
        self.gallery_dir = Path(gallery_dir)
        self.model_path = Path(model_path)
        self.labels_path = Path(labels_path)
        self.unknown_threshold = unknown_threshold

        # LBPH requires opencv-contrib-python
        self._model = cv2.face.LBPHFaceRecognizer_create()
        self._label_to_name: dict[int, str] = {}

        if self.model_path.exists() and self.labels_path.exists():
            self._load()
        else:
            self.train_from_gallery()

    def _load(self) -> None:
        self._model.read(str(self.model_path))
        import json

        with open(self.labels_path, encoding="utf-8") as f:
            self._label_to_name = json.load(f)

    def _save(self) -> None:
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        self.labels_path.parent.mkdir(parents=True, exist_ok=True)
        self._model.write(str(self.model_path))
        import json

        with open(self.labels_path, "w", encoding="utf-8") as f:
            json.dump(self._label_to_name, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _prep_face(
        img_gray: np.ndarray, size: tuple[int, int] = (128, 128)
    ) -> np.ndarray:
        face = cv2.resize(img_gray, size)
        face = cv2.equalizeHist(face)
        return face

    def train_from_gallery(self) -> None:
        faces: list[np.ndarray] = []
        labels: list[int] = []
        label_to_name: dict[int, str] = {}
        current_label = 0

        if not self.gallery_dir.exists():
            # No gallery; initialize with empty model.
            self._label_to_name = {}
            return

        for person_dir in sorted(self.gallery_dir.iterdir()):
            if not person_dir.is_dir():
                continue
            name = person_dir.name
            for img_path in person_dir.glob("*.jpg"):
                img = cv2.imread(str(img_path))
                if img is None:
                    continue
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                face_prep = self._prep_face(gray)
                faces.append(face_prep)
                labels.append(current_label)
            label_to_name[current_label] = name
            current_label += 1

        if faces and labels:
            self._model.train(faces, np.array(labels))
            self._label_to_name = label_to_name
            self._save()
        else:
            self._label_to_name = {}

    def recognize(self, img_gray_face: np.ndarray) -> tuple[str, float]:
        if not self._label_to_name:
            return "Unknown", float("inf")
        pred_label, confidence = self._model.predict(self._prep_face(img_gray_face))
        name = self._label_to_name.get(int(pred_label), "Unknown")
        if confidence > self.unknown_threshold:
            return "Unknown", confidence
        return name, confidence


class FacePipeline:
    """
    Combines face detection + recognition.
    """

    def __init__(
        self,
        gallery_dir: Path,
        model_path: Path,
        labels_path: Path,
        unknown_threshold: float = 60.0,
    ) -> None:
        self.detector = FaceDetector()
        self.recognizer = FaceRecognizer(
            gallery_dir, model_path, labels_path, unknown_threshold
        )

    def assign_identity(self, img_rgb: np.ndarray, person_xyxy: list[int]) -> str:
        x1, y1, x2, y2 = person_xyxy
        roi = img_rgb[max(0, y1) : max(0, y2), max(0, x1) : max(0, x2)]
        if roi.size == 0:
            return "Unknown"
        gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
        faces = self.detector.detect(gray)
        if not faces:
            return "Unknown"
        # choose largest face
        fx, fy, fw, fh = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]
        face_gray = gray[fy : fy + fh, fx : fx + fw]
        name, _ = self.recognizer.recognize(face_gray)
        return name
