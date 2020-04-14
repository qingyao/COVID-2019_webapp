import re, json, os, sys
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

url = 'https://www.zhihu.com/2019-nCoV/trends'
with urllib.request.urlopen(url) as response:
    html = response.read()

soup = BeautifulSoup(html, 'html.parser')
now = datetime.now()
with open('new_data/ncov_{}.txt'.format(now.strftime("%m%d-%Hh")),'w') as f:
    f.write(soup.prettify())

with open('new_data/ncov_{}.txt'.format(now.strftime("%m%d-%Hh"))) as f:
    content = f.read()

output_str = re.search('("historyList.+),"specialAccounts',content).group(1)
new_dat = json.loads('{'+output_str)
#print(new_dat['domesticList'])
#sys.exit()

## load previous data
all_files = sorted(os.listdir('data_dict'))
previous_dat = json.load(open('data_dict/'+all_files[-1]))

# for oversea data
with open('oversea_data_dict/'+sorted(os.listdir('oversea_data_dict'))[-1]) as f:
    oversea_dat = json.load(f)

## add new data
time_str = re.search('截至.+时',content).group()
mn, day, hr = re.search('(\d+) 月 (\d+) 日 (\d+)',time_str).group(1,2,3)
time = datetime(2020, int(mn), int(day), int(hr)).isoformat()

province_situation = {}
_,con,cure,death,sus = new_dat ['historyList'][0].values()
previous_dat['China']['confirm']['no'].append(con)
previous_dat['China']['cure']['no'].append(cure)
previous_dat['China']['death']['no'].append(death)
previous_dat['China']['suspect']['no'].append(sus)

previous_dat['China']['confirm']['time'].append(time)
previous_dat['China']['suspect']['time'].append(time)
previous_dat['China']['death']['time'].append(time)
previous_dat['China']['cure']['time'].append(time)

for i in new_dat['domesticList']:
    province = i['name']
    if len(province) <= 4:
        if province.startswith('中'):
            province = province[2:]
        else:
            province = province[:2]
    elif province.startswith('内'):
        province = province[:3]
    else:
        province = province[:2]
    print(province)    
    if province in previous_dat:
        
        previous_dat[province]['confirm']['no'].append(i['conNum'])
        previous_dat[province]['cure']['no'].append(i['cureNum'])
        previous_dat[province]['death']['no'].append(i['deathNum'])
        previous_dat[province]['suspect']['no'].append(i['susNum'])

        previous_dat[province]['confirm']['time'].append(time)
        previous_dat[province]['suspect']['time'].append(time)
        previous_dat[province]['death']['time'].append(time)
        previous_dat[province]['cure']['time'].append(time)

        province_situation[province] = {}
        for j in i['cities']:
            print(j)
            province_situation[province][j['name']] = [j['conNum'],j['cureNum'],j['deathNum']]

for i in new_dat['overseasList']:            
    country = i['name'].encode('utf8').decode('utf8')
    if country not in oversea_dat:
        print(country)
        oversea_dat[country] = {'confirm':{'no':[],'time':[]},
                                 'cure':{'no':[],'time':[]},
                                 'death':{'no':[],'time':[]},
                                 'suspect':{'no':[],'time':[]}}
    oversea_dat[country]['confirm']['no'].append(i['conNum'])
    oversea_dat[country]['cure']['no'].append(i['cureNum'])
    oversea_dat[country]['death']['no'].append(i['deathNum'])
    oversea_dat[country]['suspect']['no'].append(i['susNum'])
    oversea_dat[country]['confirm']['time'].append(time)
    oversea_dat[country]['suspect']['time'].append(time)
    oversea_dat[country]['death']['time'].append(time)
    oversea_dat[country]['cure']['time'].append(time)
    
with open('oversea_data_dict/oversea_data_dict_{}.json'.format(now.strftime("%m%d-%Hh")),'w') as f:
    json.dump(oversea_dat,fp=f)

with open('county_case.json','w') as f:
    json.dump(province_situation, fp=f)

with open('data_dict/data_dict_{}.json'.format(now.strftime("%m%d-%Hh")),'w') as f:
    json.dump(previous_dat,fp=f)
