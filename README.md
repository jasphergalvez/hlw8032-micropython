# hlw8032-micropython
# MicroPython HLW8032 Driver

*A zero‑dependency, single‑file helper for the HLW8032 mains‑monitoring IC*

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](#license)

---

## ✨ Features

* **One file only** – just `hlw8032.py` (plus this README & `manifest.py`).
* Keeps the **USB/REPL UART free** – uses any spare hardware UART at 4 800 bps 8E1.
* **Self‑syncing frame grabber** – works even if you start reading mid‑stream.
* Calculates **Vrms, Irms, active power (W), apparent power (VA)** and **power‑factor** from every 24‑byte report.
* No external dependencies; works on ESP32, RP2, STM32 … any µPy board with two UARTs.

---

## 📦 Installation

<details>
<summary><strong>Option A – install straight from GitHub (MIP)</strong></summary>

```python
import mip
mip.install("github:<your‑user>/<repo>")  # replace with your path
```

</details>

<details>
<summary><strong>Option B – manual copy</strong></summary>

1. Copy **`hlw8032.py`** into the board’s filesystem (e.g. via `ampy`, `rshell`, or the Thonny file browser).
2. Reboot or `import hlw8032`.

</details>

---

## ⚡ Wiring <sup>(typical 230 V use)</sup>

| HLW8032 pin | Purpose                  | ESP32 pin                             | Notes                                      |
| ----------- | ------------------------ | ------------------------------------- | ------------------------------------------ |
| **TX**      | 5 V UART output          | `Rx` (via 4 k7 + 10 k divider → 3 V3) | Level‑shift *down* to 3 V3.                |
| **GND**     | Ground                   | `GND`                                 | Common ground.                             |
| **VP / VN** | Differential mains sense | –                                     | Use the datasheet 4×470 kΩ : 1 kΩ divider. |
| **I+ / I‑** | Shunt sense              | –                                     | 1 mΩ ±1 % typical.                         |
| **VCC**     | +5 V supply              | 5 V                                   | The IC is **5 V only**.                    |

> ⚠️  **Never** connect the HLW8032 TX directly to a 3 V3 pin without the resistor divider or an opto‑coupler – it will eventually kill the MCU.

---

## 🏃 Quick start

```python
from hlw8032 import EnergyMeter
import time

meter = EnergyMeter(uart_id=2, rx=4, tx=5)  # choose any free UART & pins

while True:
    if (d := meter.read()):
        print("{Vrms:7.2f} V  {Irms:6.3f} A  {P_active:7.2f} W  "
              "{S_apparent:7.2f} VA  PF={PF:.3f}".format(**d))
    time.sleep(0.25)
```

Example console output with a 60 W bulb:

```
229.80 V  0.260 A  59.67 W  59.95 VA  PF=0.995
```

---

## 🛠 API reference

### `class EnergyMeter(...)`

High‑level façade – handles UART creation, frame sync, math.

```python
EnergyMeter(
    uart_id: int = 1,   # which hardware UART to use
    rx: int = 16,       # RX pin connected to HLW TX (level‑shifted!)
    tx: int = 17,       # dummy TX pin (HLW8032 ignores it)
    v_coeff: float = 1.88,  # voltage divider ratio (V_real / V_adc)
    i_coeff: float = 1.0,   # shunt scaling (I_real / I_adc)
    uart_obj: machine.UART | None = None,  # supply an existing UART
)
```

#### `.read(timeout_ms=120) -> dict | None`

*Returns `None` on timeout; otherwise a dictionary with:*

| Key          | Type  | Description                                 |
| ------------ | ----- | ------------------------------------------- |
| `Vrms`       | float | Line voltage in volts.                      |
| `Irms`       | float | RMS current in amperes.                     |
| `P_active`   | float | Real/active power in watts.                 |
| `S_apparent` | float | Apparent power in volt‑amperes.             |
| `PF`         | float | Power factor = `P_active / S_apparent`.     |
| `frame`      | bytes | (Optional) raw 24‑byte frame for debugging. |

### Low‑level helpers (advanced)

* `_HLW8032` – internal class that exposes `.read()` returning the same dict but takes a **ready UART** instead of creating its own.
* Helper constants: `_FRAME`, `_ANCHOR`, `_BAUD` – exposed for hacking.

---

## 🔧 Calibration

1. **Voltage coefficient** – `v_coeff = (V_divider_total / R_low)`
   For the datasheet 4×470 kΩ + 1 kΩ network that’s **1 880 k / 1 k ≈ 1.88**.
2. **Current coefficient** – if you use a 1 mΩ shunt, leave `i_coeff=1.0`; otherwise scale.
3. Compare against a multimeter and tweak the two coefficients until readings match.

---

## DATASHEET FOR HLW8032
https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjbvKCNsPyNAxX89zgGHReoKS8QFnoECAkQAQ&url=https%3A%2F%2Fw2.electrodragon.com%2FChip-cn-dat%2FHLW-dat%2FHLW8032-dat%2FHLW8032.pdf&usg=AOvVaw2SctmmYgO9bnaaTxazrCtC&opi=89978449

Pull requests welcome – especially board test reports & examples!

---

## License

`hlw8032.py`, docs and examples are released under the **MIT License** – see [LICENSE](LICENSE) for full text.

