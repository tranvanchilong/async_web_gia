import b_func
import asyncio
import time
import random

class b_test_proxy:
    '''
    Class chỉ dùng để test các proxy
    '''
    def __init__ (self, number=50, second=1, time_out=60, total_concurrent=50):
        self.logger = b_func.b_log('proxy_test')
        self.rq_ = b_func.async_rq(number, second, time_out, total_concurrent)
        self._200 = 0
        self._500 = 0
        self.total_proxy = b_func.ROTATING_PROXY_LIST
        random.shuffle(self.total_proxy)
        self.logger.info(f"total proxy: {len(self.total_proxy)}")

    async def test_proxy(self):
        url = "https://ident.me"
        await asyncio.gather(*(self.rq_url(url, proxy) for proxy in self.total_proxy))
        self.logger.info(f"total proxy: {len(self.total_proxy)} - 200: {self._200} - 500: {self._500}")
        await self.rq_.async_request_close()

    async def rq_url(self, url, proxy=None, callback=None, cb_kwargs=None):
        try:
            response = await self.rq_.async_request_all(url, "html", proxy=proxy)
            self.logger.info(f"stt: {response['status']} - rq_t: {response['request_time']} - proxy: {response['proxy']} - url: {url}")
            
            if response['status'] == 200:
                self._200 += 1
            else:
                self._500 += 1
            self.logger.debug(f"proxy: {proxy} - status: {response['status']} - rq_time: {response['request_time']} - data: {response['html']}")
        except:
            self.logger.exception(f"rq_final url exception: {url}")


async def test_():
    rq_ = b_test_proxy(number=30, second=1, time_out=60, total_concurrent=77)
    await rq_.test_proxy()

asyncio.run(test_())