import utime
import math
from machine import I2C, Pin
import config
from mpu6050 import MPU6050

# Configuración
i2c = I2C(0, sda=Pin(config.PIN_SDA), scl=Pin(config.PIN_SCL))
mpu = MPU6050(i2c)

def get_angles(accel):
    x, y, z = accel['x'], accel['y'], accel['z']
    # Cálculo de Pitch (Lo que ya usa tu proyecto)
    # Atan2(z, sqrt(x²+y²))
    pitch = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
    
    # Cálculo de Roll (Nuevo para esta prueba)
    # Atan2(y, sqrt(x²+z²))
    roll = math.degrees(math.atan2(y, math.sqrt(x**2 + z**2)))
    
    return pitch, roll

print("Moviendo sensor... (Ctrl+C para parar)")
print("PITCH (Adelante/Atrás) | ROLL (Izq/Der)")

while True:
    accel = mpu.get_accel_data()
    p, r = get_angles(accel)
    
    # Imprimimos formateado para fácil lectura
    print(f"Pitch: {p:6.2f}° | Roll: {r:6.2f}°")
    utime.sleep_ms(200)