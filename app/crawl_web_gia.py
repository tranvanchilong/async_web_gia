import asyncio
import time
import b_func
from selectolax.parser import HTMLParser
import re
import requests
import traceback
import datetime

project_name = "async_web_gia"
MONGO_URI = "mongodb://adminmg:tM5Jngh9EbKu@139.162.28.246:27018/" #"mongodb://adminmg:tM5Jngh9EbKu@5.161.176.184:27018/"
MONGODB_DB = 'web_gia_com'
MONGODB_COLLECTION = "data"
db_client = b_func.MongoAsyncPipeline(MONGO_URI, MONGODB_DB, MONGODB_COLLECTION)
logger = b_func.b_log(project_name)

#
# Crawl
#
async def main():
    try:
        t0 = time.time()
        await db_client.check_connect()

        global rq_
        rq_ = b_func.b_crawl(
            time_out=30, 
            max_rq_tasks=100, 
            proxy_use=False, 
            proxy_wait=5, 
            proxy_reanimate=600, 
            log_set="INFO",
        )
        
        # Start
        list_input=[
        #GIá vànd
            {
            "father": "Biểu đồ giá vàng ",
            "path": "giavang",
            "name": "SJC 1 tháng",
            "name_path": "sjc-1-thang",
            "link": "https://giavang.org/trong-nuoc/",
            "parse_key": "section #bieu_do_sjc",
            "replace_key": ""
            },
            {
            "father": "Biểu đồ giá vàng ",
            "path": "giavang",
            "name": "SJC hôm nay",
            "name_path": "sjc-hom-nay",
            "link": "https://webgia.com/gia-vang/sjc/bieu-do-1-ngay.html",
            "parse_key": "#bieu_do_sjc",
            "replace_key": ""
            },
            {
            "father": "Biểu đồ giá vàng ",
            "path": "giavang",
            "name": "SJC 1 năm",
            "name_path": "sjc-1-nam",
            "link": "https://webgia.com/gia-vang/sjc/bieu-do-1-nam.html",
            "parse_key": "#bieu_do_sjc",
            "replace_key": ""
            },
            {
            "father": "Biểu đồ giá vàng ",
            "path": "giavang",
            "name": "Thế Giới",
            "name_path": "the-gioi",
            "link": "https://webgia.com/gia-vang/the-gioi/",
            "parse_key": "article.col-xs-12",
            "replace_key": ""
            },
            {
            "father": "Tổng hợp Giá vàng ",
            "path": "giavang",
            "name": "SJC trên Toàn Quốc",
            "name_path": "sjc-tren-toan-quoc",
            "link": "https://giavang.org/?123",
            "parse_key": ".table.table-striped",
            "replace_key": "td i"
            },
            {
            "father": "Giá vàng ",
            "path": "giavang",
            "name": "SJC",
            "name_path": "sjc",
            "link": "https://giavang.org/trong-nuoc/sjc/",  #"https://giavang.org/",
            "parse_key": ".table.table-striped",
            "replace_key": "td i"
            },
            {
            "father": "Giá vàng ",
            "path": "giavang",
            "name": "DOJI",
            "name_path": "doji",
            "link": "https://giavangvietnam.com/gia-vang-doji/",
            "parse_key": ".lastestGoldTable",
            "replace_key": "tr td"
            },
            {
            "father": "Giá vàng ",
            "path": "giavang",
            "name": "PNJ",
            "name_path": "pnj",
            "link": "https://giavang.org/trong-nuoc/pnj/", #"https://giavang.org/?abc",
            "parse_key": "table.table-hover",
            "replace_key": "td i"   
            },
            {
            "father": "Giá vàng ",
            "path": "giavang",
            "name": "Phú Quý",
            "name_path": "phu-quy",
            "link": "https://giavang.org/trong-nuoc/phu-quy/",
            "parse_key": "table.table-striped",
            "replace_key": "td i"
            },
            {
            "father": "Giá vàng ",
            "path": "giavang",
            "name": "Bảo Tín Minh Châu",
            "name_path": "bao-tin-minh-chau",
            "link": "https://giavang.org/trong-nuoc/bao-tin-minh-chau/",
            "parse_key": "table.table-striped",
            "replace_key": "td i"
            },
            {
            "father": "Giá vàng ",
            "path": "giavang",
            "name": "Mi Hồng",
            "name_path": "mi-hong",
            "link": "https://giavang.org/trong-nuoc/mi-hong/",   #"https://giavangvietnam.com/gia-vang-mi-hong/",
            "parse_key": "table.table-striped",        #".lastestGoldTable",
            "replace_key": "td i"
            },
            {
            "father": "Giá vàng ",
            "path": "giavang",
            "name": "Thế Giới",
            "name_path": "the-gioi",
            "link": "https://giavang.org/the-gioi/",
            "parse_key": ".row.border-content",
            "replace_key": ""
            },

        #Tỉ giá ngân hàng
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "ABBank",
            "name_path": "abbank",
            "link": "https://chogia.vn/ty-gia/abbank/",
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "ACB",
            "name_path": "acb",
            "link": "https://chogia.vn/ty-gia/acb/", #"https://tygiadola.net/nganhang/acb",
            "parse_key": "table.uk-table-striped",
            "replace_key": "th.text-primary"
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "Agribank",
            "name_path": "agribank",
            "link": "https://www.agribank.com.vn/vn/ty-gia",
            "parse_key": "table.table-striped",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "Bản Việt",
            "name_path": "ban-viet",
            "link": "https://thebank.vn/cong-cu/tinh-ty-gia-ngoai-te/ty-gia-vietcapitalbank.html",
            "parse_key": "table.load-more-wrap",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "Bảo Việt",
            "name_path": "bao-viet",
            "link": "https://thebank.vn/cong-cu/tinh-ty-gia-ngoai-te/ty-gia-baovietbank.html",
            "parse_key": "table.load-more-wrap",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "BIDV",
            "name_path": "bidv",
            "link": "https://ngan-hang.com/ty-gia-ngan-hang-bidv",
            "parse_key": "table.table-exchangeRate",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "CBBank",   #sửa thành CBBank
            "name_path": "cbbank",
            "link": "https://chogia.vn/ty-gia/cbbank/",
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "Đông Á",
            "name_path": "dong-a",
            "link": "https://ngan-hang.com/ty-gia-ngan-hang-donga",
            "parse_key": "table.table-exchangeRate",
            "replace_key": "td i"
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "EximBank",
            "name_path": "eximbank",
            "link": "https://eximbank.com.vn/tygiangoaitevagiavang",
            "parse_key": ".table-responsive",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "GPBank",
            "name_path": "gpbank",
            "link": "https://thebank.vn/cong-cu/tinh-ty-gia-ngoai-te/ty-gia-gpbank.html",
            "parse_key": "table.table-exchange",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "HDBank",
            "name_path": "hdbank",
            "link": "https://chogia.vn/ty-gia/hdbank/",
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "Hong Leong",
            "name_path": "hong-leong",
            "link": "https://chogia.vn/ty-gia/hlbank/",
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "HSBC",
            "name_path": "hsbc",
            "link": "https://www.hsbc.com.vn/foreign-exchange/rate/",
            "parse_key": "#content_main_basicTable_2",
            "replace_key": "table caption"
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "Kiên Long",
            "name_path": "kien-long",
            "link": "https://kienlongbank.com/ty-gia",
            "parse_key": "table.table",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "Indovina Bank",
            "name_path": "indovina-bank",
            "link": "https://chogia.vn/ty-gia/indovinabank/",
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "Liên Việt",
            "name_path": "lien-viet",
            "link": "https://lienvietpostbank.com.vn/ti-gia/",
            "parse_key": ".wrap-content-search-big table",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "Maritime Bank",  #đổi name thành Maritime Bank
            "name_path": "mariatime-bank",
            "link": "https://chogia.vn/ty-gia/msb/", 
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "MB",
            "name_path": "mbbank",
            "link": "https://tygiahomnay.com/ngan-hang-quan-doi",  #số hơi khác web giá nhưng k đáng kể
            "parse_key": "table.table-bordered",
            "replace_key": "td i"
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "Nam Á Bank",
            "name_path": "nam-a-bank",
            "link": "https://www.namabank.com.vn/ty-gia",
            "parse_key": "div.table",
            "replace_key": "td i"
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "NCB",
            "name_path": "ncb",
            "link": "https://chogia.vn/ty-gia/ncb/",
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "OCB",
            "name_path": "ocb",
            "link": "https://chogia.vn/ty-gia/ocb/",
            "parse_key": "table.ngoai-te",
            "replace_key": ""
            },
            #     {
            # "father": "Tỉ giá ngoại tệ ",
            # "path": "tygia",
            # "name": "OceanBank",
            # "link": "https://oceanbank.vn/ty-gia-ngoai-te.html",
            # "parse_key": "table.tb_tg",
            # "replace_key": ""
            # },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "PGBank",
            "name_path": "pgbank",
            "link": "https://chogia.vn/ty-gia/pgbank/",
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "PublicBank",
            "name_path": "public-bank",
            "link": "https://topnganhang.net/ty-gia/public-bank-50",
            "parse_key": "table.table-striped",
            "replace_key": "td.text-right"
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "PVcomBank",
            "name_path": "pvcombank",
            "link": "https://chogia.vn/ty-gia/pvcombank/",
            "parse_key": "table.uk-table-striped",
            "replace_key": "td.text-right"
            },
            {
            "father": "Tỉ giá ngoại tệ ", #tat proxy
            "path": "tygia",
            "name": "Sacombank",
            "name_path": "sacombank",
            "link": "https://chogia.vn/ty-gia/sacombank/", #"https://www.sacombank.com.vn/company/Pages/ty-gia.aspx",
            "parse_key": "table.uk-table-striped",
            "replace_key": "td i"
            },


            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "SCB",
            "name_path": "scb",
            "link": "https://chogia.vn/ty-gia/scb/",
            "parse_key": "table.uk-table-striped",
            "replace_key": "td i"
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "SeABank",
            "name_path": "seabank",
            "link": "https://chogia.vn/ty-gia/seabank/",
            "parse_key": "table.uk-table-striped",
            "replace_key": "td i"
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "SHB",
            "name_path": "shb",
            "link": "https://www.shb.com.vn/tygia/ty-gia-hoi-doai/",
            "parse_key": "table.table-striped",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "Techcombank",
            "name_path": "techcombank",
            "link": "https://chogia.vn/ty-gia/techcombank/",
            "parse_key": "table.ngoai-te",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "TPBank",
            "name_path": "tpbank",
            "link": "https://chogia.vn/ty-gia/tpb/",
            "parse_key": "table.ngoai-te",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "UOB",
            "name_path": "uob",
            "link": "https://chogia.vn/ty-gia/uob/",
            "parse_key": "table.ngoai-te",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "VIB",
            "name_path": "vib",
            "link": "https://chogia.vn/ty-gia/vib/",
            "parse_key": "table.uk-table-striped",
            "replace_key": "th.text-right"
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "VietABank",
            "name_path": "viet-a-bank",
            "link": "https://vietabank.com.vn/tien-ich/ty-gia-ngoai-te.html",
            "parse_key": "table.table-bank",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "Việt Bank",
            "name_path": "viet-bank",
            "link": "https://thebank.vn/cong-cu/tinh-ty-gia-ngoai-te/ty-gia-vietbank.html",    #số khác web giá
            "parse_key": "table.table-exchange",
            "replace_key": ""
            },
              {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "Viet Capital Bank",
            "name_path": "viet-capital-bank",
            "link": "https://chogia.vn/ty-gia/vietcapitalbank/",
            "parse_key": "table.ngoai-te",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "Vietcombank",
            "name_path": "vietcombank",
            "link": "https://chogia.vn/ty-gia/vietcombank/",
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "VietinBank",
            "name_path": "viettinbank",
            "link": "https://chogia.vn/ty-gia/vietinbank/", #"https://www.vietinbank.vn/web/home/vn/ty-gia/",
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "VPBank",
            "name_path": "vpbank",
            "link": "https://webgia.com/ty-gia/vpbank/",
            "parse_key": "table.table.table-exchanges",
            "replace_key": "td i"
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "VRBank",
            "name_path": "vrbank",
            "link": "https://chogia.vn/ty-gia/vrbank/",
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },

        # Ngoại tệ
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "AUD",
            "name_path": "aud",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-do-la-uc-aud.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "CAD",
            "name_path": "cad",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-do-canada-cad.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "CHF",
            "name_path": "chf",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-france-thuy-si-chf.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "CNY",
            "name_path": "cny",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-nhan-dan-te-cny.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "DKK",
            "name_path": "dkk",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-krone-dan-mach-dkk.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            # {
            # "father": "Tỉ giá ",
            # "path": "ngoaite",
            # "name": "CAD",
            # "link": "https://thebank.vn/cong-cu/tinh-ty-gia-ngoai-te/cad.html",
            # "parse_key": "table.table-exchange",
            # "replace_key": ""
            # },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "EUR",
            "name_path": "eur",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-euro-eur.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "GBP",
            "name_path": "gbp",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-bang-anh-gbp.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "HKD",
            "name_path": "hkd",
            "link": "https://thebank.vn/cong-cu/tinh-ty-gia-ngoai-te/hkd.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "IDR",
            "name_path": "idr",
            "link": "https://webgia.com/ngoai-te/idr/",
            "parse_key": "table.table-currencies",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "INR",
            "name_path": "inr",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-rupi-an-do-inr.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "KWD",
            "name_path": "kwd",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-kuwaiti-dinar-kwd.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "LAK",
            "name_path": "lak",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-kip-lao-lak.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "MYR",
            "name_path": "myr",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-ringgit-ma-lay-myr.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "NOK",
            "name_path": "nok",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-krone-na-uy-nok.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "NZD",
            "name_path": "nzd",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-do-new-zealand-nzd.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "PHP",
            "name_path": "php",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-peso-philippine-php.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "RUB",
            "name_path": "rub",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-rup-nga-rub.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "SAR",
            "name_path": "sar",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-saudi-rial-sar.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "SEK",
            "name_path": "sek",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-krone-thuy-dien-sek.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "SGD",
            "name_path": "sgd",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-do-singapore-sgd.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "THB",
            "name_path": "thb",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-bat-thai-lan-thb.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "TWD",
            "name_path": "twd",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-do-dai-loan-twd.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
             {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "USD",
            "name_path": "usd",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-do-la-my-usd.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
             {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "ZAR",
            "name_path": "zar",
            "link": "https://webgia.com/ngoai-te/zar/",   #web thiếu JPY
            "parse_key": "table.table-currencies",
            "replace_key": ""
            },
             {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "JPY",
            "name_path": "jpy",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-yen-nhat-jpy.html",   #web thiếu JPY
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
              {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "HKD",
            "name_path": "hkd",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-do-hongkong-hkd.html",   #web thiếu HKD
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
               {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "KRW",
            "name_path": "krw",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-won-han-quoc-krw.html",   #web thiếu KRW
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
                  {
            "father": "Tỉ giá ",
            "path": "ngoaite",
            "name": "KHR",
            "name_path": "khr",
            "link": "https://blogtygia.com/chuyen-doi-tien-te/ty-gia-ngoai-te-riel-campuchia-khr.html",   #web thiếu KHR
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },

        #lãi suất
            {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "Bắc Á Bank",
            "name_path": "bac-a-bank", 
            "link": "https://taichinh24h.com.vn/lai-suat/bacabank/",      #wed chưa có link
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },
            {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "ABBank",
            "name_path": "abbank",
            "link": "https://www.abbank.vn/thong-tin/lai-suat-tiet-kiem-vnd.html",
            "parse_key": "table",
            "replace_key": ""
            },
            {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "Agribank",
            "name_path": "agribank",
            "link": "https://www.agribank.com.vn/vn/lai-suat",
            "parse_key": "table.table-striped",
            "replace_key": ""
            },
            {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "Bảo Việt",
            "name_path": "bao-viet",
            "link": "https://banker.vn/baoviet-bank-tang-lai-suat-huy-dong-tai-nhieu-ky-han",  #2 bảng mới lấy 1
            "parse_key": "table.__MASTERCMS_TABLE_DATA",
            "replace_key": ""
            },
            {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "BIDV",
            "name_path": "bidv",
            "link": "https://onehousing.vn/thong-tin-va-doi-song/cap-nhat-lai-suat-ngan-hang-bidv-moi-nhat",
            "parse_key": "table",
            "replace_key": ""
            },
            {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "CBBank",
            "name_path": "cbbank",
            "link": "https://chogia.vn/lai-suat/cbbank/", #"https://www.cbbank.vn/Pages/InterestRate.aspx",
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },
            {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "Đông Á",
            "name_path": "dong-a",
            "link": "https://topi.vn/lai-suat-ngan-hang-dong-a.html",
            "parse_key": "table",
            "replace_key": ""
            },
       
            {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "Hong Leong Bank",
            "name_path": "hong-leong-bank",
            "link": "https://www.hlbank.com.vn/vi/help-and-support/interest-rates/priority-banking-fixed-deposits.html",
            "parse_key": ".bannerparsys",
            "replace_key": ""
            },
            {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "Indovina Bank",
            "name_path": "indovina-bank",
            "link": "https://www.indovinabank.com.vn/vi/interest-rate",
            "parse_key": ".content-bp",
            "replace_key": ""
            },
            {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "Kiên Long Bank",
            "name_path": "kien-long-bank",
            "link": "https://laisuat.kienlongbank.com/lai-suat-ca-nhan",
            "parse_key": "table.table-responsive",
            "replace_key": ""
            },
            {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "MSB",
            "name_path": "msb",
            "link": "https://www.msb.com.vn/vi/w/ca-nhan/tiet-kiem/tiet-kiem-lai-suat-cao-nhat",
            "parse_key": "div.section-content table.table",
            "replace_key": ""
            },
            {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "MB Bank",
            "name_path": "mb-bank",
            "link": "https://www.tcqtkd.edu.vn/lai-suat-mb-bank/",
            "parse_key": "table",
            "replace_key": ""
            },
               {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "Nam Á Bank",
            "name_path": "nam-a-bank",
            "link": "https://www.tcqtkd.edu.vn/lai-suat-nam-a-bank/",
            "parse_key": "table",
            "replace_key": "td i"
            },
                {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "NCB",
            "name_path": "ncb",
            "link": "https://topi.vn/bang-lai-suat-ngan-hang-ncb.html",
            "parse_key": "table",
            "replace_key": ""
            },
                 {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "OCB",
            "name_path": "ocb",
            "link": "https://topi.vn/lai-suat-ngan-hang-ocb.html",
            "parse_key": "table",
            "replace_key": ""
            },
            {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "OceanBank",
            "name_path": "oceanbank",
            "link": "http://oceanbank.vn/lai-suat/19/tiet-kiem-thuong.html",
            "parse_key": "table.tb_lstk",
            "replace_key": ""
            },
             {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "PG Bank",           #stalette thiếu link
            "name_path": "pgbank",
            "link": "https://www.tcqtkd.edu.vn/lai-suat-ngan-hang-pg-bank/",
            "parse_key": "table",
            "replace_key": ""
            },
            {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "Publicbank",
            "name_path": "publicbank",
            "link": "https://thebank.vn/gui-tiet-kiem/gui-tiet-kiem-ngan-hang-public-bank-viet-nam-36.html",
            "parse_key": ".ct_tab_product",
            "replace_key": ""
            },
            #   {
            # "father": "Lãi suất gửi tiết kiệm ",
            # "path": "laisuat",
            # "name": "PVcombank",
            # "link": "https://thebank.vn/gui-tiet-kiem/gui-tiet-kiem-ngan-hang-pvcombank-42.html",
            # "parse_key": ".ct_tab_product",
            # "replace_key": ""
            # },
               {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "PVcombank",
            "name_path": "pvcombank",
            "link": "https://thebank.vn/gui-tiet-kiem/gui-tiet-kiem-ngan-hang-pvcombank-42.html",
            "parse_key": ".ct_tab_product .prd_gtk",
            "replace_key": ""
            },
            #    {
            # "father": "Lãi suất gửi tiết kiệm ",
            # "path": "laisuat",
            # "name": "SaigonBank",
            # "link": "https://www.saigonbank.com.vn/vi/truy-cap-nhanh/lai-suat/Lai-suat-tien-gui-tiet-kiem",
            # "parse_key": "div table",
            # "replace_key": ""
            # },
             {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "SCB",
            "name_path": "scb",
            "link": "https://www.scb.com.vn/vie/tien-gui-khcn/tiet-kiem-thong-thuong",
            "parse_key": ".content-table",
            "replace_key": ""
            },
             {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "SeABank",
            "name_path": "seabank",
            "link": "https://www.seabank.com.vn/interest",
            "parse_key": ".ng-star-inserted .table-striped",
            "replace_key": ""
            },
              {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "SHB",
            "name_path": "shb",
            "link": "https://ibanking.shb.com.vn/Rate/TideRate",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
              {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "TPBank",
            "name_path": "tpbank",
            "link": "https://topi.vn/lai-suat-ngan-hang-tp-bank.html",
            "parse_key": "table",
            "replace_key": ""
            },
              {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "VIB",
            "name_path": "vib",
            "link": "https://onehousing.vn/thong-tin-va-doi-song/lai-suat-ngan-hang-vib-moi-nhat-lien-tuc-cap-nhat",
            "parse_key": "table",
            "replace_key": ""
            },
               {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "Bản Việt",
            "name_path": "viet-capital-bank",
            "link": "https://topi.vn/lai-suat-ngan-hang-ban-viet.html",
            "parse_key": "table",
            "replace_key": ""
            },
               {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "Vietcombank",
            "name_path": "vietcombank",
            "link": "https://www.tcqtkd.edu.vn/gui-tiet-kiem-vietcombank/",
            "parse_key": "table",
            "replace_key": "td i"
            },
               {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "Vietinbank",
            "name_path": "vietinbank",
            "link": "https://chogia.vn/lai-suat/vietinbank/", #"https://www.vietinbank.vn/web/home/vn/lai-suat",
            "parse_key": "table.uk-table-striped",
            "replace_key": "td i"
            },
                {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "VPBank",
            "name_path": "vpbank",
            "link": "https://vpbankonline.vpbank.com.vn/tiet-kiem/tiet-kiem-thuong-truc-tuyen/",
            "parse_key": "table.Table",
            "replace_key": ""
            },
           

        #tiền ảo
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BTC",# (Bitcoin)",
            "name_path": "btc",
            "link": "https://webgia.com/tien-ao/bitcoin/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ETH",# (Ethereum)",
            "name_path": "eth",
            "link": "https://webgia.com/tien-ao/ethereum/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BNB",# (Binance Coin)",
            "name_path": "bnb",
            "link": "https://webgia.com/tien-ao/bnb/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "XRP",# (Ripple)",
            "name_path": "xrp",
            "link": "https://webgia.com/tien-ao/ripple/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BCH",# (Bitcoin Cash)",
            "name_path": "bch",
            "link": "https://webgia.com/tien-ao/bitcoin-cash/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "XEM",# (NEM)",
            "name_path": "xem",
            "link": "https://webgia.com/tien-ao/nem/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "LTC",# (Litecoin)",
            "name_path": "ltc",
            "link": "https://webgia.com/tien-ao/litecoin/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "DASH",# (Dash)",
            "name_path": "dash",
            "link": "https://webgia.com/tien-ao/dash/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ETC",# (Ethereum Classic)",
            "name_path": "etc",
            "link": "https://webgia.com/tien-ao/ethereum-classic/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            # {
            # "father": "Tỷ giá ",
            # "path": "tienao",
            # "name": "MIOTA (IOTA)",
            # "link": "https://webgia.com/tien-ao/iota/", #không có biểu đồ
            # "parse_key": "section#coin-live",
            # "replace_key": ""
            # },
            
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "NEO",# (NEO)",
            "name_path": "neo",
            "link": "https://webgia.com/tien-ao/neo/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "QTUM",# (Qtum)",
            "name_path": "qtum",
            "link": "https://webgia.com/tien-ao/qtum/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "XMR",# (Monero)",
            "name_path": "xmr",
            "link": "https://webgia.com/tien-ao/monero/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "STRAT",# (Stratis)",
            "name_path": "strat",
            "link": "https://webgia.com/tien-ao/stratis/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "WAVES",# (Waves)",
            "name_path": "wavea",
            "link": "https://webgia.com/tien-ao/waves/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "EOS",# (EOS)",
            "name_path": "eos",
            "link": "https://webgia.com/tien-ao/eos/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ZEC",# (Zcash)",
            "name_path": "zec",
            "link": "https://webgia.com/tien-ao/zcash/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BTS",# (BitShares)",
            "name_path": "bts",
            "link": "https://webgia.com/tien-ao/bitshares/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "OMG",# (OmiseGo)",
            "name_path": "omg",
            "link": "https://webgia.com/tien-ao/omisego/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "USDT",# (Tether)",
            "name_path": "usdt",
            "link": "https://webgia.com/tien-ao/tether/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BNB",# (Tether)",
            "name_path": "bnb",
            "link": "https://webgia.com/tien-ao/bnb/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "USDC",# (Tether)",
            "name_path": "usdc",
            "link": "https://webgia.com/tien-ao/usd-coin/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "XRP",# (Tether)",
            "name_path": "xrp",
            "link": "https://webgia.com/tien-ao/xrp/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BUSD",# (Tether)",
            "name_path": "busd",
            "link": "https://webgia.com/tien-ao/binance-usd/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ADA",# (Tether)",
            "name_path": "ada",
            "link": "https://webgia.com/tien-ao/cardano/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "DOGE",# (Tether)",
            "name_path": "doge",
            "link": "https://webgia.com/tien-ao/dogecoin/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "MATIC",# (Tether)",
            "name_path": "matic",
            "link": "https://webgia.com/tien-ao/polygon/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "SOL",# (Tether)",
            "name_path": "sol",
            "link": "https://webgia.com/tien-ao/solana/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "DOT",# (Tether)",
            "name_path": "dot",
            "link": "https://webgia.com/tien-ao/polkadot-new/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "LTC",# (Tether)",
            "name_path": "ltc",
            "link": "https://webgia.com/tien-ao/litecoin/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "SHIB",# (Tether)",
            "name_path": "shib",
            "link": "https://webgia.com/tien-ao/shiba-inu/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "AVAX",# (Tether)",
            "name_path": "avax",
            "link": "https://webgia.com/tien-ao/avalanche/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "DAI",# (Tether)",
            "name_path": "dai",
            "link": "https://webgia.com/tien-ao/multi-collateral-dai/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "TRX",# (Tether)",
            "name_path": "trx",
            "link": "https://webgia.com/tien-ao/tron/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "UNI",# (Tether)",
            "name_path": "uni",
            "link": "https://webgia.com/tien-ao/uniswap/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "WBTC",# (Tether)",
            "name_path": "wbtc",
            "link": "https://webgia.com/tien-ao/wrapped-bitcoin/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ATOM",# (Tether)",
            "name_path": "atom",
            "link": "https://webgia.com/tien-ao/cosmos/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "LINK",# (Tether)",
            "name_path": "link",
            "link": "https://webgia.com/tien-ao/chainlink/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "LEO",# (Tether)",
            "name_path": "leo",
            "link": "https://webgia.com/tien-ao/unus-sed-leo/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "XMR",# (Tether)",
            "name_path": "xmr",
            "link": "https://webgia.com/tien-ao/monero/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ETC",# (Tether)",
            "name_path": "etc",
            "link": "https://webgia.com/tien-ao/ethereum-classic/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "TON",# (Tether)",
            "name_path": "ton",
            "link": "https://webgia.com/tien-ao/toncoin/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "APT",# (Tether)",
            "name_path": "apt",
            "link": "https://webgia.com/tien-ao/aptos/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BCH",# (Tether)",
            "name_path": "bch",
            "link": "https://webgia.com/tien-ao/bitcoin-cash/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "XLM",# (Tether)",
            "name_path": "xlm",
            "link": "https://webgia.com/tien-ao/stellar/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "OKB",# (Tether)",
            "name_path": "okb",
            "link": "https://webgia.com/tien-ao/okb/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "APE",# (Tether)",
            "name_path": "ape",
            "link": "https://webgia.com/tien-ao/apecoin-ape/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "NEAR",# (Tether)",
            "name_path": "near",
            "link": "https://webgia.com/tien-ao/near-protocol/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "CRO",# (Tether)",
            "name_path": "cro",
            "link": "https://webgia.com/tien-ao/cronos/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "FIL",# (Tether)",
            "name_path": "fil",
            "link": "https://webgia.com/tien-ao/filecoin/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "LDO",# (Tether)",
            "name_path": "ldo",
            "link": "https://webgia.com/tien-ao/lido-dao/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ALGO",# (Tether)",
            "name_path": "algo",
            "link": "https://webgia.com/tien-ao/algorand/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "QNT",# (Tether)",
            "name_path": "qnt",
            "link": "https://webgia.com/tien-ao/quant/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "VET",# (Tether)",
            "name_path": "vet",
            "link": "https://webgia.com/tien-ao/vechain/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ICP",# (Tether)",
            "name_path": "icp",
            "link": "https://webgia.com/tien-ao/internet-computer/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "HBAR",# (Tether)",
            "name_path": "hbar",
            "link": "https://webgia.com/tien-ao/hedera/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "MANA",# (Tether)",
            "name_path": "mana",
            "link": "https://webgia.com/tien-ao/decentraland/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "FTM",# (Tether)",
            "name_path": "ftm",
            "link": "https://webgia.com/tien-ao/fantom/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "AAVE",# (Tether)",
            "name_path": "aave",
            "link": "https://webgia.com/tien-ao/aave/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BIT",# (Tether)",
            "name_path": "bit",
            "link": "https://webgia.com/tien-ao/bitdao/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "EOS",# (Tether)",
            "name_path": "eos",
            "link": "https://webgia.com/tien-ao/eos/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BIT",# (Tether)",
            "name_path": "bit",
            "link": "https://webgia.com/tien-ao/bitdao/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "AXS",# (Tether)",
            "name_path": "axs",
            "link": "https://webgia.com/tien-ao/axie-infinity/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "SAND",# (Tether)",
            "name_path": "sand",
            "link": "https://webgia.com/tien-ao/the-sandbox/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "FLOW",# (Tether)",
            "name_path": "flow",
            "link": "https://webgia.com/tien-ao/flow/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "EGLD",# (Tether)",
            "name_path": "egld",
            "link": "https://webgia.com/tien-ao/multiversx-egld/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "THETA",# (Tether)",
            "name_path": "theta",
            "link": "https://webgia.com/tien-ao/theta-network/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "XTZ",# (Tether)",
            "name_path": "xtz",
            "link": "https://webgia.com/tien-ao/tezos/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "LUNC",# (Tether)",
            "name_path": "lunc",
            "link": "https://webgia.com/tien-ao/terra-luna/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "TUSD",# (Tether)",
            "name_path": "tusd",
            "link": "https://webgia.com/tien-ao/trueusd/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "CHZ",# (Tether)",
            "name_path": "chz",
            "link": "https://webgia.com/tien-ao/chiliz/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "USDP",# (Tether)",
            "name_path": "usdp",
            "link": "https://webgia.com/tien-ao/paxos-standard/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BSV",# (Tether)",
            "name_path": "bsv",
            "link": "https://webgia.com/tien-ao/bitcoin-sv/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "HT",# (Tether)",
            "name_path": "ht",
            "link": "https://webgia.com/tien-ao/huobi-token/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "GRT",# (Tether)",
            "name_path": "grt",
            "link": "https://webgia.com/tien-ao/the-graph/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "FXS",# (Tether)",
            "name_path": "fxs",
            "link": "https://webgia.com/tien-ao/frax-share/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "KCS",# (Tether)",
            "name_path": "kcs",
            "link": "https://webgia.com/tien-ao/kucoin-token/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ZEC",# (Tether)",
            "name_path": "zec",
            "link": "https://webgia.com/tien-ao/zcash/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "TWT",# (Tether)",
            "name_path": "twt",
            "link": "https://webgia.com/tien-ao/curve-dao-token/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "USDD",# (Tether)",
            "name_path": "usdd",
            "link": "https://webgia.com/tien-ao/usdd/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "XEC",# (Tether)",
            "name_path": "xec",
            "link": "https://webgia.com/tien-ao/ecash/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BTT",# (Tether)",
            "name_path": "btt",
            "link": "https://webgia.com/tien-ao/bittorrent-new/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "CAKE",# (Tether)",
            "name_path": "cake",
            "link": "https://webgia.com/tien-ao/pancakeswap/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "MIOTA",# (Tether)",
            "name_path": "miota",
            "link": "https://webgia.com/tien-ao/iota/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "MKR",# (Tether)",
            "name_path": "mkr",
            "link": "https://webgia.com/tien-ao/maker/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "KLAY",# (Tether)",
            "name_path": "klay",
            "link": "https://webgia.com/tien-ao/klaytn/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "DASH",# (Tether)",
            "name_path": "dash",
            "link": "https://webgia.com/tien-ao/dash/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BNB",# (Tether)",
            "name_path": "bnb",
            "link": "https://webgia.com/tien-ao/bnb/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "RUNE",# (Tether)",
            "name_path": "rune",
            "link": "https://webgia.com/tien-ao/thorchain/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "SNX",# (Tether)",
            "name_path": "snx",
            "link": "https://webgia.com/tien-ao/synthetix/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "GUSD",# (Tether)",
            "name_path": "gusd",
            "link": "https://webgia.com/tien-ao/gemini-dollar/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "NEO",# (Tether)",
            "name_path": "neo",
            "link": "https://webgia.com/tien-ao/neo/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "MINA",# (Tether)",
            "name_path": "mina",
            "link": "https://webgia.com/tien-ao/mina/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "OP",# (Tether)",
            "name_path": "op",
            "link": "https://webgia.com/tien-ao/optimism-ethereum/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "PAXG",# (Tether)",
            "name_path": "paxg",
            "link": "https://webgia.com/tien-ao/pax-gold/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "IMX",# (Tether)",
            "name_path": "imx",
            "link": "https://webgia.com/tien-ao/immutable-x/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "GMX",# (Tether)",
            "name_path": "gmx",
            "link": "https://webgia.com/tien-ao/gmx/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "OSMO",# (Tether)",
            "name_path": "osmo",
            "link": "https://webgia.com/tien-ao/osmosis/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "NEXO",# (Tether)",
            "name_path": "nexo",
            "link": "https://webgia.com/tien-ao/nexo/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ZIL",# (Tether)",
            "name_path": "zil",
            "link": "https://webgia.com/tien-ao/zilliqa/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "GT",# (Tether)",
            "name_path": "gt",
            "link": "https://webgia.com/tien-ao/gatetoken/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ENJ",# (Tether)",
            "name_path": "enj",
            "link": "https://webgia.com/tien-ao/enjin-coin/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BNB",# (Tether)",
            "name_path": "bnb",
            "link": "https://webgia.com/tien-ao/bnb/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "LUNA",# (Tether)",
            "name_path": "luna",
            "link": "https://webgia.com/tien-ao/terra-luna-v2/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "CVX",# (Tether)",
            "name_path": "cvx",
            "link": "https://webgia.com/tien-ao/convex-finance/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "1INCH",# (Tether)",
            "name_path": "1inch",
            "link": "https://webgia.com/tien-ao/1inch/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "FEI",# (Tether)",
            "name_path": "fei",
            "link": "https://webgia.com/tien-ao/fei-usd/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ETHW",# (Tether)",
            "name_path": "ethw",
            "link": "https://webgia.com/tien-ao/ethereum-pow/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "LRC",# (Tether)",
            "name_path": "lrc",
            "link": "https://webgia.com/tien-ao/loopring/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BAT",# (Tether)",
            "name_path": "bat",
            "link": "https://webgia.com/tien-ao/basic-attention-token/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "COMP",# (Tether)",
            "name_path": "comp",
            "link": "https://webgia.com/tien-ao/compound/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "GALA",# (Tether)",
            "name_path": "gala",
            "link": "https://webgia.com/tien-ao/gala/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "HNT",# (Tether)",
            "name_path": "hnt",
            "link": "https://webgia.com/tien-ao/helium/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "RPL",# (Tether)",
            "name_path": "rpl",
            "link": "https://webgia.com/tien-ao/rocket-pool/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "KAVA",# (Tether)",
            "name_path": "kava",
            "link": "https://webgia.com/tien-ao/kava/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "STX",# (Tether)",
            "name_path": "stx",
            "link": "https://webgia.com/tien-ao/stacks/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "T",# (Tether)",
            "name_path": "t",
            "link": "https://webgia.com/tien-ao/threshold/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "CSPR",# (Tether)",
            "name_path": "cspr",
            "link": "https://webgia.com/tien-ao/casper/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "HOT",# (Tether)",
            "name_path": "hot",
            "link": "https://webgia.com/tien-ao/holo/",
            "parse_key": "section#coin-live",
            "replace_key": ""
            },
     


             {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BTC (Bitcoin)",
            "name_path": "detail-btc",
            "link": "https://webgia.com/tien-ao/bitcoin/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ETH (Ethereum)",
            "name_path": "detail-eth",
            "link": "https://webgia.com/tien-ao/ethereum/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BNB (Binance Coin)",
            "name_path": "detail-bnb",
            "link": "https://webgia.com/tien-ao/bnb/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "XRP (Ripple)",
            "name_path": "detail-xrp",
            "link": "https://webgia.com/tien-ao/ripple/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BCH (Bitcoin Cash)",
            "name_path": "detail-bch",
            "link": "https://webgia.com/tien-ao/bitcoin-cash/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "XEM (NEM)",
            "name_path": "detail-xem",
            "link": "https://webgia.com/tien-ao/nem/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "LTC (Litecoin)",
            "name_path": "detail-ltc",
            "link": "https://webgia.com/tien-ao/litecoin/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "DASH (Dash)",
            "name_path": "detail-dash",
            "link": "https://webgia.com/tien-ao/dash/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ETC (Ethereum Classic)",
            "name_path": "detail-etc",
            "link": "https://webgia.com/tien-ao/ethereum-classic/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            # {
            # "father": "Tỷ giá ",
            # "path": "tienao",
            # "name": "MIOTA (IOTA)",
            # "link": "https://webgia.com/tien-ao/iota/", #không có biểu đồ
            # "parse_key": "section#coin-live",
            # "replace_key": ""
            # },
            
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "NEO (NEO)",
            "name_path": "detail-neo",
            "link": "https://webgia.com/tien-ao/neo/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "QTUM (Qtum)",
            "name_path": "detail-qtum",
            "link": "https://webgia.com/tien-ao/qtum/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "XMR (Monero)",
            "name_path": "detail-xmr",
            "link": "https://webgia.com/tien-ao/monero/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "STRAT (Stratis)",
            "name_path": "detail-strat",
            "link": "https://webgia.com/tien-ao/stratis/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "WAVES (Waves)",
            "name_path": "detail-wavea",
            "link": "https://webgia.com/tien-ao/waves/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "EOS (EOS)",
            "name_path": "detail-eos",
            "link": "https://webgia.com/tien-ao/eos/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "ZEC (Zcash)",
            "name_path": "detail-zec",
            "link": "https://webgia.com/tien-ao/zcash/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "BTS (BitShares)",
            "name_path": "detail-bts",
            "link": "https://webgia.com/tien-ao/bitshares/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "OMG (OmiseGo)",
            "name_path": "detail-omg",
            "link": "https://webgia.com/tien-ao/omisego/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            {
            "father": "Tỷ giá ",
            "path": "tienao",
            "name": "USDT (Tether)",
            "name_path": "detail-usdt",
            "link": "https://webgia.com/tien-ao/tether/?abc",
            "parse_key": "article div",
            "replace_key": ""
            },
            

        # Xăng dầu
            {
            "father": "Giá bán lẻ xăng dầu ",
            "path": "xangdau",
            "name": "Petrolimex",
            "name_path": "petrolimex",
            "link": "https://webtygia.com/gia-xang-dau/petrolimex.html",
            "parse_key": "table.table-bordered",
            "replace_key": ""
            },
            {
            "father": "Biểu đồ  ",
            "path": "xangdau",
            "name": "giá dầu thô thế giới",
            "name_path": "gia-dau-tho-the-gioi",
            "link": "https://webgia.com/gia-xang-dau/dau-tho/",  #chia hai bang
            "parse_key": "div.row",
            "replace_key": ""
            },

            # {
            # "father": "Tỉ giá ngoại tệ ",
            # "path": "tygia",
            # "name": "OceanBank",
            # "link": "https://oceanbank.vn/ty-gia-ngoai-te.html",
            # "parse_key": "table.tb_tg",
            # "replace_key": ""
            # },
                {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "SaigonBank",
            "name_path": "sai-gon-bank",
            "link": "https://www.saigonbank.com.vn/vi/truy-cap-nhanh/lai-suat/Lai-suat-tien-gui-tiet-kiem",
            "parse_key": "div table",
            "replace_key": ""
            },
                 {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "GPBank",
            "name_path": "gpbank",
            "link": "https://www.gpbank.com.vn/InterestDetail",   #https://www.gpbank.com.vn/InterestDetail lõi ssl, thêm verify=False vào request
            "parse_key": "table.table-striped",
            "replace_key": ""
            },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "SaigonBank",
            "name_path": "saigonbank",
            "link": "https://chogia.vn/ty-gia/saigonbank/",
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },
             {
            "father": "Lãi suất gửi tiết kiệm  ",
            "path": "laisuat",
            "name": "VR Bank",
            "name_path": "vrbank",
            "link": "https://thebank.vn/gui-tiet-kiem/gui-tiet-kiem-ngan-hang-vrb-39.html",
            "parse_key": "table",
            "replace_key": ""
            },

              {
            "father": "Lãi suất gửi tiết kiệm  ",
            "path": "laisuat",
            "name": "tại các ngân hàng",
            "name_path": "lai-suat-ngan-hang",
            "link": "https://chogia.vn/lai-suat/",
            "parse_key": "table",
            "replace_key": ""
            },
             {
            "father": "Lãi suất gửi tiết kiệm  ",
            "path": "laisuat",
            "name": "Viettinbank",
            "name_path": "viettinbank",
            "link": "https://www.vietinbank.vn/web/home/vn/lai-suat",
            "parse_key": "table",
            "replace_key": ""
            },   
             {
            "father": "Tỉ giá ",
            "path": "tienao",
            "name": "tiền ảo",
            "name_path": "ti-gia-tien-ao",
            "link": "https://wwebgia.com/tien-ao/",
            "parse_key": "table.table-radius",
            "replace_key": ""
            },  
                  
            ]
        
        inputs_=[
            
            #  {
            # "father": "Lãi suất gửi tiết kiệm ",
            # "path": "laisuat",
            # "name": "VRBank",
            # "link": "https://thebank.vn/gui-tiet-kiem/gui-tiet-kiem-ngan-hang-vrb-39.html",
            # "parse_key": ".prd_gtk table",
            # "replace_key": ""
            # },
            {
            "father": "Tỉ giá ngoại tệ ",
            "path": "tygia",
            "name": "OceanBank",
            "name_path": "oceanbank",
            "link": "https://chogia.vn/ty-gia/oceanbank/",  #"https://oceanbank.vn/ty-gia-ngoai-te.html",
            "parse_key": "table.uk-table-striped",
            "replace_key": ""
            },

            #  {
            # "father": "Biểu đồ giá vàng ",
            # "path": "giavang",
            # "name": "SJC hôm nay",
            # "name_path": "sjc-hom-nay",
            # "link": "https://webgia.com/gia-vang/sjc/bieu-do-1-ngay.html",
            # "parse_key": "#bieu_do_sjc",
            # "replace_key": ""
            # },

                {
            "father": "Lãi suất gửi tiết kiệm ",
            "path": "laisuat",
            "name": "VPBank",
            "name_path": "vpbank",
            "link": "https://vpbankonline.vpbank.com.vn/tiet-kiem/tiet-kiem-thuong-truc-tuyen/",
            "parse_key": "table.Table",
            "replace_key": ""
            },
            
            #     {
            # "father": "Lãi suất gửi tiết kiệm ",
            # "path": "laisuat",
            # "name": "SaigonBank",
            # "link": "https://www.saigonbank.com.vn/vi/truy-cap-nhanh/lai-suat/Lai-suat-tien-gui-tiet-kiem",
            # "parse_key": "div table",
            # "replace_key": ""
            # },
            #      {
            # "father": "Lãi suất gửi tiết kiệm ",
            # "path": "laisuat",
            # "name": "GPBank",
            # "link": "https://www.gpbank.com.vn/InterestDetail",   #https://www.gpbank.com.vn/InterestDetail lõi ssl, thêm verify=False vào request
            # "parse_key": "table.table-striped",
            # "replace_key": ""
            # },
            # {
            # "father": "Tỉ giá ngoại tệ ",
            # "path": "tygia",
            # "name": "SaigonBank",
            # "link": "https://www.saigonbank.com.vn/vi/truy-cap-nhanh/ty-gia-ngoai-te",
            # "parse_key": "div#lstRate",
            # "replace_key": ""
            # }
            
        ]
        def rq(url):
            # re=requests.get(input_["link"])
            # url="https://oceanbank.vn/ty-gia-ngoai-te.html"
            # print(input_)
            proxies={'https': 'http://pxuser:jka&^4hhBJFk9)*@51.81.196.44:3128'}
            response = requests.get(url, proxies=proxies, verify=False,)
            status_ = response.status_code
            # print(status_)
            html_ = response.text
            # print(status_)
            return html_ , status_
        
        while True:
            try:
                for input_ in inputs_:
                    html_ , status_= rq(input_["link"])
                    reponse ={
                        "status": status_,
                        "input_" : input_,
                        "html": html_
                    }
                    # print(reponse["input_"])
                    await handle_home(reponse)

                
                for input_ in list_input:
                    # handle_parse(input_)
                    # print(input_)
                    rq_.add_queue(input_["link"], callback=handle_home, cb_kwargs={"input_": input_})
            except:
                pass
        
        # Finish
        await rq_.wait()
        print(f"Finish - total_time: {time.time() - t0}")
    except:
        def send_to_telegram(message):

            apiToken = '5656002256:AAG6izjj3dmOYdHd0iZz9TKrgeRLWv32VDc'
            chatID = '-892437569'
            apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

            try:
                response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
                print(response.text)
            except Exception as e:
                print(e)

        # send_to_telegram(f'[Crawl_Web_Gia]\nLink_error: {input_["link"]}' + "\nDetail_error: " +traceback.format_exc())
        # print(input_["link"])
        # print(traceback.format_exc())
async def handle_home(response):
    # html_=fetch(response["input_"]["link"])  
    # def send_to_telegram(message):
    #     apiToken = '5656002256:AAG6izjj3dmOYdHd0iZz9TKrgeRLWv32VDc'
    #     chatID = '-892437569'
    #     apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

    #     try:
    #         response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
    #         print(response.text)
    #     except Exception as e:
    #         print(e)
    # print (response["status"])
    # print(response["input_"]["link"])
    # if response["status"] != 200:
    #    send_to_telegram(f'[Crawl_Web_Gia]\nLink_error: {response["input_"]["link"]}' + "\nDetail_error: " + str(response['status']))
        
    input_=crawl_sm_home(response["input_"], response["html"])
    link=input_["link"]
    
    
    # find_ = {"link": { "$regex": link }}
    filter_ = {"link":1}
    find_data = await db_client.find_one({"link": link})
    # print(find_data)
    # print(find_data)
    if find_data==None:
    # print(input_["name"])
        insert_await = await db_client.insert_item(input_)
    else:
        # print(find_data["update_time"])
        # delta = abs(datetime.datetime.now() - find_data["update_time"])
        # print(delta.days)
        # if delta.days==0 :
        #     send_to_telegram(f'[Crawl_Web_Gia]\nLink_error: {response["input_"]["link"]}' + '/nDetail_error: '  + 'updated')
        # else:
        #     send_to_telegram("not updated")

            
    # # print(find_data["_id"])
        insert_await = await db_client.update_one(find_data["_id"],input_)
    print(insert_await)
  
    
# parse data
def crawl_sm_home(input_,html_):
    # if input_["name"]=="SJC":
    #     root = HTMLParser(html_)

    #     # Tìm bảng trong HTML và lấy những hàng có chứa "SJC"
    #     table = root.css_first('table')
    #     rows = table.css('tr')

    #     sjc_rows = [row for row in rows if 'SJC' in row.text()]

    #     # Xóa những hàng không có "SJC" khỏi bảng
    #     for row in rows:
    #         if row not in sjc_rows:
    #             cells = row.css('td')
    #             for cell in cells:
    #                 cell.decompose()

    #     valid_rows = [row for row in rows if row.css('td')]

    #     # Xóa những hàng không có ô
    #     for row in rows[1:]:
    #         if row not in valid_rows:
    #             cells = row.css('th')
    #             for cell in cells:
    #                 cell.decompose()


    #     # In ra bảng đã được lọc
    #     # print(table.html)
    #     input_.update({
    #         "table": table.html
    #     })
    # elif input_["name"]=="PNJ":
    #     root = HTMLParser(html_)
    #     #Tìm bảng trong HTML và lấy những hàng có chứa "PNJ"
    #     table = root.css_first('table')
    #     rows = table.css('tr')
    #     pnj_rows = [row for row in rows if 'PNJ' in row.text()]

    #     # Duyệt qua từng hàng và xóa những ô không có "PNJ"
    #     for row in rows:
    #         if row not in pnj_rows:
    #             if "TP. Hồ Chí Minh" not in row.text() and "Hà Nội" not in row.text() and "Đà Nẵng" not in row.text() and  "Miền Tây" not in row.text():
    #                 links = row.css('a')
    #                 for link in links:
    #                     if "https://giavang.org/khu-vuc" in link.attributes.get('href', ''):
    #                         if "TP. Hồ Chí Minh" not in link.text() and "Hà Nội" not in link.text() and "Đà Nẵng" not in link.text() and "Miền Tây" not in link.text():
    #                             link.decompose()
    #     for row in rows:
    #         if row not in pnj_rows:
    #             cells = row.css('td')
    #             for cell in cells:
    #                 if 'PNJ' not in cell.text():
    #                     cell.decompose()
    #     for row in rows:
    #         if row not in pnj_rows:
    #             cells = row.css('th')
    #             for cell in cells:
    #                 if not cell.css('a'):
    #                     cell.decompose()
    #     # In ra bảng đã được lọc
    #     # print(table.html)
    #     input_.update({
    #         "table": table.html
    #     })
        # add_db(input_)
    if input_["father"]== "Biểu đồ giá vàng ":
        root = HTMLParser(html_)
        scripts = root.css('script')
        table = root.css_first(input_["parse_key"]).html
        for script in scripts:
            table=table+script.html
        # print(table)
        input_.update({
            "table": table,
            "update_time": datetime.datetime.now()
        })
    elif input_["father"]== "Tỷ giá ":
        tree = HTMLParser(html_)
        scripts = tree.css('script')
        table = tree.css_first(input_["parse_key"]).html
        for script in scripts:
            table=table+script.html
        input_.update({
            "table": table,
            "update_time": datetime.datetime.now()
        })
    elif input_["name"]== "giá dầu thô thế giới":
        tree = HTMLParser(html_)
        scripts = tree.css('script')
        # table = root.css_first(input_["parse_key"]).html
        table=""
        for script in scripts:
            table=table+script.html
        input_.update({
            "table": table,
            "update_time": datetime.datetime.now()
        })
    elif input_["name"]== "MB Bank" or input_["name"]== "Nam Á Bank" or input_["name"]== "PG Bank" or input_["name"]== "Vietcombank" :
        tree = HTMLParser(html_)
        try:
            node = tree.css_first(input_["parse_key"]).html
            remove = tree.css_first(input_["replace_key"]).html
            node = node.replace(remove, "")
        except:
            node = tree.css_first(input_["parse_key"]).html
        remove='<table class="table table-bordered table-hover table-striped text-right"'
        replace="<table"
        node = node.replace(replace, remove)
        input_.update({
            "table": node,
            "update_time": datetime.datetime.now()
        })
    elif input_["name"]== "Indovina Bank":
        tree = HTMLParser(html_)
        # print(tree.html)
        try:
            node = tree.css_first(input_["parse_key"]).html
            remove = tree.css_first(input_["replace_key"]).html
            node = node.replace(remove, "")
        except:
            node = tree.css_first(input_["parse_key"]).html
        # print(node)
        # print(input_["name"])
        import re
        regex1=re.compile(r'<table(.*?)>')
        kq=regex1.search(node) #findAll
        name=kq.group(0)
        # print(type(name))
        
        remove='<table class="table table-bordered table-hover table-striped text-right">'
        # # if input_["name"] == "MB Bank":   
        replace=name
        node = node.replace(replace, remove)

        table = HTMLParser(node)

        for tab in table.css("a"):
            replace=f"<a>{tab.text()}</a>"
            node = node.replace(tab.html, replace)
        #xóa image
        for tab in table.css("img"):
            href=(tab.html)
            node = node.replace(href, "")
        input_.update({
            "table": node,
            "update_time": datetime.datetime.now()
        })
        # print(input_["table"])
    elif input_["name"]== "VR Bank":
        tree = HTMLParser(html_)
        # print(tree.html)
        try:
            node = tree.css_first(input_["parse_key"]).html
            remove = tree.css_first(input_["replace_key"]).html
            node = node.replace(remove, "")
        except:
            node = tree.css_first(input_["parse_key"]).html
        input_.update({
            "table": node,
            "update_time": datetime.datetime.now()
        })
    elif input_["name"]== "tại các ngân hàng":
        tree = HTMLParser(html_)
        scripts = tree.css('table')
        # table = tree.css_first(input_["parse_key"]).html
        table="LÃI SUẤT TIẾT KIỆM GỬI TẠI QUẦY"
        remove='table table-bordered table-hover table-striped text-right'
        table=table+scripts[0].html+"LÃI SUẤT TIẾT KIỆM KHI GỬI TRỰC TUYẾN (ONLINE)"+scripts[1].html
        for script in scripts:
            replace=(script.attributes["class"])
            table = table.replace(replace, remove)
            # print(table)
        # node=table
        # import re
        # # print(node)
        # regex1=re.compile(r'<table(.*?)>')
        # kq=regex1.search(node) #findAll
        # name=kq.group(1)
        # if name == None:
        #     name=""
        # else:
        # # print(name)
        #     node= HTMLParser(node)

        #     links = node.css('table')
        #     node=node.html
        #     # for link in links:
        #         # print(link.html)
        #     remove=' class="table table-bordered table-hover table-striped text-right"'
        #     replace=name
        #     node = node.replace(replace, remove)
        #     regex2=re.compile(r'<table class="uk-table uk-table-striped "(.*?)>')
        #     kq=regex1.search(node) #findAll
        #     name2=kq.group(0)
        #     remove2='<table class="table table-bordered table-hover table-striped text-right" >'
        #     node = node.replace(name2, remove2)
        input_.update({
            "table": table,
            "update_time": datetime.datetime.now()
        })
    # elif input_["name_path"]== "eximbank":
    else: 
        tree = HTMLParser(html_)
        # print(tree.html)
        try:
            node = tree.css_first(input_["parse_key"]).html
            remove = tree.css_first(input_["replace_key"]).html
            node = node.replace(remove, "")
        except:
            node = tree.css_first(input_["parse_key"]).html
        # with open(f'{input_["father"]+input_["name"]}.html', 'w', encoding='utf8') as f:
        #     f.write(input_["father"]+input_["name"]+node)

        import re
        # print(node)
        regex1=re.compile(r'<table(.*?)>')
        kq=regex1.search(node) #findAll
        name=kq.group(1)
        if name == None:
            name=""
        else:
        # print(name)
            node= HTMLParser(node)

            links = node.css('table')
            node=node.html
            # for link in links:
                # print(link.html)
            remove=' class="table table-bordered table-hover table-striped text-right"'
            replace=name
            node = node.replace(replace, remove)
        
        table=HTMLParser(node)

        #xóa link
        for tab in table.css("a"):
            replace=f"<a>{tab.text()}</a>"
            # href=('href="'+tab.attributes["href"]+'"')
            node = node.replace(tab.html, replace)

        #xóa image
        for tab in table.css("img"):
            href=(tab.html)
            node = node.replace(href, "")

        # for tab in table.css("a"):
        #     href=('href="'+tab.attributes["href"]+'"')
        #     node = node.replace(href, "")

        #xóa thẻ span
        if input_["name"] == "ACB":
            for tab in table.css("span"):
                node = node.replace(tab.html, "")
        elif input_["name"] == "HSBC":
            list_change = [
            { 
            "path": "tygia",
            "remove":"US Dollar (USD)",
            "replace": '      USD'
            },
            { 
            "path": "tygia",
            "remove":"Euro (EUR)",
            "replace": 'EUR'
            },
            {
            "path": "tygia" ,
            "remove":"British Pound (GBP)",
            "replace": 'GBP'
            },
            { 
            "path": "tygia" ,   
            "remove":"Hong Kong Dollar (HKD)",
            "replace": 'HKD'
            },
            { 
            "path": "tygia"   ,
            "remove":"Japanese Yen (JPY)",
            "replace": 'JPY'
            },
            { 
            "path": "tygia"  , 
            "remove":"Australian Dollar (AUD)",
            "replace": 'AUD'
            },
            { 
            "path": "tygia"   ,    
            "remove":"Singapore Dollar (SGD)",
            "replace": 'SGD'
            },
            { 
            "path": "tygia"    ,   
            "remove":"Thai Baht (THB)",
            "replace": 'THB'
            },
            { 
            "path": "tygia"   ,    
            "remove":"Canadian Dollar (CAD)",
            "replace": 'CAD'
            },
            { 
            "path": "tygia"   ,    
            "remove":"New Zealand Dollar (NZD)",
            "replace": 'NZD'
            },
            { 
            "path": "tygia"   ,  
            "remove":"Swiss Franc (CHF)",
            "replace": 'CHF'
            },
            { 
            "path": "tygia"   ,  
            "remove":"Currencies",
            "replace": 'Ngoại tệ'
            },
            { 
            "path": "tygia"   ,  
            "remove":"Cash Buying",
            "replace": 'Mua tiền mặt'
            },
            { 
            "path": "tygia"   ,  
            "remove":"Telegraphic Buying",
            "replace": 'Mua chuyển khoản'
            },
            { 
            "path": "tygia"   ,  
            "remove":"Cash Selling",
            "replace": 'Bán tiền mặt'
            },
            { 
            "path": "tygia"   ,  
            "remove":"Telegraphic Selling",
            "replace": 'Bán chuyển khoản'
            },
            ]
            for change in list_change:
                node=node.replace(change["remove"],change["replace"])
        elif input_["name"] == "EximBank":
            list_change = [
            { 
            "path": "tygia",
            "remove":"Đô-la Mỹ",
            "replace": 'USD'
            },
            { 
            "path": "tygia",
            "remove":"Đồng Euro",
            "replace": 'EUR'
            },
            {
            "path": "tygia" ,
            "remove":"Bảng Anh",
            "replace": 'GBP'
            },
            { 
            "path": "tygia" ,   
            "remove":"Đô-la Hồng Kông",
            "replace": 'HKD'
            },
            { 
            "path": "tygia"   ,
            "remove":"Yên Nhật",
            "replace": 'JPY'
            },
            { 
            "path": "tygia"  , 
            "remove":"Ðô-la Úc",
            "replace": 'AUD'
            },
            { 
            "path": "tygia"   ,    
            "remove":"Ðô-la Singapore",
            "replace": 'SGD'
            },
            { 
            "path": "tygia"    ,   
            "remove":"Bat Thái Lan",
            "replace": 'THB'
            },
            { 
            "path": "tygia"   ,    
            "remove":"Ðô-la Canada",
            "replace": 'CAD'
            },
            { 
            "path": "tygia"   ,    
            "remove":"Ðô-la New Zealand",
            "replace": 'NZD'
            },
            { 
            "path": "tygia"   ,  
            "remove":"Franc Thụy Sĩ",
            "replace": 'CHF'
            },

            ]
            for change in list_change:
                node=node.replace(change["remove"],change["replace"])
        # elif 
        # print(node)
            # print(node)
        # print(node)
        # print(node)
        
        # with open(f'{input_["father"]+input_["name"]}.html', 'w', encoding='utf8') as f:
        #     f.write(input_["father"]+input_["name"]+node)

        # if input_["path"] == "tygia" and input_["name"] == "ABBank":
        #     scripts = HTMLParser(node).css('tr')
        #     table="<table>"
        #     for script in scripts[12:]:
        #         table=table+script.html
        #         input_.update({
        #             "table": table+"</table>"
        #         })
        # else:
        #     input_.update({
        #         "table": node
        #     })
        input_.update({
            "table": node,
            "update_time": datetime.datetime.now()
        })
    # print(input_["table"])
    return(input_)

asyncio.run(main())
