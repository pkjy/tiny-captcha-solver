FROM python:3.8-slim-buster
# 拉取一个基础镜像，基于python3.8
LABEL maintainer="pkjy pkjy@outlook.com"
RUN mkdir /app

COPY ./sources.list /etc/apt/sources.list
RUN cat /etc/apt/sources.list
RUN rm -Rf /var/lib/apt/lists/*
RUN apt-get clean \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y libgl1 python3-opencv tesseract-ocr 
# 维护者信息
ADD ./requirements.txt ./app.py /app/
ADD ./tessdata /tessdata
# 将你的项目文件放到docker容器中的/app文件夹，这里code是在根目录的，与/root /opt等在一个目录
# 这里的路径，可以自定义设置，主要是为了方便对项目进行管理
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone 
# 设置容器时间，有的容器时区与我们的时区不同，可能会带来麻烦
ENV LANG C.UTF-8 
# 设置语言为utf-8
WORKDIR /app
# 设置工作目录，也就是下面执行 ENTRYPOINT 后面命令的路径
# RUN pip3 install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
# 根据requirement.txt下载好依赖包
# ENV TESSDATA_PREFIX=/app/tessdata

ENTRYPOINT ["python3","app.py"]