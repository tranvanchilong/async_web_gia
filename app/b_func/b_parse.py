import traceback
import random
from parsel import Selector # https://github.com/scrapy/parsel scrapy selector
import validators

def hrefs_filter(hrefs, root, specific_ignores = []):
    ''' Copy tren mang: https://www.jcchouinard.com/web-scraping-with-python-and-requests-html/
    updated_links = []
    for link in jlinks:
        if re.search(".*@.*|.*javascript:.*|.*tel:.*",link):
            link = ""
        elif re.search("^(?!http).*",link):
            link = domain + link
            updated_links.append(link)
        else:
            updated_links.append(link)
    '''
    href_is_ignores = ["#", "/", "javascript:;"]
    common_ignores = ["tel:", "mailto:", "wp-content/uploads", "/go/"]
    new_hrefs = []
    for href in hrefs:
        # Ignore case
        if any(check == href for check in href_is_ignores):
            continue
        elif any(check in href for check in common_ignores):
            continue
        elif any(check in href for check in specific_ignores):
            continue

        # Add root to link without root
        if "://" not in href:
            href = root + href

        # Ignore url to external site
        if not href.startswith(root):
            continue

        # Validate link ( Có vẻ hàm bọn nó viết hơi ngu, print ra để khi chạy thấy nó ngu thì bỏ nó đi )
        if validators.url(href) != True:
            continue

        
        if "#" in href:
            new_url = href.split("#")[0]
            if root not in new_url:
                continue
            new_hrefs.append(new_url)
        else:
            new_hrefs.append(href)
    return list(set(new_hrefs))
def parse_gooogle(html_):
    data = []
    try:
        # Parsing the page
        tree = html.fromstring(html_)      
        for content in tree.xpath('//*[@id="main"]/div/div'):
            tree_ = html.fromstring(html.tostring(content))
            title = tree_.xpath('//h3')
            if len(title) == 0: continue
            for t in title:
                title_ = t[0].text
            # print(f"title_: {title_}")

            link = tree_.xpath('//a')[0].get('href')
            if "url?q=" in link:
                link = link.split('url?q=')[1].split('&sa')[0].strip()
                # # Write
                # rd = random.randint(1000, 9999)
                # with open(f"./google_demo/google-{rd}.html", 'w', encoding='utf8') as f:
                #     f.write(html_)
            # print(f"link: {link}")

            description = tree_.xpath('//div[2]')[0]
            if "<span" in str(html.tostring(description)):
                remove_ = description.xpath('//span/text()')
                # print(f"remove_: {remove_}")
                description = description.xpath("string()").strip()
                for rm in remove_:
                    # print(f"rm: {rm}")
                    description = description.replace(rm.strip(), '').strip()
            else:
                description = description.xpath("string()").strip()

            # print(f"description: {description}")


            # print()
            # print()
            # print()
            extracted_content = {
                'title': title_,
                # 'url': link,
                # 'description': description,
            }
            data.append(extracted_content)
    except:
        # print(f"error: {traceback.format_exc()}")
        # Write
        # with open("google.html", 'w', encoding='utf8') as f:
        #     f.write(html_)
        pass

    return data
def scrapy_parse_gooogle(html_):
    selector = Selector(text=html_)
    data = []
    retry_ = False
    # Check
    if "There are no results for" in html_:
        print(f"RETRYRETRYRETRYRETRY: There are no results for {url}")
        retry_ = True
    else:
        # #  write sample data
        # with open("google.html", "w", encoding="utf8") as f:
        #     f.write(html_)

        # parse
        for content in selector.xpath('//*[@id="main"]/div/div'):
            try:
                title = content.xpath('.//h3').xpath("string()").get()
                if title == None: continue
                # print(f"title: {title}")
                link = content.xpath('.//a').attrib['href']
                if "url?q=" in link:
                    link = link.split('url?q=')[1].split('&sa')[0].strip()
                elif "url=" in link:
                    link = link.split('url=')[1].split('&')[0].strip()
                # print(f"link: {link}")
                description = content.xpath('.//div[2]')
                if "<span" in str(description.get()):
                    remove_ = description.xpath('.//span/text()').getall()
                    # print(f"remove_: {remove_}")
                    description = description.xpath("string()").get()
                    for rm in remove_:
                        # print(f"rm: {rm}")
                        description = description.replace(rm.strip(), '').strip()
                else:
                    description = description.xpath("string()").get().strip()

                # print(f"description: {description}")
                # print()
                # print()
                extracted_content = {
                    'title': title,
                    'url': link,
                    'description': description,
                }
                # print(f"extracted_content: {extracted_content}")
                data.append(extracted_content)
            except Exception as e:
                # print(f"EEEEEEEEEEEEEEEE: {e} - content: {content.getall()}")
                pass
        
        return data
def scrapy_parse_bing(html_):
    selector = Selector(text=html_)
    data = []
    retry_ = False
    # Check
    if "There are no results for" in html_:
        # print(f"RETRYRETRYRETRYRETRY: There are no results")
        retry_ = True
    else:
        # #  write sample data
        # with open("google.html", "w", encoding="utf8") as f:
        #     f.write(html_)

        # parse
        for content in selector.xpath('//ol/li'):
            try:
                title = content.xpath('h2').xpath("string()").get()
                link = content.xpath('h2/a').attrib['href']
                # https://translate.google.com/website?sl=auto&tl=en&hl=en&u=https://meri.edu.in/meri/recruiters/mba-placement-campus-interview-of-hbl-global-a-division-hdb-financial-services-ltd/
                if "translate.google.com" in link:
                    link = link.replace("https://translate.google.com/website?sl=auto&tl=en&hl=en&u=", "").strip()
                description = content.xpath('div/p').xpath("string()").get()
                extracted_content = {
                    'title': title,
                    'url': link,
                    'description': description,
                }
                data.append(extracted_content)
            except Exception as e:
                # print(f"EEEEEEEEEEEEEEEE: {e} - content: {content.getall()}")
                pass
        
    return data