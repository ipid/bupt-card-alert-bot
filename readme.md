## 北邮校园卡消费记录通知机器人

The bot is now testing in production. Use it with causion.

此 Bot 正通过生产环境来测试代码，请谨慎使用。



#### 所需环境

Python 3.6+，建议使用 venv。

#### 项目部署

1、通过 `git clone` 或下载 zip 包来下载本项目文件并解压；

2、切换到 main.py 所在目录后，安装依赖包：

```bash
pip install -r requirements.txt
```

3、自行建立一个 Telegram Bot（教程：[How to create your own Telegram bot](https://www.teleme.io/articles/create_your_own_telegram_bot?hl=zh-hans)）。

4、建立好之后，将 config.sample.json 改名为 config.json，并填写其中的内容。

5、部署 Telegram 机器人。运行命令：

```bash
python main.py --deploy
```

并按照指示部署机器人。

6、持续地运行服务器：

```bash
nohup python main.py &
```

在此步，你可以使用 supervisor 等工具来管理此应用，以让你的 bot 高可用。



#### 版权

本代码按照 MIT 协议发布。征得同意使用了 [FredericDT/BUPTCardScraper](https://github.com/FredericDT/BUPTCardScraper) 的部分代码。