"""
pip install pyaudio, pydub, edge_tts, slack_sdk
"""

import threading
import queue
import time

import asyncio
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from pydub import AudioSegment
from pydub.playback import play
import edge_tts
import io
import string

# 创建一个队列存放音频文件
queue = queue.Queue(maxsize=5)

# 定义一个函数用来消费音频文件，这个函数始终执行
def play_sound():
    while True:
        # 取出并播放一个音频文件
        audio = queue.get()
        play(audio)

# 文字转语音
TEXT = """你好，世界！"""
VOICE = "zh-CN-XiaoxiaoNeural"
async def tts(TEXT):
    communicate = edge_tts.Communicate(TEXT, VOICE)
    audio_stream = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_stream.write(chunk["data"])
        # elif chunk["type"] == "WordBoundary":
        #     print(f"WordBoundary: {chunk}")
    audio_stream.seek(0)
    audio = AudioSegment.from_file(audio_stream)
    return audio

# 判断是否tts句子是否是纯标点符号组成的
def is_punctuation(s):
  punctuation = set(string.punctuation + string.whitespace)
  for c in s:
    if c not in punctuation:
      return False
  return True

# 获取时间戳
def get_conversations_timestamp():
    global conversations_timestamp
    # 初始化，配置文件不存在，创建一个空配置文件
    file_name = 'save_conversations_timestamp.ini'
    if not os.path.exists(file_name):
        with open(file_name, 'w') as f:
            f.write('')  
    # 从配置文件中获取消息列标识
    with open(file_name, 'r') as f:
        first_line = f.readline()  
        if not first_line:
            conversations_timestamp = None
        else:
            conversations_timestamp = first_line

# 获取用户输入
def get_user_input():
    print('You:')
    lines = []
    while not lines:
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
    return "\n".join(lines)

# 发送消息
def send_msg(message):
    global conversations_timestamp, last_msg_timestamp
    file_name = 'save_conversations_timestamp.ini'
    try:
        response = client.chat_postMessage(
            channel=channel_id, 
            text=message, 
            thread_ts=conversations_timestamp, 
            as_user=True
            )
    except SlackApiError as e:
        print(f"Error sending message: {e}")
    # 更新消息列最后一次的回复时间戳
    last_msg_timestamp = response['message']['ts']
    # 是否开启新的消息列（/reset的实现方式）
    if not conversations_timestamp:
        conversations_timestamp = response['ts']
        # 配置文件中更新消息列标识
        with open(file_name, 'r+') as f:
            f.seek(0)  
            f.write(conversations_timestamp)  

# 获取回复
def get_print_new_msg():
    print('Claude:')
    global time_step, tts_flag
    print_new_msg = tts_new_msg = 1
    while True:
        try:
            new_msg = client.conversations_replies(
                token=userOAuthToken, 
                channel=channel_id, 
                ts=conversations_timestamp,
                oldest=last_msg_timestamp
                )
        except SlackApiError as e:
            print(f"Error sending message: {e}")
        # \n&gt; _*Please note:* 
        # 当你的回复被*Please note:*提示时，会有多条消息，我们调整获取策略，这里只获取第二条(第一条是我们的输入)
        # 消息长度为1，未回复(是我们的输入)，消息长度为2，正常回复
        if len(new_msg['messages']) == 1: 
            continue
        idx = 1 - len(new_msg['messages'])
        new_msg = new_msg['messages'][idx]['text']
        # 回复生成中
        if new_msg == '_Typing…_': 
            time.sleep(time_step)
            continue
        # 开始生成回复，逐步打印
        if new_msg.endswith('_Typing…_'):
            if tts_flag:
                # 语音分段
                for idx,c in enumerate(new_msg[:-11][::-1]):
                    if c in ",;:!?，。；：！？\n":
                        if is_punctuation(new_msg[tts_new_msg:-11-idx]):
                            continue
                        audio = asyncio.run(tts(new_msg[tts_new_msg:-11-idx]))
                        tts_new_msg = len(new_msg)-11-idx
                        queue.put(audio)
                        break
            # 打印
            print(new_msg[print_new_msg:-11], end='')
            print_new_msg = len(new_msg)-11
            time.sleep(time_step)
        else:
            if tts_flag:
                audio = asyncio.run(tts(new_msg[tts_new_msg:]))
                queue.put(audio)
            print(new_msg[print_new_msg:],end = '[END]\n\n')
            break
    return new_msg[1:]

# 主程序
def chat():
    global conversations_timestamp
    get_conversations_timestamp()
    while True:
        # 获取输入
        message = get_user_input()
        if message == '/reset':
            conversations_timestamp = None
            print('重置对话！')
            continue
        # 发送输入
        send_msg(f'<@{claude_id}>' + message)
        # 获取、打印回复
        time.sleep(time_step + 1)
        new_msg = get_print_new_msg()

# 运行
if __name__ == "__main__":
    print("\n\
    ***************************************************\n\
        你好! 此程序使用Slack的API实现与Claude对话;\n\
        两次回车换行进行交互, 请您开始吧!\n\
        输入'/reset'重置对话。\n\
    ***************************************************\n")

    # 是否开启语音1开启，0关闭
    tts_flag = 0
    # User OAuth Token
    userOAuthToken = ''
    # 频道ID
    channel_id = ''
    # claude_id
    claude_id = ''
    # 连接slack
    client = WebClient(token=userOAuthToken)
    # 消息列最后一次的回复时间戳
    last_msg_timestamp = None
    # 更新回复的时间间隔
    time_step = 1

    if tts_flag:
        # 创建一个线程来打印队列中的元素
        printer_thread = threading.Thread(target=play_sound)
        printer_thread.start()
    chat()
