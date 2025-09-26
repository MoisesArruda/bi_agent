FROM python:3.11-slim

WORKDIR /

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

# Comando para rodar o Streamlit
CMD ["streamlit", "run", "src/frontend/app.py", "--server.port", "8501"]