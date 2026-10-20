FROM python:3.10-slim

# ffmpegと軽量版依存パッケージのインストール
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# CPU専用の軽量版 PyTorch をインストールして容量を大幅削減
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

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
