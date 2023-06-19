import asyncio
import time
import b_func
from b_func import b_log
from parsel import Selector # https://github.com/scrapy/parsel scrapy selector

#
# Config
#
logger = b_log('user_agents_crawl')
json_file = b_func.b_write_aiofiles("json_data.json")

#
# Notes
#
'''
List cập nhật liên tục: https://techblog.willshouse.com/2012/01/03/most-common-user-agents/
'''

#
# Crawl
#
async def main_crawl():
    t0 = time.time()
    global rq_
    rq_ = b_func.b_crawl(number=1, second=1, time_out=60, total_concurrent=177, proxy_use=False, same_session=True)
    
    # Start
    for i in range(1, 11):
        url = f"https://developers.whatismybrowser.com/useragents/explore/software_type_specific/web-browser/{i}"
        rq_.add_queue(url, callback=parse, cb_kwargs=None)
    
    # Finish
    await rq_.wait()
    await json_file.close()
    print(f"Finish - total_time: {time.time() - t0}")


async def parse(response):
    # Retry
    if response['status'] != 200:
        rq_.add_queue(response['url'], callback=parse, cb_kwargs=None)
        return

    # Parse data
    selector = Selector(text=response['html'])
    item = {}
    for ua in selector.xpath('//tr'):
        item['ua'] = ua.xpath('./td/a/text()').get()
        item['software'] = ua.xpath('./td[2]/text()').get()
        item['os'] = ua.xpath('./td[3]/text()').get()
        print(f"ua: {item['ua']}")
        print(f"software: {item['software']}")
        print(f"os: {item['os']}")
        # print(f"ua: {ua.get()}")
        print("\n\n\n")
        
        # Write data
        if item['os'] in ['Windows', 'Macintosh', 'Linux']:
            if "Chrome" in item['software']:
                item['deviceCategory'] = "Desktop"
                await json_file.write(item)


asyncio.run(main_crawl())