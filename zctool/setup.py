#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# setup.py
"""
python 转换为  exe文件
"""
from distutils.core import setup
import py2exe
import sys


sys.argv.append("py2exe")
setup(console=["zctool.py"])
