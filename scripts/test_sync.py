import unittest
from unittest.mock import patch
from sync_public import apply_photos,refresh

class SyncTests(unittest.TestCase):
 def data(self):return {'contributorId':'2297440','owner':'Sayantan Ghosh','profileId':'MjI5NzQ0MA','countries':[{'code':'IN','count':1}],'species':[{'name':'House Sparrow','scientificName':'Passer domesticus','countries':['IN'],'photo':{'assetId':'old'}}]}
 def photo(self):return {'userId':'USER2297440','mediaType':'photo','assetId':123,'taxonomy':{'sciName':'Passer domesticus'},'location':{'countryCode':'ES'}}
 def test_owner_photo_and_country(self):
  birds,unmatched=apply_photos(self.data(),[self.photo()]);self.assertEqual(birds[0]['photo']['assetId'],'123');self.assertEqual(birds[0]['countries'],['ES','IN']);self.assertEqual(unmatched,[])
 def test_reject_wrong_owner_and_restricted(self):
  for overrides in [{'userId':'USER999'},{'restricted':True},{'mediaType':'audio'},{'exoticCategory':'escapee'}]:
   with self.assertRaises(ValueError):apply_photos(self.data(),[{**self.photo(),**overrides}])
 def test_failure_retains_data(self):
  d=self.data()
  with patch('sync_public.sync_countries',side_effect=ValueError('offline')),patch('sync_public.sync_photos',side_effect=ValueError('offline')):new,errors=refresh(d)
  self.assertEqual(new['species'],d['species']);self.assertEqual(new['countries'],d['countries']);self.assertEqual(len(errors),2)
 def test_unmatched_not_invented(self):
  extra={**self.photo(),'taxonomy':{'sciName':'Unknown','comName':'Unknown bird'}}
  birds,unmatched=apply_photos(self.data(),[self.photo(),extra]);self.assertEqual(len(birds),1);self.assertEqual(unmatched,['Unknown bird'])
if __name__=='__main__':unittest.main()
