#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 13:23:21 2020

@author: Roger Selzler
"""

import thingspeak
from pprint import pprint as p
t=thingspeak.ThingSpeak(user_api_key='USER API KEY')

t = thingspeak.ThingSpeak()
ch=t.get_channel(9)
ch.get_field_data(ch.read_feed(10))

p(ch.__dict__)