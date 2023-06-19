import time
import traceback
import aiohttp
import asyncio
import random
import threading
from queue import Queue, Empty
from .b_functions import b_log
# from playwright.async_api import async_playwright

# Config
with open('./b_func/proxy.py', 'r', encoding='utf8') as f:
    ROTATING_PROXY_LIST = [line.strip() for line in f.readlines() if line.strip() != '' and "#" not in line]
def rd_ua():
    import json
    with open("./b_func/useragents.json", 'r', encoding='utf8') as f:
        data = f.read()
        useragents = json.loads(data)

    mobile_user_agents = [ua['ua'] for ua in useragents if ua['deviceCategory'] == 'mobile']
    desktop_user_agents = [ua['ua'] for ua in useragents if ua['deviceCategory'] == 'desktop']

    mobile_user_agents = list(set(mobile_user_agents))
    desktop_user_agents = list(set(desktop_user_agents))
    
    return mobile_user_agents, desktop_user_agents
mobile_user_agents, desktop_user_agents = rd_ua()


#
# Crawl
#
class b_crawl:
    '''
    Class chính để crawl, được gộp phần proxy vào.
    Cơ bản class sẽ tạo 3 async taks riêng biệt:
    - task monitor: để đếm số lượng task đang chạy và đang chờ, số lượng request 200, 500, proxies die...
    - task handle proxy: nếu proxy_use=False sẽ kết thúc luôn task này, và trong các hàm khác sẽ bỏ qua phần proxy. Task này sẽ dùng 3 queue, 1 queue proxy chính chạy ok, 1 queue proxy vừa sử dụng, và 1 queue proxy die.
        > q_proxy: queue chính là các proxy ok get ra xài luôn
        > q_put_proxy: các proxy vừa dùng xong sẽ được đưa vào queue này, task sẽ lấy proxy ra so sánh thời gian sử dụng xong với hiện tại nếu lớn hơn proxy_wait sẽ được đưa lại vào queue q_proxy
        > q_die_proxy: các proxy die sẽ được đưa vào queue này, task sẽ lấy proxy ra so sánh thời gian sử dụng xong với hiện tại nếu lớn hơn proxy_reanimate proxy có thể sử dụng lại, sau đó sẽ được đưa lại vào queue q_proxy
    - task create_task: task này sẽ lấy các url được thêm vào q_task_waitting từ hàm add_queue và so sánh số task running trong q_task_running, nếu nhỏ hơn max_rq_tasks thì sẽ tạo thêm task request, nếu không sẽ chờ. Mỗi url được lấy ra sẽ tạo task request và put vào q_task_running 1 đơn vị, sau khi hoàn thành sẽ get từ q_task_running để giảm số task running đi.
    '''
    def __init__ (self, 
        time_out=20, 
        max_rq_tasks=170, 
        proxy_use=False, 
        proxy_wait=10, 
        proxy_reanimate=600, 
        same_session=False, 
        log_folder='', 
        log_set="DEBUG" # Change to INFO to ignore DEBUG log
        ):

        self.logger = b_log(f'{log_folder}b_crawl')
        self.logger_200 = b_log(f'{log_folder}b_crawl_200', stream=False)    # log lưu request thành công, không show ra màn hình
        self.logger_500 = b_log(f'{log_folder}b_crawl_500', stream=False)    # log lưu request không thành công, không show ra màn hình
        self.logger_retry = b_log(f'{log_folder}b_crawl_retry', stream=False)    # log lưu request không thành công, không show ra màn hình
        self.log_set = log_set    # cấp độ log, DEBUG sẽ print các request ra màn hình
        self.same_session = same_session    # dùng async_request_session để gửi chung 1 session, nếu False thì sẽ dùng async_request_all mỗi lần gửi request sẽ tạo 1 session mới
        self.time_out = time_out
        self.max_rq_tasks = max_rq_tasks    # dùng để hạn chế số task trong async aio được tạo ra, url sẽ được lưu trong queue và k tạo task quá số này
        self._200 = 0   # count status 200
        self._404 = 0   # count status 404
        self._500 = 0   # count status 500
        self.proxy_wait = proxy_wait            # thời gian chờ giữa 2 lần request của cùng 1 proxy
        self.proxy_reanimate = proxy_reanimate  # thờI gian chờ phục hồi của proxy die
        self.q_proxy = asyncio.Queue()          # queue chính là các proxy ok get ra xài luôn
        self.q_put_proxy = asyncio.Queue()      # các proxy vừa dùng xong sẽ được đưa vào queue này, để tạo task sleep proxy_wait giây, để proxy có thể sử dụng lại, sau đó sẽ được đưa lại vào queue q_proxy
        self.q_die_proxy = asyncio.Queue()      # các proxy die sẽ được đưa vào queue này, để tạo task sleep proxy_reanimate giây, để proxy có thể sử dụng lại, sau đó sẽ được đưa lại vào queue q_proxy
        self.proxy_use = proxy_use              # True nếu sử dụng proxy
        self.q_task_waitting = asyncio.Queue()
        self.q_task_running = asyncio.Queue()
        self.total_rq_time = float(0)
    
    # Task quản lý các proxy queue, chờ phục hồi proxy
    async def task_handle_proxy(self):
        if self.proxy_use != True:
            return
        proxy_list = ROTATING_PROXY_LIST
        self.total_proxy = len(proxy_list)
        random.shuffle(proxy_list)
        for proxy in proxy_list:
            self.q_proxy.put_nowait({
                "proxy": proxy,
                "time": time.time()
            })
        self.logger.info(f"total proxy: {self.q_proxy.qsize()}")
        while True:
            if self.q_put_proxy.qsize() > 0:
                for i in range(self.q_put_proxy.qsize()):
                    proxy_data = await self.get_proxy(self.q_put_proxy)
                    if time.time() - proxy_data['time'] > self.proxy_wait:
                        proxy_data.update({'time': time.time()})
                        self.q_proxy.put_nowait(proxy_data)
                    else:
                        self.q_put_proxy.put_nowait(proxy_data)
            if self.q_die_proxy.qsize() > 0:
                for i in range(self.q_die_proxy.qsize()):
                    proxy_data = await self.get_proxy(self.q_die_proxy)
                    if time.time() - proxy_data['time'] > self.proxy_reanimate:
                        proxy_data.update({'time': time.time()})
                        self.q_proxy.put_nowait(proxy_data)
                    else:
                        self.q_die_proxy.put_nowait(proxy_data)
            await asyncio.sleep(0.01)
    
    # Get proxy từ queue
    async def get_proxy(self, queue_):
        proxy_data = await queue_.get()
        queue_.task_done()
        return proxy_data
    
    # Task monitor chung, để đếm số request thành công, không thành công, proxy die... và lưu lại log
    async def async_task_monitor(self):
        t0 = time.time()  
        while True:
            await asyncio.sleep(5)
            avg_rq = round(self.total_rq_time / (self._200 + self._404 + self._500), 2)
            if self.proxy_use == False:
                self.logger.info(f"crawl: {(self._200 + self._404 + self._500) / (time.time() - t0):.2f}/s - sucess: {self._200 / (time.time() - t0):.2f}/s - 200: {self._200} - 404: {self._404} - 500: {self._500} - t_run: {self.q_task_running.qsize()} - t_wait: {self.q_task_waitting.qsize()} - avg_rq_time: {avg_rq} s")
            else:
                self.logger.info(f"crawl: {(self._200 + self._404 + self._500) / (time.time() - t0):.2f}/s - sucess: {self._200 / (time.time() - t0):.2f}/s - 200: {self._200} - 404: {self._404} - 500: {self._500} - proxy_ok: {self.total_proxy - self.q_die_proxy.qsize()} - proxy_die: {self.q_die_proxy.qsize()}  - t_run: {self.q_task_running.qsize()} - t_wait: {self.q_task_waitting.qsize()} - avg_rq_time: {avg_rq} s")
    
    # Thêm url vào queue để crawl
    def add_queue(self, url, callback=None, cb_kwargs=None):
        self.q_task_waitting.put_nowait([url, callback, cb_kwargs])
        
    # Task quản lý crawl, tạo các task crawl
    async def create_task_queue(self):
        # Init rq_
        self.rq_ = async_rq(self.time_out, self.max_rq_tasks)
        while True:
            # Check nếu tổng số task running đang lớn hơn max_rq_tasks thì bỏ qua không add thêm task
            if self.q_task_running.qsize() > self.max_rq_tasks:
                await asyncio.sleep(0.001)
                continue
            task_get = await self.q_task_waitting.get()
            url, callback, cb_kwargs = task_get[0], task_get[1], task_get[2]
            
            # Create request task
            asyncio.create_task(self.rq_final(url, callback=callback, cb_kwargs=cb_kwargs))
            self.q_task_running.put_nowait('')
            
            await asyncio.sleep(0.001)

    # Task chờ để đợi các task crawl, xác định thời điểm mà task running và task waiting đều = 0 là không còn task nào để thực hiện, 
    # sẽ kill các task để finish. Thực ra nếu đúng thì phải đếm chính xác các task đang active, nếu tổng số bằng số task chính (hiện tại là 4 task
    # bao gồm main (wait chạy trong main), monitor, proxy, create_task_queue) thì tức là không còn task request hay parse, insert db nào đang hoạt động và 
    # có thể finish
    async def wait(self):
        rq_task = asyncio.create_task(self.create_task_queue())
        monitor_task = asyncio.create_task(self.async_task_monitor())
        proxy_task = asyncio.create_task(self.task_handle_proxy())
        tasks = [rq_task, monitor_task, proxy_task]
        # await asyncio.sleep(3)  # wait for initial

        # Stop
        t0 = time.time()  
        while True:
            # Stop thread
            if self.q_task_waitting.qsize() == 0 and self.q_task_running.qsize() == 0:
                count_active_tasks = len(asyncio.all_tasks())
                if count_active_tasks < 5: # thực tế các task đang chạy chỉ còn các task quản lý chính, nên có thể kết thúc qui trình
                    for task in asyncio.all_tasks():
                        print(task)
                    break
            await asyncio.sleep(0.01)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await self.rq_.async_request_close()
        self.logger.info("Thread wait stop")


    
    # Hàm request thẳng không qua queue xử lý, vẫn chờ các proxy và giới hạn luồng, chỉ thêm vào để trả thẳng kết quả thay vì phải trả qua
    # callback gây khó khăn trong nhiều trường hợp
    async def single_request(self, url, type="html", method="GET", payload=None, headers=None, callback=None, cb_kwargs=None):
        retry_ = 0
        while True:
            retry_ += 1
            if retry_ > 3:
                return "max retry"

            if self.q_task_running.qsize() > self.max_rq_tasks:
                await asyncio.sleep(0.001)
                continue
            self.q_task_running.put_nowait('')

            # Set proxy
            if self.proxy_use == True: 
                proxy_data = await self.get_proxy(self.q_proxy)
                proxy = proxy_data['proxy']
            else: proxy = None

            response = await self.rq_.async_request_all(url, type=type, method=method, payload=payload, proxy=proxy, headers=headers)
            if response['status'] not in [200, 404]:
                self.logger_retry.info(f"retry: {retry_} - status: {response['status']} - url: {url} - proxy: {proxy}")
                await self.q_task_running.get()
                self.total_rq_time += float(response['request_time'])
                if self.proxy_use == True: self.q_put_proxy.put_nowait({"proxy": proxy, "time": time.time() - float(response['request_time'])})
                continue
            return await self.handle_response(url, response, proxy, callback=callback, cb_kwargs=cb_kwargs)
    # Hàm request chính, xử lý các vấn đề liên quan đến request như proxy, status ...
    async def rq_final(self, url, type_="html", callback=None, cb_kwargs=None):
        try:
            # Set proxy
            if self.proxy_use == True: 
                proxy_data = await self.get_proxy(self.q_proxy)
                proxy = proxy_data['proxy']
            else: proxy = None
            
            # Request
            if self.same_session == True:
                response = await self.rq_.async_request_session(url, type_, proxy=proxy)
            else:
                response = await self.rq_.async_request_all(url, type_, proxy=proxy)
            
            return await self.handle_response(url, response, proxy, callback=callback, cb_kwargs=cb_kwargs)
        except:
            self.logger_500.exception(f"rq_final url exception: {url}")
            await self.q_task_running.get()
            return traceback.format_exc()
    # Hàm xử lý các response, tuỳ theo response mà xử lý proxy đưa vào các queue tương ứng
    async def handle_response(self, url, response, proxy, callback=None, cb_kwargs=None):
        if self.log_set == "DEBUG":
            print(f"stt: {response['status']} - rq_t: {response['request_time']} - proxy: {response['proxy']} - url: {url}")

        # Count status & handle proxy
        if response['status'] == 200:
            if self.proxy_use == True: self.q_put_proxy.put_nowait({"proxy": proxy, "time": time.time() - float(response['request_time'])})
            self.logger_200.info(f"stt: {response['status']} - rq_t: {response['request_time']} - proxy: {response['proxy']} - url: {url}")
            self._200 += 1
        elif response['status'] == 404:
            if self.proxy_use == True: self.q_put_proxy.put_nowait({"proxy": proxy, "time": time.time() - float(response['request_time'])})
            self.logger_200.info(f"stt: {response['status']} - rq_t: {response['request_time']} - proxy: {response['proxy']} - url: {url}")
            self._404 += 1
        elif any([response['status'] in ["asyncio.TimeoutError", "ErrConn", 500]]):
            if self.proxy_use == True: self.q_put_proxy.put_nowait({"proxy": proxy, "time": time.time() - float(response['request_time'])})
            self.logger_500.info(f"stt: {response['status']} - rq_t: {response['request_time']} - proxy: {response['proxy']} - url: {url}")
            self._500 += 1
        else:
            self.logger_500.info(f"stt: {response['status']} - rq_t: {response['request_time']} - proxy: {response['proxy']} - url: {url}")
            if self.proxy_use == True: self.q_die_proxy.put_nowait({"proxy": proxy, "time": time.time() - float(response['request_time'])})
            self._500 += 1
        await self.q_task_running.get()
        self.total_rq_time += float(response['request_time'])

        # Retry
        if response['status'] not in [200, 404]:
            self.logger_retry.info(f"retry - status: {response['status']} - url: {url} - proxy: {proxy}")
            # self.add_queue(response['url'], callback=callback, cb_kwargs=cb_kwargs)
            await self.single_request(response['url'], type="html", method="GET", payload=None, headers=None, callback=callback, cb_kwargs=cb_kwargs)
            return "retry"
        
        try:        
            # Callback
            if cb_kwargs: response.update(cb_kwargs)
            if callback != None: 
                await callback(response)
            return response
        except:
            self.logger_500.exception(f"handle_response exception: {url}")
            return traceback.format_exc()
class b_crawl_headless:
    '''
    Tương tự như b_crawl nhưng sử dụng playwright để request headless browser
    '''
    def __init__ (
        self, 
        number=5, 
        second=1, 
        time_out=60, 
        max_rq_tasks=17, 
        proxy_use=False, 
        proxy_wait=10, 
        proxy_reanimate=600, 
        same_session=False, 
        log_folder='', 
        headless_browsers=False, 
        keep_headless=False,
        log_set="INFO",
        ):
        self.logger = b_log(f'{log_folder}b_crawl')
        self.logger_200 = b_log(f'{log_folder}b_crawl_200', stream=False)    # log lưu request thành công, không show ra màn hình
        self.logger_500 = b_log(f'{log_folder}b_crawl_500', stream=False)    # log lưu request không thành công, không show ra màn hình
        self.log_set = log_set    # cấp độ log, DEBUG sẽ print các request ra màn hình
        self.same_session = same_session    # dùng async_request_session để gửi chung 1 session, nếu False thì sẽ dùng async_request_all mỗi lần gửi request sẽ tạo 1 session mới
        self.number = number
        self.second = second
        self.time_out = time_out
        self.max_rq_tasks = max_rq_tasks
        self.stop_threads = False # khi crawl xong sẽ đổi thành True để stop hết các thread
        self._200 = 0   # count status 200
        self._404 = 0   # count status 404
        self._500 = 0   # count status 500
        self.headless_browsers = headless_browsers # True: sử dụng giả lập browser để request các trang sử dụng js ...
        self.keep_headless = keep_headless      # True: giữ lại session không close để gửi sang callback sử dụng tiếp (click, ...)
        self.proxy_use = proxy_use              # True nếu sử dụng proxy
        self.proxy_wait = proxy_wait            # thời gian chờ giữa 2 lần request của cùng 1 proxy
        self.proxy_reanimate = proxy_reanimate  # thờI gian chờ phục hồi của proxy die
        self.q_proxy = asyncio.Queue()          # queue chính là các proxy ok get ra xài luôn
        self.q_put_proxy = asyncio.Queue()      # các proxy vừa dùng xong sẽ được đưa vào queue này, để tạo task sleep proxy_wait giây, để proxy có thể sử dụng lại, sau đó sẽ được đưa lại vào queue q_proxy
        self.q_die_proxy = asyncio.Queue()      # các proxy die sẽ được đưa vào queue này, để tạo task sleep proxy_reanimate giây, để proxy có thể sử dụng lại, sau đó sẽ được đưa lại vào queue q_proxy
        self.q_task_waitting = asyncio.Queue()
        self.q_task_running = asyncio.Queue()
    
    # Thread quản lý các proxy queue, tạo các task chờ phục hồi proxy
    async def task_handle_proxy(self):
        if self.proxy_use != True:
            return
        proxy_list = ROTATING_PROXY_LIST
        self.total_proxy = len(proxy_list)
        random.shuffle(proxy_list)
        for proxy in proxy_list:
            self.q_proxy.put_nowait({
                "proxy": proxy,
                "time": time.time()
            })
        self.logger.info(f"total proxy: {self.q_proxy.qsize()}")
        while True:
            if self.q_put_proxy.qsize() > 0:
                for i in range(self.q_put_proxy.qsize()):
                    proxy_data = await self.get_proxy(self.q_put_proxy)
                    if time.time() - proxy_data['time'] > self.proxy_wait:
                        proxy_data.update({'time': time.time()})
                        self.q_proxy.put_nowait(proxy_data)
                    else:
                        self.q_put_proxy.put_nowait(proxy_data)
            if self.q_die_proxy.qsize() > 0:
                for i in range(self.q_die_proxy.qsize()):
                    proxy_data = await self.get_proxy(self.q_die_proxy)
                    if time.time() - proxy_data['time'] > self.proxy_reanimate:
                        proxy_data.update({'time': time.time()})
                        self.q_proxy.put_nowait(proxy_data)
                    else:
                        self.q_die_proxy.put_nowait(proxy_data)
            await asyncio.sleep(0.01)
    
    # Get proxy từ queue, chưa có sẽ await sleep để async vẫn hoạt động
    async def get_proxy(self, queue_):
        proxy_data = await queue_.get()
        queue_.task_done()
        return proxy_data
    
    # Thread monitor chung, để đếm số request thành công, không thành công, proxy die... và lưu lại log
    async def async_task_monitor(self):
        t0 = time.time()
        while True:
            await asyncio.sleep(5)
            if self.proxy_use == False:
                self.logger.info(f"crawl: {(self._200 + self._404 + self._500) / (time.time() - t0):.2f}/s - sucess: {self._200 / (time.time() - t0):.2f}/s - 200: {self._200} - 404: {self._404} - 500: {self._500} - t_run: {self.q_task_running.qsize()} - t_wait: {self.q_task_waitting.qsize()}")
            else:
                self.logger.info(f"crawl: {(self._200 + self._404 + self._500) / (time.time() - t0):.2f}/s - sucess: {self._200 / (time.time() - t0):.2f}/s - 200: {self._200} - 404: {self._404} - 500: {self._500} - proxy_ok: {self.total_proxy - self.q_die_proxy.qsize()} - proxy_die: {self.q_die_proxy.qsize()}  - t_run: {self.q_task_running.qsize()} - t_wait: {self.q_task_waitting.qsize()}")
    # Thêm url vào queue để crawl
    def add_queue(self, url, callback=None, cb_kwargs=None):
        self.q_task_waitting.put_nowait([url, callback, cb_kwargs])
        
    # Thread quản lý crawl, tạo các task crawl
    async def create_task_queue(self):
        # Init rq_
        playwright_rq.kill_chrome()
        self.playwright = await async_playwright().start()
        if self.proxy_use == True: # sử dụng proxy nên mỗi request sẽ tạo context riêng để gán proxy
            self.browser = await self.playwright.chromium.launch(headless=True, proxy={"server": "per-context"})
            context = None
        else: # k sử dụng proxy nên dùng chung context, chỉ tạo các page mới để crawl
            self.browser = await self.playwright.chromium.launch(headless=True)
            ua = user_agent_rd()
            context = await self.browser.new_context(user_agent=ua)
            context.set_default_timeout(self.time_out * 1000)
        self.rq_ = playwright_rq(self.browser, context, self.keep_headless, self.number, self.second, self.time_out, self.max_rq_tasks)
        
        while True:
            # Check nếu tổng số task running đang lớn hơn max_rq_tasks thì bỏ qua không add thêm task
            if self.q_task_running.qsize() > self.max_rq_tasks:
                await asyncio.sleep(0.001)
                continue
            task_get = await self.q_task_waitting.get()
            url, callback, cb_kwargs = task_get[0], task_get[1], task_get[2]
            
            # Create request task
            asyncio.create_task(self.rq_final(url, callback=callback, cb_kwargs=cb_kwargs))
            self.q_task_running.put_nowait('')
            
            await asyncio.sleep(0.001)

        # đóng browser, stop playwright, kill chrome (có thể k cần thiết và gặp lỗi với những máy sử dụng chrome - chỗ này chưa tối ưu)
        await browser.close()
        await playwright.stop()
        playwright_rq.kill_chrome()
    
    # Task chờ để đợi các task crawl, xác định thời điểm mà task running và task waiting đều = 0 là không còn task nào để thực hiện, 
    # sẽ kill các task để finish. Thực ra nếu đúng thì phải đếm chính xác các task đang active, nếu tổng số bằng số task chính (hiện tại là 4 task
    # bao gồm main (wait chạy trong main), monitor, proxy, create_task_queue) thì tức là không còn task request hay parse, insert db nào đang hoạt động và 
    # có thể finish
    async def wait(self):
        rq_task = asyncio.create_task(self.create_task_queue())
        monitor_task = asyncio.create_task(self.async_task_monitor())
        proxy_task = asyncio.create_task(self.task_handle_proxy())
        tasks = [rq_task, monitor_task, proxy_task]
        # await asyncio.sleep(3)  # wait for initial

        # Stop
        t0 = time.time()  
        while True:
            # Stop thread
            time_check = time.time() - t0
            if time_check < 30:
                # Stop qua 30s đầu để trong queue bắt đầu có data, tránh trường hợp vừa chạy thì 2 queue trên đều = 0
                await asyncio.sleep(0.01)
                continue
            if self.q_task_waitting.qsize() == 0 and self.q_task_running.qsize() == 0:
                count_active_tasks = len(asyncio.all_tasks())
                if count_active_tasks < 6: # thực tế các task đang chạy chỉ còn các task quản lý chính, nên có thể kết thúc qui trình
                    for task in asyncio.all_tasks():
                        print(task)
                    break
            await asyncio.sleep(0.01)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await self.browser.close()
        await self.playwright.stop()
        playwright_rq.kill_chrome()
        self.logger.info("Thread wait stop")
    
    async def single_playwright(self, url, headers=None, callback=None, cb_kwargs=None):
        while True:
            if self.q_task_running.qsize() > self.max_rq_tasks:
                await asyncio.sleep(0.001)
                continue
            self.q_task_running.put_nowait('')

            # Set proxy
            if self.proxy_use == True: 
                proxy_data = await self.get_proxy(self.q_proxy)
                proxy = proxy_data['proxy']
                response = await self.rq_.playwright_rq_multi_session(url, proxy)
            else: 
                response = await self.rq_.playwright_rq_session(url, proxy)

            return await self.handle_response(url, response, proxy, callback=callback, cb_kwargs=cb_kwargs)
    # Hàm request chính, xử lý các vấn đề liên quan đến request như proxy, status ...
    async def rq_final(self, url, type_="html", callback=None, cb_kwargs=None):
        try:
            # Set proxy
            if self.proxy_use == True: 
                proxy_data = await self.get_proxy(self.q_proxy)
                proxy = proxy_data['proxy']
            else: proxy = None
            
            # Request
            if self.proxy_use == True: # sử dụng playwright_rq_multi_session để mỗi context có thể gán proxy
                response = await self.rq_.playwright_rq_multi_session(url, proxy)
            else:
                response = await self.rq_.playwright_rq_session(url, proxy)

            return await self.handle_response(url, response, proxy, callback=callback, cb_kwargs=cb_kwargs)
        except:
            self.logger_500.exception(f"rq_final url exception: {url}")
            await self.q_task_running.get()
            return traceback.format_exc()
    
    # Hàm xử lý các response, tuỳ theo response mà xử lý proxy đưa vào các queue tương ứng
    async def handle_response(self, url, response, proxy, callback=None, cb_kwargs=None):
        if self.log_set == "DEBUG":
            print(f"stt: {response['status']} - rq_t: {response['request_time']} - proxy: {response['proxy']} - url: {url}")

        # Count status & handle proxy
        if response['status'] == 200:
            if self.proxy_use == True: self.q_put_proxy.put_nowait({"proxy": proxy, "time": time.time()})
            self.logger_200.info(f"stt: {response['status']} - rq_t: {response['request_time']} - proxy: {response['proxy']} - url: {url}")
            self._200 += 1
        elif response['status'] == 404:
            if self.proxy_use == True: self.q_put_proxy.put_nowait({"proxy": proxy, "time": time.time()})
            self.logger_200.info(f"stt: {response['status']} - rq_t: {response['request_time']} - proxy: {response['proxy']} - url: {url}")
            self._404 += 1
        elif any([response['status'] in ["asyncio.TimeoutError", "ErrConn"]]):
            if self.proxy_use == True: self.q_put_proxy.put_nowait({"proxy": proxy, "time": time.time()})
            self.logger_500.info(f"stt: {response['status']} - rq_t: {response['request_time']} - proxy: {response['proxy']} - url: {url}")
            self._500 += 1
        else:
            self.logger_500.info(f"stt: {response['status']} - rq_t: {response['request_time']} - proxy: {response['proxy']} - url: {url}")
            if self.proxy_use == True: self.q_die_proxy.put_nowait({"proxy": proxy, "time": time.time()})
            self._500 += 1
        await self.q_task_running.get()
        
        try:        
            # Callback
            if cb_kwargs: response.update(cb_kwargs)
            if callback != None: 
                await callback(response)
            return response
        except:
            self.logger_500.exception(f"handle_response exception: {url}")
            return traceback.format_exc()
            
#
# Async
#
class async_rq:
    '''
    Class request gộp chung khởi tạo session, rate limit, timeout
    async_request_session(): hàm này chạy chung các request trên 1 session, về lý thuyết là nhẹ hơn và nhanh hơn
    async_request_all(): hàm này chạy riêng các request trên các session khác nhau, trong trường hợp request tới search engine thì có thể dùng chung session sẽ bị detect cookies hoặc gì đó nên đã dùng riêng session và thấy ok nên cứ dùng
    '''
    # Khởi tạo rate limit và session
    def __init__ (self, number=50, second=1, time_out=60, max_rq_tasks=17):
        self.rate_limit_ = self.rate_limit_conf(number, second)
        self.time_out = time_out
        self.session = self.async_request_init(self.time_out, max_rq_tasks)
    # class rate limit, sử dụng với function rate_limit, đảm bảo giới hạn trong 1 khoảng thời gian chỉ có 1 số lượng request nhất định. Vd shopify giới hạn 4rq/s.
    # thuật toán cơ bản là chia số giây cho số rq, vd 10rq/3s -> 3/10 = 0.3, tương ứng là mỗi 0.3s sẽ có 1 rq. Hàm sẽ loop thời gian và so sánh nếu thời gian > 0.3 thì sẽ trả ra 1 token, có 1 token thì request sẽ được thực hiện sau đó set lại token = 0 và loop tiếp tục chạy.
    class rate_limit_conf:
        def __init__ (self, number, second):
            self.updated_at = time.monotonic()
            self.NUMBER = number
            self.SECOND = second
            self.TOKEN = 0
    async def rate_limit(self):
        def add_token():
            if time.monotonic() - self.rate_limit_.updated_at > (self.rate_limit_.SECOND / self.rate_limit_.NUMBER):
                self.rate_limit_.TOKEN = 1
        t0 = time.time()
        while self.rate_limit_.TOKEN < 1:
            add_token()
            await asyncio.sleep(0.001)
        self.rate_limit_.updated_at = time.monotonic()
        self.rate_limit_.TOKEN = 0
    # Khởi tạo session
    def async_request_init(self, time_out, max_rq_tasks):
        timeout = aiohttp.ClientTimeout(total=time_out)
        connector = aiohttp.TCPConnector(limit=max_rq_tasks)
        session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return session
    async def async_request_close(self):
        await self.session.close()
    # request dùng chung sesion
    async def async_request_session(self, url, type, payload=None, proxy=None, auth_info=None, headers=None):
        # await self.rate_limit()
        t0 = time.time()
        if headers == None: headers = {'user-agent': user_agent_rd()}
        else: headers.update({'user-agent': user_agent_rd()})
        http_proxy = "http://" + proxy if proxy != None else None
        
        # Test proxy
        proxy_test = ''
        # test_url = "https://ident.me"
        # async with self.session.get(test_url, headers=headers, proxy=http_proxy) as response:
        #     proxy_test = await response.text()

        try:
            async with self.session.get(url, headers=headers, proxy=http_proxy) as response:
                if type == "JSON": html = await response.json()
                else: html = await response.text()
                    
            status= response.status
            headers = response.headers
            request_info = response.request_info
            
                    
        except aiohttp.ClientResponseError as ex:
            status = ex.status
            headers = request_info = html = ''
        except aiohttp.ClientConnectionError:
            status = 'ErrConn'
            headers = request_info = html = ''
        except asyncio.TimeoutError:
            status = 'asyncio.TimeoutError'
            headers = request_info = html = ''
        except:
            status = str(traceback.format_exc())
            headers = request_info = html = ''
        
        return {
            'url': url,
            'status': status,
            "headers": headers,
            "request_info": request_info,
            "html": html,
            "proxy_test": proxy_test,
            "proxy": proxy,
            "request_time": f"{time.time() - t0:.2f}"
        }
    # reqeust dùng session riêng biệt
    async def async_request_all(self, url, type, method="GET", payload=None, proxy=None, headers=None):
        # await self.rate_limit()
        t0 = time.time()
        timeout = aiohttp.ClientTimeout(total=self.time_out)
        if proxy != None: http_proxy = "http://" + proxy 
        else: http_proxy = None

        ua = user_agent_rd()
        if headers == None: headers = {
            'user-agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
            'Accept-Language': 'en-US,en;q=0.5', 
            'Accept-Encoding': 'gzip, deflate'
        }
        else: headers.update({
            'user-agent': ua
        })

        try:
            proxy_test = ''
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if method == "GET":
                    async with session.get(url, headers=headers, proxy=http_proxy, verify_ssl=False) as response:
                        if type == "JSON": html = await response.json()
                        else: html = await response.text()
                elif method == "POST": 
                    if type == "JSON":
                        async with session.post(url, headers=headers, json=payload, proxy=http_proxy) as response:
                            html = await response.json()
                    else: 
                        async with session.post(url, headers=headers, data=payload, proxy=http_proxy) as response:
                            html = await response.text()
            
            status= response.status
            headers = response.headers
            request_info = response.request_info

        except aiohttp.ClientResponseError as ex:
            status = ex.status
            headers = request_info = html = ''
        except aiohttp.ClientConnectionError:
            print(f"er: {traceback.format_exc()}")
            status = f'ErrConn'
            headers = request_info = html = ''
        except asyncio.TimeoutError:
            status = 'asyncio.TimeoutError'
            headers = request_info = html = ''
        except:
            status = str(traceback.format_exc())
            headers = request_info = html = ''

        return {
            'url': url,
            'status': status,
            "headers": headers,
            "request_info": request_info,
            "html": html,
            "proxy_test": proxy_test,
            "proxy": proxy,
            "request_time": f"{time.time() - t0:.2f}"
        }
def user_agent_rd():
    'random lấy user agent'
    random.shuffle(mobile_user_agents)
    ua = mobile_user_agents[0]
    return ua
class playwright_rq:
    def __init__ (self, browser, context=None, keep_headless=False, number=5, second=1, time_out=60, max_rq_tasks=17):
        self.rate_limit_ = self.rate_limit_conf(number, second)
        self.time_out = time_out
        self.browser = browser
        self.keep_headless = keep_headless
        if context != None:
            self.context = context
    class rate_limit_conf:
        def __init__ (self, number, second):
            self.updated_at = time.monotonic()
            self.NUMBER = number
            self.SECOND = second
            self.TOKEN = 0
    async def rate_limit(self):
        def add_token():
            if time.monotonic() - self.rate_limit_.updated_at > (self.rate_limit_.SECOND / self.rate_limit_.NUMBER):
                self.rate_limit_.TOKEN = 1
        t0 = time.time()
        while self.rate_limit_.TOKEN < 1:
            add_token()
            await asyncio.sleep(0.001)
        self.rate_limit_.updated_at = time.monotonic()
        self.rate_limit_.TOKEN = 0
    def convert_proxy(self, proxy):
        if "@" in proxy:
            user_pass = proxy.split("@")[0]
            server_ = proxy.split("@")[1]
            user = user_pass.split(":")[0]
            pass_ = user_pass.split(":")[1]
            # pxuser:Ok&*2jnghNa78@51.81.196.97:3128
            proxy_converted = {
                "server": f"http://{server_}",
                "username": user,
                "password": pass_
            }
        else:
            proxy_converted = {
                "server": f"http://{proxy}",
            }
        return proxy_converted
    def kill_chrome():
        import os
        os. system("taskkill /f /im chrome.exe")
    async def playwright_rq_multi_session(self, url, proxy):
        await self.rate_limit()
        t0 = time.time()

        try:
            # config
            ua = user_agent_rd()
            proxy_ = self.convert_proxy(proxy)

            context = await self.browser.new_context(
                user_agent=ua,
                proxy=proxy_
            )
            context.set_default_timeout(self.time_out * 1000)
            page = await context.new_page()
            page.set_default_navigation_timeout(self.time_out * 1000)
            respone = await page.goto(url)
            status = respone.status
            await page.wait_for_load_state("networkidle")
            html = await page.content()
            if self.keep_headless == False:
                await page.close()
                await context.close()

        except Exception as e:
            # print(f"playwright_rq_multi_session error: {e}")
            status = 500
            html = ''
            await page.close()
            await context.close()

        if self.keep_headless == False:
            return {
                'url': url,
                'status': status,
                "html": html,
                "proxy": proxy,
                "request_time": f"{time.time() - t0:.2f}",
            }
        else:
            return {
                'url': url,
                'status': status,
                "html": html,
                "proxy": proxy,
                "request_time": f"{time.time() - t0:.2f}",
                "page": page,
                "context": context,
            }
    async def playwright_rq_session(self, url, proxy):
        await self.rate_limit()
        t0 = time.time()

        try:
            # config
            page = await self.context.new_page()
            respone = await page.goto(url)
            status = respone.status
            await page.wait_for_load_state("networkidle")
            html = await page.content()
            if self.keep_headless == False:
                await page.close()

        except Exception as e:
            print(f"playwright_rq_session error: {e}")
            status = ""
            html = ''
            await page.close()
        if self.keep_headless == False:
            return {
                'url': url,
                'status': status,
                "html": html,
                "proxy": proxy,
                "request_time": f"{time.time() - t0:.2f}",
            }
        else:
            return {
                'url': url,
                'status': status,
                "html": html,
                "proxy": proxy,
                "request_time": f"{time.time() - t0:.2f}",
                "page": page,
            }
