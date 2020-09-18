# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests
from urllib.parse import urljoin
import json as Json
import pytz
import datetime
import pandas as pd

def validate(val,type_val):
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
        
class ThingSpeak():
    def __init__(self,user_api_key=None):
        self.user_api_key=user_api_key
        self._url = 'https://api.thingspeak.com'
    
    def __verify_response(self,response):
        if response.status_code == 200:
            return response
        else:
            raise ValueError("Request returned code {}. Message: {}".format(response.status_code,response.content))
            
    def __verify_channel(self,channel):
        if not isinstance(channel,Channel): raise TypeError('channel must be an instance of Channel')
        
    def __verify_user_api_key(self):
        if self.user_api_key is None:
            raise ValueError('user_api_key must be set.' )
            
    def __build_update_url(self):
        url =  self._url + '/update?api_key=' + self._write_api +'&'+ '&'.join(['field{}={}'.format(key,self._fields[key]) for key in self._fields])
        return url
    
    def get_channels(self):
        self.__verify_user_api_key()
        response = requests.get(urljoin(self._url,'channels.json?api_key={}'.format(self.user_api_key)))
        if response.status_code == 200:
            channels_json = Json.loads(response.content)
            channels = []
            for ch in channels_json:
                channels.append(Channel(ch))
            return channels
        else:
            raise ValueError("Request returned code {}. Message: {}".format(response.status_code,response.content))
            
    def get_channel(self,channel_id,read_api_key = None, write_api_key=None):
        url='/'.join([self._url,'channels',str(channel_id),'status.json'])
        print(url)
        response=requests.get(url,params=dict(api_key=None if read_api_key is None else read_api_key))
        response = self.__verify_response(response)
        if response.content.decode()=='"-1"':
            print('Channel may require read api key or does not exist')
            return
        else:
            json = Json.loads(response.content)
            json_channel = json['channel']
            json_channel['id'] = channel_id
            api_keys = []
            if read_api_key  is not None: api_keys.append(dict(api_key=read_api_key, write_flag=False))
            if write_api_key is not None: api_keys.append(dict(api_key=write_api_key,write_flag=True))
            json_channel['api_keys'] = api_keys
            
            return Channel(json_channel)
        
        
#        json_channel = dict(id=channel_id,)
        
    def clear_channel(self,channel):
        self.__verify_channel(channel)
        url = '/'.join([self._url,'channels',str(channel.id),'feeds.json'])
        response = requests.delete(url,params=dict(api_key=self.user_api_key))
        response = self.__verify_response(response)
        return response
    
    def update_channel(self,channel):
        self.__verify_channel(channel)
        url = '/'.join([self._url,'channels','{}.json'.format(channel.id)])
        self.__verify_user_api_key()
        ch_json = dict(api_key=self.user_api_key)
        for var in ['name','description', 'latitude','longitude','elevation','public_flag','url','metadata']:
            ch_json[var]=channel[var]
        response=requests.put(url,data=ch_json)
        response=self.__verify_response(response)
        return Channel(Json.loads(response.content))
      
        
    def delete_channel(self,channel,force_delete = False):
        self.__verify_channel(channel)
        url = '/'.join([self._url,'channels','{}.json'.format(channel.id)])
        if not force_delete: 
            ans = input('Are you sure you want to delete the channel {} id: {}? (y)'.format(channel.name,channel.id))
            if not ans.lower() in ['y','yes']:
                print('Operation canceled')
                return
        response = requests.delete(url,params=dict(api_key=self.user_api_key))
        response = self.__verify_response(response)
                
            
    def delete_all_channels(self):        
        ans = input('Are you sure you want to delete all channels (there is no going back)? (y)')
        if ans.lower() not in ['y','yes']: return
        channels = self.get_channels()
        for ch in channels:
            self.delete_channel(ch,force_delete = True)
            
    def create_channel(self,
                       name=None, 
                       description=None, 
                       latitude=None, 
                       longitude=None, 
                       elevation=None, 
                       public_flag=False, 
                       url=None, 
                       metadata=None, 
                       tags=[],
                       fields=[]):
        if self.user_api_key is None:
            raise ValueError("To create a channel you first need to set the user_api_key, that can be found on your mathworks profile: 'https://thingspeak.com/account/profile'")
        for var in ['name','description','metadata','url']:
            if not isinstance(eval(var),(str,type(None))):
                raise ValueError("{} should be of type str".format(var))
        for var in ['latitude','longitude','elevation']:
            if not isinstance(eval(var),(int,float,type(None))):
                raise ValueError("{} should be of type int or float".format(var))
            if var == 'latitude':
                if eval(var) <-90 or eval(var) > 90:
                    raise ValueError('Invalid latitude. Should be between -90 and 90')
            elif var == 'longitude':
                if eval(var) < -180 or eval(var) > 180:
                    raise ValueError('Invalid longitude. Should be between -180 and 180')
        if not isinstance(public_flag,(bool,type(None))):
            raise ValueError("public_flag should be of type bool")
        if len(fields)>8:
            raise ValueError('Maximum number of fields is 8')
        channel = dict(api_key=self.user_api_key)
        for var in ['name','description','latitude','longitude','elevation','url','metadata']:
            if eval(var) is not None:
                channel[var]=eval(var)
        if tags != []:
            channel['tags']=','.join(tags)
        for field_i, field in enumerate(fields):
            channel['field{}'.format(field_i+1)] = field
        response = requests.post(urljoin(self._url,'channels.json'),json=channel)
        response = self.__verify_response(response)
        return Channel(Json.loads(response.content))
    
#    def set_fields(self,fields):
#        self._fields=dict()
#        for i,field in enumerate(fields):
#            if i <8:
#                self._fields[i+1]=fields[i]            
#            else:
#                raise ValueError('field outside maximum range (8).')

class Channel():
    def __init__(self,json={}):
        self._url = 'https://api.thingspeak.com'
        for var in ['id', 'name', 'description', 'latitude', 'longitude', 'created_at', 'elevation', 'last_entry_id', 'public_flag', 'url', 'ranking', 'metadata', 'license_id', 'github_url', 'tags', 'api_keys']:
            if var in json.keys():
                setattr(self,var, json[var])
            else:
                setattr(self,var,None)
                
    def __getitem__(self,attribute):
        return getattr(self,attribute)
    
    def __verify_response(self,response):
        if response.status_code == 200:
            return response
        else:
            raise ValueError("Request returned code {}. Message: {}".format(response.status_code,response.content))
            
    def get_api_keys(self,write_api_keys=True):
        keys = []
        for key in self.api_keys:
            if write_api_keys:
                if key['write_flag']:
                    keys.append(key['api_key'])
            else:
                if not key['write_flag']:
                    keys.append(key['api_key'])
        return keys
    
    def __get_api_key(self,index,write_api_key = True):
        keys = self.get_api_keys(write_api_keys=write_api_key)
        if len(keys) == 0: return None
        if len(keys)>index:
            return keys[index]
        else:
            raise ValueError('index greater than available keys')
            
    def get_write_api_key(self,index=0):
        return self.__get_api_key(index=index)
            
    def get_read_api_key(self,index=0):
        return self.__get_api_key(write_api_key=False,index=index)
    
    def write_data(self,data=[]):
        if data==[]: return
        get_str = ''
        if self.get_write_api_key()!='':
            get_str = 'api_key={}'.format(self.get_write_api_key())
        get_str = '&'.join([get_str, '&'.join(['field{}={}'.format(di+1,dval) for di,dval in enumerate(data)])])
        full_url = '/'.join([self._url,'update?'+get_str])
        print(full_url)
        response=requests.get(full_url)
        response = self.__verify_response(response)
        return Json.loads(response.content)
        
    def __build_read_url(self,kwargs):
        locals().update(kwargs)
        url = ''
        for var in ['results','days','minutes','start','end']:
            if eval(var) is not None:
                if url == '':
                    url='{}={}'.format(var,eval(var))
                else:
                    url='&'.join([url, '{}={}'.format(var,eval(var))])
                if var not in ['start', 'end']:
                    validate(eval(var),int)
                    break
                else:
                    validate(eval(var),str)
                    validate_datetime_sprtime(eval(var),'%Y-%m-%d %H:%M:%S')
                    if var == 'end': break
        var = 'timezone'
        if eval(var) not in pytz.all_timezones:
            raise ValueError('{} not a valid timezone'.format(eval(var)))
        else:
            url='&'.join([url, '{}={}'.format(var,eval(var))])
        for var in ['status','metadata','location']:
            validate(eval(var),bool)
            if eval(var):
                url = '&'.join([url,'{}={}'.format(var,eval(var))])
        for var in ['min','max']:
            if eval(var) is not None:
                validate(eval(var),(int,float))
                url = '&'.join([url,'{}={}'.format(var,eval(var))])
        for var in ['round']:
            if eval(var) is not None:
                validate(eval,int)
                url = '&'.join([url,'{}={}'.format(var,eval(var))])
        for var in ['timescale', 'sum','average','median']:
            if eval(var) is not None:
                validate(eval(var),(int,str))
                if isinstance(eval(var),str):
                    print('validated')
                    if eval(var) != 'daily': 
                        raise ValueError("{} options are: 'daily' or integer".format(var))
                url = '&'.join([url,'{}={}'.format(var,eval(var))])
        return url
    
    def read_feed(self,
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
        url = self.__build_read_url(variables)
        baseurl = '/'.join([self._url,'channels',str(self.id),'feeds.json?'])
        if self.get_read_api_key()!='':
            baseurl = baseurl+ 'api_key={}'.format(self.get_read_api_key())
        
        full_url = '&'.join([baseurl,url])
        response = requests.get(full_url)
        response = self.__verify_response(response)
        return Json.loads(response.content)
    
    def read_field(self,
                  field=1,
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
        url = self.__build_read_url(variables)
        validate(field,int)
        if not((field>0) and (field<9)): raise ValueError('field must be an integer between 1 and 8')
        baseurl = '/'.join([self._url,'channels',str(self.id),'fields',str(field)+'.json?'])
        if self.get_write_api_key()!='':
            baseurl = baseurl+ 'api_key={}'.format(self.get_write_api_key())
        full_url = '&'.join([baseurl,url])
        response = requests.get(full_url)
        response = self.__verify_response(response)
        return Json.loads(response.content)
    
    def get_field_data(self,json): #,field_name = True
        if 'channel' not in json.keys(): raise ValueError('Invalid json. channel key not found')
        if 'feeds' not in json.keys(): 
            print('no feed data available on json')
            return
        valid_fields = [key for key in json['channel'] if 'field' in key]
        if len(valid_fields) == 0: 
            print('No valid fields to retrive data.')        
            return
        if len(json['feeds']) == 0:
            print('No data available.')
            return
        fields = [key for key in valid_fields if key in json['feeds'][0].keys()]
        column_names = ['created_at','entry_id']
        for field in fields:
            column_names.append(field)
        df = pd.DataFrame(columns=column_names)
        for item in json['feeds']:
            df=df.append(item,ignore_index=True)
        return df
        
if __name__ == '__main__':
    t=ThingSpeak()
    print(t.__dict__)

    