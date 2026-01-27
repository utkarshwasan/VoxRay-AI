FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ /app/backend/
COPY consolidated_medical_data/ /app/consolidated_medical_data/
COPY frontend/dist /app/frontend/dist
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]