# !/usr/bin/env python
# coding: utf-8
""" QQ钱包
"""

import json
import logging
import hashlib
import hmac

from tornado import gen

from lib.http import http_get, http_post
from lib.utils import make_sign, xml_to_dict


QQ_APP_ID = APP_ID = ""
APP_SECRET = ""
QQ_ORDER_URL = ""
QQ_MCH_ID = ""
QQ_PAY_CALLBACK = ""


@gen.coroutine
def qq_get_profile(openid, access_token):
    """ 根据access_token获取用户微信信息
    """
    url = ("https://graph.qq.com/user/get_user_info?"
           "access_token=%s&oauth_consumer_key=%s&openid=%s" %
           (access_token, APP_ID, openid)
           )

    rc, raw_body = yield http_get(url)
    data = json.loads(raw_body)
    user_info = {}
    logging.debug(data)
    if not data['ret']:
        user_info['qq_openid'] = openid
        user_info['avatar_url'] = data['figureurl_qq_2']
    else:
        print "QQ Error:", data['msg']

    raise gen.Return(user_info)


@gen.coroutine
def qq_get_token(auth_code):
    """ 根据返回给前端的auth_code, 获取access_token
    """
    url = "https://graph.qq.com/oauth2.0/me?access_token=%s" % auth_code

    rc, raw_body = yield http_get(url)
    body = json.loads(raw_body[10: -3])
    if body.get('error'):
        logging.error("qq get token error:%s",  body["error_description"])
        raise gen.Return({})
    else:
        raise gen.Return(body)


def qq_make_sign(params):
    """ 签名
    """
    app_key = "&key=%s" % APP_SECRET

    return make_sign(params, app_key, uppercase=True)


@gen.coroutine
def qq_make_order(params):
    """ 请求订单
    """
    params['sign'] = qq_make_sign(params)
    xml_params = dict_to_xml(params)

    _, raw_body = yield http_post(QQ_ORDER_URL, body=xml_params)

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
        xml.append("<{0}>{1}</{0}>".format(k, v))
        """
        if str(v).isdigit():
            xml.append("<{0}>{1}</{0}>".format(k, v))
        else:
            xml.append("<{0}><![CDATA[{1}]]></{0}>".format(k, v))
        """
    xml.append("</xml>")

    return "".join(xml)


def make_front_sig(data, key):
    """ 返回客户端订单信息签名
    """
    data_strs = ["%s=%s" % (k, data[k]) for k in sorted(data)]
    sign_str = "&".join(data_strs)
    hashed = hmac.new(key, sign_str, hashlib.sha1)

    return hashed.digest().encode("base64").rstrip('\n')
