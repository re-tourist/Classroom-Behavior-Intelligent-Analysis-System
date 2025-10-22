# 项目部署、训练与测试指南（基于 ClassroomBehaviorDetection 根目录的相对路径）

本指南将所有命令与路径统一为相对路径，根目录以 `ClassroomBehaviorDetection` 为基准。

## 1. 环境配置
```powershell
# 进入项目根目录
cd ClassroomBehaviorDetection

# 建议使用 venv
python -m venv .venv
.venv\Scripts\activate

# 升级 pip
python -m pip install --upgrade pip

# 安装项目依赖（含 ultralytics、opencv-contrib-python 等）
pip install -r requirements.txt
```

## 2. 数据集（SCB / YOLO 结构）
目录结构示例：
```
./data/SCBehavior_Dataset/SCBehavior_YOLO/
  images/train/*.jpg
  images/val/*.jpg
  labels/train/*.txt
  labels/val/*.txt
```
- 数据集 YAML：`./configs/scb.yaml`（已指向 `SCBehavior_YOLO`）。

## 3. YOLOv8 微调（官方小模型 yolov8n.pt）
使用 Ultralytics CLI 在 SCB YOLO 结构数据集上微调：
```powershell
# 仍在 ClassroomBehaviorDetection 目录下
yolo task=detect mode=train model=yolov8n.pt data=./configs/scb.yaml imgsz=640 epochs=100 batch=16 project=./output name=scb_yolov8n
```
- 训练产物：`./output/scb_yolov8n/weights/best.pt`（与 `last.pt`）。
- 显存不足可：`batch=8` 或改用 `model=yolov8s.pt` 视硬件而定。

## 4. 验证集测试与结果保存
包含两类输出：
- YOLO 检测可视化（若干标框图片）
- 每个个体的课堂行为统计 CSV

### 4.1 YOLOv8 可视化（保存标框图片）
```powershell
yolo task=detect mode=predict model=./output/scb_yolov8n/weights/best.pt source=./data/SCBehavior_Dataset/SCBehavior_YOLO/images/val save=True project=./output name=scb_yolov8n_predict
```
- 可视化图片保存到：`./output/scb_yolov8n_predict/predict/`（Ultralytics 默认目录结构）。

### 4.2 按人导出课堂行为 CSV（支持匿名模式）
```powershell
# 使用 YOLOv8 推理 + 个体行为分析，导出 CSV
python src\identity_demo_v8.py --images_dir ./data/SCBehavior_Dataset/SCBehavior_YOLO/images/val --weights ./output/scb_yolov8n/weights/best.pt --output_csv ./output/identity_v8.csv --save_anno_dir ./output/identity_v8_anno --no_face
```
- `--no_face`：无初始人脸图库时，按匿名 ID（`Unknown_<frame>_<index>`）统计，避免所有 Unknown 合并。
- `--save_anno_dir`：同时保存项目内的标注可视化（与 YOLO 预测输出独立，可二选一或都保存）。
- 输出 CSV：`./output/identity_v8.csv`
- 字段：`frame,id,head,head_up_rate,head_up_rate_smooth`

## 5. 常见问题
- `yolo` 命令不可用：可改用 `python -m ultralytics ...`。
- 权重下载失败：网络不稳定时，请手动下载到 `./data/weights/`，并在命令中将 `model=` 或 `--weights` 指向该文件。
- 显存不足：降低 `batch` 或改用更小模型（`yolov8n.pt`）。
