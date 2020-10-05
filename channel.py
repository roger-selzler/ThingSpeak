# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 12:29:35 2020

@author: rogerselzler
"""
import thingspeak.mathworks_rest_api_responses as mra
import pytz
import requests
import json

def validate_type(val, type_val):
    if not isinstance(val,list): val= [val]
    for v in val:
        if not isinstance(v,type_val):
            if isinstance(v,bool) and (bool not in type_val): raise TypeError('Value should be of type: {}'.format(type_val))
#        if type(v) not in type_val:
            raise TypeError('Value should be of type: {}'.format(type_val))      
            
def validate_datetime_sprtime(val,fmt):
    try:
        datetime.datetime.strptime(val,fmt)
    except ValueError:
        raise ValueError('Incorrect data format, should be {}'.format(fmt))

class Channel():
    def __init__(self,channel_id,read_api_key=None,write_api_key = None):
        self._url = 'https://api.thingspeak.com'
        self._channel_id = channel_id
        if write_api_key is not None:
            if type(write_api_key) == list:
                for key in write_api_key:
                    if type(key) is not str:
                        raise TypeError('write_api_key must be a string or list of strings')
                self._write_api_key = write_api_key
            elif type(write_api_key) == str:
                self._write_api_key = [write_api_key]
            else:
                raise TypeError('write_api_key must be a string or list of strings')  
        else: self._write_api_key = None
        if read_api_key is not None:
            if type(read_api_key) == list:
                for key in read_api_key:
                    if type(key) is not str:
                        raise TypeError('write_api_key must be a string or list of strings')
                self._read_api_key = read_api_key
            elif type(read_api_key) == str:
                self._read_api_key = [read_api_key]
            else:
                raise TypeError('read_api_key must be a string or list of strings')
        else: self._read_api_key = None
        
    def __build_request_params(self,kwargs,write=False):
        locals().update(kwargs)
        params=dict()
        if write:
            if self._write_api_key is not None:
                params['api_key'] = self._write_api_key
        else:
            if self._read_api_key is not None:
                params['api_key'] = self._read_api_key
        for var in ['results','days','minutes','start','end']:
            if eval(var) is not None:                
                if var not in ['start', 'end']:
                    validate_type(eval(var),int)
                else:
                    validate_type(eval(var),str)
                    validate_datetime_sprtime(eval(var),'%Y-%m-%d %H:%M:%S')
                    # if var == 'end': break
                params[var] = eval(var)
        var = 'timezone'
        if eval(var) not in pytz.all_timezones:
            raise ValueError('{} not a valid timezone'.format(eval(var)))
        else:
            params[var] = eval(var)
        for var in ['status','metadata','location']:
            validate_type(eval(var),bool)
            if eval(var):
                params[var] = eval(var)
        for var in ['min','max']:
            if eval(var) is not None:
                validate_type(eval(var),(int,float))
                params[var] = eval(var)
        for var in ['round']:
            if eval(var) is not None:
                validate_type(eval,int)
                params[var] = eval(var)
        for var in ['timescale', 'sum','average','median']:
            if eval(var) is not None:
                validate_type(eval(var),(int,str))
                if isinstance(eval(var),str):
                    if eval(var) != 'daily': 
                        raise ValueError("{} options are: 'daily' or integer".format(var))
                params[var] = eval(var)
        return params 
    
    @property
    def id(self):
        return self._channel_id
    
    def get_write_api_key(self,index=0):
        if self._write_api_key is None: return None
        if index < len(self._write_api_key):
            return self._write_api_key[index]
        else: raise ValueError('index out of range')
        
    def get_read_api_key(self,index=0):
        if self._read_api_key is None: return None
        if index < len(self._read_api_key):
            return self._read_api_key[index]
        else: raise ValueError('index out of range')
    
    def read_channel_feed(self,
                          results=None,
                          days=None,
                          minutes=None,
                          start=None,
                          end=None,
                          timezone=pytz.utc.zone,
                          status=False,
                          metadata=False,
                          location=False,
                          min=None,
                          max=None,
                          round=None,
                          timescale=None,
                          sum=None,
                          average=None,
                          median=None):
        variables = locals()
        del variables['self']
        params = self.__build_request_params(variables)
        baseurl = '/'.join([self._url,'channels',str(self.id),'feeds.json?'])
        response = requests.get(baseurl,params=params)
        mra.check_response(response)
        return(json.loads(response.content))
    
    def write_channel_feed(self,data=None,**kwargs):
        locals().update()
        params = dict()
        if data is not None:
            if not isinstance(data,list): data = [data]
            if len(data) <8:
                for data_i in range(len(data)):
                    params['field{}'.format(data_i+1)] = data[data_i]
        else:
            print(kwargs)
            for i in range(8):
                if 'field{}'.format(i+1) in kwargs:
                    params['field{}'.format(i+1)] = kwargs['field{}'.format(i+1)]
                    
        if self._write_api_key is not None:
            params['api_key'] = self.get_write_api_key()
        baseurl = '/'.join([self._url,'update'])
        response = requests.get(baseurl,params)
        mra.check_response(response)
        return(json.loads(response.content))
