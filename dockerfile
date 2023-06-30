FROM python:3.9-slim

EXPOSE 8080

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD streamlit run --server.port 8080 --server.enableCORS false dashboard.py
