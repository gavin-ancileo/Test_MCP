FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt
# Copy core application files
COPY app.py .
COPY config.py .
COPY database.py .
COPY validation.py .
COPY models.py .
COPY mcp_tools.py .

# Copy modular directory structures
COPY routers/ ./routers/
COPY services/ ./services/
COPY tools/ ./tools/

# Copy data and initialization files
COPY prompts_data.py .
COPY init-database.py .
COPY init-db.sql /app/init-db.sql
COPY 40-prompts.sql /app/40-prompts.sql
COPY 40-prompts-rich.sql /app/40-prompts-rich.sql
COPY seed-40-prompts.py /app/seed-40-prompts.py
EXPOSE 8001
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
