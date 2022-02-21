# -*- encoding:utf-8 -*-
# Author : CHEN Yingpei  
# Email  : yingpei.chen@skyroam.com
import io
import os
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import xlsxwriter

base_dir = os.path.dirname(os.path.abspath(__file__))


def export_excel(filename, data: list or dict, columns: list, **kwargs):
    """导出excel文件"""
    df = pd.DataFrame(data=data, columns=columns)

    file_path = os.path.join(os.path.join(base_dir, "export_files"), filename)
    df.to_excel(file_path, **kwargs)

    print(f"===== Finished in saving Excel file: {file_path} =====")


def export_multiple_sheet_excel(filename, data: List[dict], specific_dir: str = None, **kwargs):
    """
    导出多个 sheet 的数据，data数据中包含每一个 sheet 的数据，
    需要有 sheet 的内容，sheet的 columns，sheet的名称
    格式为：
        [
            {"sheet_name": "xx..", "columns": [x, ...], "data":[[x], [x]...]},
            {...},
        ]
    """
    file_path = os.path.join(os.path.join(base_dir, "export_files"), filename)
    with pd.ExcelWriter(file_path) as writer:
        for index, d in enumerate(data):
            sheet_name = d.get("sheet_name", f"sheet{index}")
            sheet_columns = d.get("columns")
            sheet_data = d.get("data")
            df = pd.DataFrame(data=sheet_data, columns=sheet_columns)
            df.to_excel(writer, sheet_name=sheet_name, **kwargs)

    print(f"===== Finished in saving Excel file: {file_path} =====")


def export_excel_and_summary(filename, data: list or dict, columns: list, **kwargs):
    """导出excel文件，数据会在最底下做汇总"""
    df1 = pd.DataFrame(data=data, columns=columns)

    s = df1.sum()

    total_data = list()
    for column in columns:
        if column == "共享组卡池ID":
            total_data.append("Total")
        else:
            total_data.append(s[column])

    df2 = pd.DataFrame(data=[total_data], columns=columns)
    res_df = pd.concat([df1, df2])

    file_path = os.path.join(os.path.join(base_dir, "export_files"), filename)
    res_df.to_excel(file_path, **kwargs)

    print(f"===== Finished in saving Excel file: {file_path} =====")


def export_excel_sort(filename, data: list or dict, columns: list,
                      sort_columns: list, sort_type: str = "ASC", **kwargs):
    """导出excel文件，并对某个字段进行排序"""
    df = pd.DataFrame(data=data, columns=columns)
    if sort_type == "ASC":
        # sort ascending
        flag = True
    elif sort_type == "DES":
        # sort descending
        flag = False
    else:
        raise ValueError("Wrong sorting type")

    sorted_df = df.sort_values(by=sort_columns, ascending=flag)

    file_path = os.path.join(os.path.join(base_dir, "export_files"), filename)
    sorted_df.to_excel(file_path, **kwargs)

    print(f"===== Finished in saving Excel file: {file_path} =====")


def export_html(data: list or dict, columns: list, sort_columns: list, ascending: list, **kwargs):
    """将数据导出成 html 格式，用于发送邮件"""

    df = pd.DataFrame(data=data, columns=columns)
    sorted_df = df.sort_values(by=sort_columns, ascending=ascending)

    return sorted_df.to_html(**kwargs)


def export_html_roaming_flow(data: list or dict, columns: list, sort_columns: list, ascending: list, **kwargs):
    """将数据导出成 html 格式，用于发送邮件"""

    df = pd.DataFrame(data=data, columns=columns)
    sorted_df = df.sort_values(by=sort_columns, ascending=ascending)

    df1 = sorted_df[sorted_df.指标 == "流量(GB)"]
    df2 = pd.DataFrame(data=[["   -", "", "", "", "", "", "", "", ""]], columns=columns)  # 插入一行空数据做分割
    df3 = sorted_df[sorted_df.指标 == "成本(USD)"]
    frames = [df1, df2, df3]
    new_df = pd.concat(frames)

    return new_df.to_html(**kwargs)


def write_excel_stream(data: list or dict, columns: list, sort_columns: list, sort_type: str = "ASC", **kwargs):
    """将数据导出成 stream 格式用于发送邮件附件"""
    if sort_type == "ASC":
        # ascending
        flag = True
    elif sort_type == "DES":
        # descending
        flag = False
    else:
        raise ValueError("Wrong sorting type")
    df = pd.DataFrame(data=data, columns=columns)
    bio = io.BytesIO()
    # By setting the 'engine' in the ExcelWriter constructor.
    writer = pd.ExcelWriter(bio, engine='xlsxwriter')
    if sort_columns:
        sorted_df = df.sort_values(by=sort_columns, ascending=flag)
        sorted_df.to_excel(writer, **kwargs)
    else:
        df.to_excel(writer, **kwargs)

    # Save the workbook
    writer.save()

    bio.seek(0)
    workbook = bio.read()
    return workbook


def merge_and_writer_stream(df: pd.DataFrame, merge_cols: list = None):
    """按行合并同种数据的单元格"""
    rows_count = df.index.size
    print(f"数据行共有: {rows_count}行")

    cols = list(df.columns.values)

    if not all([m in cols for m in merge_cols]):
        print("`merge_cols` includes columns that are not in `df`'s columns")
        return
    out = io.BytesIO()
    workbook = xlsxwriter.Workbook(out)
    worksheet = workbook.add_worksheet()
    format_headers = workbook.add_format({'border': 1, 'bold': True, 'align': 'center',
                                          'valign': 'vcenter', 'fg_color': '#4CBC87'})
    format_content = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})

    # writing headers
    for i, col in enumerate(cols):
        worksheet.write(0, i, col, format_headers)

    groups = df.groupby(by=merge_cols)
    row_record = 1
    for group in groups:
        group_df = group[1]
        group_num = group[1].values.shape[0]

        if group_num == 1:
            # if the records of a group equal to 1, just add it to the chart
            for col_num in range(len(cols)):
                worksheet.write(row_record, col_num, group_df.iloc[0, col_num], format_content)
            row_record += group_num
            continue

        # groups that have more than one records
        for row_num in range(row_record, row_record + group_num):
            for col in cols:
                col_num = cols.index(col)
                if col in merge_cols:

                    if row_num == row_record:
                        # merge the data
                        worksheet.merge_range(row_record, col_num, row_record + group_num - 1, col_num,
                                              group_df.iloc[row_num - row_record, col_num], format_content)
                else:
                    worksheet.write(row_num, col_num, group_df.iloc[row_num - row_record, col_num], format_content)

        row_record += group_num

    workbook.close()
    out.seek(0)
    return out.read()


def draw_chart(data, columns, filename):
    """将数据画出一个图表"""
    df = pd.DataFrame(data=data, columns=columns)

    max_flow_index = df['Flow Usage(GB)'].idxmax()
    min_flow_index = df['Flow Usage(GB)'].idxmin()
    max_cost_index = df['Cost(USD)'].idxmax()
    min_cost_index = df['Cost(USD)'].idxmin()

    max_flow = float(df.iloc[max_flow_index]['Flow Usage(GB)'])
    min_flow = float(df.iloc[min_flow_index]['Flow Usage(GB)'])
    max_cost = float(df.iloc[max_cost_index]['Cost(USD)'])
    min_cost = float(df.iloc[min_cost_index]['Cost(USD)'])

    print(f"IN DataFrame: MAX_FLOW: {max_flow}, MIN_COST: {max_cost}")
    print(f"IN DataFrame: MIN_FLOW: {min_flow}, MIN_COST: {min_cost}")
    plt.figure(figsize=(16, 20), )

    ax = df.plot(x="Date",
                 y=["Cost(USD)", "Flow Usage(GB)"],
                 secondary_y=["Flow Usage(GB)"],
                 title="Roaming Card Flow Usage and Cost Summary",
                 figsize=(16, 9),
                 grid=True,
                 style='.-',
                 color=["darkred", "steelblue"])
    ax.set_ylabel("Cost(USD)")
    ax.set_ylim(0, max_cost * 1.2)
    ax.right_ax.set_ylabel("Flow Usage(GB)")
    ax.right_ax.set_ylim(0, max_flow * 1.2)

    path = os.path.join(os.path.join(base_dir, "export_files"), filename)
    plt.savefig(path)


def draw_one_bar_chart(data, x_label, y_label, filename):
    """生成柱状图"""
    df = pd.DataFrame([[k, v] for k, v in data.items()], columns=[x_label, y_label])
    plt.figure()

    ax = df.plot(x=x_label,
                 y=y_label,
                 kind="bar",
                 title="Non-package Product Daily Cost",
                 figsize=(16, 9),
                 fontsize=10,
                 xticks=list(data.values()),
                 grid=False,
                 color=["LightBlue"])

    ax.set_ylabel(y_label)

    ax.legend(loc="upper left")
    plt.xticks(rotation=0)

    path = os.path.join(os.path.join(base_dir, "export_files"), filename)
    plt.savefig(path)
