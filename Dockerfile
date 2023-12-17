FROM python:3.12.0

COPY app /app

VOLUME /var/log/tapo-controller
VOLUME /etc/tapo-controller

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "/app/app.py"]