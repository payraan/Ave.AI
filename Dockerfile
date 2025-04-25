FROM python:3.9-slim

WORKDIR /app

# اول فقط نیازمندی‌ها را کپی و نصب می‌کنیم تا از کش Docker استفاده شود
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# بقیه فایل‌ها را کپی می‌کنیم
COPY . .

# اطمینان از اینکه Railway از ENV استفاده کنه
ENV PORT=8290

# افزودن پیغام شفاف
RUN echo "⚠️ AVE_API_KEY is required as an environment variable!"

# تنظیم Python برای پاک نکردن بافر خروجی
ENV PYTHONUNBUFFERED=1

# صبر برای اتمام تنظیم متغیرهای محیطی در Railway
CMD echo "Starting service..." && \
    echo "Checking environment:" && \
    echo "PORT=$PORT" && \
    echo "AVE_API_KEY exists: $(if [ -n \"$AVE_API_KEY\" ]; then echo true; else echo false; fi)" && \
    if [ -z "$AVE_API_KEY" ]; then echo "❌ ERROR: AVE_API_KEY environment variable is not set!"; exit 1; fi && \
    echo "Starting uvicorn..." && \
    uvicorn main:app --host 0.0.0.0 --port $PORT
