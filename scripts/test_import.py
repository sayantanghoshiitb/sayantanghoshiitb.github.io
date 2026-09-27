import unittest
from import_ebird import aggregate,attach_media,date
def row(name='House Sparrow',sci='Passer domesticus',sid='S1',region='IN-WB',dt='2024-01-02'):
 return {'Common Name':name,'Scientific Name':sci,'Submission ID':sid,'State/Province':region,'Date':dt}
class ImportTests(unittest.TestCase):
 def test_world_dedup_country_overlap(self):
  birds,countries,count,_=aggregate([row(),row(sid='S2',region='ES-M'),row(sid='S3',dt='2023-01-02')])
  self.assertEqual(len(birds),1);self.assertEqual(sum(c['count'] for c in countries),2);self.assertEqual(count,3);self.assertEqual(birds[0]['firstSeen'],'2023-01-02')
 def test_without_photos_is_retained(self):
  birds,*_=aggregate([row()]);self.assertEqual(birds[0]['name'],'House Sparrow');self.assertNotIn('photo',birds[0])
 def test_non_species_excluded(self):
  birds,_,_,n=aggregate([row(),row(name='duck sp.',sci='Anatidae sp.')]);self.assertEqual(len(birds),1);self.assertEqual(n,1)
 def test_wrong_contributor_rejected(self):
  birds,*_=aggregate([row()]);m={'Media Type':'photo','Contributor ID':'999','Asset ID':'123','Scientific Name':'Passer domesticus'}
  self.assertEqual(attach_media(birds,[m],'2297440','Sayantan Ghosh'),0)
 def test_audio_rejected_and_owner_photo_accepted(self):
  birds,*_=aggregate([row()]);m={'Media Type':'audio','Contributor ID':'2297440','Asset ID':'123','Scientific Name':'Passer domesticus','Checklist ID':'S1'}
  self.assertEqual(attach_media(birds,[m],'2297440','Sayantan Ghosh'),0);m['Media Type']='photo';self.assertEqual(attach_media(birds,[m],'2297440','Sayantan Ghosh'),1)
 def test_wrong_checklist_rejected(self):
  birds,*_=aggregate([row()]);m={'Media Type':'photo','Contributor ID':'2297440','Asset ID':'123','Scientific Name':'Passer domesticus','Checklist ID':'S999'}
  self.assertEqual(attach_media(birds,[m],'2297440','Sayantan Ghosh'),0)
 def test_invalid_data_fails(self):
  with self.assertRaises(ValueError):aggregate([{'Common Name':'Sparrow'}])
  with self.assertRaises(ValueError):date('not a date')
if __name__=='__main__':unittest.main()
