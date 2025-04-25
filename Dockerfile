FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the FastAPI app on port 8290
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8290"]
