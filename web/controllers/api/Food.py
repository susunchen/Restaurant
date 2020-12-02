# -*- coding: utf-8 -*-
from web.controllers.api import route_api
from  flask import request,jsonify,g
from common.models.food.food_cat import FoodCat
from common.models.food.food import Food
from common.models.member.Member_Cart import MemberCart
from common.models.member.MemberComment import MemberComment
from common.models.member.Member import Member

from common.models.food.hall import Hall
from common.libs.UrlManager import UrlManager
from common.libs.Help import getCurrentDate,getDictFilterField,selectFilterObj
from common.libs.res import Recommend
from application import app,db
from sqlalchemy import  or_

@route_api.route("/food/index" )
def foodIndex():
    resp = { 'code':200 ,'msg':'操作成功~','data':{} }
    req = request.args
    id = int(req.get("id", 0))

    cat_list = FoodCat.query.filter_by(status=1,hall_id=id ).order_by( FoodCat.weight.desc() ).all()
    food_list = Food.query.filter_by(status=1, hall_id=id).order_by( Food.cat_id.desc() ).all()
    hall_info = Hall.query.filter_by(id = id).first()
    data_cat_list = []
    data_hall_list = []
    data_food_list = []
    Recommend_food_list = []
    #取餐厅数据：
    tmp_data = {
        'id': id,
        'name': hall_info.name,
        "main_photo":UrlManager.buildImageUrl(hall_info.main_image)
    }
    data_hall_list.append(tmp_data)
    food_id = Recommend(g.member_info.id, id)



    #取食物数据：
    if food_list:
        for item in food_list:
            tmp_data = {
                'id': item.id,
                'name': "%s"%( item.name ),
                'price': str( item.price ),
                'cat_id': item.cat_id,
                'min_price':str( item.price ),
                'pic_url': UrlManager.buildImageUrl(item.main_image)
            }
            if item.id in food_id:
                Recommend_food_list.append(tmp_data)

            data_food_list.append(tmp_data)
    Recommend_cat_list = {
        'id': "i" + str(1),
        'classifyName': "推荐菜品"
    }
    Recommend_cat_list["goods"] = Recommend_food_list
    data_cat_list.append(Recommend_cat_list)
    #取食物列表数据：
    if cat_list:
        for item in cat_list:
            tmp_data = {
                'id': "i"+str(item.id+1),
                'classifyName': item.name
            }
            tmp_data["goods"] = []
            for food_item in data_food_list:
                if food_item["cat_id"] == item.id:
                    tmp_data["goods"].append(food_item)
            data_cat_list.append(tmp_data)


    resp['data']['hall_info'] = data_hall_list
    resp['data']['cat_list'] = data_cat_list
    resp['data']['food_list'] = data_food_list
    return jsonify( resp )

@route_api.route("/food/search" )
def foodSearch():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    cat_id = int( req['cat_id'] ) if 'cat_id' in req else 0
    mix_kw = str(req['mix_kw']) if 'mix_kw' in req else ''
    p = int( req['p'] ) if 'p' in req else 1

    if p < 1:
        p = 1

    page_size = 10
    offset = ( p - 1 ) * page_size
    query = Food.query.filter_by(status=1 )
    if cat_id > 0:
        query = query.filter_by(cat_id = cat_id)

    if mix_kw:
        rule = or_(Food.name.ilike("%{0}%".format(mix_kw)), Food.tags.ilike("%{0}%".format(mix_kw)))
        query = query.filter(rule)

    food_list = query.order_by(Food.total_count.desc(), Food.id.desc())\
        .offset( offset ).limit( page_size ).all()

    data_food_list = []
    if food_list:
        for item in food_list:
            tmp_data = {
                'id': item.id,
                'name': "%s"%( item.name ),
                'price': str( item.price ),
                'min_price':str( item.price ),
                'pic_url': UrlManager.buildImageUrl(item.main_image)
            }
            data_food_list.append(tmp_data)
    resp['data']['list'] = data_food_list
    resp['data']['has_more'] = 0 if len( data_food_list ) < page_size else 1
    return jsonify(resp)

@route_api.route("/food/info" )
def foodInfo():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    id = int(req['id']) if 'id' in req else 0
    food_info = Food.query.filter_by( id = id ).first()
    if not food_info or not food_info.status :
        resp['code'] = -1
        resp['msg'] = "美食已下架"
        return jsonify(resp)

    member_info = g.member_info
    cart_number = 0
    if member_info:
        cart_number = MemberCart.query.filter_by( member_id =  member_info.id ).count()
    resp['data']['info'] = {
        "id":food_info.id,
        "name":food_info.name,
        "summary":food_info.summary,
        "total_count":food_info.total_count,
        "comment_count":food_info.comment_count,
        'main_image':UrlManager.buildImageUrl( food_info.main_image ),
        "price":str( food_info.price ),
        "stock":food_info.stock,
        "pics":[ UrlManager.buildImageUrl( food_info.main_image ) ]
    }

    resp['data']['cart_number'] = cart_number
    return jsonify(resp)


@route_api.route("/food/comments")
def foodComments():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    id = int(req['id']) if 'id' in req else 0
    query = MemberComment.query.filter( MemberComment.food_ids.ilike("%_{0}_%".format(id)) )
    list = query.order_by( MemberComment.id.desc() ).limit(5).all()
    data_list = []
    if list:
        member_map = getDictFilterField( Member,Member.id,"id",selectFilterObj( list,"member_id" ) )
        for item in list:
            if item.member_id not in member_map:
                continue
            tmp_member_info = member_map[ item.member_id ]
            tmp_data = {
                'score':item.score_desc,
                'date': item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                "content":item.content,
                "user":{
                    'nickname':tmp_member_info.nickname,
                    'avatar_url':tmp_member_info.avatar,
                }
            }
            data_list.append( tmp_data )
    resp['data']['list'] = data_list
    resp['data']['count'] = query.count()
    return jsonify(resp)


@route_api.route("/food/res")
def foodRes():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values

    url = SQLALCHEMY_DATABASE_URI.split("/")[2]
    url_list = url.split("@")
    host = url_list[1]    #数据库ip地址
    li = url_list[0]
    username = li.split(":")[0] #用户名
    password = li.split(":")[1] #密码

    member_id = int(req['member_id'])  # 用户的id
    hall_id = int(req['hall_id'])  # 餐厅的id

    food_data, member_food_id = read_sql(host, username, password, member_id)
    res = get_res_data(food_data, member_food_id, do, hall_id)  # 推荐结果

    if len(res) == 0:  # 新用户
        no_res_data = food_data.sort_values('num', ascending=False).iloc[0:3]
        no_res = copy.deepcopy(no_res_data[['food_id', 'food_name']])
        no_res['food_cos'] = 0
        res = copy.deepcopy(no_res) #推荐结果
    res_id = list(res['food_id'])   #推荐id
    #res_name = list(res['food_name']) #推荐名称
    #res_cos = list(res['food_cos']) #推荐相似度

    request['data']['res_id'] = res_id
    return jsonify(res_id)