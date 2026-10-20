FROM python:3.10-slim

# ffmpegのインストール
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 必要なライブラリのインストール
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    ffmpeg-python \
    openai-whisper \
    transformers \
    torch \
    pillow

COPY . .

# Renderのポート(10000)に合わせて起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
