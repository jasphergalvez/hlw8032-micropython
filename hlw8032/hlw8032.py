"""
hlw8032_single.py – One‑file MicroPython library + demo for the HLW8032 energy‑metering IC

Usage (REPL or your own main.py):
    from hlw8032_single import EnergyMeter
    m = EnergyMeter(uart_id=2, rx=4, tx=5)   # pick any spare UART & pins
    while True:
        if (d := m.read()):
            print("{Vrms:7.2f} V  {Irms:6.3f} A  {P_active:7.2f} W  "
                  "{S_apparent:7.2f} VA  PF={PF:.3f}".format(**d))
"""
from machine import UART
import time

# ------------------------- protocol constants ---------------------------
_FRAME     = 24          # bytes per HLW8032 report
_ANCHOR    = 0x5A        # byte‑1 (index 1) is always 0x5A
_BAUD      = 4_800       # fixed by the chip
_UART_CONF = dict(bits=8, parity=0, stop=1)   # 8E1

# ------------------------- helpers -------------------------------------
def _checksum_ok(buf: bytes) -> bool:
    """Return True iff low byte of Σ(bytes 2‑22) equals byte 23."""
    return (sum(buf[2:23]) & 0xFF) == buf[23]

# ------------------------- low‑level driver -----------------------------
class _HLW8032:
    """Minimal raw‑frame reader & decoder (internal—use EnergyMeter)."""

    def __init__(self, uart: UART, v_coeff=1.88, i_coeff=1.0):
        self.uart      = uart
        self.v_coeff   = v_coeff
        self.i_coeff   = i_coeff

    # ----- frame acquisition (self‑syncing) -----
    def _get_frame(self, timeout_ms=80):
        start = time.ticks_ms()
        buf   = bytearray()
        while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
            if self.uart.any():
                buf += self.uart.read()
                # keep buffer reasonable
                if len(buf) > 128:
                    buf = buf[-64:]
                for i in range(len(buf) - _FRAME + 1):
                    if buf[i+1] == _ANCHOR and _checksum_ok(buf[i:i+_FRAME]):
                        return bytes(buf[i:i+_FRAME])
        return None

    # ----- public API -----
    def read(self, timeout_ms=80):
        """Return dict with Vrms, Irms, active & apparent power, PF, or None."""
        f = self._get_frame(timeout_ms)
        if not f:
            return None
        # unpack registers
        up, ur = int.from_bytes(f[2:5], 'big'), int.from_bytes(f[5:8], 'big')
        ip, ir = int.from_bytes(f[8:11], 'big'), int.from_bytes(f[11:14], 'big')
        pp, pr = int.from_bytes(f[14:17], 'big'), int.from_bytes(f[17:20], 'big')
        # effective quantities
        vrms   = (up / ur) * self.v_coeff
        irms   = (ip / ir) * self.i_coeff
        p_act  = (pp / pr) * self.v_coeff * self.i_coeff
        s_app  = vrms * irms
        pf     = p_act / s_app if s_app else 0.0
        return {
            "Vrms": vrms,
            "Irms": irms,
            "P_active": p_act,
            "S_apparent": s_app,
            "PF": pf,
            "frame": f,   # raw 24‑byte blob (optional)
        }

# ------------------------- façade class --------------------------------
class EnergyMeter:
    """High‑level wrapper—just specify UART ID & pins, call .read()."""

    def __init__(
        self,
        uart_id: int = 1,
        rx: int = 16,
        tx: int = 17,
        v_coeff: float = 1.0,
        i_coeff: float = 1.0,
        uart_obj: UART | None = None,
    ):
        # Use provided UART or create a new one with 4800‑8E1
        self.uart = uart_obj or UART(uart_id, _BAUD, rx=rx, tx=tx, **_UART_CONF)
        self._hlw = _HLW8032(self.uart, v_coeff, i_coeff)

    def read(self, timeout_ms: int = 120):
        """Return dict with all quantities; None if no valid frame."""
        return self._hlw.read(timeout_ms)

