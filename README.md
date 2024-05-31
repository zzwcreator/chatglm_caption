<<<<<<< HEAD
# 项目实现过程

## 1. 环境准备
**所需硬件：笔记本电脑、Airbox、树莓派、摄像头、麦克风、扬声器、路由器网线等保证Airbox、树莓派和笔记本电脑在同一个局域网下。**
### 1.1 Airbox
1.mqtt配置：
`pip install paho-mqtt`

2.ChatGLM 6B配置，首先刷机，参照:
```
https://gitee.com/zilla0717/AirboxWiki/blob/master/README.md
```
airbox中可以使用多种应用，然而不同应用之间可能会存在着依赖冲突，为了避免这种情况的发生，我们使用虚拟环境来构建应用的运行环境，安装virtualenv。
```
pip3 install virtualenv -i https://pypi.tuna.tsinghua.edu.cn/simple
```
新建虚拟环境`virtualenv zzwenv`，即将在当前目录下新建一个名为env_name虚拟环境，虚拟环境的文件即存储在当前目录下的env_name文件夹里。这个虚拟环境包含了全局的python和pip的拷贝。激活虚拟环境`source zzwenv/bin/activate`

假设我们使用int8-2048模型，下载官方提供的模型文件chatglm-int8-2048目录到AirBox的/data下，模型的百度网盘地址为：
```
https://pan.baidu.com/share/init?surl=N6HZy9oq4ZnyRyz9MaDU6Q&pwd=1684
```

chatglm-int8-2048目录包含三个文件一个chatglm2-6b_2048_int8.bmodel模型文件，一个是libtpuchat.socpp编译的so文件，最后一个是tokenizer.model。

下载官方demo：
```
cd /data/
git clone https://github.com/zhengorange/chatbot.git
```
修改config.ini配置文件为：
```
[llm_model]
libtpuchat_path = ../chatglm-int8-2048/libtpuchat.so
bmodel_path = ../chatglm-int8-2048/chatglm2-6b_2048_int8.bmodel
token_path = ../chatglm-int8-2048/tokenizer.model
```
config.ini需要配置正确的模型文件，默认是选择int8-2048的模型。若要改更为其他模型文件，请修改配置文件中的模型文件路径。

安装项目所需依赖，在AirBox终端进入到/data/chatbot/目录下，执行：
```
source ../chatdoc/zzwenv/bin/activat
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```


### 1.2 树莓派
1.安装镜像，版本：`2024-03-15-raspios-bookworm-armhf.img`

2.查看树莓派版本`lsb_release -a`换源更新,具体可参考：
```
https://blog.csdn.net/Mars_ZERO/article/details/136392262
```

3.安装mqtt相关的库：
```
pip3 install paho-mqtt
pip3 install typing_extensions
```

4.rtsp推流配置：
镜像默认安装了`ffmpeg`，不用再安装，下载rtsp编译好的服务器`rtsp-simple-server`

5.语音唤醒snowboy，安装相关的库：
```
sudo apt-get install python3-pyaudio
sudo apt-get install swig
sudo apt-get install libatlas-base-dev
```

### 1.3 笔记本电脑
作为mqtt broker安装mosquitto


## 2.启动过程：

1.笔记本电脑作为broker，在mosquitto的安装路径cmd下执行：`.\mosquitto.exe -c mosquitto.conf -v`

2.树莓派启动rtsp推流：
```
#终端1：
cd /home/zzw/chatbot
./mediamtx &
#终端2：
ffmpeg -re -i /dev/video0 -s 720x480 -vcodec libx264 -preset:v ultrafast -tune:v zerolatency  -rtsp_transport tcp -f rtsp rtsp://192.168.31.179:8554/camera_test
#终端3：
cd /home/zzw/chatbot/snowboy_test/ && python snow.py
#终端4：
cd /home/zzw/chatbot/snowboy_test/ && python mqtt_res.py
```

3.Airbox进入激活环境、进入代码目录、执行代码:

```
source /data/zzwenv/chatbot/bin/activate
cd /data/chatbot && python vqa.py
```

=======
# chatglm_caption
>>>>>>> c39b028961dbf4b36fba0bd21ff21b9773835a56
