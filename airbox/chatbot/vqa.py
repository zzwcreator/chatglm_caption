import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
import cv2
from chat import TPUChatglm
import cpuinfo
import paho.mqtt.client as mqtt
import time
import queue
import threading

print("Package import finish!")



Rece_flag = 0 #全局变量，接收mqtt消息的标志

Ques = " " #全局变量，接收mqtt消息

# MQTT相关函数
# 当代理响应订阅请求时被调用。
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("连接成功")
    print("Connected with result code " + str(rc))
# 当代理响应订阅请求时被调用
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
# 当使用使用publish()发送的消息已经传输到代理时被调用。
def on_publish(client, obj, mid):
    print("OnPublish, mid: " + str(mid))
# 当收到关于客户订阅的主题的消息时调用。 message是一个描述所有消息参数的MQTTMessage。

def on_message(client, userdata, msg):
    # print(msg.topic + " " + str(msg.payload))
    global Rece_flag
    Rece_flag = 1
    rece = msg.payload
    global Ques
    Ques = rece.decode('UTF-8','strict')
    print(Ques)
    # 定义一个全局变量实现同步并返回树莓派接收到的question

# 当客户端有日志信息时调用
def on_log(client, obj, level, string):
    print("Log:" + string)
# 实例化
client = mqtt.Client()
# client.username_pw_set("admin", "password")
# 回调函数
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
# client.on_log = on_log
# host为启动的broker地址 举例本机启动的ip 端口默认1883
client.connect(host="192.168.31.178", port=1883, keepalive=6000)  # 订阅频道
time.sleep(1)

# 多个主题采用此方式
# client.subscribe([("demo", 0), ("test", 2)])      #  test主题，订阅者订阅此主题，即可接到发布者发布的数据

# 订阅主题 实现双向通信中接收功能，qs质量等级为2
client.subscribe(("airbox", 2))
client.loop_start()

print("MQTT init finish!")

# camera初始化
# 无缓存读取视频流类
class VideoCapture:
  def __init__(self, name):
    self.cap = cv2.VideoCapture(name)
    self.q = queue.Queue()
    t = threading.Thread(target=self._reader)
    t.daemon = True
    t.start()
  # 帧可用时立即读取帧，只保留最新的帧
  def _reader(self):
    while True:
      ret, frame = self.cap.read()
      if not ret:
        print("读取帧失败")
        exit(0)
        break
      if not self.q.empty():
        try:
          self.q.get_nowait()   # 删除上一个（未处理的）帧
        except queue.Empty:
          pass
      self.q.put(frame)

  def read(self):
    return self.q.get()

cap = VideoCapture("rtsp://192.168.31.179:8554/camera_test")
frame = cap.read()
print("camera init well!")

# 模型初始化
glm = None
cpu_info = cpuinfo.get_cpu_info()
cpu_name = cpu_info['brand_raw']
if cpu_name != "Apple M1 Pro":
    glm = TPUChatglm()
print("model init well!")

# dense caption函数
def sample_dense_captions_image_file():
    # Set the values of your computer vision endpoint and computer vision key
    # as environment variables:
    try:
        endpoint = os.environ["VISION_ENDPOINT"]
        key = os.environ["VISION_KEY"]
    except KeyError:
        print("Missing environment variable 'VISION_ENDPOINT' or 'VISION_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create an Image Analysis client.
    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    # Load image to analyze into a 'bytes' object.
    with open("image.png", "rb") as f:
        image_data = f.read()
    # Extract multiple captions, each for a different area of the image.
    # This will be a synchronously (blocking) call.
    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.DENSE_CAPTIONS],
        gender_neutral_caption=True,  # Optional (default is False)
    )

    resultcap = []
    if result.dense_captions is not None:
        for caption in result.dense_captions.list:
            location = str((caption.bounding_box.x,caption.bounding_box.y,caption.bounding_box.width,caption.bounding_box.height))
            text = str(caption.text)
            resultcap.append(text + location)
    return resultcap

    # Print dense caption results to the console. The first caption always
    # corresponds to the entire image. The rest correspond to sub regions.
    # print("Image analysis results:")
    # print(" Dense Captions:")
    # if result.dense_captions is not None:
    #     for caption in result.dense_captions.list:
    #         print(f"   '{caption.text}', {caption.bounding_box}")
    # print(f" Image height: {result.metadata.height}")
    # print(f" Image width: {result.metadata.width}")
    # print(f" Model version: {result.model_version}")


if __name__ == "__main__":
    history = []
    # while 1:
    #     time.sleep(1)
    # while 1:
    #     msg = input("please input：")
    #     if msg == 'q':
    #         ret,frame = cap.read()
    #         cv2.imwrite('image.png', frame)  
    #         print("Frame saved as image.png") 
    #         res = sample_dense_captions_image_file()
    #         # 问题到时候替换为用户的输入
    #         Ques = "图片里有什么东西？"
    #         Prompt = "请根据我对图像的文字描述回答问题。 问题：" + Ques + "文字描述及位置(x,y,w,h)：" +str(res)
    #         print(Prompt)
    #         for response, history in glm.stream_predict(Ques, history):
    #             print(response)
    print("等待树莓派传输的问题！")
    fun_flag = 0
    is_ask = 0
    while 1:
        if Rece_flag == 1:
            print("开始推理")
            # frame = cap.read()
            # cv2.imwrite('image.png', frame)  
            # print("Frame saved as image.png") 
            # res = sample_dense_captions_image_file()
            # print(res)
            # 问题到时候替换为用户的输入
            # Ques = "图片里有什么东西？"
            if (Ques == '模型对话'):
                fun_flag = 1
                is_ask = 0
            elif (Ques == '视觉问答'):
                fun_flag = 2
                is_ask = 0
            elif (Ques == '意图理解'):
                fun_flag = 3
                is_ask = 0
            else:
                is_ask = 1
                Prompt = "回答问题：" + Ques + "要求输出50字以内，如果您不清楚我问的问题，您可以要求我再重新叙述。"
                
            if fun_flag == 1:
                Prompt = "回答问题：" + Ques + "要求输出50字以内，如果您不清楚我问的问题，您可以要求我再重新叙述。"
            elif fun_flag == 2:
                frame = cap.read()
                cv2.imwrite('image.png', frame)  
                print("Frame saved as image.png") 
                res = sample_dense_captions_image_file()
                Prompt = "请根据图像的dense caption进行视觉问答,要求只输出中文答案并不超过50字。 问题：" + Ques + "图像的dense caption为：" +str(res)
            elif fun_flag == 3:
                frame = cap.read()
                cv2.imwrite('image.png', frame)  
                print("Frame saved as image.png") 
                res = sample_dense_captions_image_file()
                Prompt = "请理解我问题的意图，并根据图像的dense caption进行视觉理解问答,要求只输出中文答案并不超过50字。 问题：" + Ques + "图像的dense caption为：" +str(res)

            print(Prompt)
            # if is_ask ==1:
            #     print("大模型执行问答.........................")
            if is_ask == 1:
                for response, history in glm.stream_predict(Prompt, history):
                    a = 1
                print(response)
                client.publish(topic="airbox_res", payload=response, qos=2)

        Rece_flag = 0
        time.sleep(1)
        
    # while True:
    #     # 发布MQTT信息
    #     sensor_data = "ni hao ......from topic-demo"
    #     # 消息将会发送给代理，并随后从代理发送到订阅匹配主题的任何客户端。
    #     # publish(topic, payload=None, qos=0, retain=False)
    #     # topic:该消息发布的主题
    #     # payload:要发送的实际消息。如果没有给出，或设置为无，则将使用零长度消息。 传递int或float将导致有效负载转换为表示该数字的字符串。 如果你想发送一个真正的int / float，使用struct.pack（）来创建你需要的负载
    #     # qos:服务的质量级别 对于Qos级别为1和2的消息，这意味着已经完成了与代理的握手。 对于Qos级别为0的消息，这只意味着消息离开了客户端。
    #     # retain:如果设置为True，则该消息将被设置为该主题的“最后已知良好” / 保留的消息
    #     client.publish(topic="airbox_res", payload=sensor_data, qos=2)
    #     time.sleep(2)

    # Prompt = "请根据我对图像的文字描述以及每句话所描述对象的位置(x,y,w,h)，回答问题。 问题：图片里有什么东西？对图像的描述有：['a person in a room with a bed and a blanket(0, 0, 640, 480)', 'a person wearing glasses and holding his hand to his mouth(0, 133, 217, 327)', 'a close-up of a pillow(323, 62, 82, 138)', "a black and white photo of a person's face(67, 391, 246, 84)"]"


    










