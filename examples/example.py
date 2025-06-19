import hlw8032
import time


# EXAMPLE FOR LOOP READING POWER MONITORING
if __name__ == "__main__":
    meter = hlw8032.EnergyMeter(uart_id=1, rx=16, tx=17, v_coeff=1.0)   # adjust V_coeff for calibration. Default is 1.0 for config in datasheet
    while True:
        data = meter.read()
        if data:
            print("V={Vrms:7.2f} V | I={Irms:6.3f} A | "
                  "P={P_active:7.2f} W | S={S_apparent:7.2f} VA | "
                  "PF={PF:.3f}".format(**data))
        else:
            print("…waiting for frame")
        time.sleep_ms(250)


#Keywords
#EnergyMeter(uartid, rx, tx, v_coeff, i_coeff)
# uart_obj = UART()  define your own UART object, if none defined, uses default for ESP32-WROOM-D2