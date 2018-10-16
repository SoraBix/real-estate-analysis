import scrapy
from scrapy.exporters import JsonItemExporter
from crawler.items import RealtorItem
from bs4 import BeautifulSoup

class RealtorSpider(scrapy.Spider):
	name = "realtor"
	allowed_domains = ["realtor.com"]
	start_urls = []
	for i in range(1, 68):
		tmp_url = "https://www.realtor.com/apartments/Los-Angeles_CA"
		if i == 1:
			start_urls.append(tmp_url)
		else:
			start_urls.append(tmp_url+'/pg-'+str(i))
	download_delay = 0.5
	exporter = None

	def parse(self, response):
		try:
			output_path = "/Users/sora/DATA/Work/Career/real-estate-analysis/output/realtor.json"
			ouput_file = open(output_path, 'w')
			self.exporter = JsonItemExporter(ouput_file)
			self.exporter.start_exporting()
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
			self.exporter.export_item(item)
		except:
			print "Export Error!"
		return item

	def closed(self, reason):
		self.exporter.finish_exporting()
		self.exporter.file.close()
		return
