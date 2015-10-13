# -*- coding: utf-8 -*-
import json
from flask import Flask, request, make_response
from LibrarySpider import LibrarySpider

app = Flask(__name__)


@app.route("/library", methods=["POST"])
def library():
    SID = request.form["SID"]
    password = request.form["password"]
    spider = LibrarySpider(SID, password)
    spider.post()
    spider.main()
    if not spider.flag:
        wrong = {
            "errcode": 1,
            "errmsg": "wrong_id"
        }
        libraryJson = wrong
    else:
        libraryJson = spider.libraryJson

    resp = make_response(json.dumps(libraryJson), 200)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Content-type'] = 'application/json'
    return resp


if __name__ == "__main__":
    app.debug = True
    app.run()
