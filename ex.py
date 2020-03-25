from bs4 import BeautifulSoup, SoupStrainer
import requests

params = {'q':'lạc trôi'}
r = requests.get('https://chiasenhac.vn/tim-kiem', params=params)
soup_trainer = SoupStrainer(class_={'media-title mt-0 mb-0'})
s = BeautifulSoup(r.text,'lxml',parse_only=soup_trainer)
url = s.find(class_='search_title search-line-music')
print(url['href'])

# goto music page
music_page = requests.get(url['href'])
soup_trainer_2 = SoupStrainer(class_='download_item')
s_2 = BeautifulSoup(music_page.text,'lxml',parse_only=soup_trainer_2)
list_urls = s_2.find_all(class_='download_item')
print([i['href'] for i in list_urls])
