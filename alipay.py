# !/usr/bin/env python
# encoding: utf8

""" 支付宝相关
"""

import rsa
import base64
import logging


ALI_APP_ID = ''
KEY = """-----BEGIN RSA PRIVATE KEY-----
-----END RSA PRIVATE KEY-----"""


PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
-----END PUBLIC KEY-----"""


def to_str(value):
    """dict to str
    """
    raw = []
    if isinstance(value, dict):
        for k, v in value.items():
            raw.append('%s:"%s"' % (k, v))
        return "{" + ",".join(raw).encode("utf8") + "}"
    else:
        return str(value)


def make_sign(params, key_str=KEY):
    """ 签名
    """
    raw_str = "&".join(["%s=%s" % (k, to_str(v)) for k, v in sorted(params.items())])
    private_key = rsa.PrivateKey.load_pkcs1(key_str)
    logging.debug(raw_str)
    sign = base64.b64encode(rsa.sign(raw_str, private_key, 'SHA-1'))
    return sign


def verify_sign(params, key_str=PUBLIC_KEY):
    """ 验签
    """
    sign = params.pop('sign')
    params.pop('sign_type')

    sign = base64.b64decode(sign)
    raw_str = "&".join(["%s=%s" % (k, v) for k, v in sorted(params.items())])
    public_key = rsa.PublicKey.load_pkcs1_openssl_pem(key_str)

    try:
        if rsa.verify(raw_str, sign, public_key):
            return True
    except Exception:
        return False

