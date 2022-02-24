# -*- coding: utf-8 -*- 
# @Time : 2022/2/21 16:10 
# @Author : u4f55u6770 
# @contact: hejie@skyroam.com
import requests
from urllib import request


if __name__ == '__main__':
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/51.0.2704.63 Safari/537.36'}
    login_url = "http://npirspublic.ceris.purdue.edu/ppis/default.aspx"
    login_response = requests.get(url=login_url, headers=headers)
    url = "http://npirspublic.ceris.purdue.edu/ppis/chemical.aspx"
    filter_url_data = {'ctl00$ContentPlaceHolder1$TextBoxInput2': 'Cyfluthrin',
                       '__VIEWSTATE': '/wEPDwULLTIxMjQxMDI1NjIPZBYCZg9kFgICAw9kFgQCEQ8PFgIeBFRleHQFBDIwMjJkZAITDw8WAh8ABQQyMDIyZGQYAgUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgYFHWN0bDAwJENvbnRlbnRQbGFjZUhvbGRlcjEkRVBBBSFjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJHByb2R1Y3QFIWN0bDAwJENvbnRlbnRQbGFjZUhvbGRlcjEkcHJvZHVjdAUhY3RsMDAkQ29udGVudFBsYWNlSG9sZGVyMSRjb21wYW55BSFjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJGNvbXBhbnkFIGN0bDAwJENvbnRlbnRQbGFjZUhvbGRlcjEkYWN0aXZlBSRjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJE11bHRpVmlldzEPD2RmZNOMi1sLWrkfmSGUlTHv+7ZvxrQ3gGz/BVLuo2biImVj',
                        '__EVENTVALIDATION': '/wEWCwK4o8ejCwKkxNeECwLc3uCnBALc3tSnBAKO2t3XAgKYg5zrAQKcy4bBBwLs25fOAwLNhbjDCwKboL6OBQKgpqHxCYqmcp6hgO1q5kG9Hn3i4NiAneEq5gBEMigTs6pf5fjy',
                       '__VIEWSTATEGENERATOR': '3FFEBF03'
                       }
    filter_response = requests.post(url=url, data=filter_url_data, headers=headers, cookies=login_response.cookies, allow_redirects=False)
    # print(filter_response.history[0].text)
    print(filter_response.text)

    cookie_hdr = request.HTTPCookieProcessor()
    opener = request.build_opener(cookie_hdr)
    req = request.Request(url)
    with opener.open(req) as f:
        # bla...bla...bla
        page_data = f.read()
        print(page_data)
