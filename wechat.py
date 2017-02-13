import json
import logging

from tornado import gen

from lib.utils import make_sign, xml_to_dict
from lib.http import http_get, http_post


WECHAT_PARTNER_ID = ''
WECHAT_APP_ID = ''

WECHAT_APP_SECRET = ""  # 获取微信用户权限
WECHAT_APP_KEY = ""   # 商户key

WECHAT_PAY_CALLBACK = ""

WECHAT_ORDER_URL = "https://api.mch.weixin.qq.com/pay/unifiedorder"


@gen.coroutine
def wechat_get_profile(open_id, access_token):
    """ 根据access_token获取用户微信信息
    """
    url = ("https://api.weixin.qq.com/sns/userinfo?lang=zh_CN&"
           "access_token=%s&openid=%s" % (access_token, open_id))

    data = yield wechat_get(url)
    user_info = {}
    logging.debug("wechat profile: %s", data)
    if data:
        user_info['wechat_openid'] = open_id
        user_info['avatar_url'] = data['headimgurl']

    raise gen.Return(user_info)


def wechat_get_token(auth_code):
    """ 根据微信返回给前端的auth_code, 获取access_token
    """
    url = ("https://api.weixin.qq.com/sns/oauth2/access_token?"
           "appid=%s&secret=%s&code=%s&grant_type=authorization_code" %
           (WECHAT_APP_ID, WECHAT_APP_SECRET, auth_code))

    return wechat_get(url)


@gen.coroutine
def wechat_get(url):
    _, raw_body = yield http_get(url)

    body = json.loads(raw_body)
    rc = body.get('errcode')
    if rc:
        raise gen.Return({})
    else:
        raise gen.Return(body)


def wechat_make_sign(params):
    """ 微信签名
    """
    wechat_key = "&key=%s" % WECHAT_APP_KEY

    return make_sign(params, wechat_key, uppercase=True)


@gen.coroutine
def make_order(params):
    """ 微信发器订单
    """
    logging.info("wechat make order info:%s", params)
    params['sign'] = wechat_make_sign(params)
    xml_params = dict_to_xml(params)

    _, raw_body = yield http_post(WECHAT_ORDER_URL, body=xml_params)

    data = xml_to_dict(raw_body)
    if data['return_code'] == 'SUCCESS':
        raise gen.Return(data)
    else:
        raise gen.Return({})


def dict_to_xml(params):
    """ 转格式
    """
    xml = ["<xml>"]
    for k, v in params.iteritems():
        if str(v).isdigit():
            xml.append("<{0}>{1}</{0}>".format(k, v))
        else:
            xml.append("<{0}><![CDATA[{1}]]></{0}>".format(k, v))
    xml.append("</xml>")

    return "".join(xml)

