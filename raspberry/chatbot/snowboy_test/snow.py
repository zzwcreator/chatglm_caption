import snowboydecoder
import signal
import wave
import sys
import json
import requests
import time
import os
import base64
from pyaudio import PyAudio, paInt16
import webbrowser
from fetchToken import fetch_token
from mqtt import mqtt_init
import time

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

interrupted = False # snowboy监听唤醒结束标志
endSnow = False # 程序结束标志

framerate = 16000  # 采样率
num_samples = 2000  # 采样点
channels = 1  # 声道
sampwidth = 2  # 采样宽度2bytes

FILEPATH = './audio/audio.wav' # 录制完成存放音频路径
music_exit = './audio/exit.wav' # 唤醒系统退出语音
music_open = './audio/open.wav' # 唤醒系统打开语音
os.close(sys.stderr.fileno()) # 去掉错误警告

def signal_handler(signal, frame):
    """
    监听键盘结束
    """
    global interrupted
    interrupted = True

def interrupt_callback():
    """
    监听唤醒
    """
    global interrupted
    # print(123132)
    return interrupted

def detected():
    """
    唤醒成功
    """
    print('唤醒成功')
    play(music_open)
    global interrupted
    interrupted = True
    detector.terminate()

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

def save_wave_file(filepath, data):
    """
    存储文件
    """
    wf = wave.open(filepath, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b''.join(data))
    wf.close()

def my_record():
    """
    录音
    """
    pa = PyAudio()
    stream = pa.open(format=paInt16, channels=channels,
                     rate=framerate, input=True, frames_per_buffer=num_samples)
    my_buf = []
    # count = 0
    t = time.time()
    print('开始录音...')
    while time.time() < t + 4:  # 秒
        string_audio_data = stream.read(num_samples)
        my_buf.append(string_audio_data)
    print('录音结束!')
    save_wave_file(FILEPATH, my_buf)
    stream.close()


def speech2text(speech_data, token, dev_pid=1537):
    """
    音频转文字
    """
    FORMAT = 'wav'
    RATE = '16000'
    CHANNEL = 1
    CUID = '123456PYTHON'
    SPEECH = base64.b64encode(speech_data).decode('utf-8')
    data = {
        'format': FORMAT,
        'rate': RATE,
        'channel': CHANNEL,
        'cuid': CUID,
        'len': len(speech_data),
        'speech': SPEECH,
        'token': token,
        'dev_pid': dev_pid
    }
    # 语音转文字接口 该接口可能每个人不一样，取决于你需要哪种语音识别功能，本文使用的是 语音识别极速版

    url = 'http://vop.baidu.com/server_api'
    headers = {'Content-Type': 'application/json'} # 请求头
    print('正在识别...')
    r = requests.post(url, json=data, headers=headers)
    Result = r.json()
    # print(Result)
    if 'result' in Result:
        return Result['result'][0]
    else:
        return Result

def get_audio(file):
    """
    获取音频文件
    """
    with open(file, 'rb') as f:
        data = f.read()
    return data

def identifyComplete(text):
    """
    识别成功
    """
    print("识别的内容为：")
    print(text)
    maps = {
        '模型对话': ['模型对话。', '模型对话', '模型对话，', '对话。', '行对话。'],
        '视觉问答': ['视觉问答。', '视觉问答', '视觉问答，', '问答。', '学问答。'],
        '意图理解': ['意图理解。', '意图理解', '意图理解，', '理解。']
    }
    if (text == '再见。' or text == '拜拜。'):
        play(music_exit) # 关闭系统播放反馈语音
        exit()
    if text in maps['打开百度']:
        webbrowser.open_new_tab('https://www.baidu.com')
        play('./audio/openbaidu.wav') # 识别到播放反馈语音
    else:
        play('./audio/none.wav') # 未匹配口令播放反馈语音
    print('操作完成')

client = mqtt_init()
maps = {
        '模型对话': ['模型对话。', '模型对话', '模型对话，', '对话。', '行对话。'],
        '视觉问答': ['视觉问答。', '视觉问答', '视觉问答，', '问答。', '学问答。', '觉问答。'],
        '意图理解': ['意图理解。', '意图理解', '意图理解，', '理解。', '胡理解。', '图理解。']
        }
if __name__ == "__main__":
    while endSnow == False:
        interrupted = False
        # 实例化snowboy，第一个参数就是唤醒识别模型位置
        detector = snowboydecoder.HotwordDetector('xiaozhi.pmdl', sensitivity=0.5)
        print('等待唤醒')
        # snowboy监听循环
        detector.start(detected_callback=detected,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)
        my_record() # 唤醒成功开始录音
        TOKEN = fetch_token() # 获取token
        # print(TOKEN)
        speech = get_audio(FILEPATH)
        result = speech2text(speech, TOKEN, int(1537))
        print("识别的内容为：", result)
        

        # client.publish(topic="airbox", payload=result, qos=2)
        # print("话题发布成功")  

        if type(result) == str:
            # identifyComplete(result.strip('，'))
            text = result.strip('，')
            if (text == '再见。' or text == '拜拜。'):
                play(music_exit) # 关闭系统播放反馈语音
                exit()
            if text in maps['模型对话']:
                play('./audio/MXDH.wav') # 识别到播放反馈语音
                client.publish(topic="airbox", payload="模型对话", qos=2)
                print("话题发布成功")  
            elif text in maps['视觉问答']:
                play('./audio/SJWD.wav') # 识别到播放反馈语音: 
                client.publish(topic="airbox", payload="视觉问答", qos=2)
                print("话题发布成功")  
            elif text in maps['意图理解']:
                play('./audio/YTLJ.wav') # 识别到播放反馈语音: 
                client.publish(topic="airbox", payload="意图理解", qos=2)
                print("话题发布成功")  
            else:
                if(len(result) > 4):
                    client.publish(topic="airbox", payload=result, qos=2)
                    print("话题发布成功")  
                    play('./audio/dong.wav') # 未匹配口令播放反馈语音
            print('操作完成')