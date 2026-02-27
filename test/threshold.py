import utime
from machine import I2C, Pin
import config
from mpu6050 import MPU6050
from posture_logic import PostureProcessor

# --- 1. CONFIGURACIÓN ---
UMBRAL_PRUEBA = 15.0  # El límite para que suene la alarma (Grados)
TOLERANCIA = 0.5      # Margen de error aceptable para tu informe

# Hardware
i2c = I2C(0, sda=Pin(config.PIN_SDA), scl=Pin(config.PIN_SCL))
mpu = MPU6050(i2c)
led_red = Pin(config.PIN_LED_RED, Pin.OUT)
led_green = Pin(config.PIN_LED_GREEN, Pin.OUT)

# Lógica (Usamos alpha 0.96 o el que tengas configurado)
processor = PostureProcessor(alpha=0.96)

# --- 2. CALIBRACIÓN INICIAL ---
print(f"\n--- PRUEBA DE UMBRAL (Límite: {UMBRAL_PRUEBA}°) ---")
print("Paso 1: Mantén el sensor QUIETO en la posición 'Buena Postura'.")
print("Calibrando en 3 segundos...")
utime.sleep(3)

accel = mpu.get_accel_data()
gyro = mpu.get_gyro_data()
processor.reset()
referencia = processor.calculate_pitch(accel, gyro)
processor.reset(initial_angle=referencia)

print(f"--> REFERENCIA FIJADA: {referencia:.2f}°")
print("Paso 2: Inclina el sensor LENTAMENTE hasta que cambie el LED.")
print("-" * 70)
print(f"{'DESVIACIÓN':^15} | {'ESTADO':^10} | {'VISUALIZACIÓN':<40}")
print("-" * 70)

# --- 3. BUCLE DE PRUEBA ---
while True:
    # Lectura
    accel = mpu.get_accel_data()
    gyro = mpu.get_gyro_data()
    angulo_actual = processor.calculate_pitch(accel, gyro)
    
    # Cálculo
    desviacion = abs(angulo_actual - referencia)
    es_mala_postura = desviacion > UMBRAL_PRUEBA
    
    # Actuadores
    if es_mala_postura:
        led_red.on()
        led_green.off()
        estado_txt = "!!! MAL !!!"
    else:
        led_red.off()
        led_green.on()
        estado_txt = "OK"
        
    # Visualización tipo barra de progreso
    # Cada '#' son 2 grados
    barra = "#" * int(desviacion / 2)
    # Marca visual del umbral
    marca_umbral = "|" if len(barra) < (UMBRAL_PRUEBA/2) else ""
    
    print(f"{desviacion:14.2f}° | {estado_txt:^10} | {barra}{marca_umbral}")
    
    utime.sleep_ms(1000) # Velocidad de lectura cómoda para el ojo