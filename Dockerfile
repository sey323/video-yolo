FROM python:3.8

# opencv-devのインストール
RUN apt-get update -y && apt-get install -y git libopencv-dev cmake\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ライブラリのインストール
COPY requirements.txt .
RUN pip install pip==21.2.4 \
    && pip install --no-cache-dir -r requirements.txt 

# 実行環境の準備
ENV HOME /app
WORKDIR $HOME
COPY ./ .

CMD [ "python", "./run.py" ]    
