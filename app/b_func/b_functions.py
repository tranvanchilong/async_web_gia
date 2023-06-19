import logging, os, time, json
from logging.handlers import RotatingFileHandler
import re
import json
import aiofiles 
import urllib.parse

def b_log(log_name, stream = True, log_set="INFO"):
    '''
    stream = Fale: không print ra màn hình nhưng vẫn lưu vào file log
    '''
    os.makedirs('./logs/') if not os.path.exists('./logs/') else True
    logger = logging.getLogger(log_name)

    hnd_all = RotatingFileHandler('./logs/' + log_name + ".log", maxBytes=10000000, backupCount=5, encoding='utf-8')
    # hnd_all.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s ''[in %(pathname)s:%(lineno)d]'))
    # hnd_all.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s ''[in %(filename)s:%(lineno)d]', datefmt='%Y%m%d %H:%M:%S'))
    hnd_all.setFormatter(logging.Formatter('%(asctime)s %(levelname)s[in %(filename)s:%(lineno)d]: %(message)s ', datefmt='%Y%m%d %H%M%S'))
    hnd_all.setLevel(logging.DEBUG)
    logger.addHandler(hnd_all)

    if stream == True:
        hnd_stream = logging.StreamHandler()
        hnd_stream.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s ''[in %(filename)s:%(lineno)d]', datefmt='%Y%m%d %H:%M:%S'))
        hnd_stream.setLevel(logging.DEBUG)
        logger.addHandler(hnd_stream)

    if log_set == "INFO":
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

    return logger
def chunks(list_, number):
    '''
    Chia list thành những list có size = number
    '''
    def chunks_(list_, number):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(list_), number):
            yield list_[i:i + number]
    return list(chunks_(list_, number))
def make_slug(name):
    # Tạo slug cho website từ title
    remove_special = re.sub('[^A-Za-z0-9. _-]+', '', name).replace(" ", "-").lower().strip()
    return remove_special
class b_write: # old version
    def __init__(self, filename):
        with open(filename, "w", encoding='utf-8') as outfile:
            pass
        self.file = open(filename, "ab+")
    def write(self, data):
        json.dump(data, self.file)
        print("writed")
    def close(self):
        self.file.close()
    def append_json(self, item):
        self.file.seek(0,2)
        if self.file.tell() == 0 :                         #Check if file is empty
            self.file.write(json.dumps([item]).encode('utf-8'))  #If empty, write an array
        else :
            self.file.seek(-1,2)           
            self.file.truncate()                           #Remove the last character, open the array
            self.file.write(' , '.encode('utf-8'))                #Write the separator
            self.file.write(json.dumps(item).encode('utf-8'))    #Dump the dictionary
            self.file.write(']'.encode('utf-8'))
class b_write_aiofiles:
    '''
    Class lưu data vào 1 file json hoặc text trong folder data. 
    Với dạng file json phải gọi close file sau khi crawl xong.
    '''
    def __init__(self, filename):
        os.makedirs('./data/') if not os.path.exists('./data/') else True
        filename = "./data/" + filename
        with open(filename, "w", encoding='utf-8') as outfile:
            if ".json" in filename:
                outfile.write("[")
            pass
        self.filename = filename
    async def write(self, data):
        async with aiofiles.open(self.filename, "a") as out:
            if type(data) != dict:
                await out.write(data)
                await out.write("\n")
                await out.flush()
            else:
                await out.write(json.dumps(data))
                await out.write(",")
                await out.flush()
                
    async def close(self):
        if ".json" in self.filename:
            async with aiofiles.open(self.filename, "ab+") as out:
                await out.seek(-1,2)           
                await out.truncate()                           #Remove the last character, open the array
                await out.write(']'.encode('utf-8'))                #Write the separator

class b_write_site_html:
    '''
    Class lưu html được crawl vào 1 folder chứa các file html của các url đã crawl.
    '''
    def __init__(self, domain):
        self.folder_ = f'./data/{domain}/'
        os.makedirs(self.folder_) if not os.path.exists(self.folder_) else True
    async def write_url_html(self, url, data):
        file_path = self.folder_ + urllib.parse.quote_plus(url) + ".html"
        async with aiofiles.open(file_path, "w", encoding='utf8') as out:
            await out.write(data)

async def write_url_html(folder_, url, data):
    # Ghi html ra file
    folder_ = f'./data/{folder_}/'
    os.makedirs(folder_) if not os.path.exists(folder_) else True
    file_path = folder_ + urllib.parse.quote_plus(url) + ".html"
    async with aiofiles.open(file_path, "w", encoding='utf8') as out:
        await out.write(data)