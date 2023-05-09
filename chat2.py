import time
import os
from slack import WebClient
from slack.errors import SlackApiError

# User OAuth Token
userOAuthToken = ''
# 频道ID
channel_id = ''
# claude_id
claude_id = ''
# 连接slack
client = WebClient(token=userOAuthToken)

print("""\

***************************************************
    你好! 此程序使用Slack的API实现与Claude对话;
    两次回车换行进行交互, 请您开始吧!
    输入'/reset'重置对话。
***************************************************\

    """)

# 初始化，配置文件不存在，创建一个空配置文件
file_name = 'save_conversations_timestamp.ini'
if not os.path.exists(file_name):
    with open(file_name, 'w') as f:
        f.write('')  

def get_print_new_msg():
    global time_step

    len_new_msg = 1
    while True:
        try:
            new_msg = client.conversations_replies(
                token=userOAuthToken, 
                channel=channel_id, 
                # ts 为空的情况下会新建一个对话（/reset的实现方式）
                ts=conversations_timestamp,
                oldest=last_msg_timestamp
                )
        except SlackApiError as e:
            print(f"Error sending message: {e}")
        
        # \n&gt; _*Please note:* 
        # 当你的回复被*Please note:*提示时, 会有多条消息，我们调整获取策略，这里只获取第二条（第一条是我们的输入）
        idx = 1 - len(new_msg['messages'])
        new_msg = new_msg['messages'][idx]['text']
        # 未回复
        if new_msg == '_Typing…_': 
            time.sleep(time_step)
            continue
        # 开始回复，逐步打印
        if new_msg.endswith('Typing…_'):
            print(new_msg[len_new_msg:-11], end='')
            len_new_msg = len(new_msg)-11
            time.sleep(time_step)
        else:
            print(new_msg[len_new_msg:],end = '[END]\n\n')
            break
    return new_msg[1:]

def get_user_input():
    lines = []
    while not lines:
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
    return "\n".join(lines)

def send_msg(message):
    global conversations_timestamp, last_msg_timestamp

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

# 从配置文件中获取消息列标识
with open(file_name, 'r') as f:
    first_line = f.readline()  
    if not first_line:
        conversations_timestamp = None
    else:
        conversations_timestamp = first_line

# 消息列最后一次的回复时间戳
last_msg_timestamp = None
# 更新回复的时间间隔
time_step = 0.5

# 主程序
def chat():
    global conversations_timestamp
    while True:
        # 获取输入
        print('You:')
        message = get_user_input()
        if message == '/reset':
            conversations_timestamp = None
            print('重置对话！')
            continue

        # 发送输入
        send_msg(f'<@{claude_id}>' + message)

        # 获取、打印回复（获取是为了以后接入其他api，目前无用）
        print('Claude:')
        time.sleep(time_step + 1)
        new_msg = get_print_new_msg()

# 运行
if __name__ == '__main__':
    chat()
