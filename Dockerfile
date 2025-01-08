# Použití základního Python image
FROM python:3.12-slim

# Instalace základních nástrojů pro kompilaci
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Nastavení pracovního adresáře
WORKDIR /app

# Kopírování požadavků a jejich instalace
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Kopírování aplikace do kontejneru
COPY . .

# Nastavení prostředí pro Flask
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Exponování portu
EXPOSE 5000

# Spuštění aplikace
CMD ["flask", "run"]