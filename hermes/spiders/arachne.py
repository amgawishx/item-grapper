import scrapy


class ArachneSpider(scrapy.Spider):
    
    name = 'arachne'
    
    start_urls = ["https://free-proxy-list.net/",
                  "https://www.sslproxies.org/",
                  "https://www.us-proxy.org/"]

    def parse(self, response):
        table = response.css('table')
        rows = table.css('tr')
        for row in rows:
            cells = row.css('td')
            try:
                yield {
                    'IP Address': cells[0].css('::text').get(),
                    'Port': cells[1].css('::text').get(),
                    'Code': cells[2].css('::text').get(),
                    'Anonymity': cells[4].css('::text').get(),
                    'Https': cells[6].css('::text').get(),
                }
            except IndexError:
                yield None
