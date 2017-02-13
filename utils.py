# encoding: utf8

""" lib.utils
"""

from hashlib import md5
import xml.etree.ElementTree as ET


def xml_to_dict(xml_params):
    """ 转格式
    """
    data = {}

    xml = ET.fromstring(xml_params)
    for ele in xml.getchildren():
        data[ele.tag] = ele.text

    return data


def make_sign(data, key_str='', uppercase=False):
    """ 生成验证
    """
    data_strs = ["%s=%s" % (k, data[k]) for k in sorted(data) if str(data[k])]
    sign_str = "&".join(data_strs)
    sign_str += key_str

    sign = md5(sign_str).hexdigest()
    if uppercase:
        return sign.upper()
    else:
        return sign
