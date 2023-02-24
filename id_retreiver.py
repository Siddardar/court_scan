import json
from bs4 import BeautifulSoup, SoupStrainer
import requests
import lxml
import re as string

ls = []
data = json.load(open(r'json_data\rawData.json'))

for i in data['Data']:
    s = i['href']
    link = f'https://www.myactivesg.com{s}' 
    
    del i['href']
    del i['imgSrc']
    del i['imgAlt']
    del i['activities']
    
    i['facilityName'] = i['facilityName'].title()
    i['facilityAddress'] = i['facilityAddress'].title()
    
    with requests.Session() as re:
        res = re.get(link)
        parser = 'lxml' 
        resp = re.get(link)
        soup = BeautifulSoup(resp.content, parser)

        try:
            button = soup.find('div', class_ = 'book-button')
            link = button.find('a', href = True)['href']
            id  = string.findall(r'\d+', str(link))[0]
            i['facilityID'] = id

        except:
            i['facilityID'] = 'Error'
            ls.append(i['facilityName'])

with open(r'json_data\data.json', "w") as jsonFile:
    json.dump(data, jsonFile)

print(ls)