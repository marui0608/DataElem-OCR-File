# -*- encoding: utf-8 -*-
'''
@File    :   fileBase64.py
@Time    :   2022/06/14 17:37:15
@Author  :   Fighter.Ma
@Email   :   fighter_ma1024@163.com
@Software:   VsCode
@License :   (C)Copyright 2021-2022, Fighter-Ma-China
'''

# here put the import lib

import base64


def b64_file(file):
    b64 = base64.b64encode(file).decode()
    return b64