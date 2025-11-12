FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

RUN mkdir -p /app/data

# Container expects hostapd log mounted at /var/log/hostapd.log
# Start parser and webapp together (simple supervision)
CMD ["bash","-lc","python3 parser.py --file /var/log/hostapd.log & sleep 1; python3 webapp.py"]
