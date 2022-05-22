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
ENV APP_NAME video-yolo
WORKDIR /home/$APP_NAME
COPY ./src ./src
COPY main.py .
COPY api.py .

CMD [ "python", "./api.py" ]    
