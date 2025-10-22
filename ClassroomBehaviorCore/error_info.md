问题：在 Linux 环境执行 Windows 风格路径导致文件找不到

原始命令：
(base) root@zgs-ubuntu-01:/home/XYJ_project/ClassroomBehaviorDetection# python src\identity_demo_v8.py --images_dir ./data/SCBehavior_Dataset/SCBehavior_YOLO/images/val \
> --weights ./output/scb_yolov8n/weights/best.pt --output_csv ./output/identity_v8.csv --save_anno_dir ./output/identity_v8_anno --no_face

报错：
python: can't open file 'srcidentity_demo_v8.py': [Errno 2] No such file or directory

根因：
- 在 Linux/Unix shell 中，`\` 是转义字符；`src\identity_demo_v8.py` 会被解析为 `srcidentity_demo_v8.py`，从而找不到文件。
- Linux 的路径分隔符应使用 `/`，Windows 使用 `\`。

修复：
- Linux：把 `src\identity_demo_v8.py` 改为 `src/identity_demo_v8.py`；其余路径保持 `./...` 或 `/...`。
- Windows：保留反斜杠 `\`。

正确示例
Linux：
python src/identity_demo_v8.py --images_dir ./data/SCBehavior_Dataset/SCBehavior_YOLO/images/val \
  --weights ./output/scb_yolov8n/weights/best.pt --output_csv ./output/identity_v8.csv \
  --save_anno_dir ./output/identity_v8_anno --no_face

Windows（PowerShell）：
python src\identity_demo_v8.py --images_dir .\data\SCBehavior_Dataset\SCBehavior_YOLO\images\val --weights .\output\scb_yolov8n\weights\best.pt --output_csv .\output\identity_v8.csv --save_anno_dir .\output\identity_v8_anno --no_face

注意：
- 请根据实际训练输出目录调整 `--weights` 路径，如 `.\output\yolov8n5\weights\best.pth`。
- 运行前确认工作目录正确：
  - Linux：`pwd`，并验证 `ls src/identity_demo_v8.py`
  - Windows：`Get-Location`，并验证 `Test-Path .\src\identity_demo_v8.py`
