# SQ12345-Spider使用Python实现的SQ12345网站发帖检测
功能：爬取SQ12345网站发帖，对发帖标题及内容进行关键字过滤，符合过滤条件的帖子调用微信企业号通知。
## 使用方法 ##
Python版本： Python 3.4 & Python 3.5测试通过，不兼容Python 2.x

依赖包：`requests`、`beautifulsoup4`

运行前需要将微信的`corpid`及`corpsecret`写入`wchat`文件中，此文件为文本文件，第一行是`corpid`，第二行是`corpsecret`，将此文件置于根目录下再运行`Spider.py`文件即可。

本爬虫基于
https://github.com/g199209/Spider
修改而来。
