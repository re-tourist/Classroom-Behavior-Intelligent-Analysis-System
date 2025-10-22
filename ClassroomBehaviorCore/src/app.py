import sys
from pathlib import Path

from PySide6 import QtWidgets

APP_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    # 更统一的控件外观
    app.setStyle("Fusion")
    from ui.main_window import MainWindow

    win = MainWindow(APP_ROOT)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
