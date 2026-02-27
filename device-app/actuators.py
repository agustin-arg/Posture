from machine import Pin, PWM
import utime
import config


class PostureActuators:
    def __init__(self):
        # LEDs de Postura
        self.led_red = Pin(config.PIN_LED_RED, Pin.OUT)
        self.led_green = Pin(config.PIN_LED_GREEN, Pin.OUT)
        self.led_blue = Pin(config.PIN_LED_BLUE, Pin.OUT)

        # LED de Batería Baja
        self.led_battery_low = Pin(config.PIN_LED_BAT_LOW, Pin.OUT)
        self.led_battery_low.off()

        # Inicializar Buzzer y Vibrador
        self.buzzer = PWM(Pin(config.PIN_BUZZER), freq=220, duty=0)
        self.vibrator = Pin(config.PIN_VIBRATOR, Pin.OUT, value=0)

        # Inicializar Servo
        try:
            self.servo = PWM(Pin(config.PIN_SERVO), freq=config.SERVO_FREQ, duty=0)
        except Exception:
            self.servo = None

        # Variables de estado interno del Servo
        # _servo_state: 0=IDLE, 1=ALERT, 2=RETURN, 3=COOLDOWN
        self._servo_state = 0
        self._servo_debounce_since = 0
        self._servo_phase_until = 0

        # Variables de estado del Buzzer (patrón "pi-pi")
        self._buzzer_cycle_start = 0

        # Variables de estado del Vibrador (pulso periódico)
        self._vib_active_until = 0
        self._vib_next_trigger = 0

    def set_ble_led(self, state):
        """Controla el LED Azul para estado de conexión"""
        self.led_blue.value(1 if state else 0)

    def blink_ble_led(self):
        """Parpadeo del LED Azul para indicar espera"""
        self.led_blue.on()
        utime.sleep_ms(50)
        self.led_blue.off()
        utime.sleep_ms(950)

    def signal_battery_low(self):
        """
        Señal única en el PIN 2 (LED Integrado) antes de morir.
        Se enciende fijo por 2 segundos.
        """
        self.led_battery_low.on()
        utime.sleep(2)
        self.led_battery_low.off()

    def feedback_calibration(self):
        """Secuencia visual: Parpadeo LED Azul"""
        for _ in range(3):
            self.led_blue.on()
            utime.sleep_ms(100)
            self.led_blue.off()
            utime.sleep_ms(100)

    def confirm_calibration(self):
        """Confirmación visual: LED Verde"""
        self.led_green.on()
        utime.sleep_ms(1000)
        self.led_green.off()

    def stop_all(self, keep_ble_led=True):
        """Apaga actuadores principales (Rojo, Verde, Motores)"""
        self.led_red.off()
        self.led_green.off()
        if not keep_ble_led:
            self.led_blue.off()

        # El LED de batería (Pin 2) no se apaga aquí porque
        # normalmente stop_all se llama antes de hibernar

        try:
            self.buzzer.duty(0)
        except:
            pass
        self._buzzer_cycle_start = 0

        try:
            self.vibrator.value(0)
        except:
            try:
                self.vibrator.off()
            except:
                pass
        self._vib_active_until = 0
        self._vib_next_trigger = 0

        try:
            if self.servo:
                self.servo.duty(0)
        except:
            pass
        self._servo_state = 0
        self._servo_debounce_since = 0
        self._servo_phase_until = 0

    def set_battery_led(self, state):
        """Enciende/apaga LED de batería baja"""
        if state:
            self.led_battery_low.on()
        else:
            self.led_battery_low.off()

    def update(self, is_bad_posture, settings):
        """Actualiza LEDs Rojo/Verde y Motores"""
        # 1. LEDs Postura
        if settings.leds_enabled:
            self.led_red.value(is_bad_posture)
            self.led_green.value(not is_bad_posture)
        else:
            self.led_red.off()
            self.led_green.off()

        # 2. Buzzer (patrón "pi-pi" periódico)
        self._update_buzzer(is_bad_posture, settings.buzzer_enabled)

        # 3. Vibrador (pulso periódico, no constante)
        self._update_vibrator(is_bad_posture, settings.vibrator_enabled)

        # 4. Servo (ciclo periódico cada SERVO_INTERVAL_MS)
        self._update_servo(is_bad_posture, settings.servo_enabled)

    def _angle_to_duty(self, angle):
        min_duty = 25
        max_duty = 75
        if angle is None:
            return 0
        a = max(0, min(90, int(angle)))
        return int(min_duty + (a / 90.0) * (max_duty - min_duty))

    def _update_buzzer(self, is_bad_posture, enabled):
        """
        Patrón "pi-pi": dos beeps cortos (BUZZER_BEEP_MS cada uno,
        separados por BUZZER_GAP_MS) seguidos de silencio BUZZER_INTERVAL_MS.
        Ciclo total ≈ 4 segundos. Se resetea al recuperar buena postura.
        """
        if not enabled or not is_bad_posture:
            self.buzzer.duty(0)
            self._buzzer_cycle_start = 0
            return

        now = utime.ticks_ms()

        # Iniciar ciclo al entrar en mala postura
        if self._buzzer_cycle_start == 0:
            self._buzzer_cycle_start = now

        elapsed = utime.ticks_diff(now, self._buzzer_cycle_start)
        total_cycle = (
            config.BUZZER_BEEP_MS
            + config.BUZZER_GAP_MS
            + config.BUZZER_BEEP_MS
            + config.BUZZER_INTERVAL_MS
        )

        # Reiniciar ciclo al completarse
        if elapsed >= total_cycle:
            self._buzzer_cycle_start = now
            elapsed = 0

        t1 = config.BUZZER_BEEP_MS
        t2 = t1 + config.BUZZER_GAP_MS
        t3 = t2 + config.BUZZER_BEEP_MS

        if elapsed < t1:
            # Primer "pi"
            self.buzzer.freq(config.BUZZER_FREQ)
            self.buzzer.duty(512)
        elif elapsed < t2:
            # Pausa entre "pi-pi"
            self.buzzer.duty(0)
        elif elapsed < t3:
            # Segundo "pi"
            self.buzzer.freq(config.BUZZER_FREQ)
            self.buzzer.duty(512)
        else:
            # Silencio hasta el siguiente ciclo
            self.buzzer.duty(0)

    def _update_vibrator(self, is_bad_posture, enabled):
        """
        Pulso periódico: ON durante VIBRATOR_DURATION_MS,
        luego OFF durante VIBRATOR_INTERVAL_MS. Ciclo total ≈ 4 segundos.
        El motor no está activo continuamente, lo que evita interferencias
        con las lecturas del MPU6050. Se resetea al recuperar buena postura.
        """
        if not enabled or not is_bad_posture:
            self.vibrator.value(0)
            self._vib_next_trigger = 0
            self._vib_active_until = 0
            return

        now = utime.ticks_ms()

        # Primera activación: disparar inmediatamente
        if self._vib_next_trigger == 0:
            self._vib_active_until = utime.ticks_add(now, config.VIBRATOR_DURATION_MS)
            self._vib_next_trigger = utime.ticks_add(
                now, config.VIBRATOR_DURATION_MS + config.VIBRATOR_INTERVAL_MS
            )
            self.vibrator.value(1)
            return

        if utime.ticks_diff(now, self._vib_active_until) < 0:
            # Dentro del pulso activo
            self.vibrator.value(1)
        elif utime.ticks_diff(now, self._vib_next_trigger) >= 0:
            # Fin de la pausa: nuevo pulso
            self._vib_active_until = utime.ticks_add(now, config.VIBRATOR_DURATION_MS)
            self._vib_next_trigger = utime.ticks_add(
                now, config.VIBRATOR_DURATION_MS + config.VIBRATOR_INTERVAL_MS
            )
            self.vibrator.value(1)
        else:
            # En pausa entre pulsos (MPU6050 lee sin interferencia)
            self.vibrator.value(0)

    def _update_servo(self, is_bad_posture, enabled):
        """
        Ciclo periódico: debounce → mueve a ALERT_ANGLE (SERVO_HOLD_MS) →
        vuelve a IDLE_ANGLE (SERVO_HOLD_MS) → espera SERVO_INTERVAL_MS (5s) →
        repite mientras la postura siga siendo incorrecta.
        Estados: 0=IDLE, 1=ALERT, 2=RETURN, 3=COOLDOWN
        """
        if self.servo is None:
            return

        now = utime.ticks_ms()

        if not enabled or not is_bad_posture:
            # Sin movimiento activo: parar de inmediato
            if self._servo_state in (0, 3):
                try:
                    self.servo.duty(0)
                except:
                    pass
                self._servo_state = 0
                self._servo_debounce_since = 0
                self._servo_phase_until = 0
                return
            # Estados 1 y 2: dejar que la máquina de estados complete el recorrido

        # --- Estado 0: IDLE — esperar debounce antes de disparar ---
        if self._servo_state == 0:
            if self._servo_debounce_since == 0:
                self._servo_debounce_since = now
            if (
                utime.ticks_diff(now, self._servo_debounce_since)
                >= config.SERVO_DEBOUNCE_MS
            ):
                # Debounce superado → mover a posición de alerta
                try:
                    self.servo.duty(self._angle_to_duty(config.SERVO_ALERT_ANGLE))
                except:
                    pass
                self._servo_state = 1
                self._servo_phase_until = utime.ticks_add(now, config.SERVO_HOLD_MS)
                self._servo_debounce_since = 0
            return

        # --- Estado 1: ALERT — sostenido, luego volver ---
        if self._servo_state == 1:
            if utime.ticks_diff(now, self._servo_phase_until) >= 0:
                try:
                    self.servo.duty(self._angle_to_duty(config.SERVO_IDLE_ANGLE))
                except:
                    pass
                self._servo_state = 2
                self._servo_phase_until = utime.ticks_add(now, config.SERVO_HOLD_MS)
            return

        # --- Estado 2: RETURN — en posición inicial, luego apagar y esperar ---
        if self._servo_state == 2:
            if utime.ticks_diff(now, self._servo_phase_until) >= 0:
                try:
                    self.servo.duty(0)  # Apagar señal PWM (servo libre)
                except:
                    pass
                self._servo_state = 3
                self._servo_phase_until = utime.ticks_add(now, config.SERVO_INTERVAL_MS)
            return

        # --- Estado 3: COOLDOWN — esperar SERVO_INTERVAL_MS (5s) ---
        if self._servo_state == 3:
            if utime.ticks_diff(now, self._servo_phase_until) >= 0:
                # Pausa terminada → volver a IDLE para disparar de nuevo
                self._servo_state = 0
                self._servo_debounce_since = 0
