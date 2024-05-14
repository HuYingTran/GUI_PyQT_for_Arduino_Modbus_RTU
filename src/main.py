from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import sys
import time

import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

import minimalmodbus
import serial
import serial.tools.list_ports

# khai báo địa chỉ thanh ghi các dữ liệu

# kích thước vật kẹp
address_value_vk = 0

# trang thai kep
address_status_kep = 1

# trạng thái
address_status = 2

# value D
address_value_D = 3

# current_max
address_value_I = 4

# giá trị D hiện tại sau mỗi vòng loop
address_value_D_now = 5

# giá trị dòng điện hiện tại
address_value_I_now = 6

# trạng thái I/O
address_status_IO = 7

m_baudrate = [9600, 115200, 25600,]  # Một mảng các số nguyên

# Tay kẹp có 3 trạng thái:
# 0 - pasue
# 1 - kẹp vào
# 2 - mở ra
status_tay_kep = [0,1,2]

# độ mở Max or D_max
D_max = 100

class modbus_setting:
    def __init__(self, port, baudrate, parity, stopBits):
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.stopBits = stopBits

class modbus_status:
    def __init__(self, connected, gap, pause, clean):
        self.connected = connected
        self.gap = gap
        self.pause = pause
        self.clean = clean

class modbus_value:
    def __init__(self, value_I, value_D):
        self.value_I = value_I
        self.value_D = value_D

class modbus_master:
    def __init__(self, m_setting, m_status, m_value):
        self.m_setting = m_setting
        self.m_status = m_status
        self.m_value = m_value


m_setting = modbus_setting('','','','')
m_status = modbus_status(0,0,0,0)
m_value = modbus_value(0,0)
m_master = modbus_master(m_setting, m_status, m_value)
slave_id = 1

# mang optin D va I
array_I_D = [[0,0]]

array_D = np.array([[0,0]])
array_I = np.array([[0,0]])

#timer bắt đầu đếm sau khi conenct
timers = 0

class Ui_main(QMainWindow):
    def __init__(self):
        super(Ui_main, self).__init__()
        uic.loadUi('gui_main.ui', self)

        self.scroll_tuyChinh.setRange(0, D_max) # Đặt dải giá trị từ 0 đến 100
        self.scroll_tuyChinh.setSingleStep(10)  # Đặt bước là 10

        self.master = None
        self.function_gap_pasue_mo(self.read_value(address_status_kep)) # Cập nhật trạng thái hoạt động của tay kẹp
        self.comboBox_options.addItem("None")
        self.label_status.setText("")

        #code function btn
        self.btn_setting.clicked.connect(self.function_setting)
        self.btn_connect.clicked.connect(self.function_connect)
        self.btn_io.clicked.connect(self.function_io)

        self.scroll_tuyChinh.valueChanged.connect(self.function_tuyChinh)
        # self.t_edit_tuyChinh.textChanged.connect(self.function_tuyChinh_text)

        self.comboBox_options.activated.connect(self.function_options)
        self.btn_send.clicked.connect(self.function_send)
        self.btn_add.clicked.connect(self.function_add)
        self.btn_remove.clicked.connect(self.function_remove)

        self.btn_gap.clicked.connect(self.function_gap)
        self.btn_pause.clicked.connect(self.function_pause)
        self.btn_mo.clicked.connect(self.function_mo)
        self.btn_reset.clicked.connect(self.function_reset)

        # settup timer
        self.timer = QtCore.QTimer(self, interval=5)  # su dung timer de lien tuc cap nhat gia tri
        self.timer.timeout.connect(self.update_value)
        #end function btn

        # Thiết lập chế độ đàn hồi cho cửa sổ
        # window_size = self.size()
        # # Phóng to MainWindow theo kích thước cửa sổ
        # self.resize(window_size)
        # Vẽ biểu đồ
        
        # Tạo 2 biểu đồ
        self.canvas1 = FigureCanvas(plt.figure())
        layout1 = QVBoxLayout(self.widget_d)
        layout1.addWidget(self.canvas1)
        self.ax1 = self.canvas1.figure.subplots()

        self.canvas2 = FigureCanvas(plt.figure())
        layout2 = QVBoxLayout(self.widget_i)
        layout2.addWidget(self.canvas2)
        self.ax2 = self.canvas2.figure.subplots()

        self.plot1()
        self.plot2()
        
        self.show()
        

    def plot1(self):
        self.ax1.set_xlabel('Time(s)')
        self.ax1.set_ylabel('Value_D')
        self.ax1.set_xlim(0, 250)
        self.ax1.set_ylim(-10, D_max)
        self.canvas1.draw()
        self.canvas1.figure.tight_layout(pad=2)

    def plot2(self):
        self.ax2.set_xlabel('Time(s)')
        self.ax2.set_ylabel('Value_I')
        self.ax2.set_xlim(0, 250)
        self.ax2.set_ylim(-10, 100)
        self.canvas2.draw()
        self.canvas2.figure.tight_layout(pad=2)


    def read_value(self, address):
        try:
            return self.master.read_register(address,0)
        except:
            self.label_status.setText("Lỗi đọc giá trị")
            return 0

    def write_value(self, address, value):
        try:
            self.master.write_register(address, value)
        except:
            self.label_status.setText("Lỗi ghi giá trị")
            return

    def function_setting(self):
        self.window_setting = Ui_setting()
        self.window_setting.show()

    def function_connect(self):
        status_connect = ""
        if m_master.m_status.connected:
            self.master.serial.close()
            m_master.m_status.connected = 0
            self.btn_connect.setStyleSheet('background-color: rgb(0,255,0)')
            self.btn_connect.setText("CONNECT")
            self.label_status.setText("disconnect")
        else:
            try:
                self.master = minimalmodbus.Instrument(port=m_master.m_setting.port, slaveaddress=slave_id)
                self.master.serial.baudrate = int(m_master.m_setting.baudrate)
                self.master.serial.bytesize = 8
                self.master.serial.parity = serial.PARITY_NONE #m_master.m_setting.parity
                self.master.serial.stopbits = int(m_master.m_setting.stopBits)           
                m_master.m_status.connected = 1
            except:
                m_master.m_status.connected = 0
                
            # xử lsy hiển thị kết quả connect
            if m_master.m_status.connected:
                status_connect = "created"
                self.btn_connect.setStyleSheet('background-color: red')
                self.btn_connect.setText("DISCONNECT")
            else:
                status_connect = "creat faile"
                self.btn_connect.setStyleSheet('background-color: rgb(0,255,0)')

            self.label_status.setText(f"Connect: {m_master.m_setting.port} {status_connect}")
    
        # khởi chạy timer
        if m_master.m_status.connected:
            print("Start timer")
            self.timer.start(1000)
        else:
            self.timer.stop()
            print("Stop timer")

    def function_io(self):
        # kiểm tra trạng thái I/O để cập nhật button
        status_io = self.read_value(address_status_IO)
        # Đổi màu btn vag gửi giá trị mới
        status_io = not status_io
        if status_io:
            self.btn_io.setStyleSheet('background-color: rgb(0,255,0)')
        else:
            self.btn_io.setStyleSheet('background-color: rgb(255, 85, 0)') 
        
        self.write_value(address_status_IO, status_io) 

        self.function_gap_pasue_mo(self.read_value(address_status_kep))

    def function_tuyChinh(self):
        m_master.m_value.value_D = self.scroll_tuyChinh.value()
        # self.t_edit_tuyChinh.setPlainText(str(m_master.m_value.value_D))
        self.write_value(address_value_D_now, m_master.m_value.value_D)

    def function_gap_pasue_mo(self, i):
        # kiểm tra trạng thái để cập nhật button
        self.read_value(address_status_kep)

        # Đổi màu btn và gửi giá trị mới
        if m_master.m_status.gap == status_tay_kep[i]:
            return
        else:
            m_master.m_status.gap = status_tay_kep[i]
            self.write_value(address_status_kep, m_master.m_status.gap)

        self.btn_gap.setStyleSheet('background-color: rgb(170, 170, 255)')
        self.btn_pause.setStyleSheet('background-color: rgb(170, 170, 255)')
        self.btn_mo.setStyleSheet('background-color: rgb(170, 170, 255)')
        if i == 0:
            self.btn_pause.setStyleSheet('background-color: rgb(255, 170, 0);')
        elif i == 1:
            self.btn_gap.setStyleSheet('background-color: rgb(255, 170, 0);')
        else:
            self.btn_mo.setStyleSheet('background-color: rgb(255, 170, 0);')

    def function_gap(self):
        self.function_gap_pasue_mo(1)

    def function_pause(self):
        self.function_gap_pasue_mo(0)

    def function_mo(self):
        self.function_gap_pasue_mo(2)

    def function_reset(self):
        global array_D
        global array_I
        array_D = np.array([[0,0]])
        array_I = np.array([[0,0]])

        global timers
        timers = 0
        # self.ax1.clear()
        # self.ax2.clear()

    def function_options(self):
        try:
            idex = self.comboBox_options.currentIndex()
            self.t_edit_valueD.setPlainText(str(array_I_D[idex][0]))
            self.t_edit_valueI.setPlainText(str(array_I_D[idex][1]))
        except:
            self.label_status.setText("Lỗi chọn options")

    def function_send(self): 
        try:
            d = int(self.t_edit_valueD.toPlainText())
            self.write_value(address_value_D, d)
            i = int(self.t_edit_valueI.toPlainText())
            self.write_value(address_value_I, i)
            self.label_status.setText("Gửi dữ liệu thành công")
        except:
            self.label_status.setText("Hãy nhập giá trị I, D")

    def function_add(self):
        try:
            d = self.t_edit_valueD.toPlainText()
            i = self.t_edit_valueI.toPlainText()
            if d == '' or i == '':
                return
            self.comboBox_options.addItem(f"D:{d}; I:{i}")
            new_array = [int(d), int(i)]
            array_I_D.append(new_array)
        except:
            self.label_status.setText("Hãy nhập giá trị I, D")

    def function_remove(self):
        idex = self.comboBox_options.currentIndex()
        if idex == 0:
            return
        self.comboBox_options.removeItem(idex)
        del array_I_D[idex]

    def update_value(self):
        self.label_D.setText(str(self.read_value(address_value_D_now)))
        self.label_I.setText(str(self.read_value(address_value_I_now)))
        self.scroll_tuyChinh.setValue(self.read_value(address_value_D_now))

        # biểu đồ
        global timers
        timers = timers+1
        self.label_time.setText(str(timers))

        global array_D
        new_array = [[timers, int(self.label_D.text())]]
        array_D = np.append(array_D, new_array, axis=0)
        self.ax1.clear()
        self.ax1.plot(array_D[:, 0], array_D[:, 1])
        self.plot1()

        global array_I
        new_array = [[timers, int(self.label_I.text())]]
        array_I = np.append(array_I, new_array, axis=0)
        self.ax2.clear()
        self.ax2.plot(array_I[:, 0], array_I[:, 1])
        self.plot2()
        

class Ui_setting(QMainWindow):
    def __init__(self):
        super(Ui_setting,self).__init__()
        uic.loadUi('gui_setting.ui',self)

        # tìm cổng com và add vào comboBox
        ports = serial.tools.list_ports.comports()
        #xóa các item cũ trong comboBox
        self.comboBox_port.clear()
        for port in ports:
            self.comboBox_port.addItem(str(port.device))
        # self.comboBox_port

        self.btn_ok.clicked.connect(self.function_ok)

    def function_ok(self):
        m_master.m_setting.port = self.comboBox_port.currentText()
        print(m_master.m_setting.port)
        m_master.m_setting.baudrate = self.comboBox_baud.currentText()
        m_master.m_setting.parity = self.comboBox_parity.currentText()
        m_master.m_setting.stopBits = self.comboBox_stopBits.currentText()
        self.close() # đóng của sổ setting


app=QtWidgets.QApplication(sys.argv)
window = Ui_main()

sys.exit(app.exec_())