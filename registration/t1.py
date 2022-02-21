# -*- coding: utf-8 -*- 
# @Time : 2022/2/18 13:53 
# @Author : u4f55u6770 
# @contact: hejie@skyroam.com
import requests
from bs4 import BeautifulSoup

url_str = "https://portal.apvma.gov.au/pubcris?p_auth=W6OhzEUH&p_p_id=pubcrisportlet_WAR_pubcrisportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=2&p_p_col_count=4&_pubcrisportlet_WAR_pubcrisportlet_javax.portlet.action=search"
# url_str = "https://portal.apvma.gov.au/pubcris?p_auth=W6OhzEUH&p_p_id=pubcrisportlet_WAR_pubcrisportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=2&p_p_col_count=4&_pubcrisportlet_WAR_pubcrisportlet_javax.portlet.action=navigate&_pubcrisportlet_WAR_pubcrisportlet_delta=75&_pubcrisportlet_WAR_pubcrisportlet_keywords=&_pubcrisportlet_WAR_pubcrisportlet_advancedSearch=false&_pubcrisportlet_WAR_pubcrisportlet_andOperator=true&_pubcrisportlet_WAR_pubcrisportlet_orderByCol=code&_pubcrisportlet_WAR_pubcrisportlet_orderByType=desc&_pubcrisportlet_WAR_pubcrisportlet_resetCur=false&cur=2"
# url_str = "https://portal.apvma.gov.au/pubcris?p_auth=W6OhzEUH&p_p_id=pubcrisportlet_WAR_pubcrisportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=2&p_p_col_count=4&_pubcrisportlet_WAR_pubcrisportlet_javax.portlet.action=navigate&_pubcrisportlet_WAR_pubcrisportlet_delta=75&_pubcrisportlet_WAR_pubcrisportlet_keywords=&_pubcrisportlet_WAR_pubcrisportlet_advancedSearch=false&_pubcrisportlet_WAR_pubcrisportlet_andOperator=true&_pubcrisportlet_WAR_pubcrisportlet_orderByCol=code&_pubcrisportlet_WAR_pubcrisportlet_orderByType=desc&_pubcrisportlet_WAR_pubcrisportlet_resetCur=false&cur=3"
# url_str = "https://portal.apvma.gov.au/pubcris?p_auth=W6OhzEUH&p_p_id=pubcrisportlet_WAR_pubcrisportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=2&p_p_col_count=4&_pubcrisportlet_WAR_pubcrisportlet_javax.portlet.action=navigate&_pubcrisportlet_WAR_pubcrisportlet_delta=75&_pubcrisportlet_WAR_pubcrisportlet_keywords=&_pubcrisportlet_WAR_pubcrisportlet_advancedSearch=false&_pubcrisportlet_WAR_pubcrisportlet_andOperator=true&_pubcrisportlet_WAR_pubcrisportlet_orderByCol=code&_pubcrisportlet_WAR_pubcrisportlet_orderByType=desc&_pubcrisportlet_WAR_pubcrisportlet_resetCur=false&cur=4"
if __name__ == '__main__':

    # 获取翻页的数据

    # 进入到详情

    # 获取计量

    r = requests.post(url_str)
    # print(r.text)
    soup = BeautifulSoup(r.text, 'lxml')
    # print(soup)
    # all_topics = soup.find_all(['td'])
    all_topics = soup.select('.results-row > td > a')
    # No, Name, Product type, Status, Actives 内容

    # 对应的 Amount 和 Units
    for i in range(0, len(all_topics)):

        if i % 2 == 0:
            print("药品:", all_topics[i+1].get_text())

            d = all_topics[i]['href']

            # print(d)
            r2 = requests.get(d)
            soup2 = BeautifulSoup(r2.text, 'html.parser')
            # #_pubcrisportlet_WAR_pubcrisportlet_docsContent > div:nth-child(2) > fieldset > table > tbody > tr.results-row > td:nth-child(1)
            all_topics2 = soup2.select(
                '#_pubcrisportlet_WAR_pubcrisportlet_docsContent > div:nth-child(2) > fieldset > table td')
            # print(all_topics2)
            for index in range(0, len(all_topics2)):
                if index % 5 == 0:
                    print(all_topics2[index - 5].get_text(), all_topics2[index - 4].get_text(),
                          all_topics2[index - 3].get_text(), all_topics2[index - 2].get_text(),
                          all_topics2[index - 1].get_text())
            print('\n')


detail_url = all_topics[index]['href']  # 获取明细数据地址
            # print(condition, detail_url)
            detail_response = requests.get(detail_url)
            detail_soup = BeautifulSoup(detail_response.text, 'lxml')
            all_topics2 = detail_soup.select(
                '#_pubcrisportlet_WAR_pubcrisportlet_docsContent > div:nth-child(2) > fieldset > table td')

            if index % 2 == 0:




                # columns = ['Active ingredient name', 'No', 'Name', 'Product type', 'Status',
                #            'Actives', 'Constituent name', 'Amount', 'Units']
                for i in range(0, len(all_topics2)):
                    if i % 5 == 0 and i != 0:
                        export_list.append({'Active ingredient name': condition, 'No': all_topics[index].get_text(),
                                            'Name': all_topics[index + 1].get_text(), 'Product type': product_type,
                                            'Status': status, 'Actives': actives,
                                            'Constituent name': all_topics2[i - 5].get_text(),
                                            'Amount': all_topics2[i - 2].get_text(),
                                            'Units': all_topics2[i - 1].get_text()})
                row += 1



print(condition, export_list)
        columns = ['Active ingredient name', 'No', 'Name', 'Product type', 'Status',
                   'Actives', 'Constituent name', 'Amount', 'Units']
        export_excel(f"{condition}.xlsx",
                     data=export_list,
                     columns=columns,
                     encoding="utf-8-sig",
                     header=True,
                     index=False)