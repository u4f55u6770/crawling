# -*- coding: utf-8 -*- 
# @Time : 2022/2/21 14:34 
# @Author : u4f55u6770 
# @contact: hejie@skyroam.com
import requests
from bs4 import BeautifulSoup
from registration.app_main import read_blad
from exports import export_excel


def capture(condition: str):
    data = []

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/51.0.2704.63 Safari/537.36'}
    login_url = "https://eatsafe.nzfsa.govt.nz/web/public/acvm-register"
    login_response = requests.post(url=login_url, headers=headers)
    url = "https://eatsafe.nzfsa.govt.nz/web/public/acvm-register?p_p_id=searchAcvm_WAR_aaol&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-2&p_p_col_count=1&_searchAcvm_WAR_aaol_action=search"
    filter_url_data = {'active': condition}
    filter_response = requests.post(url=url, data=filter_url_data, headers=headers, cookies=login_response.cookies)
    soup = BeautifulSoup(filter_response.text, 'lxml')
    all_topics = soup.select('#row > tbody > tr')
    print(condition, "抓取的数据：", len(all_topics))
    row = 1
    for i in all_topics:
        td_text = [td.text.strip() for td in i.find_all("td")]
        # 详情页面
        link_arr = soup.select(f'#row > tbody > tr:nth-child({row}) > td.actionCell > a')
        detail_url = link_arr[0]['href']
        # print(td_text)
        obj = {'Registration Number': td_text[0], 'Trade Name': td_text[1],
               'Date of Registration': td_text[2], 'Registrant': td_text[3],
               'detail': []}

        # print(detail_url)
        detail_response = requests.get(url=detail_url, cookies=login_response.cookies)
        # print(detail_response.text)
        detail_soup = BeautifulSoup(detail_response.text, 'lxml')
        detail_all = detail_soup.select('.documentTable tr')
        print(td_text[0], "详情提取：", len(detail_all) - 1)
        for j in range(1, len(detail_all)):
            detail = [td.text.strip() for td in detail_all[j].find_all("td")]
            # print(detail)
            obj['detail'].append({'content': detail[1], 'unit': detail[2]})
        data.append(obj)
        row += 1
    return data


def main():
    conditions = read_blad()

    for condition in conditions:
        data = capture(condition)
        export_list = []
        for r in data:
            v = {'Registration Number': r['Registration Number'], 'Trade Name': r['Trade Name'],
                 'Date of Registration': r['Date of Registration'], 'Registrant': r['Registrant']}
            for d in r.get('detail'):
                v['content'] = d['content']
                v['unit'] = d['unit']
            export_list.append(v)

        if len(export_list) > 0:
            columns = ['Registration Number', 'Trade Name', 'Date of Registration', 'Registrant', 'content', 'unit']
            file_name = f"new_zealand_{condition}.xlsx"
            export_excel(file_name,
                         data=export_list,
                         columns=columns,
                         encoding="utf-8-sig",
                         header=True,
                         index=False)

        print("===========>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")


if __name__ == '__main__':
    main()
