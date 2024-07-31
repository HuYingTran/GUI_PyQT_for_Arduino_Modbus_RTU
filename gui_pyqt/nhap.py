import minimalmodbus
import serial

# Set up the instrument
instrument = minimalmodbus.Instrument('COM8', 1)  # Port name and slave address (1 in this case)
instrument.serial.baudrate = 9600        # Baudrate
instrument.serial.bytesize = 8           # Number of data bits to use
instrument.serial.parity   = serial.PARITY_NONE  # No parity
instrument.serial.stopbits = 1           # Number of stop bits
instrument.serial.timeout  = 0.5           # Timeout in seconds

# Debugging mode (optional)
instrument.debug = True

# Function code 6 is for writing a single register (holding register)
register_address = 1    # The address of the register you want to write to
value_to_write = 6    # The value you want to write to the register

# Write a value to the register
try:
    instrument.write_register(register_address, value_to_write, functioncode=6)
    print(f"Successfully wrote value {value_to_write} to register {register_address}")
except Exception as e:
    print(f"Error: {e}")

try:
    value = instrument.read_register(1, functioncode=3)
    print(f"Successfully read value {value} from register {register_address}")
except Exception as e:
    print(f"Error2: {e}")