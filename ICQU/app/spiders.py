# coding=utf-8

import json
import requests
import threading
from hashlib import md5
from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup as Beautiful


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


class LibrarySpider(BaseSpider):

    def __init__(self, SID, password):

        self.response = None
        self.prefix_url = "http://lib.cqu.edu.cn"

        self.prefixUrl = "https://sso.lib.cqu.edu.cn:8949/adlibSso/login"
        self.firstUrl = "https://sso.lib.cqu.edu.cn:8949/adlibSso/login? \
                        service=http%3A%2F%2Flib.cqu.edu.cn%2Fmetro%2Flogin.htm"
        self.secondUrl = "http://lib.cqu.edu.cn/metro/login.htm"
        self.NowBorrowUrl = "http://lib.cqu.edu.cn/metro/readerNowBorrowInfo.htm"
        self.ReadBookingUrl = "http://lib.cqu.edu.cn/metro/readerBooking.htm"
        self.OutDateInfoUrl = "http://lib.cqu.edu.cn/metro/outDateInfo.htm"
        self.ReaderArrearageUrl = "http://lib.cqu.edu.cn/metro/readerArrearage.htm"

        self.headers = {
            'Host': 'sso.lib.cqu.edu.cn:8949',
            'Origin': 'https://sso.lib.cqu.edu.cn:8949',
            "Content-Type": "application/x-www-form-urlencoded",
            'Referer': 'https://sso.lib.cqu.edu.cn:8949/adlibSso/login',
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, \
                                         like Gecko) Chrome/38.0.2125.122 Safari/537.36"
        }
        self.s = requests.Session()

        self.libraryJson = {"NowBorrow": {}, "ReadBooking": {}, "OutDateInfo": {}, "ReaderArrearage": {}}
        super(LibrarySpider, self).__init__(SID, password)

    def __str__(self):
        return "library spider"

    def get_args(self, url):
        try:
            response = self.s.get(url)
        except IOError as e:
            return e
        return response

    def analyze_args(self):
        resp = self.get_args(self.prefixUrl)
        soup = BeautifulSoup(resp.text, fromEncoding="gbk")
        inp = soup("input")
        lt = str(inp[3]).split('value="')[1].split('"')[0]
        execution = str(inp[4]).split('value="')[1].split('"')[0]
        return [lt, execution, resp.cookies]

    def post(self):
        args = self.analyze_args()
        lt = args[0]
        execution = args[1]
        postdata = {
            "username": self.SID,
            "password": self.password,
            "id": "null",
            "lt": lt,
            "execution": execution,
            "_eventId": "submit",
            "submit": "登录"
        }
        req = self.s.post(self.firstUrl, data=postdata, headers=self.headers)
        self.response = req

    def reRew(self, strnumber):
        req2 = self.s.get("http://lib.cqu.edu.cn/metro/renewbook.htm?stripNumber=%s" % strnumber)
        soup = Beautiful(req2.text)
        div = soup.find_all("div", attrs={"class": "tishi"})[0]
        tishi = div.find_all("p")[1].text
        return tishi

    def post_NowBorrow(self):
        req = self.s.get(self.NowBorrowUrl).text     # 不能乱传headers,最好不要有
        soup = Beautiful(req)
        if soup("p")[-1].text == "没有相关记录！".decode("utf-8"):
                self.libraryJson["NowBorrow"]["statusinfo"] = "none"
        else:
            try:
                table = soup.find_all("table", attrs={"class": "liebiao"})[0]
            except IndexError as e:
                self.flag = False
                return

            font = soup.find_all("font", attrs={"class": "redfont"})

            alreadyBorrow = font[0].text
            currentBorrow = font[2].text
            notComment = font[3].text
            sumBorrow = font[4].text
            self.libraryJson["NowBorrow"]["alreadyBorrow"] = alreadyBorrow
            self.libraryJson["NowBorrow"]["notComment"] = notComment
            self.libraryJson["NowBorrow"]["sumBorrow"] = sumBorrow
            self.libraryJson["NowBorrow"]["currentBorrow"] = currentBorrow

            tr = table.find_all("tr")
            th = tr[0].find_all("th")
            slen = len(th)

            for i in range(int(currentBorrow)):
                self.libraryJson["NowBorrow"]["book_%s" % str(i+1)] = {}
                td = tr[i+1].find_all("td")
                for j in range(slen):
                    if j == 0:
                        self.libraryJson["NowBorrow"]["book_%s" % str(i+1)][th[j].text.strip()] = self.prefix_url + td[j].img["src"]
                    elif j == 1:
                        self.libraryJson["NowBorrow"]["book_%s" % str(i+1)][th[j].text.strip()] = [self.prefix_url+td[j].a["href"], td[j].text]
                    elif j < 7:
                        self.libraryJson["NowBorrow"]["book_%s" % str(i+1)][th[j].text.strip()] = td[j].text
                    else:
                        self.libraryJson["NowBorrow"]["book_%s" % str(i+1)][th[j].text.strip()] = td[j].input["onclick"]

    def post_ReadBooking(self):
        req = self.s.get(self.ReadBookingUrl, cookies=self.response.cookies).text
        soup = Beautiful(req)

        if soup("p")[-1].text == "没有相关记录！".decode("utf-8"):
            self.libraryJson["ReadBooking"]["statusinfo"] = "none"
        else:
            try:
                table = soup.find_all("table", attrs={"class": "liebiao"})[0]
            except Exception as e:
                return e

            tr = table.find_all("tr")
            count_book = len(tr[1:])
            self.libraryJson["ReadBooking"]["count_book"] = str(count_book)
            th = tr[0].find_all("th")
            slen = len(th)

            for i in range(count_book):
                self.libraryJson["ReadBooking"]["book_%s" % str(i+1)] = {}
                td = tr[i+1].find_all("td")
                for j in range(1, slen):
                    if j == 1:
                        self.libraryJson["ReadBooking"]["book_%s" % str(i+1)][th[j].text.strip()] = self.prefix_url + td[j].img["src"]
                    elif j == 2:
                        self.libraryJson["ReadBooking"]["book_%s" % str(i+1)][th[j].text.strip()] = [self.prefix_url+td[j].a["href"], td[j].text]
                    else:
                        self.libraryJson["ReadBooking"]["book_%s" % str(i+1)][th[j].text.strip()] = td[j].text

    def post_OutDateInfo(self):
        req = self.s.get(self.OutDateInfoUrl, cookies=self.response.cookies).text
        soup = Beautiful(req)
        if soup("p")[-1].text == "没有相关记录！".decode("utf-8"):
            self.libraryJson["OutDateInfo"]["statusinfo"] = "none"
        else:
            try:
                table = soup.find_all("table", attrs={"class": "liebiao"})[0]
            except IndexError as e:
                return
            tr = table.find_all("tr")
            count_book = len(tr[1:])
            self.libraryJson["OutDateInfo"]["count_book"] = str(count_book)
            th = tr[0].find_all("th")
            slen = len(th)

            for i in range(count_book):
                self.libraryJson["OutDateInfo"]["book_%s" % str(i+1)] = {}
                td = tr[i+1].find_all("td")
                for j in range(slen):
                    if j == 0:
                        self.libraryJson["OutDateInfo"]["book_%s" % str(i+1)][th[j].text.strip()] = self.prefix_url + td[j].img["src"]
                    elif j == 1:
                        self.libraryJson["OutDateInfo"]["book_%s" % str(i+1)][th[j].text.strip()] = [self.prefix_url+td[j].a["href"], td[j].text]
                    else:
                        self.libraryJson["OutDateInfo"]["book_%s" % str(i+1)][th[j].text.strip()] = td[j].text

    def post_ReaderArrearage(self):
        req = self.s.get(self.ReaderArrearageUrl, cookies=self.response.cookies).text
        soup = Beautiful(req)
        if soup("p")[-1].text == "没有相关记录！".decode("utf-8"):
            self.libraryJson["ReaderArrearage"]["statusinfo"] = "none"
        else:
            try:
                table = soup.find_all("table", attrs={"class":"liebiao"})[0]
            except Exception as e:
                return

            font = soup.find_all("font",attrs={"class":"redfont"})[0].text
            self.libraryJson["ReaderArrearage"]["sumMoney"] = font

            tr = table.find_all("tr")
            count_book = len(tr[1:])
            self.libraryJson["ReaderArrearage"]["count_book"] = str(count_book)
            th = tr[0].find_all("th")
            slen = len(th)

            for i in range(count_book):
                self.libraryJson["ReaderArrearage"]["book_%s" % str(i+1)] = {}
                for j in range(slen):
                    td = tr[i+1].find_all("td")
                    self.libraryJson["ReaderArrearage"]["book_%s" % str(i+1)][th[j].text.strip()] = td[j].text

    def main(self):
        threads = []
        t1 = threading.Thread(target=self.post_NowBorrow)
        threads.append(t1)
        t2 = threading.Thread(target=self.post_ReadBooking)
        threads.append(t2)
        t3 = threading.Thread(target=self.post_OutDateInfo)
        threads.append(t3)
        t4 = threading.Thread(target=self.post_ReaderArrearage)
        threads.append(t4)

        for t in threads:
            t.setDaemon(True)
            t.start()
        for t in threads:
            t.join()


class YikatongSpider(BaseSpider):
    def __init__(self, SID, password):

        self.login_url = "http://ids.cqu.edu.cn/amserver/UI/Login"
        self.kard_url = "http://i.cqu.edu.cn/welcome/getUserInfo.do"
        self.postdata = {
            "IDToken0": "",
            "IDToken1": SID,
            "IDToken2": password,
            "IDButton": "Submit",
            "goto": "",
            "encoded": "true",
            "gx_charset": "UTF-8"
        }
        self.result = []
        super(YikatongSpider, self).__init__(SID, password)

    def post(self):
        # print self.postdata
        s = requests.Session()    # 自动管理cookies
        req = s.post(self.login_url, data=self.postdata, headers=self.headers)
        req2 = s.get(self.kard_url, headers=self.headers)
        # print req2.text.encode("utf-8")
        soup = BeautifulSoup(req2.text)
        try:
            remainder1 = soup("td")[-5].text.split("元".decode("utf-8"))[0] + "元".decode("utf-8")
            penalty1 = soup("td")[-1].text.split("元".decode("utf-8"))[0] + "元".decode("utf-8")
        except IndexError:
            self.flag = False
            return
        self.result = [remainder1, penalty1]


class KebiaoSpider(BaseSpider):
    def __init__(self, SID, password):

        self.slogin_url = "http://syjx.cqu.edu.cn/login"
        self.skebiao_url = "http://syjx.cqu.edu.cn/admin/schedule/getPrintStudentSchedule"
        self.postdata = {
            "username": SID,
            "password": md5(password).hexdigest()
        }
        self.postdata2 = {
            "stuNum": SID
        }
        self.sresult = {}
        super(KebiaoSpider, self).__init__(SID, password)

    def post(self):
        s = requests.Session()
        req = s.post(self.slogin_url, data=self.postdata, headers=self.headers)
        req2 = s.post(self.skebiao_url, data=self.postdata2, headers=self.headers)
        if not req2.text:
            self.flag = False
            return
        self.sresult = json.loads(req2.text)


class GradeSpider(BaseSpider):
    def __init__(self, SID, password, year, team_number):

        self.login_url =  "http://202.202.1.176:8080/_data/index_login.aspx"
        # self.prefix_core_url = "http://202.202.1.176:8080/xscj/Stu_MyScore.aspx"
        self.core_url = "http://202.202.1.176:8080/xscj/Stu_MyScore_rpt.aspx"
        self.hash_value = md5(SID+md5(password).hexdigest()[0:30].upper()+"10611").hexdigest()[0:30].upper()
        self.postdata = {
                    'Sel_Type': 'STU',
                    'txt_dsdsdsdjkjkjc': SID,
                    'txt_dsdfdfgfouyy': password,
                    'txt_ysdsdsdskgf': "",
                    "pcInfo": "Mozilla%2F4.0+%28compatible%3B+MSIE+7.0%3B+Windows+NT+6.1%3B+Trident%2F7.0%3B+SLCC2%3B+.NET+CLR+2.0.50727%3B+.NET+CLR+3.5.30729%3B+.NET+CLR+3.0.30729%3B+Media+Center+PC+6.0%3B+.NET4.0C%29x860+SN%3ANULL",
                    "typeName": "%D1%A7%C9%FA",
                    "aerererdsdxcxdfgfg": "",
                    "efdfdfuuyyuuckjg": self.hash_value
        }
        self.postcore = {
                    "sel_xn": year,
                    "sel_xq": team_number,
                    "SJ": "1",
                    'btn_search':'%BC%EC%CB%F7',
                    "SelXNXQ": "2",
                    "zfx_flag": "0"
        }
        self.grade_info = {"课程总数":"","学年学期":"", "课程名称":[],"学分":[],"成绩":[]}
        self.error = False
        super(GradeSpider, self).__init__(SID, password)

    def post(self):
        s = requests.Session()
        req = s.post(self.login_url, data=self.postdata, headers=self.headers)
        # req2 = s.get(self.prefix_core_url, headers=self.headers)
        req2 = s.post(self.core_url, data=self.postcore, headers=self.headers)
        # print req2.text
        # return
        soup = BeautifulSoup(req2.text)
        try:
            td = soup("table")[2]("td")
        except IndexError:
            self.error = True
            return
        self.grade_info["学年学期"] = td[0].text
        count = len(td)/11
        self.grade_info["课程总数"] = count
        if count == 0:
            self.flag = False
            return

        for i in range(len(td)):
            if i % 11 == 1:
                self.grade_info["课程名称"].append(td[i].text)
            elif i % 11 == 2:
                self.grade_info["学分"].append(td[i].text)
            elif i % 11 == 6:
                self.grade_info["成绩"].append(td[i].text)

