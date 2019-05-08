from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose
from scrapy.spiders import Spider
from w3lib.html import remove_tags
from ..items import ContractItem


class ContractSpider(Spider):
    name = "contract_spider"
    start_urls = ["https://overthecap.com/position/"]

    # 1. SCRAPING
    def parse(self, response):
        for position_slug in response.css("#select-position > option::attr(value)").extract():
            url = self.start_urls[0] + position_slug
            yield Request(url, callback=self.extract, meta={"position": position_slug})

    def extract(self, response):
        for row in response.css(".position-table > tbody > tr"):
            item_loader = ItemLoader(item=ContractItem(), selector=row)
            # removes html tags
            item_loader.default_input_processor = MapCompose(remove_tags)
            item_loader.default_output_processor = TakeFirst()

            item_loader.add_css("player", "td:nth-of-type(1)")
            item_loader.add_css("team", "td:nth-of-type(2)")
            item_loader.add_css("age", "td:nth-of-type(3)")
            item_loader.add_css("total_value", "td:nth-of-type(4)")
            item_loader.add_css("avg_year", "td:nth-of-type(5)")
            item_loader.add_css("total_guaranteed", "td:nth-of-type(6)")
            item_loader.add_css("fully_guaranteed", "td:nth-of-type(7)")
            item_loader.add_css("free_agency_year", "td:nth-of-type(8)")
            item_loader.add_value("position", response.meta["position"])
            yield item_loader.load_item()
