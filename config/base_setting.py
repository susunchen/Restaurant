# -*- coding: utf-8 -*-
SERVER_PORT = 8889
DEBUG = False
SQLALCHEMY_ECHO = False
AUTH_COOKIE_NAME = "mooc_food"

'''
过滤URL
'''
IGNORE_URLS = {
    "^/user/login",
    "^/api", "^/qrcode","^/production","^/cabint"
}


API_IGNORE_URLS = [
    "^/api"
]
IGNORE_CHECK_LOGIN_URLS = [
    "^/static",
    "^/favicon.ico"
]


PAGE_SIZE = 50
PAGE_DISPLAY = 10



STATUS_MAPPING = {
    "1":"正常",
    "0":"已删除"
}

CABINT_STATUS_MAPPING = {
    "1":"空置",
    "0":"使用中"
}

OPTION_TYPE_MAPPING = {
    "1":"生产摄像头",
    "2":"过程扫码器",
    "3":"机械臂",
    "4":"智能取餐柜",
    "5":"二维码打印机",
    "6":"传送带"

}
MINA_APP = {
    'appid' :'wxc1bb68825a7a903a',
    'appkey' : 'eb32b5239177b2e9e88561c8b13db7cb'


}

UPLOAD = {
    'ext':[ 'jpg','gif','bmp','jpeg','png' ],
    'prefix_path':'/web/static/upload/',
    'prefix_url':'/static/upload/'
}
APP = {
    #'domain':'https://www.szuforti.top'
    #"domain":"http://szu125.zicp.vip"
    "domain":"127.0.0.1:8889"
}
PAY_STATUS_MAPPING = {
    "1":"已支付",
    "-8":"待支付",
    "0":"已关闭"
}

PAY_STATUS_DISPLAY_MAPPING = {
    "0":"订单关闭",
    "1":"待评价",
    "3":"已完成",
    "2":"已完成",
    "-8":"待支付",
    "-7":"支付完成代配送确认",
    "-6":"配送确认代生产",
    "-5":"生产完成代入柜",
    "-4":"入柜成功代收取",
    "-3":"收取成功配送中",
    "-2":"已经送达,用户待确认",
    "4":"评价完成",

}
# 华为云账号：
HUAWEI_IOT = {
    "appId":"Y_W4ttL4BLbD5oJy6GALURgg3kka",
    "secret":"KihKip0c4Yvj8OG6ekvkhfe3OJsa"
}
# 华为云的设备：
SCAN = {
    "deviceId":"55c1ff2c-0b01-49ef-9974-47db03a1f514"
}
MOTER= {

    "deviceId":"985d6a4d-b4f9-4a23-b7aa-d80ef700ea7c"
}
CABINT= {
    "deviceId":"d5d81dae-beae-4dad-8627-8e0a6799a4c8"
}