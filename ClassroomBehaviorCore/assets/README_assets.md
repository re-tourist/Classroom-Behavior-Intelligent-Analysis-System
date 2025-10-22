# UI 资源清单

为提升界面精致度，建议提供以下素材（PNG/SVG，浅色/深色适配）：

- 应用 Logo：`assets/logo.(png|svg)`，512×512 与 128×128 两版
- 工具栏图标：
  - `icons/open_file.(png|svg)`
  - `icons/camera.(png|svg)`
  - `icons/start.(png|svg)` / `icons/stop.(png|svg)`
  - `icons/export_csv.(png|svg)` / `icons/export_json.(png|svg)`
- 字体（可选）：更现代的界面字体文件如 `assets/fonts/Inter.ttf`
- 示例视频：`data/samples/demo.mp4`（课堂环境 30–60 秒）

请将上述文件按路径放置，界面会自动加载（图标可后续在 `main_window.py` 中绑定）。