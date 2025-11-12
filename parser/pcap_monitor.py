#!/usr/bin/env python3
"""
pcap_monitor.py (optional)
Simple wrapper to run tshark and capture EAPOL frames to a rotating pcap file.
Requires: tshark installed and interface in monitor mode (or capture from AP if possible).

Usage:
  python3 pcap_monitor.py --iface wlan0mon --out eapol.pcap

This is a helper for advanced users who want to capture 802.1X/EAPOL frames for forensic analysis.
It does not parse passwords — EAPOL captures show handshake frames only.
"""
import argparse
import subprocess
import sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iface", required=True)
    ap.add_argument("--out", default="eapol.pcap")
    args = ap.parse_args()

    tshark_cmd = [
        "tshark",
        "-i", args.iface,
        "-w", args.out,
        "-f", "ether proto 0x888e",  # capture EAPOL only
    ]
    print("Running:", " ".join(tshark_cmd))
    try:
        subprocess.run(tshark_cmd)
    except KeyboardInterrupt:
        print("Stopped by user")
    except FileNotFoundError:
        print("tshark not found. Install tshark (wireshark) to use this tool.", file=sys.stderr)

if __name__ == "__main__":
    main()
