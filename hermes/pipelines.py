# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from re import match

class InvalidDrop:
    """
    A filter to ensure that we acquired a valid proxy IP.
    """

    ip_pattern = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
    
    def process_item(self, item, spider):
        adapt = ItemAdapter(item)
        if match(self.ip_pattern, adapt.get("IP Address")):
            return item
        else:
            raise DropItem
            
class DuplicateDrop:
    """
    A filter to ensure that we don't acquire the same proxy twice from different sources.
    """
    
    def __init__(self):
        self.ips_seen = set()
        
    def process_item(self, item, spider):
        adapt = ItemAdapter(item)
        if adapt.get("IP Address") in self.ips_seen:
            raise DropItem
        else:
            self.ips_seen.add(adapt.get("IP Address"))
            return item

class NonHttpsDrop:
    """
    A filter to drop any non-https proxy for security reasons.
    """
    
    def process_item(self, item, adapt):
        adapt = ItemAdapter(item)
        if adapt.get("Https")=="no":
            raise DropItem
        else:
            return item


class NonEliteDrop:
    """
    A filter to drop any non-elite proxies to avoid detections as bots
    or any IP leaks.
    """

    def process_item(self, item, adapt):
        adapt = ItemAdapter(item)
        if adapt.get("Anonymity") != "elite proxy":
            raise DropItem
        else:
            return item
