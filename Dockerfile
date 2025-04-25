FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# اطمینان از اینکه Railway از ENV استفاده کنه
ENV PORT=8290

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8290"]
