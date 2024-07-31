import minimalmodbus

# Địa chỉ slave
slave_address = 1

# Khởi tạo đối tượng slave với port và ID slave
instrument = minimalmodbus.Instrument('COM2', slave_address)  # Đổi thành cổng serial của bạn

# Cài đặt các thông số kết nối
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 0.5  # Timeout cho mỗi truy vấn

# Đọc giá trị từ thanh ghi của slave (địa chỉ 0)
register_address = 0
value = instrument.read_register(register_address, functioncode=3)  # functioncode=4 là đọc thanh ghi
print("Giá trị đọc được từ thanh ghi {}: {}".format(register_address, value))
