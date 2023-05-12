from sys import argv, exit

from PySide2.QtWidgets import QApplication

from ui.MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication(argv)
    gui = MainWindow()
    gui.show()
    exit(app.exec_())
