FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# Pacotes nativos mínimos
RUN pip install --upgrade pip
# A linha abaixo apenas atualiza os pacotes, mas não instala nada. Pode ser removida se não for instalar nenhuma dependência do sistema.
RUN apt-get update && apt-get install -y --no-install-recommends 

WORKDIR /app

# 1. Dependências
COPY app/requirements.txt ./        
RUN pip install --no-cache-dir -r requirements.txt

# 2. Código-fonte completo
COPY app/. ./                        

EXPOSE 8501

# 3. Comando de execução (CORRIGIDO)
CMD ["streamlit", "run", "streamlit_app.py"]
