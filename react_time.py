import utime
from machine import I2C, Pin
import config
from mpu6050 import MPU6050
from posture_logic import PostureProcessor

# --- CONFIGURACIÓN ---
UMBRAL = 15.0
i2c = I2C(0, sda=Pin(config.PIN_SDA), scl=Pin(config.PIN_SCL))
mpu = MPU6050(i2c)
processor = PostureProcessor(alpha=0.96)

# Actuador para medir
# Usamos el LED porque es visual, pero el código mide la señal eléctrica
led_red = Pin(config.PIN_LED_RED, Pin.OUT)

print("\n--- TEST DE LATENCIA (TIEMPO DE REACCIÓN) ---")
print("1. Mantén postura BIEN.")
print("2. Inclínate RÁPIDO hacia adelante para provocar el disparo.")
print("3. El sistema medirá cuánto tardó en reaccionar.")

# Calibración rápida
utime.sleep(1)
accel = mpu.get_accel_data()
gyro = mpu.get_gyro_data()
processor.reset()
referencia = processor.calculate_pitch(accel, gyro)
processor.reset(initial_angle=referencia)
print("--> CALIBRADO. ¡Haz un movimiento brusco ahora!")

while True:
    # 1. Marca de tiempo ANTES de leer y procesar (T0)
    t_inicio = utime.ticks_us()
    
    # 2. Lectura y Proceso Matemático
    accel = mpu.get_accel_data()
    gyro = mpu.get_gyro_data()
    angulo = processor.calculate_pitch(accel, gyro)
    desviacion = abs(angulo - referencia)
    
    # 3. Decisión Lógica
    if desviacion > UMBRAL:
        # Si detectamos mala postura, encendemos
        # Y medimos el tiempo inmediatamente después de la orden eléctrica
        led_red.on()
        t_final = utime.ticks_us()
        
        delta_us = utime.ticks_diff(t_final, t_inicio)
        delta_ms = delta_us / 1000.0
        
        print(f"¡DISPARO! Latencia total de sistema: {delta_ms:.3f} ms")
        print(f"Desviación detectada: {desviacion:.2f}°")
        
        # Pausa para que leas y reinicies
        utime.sleep(2)
        led_red.off()
        print("--- Listo para otro intento ---")
        
    else:
        led_red.off()
    
    # Simula tu delay normal de main.py (importante para realismo)
    utime.sleep_ms(100)