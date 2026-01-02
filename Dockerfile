FROM python:3.11-slim

WORKDIR /app

# Copy only what you need (NOT .env)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Create .env with defaults if it doesn't exist
RUN echo "FLASK_ENV=production\nFLASK_DEBUG=0" > .env.default

EXPOSE 5000

CMD ["python", "app.py"]

