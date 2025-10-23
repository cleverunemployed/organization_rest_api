FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean


COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade setuptools wheel

RUN pip install --no-cache-dir psycopg2-binary==2.9.9

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]