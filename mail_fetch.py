#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from calendar_generate import CalendarGenerate
from calendar_resovle import CalendarResovle
from mail_resovle import MailResovle
import os
import re
import imaplib

class MailFetch:
    def __init__(self, user_email, password, imap_server, port):
        if len(imap_server) == 0:
            imap_server = 'imap.' + re.split('@', user_email)[-1]
        self.user_email = user_email
        self.password = password
        self.imap_server = imap_server
        self.port = port
        self.mailbox = None

    def get_mails(self) -> list:
        if self.mailbox is None:
            return []
        mail_model_list = self.resovle_all_mails()
        mail_model_list = self.filter_validate_mail(mail_model_list)
        self.stop_server()
        return mail_model_list

    # 已排好序： 旧 -> 新
    def resovle_all_mails(self) -> list:
        if self.mailbox is None:
            return []
        mailbox = self.mailbox
        mailbox.select("12306")  # Select the "12306" mailbox
        _, data = mailbox.search(None, "ALL")  # Search for all emails
        mail_model_list = []
        for num in data[0].split():
            _, msg_data = mailbox.fetch(num, "(RFC822)")  # Fetch the email with the given number
            msg_content = msg_data[0][1].decode("utf-8")
            mail_model = MailResovle().resovle_to_mail(msg_content)  # 解析出邮件
            if len(mail_model):
                mail_model_list.append(mail_model)
        return mail_model_list

    def login(self):
        try:
            # 连接到IMAP服务器:
            mailbox = imaplib.IMAP4_SSL(self.imap_server, self.port)
            mailbox.login(self.user_email, self.password)
            self.mailbox = mailbox
            return True
        except Exception:
            self.mailbox = None
            return False

    def stop_server(self):
        if self.mailbox is None:
            return
        self.mailbox.logout()

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
    password = ''  # 这个密码不是邮箱登录密码，是IMAP服务密码
    imap_server = 'imap.126.com'
    port = 993
    mail_fetch = MailFetch(user_email, password, imap_server, port)
    alarm_before_hour = 2
    if mail_fetch.login():
        print("登录成功")
        mail_model_list = mail_fetch.get_mails()
        DATABASE_DIR_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "./database")
        calendarHelper = CalendarGenerate('12306', DATABASE_DIR_PATH + '/' + user_email + '.ics')
        for mail in mail_model_list:
            print(mail)
            event_id = mail['order_id']
            event_title, event_start, event_end, event_description = CalendarResovle().generate_calendar_model(mail)
            calendarHelper.add_event(event_id, event_title, event_end, event_start, event_description, alarm_before_hour)
        calendarHelper.save_ics()
    else:
        print("登录失败")
