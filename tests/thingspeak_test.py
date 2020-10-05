import unittest
import thingspeak
import json
import os

if os.path.isfile('tests/variables.txt'):
    var_file =  'tests/variables.txt'
else:
    var_file = 'tests/variables_template.txt'

with open(var_file) as f:
    var= json.load(f)
    
class Test_thingspeak(unittest.TestCase):
    def __init__(self,*args,**kwargs):
        super(Test_thingspeak,self).__init__(*args,**kwargs)
        self._user_api_key = var['user_api_key']
        self.t = thingspeak.ThingSpeak() #no user api key
        self.tk = thingspeak.ThingSpeak(self._user_api_key) # with user api key
        self.channel_name = 'test random Channel 1455'
        print('running tests')
        
    def test_create_channel(self):
        print("Create channel Test")
        # fails because no user api_key
        with self.assertRaises(ValueError):
            self.t.create_channel(name=self.channel_name)
        channel_count = len(self.tk.get_channels())
        channel = self.tk.create_channel(name=self.channel_name)        
        self.assertEqual(channel_count+1,len(self.tk.get_channels()))
        self.assertEqual(self.channel_name,channel.name)
        self.tk.delete_channel(channel,force_delete=True)
        self.assertEqual(channel_count,len(self.tk.get_channels()))
        
        
            
            
    def test_no_id(self):
        tu =  thingspeak.ThingSpeak()
        self.assertEqual(tu.user_api_key,None)
        
    def test_id(self):
        tu =  thingspeak.ThingSpeak()
        self.assertEqual(tu.user_api_key,None)
    
    def test_get_channel_public(self):
        t = thingspeak.ThingSpeak()
        ch = t.get_channel(channel_id=9)
        self.assertEqual(ch.id,9)
        self.assertEqual(ch.get_read_api_key(),None)
        self.assertEqual(ch.get_write_api_key(),None)
        self.assertEqual(ch.get_api_keys(),[])
        self.assertEqual(len(ch.read_feed(results=2)['feeds']),2)
        res = ch.read_field(2,results=1)
        self.assertTrue('field2' in res['feeds'][0].keys())
        with self.assertRaises(ValueError):
            ch.get_field_data({})
#        self.assertTrue()
        
#        t.get_channel()
    def test_get_channel_public(self):
        self.t.get_channel(9)
        print('TODO')
    
    def get_channels(self):
        print(self.__dict__)
        
if __name__ == '__main__':
    unittest.main()