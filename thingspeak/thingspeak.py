# -*- coding: utf-8 -*-
"""
Spyder Editor

@author: Roger Selzler
"""

import requests
from urllib.parse import urljoin
import pytz
import datetime
import pandas as pd
import os

import thingspeak.mathworks_rest_api_responses as mra
import pytz
import requests
import json

if os.path.isfile('tests/variables.txt'):
    var_file =  'tests/variables.txt'
else:
    var_file = 'tests/variables_template.txt'

with open(var_file) as f:
    config= json.load(f)
    
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
        
class ThingSpeak():
    """tst.
    NAME
        ThingSpeak
    
    DESCRIPTION
        This module provides methods to easily access thingspeak from mathworks
    
    FUNCTIONS
        create_channel(...)
            Create a thingspeak channel.
            
        clear_channel(...)
            Clear the data of the channel, but keeps its configurations.
            
        delete_channel(channel,force_delete)
            Delete a channel.
            
        delete_all_channels(force_delete)
            Delete all channels for a given user.
            
        get_channels()
            Get all channels for a given user.
            
    Parameters
    ----------
        user_api_key (str): user api_key found on mathworks profile."""
    def __init__(self,user_api_key=None):
        self.user_api_key=user_api_key
        self._url = 'https://api.thingspeak.com'
            
    def __verify_channel(self,channel):
        if not isinstance(channel,Channel): raise TypeError('channel must be an instance of Channel')
        
    def __verify_user_api_key(self):
        if self.user_api_key is None:
            raise ValueError("To create a channel you first need to set the user_api_key, that can be found on your mathworks profile: 'https://thingspeak.com/account/profile'")
            # raise ValueError('user_api_key must be set.' )
    
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
        """
        Create a new channel.
        
        Parameters
        ----------
            name (str): Name of the Channel.
            
            description (str): 
                Description of the channel.
            
            latitude (float): 
                Latitude in degrees.
            
            longitude (float): 
                Longitude in degrees.
            
            elevation (float):
                Elevation in meters above sea.
            
            public_flag (bool):
                Whether the channel is public.
                        
            url (str): 
                The webpage URL for the channel
                
            metadata (string):
                Metadata for the channel, which can include JSON, XML, or any other data.
            
            tags (list):
                List of tags.
            
            fields (list):
                The label for the fields. If None, field will be innactive.                
            """
        self.__verify_user_api_key()
        for var in ['name','description','metadata','url']:
            if not isinstance(eval(var),(str,type(None))):
                raise ValueError("{} should be of type str".format(var))
        for var in ['latitude','longitude','elevation']:
            if not isinstance(eval(var),(int,float,type(None))):
                raise ValueError("{} should be of type int or float".format(var))
            if eval(var) is not None:
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
        mra.check_response(response)
        return Channel(json=json.loads(response.content))
    
    def clear_channel(self,channel):
        """Clear the feed of the channel.
        
        Parameters
        ----------
            channel (Channel): a Channel object from thingspeak
        
        Return
        ------
            response (Response object): response object from requests package.
        """
        self.__verify_channel(channel)
        url = '/'.join([self._url,'channels',str(channel.id),'feeds.json'])
        response = requests.delete(url,params=dict(api_key=self.user_api_key))
        response = mra.check_response(response)
        return response
    
    def delete_channel(self,channel,force_delete = False):
        """
        Delete a channel.
        
        Parameters
        ----------
            channel (Channel): a Channel object from thingspeak.
            force_delete(bool): if True, the channel will be deleted quietly
        """
        self.__verify_channel(channel)
        url = '/'.join([self._url,'channels','{}.json'.format(channel.id)])
        if not force_delete: 
            ans = input('Are you sure you want to delete the channel {} id: {}? (y)'.format(channel.name,channel.id))
            if not ans.lower() in ['y','yes']:
                print('Operation canceled')
                return
        response = requests.delete(url,params=dict(api_key=self.user_api_key))
        mra.check_response(response)
                
            
    def delete_all_channels(self):
        """Delete all channels based on user_api_key."""
        ans = input('Are you sure you want to delete all channels (there is no going back)? (y)')
        if ans.lower() not in ['y','yes']: return
        channels = self.get_channels()
        for ch in channels:
            self.delete_channel(ch,force_delete = True)
     
    def get_channels(self):
        """Get channels based on user_api_key."""
        self.__verify_user_api_key()
        baseurl = '/'.join([self._url,'channels.json'])
        params=dict(api_key=self.user_api_key)
        response = requests.get(baseurl,params=params)
        mra.check_response(response)
        channels_json = json.loads(response.content)
        channels = []
        for ch in channels_json:
            channels.append(Channel(json=ch))
        return channels
    
    def get_channel(self,channel_id):
        """
        Get channel based on channel id.
        
        Parameters
        ----------
            channel_id (int): the id of the channel.
        """
        url='/'.join([self._url,'channels','{}.json'.format(channel_id)])
        params = dict()
        if self.user_api_key is not None: params['api_key'] = self.user_api_key
        response=requests.get(url,params=params)
        mra.check_response(response)
        return Channel(json=json.loads(response.content))
        
    def read_channel_settings(self,channel):
        """Read channel settings.
        
        Parameters
        ----------
            channel (Channel): a Channel object from thingspeak
        
        Return
        ------
            json object with channel settings
        """
        baseurl = '/'.join([self._url,'channels','{}.json'.format(channel.id)])
        response = requests.get(baseurl,params=dict(api_key=self.user_api_key))
        mra.check_response(response)
        return json.loads(response.content)
            
    def update_channel(self,channel):
        self.__verify_channel(channel)
        url = '/'.join([self._url,'channels','{}.json'.format(channel.id)])
        self.__verify_user_api_key()
        ch_json = dict(api_key=self.user_api_key)
        for var in ['name','description', 'latitude','longitude','elevation','public_flag','url','metadata']:
            ch_json[var]=channel[var]
        response=requests.put(url,data=ch_json)
        response=self.__verify_response(response)
        return Channel(json.loads(response.content))
    
    
class Channel():
    def __init__(self,channel_id=None,read_api_key=None,write_api_key = None,json=None):
        self._url = 'https://api.thingspeak.com'
        if json is not None:
            self.__create_variables_from_json(json)
        else:
            if channel_id is None: raise ValueError("channel_id must be a valid integer.")
            self.id = channel_id
            self.api_keys=[]
            if write_api_key is not None:
                if type(write_api_key) != list: write_api_key = [write_api_key]
                for key in write_api_key:
                    if type(key) is not str:
                        raise TypeError('write_api_key must be a string or list of strings')
                    self.add_api_key(key,write=True)                    
            if read_api_key is not None:
                if type(read_api_key) != list: read_api_key = [read_api_key]
                for key in read_api_key:
                    if type(key) is not str:
                        raise TypeError('write_api_key must be a string or list of strings')
                    self.add_api_key(key,write=False)
                
            
    def __create_variables_from_json(self,json_):
        for key in ['id', 'name', 'description', 'latitude', 'longitude', 'created_at', 'elevation', 'last_entry_id', 'public_flag', 'url', 'ranking', 'metadata', 'license_id', 'github_url', 'tags', 'api_keys']:
            if key in json_.keys():
                if json_[key] is None:
                    setattr(self,key,None)
                else:
                    if key in ['id']:
                        setattr(self,key,int(json_[key]))
                    elif key in ['latitude','longitude','elevation']:
                        if json_[key] == '':
                            setattr(self,key,None)
                        else:
                            setattr(self,key,float(json_[key]))                        
                    else:
                        setattr(self,key,json_[key])
                
    def __build_request_params(self,kwargs,write=False):
        locals().update(kwargs)
        params=dict()
        if write:
            if self._write_api_key is not None:
                params['api_key'] = self._write_api_key
        else:
            if self.get_read_api_key() is not None:
                params['api_key'] = self.get_read_api_key()
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
    
    def add_api_key(self,api_key,write=False):
        """Add api key.
        
        Parameters
        ----------
            api_key (str): api_key set on thingspeak
            write (bool): if True, the api_key is for writing data to the channel. If False, api_key is for reading data from the channel.
        """
        if not isinstance(api_key,str): return None
        api_key=dict(api_key=api_key,write_flag=True if write else False)
        self.api_keys.append(api_key)
        
    def get_write_api_key(self,index=0):
        """Get write api key.
        
        Parameters
        ----------
            index (int): get the key by index.
        
        Returns
        -------
            api_key (str): returns the write api_key indexed by index.
        """
        write_api_keys = [api_key for api_key in self.api_keys if api_key['write_flag']]        
        if len(write_api_keys) == 0: return None
        if len(write_api_keys) > index:
            return write_api_keys[index]['api_key']
        else: raise ValueError('index out of range')
        
    def get_read_api_key(self,index=0):
        """Get the read api key.
        
        Parameters
        ----------
            index (int): get the key by index.
            
        Returns
        -------
            api_key (str): returns the read api_key indexed by index.
        """        
        read_api_keys = [api_key for api_key in self.api_keys if not api_key['write_flag']]
        if len(read_api_keys) == 0: return None
        if len(read_api_keys) > index:
            return read_api_keys[index]['api_key']
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
        """Read channel feed.
        
        Parameters
        ----------
        Please, refer to 'https://www.mathworks.com/help/thingspeak/readdata.html': 
            
            results (int):          Number of entries to retrieve. The maximum number is 8,000.
            
            days (int):             Number of 24-hour periods before now to include in response. The default is 1.
            minutes (int):          Number of 60-second periods before now to include in response. The default is 1440.
            start (str):            Start date in format YYYY-MM-DD%20HH:NN:SS.
            end (str):              End date in format YYYY-MM-DD%20HH:NN:SS.
            timezone(str):          Identifier from Time Zones Reference for this request. 'https://www.mathworks.com/help/thingspeak/time-zones-reference.html'
            offset (int):           Timezone offset that results are displayed in. Use the timezone parameter for greater accuracy.
            status (bool):          Include status updates in feed by setting "status=True".
            metadata (bool):        Include metadata for a channel by setting "metadata=True".
            location (bool):        Include latitude, longitude, and elevation in feed by setting "location=true".
            min (float):            Minimum value to include in response.
            max (float):            Maximum value to include in response.
            round (int):            Round to this many decimal places.
            timescale (int,str):    Get first value in this many minutes, valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily".
            sum (int,str):          Get sum of this many minutes, valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily".
            average(int,str):       Get average of this many minutes, valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily".
            median(inT,str):        Get median of this many minutes, valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily".

        """
        variables = locals()
        del variables['self']
        params = self.__build_request_params(variables)
        baseurl = '/'.join([self._url,'channels',str(self.id),'feeds.json?'])
        response = requests.get(baseurl,params=params)
        mra.check_response(response)
        return(json.loads(response.content))
    
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
        params = self.__build_request_params(variables,write=False)
        validate_type(field,int)
        if not((field>0) and (field<9)): raise ValueError('field must be an integer between 1 and 8')
        baseurl = '/'.join([self._url,'channels',str(self.id),'fields',str(field)+'.json?'])
        response = requests.get(baseurl,params)
        mra.check_response(response)
        # response = self.__verify_response(response)
        return json.loads(response.content)
    
    def read_settings(self):
        baseurl = '/'.join([self._url,'channels','{}.json'.format(self.id)])
        response = requests.get(baseurl)
        mra.check_response(response)
        return json.loads(response.content)
            
    
    def write_channel_feed(self,data=None,**kwargs):
        """Write data to the channel.
        
        data (list): contain the values to be written on speakthing's fields.
        field<N>: specifies the value to be written on field 'N', where N is an integer from 1 to 8.
        """
        baseurl = '/'.join([self._url,'update.json'])
        params = dict()
        if data is not None:
            if not isinstance(data,list): data = [data]
            if len(data) <8:
                for data_i in range(len(data)):
                    params['field{}'.format(data_i+1)] = data[data_i]
        else:
            for i in range(8):
                if 'field{}'.format(i+1) in kwargs:
                    params['field{}'.format(i+1)] = kwargs['field{}'.format(i+1)]
                    
        if self.get_write_api_key() is not None:
            params['api_key'] = self.get_write_api_key()
        response = requests.get(baseurl,params)
        mra.check_response(response)
        return(json.loads(response.content))
   
# class __Channel():
#     def __init__(self,json={}):
#         self._url = 'https://api.thingspeak.com'
#         for var in ['id', 'name', 'description', 'latitude', 'longitude', 'created_at', 'elevation', 'last_entry_id', 'public_flag', 'url', 'ranking', 'metadata', 'license_id', 'github_url', 'tags', 'api_keys']:
#             if var in json.keys():
#                 setattr(self,var, json[var])
#             else:
#                 setattr(self,var,None)
                
#     def __getitem__(self,attribute):
#         return getattr(self,attribute)
    
#     def __verify_response(self,response):
#         if response.status_code == 200:
#             return response
#         else:
#             raise ValueError("Request returned code {}. Message: {}".format(response.status_code,response.content))
            
#     def get_api_keys(self,write_api_keys=True):
#         keys = []
#         for key in self.api_keys:
#             if write_api_keys:
#                 if key['write_flag']:
#                     keys.append(key['api_key'])
#             else:
#                 if not key['write_flag']:
#                     keys.append(key['api_key'])
#         return keys
    
#     def __get_api_key(self,index,write_api_key = True):
#         keys = self.get_api_keys(write_api_keys=write_api_key)
#         if len(keys) == 0: return None
#         if len(keys)>index:
#             return keys[index]
#         else:
#             raise ValueError('index greater than available keys')
            
#     def get_write_api_key(self,index=0):
#         return self.__get_api_key(index=index)
            
#     def get_read_api_key(self,index=0):
#         return self.__get_api_key(write_api_key=False,index=index)
    
#     def write_data(self,data=[]):
#         if data==[]: return
#         get_str = ''
#         if self.get_write_api_key()!='':
#             get_str = 'api_key={}'.format(self.get_write_api_key())
#         get_str = '&'.join([get_str, '&'.join(['field{}={}'.format(di+1,dval) for di,dval in enumerate(data)])])
#         full_url = '/'.join([self._url,'update?'+get_str])
#         print(full_url)
#         response=requests.get(full_url)
#         response = self.__verify_response(response)
#         return Json.loads(response.content)
        
#     def __build_read_url(self,kwargs):
#         locals().update(kwargs)
#         url = ''
#         for var in ['results','days','minutes','start','end']:
#             if eval(var) is not None:
#                 if url == '':
#                     url='{}={}'.format(var,eval(var))
#                 else:
#                     url='&'.join([url, '{}={}'.format(var,eval(var))])
#                 if var not in ['start', 'end']:
#                     validate(eval(var),int)
#                     break
#                 else:
#                     validate(eval(var),str)
#                     validate_datetime_sprtime(eval(var),'%Y-%m-%d %H:%M:%S')
#                     if var == 'end': break
#         var = 'timezone'
#         if eval(var) not in pytz.all_timezones:
#             raise ValueError('{} not a valid timezone'.format(eval(var)))
#         else:
#             url='&'.join([url, '{}={}'.format(var,eval(var))])
#         for var in ['status','metadata','location']:
#             validate(eval(var),bool)
#             if eval(var):
#                 url = '&'.join([url,'{}={}'.format(var,eval(var))])
#         for var in ['min','max']:
#             if eval(var) is not None:
#                 validate(eval(var),(int,float))
#                 url = '&'.join([url,'{}={}'.format(var,eval(var))])
#         for var in ['round']:
#             if eval(var) is not None:
#                 validate(eval,int)
#                 url = '&'.join([url,'{}={}'.format(var,eval(var))])
#         for var in ['timescale', 'sum','average','median']:
#             if eval(var) is not None:
#                 validate(eval(var),(int,str))
#                 if isinstance(eval(var),str):
#                     print('validated')
#                     if eval(var) != 'daily': 
#                         raise ValueError("{} options are: 'daily' or integer".format(var))
#                 url = '&'.join([url,'{}={}'.format(var,eval(var))])
#         return url
    
#     def read_feed(self,
#                   results=None,
#                   days=None,
#                   minutes=None,
#                   start=None,
#                   end=None,
#                   timezone=pytz.utc.zone,
#                   status=False,
#                   metadata=False,
#                   location=False,
#                   min=None,
#                   max=None,
#                   round=None,
#                   timescale=None,
#                   sum=None,
#                   average=None,
#                   median=None):
#         variables = locals()
#         del variables['self']
#         url = self.__build_read_url(variables)
#         baseurl = '/'.join([self._url,'channels',str(self.id),'feeds.json?'])
#         if self.get_read_api_key()!='':
#             baseurl = baseurl+ 'api_key={}'.format(self.get_read_api_key())
        
#         full_url = '&'.join([baseurl,url])
#         response = requests.get(full_url)
#         response = self.__verify_response(response)
#         return Json.loads(response.content)
    
#     def read_field(self,
#                   field=1,
#                   results=None,
#                   days=None,
#                   minutes=None,
#                   start=None,
#                   end=None,
#                   timezone=pytz.utc.zone,
#                   status=False,
#                   metadata=False,
#                   location=False,
#                   min=None,
#                   max=None,
#                   round=None,
#                   timescale=None,
#                   sum=None,
#                   average=None,
#                   median=None):
#         variables = locals()
#         del variables['self']
#         url = self.__build_read_url(variables)
#         validate(field,int)
#         if not((field>0) and (field<9)): raise ValueError('field must be an integer between 1 and 8')
#         baseurl = '/'.join([self._url,'channels',str(self.id),'fields',str(field)+'.json?'])
#         if self.get_write_api_key()!='':
#             baseurl = baseurl+ 'api_key={}'.format(self.get_write_api_key())
#         full_url = '&'.join([baseurl,url])
#         response = requests.get(full_url)
#         response = self.__verify_response(response)
#         return Json.loads(response.content)
    
#     def get_field_data(self,json): #,field_name = True
#         if 'channel' not in json.keys(): raise ValueError('Invalid json. channel key not found')
#         if 'feeds' not in json.keys(): 
#             print('no feed data available on json')
#             return
#         valid_fields = [key for key in json['channel'] if 'field' in key]
#         if len(valid_fields) == 0: 
#             print('No valid fields to retrive data.')        
#             return
#         if len(json['feeds']) == 0:
#             print('No data available.')
#             return
#         fields = [key for key in valid_fields if key in json['feeds'][0].keys()]
#         column_names = ['created_at','entry_id']
#         for field in fields:
#             column_names.append(field)
#         df = pd.DataFrame(columns=column_names)
#         for item in json['feeds']:
#             df=df.append(item,ignore_index=True)
#         return df








if __name__ == '__main__':
    t=ThingSpeak()
    print(t.__dict__)

    