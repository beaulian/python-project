# coding=utf-8

import requests
from hashlib import md5
from BeautifulSoup import BeautifulSoup


# 基类也要指定object父类
# 所有类都必须要有继承的类,如果什么都不想继承，就继承到object类
class BaseSpider(object):
	def __init__(self, SID, password):

            self.SID = SID
            self.password = password
            self.flag = True   # 判断是否登录进去了
            self.headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, \
                                     like Gecko) Chrome/38.0.2125.122 Safari/537.36"
            }

            def __str__(self):
                return "yiban spider"

            def post(self):
                pass


class KaobiaoSpider(BaseSpider):
    def __init__(self, SID, password):
        self.login_url =  "http://202.202.1.176:8080/_data/index_login.aspx"
        self.kaobiao_url = "http://202.202.1.176:8080/KSSW/stu_ksap_rpt.aspx"
        self.headers = {
                'Content-Type': 'application/x-www-form-urlencode',
                'Host': '202.202.1.176:8080',
                'Origin': 'http://202.202.1.176:8080',
                'Referer': 'http://202.202.1.176:8080/KSSW/stu_ksap.aspx'
        }
        self.hash_value = md5(SID+md5(password).hexdigest()[0:30].upper()+"10611").hexdigest()[0:30].upper()
        self.postdata = {
                    'txt_dsdsdsdjkjkjc': SID,
                    'txt_dsdfdfgfouyy': password,
                    'Sel_Type': 'STU',
                    '__VIEWSTATEGENERATOR': 'CAA0A5A7',
                    'efdfdfuuyyuuckjg': self.hash_value
        }
        self.postkaobiao = {
                'sel_xnxq': '20150',
                'sel_lc': '2015001,2015-2016学年第一学期集中考试周'.decode("utf-8").encode("gb2312"),
                'btn_search': "检索".decode("utf-8").encode("gb2312")
        }
        self.kaobiao = []
        self.kaobiao_type = ""
        super(KaobiaoSpider, self).__init__(SID, password)

    def post(self):
        s = requests.Session()
        r1 = s.post(self.login_url, data=self.postdata, headers=self.headers)
        r2 = s.post(self.kaobiao_url, data=self.postkaobiao, headers=self.headers)
        soup = BeautifulSoup(r2.text)
        td =soup("td")
        try:
            del td[11]
        except IndexError:
            self.flag = False
        self.kaobiao_type = td[0].text
        for key in range(3,len(td),8):
            self.kaobiao.append([td[key+1].text, td[key+2].text, td[key+5].text, td[key+6].text])

