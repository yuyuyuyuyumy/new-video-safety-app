FROM python:3.10-slim

# ffmpeg とビルドに必要な最小パッケージをインストール
RUN apt-get update && apt-get install -y ffmpeg gcc python3-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# pip 自体を最新化
RUN pip install --no-cache-dir --upgrade pip

# CPU版 PyTorch を確実にインストールする指定方法に変更
RUN pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu

# 必要なライブラリのインストール
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    ffmpeg-python \
    openai-whisper \
    transformers \
    pillow

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
