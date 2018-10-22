import scrapy
from scrapy.exporters import JsonItemExporter
from crawler.items import CraigslistItem
from bs4 import BeautifulSoup
import sqlite3

class CraigslistSpider(scrapy.Spider):
	name = "craigslist_sql"
	allowed_domains = ["losangeles.craigslist.org"]
	start_urls = []
	for i in range(0, 3000, 120):
		tmp_url = "https://losangeles.craigslist.org/search/apa"
		if i == 0:
			start_urls.append(tmp_url)
		else:
			start_urls.append(tmp_url+'?s='+str(i))
	download_delay = 0.5
	database = sqlite3.connect("/Users/sora/DATA/Work/Career/real-estate-analysis/output/craigslist.db")
	cur = database.cursor()
	with database:
		cur.execute("CREATE TABLE IF NOT EXISTS property ( url text, price text, area text, title text, sub_title text, map_address text, latitude text, longitude text, detail text );")

	def parse(self, response):
		try:
			html = BeautifulSoup(response.body, "html5lib")
			table = html.find('ul', attrs={'class': 'rows'})
			lists = table.find_all('li', attrs={'class': 'result-row'})
			for item in lists:
				link = item.find('a')['href']
				yield scrapy.Request(url=link, callback=self.parse_page)
		except:
			print "Fetch Error!"
		return

	def parse_page(self, response):
		item = CraigslistItem()
		try:
			item['url'] = response.url
			html = BeautifulSoup(response.body, "html5lib")
			title_tag = html.find('h2')
			map_tag = html.find('div', attrs={'class': 'mapbox'})
			detail_tag = html.find('section', attrs={'class': 'userbody'})
			tags = [title_tag, map_tag, detail_tag]
			# item name, tags index, tag name, attrs, is text, attr name
			template = [['price', 0, 'span', {'class': 'price'}, True],
						['area', 0, 'span', {'class': 'housing'}, True],
						['title', 0, 'span', {'id': 'titletextonly'}, True],
						['sub_title', 0, 'small', {}, True],
						['map_address', 1, 'div', {'class': 'mapaddress'}, True],
						['latitude', 1, 'div', {'id': 'map'}, False, 'data-latitude'],
						['longitude', 1, 'div', {'id': 'map'}, False, 'data-longitude'],
						['detail', 2, 'section', {'id': 'postingbody'}, True]]
			for i in range(len(template)):
				temp = tags[template[i][1]].find(template[i][2], attrs=template[i][3])
				if temp:
					if template[i][4]:
						item[template[i][0]] = temp.text
					else:
						item[template[i][0]] = temp[template[i][5]]
		except:
			print "Parse Error!"
		try:
			self.db_insert(item)
		except:
			print "Export Error!"
		return item

	def db_insert(self, item):
		with database:
			cur.execute("INSERT INTO property VALUES ( :url, :price, :area, :title, :sub_title, :map_address, :latitude, :longitude, :detail );",
				{'url':item.url, 'price':item.price, 'area':item.area, 'title':item.title, 'sub_title':item.sub_title, 'map_address':item.map_address, 'latitude':item.latitude, 'longitude':item.longitude, 'detail':item.detail})
		return

	def closed(self, reason):
		database.close()
		return
