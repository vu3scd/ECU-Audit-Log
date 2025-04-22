
FROM python:3.10-slim

WORKDIR /app

COPY . /app
RUN pip install flask python-can

EXPOSE 5000
CMD ["python", "ecu_audit/webapp.py"]
