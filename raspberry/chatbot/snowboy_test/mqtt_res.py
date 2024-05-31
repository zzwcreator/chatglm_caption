import paho.mqtt.client as mqtt
import time
from pyaudio import PyAudio, paInt16
import wave
import sys
import json

IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
else:
    import urllib2
    from urllib import quote_plus
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode

API_KEY = 'm3wTjBa81kzqoENS1cG9wsVT'
SECRET_KEY = 'mLhsmRVlVdY14rJmcF9gfkeCeuff6A1s'


# TEXT = "什么事？"

# 发音人选择, 基础音库：0为度小美，1为度小宇，3为度逍遥，4为度丫丫，
# 精品音库：5为度小娇，103为度米朵，106为度博文，110为度小童，111为度小萌，默认为度小美 
PER = 4
# 语速，取值0-15，默认为5中语速
SPD = 5
# 音调，取值0-15，默认为5中语调
PIT = 5
# 音量，取值0-9，默认为5中音量
VOL = 5
# 下载的文件格式, 3：mp3(default) 4： pcm-16k 5： pcm-8k 6. wav
AUE = 6

FORMATS = {3: "mp3", 4: "pcm", 5: "pcm", 6: "wav"}
FORMAT = FORMATS[AUE]

CUID = "123456PYTHON"

TTS_URL = 'http://tsn.baidu.com/text2audio'


class DemoError(Exception):
    pass


"""  TOKEN start """

TOKEN_URL = 'http://aip.baidubce.com/oauth/2.0/token'
SCOPE = 'audio_tts_post'  # 有此scope表示有tts能力，没有请在网页里勾选

def fetch_token():
    print("fetch token begin")
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
    if (IS_PY3):
        result_str = result_str.decode()

    print(result_str)
    result = json.loads(result_str)
    print(result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not SCOPE in result['scope'].split(' '):
            raise DemoError('scope is not correct')
        print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')
"""  TOKEN end """

FILEPATH = './audio/exit.wav' # 录制完成存放音频路径
def play(filename):
    """
    播放音频
    """
    wf = wave.open(filename, 'rb')  # 打开audio.wav
    p = PyAudio()                   # 实例化 pyaudio
    # 打开流
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(1024)
    while data != b'':
        data = wf.readframes(1024)
        stream.write(data)
    # 释放IO
    stream.stop_stream()
    stream.close()
    p.terminate()

# 当代理响应订阅请求时被调用。
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("连接成功")
    print("Connected with result code " + str(rc))

# 当代理响应订阅请求时被调用
def on_subscribe(client, userdata, mid, granted_qos):
    # print("Subscribed: " + str(mid) + " " + str(granted_qos))
    print("已和broker建立连接")

# 当使用使用publish()发送的消息已经传输到代理时被调用。
def on_publish(client, obj, mid):
    print("OnPublish, mid: " + str(mid))

# 当收到关于客户订阅的主题的消息时调用。 message是一个描述所有消息参数的MQTTMessage。
def on_message(client, userdata, msg):
    # print(msg.topic + " " + str(msg.payload))
    rece = msg.payload
    Ques = rece.decode('UTF-8','strict')
    print(Ques)

    TEXT = Ques
    token = fetch_token()
    tex = quote_plus(TEXT)  # 此处TEXT需要两次urlencode
    print(tex)
    params = {'tok': token, 'tex': tex, 'per': PER, 'spd': SPD, 'pit': PIT, 'vol': VOL, 'aue': AUE, 'cuid': CUID,
              'lan': 'zh', 'ctp': 1}  # lan ctp 固定参数

    data = urlencode(params)
    print('test on Web Browser' + TTS_URL + '?' + data)

    req = Request(TTS_URL, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()

        headers = dict((name.lower(), value) for name, value in f.headers.items())

        has_error = ('content-type' not in headers.keys() or headers['content-type'].find('audio/') < 0)
    except  URLError as err:
        print('asr http response http code : ' + str(err.code))
        result_str = err.read()
        has_error = True

    save_file = "error.txt" if has_error else 'result.' + FORMAT
    with open(save_file, 'wb') as of:
        of.write(result_str)

    if has_error:
        if (IS_PY3):
            result_str = str(result_str, 'utf-8')
        print("tts api  error:" + result_str)

    print("result saved as :" + save_file)


    play('./result.wav')


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
client.subscribe(("airbox_res", 2))
client.loop_start()


while True:
    # 发布MQTT信息
    # sensor_data = "ni hao ......from topic-demo"
    # # 消息将会发送给代理，并随后从代理发送到订阅匹配主题的任何客户端。
    # # publish(topic, payload=None, qos=0, retain=False)
    # # topic:该消息发布的主题
    # # payload:要发送的实际消息。如果没有给出，或设置为无，则将使用零长度消息。 传递int或float将导致有效负载转换为表示该数字的字符串。 如果你想发送一个真正的int / float，使用struct.pack（）来创建你需要的负载
    # # qos:服务的质量级别 对于Qos级别为1和2的消息，这意味着已经完成了与代理的握手。 对于Qos级别为0的消息，这只意味着消息离开了客户端。
    # # retain:如果设置为True，则该消息将被设置为该主题的“最后已知良好” / 保留的消息
    # # msg = input("please innput")
    # # if msg == 'q':
    # #     client.publish(topic="airbox", payload=sensor_data, qos=2)  
    # print(123123)
    time.sleep(2)



