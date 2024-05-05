# Python 3.11をベースイメージとして使用
FROM python:3.11-slim

# libmagicのインストールに必要なパッケージを追加
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt に記載されたパッケージをインストール
# マウントされたボリュームからの相対パスを使用
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# コンテナが稼働している間、ポート8501を開放する
EXPOSE 8501

# コンテナ起動時のデフォルトコマンドはbashを維持する
CMD ["/bin/bash"]
