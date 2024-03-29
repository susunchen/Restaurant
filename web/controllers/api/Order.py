# -*- coding: utf-8 -*-
from web.controllers.api import route_api
from flask import request, jsonify,g
from application import app, db
import json, decimal
from common.models.food.food import Food
from common.models.pay.PayOrder import PayOrder
from common.libs.UrlManager import UrlManager
from common.libs.Help import selectFilterObj,getDictFilterField,getCurrentDate
from common.libs.pay.PayService import PayService
from common.libs.pay.WeChatService import WeChatService
from common.models.cabint.cabint_status import CabintStatu
from common.models.cabint.cabint_data import CabintData
from common.libs.member.CartService import CartService
from common.models.member.MemberAddress import MemberAddress
from common.models.member.Oauth_Member_Bind import OauthMemberBind
from common.libs.huawei.huawei_help import hwawei_help
from common.models.pay.PayOrderItem import PayOrderItem
import requests
from common.models.option.option import Option
from common.libs.res import Nutrition_Recommendation


@route_api.route("/order/info", methods=[ "POST" ])
def orderInfo():
	resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
	req = request.values
	params_goods = req['goods'] if 'goods' in req else None
	member_info = g.member_info
	params_goods_list = []
	if params_goods:
		params_goods_list = json.loads(params_goods)
	good_list = []
	for key,value in params_goods_list.items():
		tmp_good_list = [int(key),value]
		good_list.append(tmp_good_list)
	Nutrition = Nutrition_Recommendation(good_list)
	Nutrition_food_info = []
	if Nutrition["res_food_id"]:

		for item in Nutrition["res_food_id"]:
			tmp_food_info = Food.query.filter_by(id=item).first()
			Nutrition_food_info.append(tmp_food_info)

	food_dic = {}
	for id,number in params_goods_list.items():
		food_dic[id] = number

	food_ids = food_dic.keys()
	food_list = Food.query.filter(Food.id.in_(food_ids)).all()
	data_food_list = []
	yun_price = pay_price = decimal.Decimal(0.00)
	note = ""
	Nutrition_food_list = []
	if Nutrition_food_info:
		for item in Nutrition_food_info:
			tmp_data = {
				"id": item.id,
				"name": item.name,
				"price": str(item.price),
				'pic_url': UrlManager.buildImageUrl(item.main_image),
				"note":"你的订单菜品中缺少{}元素，为了你的健康着想，建议你加购以下菜品".format(Nutrition["min_keys"])
			}
			note = tmp_data["note"]
			Nutrition_food_list.append(tmp_data)

	if food_list:
		for item in food_list:
			tmp_data = {
				"id": item.id,
				"name": item.name,
				"price": str(item.price),
				'pic_url': UrlManager.buildImageUrl(item.main_image),
				'number': food_dic[str(item.id)]
			}
			pay_price = pay_price + item.price * int( food_dic[str(item.id)] )
			data_food_list.append(tmp_data)

	# 获取地址
	address_info = MemberAddress.query.filter_by( is_default = 1,member_id = member_info.id,status = 1 ).first()
	default_address = ''
	if address_info:
		default_address = {
			"id": address_info.id,
			"name": address_info.nickname,
			"mobile": address_info.mobile,
			"address":"%s%s%s%s"%( address_info.province_str,address_info.city_str,address_info.area_str,address_info.address )
		}



	resp['data']['food_list'] = data_food_list
	resp['data']['Nutrition_food_list'] = Nutrition_food_list
	resp['data']['note'] = note
	resp['data']['pay_price'] = str(pay_price)
	resp['data']['yun_price'] = str(yun_price)
	resp['data']['total_price'] = str(pay_price + yun_price)
	resp['data']['default_address'] = default_address
	return jsonify(resp)



@route_api.route("/order/create", methods=[ "POST"])

def orderCreate():




	resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
	req = request.values
	type = req['type'] if 'type' in req else ''
	note = req['note'] if 'note' in req else ''
	send_typeid = req['send_typeid'] if 'send_typeid in req' else 1
	express_address_id = int( req['express_address_id'] ) if 'express_address_id' in req and req['express_address_id'] else 0
	params_goods = req['goods'] if 'goods' in req else None

	items = []
	if params_goods:
		items = json.loads(params_goods)

	if len( items ) < 1:
		resp['code'] = -1
		resp['msg'] = "下单失败：没有选择商品~~"
		return jsonify(resp)

	address_info = MemberAddress.query.filter_by( id = express_address_id ).first()
	if not address_info or not address_info.status:
		resp['code'] = -1
		resp['msg'] = "下单失败：快递地址不对~~"
		return jsonify(resp)

	member_info = g.member_info
	target = PayService()
	params = {
		'type':type,
		'send_typeid':send_typeid,
		"note":note,
		'express_address_id':address_info.id,
		'express_info':{
			'mobile':address_info.mobile,
			'nickname':address_info.nickname,
			"address":"%s%s%s%s"%( address_info.province_str,address_info.city_str,address_info.area_str,address_info.address )
		}
	}

	goods = []
	for id,number in items.items():
		food_info = Food.query.filter_by( id = id).first()

		goods_item ={
			"id":id,
			"price":food_info.price,
			"number":number

		}
		goods.append(goods_item)

	resp = target.createOrder( member_info.id ,goods ,params)
	#如果是来源购物车的，下单成功将下单的商品去掉
	#if resp['code'] == 200 and type == "cart":
		#CartService.deleteItem( member_info.id,goods )

	return jsonify( resp )

@route_api.route("/order/pay", methods=[ "POST"])
def orderPay():
	resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
	member_info = g.member_info
	req = request.values
	order_sn = req['order_sn'] if 'order_sn' in req else ''
	pay_order_info = PayOrder.query.filter_by( order_sn = order_sn,member_id = member_info.id ).first()
	if not pay_order_info:
		resp['code'] = -1
		resp['msg'] = "系统繁忙。请稍后再试~~"
		return jsonify(resp)

	#oauth_bind_info = OauthMemberBind.query.filter_by( member_id =  member_info.id ).first()
	#if not oauth_bind_info:
	#	resp['code'] = -1
	#	resp['msg'] = "系统繁忙。请稍后再试~~"
	#	return jsonify(resp)

	#config_mina = app.config['MINA_APP']
	#notify_url = app.config['APP']['domain'] + config_mina['callback_url']

	#target_wechat = WeChatService( merchant_key=config_mina['paykey'] )

	#data = {
		#'appid': config_mina['appid'],
		#'mch_id': config_mina['mch_id'],
		#'nonce_str': target_wechat.get_nonce_str(),
		#'body': '订餐',  # 商品描述
		#'out_trade_no': pay_order_info.order_sn,  # 商户订单号
		#'total_fee': int( pay_order_info.total_price * 100 ),
		#'notify_url': notify_url,
		#'trade_type': "JSAPI",
		#'openid': oauth_bind_info.openid
	#}

	#pay_info = target_wechat.get_pay_info( pay_data=data)

	#保存prepay_id为了后面发模板消息
	#pay_order_info.prepay_id = pay_info['prepay_id']
	 #db.session.add( pay_order_info )
	 #db.session.commit()

	#resp['data']['pay_info'] = pay_info
	pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
	if pay_order_info.qrcode_id:
		pay_order_info.status = -7
		pay_order_info.express_status = -7
	else:
		pay_order_info.status = -6
		pay_order_info.express_status = -6
	pay_order_info.updated_time = getCurrentDate()
	db.session.add(pay_order_info)
	pay_order_food = PayOrderItem.query.filter_by(pay_order_id=pay_order_info.id).all()
	for item in pay_order_food:
		food_info = Food.query.filter_by(id = item.food_id).first()
		food_info.total_count = food_info.total_count+1
		db.session.add(food_info)
		db.session.commit()
	db.session.commit()


	return jsonify(resp)

@route_api.route("/order/callback", methods=[ "POST"])
def orderCallback():
	result_data = {
		'return_code': 'SUCCESS',
		'return_msg': 'OK'
	}
	header = {'Content-Type': 'application/xml'}
	config_mina = app.config['MINA_APP']
	target_wechat = WeChatService(merchant_key=config_mina['paykey'])
	callback_data = target_wechat.xml_to_dict( request.data )
	app.logger.info( callback_data  )
	sign = callback_data['sign']
	callback_data.pop( 'sign' )
	gene_sign = target_wechat.create_sign( callback_data )
	app.logger.info(gene_sign)
	if sign != gene_sign:
		result_data['return_code'] = result_data['return_msg'] = 'FAIL'
		return target_wechat.dict_to_xml(result_data), header
	if callback_data['result_code'] != 'SUCCESS':
		result_data['return_code'] = result_data['return_msg'] = 'FAIL'
		return target_wechat.dict_to_xml(result_data), header

	order_sn = callback_data['out_trade_no']
	pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
	if not pay_order_info:
		result_data['return_code'] = result_data['return_msg'] = 'FAIL'
		return target_wechat.dict_to_xml(result_data), header

	if int( pay_order_info.total_price * 100  ) != int( callback_data['total_fee'] ):
		result_data['return_code'] = result_data['return_msg'] = 'FAIL'
		return target_wechat.dict_to_xml(result_data), header

	if pay_order_info.status == 1:
		return target_wechat.dict_to_xml(result_data), header

	target_pay = PayService()
	target_pay.orderSuccess( pay_order_id = pay_order_info.id,params = { "pay_sn":callback_data['transaction_id'] } )
	target_pay.addPayCallbackData( pay_order_id = pay_order_info.id, data = request.data)
	return target_wechat.dict_to_xml(result_data), header

@route_api.route("/order/ops", methods=[ "POST"])
def orderOps():
	resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
	req = request.values
	member_info = g.member_info
	order_sn = req['order_sn'] if 'order_sn' in req else ''
	act = req['act'] if 'act' in req else ''
	pay_order_info = PayOrder.query.filter_by(order_sn=order_sn, member_id=member_info.id).first()
	if not pay_order_info:
		resp['code'] = -1
		resp['msg'] = "系统繁忙。请稍后再试~~"
		return jsonify(resp)


	if act == "cancel":
		target_pay = PayService( )
		ret = target_pay.closeOrder( pay_order_id=pay_order_info.id )
		if not ret:
			resp['code'] = -1
			resp['msg'] = "系统繁忙。请稍后再试~~"
			return jsonify(resp)
	elif act == "confirm":
		pay_order_info.express_status = 1
		pay_order_info.updated_time = getCurrentDate()
		db.session.add( pay_order_info )
		db.session.commit()

	return jsonify(resp)

@route_api.route("/order/open", methods=[ "POST"])
def orderOpen():
	resp = {'code': 200, 'msg': '开柜成功~', 'data': {}}
	req = request.values
	order_sn = req['order_sn']if 'order_sn' in req and req['order_sn'] else ''
	pay_order_info = PayOrder.query.filter_by( order_sn = order_sn ).first()
	cabint_id = pay_order_info.cabint_id
	hall_id=pay_order_info.hall_id
	if cabint_id == 0:
		resp['code'] = -1
		resp['msg'] = "请选择要操作的账号~~"
		return jsonify(resp)

	#deviceId = "46dc3288-5162-4238-b3cb-58705e4eb6e0"
	option_info = Option.query.filter (Option.option_type == 4).filter (Option.hall_id == hall_id)\
                .first()
	deviceId =option_info.deviceId
	serviceId = "OpenDool"
	method = "OPEN"
	body = {
		"cabint_id": cabint_id,
	}
	token = hwawei_help.getAccessToken()
	hwawei_help.CMD(token=token, deviceId=deviceId, serviceId=serviceId, method=method, paras=body)





	'''
	要更改三个表的数据
	'''
	pay_order_info = PayOrder.query.filter_by(cabint_id=cabint_id,status = -4).first()
	pay_order_info.status = '-3'
	pay_order_info.update_time = getCurrentDate()
	db.session.add(pay_order_info)

	cabint_data_info = CabintData()
	cabint_data_info.cabint_id = cabint_id
	cabint_data_info.order_sn = pay_order_info.order_sn
	cabint_data_info.action = 0
	cabint_data_info.created_time = getCurrentDate()
	db.session.add(cabint_data_info)


	cabint_info = CabintStatu.query.filter_by(id=cabint_id).first()
	cabint_info.cabint_status = 1
	cabint_info.updated_time = getCurrentDate()
	db.session.add(cabint_info)
	db.session.commit()






	return jsonify(resp)

@route_api.route("/order/arrive",methods=["POST"])
def orderArrive():
	resp = {'code':200,"msg":"已确认送达！","data":{}}
	req = request.values
	order_sn = req['order_sn']if 'order_sn' in req and req['order_sn'] else ''
	pay_order_info = PayOrder.query.filter_by( order_sn = order_sn ).first()

	#pay_order_info = PayOrder.query.filter_by(status = -3).first()
	pay_order_info.status = '-2'
	pay_order_info.update_time = getCurrentDate()
	db.session.add(pay_order_info)
	db.session.commit()

	return jsonify(resp)

@route_api.route("/order/got",methods=["POST"])
def orderGot():
	resp = {'code':200,"msg":"已确认收货！","data":{}}
	req = request.values
	order_sn = req['order_sn']if 'order_sn' in req and req['order_sn'] else ''
	pay_order_info = PayOrder.query.filter_by( order_sn = order_sn ).first()
	#pay_order_info = PayOrder.query.filter_by(status = -2).first()
	pay_order_info.status = '1'
	pay_order_info.update_time = getCurrentDate()
	db.session.add(pay_order_info)
	db.session.commit()

	return jsonify(resp)