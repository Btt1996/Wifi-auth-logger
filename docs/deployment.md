# Deployment notes

## On a Raspberry Pi / Linux machine running hostapd

1. Ensure hostapd logs to syslog (see `hostapd/hostapd.conf.example`).
2. Put `hostapd` rsyslog snippet into `/etc/rsyslog.d/30-hostapd.conf` (see `hostapd/rsyslog-hostapd.conf.example`) and restart rsyslog:

```bash
sudo cp hostapd/rsyslog-hostapd.conf.example /etc/rsyslog.d/30-hostapd.conf
sudo systemctl restart rsyslog
```

Confirm `/var/log/hostapd.log` is being written.

3. Option A — Docker:
- Copy repo to the Pi, `cd parser`
- Edit `docker-compose.yml` if the log path is different.
- `docker-compose up -d --build`
- Visit `http://<pi-ip>:5000`

4. Option B — Native Python:
- Create venv and install dependencies:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r parser/requirements.txt
  cd parser
  python3 init_db.py
  python3 parser.py --file /var/log/hostapd.log
  # in another shell:
  python3 webapp.py
  ```

## If using a consumer router with remote syslog
- In the router admin, set Syslog / Log server to the IP of the machine running this parser.
- Ensure that syslogd on that machine writes hostapd messages to `/var/log/hostapd.log` (the rsyslog snippet above helps).
- Start the parser pointing to that file.

## Useful commands
- View DB:

```bash
sqlite3 data/attempts.db “SELECT id, ts, device_mac, reason FROM attempts ORDER BY id DESC LIMIT 50;”
```

- Tail logs for debug:

```bash
tail -F /var/log/hostapd.log
