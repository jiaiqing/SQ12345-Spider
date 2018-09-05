# -*- coding: utf-8 -*-

######################
# Author : jiaiqing
# Data   : 2018-08-05
# Brief  : 宿迁12345发帖提醒
######################

import WebsiteBase
import requests, re, time
from bs4 import BeautifulSoup


class SQ12345(WebsiteBase.WebsiteBase):
    def __init__(self, Name, DBName, AgentID, KeyWords, SpecialKeyWords = []):
        super().__init__(Name, DBName, AgentID, True, KeyWords, 7, 'utf-8')

    # Return number of pages
    def GetPageRange(self):
        return range(1, 8)

    # Use requests to get the main page, return response
    def GetMainPage(self):
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        }
        return requests.get('http://bbs.suqian.cn/forum.php?mod=forumdisplay&fid=43&filter=author&orderby=dateline',headers=headers, timeout=21)


    # Return soup
    def GetEnclose(self, soup):
        return soup.find('table')

    # Return list of tag
    def GetTags(self, soup):
        return soup.find_all('tbody')

    # Return title string
    def GetTitle(self, tag):
        # Get Title Name
        if not tag.find('a', class_='s xst'):
            TitleName = ''
        else:
            TitleName = tag.find('a', class_='s xst').string
        TitleName = re.sub(r'\s', '', TitleName)
        return TitleName

    # Return Content string
    def GetContent(self, tag):
        # Get Content string
        Content = ''
        return Content

    def GetTitle_ID(self, tag):
        # Get GetTitle_ID
        str = tag.get('id')
        if str is None:
            return 0
        if re.match(r'^[0-9a-zA-Z\_]*\_[0-9a-zA-Z\_]*$', str):
            id = int(str.split('_')[-1])
        else:
            id = 0
        return id

    # Return URL string
    def GetURL(self, tag):
        if not tag.find('a', class_='s xst'):
            url = ''
        else:
            url = tag.find('a', class_='s xst')['href']
        return url

    def CheckKeywords(self, Keywords):
        pass


    # Return publish time
    def GetPublishTime(self, tag):
        return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))

    # Addditon check, return True if unused
    def AdditionCheck(self, tag):
        return True

    # Return brief string
    def GetBrief(self, tag, keywordstring):
        # Generate Brief
        BriefString = keywordstring
        return BriefString
