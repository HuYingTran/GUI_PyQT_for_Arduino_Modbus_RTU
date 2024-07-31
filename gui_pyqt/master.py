import minimalmodbus

# Địa chỉ slave
slave_address = 1

# Tạo một đối tượng instrument cho slave Modbus
instrument = minimalmodbus.Instrument('COM8', slave_address)

# Đặt cấu hình tốc độ truyền
instrument.serial.baudrate = 9600

# Địa chỉ của register
register_address = 0

# Giá trị mặc định của register
default_value = 0

while True:
    # Đọc giá trị từ register
    value = instrument.read_register(register_address, 0)
    modbus = instrument.write_bit(3, 1)
    print (modbus)

    if value != default_value:
        print(f"Received value from master: {value}")

    # Sleep để tránh việc quá tải CPU
    time.sleep(0.1)
