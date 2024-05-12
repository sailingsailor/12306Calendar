import poplib, datetime, os, re, pytz, requests, io, json
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

class CalendarResovle:
    def generate_calendar_model(self, mail):
        order_info = mail['order_info']
        begin_time = ''
        time_pattern = r"\d{4}年\d{2}月\d{2}日\d{2}:\d{2}"
        time_match = re.search(time_pattern, order_info)
        if time_match:
            time = time_match.group()
            # 解析为 datetime 对象
            begin_time = datetime.strptime(time, '%Y年%m月%d日%H:%M')
            print("时间:", begin_time)

        # 提取发站到站，连字符（-）两边的字符串
        station = ''
        station_pattern = r"，([^，]+)-([^，]+)，"
        station_match = re.search(station_pattern, order_info)
        if station_match:
            start_station = station_match.group(1).replace("站","")
            end_station = station_match.group(2).replace("站","")
            station = start_station + "-" + end_station
            print("行程:", station)
            print("发站:", start_station)
            print("到站:", end_station)

        # 提取车次
        train = ''
        train_pattern = r"[A-Z]\d+次"
        train_match = re.search(train_pattern, order_info)
        if train_match:
            train = train_match.group().replace("次","")
            print("车次:", train)

        # 提取座位号
        seat = ''
        seat_pattern = r"\d+车\d+[A-Z]号"
        seat_match = re.search(seat_pattern, order_info)
        if seat_match:
            seat = seat_match.group()
            print("座位号:", seat)

        # 提取检票口
        check_in = ''
        check_in_pattern =  r"检票口(\w+)"
        check_in_match = re.search(check_in_pattern, order_info)
        if check_in_match:
            check_in = check_in_match.group()
            print("检票口:", check_in.replace("检票口",""))
        else:
            print("未找到检票口信息。")

        # Function to extract arrival time
        # Extract arrival time from the URL
        url = f"http://touch.qunar.com/h5/train/trainStaChoose?trainNum={train}"
        content = requests.get(url).text
        # Wrap the HTML content in a StringIO object
        content_io = io.StringIO(content)
        # Use pandas to parse the HTML table
        df = pd.read_html(content_io)[0]
        # Filter the DataFrame to get the desired time
        filtered_df = df[df["车站"].str.contains(end_station)]
        #print(filtered_df)
        if not filtered_df.empty:
            arrival_time = filtered_df["到达时间"].values[0]
            #print(arrival_time)
            end_time = begin_time.replace(hour=int(arrival_time[:2]), minute=int(arrival_time[3:]))
            print("到达时间:", end_time)
        else:
            print("Time not found.")
        
        calendar_start = begin_time
        calendar_end = end_time
        calendar_title = station + ' ' + train + '次，' + seat
        calendar_description = mail['order_id'] + '，' + self.__order_type_text(mail['order_type']) + '，' + order_info
        return calendar_title, calendar_start, calendar_end, calendar_description

    def __order_type_text(self, type):
        if "insert" == type:
            return '购票'
        elif "delete" == type:
            return "退票"
        elif "modify" == type:
            return '改签'
        return ''
