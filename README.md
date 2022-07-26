# tiny-captcha-solver
> A tiny simple out-of-the-box api for slide captcha and ocr captcha. using opencv and tesseract. self training tessdata. 一个简易的验证码识别服务，支持数字、字母的OCR以及滑动验证码的缺口识别。

### 运行环境 
* python 3.8+
* opencv 
* tesseract 4.0+

### 特性
* 滑块验证码的缺口位置识别  
* 简单数字或字母的OCR识别  
* 自训练数据集，增加对某些字体的识别成功率

### 服务器部署

```shell script
# 获取代码
git clone https://github.com/pkjy/tiny-captcha-solver.git

# 进入项目目录
cd tiny-captcha-solver

# 安装依赖
apt-get install -y tesseract-ocr python3-opencv
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 运行
python app.py
```
### Docker部署  
使用 Dockerfile 构建 或者直接 Pull镜像  
```shell script
# 获取代码
git clone https://github.com/pkjy/tiny-captcha-solver.git

# 进入项目目录
cd tiny-captcha-solver

# dockerfile 构建
docker build -t tiny-captcha-solver:latest .

# 运行镜像
docker run -p 5000:5000 --name tiny-captcha-solver -d tiny-captcha-solver:latest
```  

```shell script
# 从 dockerhub pull
docker pull pkjy/tiny-captcha-solver:latest
# 运行镜像
docker run -itd --rm -p 5000:5000 --name tiny-captcha-solver pkjy/tiny-captcha-solver:latest
```  


#### use
##### send request in local, for slide.
```
POST 127.0.0.1:5000/slide/base64
content-type: application/json

# post data with body raw (json):
{
  target: base64 format for target image
  template: base64 format for full background image
}
```
will return target position `{x1,x2,y1,y2}` like
```
{
    "code": 0,
    "result": {
        "x1": "181",
        "x2": "249",
        "y1": "78",
        "y2": "146"
    }
}
```
raw input

![full](./examples/slide/full2.png)  
![source](./examples/slide/marker2.png)

result  

![result](./result.png)


##### send request in local, for ocr.
```
POST 127.0.0.1:5000/ocr/base64
content-type: application/json

# post data with body raw (json):
{
  base64: [multi base64 format for target image] 
}
```
will return target position `{"code": 0,"result": ["47SS"]}` like
```
{
    "code": 0,
    "result": [
        "47SS"
    ]
}
```

raw input  
![ocr](./examples/ocr/15.jpg)


#### demo
demo url: https://pkjy.xyz/captcha .you can request here with your images

### notice
if you get src like `data:image/jpg;base64,UklGRkgJAABXRUJQVlA4WAoAAAAQAAAAQwAAQwAAQUxQS...` you need to remove header like `data:image/jpg;base64,` since it's Data URLs usage not base64 standard format.