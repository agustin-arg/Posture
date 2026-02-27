import ubluetooth

# --- Configuración de Pines ---
PIN_SDA = 21
PIN_SCL = 22

# Pines de Feedback Visual (Postura y BLE)
PIN_LED_RED = 25  # Mala Postura
PIN_LED_GREEN = 33  # Buena Postura
PIN_LED_BLUE = 32  # Estado Bluetooth

# Pin Exclusivo Batería (LED Integrado)
PIN_LED_BAT_LOW = 2  # Solo se enciende al hibernar

PIN_BUZZER = 26
PIN_VIBRATOR = 18
PIN_SERVO = 19
PIN_BAT = 27  # Entrada ADC Batería

# --- Constantes del Servo ---
SERVO_FREQ = 50
SERVO_ALERT_ANGLE = 90
SERVO_IDLE_ANGLE = 0
SERVO_DEBOUNCE_MS = 300    # Tiempo mínimo de mala postura para confirmar
SERVO_HOLD_MS = 300         # Tiempo en cada posición (alerta / retorno)
SERVO_INTERVAL_MS = 5000    # Pausa entre ciclos de movimiento

# --- Constantes del Buzzer ---
BUZZER_FREQ = 2000          # Frecuencia del tono (Hz) — agudo y audible
BUZZER_BEEP_MS = 120        # Duración de cada "pi"
BUZZER_GAP_MS = 100         # Silencio entre los dos "pi"
BUZZER_INTERVAL_MS = 3660   # Silencio después del "pi-pi" (ciclo total ~4s)

# --- Constantes del Vibrador ---
VIBRATOR_DURATION_MS = 400  # Duración del pulso de vibración
VIBRATOR_INTERVAL_MS = 3600 # Pausa entre pulsos (ciclo total ~4s)

# --- Gestión de Energía ---
BAT_DIVIDER_FACTOR = 2.0
BAT_MIN_VOLTAGE = 4.7  # Voltaje mínimo para hibernar. Recomendado: 4.7V
BAT_CHECK_INTERVAL_MS = 300000  # 5 minutos

# --- Constantes de Batería (Voltaje en V) ---
BATTERY_VOLTAGE_MAX = 5.30
BATTERY_VOLTAGE_MID = 5.00  # Sí baja de este valor ya es LOW
# El vontage cuando esta conectado por usb es LOW

# --- UUIDs de Bluetooth BLE ---
POSTURE_SERVICE_UUID = ubluetooth.UUID("0000180f-0000-1000-8000-00805f9b34fb")
POSTURE_STATUS_CHAR_UUID = ubluetooth.UUID("00002a19-0000-1000-8000-00805f9b34fb")
THRESHOLD_ANGLE_CHAR_UUID = ubluetooth.UUID("00002a1b-0000-1000-8000-00805f9b34fb")
CALIBRATE_CHAR_UUID = ubluetooth.UUID("00002a1c-0000-1000-8000-00805f9b34fb")
BUZZER_CONTROL_CHAR_UUID = ubluetooth.UUID("00002a1e-0000-1000-8000-00805f9b34fb")
VIBRATOR_CONTROL_CHAR_UUID = ubluetooth.UUID("00002a1f-0000-1000-8000-00805f9b34fb")
LEDS_CONTROL_CHAR_UUID = ubluetooth.UUID("00002a20-0000-1000-8000-00805f9b34fb")
NOTIFY_CONTROL_CHAR_UUID = ubluetooth.UUID("00002a21-0000-1000-8000-00805f9b34fb")
SYSTEM_CONTROL_CHAR_UUID = ubluetooth.UUID("00002a22-0000-1000-8000-00805f9b34fb")
BATTERY_NOTIFY_CHAR_UUID = ubluetooth.UUID("00002a23-0000-1000-8000-00805f9b34fb")
SERVO_CONTROL_CHAR_UUID  = ubluetooth.UUID("00002a24-0000-1000-8000-00805f9b34fb")