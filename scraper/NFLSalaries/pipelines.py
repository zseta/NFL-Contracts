# -*- coding: utf-8 -*-
import MySQLdb
import pymysql
from scrapy.exceptions import NotConfigured, DropItem


class DuplicatesPipeline(object):
    def __init__(self):
        self.players = set()

    def process_item(self, item, spider):
        if item["player"] in self.players:
            raise DropItem("This player has already been stored: %s" % item)
        else:
            self.players.add(item["player"])
            return item


class DatabasePipeline(object):
    def __init__(self, db, user, passwd, host):
        self.conn = pymysql.connect(host=host,
                                    user=user,
                                    passwd=passwd,
                                    db=db,
                                    unix_socket="/opt/lampp/var/mysql/mysql.sock",
                                    charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:
            raise NotConfigured
        db = db_settings["db"]
        user = db_settings["user"]
        passwd = db_settings["passwd"]
        host = db_settings["host"]
        return cls(db, user, passwd, host)

    def process_item(self, item, spider):
        query = ("INSERT INTO Contract (player, team, position, age, total_value, avg_year, "
                 "total_guaranteed, fully_guaranteed, free_agency_year, free_agency_type)"
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        self.cursor.execute(query, (item["player"],
                                    item["team"],
                                    item["position"],
                                    item["age"],
                                    item["total_value"],
                                    item["avg_year"],
                                    item["total_guaranteed"],
                                    item["fully_guaranteed"],
                                    item["free_agency_year"],
                                    item["free_agency_type"]
                                    )
                            )
        self.conn.commit()
        return item

    def close_spider(self):
        self.conn.close()