# -*- coding: utf-8 -*-
import redis
import json
from flask import Flask, request, make_response
from LibrarySpider import LibrarySpider

app = Flask(__name__)
r = redis.Redis(host="localhost", port=6379, db=1)


@app.route("/library", methods=["POST"])
def library():
    SID = request.form["SID"]
    password = request.form["password"]
    if not r.get("%s" % SID):
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
            r.set("%s" % SID, libraryJson)
    else:
        libraryJson = eval(r.get("%s" % SID))

    resp = make_response(json.dumps(libraryJson), 200)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Content-type'] = 'application/json'
    return resp


if __name__ == "__main__":
    app.debug = True
    app.run()
