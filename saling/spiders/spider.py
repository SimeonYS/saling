import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import SalingItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class SalingSpider(scrapy.Spider):
	name = 'saling'
	start_urls = ['https://www.sallingbank.dk/banken/nyheder?PID=14&page=1']
	page = 2
	def parse(self, response):
		post_links = response.xpath('//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)


		next_page = f'https://www.sallingbank.dk/banken/nyheder?PID=14&page={self.page}'
		if self.page < len(response.xpath('//ul[@class="items-list-paging items-clear"]/li').getall()):
			self.page +=1
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//div[@class="news nyhedsdetaljedato col-md-12"]/text()').get()
		title = response.xpath('//div[@class="news h2 nyhedsdetaljeteaser col-md-12"]/text() | //h1/text()').get()
		content = response.xpath('//div[@class="nyhedsdetaljetekst col-md-6"]//text() | //div[@class="col-md-8 txtbox"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=SalingItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
