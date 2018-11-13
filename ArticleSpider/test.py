#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Dylan"
# Date: 2018/11/7 19:46

import redis
redis_cli = redis.StrictRedis(host="localhost", password="dylan", decode_responses=True)
redis_cli.incr("jobbole_count")
