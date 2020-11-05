#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from calendar_generate import CalendarGenerate
from calendar_resovle import CalendarResovle
from mail_resovle import MailResovle
import poplib, os, re

class MailFetch:
    def __init__(self, user_email, password, pop3_server):
        if len(pop3_server) == 0:
            pop3_server = 'pop.' + re.split('@',user_email)[-1]
        self.user_email = user_email
        self.password = password
        self.pop3_server = pop3_server
        self.server = None

    def get_mails(self) -> list:
        if self.server == None:
            return []
        mail_model_list = self.resovle_all_mails()
        mail_model_list = self.filter_validate_mail(mail_model_list)
        self.stop_server()
        return mail_model_list

    # 已排好序： 旧 -> 新
    def resovle_all_mails(self) -> list:
        if self.server == None:
            return []
        server = self.server
        _, mails, _ = server.list()     # list()返回所有邮件的编号
        if len(mails) == 0:
            return []
        mail_model_list = []
        for index in range(1, len(mails) + 1):  # 注意索引号从1开始
            _, lines, _ = server.retr(index) # lines存储了邮件的原始文本的每一行,
            if len(lines) == 0:
                continue
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            mail_model = MailResovle().resovle_to_mail(msg_content)  # 解析出邮件
            if len(mail_model):
                mail_model_list.append(mail_model)
        return mail_model_list

    def login(self):
        try:
            poplib._MAXLINE=20480
            # 连接到POP3服务器:
            server = poplib.POP3_SSL(self.pop3_server, 995)
            server.user(self.user_email)
            server.pass_(self.password)
            self.server = server
            return True
        except Exception:
            server = None
            return False

    def stop_server(self):
        if self.server == None:
            return
        self.server.quit() # 关闭连接

    def filter_validate_mail(self, mail_model_list):
        target_list = []
        for mail in mail_model_list:
            need_remove_mail = []
            for target in target_list:
                if target['order_id'] == mail['order_id']:
                    need_remove_mail.append(target)
                    continue
            if len(need_remove_mail) > 0:
                target_list.remove(need_remove_mail[0])
            if mail["order_type"] == "delete":
                continue
            target_list.append(mail)
        return target_list

if __name__ == '__main__':
    user_email = ''
    password = ''	# 这个密码不是邮箱登录密码，是pop3服务密码
    pop3_server = 'pop.qq.com'
    mail_fetch = MailFetch(user_email, password, pop3_server)
    alarm_before_hour = 2
    if mail_fetch.login():
        print("登录成功")
        mail_model_list = mail_fetch.get_mails()
        DATABASE_DIR_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "./database")
        calendarHelper = CalendarGenerate('12306', DATABASE_DIR_PATH + '/'+ user_email +'.ics')
        for mail in mail_model_list:
            event_id = mail['order_id']
            event_title, event_start, event_description = CalendarResovle().generate_calendar_model(mail)
            calendarHelper.add_event(event_id, event_title, event_start, event_start, event_description, alarm_before_hour)
        calendarHelper.save_ics()
    else:
        print("登录失败")