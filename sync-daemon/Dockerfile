FROM gilleslamiral/imapsync:latest
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip default-mysql-client && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install imapclient pymysql

COPY idle_daemon.py /idle_daemon.py
CMD ["python3", "/idle_daemon.py"]
