import scrapy
from scrapy.exporters import JsonItemExporter
from crawler.items import RealtorItem
from bs4 import BeautifulSoup
import sqlite3

class RealtorSpider(scrapy.Spider):
	name = "realtor_sql"
	allowed_domains = ["realtor.com"]
	start_urls = []
	for i in range(1, 68):
		tmp_url = "https://www.realtor.com/apartments/Los-Angeles_CA"
		if i == 1:
			start_urls.append(tmp_url)
		else:
			start_urls.append(tmp_url+'/pg-'+str(i))
	download_delay = 0.5
	database = sqlite3.connect("/Users/sora/DATA/Work/Career/real-estate-analysis/output/realtor.db")
	cur = database.cursor()
	with database:
		cur.execute("CREATE TABLE IF NOT EXISTS property ( url text, street text, locality text, region text, postal text, latitude text, longitude text, price text, detail text );")

	def parse(self, response):
		try:
			html = BeautifulSoup(response.body, "html5lib")
			table = html.find('ul', attrs={'class': 'prop-list'})
			lists = table.find_all('li', attrs={'class': 'component_property-card', 'class': 'js-component_property-card'})
			for item in lists:
				link = item.find('div', attrs={'class': 'card-box'}).find('a')['href']
				yield scrapy.Request(url="https://www.realtor.com" + link, callback=self.parse_page)
		except:
			print "Fetch Error!"
		return

	def parse_page(self, response):
		item = RealtorItem()
		try:
			item['url'] = response.url
			html = BeautifulSoup(response.body, "html5lib")
			address_tag = html.find('div', attrs={'class': 'ldp-header-address-wrapper'})
			map_tag = address_tag.find('span', attrs={'itemprop': 'geo'})
			layout_tag = html.find('div', attrs={'id': 'ldp-property-meta'})
			price_tag = html.find('div', attrs={'class': 'ldp-header-price'})
			detail_tag = html.find('div', attrs={'id': 'ldp-detail-overview'})
			tags = [address_tag, map_tag, layout_tag, price_tag, detail_tag]
			# item name, tags index, tag name, attrs, is text, attr name
			template = [['street', 0, 'span', {'itemprop': 'streetAddress'}, True],
						['locality', 0, 'span', {'itemprop': 'addressLocality'}, True],
						['region', 0, 'span', {'itemprop': 'addressRegion'}, True],
						['postal', 0, 'span', {'itemprop': 'postalCode'}, True],
						['latitude', 1, 'meta', {'itemprop': 'latitude'}, False, 'content'],
						['longitude', 1, 'meta', {'itemprop': 'longitude'}, False, 'content'],
						['price', 3, 'span', {'itemprop': 'price'}, False, 'content'],
						['detail', 4, 'p', {'id': 'ldp-detail-romance'}, True]]
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
			cur.execute("INSERT INTO property VALUES ( :url, :street, :locality, :region, :postal, :latitude, :longitude, :price, :detail );",
				{'url':item.url, 'street':item.street, 'locality':item.locality, 'region':item.region, 'postal':item.postal, 'latitude':item.latitude, 'longitude':item.longitude, 'price':item.price, 'detail':item.detail})
		return

	def closed(self, reason):
		database.close()
		return
