from bs4 import BeautifulSoup
import pickle
import requests
import urllib3
import feedparser
import webbrowser, os

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
try:
	requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
except AttributeError:
	pass

def get(channel,maxEntries=4):
	#get browse_id
	if channel not in cache:
		html = requests.get('https://www.youtube.com/'+channel, verify=False).text
		i=21+html.index('"browse_id"')
		j=-1+html.index('}',i)
		cache[channel]=html[i:j]
		print('from web',cache[channel])
	browseId=cache[channel]
	print(channel,browseId)
	
	#get rss
	rss = feedparser.parse('https://www.youtube.com/feeds/videos.xml?channel_id='+browseId, request_headers={'Cache-control': 'max-age=600'})
	
	lastPublished=rss['entries'][0]['published']
	s=rss['feed']['author']+' - '+lastPublished[:10]+'<br/>'
	i=0
	for e in rss['entries']:
		s+='\n<a href="'+e['link']+'"><img src="'+e['media_thumbnail'][0]['url']+'"/></a>'
		i+=1
		if i>=maxEntries:
			break
	s+='\n<br/>\n'
	return {'lastPublished':lastPublished,'html':s}

cache=dict()

try:
	with open('cache.pkl', 'rb') as f:
		cache = pickle.load(f)
except:
	print('no cache file')

with open('channels.txt') as f:
	lines = f.readlines()

channels=[]
for line in lines:
	channels.append(get(line.strip()))

channels.sort(key=lambda x: x['lastPublished'], reverse=True)

with open('index.html','w') as f:
	f.write('<style>*{font-size:36pt;padding:0;margin:0}img{width:460}</style>\n')
	for channel in channels:
		f.write(channel['html'])

webbrowser.open('file://' + os.path.realpath('index.html'))

with open('cache.pkl', 'wb') as f:
	pickle.dump(cache, f)
