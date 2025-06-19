# hlw8032‑micropython

*A zero‑dependency, single‑file MicroPython driver for the HLW8032 mains‑monitoring IC*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](#license)

---

## ✨ Features

* **One file only** – just `hlw8032.py` (plus `README.md` & `manifest.py`).
* Leaves the **USB/REPL UART free** – any spare hardware UART @ 4 800 bps 8E1.
* **Self‑syncing frame grabber** – recovers alignment even mid‑stream.
* Calculates **Vrms, Irms, active power (W), apparent power (VA)** & **power factor** every 50 ms.
* Works on ESP32, RP2040, STM32 … any µPy board with ≥ 2 UARTs.

---

## 📦 Installation

<details>
<summary><strong>Option A – install straight from GitHub (MIP)</strong></summary>

```python
import mip
mip.install("github:<your‑user>/<hlw8032‑micropython>")  # replace with your repo
```

</details>

<details>
<summary><strong>Option B – manual copy</strong></summary>

1. Copy **`hlw8032.py`** to the board (via `ampy`, `rshell`, Thonny, etc.).
2. Reboot or simply `import hlw8032`.

</details>

---

## ⚡ Wiring (typical 230 V)

| HLW8032 pin | Purpose                  | MCU pin                               | Notes                                    |
| ----------- | ------------------------ | ------------------------------------- | ---------------------------------------- |
| **TX**      | 5 V UART output          | `RX` (via 4 k7 + 10 k divider → 3 V3) | Level‑shift *down* to 3 V3.              |
| **GND**     | Ground                   | `GND`                                 | Common ground.                           |
| **VP / VN** | Differential mains sense | –                                     | Use datasheet’s 4×470 kΩ : 1 kΩ divider. |
| **I+ / I‑** | Shunt sense              | –                                     | 1 mΩ ±1 % typical.                       |
| **VCC**     | +5 V supply              | 5 V                                   | The IC is **5 V only**.                  |

> ⚠️ **Never** tie HLW8032 TX directly to a 3 V3 pin – use the resistor divider or an opto‑coupler or you may damage your MCU.

---

## 🏃 Quick start

```python
from hlw8032 import EnergyMeter
import time

meter = EnergyMeter(uart_id=2, rx=4, tx=5)  # pick any spare UART & pins

while True:
    if (d := meter.read()):
        print("{Vrms:7.2f} V  {Irms:6.3f} A  {P_active:7.2f} W  "
              "{S_apparent:7.2f} VA  PF={PF:.3f}".format(**d))
    time.sleep(0.25)
```

Expected serial output with a 60 W incandescent bulb:

```
229.80 V  0.260 A  59.67 W  59.95 VA  PF=0.995
```

---

## 🛠 API reference

### `class EnergyMeter(...)`

High‑level façade – handles UART creation, frame sync & maths.

```python
EnergyMeter(
    uart_id: int = 1,   # which hardware UART to use
    rx: int = 16,       # RX pin connected to HLW TX (level‑shifted!)
    tx: int = 17,       # dummy TX pin (HLW8032 ignores it)
    v_coeff: float = 1.88,  # voltage divider ratio (V_real / V_adc)
    i_coeff: float = 1.0,   # shunt scaling (I_real / I_adc)
    uart_obj: machine.UART | None = None,  # pass an existing UART instead
)
```

#### `.read(timeout_ms=120) -> dict | None`

Returns **`None`** on timeout; otherwise a dict:

| Key          | Type  | Description                            |
| ------------ | ----- | -------------------------------------- |
| `Vrms`       | float | Line voltage (V).                      |
| `Irms`       | float | RMS current (A).                       |
| `P_active`   | float | Real power (W).                        |
| `S_apparent` | float | Apparent power (VA).                   |
| `PF`         | float | Power factor = `P_active / S_apparent` |
| `frame`      | bytes | Raw 24‑byte frame (debug helper).      |

### Advanced Configuration

* **`_HLW8032`** – raw driver that accepts a ready UART and returns the same dict.
* Constants: `_FRAME`, `_ANCHOR`, `_BAUD`, `_UART_CONF` – import & hack as needed.

---

## 🔧 Calibration

1. **Voltage coefficient** – `v_coeff = (R_high + R_low) / R_low`
   For the 4×470 kΩ + 1 kΩ divider → **1 880 k / 1 k ≈ 1.88**.
2. **Current coefficient** – leave `i_coeff=1.0` for a 1 mΩ shunt; adjust otherwise.
3. Compare against a multimeter and tweak both until readings agree.

---

## 📑 Datasheet

[https://w2.electrodragon.com/Chip-cn-dat/HLW-dat/HLW8032-dat/HLW8032.pdf](https://w2.electrodragon.com/Chip-cn-dat/HLW-dat/HLW8032-dat/HLW8032.pdf)

Pull‑requests welcome – especially board test reports & examples! ⭐

---

## License

Released under the **GNU General Public License v3.0** – see [LICENSE](LICENSE) for full terms.

---

### Keywords (GitHub topics)

`micropython`  `hlw8032`  `energy`  `power‑meter`  `esp32`  `iot`
