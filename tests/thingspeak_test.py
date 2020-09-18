import unittest
import thingspeak
import json

with open('variables.txt') as f:
    var= json.load(f)
class Test_thingspeak(unittest.TestCase):
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
if __name__ == '__main__':
    unittest.main()