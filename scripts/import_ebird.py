"""Import your eBird Download My Data CSV and optional Macaulay media spreadsheet.
Never writes precise locations, comments, or credentials to the public site.
"""
import argparse,csv,json,re,datetime,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def key(s):return re.sub(r'[^a-z0-9]','',s.lower())
def field(row,*names):
 normalized={key(k):v.strip() for k,v in row.items() if k and isinstance(v,str)}
 return next((normalized[key(n)] for n in names if normalized.get(key(n))), '')
def date(value):
 for fmt in ['%Y-%m-%d','%m/%d/%Y','%d %b %Y','%d %B %Y','%Y-%m-%d %H:%M:%S']:
  try:return datetime.datetime.strptime(value,fmt).date().isoformat()
  except ValueError:pass
 if re.match(r'^\d{4}-\d\d-\d\dT',value):return date(value[:10])
 raise ValueError('Unrecognized observation date: '+value)
def rows(path):
 with open(path,encoding='utf-8-sig',newline='') as f:
  sample=f.read(8192);f.seek(0)
  dialect=csv.Sniffer().sniff(sample,delimiters=',\t');return list(csv.DictReader(f,dialect=dialect))
def species_level(name):return not any(s in name.lower() for s in [' sp.','/','hybrid',' x '])
def aggregate(observations):
 birds={};checklists=set();countries={};excluded=0
 for r in observations:
  name=field(r,'Common Name','comName');scientific=field(r,'Scientific Name','sciName');sid=field(r,'Submission ID','Checklist ID','subId')
  if not name or not scientific or not sid:raise ValueError('Checklist CSV must include Common Name, Scientific Name and Submission ID.')
  if not re.fullmatch(r'S\d+',sid):raise ValueError('Invalid checklist ID')
  checklists.add(sid)
  if field(r,'Countable') == '0' or not species_level(name):excluded+=1;continue
  exotic=field(r,'Exotic Code','Exotic Category').lower()
  if exotic in ['x','escapee']:excluded+=1;continue
  region=field(r,'State/Province','State Province','Country Code','Country','S/P');country=region.split('-')[0].upper()
  if not re.fullmatch('[A-Z]{2}',country):raise ValueError('Expected eBird region code (for example IN-WB) in State/Province or Country Code.')
  observed=date(field(r,'Date','Observation Date'));k=scientific.lower()
  b=birds.setdefault(k,{'name':name,'scientificName':scientific,'firstSeen':observed,'countries':set(),'checklists':set(),'regions':set()})
  b['regions'].add(region);b['firstSeen']=min(b['firstSeen'],observed);b['countries'].add(country);b['checklists'].add(sid);countries.setdefault(country,set()).add(k)
 result=[]
 for b in birds.values():b['regions']=sorted(b['regions']);b['countries']=sorted(b['countries']);b['checklists']=sorted(b['checklists']);result.append(b)
 return sorted(result,key=lambda b:b['name']),[{'code':c,'count':len(s)} for c,s in countries.items()],len(checklists),excluded
def attach_media(birds,media,contributor_id,owner):
 by_sci={b['scientificName'].casefold():b for b in birds};by_name={b['name'].casefold():b for b in birds};accepted=0
 for r in media:
  kind=field(r,'Media Type','mediaType').lower()
  if kind not in ['photo','photograph','image']:continue
  who=field(r,'User ID','Contributor ID','userId').removeprefix('USER').removeprefix('USR');credit=field(r,'Contributor','Observer','User Display Name','userDisplayName')
  if who and who!=contributor_id:continue
  if not who and credit.casefold()!=owner.casefold():continue
  b=by_sci.get(field(r,'Scientific Name','sciName').casefold()) or by_name.get(field(r,'Common Name','comName','Species').casefold())
  if not b:continue
  sid=field(r,'eBird Checklist ID','Checklist ID','ebirdChecklistId','Submission ID')
  if sid and sid not in b['checklists']:continue
  asset=field(r,'ML Catalog Number','Macaulay Library Catalog Number','Catalog Number','Asset ID','assetId').removeprefix('ML')
  if not asset.isdigit():continue
  if not b.get('photo'):
   photo={'assetId':asset,'assetUrl':f'https://macaulaylibrary.org/asset/{asset}','imageUrl':f'https://cdn.download.ams.birds.cornell.edu/api/v1/asset/{asset}/640','credit':owner}
   place=field(r,'Location Name','Location','Locality','Hotspot Name','eBird Hotspot')
   region=field(r,'State/Province','State Province','Region Code')
   country=field(r,'Country Code','Country')
   if place:photo['locationName']=place
   if re.fullmatch('[A-Z]{2}-[A-Za-z0-9]+',region):photo['regionCode']=region
   if re.fullmatch('[A-Z]{2}',country.upper()):photo['countryCode']=country.upper()
   b['photo']=photo;accepted+=1
 return accepted
def atomic_write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2),encoding='utf-8');os.replace(tmp,path)
def main():
 p=argparse.ArgumentParser();p.add_argument('--checklists',required=True,type=Path);p.add_argument('--media',type=Path);p.add_argument('--output',type=Path,default=ROOT/'data/birds.json');args=p.parse_args()
 old=json.loads(args.output.read_text('utf-8')) if args.output.exists() else {'profileId':'MjI5NzQ0MA','contributorId':'2297440','owner':'Sayantan Ghosh'}
 birds,countries,count,excluded=aggregate(rows(args.checklists))
 # Keep previously verified media for still-present species when refreshing checklists.
 prior={b['scientificName'].casefold():b.get('photo') for b in old.get('species',[])}
 for b in birds:
  if prior.get(b['scientificName'].casefold()):b['photo']=prior[b['scientificName'].casefold()]
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 if args.media:
  for b in birds:b.pop('photo',None)
  accepted=attach_media(birds,rows(args.media),old['contributorId'],old['owner']);old.update(lastPhotoSync=now,photoStatus='imported');print('Species with verified contributor photos:',accepted)
 old.update(species=birds,countries=countries,checklistCount=count,observationsComplete=True,countryMembershipComplete=True,lastObservationSync=now,lastCountrySync=now,source='Personal eBird checklist export',excludedNonSpeciesRows=excluded)
 atomic_write(args.output,old);print(f'Imported {len(birds)} distinct species from {count} checklists; excluded {excluded} ambiguous/escapee rows.')
if __name__=='__main__':main()
