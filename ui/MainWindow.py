import datetime
import threading
import time

from PySide2 import QtGui, QtCore
from PySide2.QtCore import Qt, Signal, QDate, QTime
from PySide2.QtWidgets import QMainWindow

import socket

from ntp import NtpServer
from ui.ui_main import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.WindowMinimizeButtonHint |  # 使能最小化按钮
                            Qt.WindowCloseButtonHint |  # 使能关闭按钮
                            Qt.WindowStaysOnTopHint)  # 窗体总在最前端
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon("htek.ico"))
        # 创建信号
        self.HlSignal = HlSignal()
        self.HlSignal.show_message.connect(self._show_message)
        self.HlSignal.change_time.connect(self._change_time)
        # 刷新线程
        self.refresh_thread = threading.Thread(target=self.change_time)
        self.refresh_thread.setDaemon(True)
        self.refresh_thread.start()
        # 绑定
        self.btn_use_config.clicked.connect(lambda: self.f_btn_start_with_config())
        self.btn_use_default.clicked.connect(lambda: self.f_btn_start_with_default())
        self.edit_date_time.setDate(QDate.currentDate())
        self.edit_date_time.setTime(QTime.currentTime())
        self._show_message('NTP服务未启动', 1)
        self.running = False

    def closeEvent(self, event) -> None:
        from sys import exit
        self.stop_ntp_server()
        exit(0)

    def change_time(self):
        while True:
            self.HlSignal.change_time.emit()
            time.sleep(1)

    def _change_time(self):
        self.label_show_utc.setText(str(datetime.datetime.utcnow()).split('.')[0])
        self.label_show_local.setText(str(datetime.datetime.now()).split('.')[0])

    def show_message(self, message, level=0):
        self.HlSignal.show_message.emit(message, level)

    def _show_message(self, message, level=0):
        if level == 1:
            self.label_info.setText(f'<font color=red>{message}</font>')
        else:
            self.label_info.setText(message)

    def f_btn_start_with_config(self):
        host_ip = self.edit_bind_ip.text()
        port = int(self.edit_bind_port.text())
        offset_time = count_offset(self.label_show_local.text(), self.edit_date_time.text())
        self.stop_ntp_server()
        self._show_message('正在启动NTP服务')
        thread = threading.Thread(target=self.start_ntp_server, args=[host_ip, port, offset_time, ])
        thread.setDaemon(True)
        thread.start()
        self.running = True
        self._show_message('已启动NTP服务！')

    def f_btn_start_with_default(self):
        self.set_default()
        self.f_btn_start_with_config()

    def set_default(self):
        self.edit_date_time.setDate(QDate.currentDate())
        self.edit_date_time.setTime(QTime.currentTime())

    def start_ntp_server(self, host_ip="0.0.0.0", port=123, offset_time=300):
        work_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        work_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        work_socket.bind((host_ip, port))
        self.show_message("服务位于: %s:%s " % (host_ip, port))

        self.ntp = NtpServer(work_socket, offset_time)
        self.ntp.start_server()

    def stop_ntp_server(self):
        if self.running:
            self.show_message('正在关闭NTP服务')
            self.ntp.stop_server()
            self.show_message('已关闭NTP服务')

class HlSignal(QtCore.QObject):
    # 定义信号
    show_message = Signal(str, int)
    change_time = Signal()

    def __init__(self):
        super(HlSignal, self).__init__()


def count_offset(local_time, aim_time) -> int:
    """

    :param local_time: 2000-01-01 00:00:00
    :param aim_time: 2000-02-01 01:01:01
    :return: offset time int
    """
    aim_time_stamp = datetime.datetime.strptime(aim_time, "%Y-%m-%d %H:%M:%S").timestamp()
    local_time_stamp = datetime.datetime.strptime(local_time, "%Y-%m-%d %H:%M:%S").timestamp()
    return int(aim_time_stamp - local_time_stamp)
