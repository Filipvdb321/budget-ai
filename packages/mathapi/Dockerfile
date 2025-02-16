# Gebruik een lichte Python-basisimage
FROM python:3.10-slim

WORKDIR /app

# Copy only the app package to the container
COPY ../../packages/mathapi ./

# Installeer dependencies
RUN pip install -r requirements.txt

# Maak de app module beschikbaar
ENV PYTHONPATH=/app
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

# Maak een niet-root gebruiker voor veiligheid
RUN adduser --disabled-password --gecos '' pythonuser
USER pythonuser

# Stel de standaardpoort in
EXPOSE 5000

# Start de applicatie met Flask
CMD ["flask", "--app", "app/app.py", "run", "--host=0.0.0.0"]

# TODO: Upgrade naar Gunicorn voor productie gebruik
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.app:app"]
