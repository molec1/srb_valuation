import requests
import re
import time
import pandas as pd
import datetime
import os
import html

def get_links(path, link, pattern):
    old_links = seen_links(path)

    links_file_name = path+'/links/links_'+str(datetime.datetime.now().date())+'.txt'
    for i in range(99):
        print(i)
        page = requests.get(link+str(i+1))
        #page = requests.get('https://www.4zida.rs/prodaja-stanova/beograd?strana='+str(i+1))
        p = page.content
        #get all links to offers
        links = re.findall(pattern, str(p))
        if len(links)==0:
            break
        links = [x for x in links if x not in old_links]
        links = [x for x in links if '"' not in x]
        print(links)
        if len(links)>0:
            #store them to the file with links
            file = open(links_file_name, 'a')
            for item in links:
                file.write(item+"\n")
            file.close()
            time.sleep(1)
        else:
            #print('no new links')
            if i>10:
                print('no new links')  # break


def seen_links(path):
    old_links = []
    for f in os.listdir(path+'/links'):
        file = open(path+'/links/' + f, 'r')
        links = file.read().split()
        file.close()
        old_links = old_links + links
    old_links = list(set(old_links))
    return old_links

def scraped_links(path):
    old_links = []
    for f in os.listdir(path+'/scraped'):
        df = pd.read_csv(path+'/scraped/' + f)
        if 'link' in df.columns:
            links = list(df.link)
        else:
            links = []
        old_links = old_links + links
    old_links = list(set(old_links))
    return old_links


def get_pages(path):
    links = seen_links(path)
    old_links = scraped_links(path)
    print(len(links))
    links = [x for x in links if x not in old_links]
    links = links[:-1]
    print(len(links))
    scraped = []
    for l in links[:2000]:
        try:
            ret = {'link': l}
            print(l)
            page = requests.get(l)
            p = html.unescape(page.content.decode('utf-8'))
            # print(p)
            items = re.findall(r"\"label\">([\w\s\d\\\&\#;]+):<\/div><strong _ngcontent-ng-c\d+ class=\"value \w+-\w+ \w+-\w+\">([\w\d\s\\\/., \(\)\&\#;]+)\s?", p)
            for item in items:
                ret[item[0]] = item[1]
            price = re.findall(r"class=\"label\">Cena:<\/div><div _ngcontent-ng-c\d+ class=\"value\"><strong _ngcontent-ng-c\d+>([\d\(.\d)?]+)", p)
            if len(price)>0:
                ret['price'] = price[0]
            address = re.findall(r"<app-place-info _ngcontent-ng-c\d+ _nghost-ng-c\d+ ngh=\"0\"><div _ngcontent-ng-c\d+ class=\"flex flex-col\"><strong _ngcontent-ng-c\d+ class=\"font-semibold\">(.+)<\/strong><span _ngcontent-ng-c\d+>(.+)<\/span><\/div><\/app-place-info>", p)
            if len(address)>0:
                if len(address[0]) > 0:
                    ret['street'] = address[0][0]
                if len(address[0]) > 1:
                    ret['address'] = address[0][1]
            description = re.findall(r"class=\"ed-description collapsed-description ng-star-inserted\">(.+)<\/pre>", p)
            if len(description)>0:
                ret['description'] = description[0]
            else:
            	description = re.findall(r"class=\"mt-4\">(.+)<\/p>", p)
            	if len(description)>0:
                    ret['description'] = description[0]
            title = re.findall(r"<title>(.+)<\/title>", p)
            ret['title'] = title[0]
            ret['end_date'] = datetime.datetime.now().date()
            # print(ret)
            scraped.append(ret)
        except Exception as e:
            print('err', repr(e))
        time.sleep(1.5)

    df = pd.DataFrame.from_dict(scraped)
    scraped_file_name = path+'/scraped/scraped_'+str(datetime.datetime.now().date())+'.csv'
    if os.path.exists(scraped_file_name):
        scraped_file_name = path+'/scraped/scraped_'+str(datetime.datetime.now().date())+'_'+str(datetime.datetime.now().time())+'.csv'
    df.to_csv(scraped_file_name)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #land
    #get links

    path = '4zida/land/sale'
    links = ['https://www.4zida.rs/prodaja-placeva?jeftinije_od=20000eur&struktura=gradjevinsko-zemljiste&strana=',
             'https://www.4zida.rs/prodaja-placeva?skuplje_od=20000eur&jeftinije_od=40000eur&struktura=gradjevinsko-zemljiste&strana=',
             'https://www.4zida.rs/prodaja-placeva?skuplje_od=40000eur&jeftinije_od=80000eur&struktura=gradjevinsko-zemljiste&strana=',
             'https://www.4zida.rs/prodaja-placeva?skuplje_od=80000eur&jeftinije_od=130000eur&struktura=gradjevinsko-zemljiste&strana=',
             'https://www.4zida.rs/prodaja-placeva?skuplje_od=130000eureur&struktura=gradjevinsko-zemljiste&strana=',
             ]
    pattern = r"https:\/\/www.4zida.rs\/prodaja-placeva\/[^/]+\/[^/]+\/[^/\"]+"
    for link in links:
        get_links(path, link, pattern)
    #get pages
    get_pages(path)
    #rent
    #get links

    path = '4zida/apartments/rent'
    links = ['https://www.4zida.rs/izdavanje-stanova?skuplje_od=100eur&jeftinije_od=200eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=200eur&jeftinije_od=300eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=300eur&jeftinije_od=350eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=350eur&jeftinije_od=400eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=400eur&jeftinije_od=450eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=450eur&jeftinije_od=500eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=500eur&jeftinije_od=550eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=550eur&jeftinije_od=600eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=600eur&jeftinije_od=650eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=650eur&jeftinije_od=700eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=700eur&jeftinije_od=750eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=750eur&jeftinije_od=800eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=800eur&jeftinije_od=900eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=900eur&jeftinije_od=1000eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=1000eur&jeftinije_od=1500eur&strana=',
             'https://www.4zida.rs/izdavanje-stanova?skuplje_od=1500eur&jeftinije_od=10000eur&strana=',
             ]
    link = 'https://www.4zida.rs/izdavanje-stanova?jeftinije_od=10000eur&strana='
    pattern = r"https:\/\/www.4zida.rs\/izdavanje-stanova\/[^/]+\/[^/]+\/[^/\"]+"
    for link in links:
        get_links(path, link, pattern)
    #get pages
    get_pages(path)

    #sale
    #get links
    path = '4zida/apartments/sale'
    links = ['https://www.4zida.rs/prodaja-stanova?skuplje_od=10000eur&jeftinije_od=50000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=50000eur&jeftinije_od=60000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=60000eur&jeftinije_od=65000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=65000eur&jeftinije_od=70000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=70000eur&jeftinije_od=75000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=75000eur&jeftinije_od=80000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=80000eur&jeftinije_od=85000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=85000eur&jeftinije_od=90000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=90000eur&jeftinije_od=95000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=95000eur&jeftinije_od=100000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=100000eur&jeftinije_od=105000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=105000eur&jeftinije_od=110000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=110000eur&jeftinije_od=115000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=115000eur&jeftinije_od=120000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=120000eur&jeftinije_od=125000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=125000eur&jeftinije_od=130000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=130000eur&jeftinije_od=140000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=140000eur&jeftinije_od=150000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=150000eur&jeftinije_od=160000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=160000eur&jeftinije_od=180000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=180000eur&jeftinije_od=200000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=200000eur&jeftinije_od=220000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=220000eur&jeftinije_od=240000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=240000eur&jeftinije_od=270000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=270000eur&jeftinije_od=300000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=300000eur&jeftinije_od=400000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=400000eur&jeftinije_od=500000eur&strana=',
             'https://www.4zida.rs/prodaja-stanova?skuplje_od=500000eur&strana=',
             ]
    link = 'https://www.4zida.rs/prodaja-stanova?skuplje_od=10000eur&strana='
    pattern = r"https:\/\/www.4zida.rs\/prodaja-stanova\/[^/]+\/[^/]+\/[^/\"]+"
    for link in links:
        get_links(path, link, pattern)
    #get pages
    get_pages(path)

    #houses
    #get links

    path = '4zida/houses/sale'
    links = ['https://www.4zida.rs/prodaja-kuca?skuplje_od=10000eur&jeftinije_od=25000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=25000eur&jeftinije_od=50000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=50000eur&jeftinije_od=60000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=60000eur&jeftinije_od=65000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=65000eur&jeftinije_od=70000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=70000eur&jeftinije_od=75000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=75000eur&jeftinije_od=80000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=80000eur&jeftinije_od=85000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=85000eur&jeftinije_od=90000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=90000eur&jeftinije_od=95000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=95000eur&jeftinije_od=100000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=100000eur&jeftinije_od=105000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=105000eur&jeftinije_od=110000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=110000eur&jeftinije_od=115000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=115000eur&jeftinije_od=120000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=120000eur&jeftinije_od=125000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=125000eur&jeftinije_od=130000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=130000eur&jeftinije_od=140000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=140000eur&jeftinije_od=150000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=150000eur&jeftinije_od=160000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=160000eur&jeftinije_od=180000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=180000eur&jeftinije_od=200000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=200000eur&jeftinije_od=240000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=240000eur&jeftinije_od=300000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=300000eur&jeftinije_od=500000eur&strana=',
             'https://www.4zida.rs/prodaja-kuca?skuplje_od=500000eur&strana=',
             ]
    pattern = r"https:\/\/www.4zida.rs\/prodaja-kuca\/[^/]+\/[^/]+\/[^/\"]+"
    for link in links:
        get_links(path, link, pattern)
    #get pages
    get_pages(path)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
