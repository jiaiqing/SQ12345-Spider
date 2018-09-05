# -*- coding: utf-8 -*-

######################
# Author : jiaiqing
# Data   : 2018-08-05
# Brief  : 用于获取网站新通知的爬虫基类
######################

import requests, re, time, sqlite3, json, logging
from bs4 import BeautifulSoup


class WebsiteBase:
    # Name : 网站名称
    # DBName ： 数据库名称，不要包含后缀
    # AgentID ： 微信发布时需要用到的AgentID
    # CheckContent ： 是否需要打开URL检查内容，True or False
    # KeyWords : 过滤用关键词List，如果不需要设置为[]
    # SpecialKeyWords : 特殊关键词，不受阈值的影响，只要包含一个即符合要求
    # encoding ： 网站的编码格式，不设置的话默认为utf-8
    def __init__(self, Name, DBName, AgentID, CheckContent, KeyWords, SpecialKeyWords = [], encoding = 'utf-8'):
        self.Name = Name
        self.DBName = DBName + '.db'
        self.AgentID = AgentID
        self.CheckContent = CheckContent
        self.KeyWords = KeyWords
        self.encoding = encoding
        self.SpecialKeyWords = SpecialKeyWords
        self.TITLE_ID = 620600
        self.Tmp_id = 620600
        # Error Status
        self.err = 0

        # Wchat ID & Password
        f = open('wchat')
        self.corpid = f.readline().strip()
        self.corpsecret = f.readline().strip()
        f.close()

        # Init DB
        conn = sqlite3.connect(self.DBName)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'create table Articles (Title TEXT, Content TEXT, URL TEXT, DATE DATETIME, Published INTEGER, Responsed INTEGER)')
        except:
            pass
        cursor.close()
        conn.commit()
        conn.close()

    def GET(self):
        returnErr = None
        # Open DB
        conn = sqlite3.connect(self.DBName)
        cursor = conn.cursor()


        #logging.warning('Getting : ' + self.Name + '......')

        #PageRange = self.GetPageRange()

        try:
            time.sleep(3)
            response = self.GetMainPage()
            response.encoding = self.encoding
        except Exception as err:
            returnErr = err
            #logging.error('    ' + str(response))
            logging.error('    ' + repr(err))

        soup = BeautifulSoup(response.text, 'html5lib')

        #soup = self.GetEnclose(soup)
        tags = self.GetTags(soup)
        #logging.warning('    Number of Pages : ' + str(len(tags)))

        for tag in tags:
            try:
                # Get Title
                Title = self.GetTitle(tag)
                Content = self.GetContent(tag)
                Title_ID = self.GetTitle_ID(tag)
                self.Tmp_id = max(self.Tmp_id, Title_ID)
                if not Title:
                    continue
                #logging.warning('      Checking : ' + Title)

                if Title_ID <= self.TITLE_ID:
                    continue
                #logging.warning('      Checking : ' + Title)
                print(Title)
                print(Title_ID)

                # Get URL
                ContentURL = self.GetURL(tag)
                print(ContentURL)

                # Get time
                PublishTime = self.GetPublishTime(tag)
                print(PublishTime)
            except Exception as err:
                logging.error('      Format Error!')
                logging.error('    ' + repr(err))
                continue

            # Addition Check
            if not self.AdditionCheck(tag):
                continue

            if self.KeyWords:
                # Check Title
                keywordflag = 0
                for keyword in self.KeyWords:
                    if (Title.count(keyword) > 0):
                        cursor.execute(
                            "insert into Articles (Title, Content, URL, DATE, Published,Responsed) values (?, ?, ?, ?, ?, ?)",
                            (Title, Content, ContentURL, PublishTime, 0, 0)
                        )
                        logging.warning('    Updating : ' + Title + '......')
                        keywordflag = 1
                        break
                if (keywordflag == 1):
                    continue
                # Check Content and Title
                if self.CheckContent and ContentURL != '':
                    try:
                        time.sleep(3)
                        header = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                        response = requests.get(ContentURL, timeout=21, headers = header)
                        response.encoding = self.encoding
                    except Exception as err:
                        # returnErr = err
                        logging.error('    ' + ContentURL)
                        logging.error('    ' + repr(err))
                        continue

                    for keyword in self.KeyWords:
                        if (response.text.count(keyword)) > 0:
                            cursor.execute(
                                "insert into Articles (Title, Content, URL, DATE, Published,Responsed) values (?, ?, ?, ?, ?, ?)",
                                (Title, Content, ContentURL, PublishTime, 0, 0)
                            )
                            logging.warning('    Updating : ' + Title + '......')
                            print('Updating:' + Title + 'Success!')
                            break
                continue

        self.TITLE_ID = self.Tmp_id
        # Close DB
        cursor.close()
        conn.commit()
        conn.close()


        if returnErr:
            raise returnErr

    def Update(self):
        #logging.warning('Updating : ' + self.Name + '......')

        # Init Wchat
        access_token = self.InitWchat()
        if not access_token:
            return

        # Open DB
        conn = sqlite3.connect(self.DBName)
        cursor = conn.cursor()

        cursor.execute("select * from Articles where Published = 0")
        unpublished = cursor.fetchall()

        for record in unpublished:
            # Publish
            logging.warning('  Publishing : ' + record[0] + '......')

            newsdata = {'touser': '@all',
                        'msgtype': 'news',
                        'agentid': self.AgentID,
                        'news': {'articles': [{
                            'title': record[0],
                            'description': record[1],
                            'url': record[2]
                        }]}}

            try:
                # time.sleep(1)
                r = requests.post('https://qyapi.weixin.qq.com/cgi-bin/message/send', params=access_token,
                                  data=json.dumps(newsdata, ensure_ascii=False).encode('utf-8'), timeout=21)
            except Exception as err:
                logging.error('    Publish Error!')
                print('    Publish Error!')
                logging.error('    ' + repr(err))
            else:
                if 'errcode' in r.json() and r.json()['errcode'] == 0:
                    logging.warning('    Publish Success!')
                    print('    Publish Success!')
                    cursor.execute("update Articles set Published = 1 where Title = ? and URL = ? and DATE = ?",
                                   (record[0], record[2], record[3]))
                else:
                    logging.error('    Publish Error!')
                    print('    Publish Error!')
                    logging.error('    ' + json.dumps(newsdata, ensure_ascii=False))
                    #logging.error('    ' + r.json())

        # Close DB
        cursor.close()
        conn.commit()
        conn.close()

    def ReportErrStatus(self, errstr, errstate):
        access_token = self.InitWchat()
        if not access_token:
            return

        if errstate:
            newsdata = {'touser': 'g199209',
                        'msgtype': 'news',
                        'agentid': 0,
                        'news': {'articles': [{
                            'title': '云端程序错误',
                            'description': self.Name + ' :\r\n' + errstr,
                        }]}}
        else:
            newsdata = {'touser': 'g199209',
                        'msgtype': 'news',
                        'agentid': 0,
                        'news': {'articles': [{
                            'title': '云端程序正常运行',
                            'description': self.Name + ' :\r\n云端程序已从上次错误中恢复，现已正常运行~\r\n' +
                            '错误共发生' + str(self.err) + '次',
                        }]}}

        try:
            r = requests.post('https://qyapi.weixin.qq.com/cgi-bin/message/send', params=access_token,
                              data=json.dumps(newsdata, ensure_ascii=False).encode('utf-8'), timeout=21)
        except:
            logging.error('Send Wchat Report Error!')

    def InitWchat(self):
        # Init Wchat
        Auth = {'corpid': self.corpid,
                'corpsecret': self.corpsecret}
        try:
            r = requests.get('https://qyapi.weixin.qq.com/cgi-bin/gettoken', params=Auth, timeout=21)
        except Exception as err:
            logging.error('Wchat Init Timeout!!')
            logging.error(repr(err))
            return None
        else:
            if 'access_token' in r.json():
                return {'access_token': r.json()['access_token']}
            else:
                logging.error('Wchat Init Error!!')
                return None

    def GetPageRange(self):
        pass

    def GetMainPage(self, page):
        pass

    def GetEnclose(self, soup):
        pass

    def GetTags(self, soup):
        pass

    def GetTitle(self, tag):
        pass

    def CheckKeywords(self, Keywords):
        pass

    def GetContent(self, tag):
        pass

    def GetTitle_ID(self, tag):
        pass

    def GetURL(self, tag):
        pass

    def GetPublishTime(self, tag):
        pass

    def AdditionCheck(self, tag):
        pass

    def GetBrief(self, tag, keywordstring):
        pass

