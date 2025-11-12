# Wifi-auth-logger
Small tooling to log **failed** Wi‑Fi authentication attempts from `hostapd`/syslog (timestamps, MACs, reason, raw message) and present them in a lightweight web UI.  **What it records:** timestamp, client MAC, failure reason (friendly tag), raw message.   **What it does NOT record:** plaintext passwords. WPA‑PSK handshakes.
