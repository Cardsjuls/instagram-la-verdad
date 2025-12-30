FROM python:3.11-slim

# ✅ Instalar fuentes TrueType (DejaVu) para que PIL use DejaVuSans-Bold.ttf
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core fonts-dejavu-extra \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
