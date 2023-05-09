# chat_with_slack_claude2

与[chat_with_slack_claude](https://github.com/fffnower/chat_with_slack_claude)的区别：

1.曲线方法，实现真正重置对话，即'/reset'（原理是弃用原先的消息列，开辟新的对话，不清楚开辟过多消息列会有什么负面影响）

2.你需要额外获取 Claude 的成员ID

3.试用范围: 一般来说，是用不到'/reset'的，你可以对他说，“请忘记我们之前的所有对话，重新开始。”，

他会假装忘记所有，不会再联系上下文进行回复了（实际还是记着）；

此时推荐你用 [chat_with_slack_claude](https://github.com/fffnower/chat_with_slack_claude)，

'/reset'是您需要完全重置Claude'性格'的时候，需要调用的方法，有些道德感比较强的'性格'可能不适用于与你的对话，原因我不多说...

---

你需要安装一些库:

```
pip install slack
pip install slackclient
```

你需要在api.slack.com上做一些设置，并获取一些参数用来调用slack的api；

你需要网页端访问与Claude的聊天，并获取一些参数用来调用slack的api。

你需要下载slack桌面端，并获取一些参数用来调用slack的api。

你需要将获取的参数，填入chat.py对应的位置（见注释）

请注意，你无法使用 “斜杠命令”，详见 https://api.slack.com/interactivity/slash-commands （本项目仅仅是，模拟了一下使用/reset后的效果）

---

## 1. 获取 User OAuth Token

- 进入网址：https://api.slack.com/ --> 点击右上角的【Your apps】 --> 弹出窗口【Create an app】 --> 点击【From scratch】

- 填写app名称以及选择工作空间（例：name: Bot, workspace: chat） --> 点击【Create App】

- 点击左侧边栏上的【OAuth & Permissions】 --> 下拉至【Scopes】卡片 --> 【User Token Scopes】 项下添加权限，如下：

  - channels:history
  - channels:read
  - chat:write
  - files:write
  - groups:history
  - groups:read
  - im:history
  - im:read
  - im:write
  - mpim:history
  - mpim:read
  - team:read
  - users:read

- 回到顶部【OAuth Tokens for Your Workspace】栏，点击【Install to Workspace】，然后确认授权即可

- **你的 User OAuth Token：** 

![image](https://user-images.githubusercontent.com/32289652/236893002-4ab20f60-4db8-4964-a6ce-cb5943c27c33.png)

---

## 2.频道ID

- 网页打开与新建私有频道的界面，此时网址：https://app.slack.com/client/字符串1/字符串2/thread/字符串2-1683631995.739509 

  或 https://app.slack.com/client/字符串1/字符串2

- **你的 频道ID：** 字符串2

---

## 3.claude_id

- 首先你需要在频道的输入框中 键入 @Claude 回车， 并同意应用接入你的频道。

- 你可通过[https://api.slack.com/](https://api.slack.com/events/app_mention)中的api去调取成员id

- 另外一个比较便捷的方法是，下载slack的桌面客户端，【应用】 --> 选中Claude右键 --> 【查看应用详情】 --> 复制【成员ID】

- 至此 你得到了你的 **claude_id：** 成员ID

![image](https://github.com/fffnower/chat_with_slack_claude2/assets/32289652/c71828f5-c87b-47a2-96c8-7efa266ff838)

