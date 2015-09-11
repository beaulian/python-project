#coding=utf-8

import re
import pymongo
import random
import Image, ImageDraw, ImageFont, ImageFilter
import StringIO
from flask import Flask, request, render_template, session, make_response, jsonify


numbers = ''.join(map(str, range(10)))
chars = ''.join((numbers))


def create_validate_code(size=(120, 30),
                         chars=chars,
                         mode="RGB",
                         bg_color=(255, 255, 255),
                         fg_color=(255, 0, 0),
                         font_size=18,
                         font_type="FreeSans.ttf",
                         length=4,
                         draw_points=True,
                         point_chance = 2):
    '''''
    size: 图片的大小，格式（宽，高），默认为(120, 30)
    chars: 允许的字符集合，格式字符串
    mode: 图片模式，默认为RGB
    bg_color: 背景颜色，默认为白色
    fg_color: 前景色，验证码字符颜色
    font_size: 验证码字体大小
    font_type: 验证码字体，默认为 Monaco.ttf
    length: 验证码字符个数
    draw_points: 是否画干扰点
    point_chance: 干扰点出现的概率，大小范围[0, 50]
    '''

    width, height = size
    img = Image.new(mode, size, bg_color) # 创建图形
    draw = ImageDraw.Draw(img) # 创建画笔

    def get_chars():
        '''''生成给定长度的字符串，返回列表格式'''
        return random.sample(chars, length)

    def create_points():
        '''''绘制干扰点'''
        chance = min(50, max(0, int(point_chance))) # 大小限制在[0, 50]

        for w in xrange(width):
            for h in xrange(height):
                tmp = random.randint(0, 50)
                if tmp > 50 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    def create_strs():
        '''''绘制验证码字符'''
        c_chars = get_chars()
        strs = '%s' % ''.join(c_chars)

        font = ImageFont.truetype(font_type, font_size)
        font_width, font_height = font.getsize(strs)

        draw.text(((width - font_width) / 3, (height - font_height) / 4),
                    strs, font=font, fill=fg_color)

        return strs

    if draw_points:
        create_points()
    strs = create_strs()

    # 图形扭曲参数
    params = [1 - float(random.randint(1, 2)) / 100,
              0,
              0,
              0,
              1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 500,
              0.001,
              float(random.randint(1, 2)) / 500
              ]
    img = img.transform(size, Image.PERSPECTIVE, params) # 创建扭曲

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE) # 滤镜，边界加强（阈值更大）

    return img, strs


app = Flask(__name__)
app.secret_key = "hard to guess"

conn = pymongo.Connection("localhost", 27017)    # 连接数据库
db = conn.student                                # 数据库
coll = db.stuinfo                                # 集合


@app.route('/securityCode', methods=["GET"])
def get_code():
    # 把strs发给前端,或者在后台使用session保存
    code_img, strs = create_validate_code()
    session["code"] = strs

    buf = StringIO.StringIO()
    code_img.save(buf,'JPEG',quality=70)

    buf_str = buf.getvalue()
    response = app.make_response(buf_str)
    response.headers['Content-Type'] = 'image/jpeg'
    return response


@app.route("/stuinfo", methods=["GET"])
def getstuinfo():
    name = request.args.get("name")
    code = request.args.get("code")
    strings = session["code"]
    if name:
        if code:
            if code == strings:
                info_cursor = coll.find({"name": name})
                real_info = []
                for i in info_cursor:
                    real_info.append(i)

                return render_template("stuinfo.html", infos=real_info)
            else:
                return make_response("<p style='color:red;'>验证码验证失败</p>")
        else:
            return make_response("<p style='color:red;'>请填写验证码</p>")
    else:
        return make_response("<p style='color:red;'>请输入名字</p>")


@app.route("/roommates",methods=["POST"])
def get_roommates():
    yuan = request.form["yuan"]
    dong = request.form["dong"]
    room = request.form["room"]

    address = yuan + dong
    roommates_cursor = coll.find({"accommodation": address, "roomID": int(room)})
    roommates = []
    for roommate in roommates_cursor:
        del roommate["_id"]
        roommates.append(roommate)

    resp = make_response(jsonify({"info": roommates}))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route("/api/stuinfo/scale", methods=["POST"])
def get_scale():
    classID = request.form["classID"]

    classmates = []
    for classmate_cursor in coll.find({"classroom": classID}):
        classmates.append(classmate_cursor)
    boys = []
    girls = []
    for classmate in classmates:
        del classmate["_id"]
        if classmate["sex"] == u"男":
            boys.append(classmate)
        else:
            girls.append(classmate)
    sum = len(boys) + len(girls)
    boy_count = len(boys)
    girl_count = len(girls)
    resp2 = make_response(jsonify({"sum": sum, "boys": boy_count, "girls": girl_count, "classroom": classID}))
    resp2.headers["Access-Control-Allow-Origin"] = "*"
    return resp2

if __name__ == "__main__":
    app.run(debug=True)



