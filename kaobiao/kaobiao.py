#-*-coding:utf-8-*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from flask import Flask,render_template, request, make_response
from spider import KaobiaoSpider

app = Flask(__name__)


@app.route("/kaobiao", methods=["POST", "GET"])
def kaobiao():
	if request.method == "POST":
	    SID = request.form.get("SID")
	    password = request.form.get("password")
	    spider = KaobiaoSpider(SID, password)
	    spider.post()
	    if not spider.flag:
	    	return make_response("<div align='center'>帐号或密码错误!</div>")
	    return render_template("kaobiao.html", data=spider.kaobiao, 
	    				ktype=spider.kaobiao_type, slen=len(spider.kaobiao))
	return render_template("login.html")


if __name__ == '__main__':
	app.run(debug=True)