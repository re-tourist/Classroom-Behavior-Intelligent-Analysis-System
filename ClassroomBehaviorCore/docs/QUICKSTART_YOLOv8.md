# QUICKSTART: YOLOv8 微调与验证（相对路径版）

根目录：`ClassroomBehaviorDetection`

## 1) 环境配置
```powershell
cd ClassroomBehaviorDetection
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2) 用官方小模型 yolov8n 在 SCB YOLO 数据集上微调
```powershell
yolo task=detect mode=train model=yolov8n.pt data=./configs/scb.yaml imgsz=640 epochs=100 batch=16 project=./output name=scb_yolov8n
```
- 最佳权重：`./output/scb_yolov8n/weights/best.pt`

## 3) 用验证集测试并保存输出（图片 + CSV）
- 保存检测可视化图片：
```powershell
yolo task=detect mode=predict model=./output/scb_yolov8n/weights/best.pt source=./data/SCBehavior_Dataset/SCBehavior_YOLO/images/val save=True project=./output name=scb_yolov8n_predict
```
- 导出每个个体的课堂行为 CSV（无需人脸图库用 `--no_face`）：
```powershell
python src\identity_demo_v8.py --images_dir ./data/SCBehavior_Dataset/SCBehavior_YOLO/images/val --weights ./output/scb_yolov8n/weights/best.pt --output_csv ./output/identity_v8.csv --save_anno_dir ./output/identity_v8_anno --no_face
```
- 输出位置：
  - 图片：`./output/scb_yolov8n_predict/predict/`（Ultralytics 自动保存）或 `./output/identity_v8_anno/`
  - CSV：`./output/identity_v8.csv`


  python -c "import torch; print('torch', torch.__version__, 'cuda_version', torch.version.cuda, 'cuda_available', torch.cuda.is_available())"

git clone https://github.com/20191864136/SCBehavior-Dataset.git  

pip install -r requirements.txt --upgrade --no-cache-dir