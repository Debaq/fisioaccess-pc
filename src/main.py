import sys
from PySide6.QtWidgets import QApplication
from ui.main_window_impl import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.isMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()