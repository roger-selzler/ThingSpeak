# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 12:35:20 2020

@author: rogerselzler
"""

import urllib
import requests

def check_response(response):
    response_ = Response(response)
    return response_

class Response():
    def __init__(self,response):
        self._response = response
        # if type(response.status_code) != int: raise ValueError('Status code must be an integer')
        self.status_code = response.status_code
        self.__process_response()
        
    def __process_response(self):
        
        for key in [ 'message','details','error_code']:
            if self.status_code in mr.keys():
                setattr(self,key,mr[self.status_code][key])
            else:
                setattr(self,key,'')
        
        if self.status_code != 200:
            raise urllib.error.HTTPError(self._response.url,self.status_code,mr[self.status_code]['message'],self._response.headers,None)

mr = dict()        
mr[400] = dict(message='Bad Request',
               details='The request cannot be fulfilled due to bad syntax. See REST API Reference for the correct syntax.',
               error_code = 'error_bad_request')
mr[401] = dict(message='Authorization Required',
               details='The authentication details are incorrect. Provide the correct channel API key or user API key. See Channel Data Control and ThingSpeak API Keys for information on API keys.',
               error_code = 'error_auth_required')
mr[404] = dict(message='Resource Not Found',
               details='The requested resource was not found. Check the URL and try again.',
               error_code = 'error_resource_not_found')
mr[405] = dict(message='Method Not Allowed',
               details='Use the proper HTTP method for this request. See REST API Reference for the allowed methods.',
               error_code = 'error_method_invalid')
mr[409] = dict(message='Conflict',
               details='The request is in conflict with the current state of the targeted resource. Try your request again or change the request to resolve the conflict.',
               error_code = 'error_conflict')
mr[413] = dict(message='Request Entity Too Large',
               details='Your request is too large. Reduce the size and try again.',
               error_code = 'error_request_too_large')
mr[421] = dict(message='No Action Performed',
               details='The server attempted to process your request, but has no action to perform.',
               error_code = 'error_no_action')
mr[429] = dict(message='Too Many Requests',
               details='Wait before making another request. See How to Buy and Frequently Asked Questions for specific rate limits.',
               error_code = 'error_too_many_requests')
mr[500] = dict(message='Internal Server Error',
               details='An unexpected condition was encountered.',
               error_code = '')
mr[502] = dict(message='Bad Gateway	',
               details='The server received an invalid response from the upstream server. Check your network connection and try again.',
               error_code = '')
mr[503] = dict(message='Service Unavailable	',
               details='The server was unavailable or unable to process your request. Try your request later.',
               error_code = '')
        
 
if __name__ ==  '__main__':
    response_sample= requests.get(' https://api.thingspeak.com/channels/9/feeds.json',params=dict(results=2))
    check_response(response_sample)