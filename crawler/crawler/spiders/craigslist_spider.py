import scrapy
from scrapy.exporters import JsonItemExporter
from crawler.items import CraigslistItem
from bs4 import BeautifulSoup

class CraigslistSpider(scrapy.Spider):
	name = "craigslist"
	allowed_domains = ["losangeles.craigslist.org"]
	# start_urls = ["https://losangeles.craigslist.org/d/housing/search/hhh"]
	start_urls = ["https://losangeles.craigslist.org/d/apts-housing-for-rent/search/apa"]
	download_delay = 1
	exporter = None
	output_path = "../../../output/craigslist.json"

	def parse(self, response):
		try:
			ouput_file = open(output_path, 'w')
			self.exporter = JsonItemExporter(ouput_file)
			self.exporter.start_exporting()
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
			self.exporter.export_item(item)
		except:
			print "Export Error!"
		return item

	def closed(self, reason):
		self.exporter.finish_exporting()
		self.exporter.file.close()
		return
