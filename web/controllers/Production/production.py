from flask import Blueprint,request,redirect,jsonify,make_response ,render_template
from common.libs.Help import ops_render,iPagination,getCurrentDate
from application import app ,db
from common.libs.UrlManager import UrlManager
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.pay.PayOrder import PayOrder
from common.models.food.food import Food
from common.models.option.option import Option
from common.libs.huawei.huawei_help import hwawei_help


route_production = Blueprint( 'production_page',__name__ ) #url:/production/show
global old_id
old_id = 0

@route_production.route("/show",methods = ["GET",'POST'])
def show():
    global old_id
    list_1 = []
    pay_order_info = PayOrder.query.filter_by(status = -6).first()
    if pay_order_info:
        id  = pay_order_info.id




        PayOrderItem_info = PayOrderItem.query.filter_by(pay_order_id =id ).all()
        if pay_order_info.qrcode_id =="":
            type="堂食"
        else:
            type ="外带"
            qrcode_id = pay_order_info.qrcode_id
            hall_id = pay_order_info.hall_id
            option_info = Option.query.filter(Option.option_type == 5).filter(Option.hall_id == hall_id) \
                .first()
            deviceId = option_info.deviceId
            serviceId = "PrintQR"
            method = "Print"
            body = {
                "QRcore": qrcode_id,
            }
            token = hwawei_help.getAccessToken()
            # hwawei_help.sendCommand(token = token,deviceId=deviceId,serviceId=serviceId,method=method,body=body)
            # 用下面这个
            hwawei_help.CMD(token=token, deviceId=deviceId, serviceId=serviceId, method=method, paras=body)
            old_id = id
        note = pay_order_info.note

        for item in PayOrderItem_info:
            food_info = Food.query.filter_by(id =item.food_id).first()

            tmp_data = {
                        'name': food_info.name,
                        }

            list_1.append (tmp_data)
        tmp_data  = {
            "type":type,
            "note":note,
        }

        list_1.append(tmp_data)


    return render_template( "production/show.html" ,list_1 =list_1 )

'''
@route_production.route("/set",methods = ["POST",])

def set():
    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    req = request.values
    qrcode_id  = req.get("qrcode_id", '')
    camera_id = int(req.get("camera_id", 0))
    if camera_id < 1:
            resp = {'code': -1, 'msg': '摄像头数据错误~~', 'data': {}}
            return  (resp)
    # if qrcode_id <1:
    #     #         resp = {'code': -1, 'msg': '二维码数据错误~~', 'data': {}}
    #     #         return (resp)
    if camera_id == 1:
        pay_order_info = PayOrder.query.filter_by(qrcode_id=qrcode_id).first()
        pay_order_info.status = -5
        pay_order_info.express_status = -5
        pay_order_info.updated_time = getCurrentDate()
        db.session.add(pay_order_info)
        db.session.commit()
        return (resp)


    if camera_id ==2:

        pay_order_info = PayOrder.query.filter_by(qrcode_id=qrcode_id).first()
        pay_order_info.status = -3
        pay_order_info.express_status = -3
        pay_order_info.updated_time = getCurrentDate()
        db.session.add(pay_order_info)
        db.session.commit()
        return(resp)

'''
@route_production.route("/reload",methods = ["GET",'POST'])
def reload():
    list_1 = []
    global old_id
    pay_order_info = PayOrder.query.filter_by(status = -6).first()
    if pay_order_info:
        id  = pay_order_info.id
        if  old_id != id and  pay_order_info.qrcode_id !="":

            hall_id = pay_order_info.hall_id
            option_info = Option.query.filter(Option.option_type == 5).filter(Option.hall_id == hall_id) \
                .first()
            deviceId = option_info.deviceId
            serviceId = "PrintQR"
            method = "Print"
            body = {
                "QRcore": pay_order_info.qrcode_id,
            }
            token = hwawei_help.getAccessToken()
            # hwawei_help.sendCommand(token = token,deviceId=deviceId,serviceId=serviceId,method=method,body=body)
            # 用下面这个
            hwawei_help.CMD(token=token, deviceId=deviceId, serviceId=serviceId, method=method, paras=body)
            old_id = id


        PayOrderItem_info = PayOrderItem.query.filter_by(pay_order_id =id ).all()
        if pay_order_info.qrcode_id =="":
            type="堂食"
        else:
            type ="外带"
        note = pay_order_info.note

        for item in PayOrderItem_info:
            food_info = Food.query.filter_by(id =item.food_id).first()

            tmp_data = {
                        'name': food_info.name,
                        }

            list_1.append (tmp_data)
        tmp_data  = {
            "type":type,
            "note":note,
        }
        list_1.append(tmp_data)
    return jsonify(list_1)
