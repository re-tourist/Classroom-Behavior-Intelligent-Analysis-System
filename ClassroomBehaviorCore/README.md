# ClassroomBehaviorDetection

基于 YOLOv8 的课堂行为（抬头率）检测与可视化桌面应用。以更合理的项目结构重整原有 `head_up_rate_detection_project`，并提供更精致的 PyQt 界面与统一的推理/分析模块。

## 功能概览
- 使用 YOLOv8 进行人物检测（默认 `yolov8n.pt`）
- 基于头部区域亮度的抬头率分析（滑动窗口平滑）
- PyQt 桌面应用（演示模式）：上传图片或视频进行推理，实时叠加标注与统计面板，支持导出 CSV/JSON

## 项目结构
```
ClassroomBehaviorDetection/
├── README.md
├── requirements.txt
├── configs/
│   └── config.yaml
├── assets/
│   └── README_assets.md
├── data/
│   └── README.md
└── src/
    ├── app.py
    ├── analytics/
    │   └── head_rate.py
    ├── services/
    │   └── yolov8_inference.py
    └── ui/
        └── main_window.py
```

## 环境准备
1. 安装依赖（建议 Python 3.9+）：
   ```bash
   pip install -r requirements.txt
   ```
2. 如需 GPU 加速，请先安装匹配 CUDA 的 `torch` 版本，再安装 `ultralytics`。

## 运行
```bash
cd d:\homework_for_cs\Software Engineering\group_project\ClassroomBehaviorDetection
python src/app.py
```

## 配置与模型
- 配置文件：`configs/config.yaml`
- 默认模型：`yolov8n.pt`
- 可在界面中上传图片或视频并推理，支持导出结果。

## 数据
- 请将数据集或示例视频放在 `data/` 目录下（详见 `data/README.md`）。
- 如需复用原项目 `datasets/judge_head`，建议手动复制到 `ClassroomBehaviorDetection/data/judge_head`。

## 常见问题
- 若推理报错模型缺失：下载或放置 `yolov8n.pt` 到可访问路径，或在配置中修改为绝对路径。