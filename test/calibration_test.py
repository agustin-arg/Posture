import utime
from machine import I2C, Pin
import config
from mpu6050 import MPU6050
from posture_logic import PostureProcessor

# --- Configuración Inicial ---
i2c = I2C(0, sda=Pin(config.PIN_SDA), scl=Pin(config.PIN_SCL))
mpu = MPU6050(i2c)
# Usamos el alpha corregido (0.96 o el que uses)
processor = PostureProcessor(alpha=0.96) 

calibrated_angle = 0.0
is_calibrated = False

print("\n--- INICIO TEST DE CALIBRACIÓN ---")
print("Instrucciones: Coloca el sensor en una posición 'cómoda' (no necesariamente plana).")
print("El sistema calibrará en 5 segundos...")

# Espera 5 segundos para que te acomodes
for i in range(5, 0, -1):
    print(f"Calibrando en {i}...")
    utime.sleep(1)

# --- RUTINA DE CALIBRACIÓN (FOTO INSTANTÁNEA) ---
print(">>> CAPTURANDO REFERENCIA...")
accel = mpu.get_accel_data()
gyro = mpu.get_gyro_data()

# 1. Obtenemos el ángulo absoluto actual
processor.reset() # Limpiamos basura anterior
abs_angle = processor.calculate_pitch(accel, gyro)

# 2. Guardamos este ángulo como el "Cero" del usuario
calibrated_angle = abs_angle
processor.reset(initial_angle=calibrated_angle) # Reiniciamos filtro con el nuevo valor
is_calibrated = True

print(f"REFERENCIA GUARDADA: {calibrated_angle:.2f}°\n")
print("Ahora mueve el sensor. La 'Desviación' debería partir de 0.00°")
print("-" * 60)
print(f"{'ÁNGULO ABSOLUTO':^20} | {'REFERENCIA':^15} | {'DESVIACIÓN (Real)':^20}")
print("-" * 60)

# --- BUCLE DE MEDICIÓN ---
while True:
    accel = mpu.get_accel_data()
    gyro = mpu.get_gyro_data()
    
    # Ángulo crudo actual
    current_abs = processor.calculate_pitch(accel, gyro)
    
    # La magia: Resta el valor calibrado
    deviation = current_abs - calibrated_angle
    
    print(f"{current_abs:19.2f}° | {calibrated_angle:14.2f}° | {deviation:19.2f}°")
    
    utime.sleep_ms(1000)