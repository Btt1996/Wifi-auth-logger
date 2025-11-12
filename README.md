# wifi-auth-logger

Small tooling to log **failed** Wi‑Fi authentication attempts from `hostapd`/syslog (timestamps, MACs, reason, raw message) and present them in a lightweight web UI.

**What it records:** timestamp, client MAC, failure reason (friendly tag), raw message.  
**What it does NOT record:** plaintext passwords. WPA‑PSK handshakes do not reveal entered passwords to the AP.

**Use cases:** detect brute-force attempts, spot repeated failing clients, simple auditing for networks you own.

---

## Quick start (docker)
1. Install Docker & Docker Compose.
2. Mount or point the container to your `hostapd` log (see `docker-compose.yml`).
3. `cd parser && docker-compose up --build -d`
4. Open `http://<host-ip>:5000` to view logged attempts.

## Quick start (non-docker)
- Ensure `hostapd` logs to `/var/log/hostapd.log` via syslog (see `hostapd/rsyslog-hostapd.conf.example`).
- On the machine with the log:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r parser/requirements.txt
  cd parser
  python3 parser.py --file /var/log/hostapd.log
  # open a separate shell and run:
  python3 webapp.py

	•	Visit http://localhost:5000.
  ```

---

Files of interest
	•	parser/parser.py — tails hostapd logs and stores failed auth attempts to SQLite + CSV.
	•	parser/webapp.py — small Flask UI to view/export logs.
	•	hostapd/hostapd.conf.example — hostapd logging config hints.
	•	hostapd/rsyslog-hostapd.conf.example — rsyslog snippet to write hostapd logs to /var/log/hostapd.log.
	•	parser/pcap_monitor.py — optional helper to capture EAPOL frames (advanced).

Security & law

Only run this on networks you administrate. Capturing or attempting to recover other people’s passwords on networks you do not own is illegal and unethical.

Next steps (ideas)
	•	OUI vendor lookup (MAC → vendor)
	•	Alerting/notifications on repeated failures
	•	Auto-blocking (hostapd_cli / iptables integration)
	•	Parsing RADIUS logs for WPA‑Enterprise
