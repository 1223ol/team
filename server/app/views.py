#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-04-18 21:02:40
# @Author  : daiker (daikersec@gmail.com)
# @Link    : https://daikersec.com
# @Version : $Id$
from flask import request,g,session
from sqlalchemy.sql import func
from app import app,db
from models import *
import json
import sys
import datetime 
import random
import requests
import hashlib
import reply
import receive
                                                                                           
reload(sys)
sys.setdefaultencoding('utf8')
def str2Date(strDate):
    dateList = strDate.split("-")
    # try:
    print strDate
    return datetime.date(int(dateList[0]),int(dateList[1]),int(dateList[2]))
    # except Exception as e:
        # print dateList
def date2Str(myDate):
    return str(myDate.year) + "-" + str(myDate.month) + "-" + str(myDate.day)
"""
sure id is OK
"""
def havaPlan(uid):
    if db.session.query(Plan.startTime).filter_by(uid = uid).order_by(Plan.planId.desc()).first() == None:
        return False
    return True
"""
sure id is OK
"""
def inPlan(myDate,uid):
    if not havaPlan(uid):
        return False
    startDate = db.session.query(Plan.startTime).filter_by(uid = uid).order_by(Plan.planId.desc()).first()[0]
    endDate = db.session.query(Plan.endTime).filter_by(uid = uid).order_by(Plan.planId.desc()).first()[0]
    # print startDate
    # print endDate
    if myDate >= startDate and myDate <= endDate:
        return True
    return False
"""
sure id is OK
"""
def countDays(uid):
    if not havaPlan(uid):
        return 0
    startDate = db.session.query(Plan.startTime).filter_by(uid = uid).order_by(Plan.planId.desc()).first()[0]
    endDate = db.session.query(Plan.endTime).filter_by(uid = uid).order_by(Plan.planId.desc()).first()[0]
    return (endDate - startDate).days

"""
sure id is OK
"""
def balanceCalcu(today,uid):
    # print "today"
    # print today
    allMoney = db.session.query(Plan.Money).filter_by(uid = uid).order_by(Plan.planId.desc()).first()[0]
    # print "allmoney : {i}".format(i = allMoney)
    startDate = db.session.query(Plan.startTime).filter_by(uid = uid).order_by(Plan.planId.desc()).first()[0]
    endDate = db.session.query(Plan.endTime).filter_by(uid = uid).order_by(Plan.planId.desc()).first()[0]
    restDay = (endDate - today).days + 1
    if today >=  datetime.date.today():
        restDay = (endDate - datetime.date.today()).days + 1
    # print restDay
    # print startDate
    # print today + datetime.timedelta(days = -1)
    # print endDate
    spentMon = db.session.query(func.sum(Category.money)).join(Date).filter_by(uid = uid).filter(Date.date.between(startDate,(today + datetime.timedelta(days = -1)))).first()[0]
    if spentMon == None:
        spent = 0
    else:
        spent = spentMon
    # print "spent = {i}".format(i = spent)
    return (allMoney - spent)/restDay


"""
sure id is OK
"""
@app.route('/login')
def login():
    data = {}
    APPID = 'wx69349d4642d367c0'
    SECRET = 'fd33dc688c6e08418787d938dd8ec779'
    JSCODE = request.args.get('js_code')
    url = "https://api.weixin.qq.com/sns/jscode2session?appid={APPID}&secret={SECRET}&js_code={JSCODE}&grant_type=authorization_code".format(APPID=APPID,SECRET=SECRET,JSCODE=JSCODE)
    r = requests.get(url)
    result= eval(r.text)
    openid = result['openid']
    try:
        uid = db.session.query(User.uid).filter_by(openid = openid).first()
        if uid == None:
            print "None,I will add it on database!!!"
            myUser = User(openid)
            db.session.add(myUser)
            db.session.commit()
            print "Yep,I hava add it on database"
            uid = db.session.query(User.uid).filter_by(openid = openid).first()
            print uid
        data['openid'] =  openid
        data['status'] = 'success'
    except Exception as e:
        data['status'] = 'fail'
        raise e
    return json.dumps(data,ensure_ascii=False)

"""
sure id is OK
"""
@app.route('/')
@app.route('/index')
def index():
    data={}
    openid = request.args.get('cookie')
    uid = db.session.query(User.uid).filter_by(openid = openid).first()[0]
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    date = int(request.args.get('date'))  
    if inPlan(datetime.date(year,month,date),uid):
        data['inPlan'] = 1
    else:
        data['inPlan'] = 0
    # if date == '4' :
    #     consumption = 30
    #     balance = 40 - consumption
    # else:
    # try:
    dateId = db.session.query(Date.dateId).filter_by(date = datetime.date(year,month,date),uid=uid).first()
    days = countDays(uid)
    if dateId == None:
        data['consumption']= 0
        data['isSet'] = 0
    else:
        consumption = db.session.query(func.sum(Category.money)).filter_by(dateId = dateId[0]).first()[0]
        if consumption == None:
            data['consumption'] = 0
        else:
            data['consumption'] = consumption
        data['isSet'] = 1
    days = countDays(uid)
    print data['consumption']
    if inPlan(datetime.date(year,month,date),uid) and days != 0:
        money = db.session.query(Plan.Money).filter_by(uid = uid).order_by(Plan.planId.desc()).first()[0]
        print data['consumption']
        data['balance'] =  round((balanceCalcu(datetime.date(year,month,date),uid) - data['consumption']),2)
    else:
        data['balance'] = 0
    # except Exception as e:
        # raise e
    # data['consumption']=consumption
    # data['balance']=balance
    print data
    return json.dumps(data,ensure_ascii=False) 

# @app.route("/showPlan")
# def showPlan():
#     # print(db.session.query('user').first())
#     return "123"
"""
sure id is OK
"""
@app.route("/showBill")
def showBill():
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    date = int(request.args.get('date'))
    openid = request.args.get('cookie')
    uid = db.session.query(User.uid).filter_by(openid = openid).first()[0]
    dateId = db.session.query(Date.dateId).filter_by(date = datetime.date(year,month,date),uid=uid).first()
    if dateId == None:
        allBill = []
    else:      
        allBill = db.session.query(Category).filter_by(dateId = dateId[0]).all()
    testData = {}
    testData['Bill']  = []
    allSpend = 0
    for i in allBill:
        bill = {}
        bill['id'] = i.CategoryId
        bill['type'] = i.name
        bill['money'] = i.money
        allSpend += i.money
        bill['date'] = date2Str(db.session.query(Date).filter_by(dateId=i.dateId).first().date)
        testData['Bill'] .append(bill)
    testData['allSpend'] = allSpend
    money = db.session.query(Plan.Money).filter_by(uid=uid).order_by(Plan.planId.desc()).first()[0]
    days = countDays(uid)
    if days != 0:
        testData['surplus'] = round((balanceCalcu(datetime.date(year,month,date),uid) - allSpend),2)
    else:
        testData['surplus'] = 0
    # print(testData)
    return json.dumps(testData,ensure_ascii=False)
"""
sure id is OK
"""
@app.route("/delBill")
def delBill():
    data = {}
    openid = request.args.get('cookie')
    id = request.args.get('id')
    id = int(id)
    uid = db.session.query(User.uid).filter_by(openid = openid).first()[0]
    if uid == None:
        data['status'] = 'Fail'
    try:
        sql = '''delete from Category where CategoryId = {CategoryId}'''.format(CategoryId = id)
        db.engine.execute(sql)
        # Item = Category(CategoryId = id)
        # db.session.delete(Item)
        # db.session.commit()
        data['status'] = 'Succes'
    except Exception as e:
        data['status'] = 'Fail'
        print e
    return json.dumps(data,ensure_ascii=False)


@app.route("/addPlan")
def addPlan():
    data={}
    money =  request.args.get('money')
    startDate = request.args.get('startDate')
    endDate = request.args.get('endDate')
    openid = request.args.get('cookie')
    if str2Date(startDate) >= str2Date(endDate):
        data['status'] = 'Fail'
        return json.dumps(data,ensure_ascii=False)
    uid = db.session.query(User.uid).filter_by(openid = openid).first()[0]
    myplan = Plan(str2Date(startDate),str2Date(endDate),money,uid)
    try:
        db.session.add(myplan)
        db.session.commit()
        data['status'] = 'success'
    except Exception as e:
        data['status'] = 'Fail'
        print(e)
    return json.dumps(data,ensure_ascii=False)
"""
sure id is OK
"""
def addBillLocal(money,typeName,date,openid):
    data = {}
    try:
        uid = db.session.query(User.uid).filter_by(openid = openid).first()[0]
        print 1
        dateId = db.session.query(Date.dateId).filter_by(date=str2Date(date),uid=uid).first()
        if dateId == None:
            myDate = Date(str2Date(date),uid)
            db.session.add(myDate)
            db.session.commit()
            dateId = db.session.query(Date.dateId).filter_by(date=str2Date(date),uid=uid).first()
        # print(dateId[0])
        bill = Category(unicode(typeName),dateId[0],money)
        db.session.add(bill)
        db.session.commit()
        data['status'] = 'success'
    except Exception as e:
        data['status'] = 'fail'
        raise e
    return json.dumps(data,ensure_ascii=False)


@app.route("/addBill")
def addBill():
    money =  request.args.get('money')
    typeName = request.args.get('typeName').strip()
    date = request.args.get('date')
    openid = request.args.get('cookie')
    return addBillLocal(money,typeName,date,openid)


@app.route("/showPlan")
def showPlan():
    data = {}
    openid = request.args.get('cookie')
    uid = db.session.query(User.uid).filter_by(openid = openid).first()[0]
    money = db.session.query(Plan.Money).filter_by(uid=uid).order_by(Plan.planId.desc()).first()
    if money == None:
        data['have'] = 0
        return json.dumps(data,ensure_ascii=False)
    else:
        data['have'] = 1
        money = money[0]
    startDate = db.session.query(Plan.startTime).filter_by(uid=uid).order_by(Plan.planId.desc()).first()[0]
    dateList = []
    leftMoney = []
    planMoneys = []
    print startDate
    endDate = db.session.query(Plan.endTime).filter_by(uid=uid).order_by(Plan.planId.desc()).first()[0]
    print endDate
    newstartDate = startDate
    i = 0
    while newstartDate <= endDate:
        date_str = newstartDate.strftime("%m-%d")
        dateList.append(date_str)
        allMoney = db.session.query(func.sum(Category.money)).join(Date).filter(Date.date.between(startDate,newstartDate)).filter_by(uid = uid).first()[0]
        allMoney = 0 if allMoney == None else allMoney
        if newstartDate <= datetime.date.today():
            leftMoney.append(money-allMoney)
        days = (endDate - startDate).days
        planMoney = money/days * i
        i += 1
        planMoneys.append(round((money - planMoney),2))
        newstartDate += datetime.timedelta(days=1)

    data['labels'] = dateList
    data['realMoneys'] =  leftMoney
    data['expectMoneys'] =  planMoneys
    print(data)
    return json.dumps(data,ensure_ascii=False)
"""
sure id is OK
"""
@app.route("/result")
def result():
    data={}
    startDate =  request.args.get('startDate')
    endDate =  request.args.get('endDate')
    openid = request.args.get('cookie')
    uid = db.session.query(User.uid).filter_by(openid = openid).first()[0]
    # eat = db.session.query(func.sum(Category.money)).filter_by(name=unicode('饮食 ')).first()[0]
    eat = db.session.query(func.sum(Category.money)).filter_by(name=unicode('饮食')).join(Date).filter(Date.date.between(str2Date(startDate),str2Date(endDate))).filter_by(uid = uid).first()[0]
    wear = db.session.query(func.sum(Category.money)).filter_by(name=unicode('服饰装容')).join(Date).filter(Date.date.between(str2Date(startDate),str2Date(endDate))).filter_by(uid = uid).first()[0]
    live = db.session.query(func.sum(Category.money)).filter_by(name=unicode('生活日用')).join(Date).filter(Date.date.between(str2Date(startDate),str2Date(endDate))).filter_by(uid = uid).first()[0]
    house = db.session.query(func.sum(Category.money)).filter_by(name=unicode('住房缴费')).join(Date).filter(Date.date.between(str2Date(startDate),str2Date(endDate))).filter_by(uid = uid).first()[0]
    go = db.session.query(func.sum(Category.money)).filter_by(name=unicode('交通出行')).join(Date).filter(Date.date.between(str2Date(startDate),str2Date(endDate))).filter_by(uid = uid).first()[0]
    chat = db.session.query(func.sum(Category.money)).filter_by(name=unicode('通讯')).join(Date).filter(Date.date.between(str2Date(startDate),str2Date(endDate))).filter_by(uid = uid).first()[0]
    wen = db.session.query(func.sum(Category.money)).filter_by(name=unicode('文教娱乐')).join(Date).filter(Date.date.between(str2Date(startDate),str2Date(endDate))).filter_by(uid = uid).first()[0]
    health = db.session.query(func.sum(Category.money)).filter_by(name=unicode('健康')).join(Date).filter(Date.date.between(str2Date(startDate),str2Date(endDate))).filter_by(uid = uid).first()[0]
    other = db.session.query(func.sum(Category.money)).filter_by(name=unicode('其他消费')).join(Date).filter(Date.date.between(str2Date(startDate),str2Date(endDate))).filter_by(uid = uid).first()[0]
    data['status'] = 'success'
    print(eat)
    # print(dateId)
    # '饮食', '服饰妆容', '生活日用', '住房缴费', '交通出行', '通讯']
    # db.session.query(func.sum(Category.money)).filter_by(name=unicode('饮食')).first()[0]
    data['result'] =  [eat, wear, live, house, go, chat,wen,health,other]
    for i,content in enumerate(data['result']):
        if content == None:
            data['result'][i] = 0
    print(data['result'])
    return json.dumps(data,ensure_ascii=False)

# @app.route("/login")
# def login():
#     data = {}
#     data['status'] = 'success'
#     data['result'] =  [90, 110, 145, 95, 87, 160]
#     return json.dumps(data,ensure_ascii=False)

# @app.route("/.well-known/pki-validation/fileauth.txt")
# def verity():
#     return "20180424101213022w97rnxl5swy0p57qo6uy2rfmr52o3bb05g2c8zaku4pffsj"
# def getAccessToken():
#     appID = "wxda414635ff6fd070"
#     appse  = "7125e4cdd86f80dec33054bb6c7383ea"
#     url = '''https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={appse}'''
#     url = url.format(appid = appID,appse = appse)
#     r = requests.get(url)
#     return r.text

# def getUnionId(ACCESS_TOKEN,OPENID):
#     url = '''https://api.weixin.qq.com/cgi-bin/user/info?access_token={ACCESS_TOKEN}&openid={OPENID}&lang=zh_CN'''
#     url = url.format(ACCESS_TOKEN = ACCESS_TOKEN,OPENID = OPENID)
#     r = requests.get(url)
#     return r.text

def addConver(content,pnId):
    mpId = db.session.query(Conver.mpId).filter_by(pnId = pnId).first()
    if mpId != None:
        return mpId
    mpId = content.lstrip("激活");
    converClass = Conver(mpId,pnId)
    db.session.add(converClass)
    db.session.commit()
    mpId = db.session.query(Conver.mpId).filter_by(pnId = pnId).first()[0]
    return mpId

def idConvert(pnId):
    mpId = db.session.query(Conver.mpId).filter_by(pnId = pnId).first()
    print mpId
    return mpId

def addBillByPn(content,pnId):
    content = content.lstrip("添加账单")
    typeName = content.split(" ")[0]
    money = content.split(" ")[1]
    print typeName
    print money
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    print date
    mpId = idConvert(pnId)
    if mpId == None:
        return u"请输入激活码"
    print mpId[0]
    result = eval(addBillLocal(money,typeName,date,mpId[0]))
    print result
    return result['status']
    # return "123"



@app.route("/wx",methods=['POST'])
# @app.route("/wx")
def wx():
    webData = request.data
    print "Handle Post webdata is ", webData
    recMsg = receive.parse_xml(webData)
    # print recMsg.MsgId
    # print (isinstance(recMsg, receive.Msg) and recMsg.MsgType == 'text')
    if isinstance(recMsg, receive.Msg) and (recMsg.MsgType == 'text' or recMsg.MsgType == 'voice'):
        toUser = recMsg.FromUserName
        ToUserName = recMsg.ToUserName
        content = recMsg.Content.strip().rstrip('.')
        pnId = toUser
        replyContent = u"处理异常，请稍后重试"
        if content.startswith("激活"):
            addConver(content,pnId)
            replyContent = u"添加成功,请尽情使用"
        elif content.startswith("添加账单"):
            replyContent = addBillByPn(content,pnId)
        else:
            replyContent = '''
        输入格式错误，如果激活,请输入"激活+激活码"
        如果要添加账单，请输入"添加账单+类型+金钱"
        类型有底下几类
        ["饮食", "服饰妆容", "生活日用", "住房缴费", "交通出行", "通讯", "文教娱乐", "健康", "其他消费"]
            '''
        replyMsg = reply.TextMsg(toUser, ToUserName, replyContent)
        # print replyMsg.send()
        return replyMsg.send()
    elif isinstance(recMsg, receive.Msg) and (recMsg.MsgType == 'event'):
        toUser = recMsg.FromUserName
        ToUserName = recMsg.ToUserName
        replyContent = '''
        欢迎关注，这里是吃土神器公众号。这个公众号配合小程序使用
        如果想激活,请输入"激活+激活码"
        如果要添加账单，请输入"添加账单+类型+金钱"
        类型有底下几类
        ["饮食", "服饰妆容", "生活日用", "住房缴费", "交通出行", "通讯", "文教娱乐", "健康", "其他消费"]
            '''
        replyMsg = reply.TextMsg(toUser, ToUserName, replyContent)
        # print replyMsg.send()
        return replyMsg.send()
    else:
        print "暂且不处理"
        return "success"
    # print request.form
    # signature = request.args.get('signature')
    # timestamp = request.args.get('timestamp')
    # nonce = request.args.get('nonce')
    # echostr = request.args.get('echostr')
    # token = "daiker"
    # list = [token, timestamp, nonce]
    # list.sort()
    # sha1 = hashlib.sha1()
    # map(sha1.update, list)
    # hashcode = sha1.hexdigest()
    # print "handle/GET func: hashcode, signature: ", hashcode, signature
    # if hashcode == signature:
    #     return echostr
    # else:
    #     return ""    