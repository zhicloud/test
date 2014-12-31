#!/usr/bin/python
# -*- coding: utf-8 -*-
import collections

StatusClass = collections.namedtuple("StatusClass", ('stopped', 'running', 'stopping'))
StatusEnum = StatusClass(0, 1, 2)
