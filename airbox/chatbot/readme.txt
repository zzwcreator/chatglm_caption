#激活虚拟环境
source /data/zzwenv/chatbot/bin/activate

python3运行python程序


#windows安装Mosquitto，并在修改conf文件listener为1883，allow_anonymous为true，然后通过以下命令启动mqtt broker
.\mosquitto.exe -c mosquitto.conf -v