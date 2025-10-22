from pathlib import Path

import cv2
import numpy as np
import yaml
from analytics.head_rate import HeadUpRateAnalyzer
from PySide6 import QtCore, QtGui, QtWidgets
from services.yolov8_inference import Yolov8Inference


def rgb_to_qimage(rgb: np.ndarray) -> QtGui.QImage:
    h, w, ch = rgb.shape
    bytes_per_line = ch * w
    return QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)


class DropArea(QtWidgets.QLabel):
    file_dropped = QtCore.Signal(str)

    def __init__(self) -> None:
        super().__init__("将图片或视频拖拽到此处")
        self.setAcceptDrops(True)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(720, 400)
        self.setStyleSheet(
            """
            QLabel { background: #0f1115; color:#cfd8dc; border:2px dashed #3a4b5c; border-radius:10px; }
            """
        )

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        if path:
            self.file_dropped.emit(path)


class ImageWorker(QtCore.QThread):
    image_ready = QtCore.Signal(QtGui.QImage)
    metrics_ready = QtCore.Signal(dict)
    finished = QtCore.Signal()

    def __init__(
        self, infer: Yolov8Inference, analyzer: HeadUpRateAnalyzer, image_path: str
    ) -> None:
        super().__init__()
        self.infer = infer
        self.analyzer = analyzer
        self.image_path = image_path

    def run(self) -> None:
        try:
            out = self.infer.predict_image(self.image_path, annotate=True)
            qimg = (
                rgb_to_qimage(out["annotated"])
                if out.get("annotated") is not None
                else rgb_to_qimage(out["image"])
            )
            metrics = self.analyzer.analyze_frame(out["image"], out["detections"])
            metrics["frame"] = 0
            self.image_ready.emit(qimg)
            self.metrics_ready.emit(metrics)
        finally:
            self.finished.emit()


class VideoWorker(QtCore.QThread):
    frame_ready = QtCore.Signal(QtGui.QImage)
    metrics_ready = QtCore.Signal(dict)
    finished = QtCore.Signal()

    def __init__(
        self,
        infer: Yolov8Inference,
        analyzer: HeadUpRateAnalyzer,
        source: str,
        sample_stride: int = 1,
    ) -> None:
        super().__init__()
        self.infer = infer
        self.analyzer = analyzer
        self.source = source
        self.sample_stride = max(1, int(sample_stride))
        self._running = True
        self._frame_id = 0

    def stop(self) -> None:
        self._running = False

    def run(self) -> None:
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            self.finished.emit()
            return
        while self._running:
            ret, bgr = cap.read()
            if not ret:
                break
            if self._frame_id % self.sample_stride != 0:
                self._frame_id += 1
                continue
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            out = self.infer.predict_image(rgb, annotate=True)
            qimg = (
                rgb_to_qimage(out["annotated"])
                if out.get("annotated") is not None
                else rgb_to_qimage(out["image"])
            )
            metrics = self.analyzer.analyze_frame(out["image"], out["detections"])
            metrics["frame"] = self._frame_id
            self.frame_ready.emit(qimg)
            self.metrics_ready.emit(metrics)
            self._frame_id += 1
        cap.release()
        self.finished.emit()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app_root: Path) -> None:
        super().__init__()
        self.setWindowTitle("Classroom Behavior Detection")
        self.resize(1280, 800)
        self.app_root = app_root
        self.config = self._load_config()

        self.worker: QtCore.QThread | None = None
        self._rows: list[dict] = []
        self._last_annotated: QtGui.QImage | None = None
        self._last_video_path: str | None = None

        self._build_ui()
        self._apply_style()
        self.statusBar().showMessage("就绪：上传图片或视频以开始推理")

    def _load_config(self) -> dict:
        cfg_path = self.app_root / "configs" / "config.yaml"
        if cfg_path.exists():
            with open(cfg_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}

    def _build_ui(self) -> None:
        # Toolbar
        toolbar = QtWidgets.QToolBar("Main")
        toolbar.setIconSize(QtCore.QSize(18, 18))
        self.addToolBar(toolbar)

        self.act_upload_image = QtGui.QAction("上传图片", self)
        self.act_upload_video = QtGui.QAction("上传视频", self)
        self.act_start_video = QtGui.QAction("开始视频推理", self)
        self.act_stop = QtGui.QAction("停止", self)
        self.act_save_image = QtGui.QAction("保存标注图", self)
        self.act_export_csv = QtGui.QAction("导出CSV", self)
        self.act_export_json = QtGui.QAction("导出JSON", self)
        self.act_select_weights = QtGui.QAction("选择模型权重", self)

        toolbar.addAction(self.act_upload_image)
        toolbar.addAction(self.act_upload_video)
        toolbar.addSeparator()
        toolbar.addAction(self.act_start_video)
        toolbar.addAction(self.act_stop)
        toolbar.addSeparator()
        toolbar.addAction(self.act_save_image)
        toolbar.addSeparator()
        toolbar.addAction(self.act_export_csv)
        toolbar.addAction(self.act_export_json)
        toolbar.addSeparator()
        toolbar.addAction(self.act_select_weights)

        # Central split layout
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        hsplit = QtWidgets.QSplitter(QtCore.Qt.Horizontal, central)
        layout = QtWidgets.QHBoxLayout(central)
        layout.addWidget(hsplit)

        # Left: display area with drop zone
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)
        self.drop_area = DropArea()
        self.display_label = QtWidgets.QLabel()
        self.display_label.setAlignment(QtCore.Qt.AlignCenter)
        self.display_label.setMinimumSize(720, 405)
        self.display_label.setStyleSheet(
            "background:#0b0d10; color:#e0e0e0; border:1px solid #2a3440; border-radius:6px;"
        )
        hint = QtWidgets.QLabel("或使用上方工具栏按钮选择文件")
        hint.setAlignment(QtCore.Qt.AlignCenter)
        hint.setStyleSheet("color:#8fa2b3; padding:6px;")
        left_layout.addWidget(self.drop_area)
        left_layout.addWidget(hint)
        left_layout.addWidget(self.display_label)

        # Right: stats + params
        right = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right)

        stats_box = QtWidgets.QGroupBox("统计")
        stats_layout = QtWidgets.QFormLayout(stats_box)
        self.lbl_persons = QtWidgets.QLabel("0")
        self.lbl_up = QtWidgets.QLabel("0")
        self.lbl_down = QtWidgets.QLabel("0")
        self.lbl_rate = QtWidgets.QLabel("0.00")
        self.lbl_rate_s = QtWidgets.QLabel("0.00")
        stats_layout.addRow("人数", self.lbl_persons)
        stats_layout.addRow("抬头", self.lbl_up)
        stats_layout.addRow("低头", self.lbl_down)
        stats_layout.addRow("抬头率", self.lbl_rate)
        stats_layout.addRow("平滑抬头率", self.lbl_rate_s)

        params_box = QtWidgets.QGroupBox("参数")
        params_layout = QtWidgets.QFormLayout(params_box)
        self.edit_weights = QtWidgets.QLineEdit(
            str(
                ((self.config or {}).get("inference", {}) or {}).get(
                    "weights", "yolov8n.pt"
                )
            )
        )
        btn_browse_w = QtWidgets.QPushButton("浏览")
        w_row = QtWidgets.QHBoxLayout()
        w_row.addWidget(self.edit_weights)
        w_row.addWidget(btn_browse_w)
        w_wrap = QtWidgets.QWidget()
        w_wrap.setLayout(w_row)
        params_layout.addRow("模型权重", w_wrap)

        self.sld_conf = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sld_conf.setRange(0, 100)
        self.sld_conf.setValue(
            int(
                float(
                    ((self.config or {}).get("inference", {}) or {}).get("conf", 0.25)
                )
                * 100
            )
        )
        self.lbl_conf = QtWidgets.QLabel(f"{self.sld_conf.value() / 100:.2f}")
        conf_row = QtWidgets.QHBoxLayout()
        conf_row.addWidget(self.sld_conf)
        conf_row.addWidget(self.lbl_conf)
        conf_wrap = QtWidgets.QWidget()
        conf_wrap.setLayout(conf_row)
        params_layout.addRow("置信度", conf_wrap)

        self.sld_iou = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sld_iou.setRange(0, 100)
        self.sld_iou.setValue(
            int(
                float(((self.config or {}).get("inference", {}) or {}).get("iou", 0.45))
                * 100
            )
        )
        self.lbl_iou = QtWidgets.QLabel(f"{self.sld_iou.value() / 100:.2f}")
        iou_row = QtWidgets.QHBoxLayout()
        iou_row.addWidget(self.sld_iou)
        iou_row.addWidget(self.lbl_iou)
        iou_wrap = QtWidgets.QWidget()
        iou_wrap.setLayout(iou_row)
        params_layout.addRow("NMS IoU", iou_wrap)

        self.spn_imgsz = QtWidgets.QSpinBox()
        self.spn_imgsz.setRange(320, 1280)
        self.spn_imgsz.setValue(
            int(((self.config or {}).get("inference", {}) or {}).get("imgsz", 640))
        )
        params_layout.addRow("图像尺寸", self.spn_imgsz)

        self.chk_person_only = QtWidgets.QCheckBox("仅人物类")
        default_classes = ((self.config or {}).get("inference", {}) or {}).get(
            "classes", None
        )
        self.chk_person_only.setChecked(default_classes == [0])
        params_layout.addRow("类别过滤", self.chk_person_only)

        right_layout.addWidget(stats_box)
        right_layout.addWidget(params_box)
        right_layout.addStretch(1)

        hsplit.addWidget(left)
        hsplit.addWidget(right)
        hsplit.setSizes([900, 380])

        # signals
        self.act_upload_image.triggered.connect(self._on_upload_image)
        self.act_upload_video.triggered.connect(self._on_upload_video)
        self.act_start_video.triggered.connect(self._on_start_video)
        self.act_stop.triggered.connect(self._on_stop)
        self.act_save_image.triggered.connect(self._on_save_annotated)
        self.act_export_csv.triggered.connect(self._on_export_csv)
        self.act_export_json.triggered.connect(self._on_export_json)
        self.act_select_weights.triggered.connect(lambda: self._browse_weights())
        btn_browse_w.clicked.connect(self._browse_weights)
        self.drop_area.file_dropped.connect(self._on_drop_file)
        self.sld_conf.valueChanged.connect(
            lambda v: self.lbl_conf.setText(f"{v / 100:.2f}")
        )
        self.sld_iou.valueChanged.connect(
            lambda v: self.lbl_iou.setText(f"{v / 100:.2f}")
        )

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow { background: #121418; }
            QToolBar { background: #1b2026; border-bottom: 1px solid #2a3440; }
            QToolButton { color: #e0e0e0; padding:6px 10px; }
            QToolButton:hover { background:#28313a; border-radius:4px; }
            QLabel { color: #d0d7de; font-size: 14px; }
            QGroupBox { color: #cfd8dc; border:1px solid #2a3440; border-radius:6px; margin-top: 8px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 4px; }
            QLineEdit { background:#0f1115; color:#e0e0e0; border:1px solid #2a3440; border-radius:4px; padding:4px; }
            QPushButton { background:#2a3440; color:#e0e0e0; border:0; padding:6px 10px; border-radius:4px; }
            QPushButton:hover { background:#354252; }
            QSlider::groove:horizontal { background:#2a3440; height:6px; border-radius:3px; }
            QSlider::handle:horizontal { background:#607d8b; width:14px; margin:-4px 0; border-radius:7px; }
            QSpinBox { background:#0f1115; color:#e0e0e0; border:1px solid #2a3440; border-radius:4px; padding:2px; }
            QCheckBox { color:#d0d7de; }
            """
        )

    def _browse_weights(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "选择权重文件", str(self.app_root / "data"), "模型 (*.pt *.torch)"
        )
        if path:
            self.edit_weights.setText(path)

    def _build_infer(self) -> Yolov8Inference:
        classes = [0] if self.chk_person_only.isChecked() else None
        return Yolov8Inference(
            weights=self.edit_weights.text().strip() or "yolov8n.pt",
            device=str(
                ((self.config or {}).get("inference", {}) or {}).get("device", "")
            ),
            imgsz=int(self.spn_imgsz.value()),
            conf=float(self.sld_conf.value()) / 100.0,
            iou=float(self.sld_iou.value()) / 100.0,
            classes=classes,
            max_det=int(
                ((self.config or {}).get("inference", {}) or {}).get("max_det", 1000)
            ),
            half=bool(
                ((self.config or {}).get("inference", {}) or {}).get("half", False)
            ),
        )

    def _build_analyzer(self) -> HeadUpRateAnalyzer:
        a_cfg = (self.config or {}).get("analytics", {})
        return HeadUpRateAnalyzer(
            window_size=int(a_cfg.get("window_size", 15)),
            head_region_ratio=float(a_cfg.get("head_region_ratio", 0.2)),
            brightness_threshold=float(a_cfg.get("brightness_threshold", 0.35)),
        )

    def _on_drop_file(self, path: str) -> None:
        if self._is_image(path):
            self._run_image(path)
        elif self._is_video(path):
            self._start_video(path)
        else:
            QtWidgets.QMessageBox.warning(
                self, "不支持的文件", "请上传图片或视频文件。"
            )

    def _on_upload_image(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "选择图片",
            str(self.app_root / "data"),
            "图片文件 (*.jpg *.jpeg *.png *.bmp)",
        )
        if path:
            self._run_image(path)

    def _on_upload_video(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "选择视频",
            str(self.app_root / "data"),
            "视频文件 (*.mp4 *.avi *.mov)",
        )
        if path:
            self._start_video(path)

    def _on_start_video(self) -> None:
        if self._last_video_path:
            self._start_video(self._last_video_path)
            return
        default_video = ((self.config or {}).get("ui", {}) or {}).get(
            "default_video", ""
        )
        if default_video:
            self._start_video(default_video)
        else:
            self._on_upload_video()

    def _run_image(self, path: str) -> None:
        self._rows = []
        infer = self._build_infer()
        analyzer = self._build_analyzer()
        self._set_running(False)
        self.worker = ImageWorker(infer, analyzer, path)
        self.worker.image_ready.connect(self._update_frame)
        self.worker.metrics_ready.connect(self._update_metrics)
        self.worker.finished.connect(
            lambda: self.statusBar().showMessage("图片推理完成")
        )
        self.worker.start()
        self.statusBar().showMessage("图片推理中…")

    def _start_video(self, path: str) -> None:
        self._last_video_path = path
        self._rows = []
        infer = self._build_infer()
        analyzer = self._build_analyzer()
        self._set_running(True)
        self.worker = VideoWorker(infer, analyzer, path, sample_stride=1)
        self.worker.frame_ready.connect(self._update_frame)
        self.worker.metrics_ready.connect(self._update_metrics)
        self.worker.finished.connect(
            lambda: self.statusBar().showMessage("视频推理完成")
        )
        self.worker.start()
        self.statusBar().showMessage("视频推理中…")

    def _set_running(self, running: bool) -> None:
        self.act_start_video.setEnabled(not running)
        self.act_stop.setEnabled(running)

    def _on_stop(self) -> None:
        if self.worker:
            if hasattr(self.worker, "stop"):
                self.worker.stop()  # type: ignore
            self.worker.wait()
            self.worker = None
            self.statusBar().showMessage("已停止")
            self._set_running(False)

    def _update_frame(self, qimg: QtGui.QImage) -> None:
        self._last_annotated = qimg
        pix = QtGui.QPixmap.fromImage(qimg)
        self.display_label.setPixmap(
            pix.scaled(
                self.display_label.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
        )

    def _update_metrics(self, m: dict) -> None:
        self.lbl_persons.setText(str(m.get("persons", 0)))
        self.lbl_up.setText(str(m.get("head_up", 0)))
        self.lbl_down.setText(str(m.get("head_down", 0)))
        self.lbl_rate.setText(f"{float(m.get('head_up_rate', 0.0)):.2f}")
        self.lbl_rate_s.setText(f"{float(m.get('head_up_rate_smooth', 0.0)):.2f}")
        self._rows.append(m)

    def _on_save_annotated(self) -> None:
        if not self._last_annotated:
            QtWidgets.QMessageBox.information(self, "提示", "暂无标注图可保存")
            return
        out, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "保存标注图",
            str(self.app_root / "data" / "annotated.png"),
            "PNG (*.png)",
        )
        if out:
            self._last_annotated.save(out)
            self.statusBar().showMessage(f"已保存: {out}")

    def _on_export_csv(self) -> None:
        if not self._rows:
            QtWidgets.QMessageBox.information(self, "提示", "暂无数据可导出")
            return
        out, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "保存CSV", str(self.app_root / "data" / "results.csv"), "CSV (*.csv)"
        )
        if out:
            HeadUpRateAnalyzer.export_csv(Path(out), self._rows)
            self.statusBar().showMessage(f"已导出: {out}")

    def _on_export_json(self) -> None:
        if not self._rows:
            QtWidgets.QMessageBox.information(self, "提示", "暂无数据可导出")
            return
        out, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "保存JSON",
            str(self.app_root / "data" / "results.json"),
            "JSON (*.json)",
        )
        if out:
            HeadUpRateAnalyzer.export_json(Path(out), self._rows[-1])
            self.statusBar().showMessage(f"已导出: {out}")

    @staticmethod
    def _is_image(path: str) -> bool:
        return Path(path).suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}

    @staticmethod
    def _is_video(path: str) -> bool:
        return Path(path).suffix.lower() in {".mp4", ".avi", ".mov", ".mkv"}
