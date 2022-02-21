# -*- coding: utf-8 -*- 
# @Time : 2022/2/18 18:21 
# @Author : u4f55u6770 
# @contact: hejie@skyroam.com
import xlrd
import requests
import xlsxwriter
import json
from bs4 import BeautifulSoup
from exports import merge_and_writer_stream, export_excel
import datetime
import re
import os
base_dir = os.path.dirname(os.path.abspath(__file__))


def read_blad():
    """
        读取需要查询的数据源
    :return:
    """
    workbook = xlrd.open_workbook('./ingredient/Active ingredient.xlsx')
    sheet = workbook.sheet_by_name('Sheet1 (2)')
    return [sheet.row_values(i)[0] for i in range(1, sheet.nrows)]


def capture(condition: str, urls: list, url_index: int):
    data = []

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/51.0.2704.63 Safari/537.36'}

    filter_url_data = {'keywords': condition}
    if url_index > 0:
        filter_response = requests.get(url=urls[url_index], data=filter_url_data, headers=headers)
    else:
        filter_response = requests.post(url=urls[url_index], data=filter_url_data, headers=headers)
    soup = BeautifulSoup(filter_response.text, 'lxml')
    all_topics = soup.select('.search-results table tr')

    # 获取数据总数
    # h3_arr = soup.select(f'#p_p_id_pubcrisportlet_WAR_pubcrisportlet_ > div > div > div > h3')
    h3_arr = soup.select(
        f'#_pubcrisportlet_WAR_pubcrisportlet_productSearchResultsSearchContainerPageIteratorTop > div.search-results')
    h3 = h3_arr[0].get_text() if h3_arr and len(h3_arr) > 0 else ''
    page_arr = re.findall(r'\d+', h3)
    print("page_arr", page_arr)
    if page_arr and len(page_arr) >= 3:
        total = page_arr[2]
    elif page_arr and len(page_arr) > 0:
        total = page_arr[0]
    else:
        total = 0
    grab = len(all_topics) - 2
    print("条件：", condition, "抓取数：", grab, '总数：', total)

    row = 1
    for index in range(2, len(all_topics)):
        # No
        no_arr = soup.select(
            f'#_pubcrisportlet_WAR_pubcrisportlet_productSearchResultsSearchContainer_col-no_row-{row}')
        no = no_arr[0].get_text() if no_arr and len(no_arr) > 0 else ''

        # name
        name_arr = soup.select(
            f'#_pubcrisportlet_WAR_pubcrisportlet_productSearchResultsSearchContainer_col-name_row-{row}')
        name = name_arr[0].get_text() if name_arr and len(name_arr) > 0 else ''

        # 获取类型
        product_type_arr = soup.select(
            f'#_pubcrisportlet_WAR_pubcrisportlet_productSearchResultsSearchContainer_col-product-type_row-{row}')
        product_type = product_type_arr[0].get_text() if product_type_arr and len(product_type_arr) > 0 else ''

        # 获取状态
        status_arr = soup.select(
            f'#_pubcrisportlet_WAR_pubcrisportlet_productSearchResultsSearchContainer_col-status_row-{row}')
        status = status_arr[0].get_text() if status_arr and len(status_arr) > 0 else ''

        # 获取状态
        actives_arr = soup.select(
            f'#_pubcrisportlet_WAR_pubcrisportlet_productSearchResultsSearchContainer_col-actives_row-{row}')
        actives = actives_arr[0].get_text() if actives_arr and len(actives_arr) > 0 else ''

        export_obj = {'Active ingredient name': condition, 'No': no,
                      'Name': name, 'Product type': product_type,
                      'Status': status, 'Actives': actives, 'constituents': []}
        # print("no: ", no)
        # 获取调整页面
        link_arr = soup.select(
            f'#_pubcrisportlet_WAR_pubcrisportlet_productSearchResultsSearchContainer_col-no_row-{row} > a')
        if link_arr and len(link_arr) > 0:
            detail_url = link_arr[0]['href']
            # print("url: ", detail_url)
            detail_response = requests.get(detail_url)
            detail_soup = BeautifulSoup(detail_response.text, 'lxml')

            all_topics2 = detail_soup.select(
                '#_pubcrisportlet_WAR_pubcrisportlet_docsContent > div:nth-child(2) > fieldset > table tr')
            print("No:", no, " Constituents:", len(all_topics2) - 1)
            for i in all_topics2:
                td_text = [td.text.strip() for td in i.find_all("td")]
                if len(td_text) == 0:
                    continue
                constituent = {'constituent_name': td_text[0], 'amount': td_text[3], 'units': td_text[4]}
                # print("constituent: ", constituent)
                export_obj['constituents'].append(constituent)

        data.append(export_obj)

        row += 1

    # 取第二页
    if url_index == 0 and int(grab) < int(total):
        print("条件：", condition, "开始抓第二页>>>>>>>>>>>>>>>")
        data += capture(condition, urls, 1)

    return data


def main():
    conditions = read_blad()  # 获取条件
    filter_url = ("https://portal.apvma.gov.au/pubcris?p_auth=W6OhzEUH&p_p_id=pubcrisportlet_WAR_pubcrisportlet&"
                  "p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=2&"
                  "p_p_col_count=4&_pubcrisportlet_WAR_pubcrisportlet_javax.portlet.action=search&"
                  "_pubcrisportlet_WAR_pubcrisportlet_delta=100")
    next_url = (
        "https://portal.apvma.gov.au/pubcris?p_auth=2qWBYMH2&p_p_id=pubcrisportlet_WAR_pubcrisportlet&p_p_lifecycle=1&"
        "p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_pos=2&p_p_col_count=4&"
        "_pubcrisportlet_WAR_pubcrisportlet_javax.portlet.action=navigate&_pubcrisportlet_WAR_pubcrisportlet_delta=75&"
        "_pubcrisportlet_WAR_pubcrisportlet_keywords=&_pubcrisportlet_WAR_pubcrisportlet_advancedSearch=false&"
        "_pubcrisportlet_WAR_pubcrisportlet_andOperator=true&_pubcrisportlet_WAR_pubcrisportlet_orderByCol=code&"
        "_pubcrisportlet_WAR_pubcrisportlet_orderByType=desc&_pubcrisportlet_WAR_pubcrisportlet_resetCur=false&cur=2")

    urls = [filter_url, next_url]
    source_xls = []
    conditions = ['Brodifacoum', 'Bromadiolone']  # Brodifacoum Bromadiolone
    for condition in conditions:
        export_list = []
        data = capture(condition, urls, 0)

        # 清洗数据
        for r in data:
            v = {'Active ingredient name': r.get('Active ingredient name'), 'No': r.get('No'),
                 'Name': r.get('Name'), 'Product type': r.get('Product type'),
                 'Status': r.get('Status'), 'Actives': r.get('Actives')}
            for d in r.get('constituents'):
                v['Constituent name'] = d['constituent_name']
                v['Amount'] = d['amount']
                v['Units'] = d['units']
            export_list.append(v)

        columns = ['Active ingredient name', 'No', 'Name', 'Product type', 'Status',
                   'Actives', 'Constituent name', 'Amount', 'Units']
        file_name = f"Australia_{condition}.xlsx"
        source_xls.append(os.path.join(os.path.join(base_dir, "export_files"), file_name))
        export_excel(file_name,
                     data=export_list,
                     columns=columns,
                     encoding="utf-8-sig",
                     header=True,
                     index=False)

        print("===========>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

    # 合并excel
    target_xls = "Australia_Data.xlsx"
    data = []
    for i in source_xls:
        wb = xlrd.open_workbook(i)
        for sheet in wb.sheets():
            for rownum in range(sheet.nrows):
                data.append(sheet.row_values(rownum))
    workbook = xlsxwriter.Workbook(target_xls)
    worksheet = workbook.add_worksheet()
    font = workbook.add_format({"font_size": 14})
    for i in range(len(data)):
        for j in range(len(data[i])):
            worksheet.write(i, j, data[i][j], font)
    workbook.close()


if __name__ == '__main__':
    main()
