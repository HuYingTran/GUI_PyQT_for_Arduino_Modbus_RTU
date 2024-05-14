import minimalmodbus
import time

# Địa chỉ slave
slave_address = 1

# Tạo một đối tượng instrument cho master Modbus
instrument = minimalmodbus.Instrument('COM8', slave_address)

# Đặt cấu hình tốc độ truyền
instrument.serial.baudrate = 9600

# Địa chỉ của register
register_address = 0

# Giá trị cần gửi
data_to_send = 1234

# Gửi dữ liệu tới slave device
instrument.write_register(register_address, data_to_send)

# Đóng kết nối
instrument.close_port()
