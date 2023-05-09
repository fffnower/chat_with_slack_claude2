# chat_with_slack_claude2

与chat_with_slack_claude的区别：
1.可以真正重置对话（原理是弃用原先的消息列，开辟新的对话）
2.使用前，你需要在slack里建一个私有频道，并通过@Claude的方式，把Claude加到频道中去。
3.你需要获取 Claude的app_id

你需要安装一些库:

```
pip install slack
pip install slackclient
```

你需要在api.slack.com上做一些设置，并获取一些参数用来调用slack的api；

你需要网页端访问与Claude的聊天，并获取一些参数用来调用slack的api。

你需要将获取的参数，填入chat.py对应的位置（见注释）

请注意，你无法使用 “斜杠命令”，详见 https://api.slack.com/interactivity/slash-commands

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

## 2.频道ID

- 网页打开与Claude聊天的界面，此时网址：https://app.slack.com/client/字符串1/字符串1/thread/字符串2-1683631995.739509

- **你的 频道ID：** 字符串2

## 3.claude_id

-
