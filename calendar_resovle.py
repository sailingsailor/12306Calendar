import poplib
import datetime
import os
import re
import pytz
import requests
import pandas as pd
from datetime import datetime

class CalendarResolve:
    def generate_calendar_model(self, mail):
        order_info = mail['order_info']
        train_from_to = re.search(r'\uFF0C([\u4e00-\u9fa5]{2,10}-[\u4e00-\u9fa5]{2,10})\uFF0C', order_info).group(1)
        # 提取发站和到站
        pattern_stations = r"([\u4e00-\u9fa5]+站)-([\u4e00-\u9fa5]+站)"
        stations = re.search(pattern_stations, order_info)
        start_station = stations.group(1)
        end_station = stations.group(2)
        train_number = self.__train_number_text(order_info)
        train_seat_number = self.__train_seat_number(order_info)
        train_date_text = self.__train_date_text(order_info)
        train_time_text = self.__train_time_text(train_date_text)
        calendar_start = self.__train_datetime(train_date_text)
        calendar_title = train_from_to.replace('站', '') + ' ' + train_time_text + ' ' + train_number + ' ' + train_seat_number
        calendar_description = mail['order_id'] + '，' + self.__order_type_text(mail['order_type']) + '，' + order_info
        # Function to extract arrival time
        url = f"http://touch.qunar.com/h5/train/trainStaChoose?trainNum={train_number}"
        content = requests.get(url).text
        # Use pandas to parse the HTML table
        df = pd.read_html(content)[0]
        # Filter the DataFrame to get the desired time
        filtered_df = df[df["车站"].str.contains(end_station)]
        if not filtered_df.empty:
            arrival_time = filtered_df["到达时间"].values[0]
            calendar_end = datetime.strptime(arrival_time, '%Y年%m月%d日%H:%M')
            print("到站:", end_station, "时间:", arrival_time)
        else:
            print("Time not found.")

        return calendar_title, calendar_start, calendar_end, calendar_description

    def __platform_text(self, order_info_str):
        result = re.split(',|，|。', order_info_str)
        for text in result:
            if "站" in text:
                return text
        return ''

    def __train_number_text(self, order_info_str):
        result = re.split(',|，|。', order_info_str)
        for text in result:
            if "次列车" in text:
                train_number = re.findall(r"[a-zA-Z0-9]+", text)
                return train_number[0]
        return ''

    def __train_seat_number(self, order_info_str):
        result = re.split(',|，|。', order_info_str)
        for text in result:
            if "车" in text and "号" in text:
                return text
        return ''

    def __train_date_text(self, order_info_str):
        time_pattern = re.compile(r'\d+年\d+月\d+日\d+:\d+')
        result = time_pattern.findall(order_info_str)
        if len(result) == 0:
            return ''
        return result[0]

    def __train_time_text(self, date_str):
        result = re.findall(r"\d+:\d+", date_str)
        if len(result) == 0:
            return ''
        return result[0]

    def __train_datetime(self, date_str) -> datetime:
        dt_cn = datetime.datetime.strptime(date_str, '%Y年%m月%d日%H:%M')
        dt_utc = dt_cn.astimezone(tz=pytz.timezone("UTC"))
        return dt_utc

    def __order_type_text(self, type):
        if "insert" == type:
            return '购票'
        elif "delete" == type:
            return "退票"
        elif "modify" == type:
            return '改签'
        return ''
