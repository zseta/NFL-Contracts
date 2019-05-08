# -*- coding: utf-8 -*-

# Scrapy settings for NFLSalaries project

BOT_NAME = 'NFLSalaries'

SPIDER_MODULES = ['NFLSalaries.spiders']
NEWSPIDER_MODULE = 'NFLSalaries.spiders'

# user-agent
# USER_AGENT = ""

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure item pipelines
DB_SETTINGS = {
    "db": "nfl_contracts",
    "user": "root",
    "passwd": "root",
    "host": "localhost"
}

# Configure item pipelines
ITEM_PIPELINES = {
    'NFLSalaries.pipelines.DuplicatesPipeline': 1,
    'NFLSalaries.pipelines.DatabasePipeline': 2
}
