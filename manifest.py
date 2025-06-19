# manifest.py – minimal MIP manifest for the single‑file HLW8032 driver
#install with  mip.install("github:<user>/<repo>")

metadata(
    version="0.1.0",                            
    description="All‑in‑one MicroPython driver for the HLW8032 energy‑metering IC",
    author="Jaspher Galvez <jasphergalvez14@gmail.com>",
    license="GNU",
)

# ship the single module to the board’s filesystem root
module("hlw8032")
