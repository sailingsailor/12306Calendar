from mail_fetch import MailFetch
from calendar_generate import CalendarGenerate
from calendar_resovle import CalendarResovle
from flask import Flask, request, jsonify, make_response, send_from_directory
import shutil, re, os, pytz, random, string
from datetime import datetime

app = Flask(__name__)
# 避免在其他路径运行时，./database 的相对路径 不正确了
LOG_DIR_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "./log")

IS_DEBUG_ENV = True

@app.route('/')
def do_login():
    if check_args() == False:
        return login_fail_file()
    user_email = request.args.get("u")
    password = request.args.get("p")
    try:
        alarm_before_hour = int(request.args.get("h"))
    except:
        alarm_before_hour = 1
    try:
        return sync_fetch(user_email, password, alarm_before_hour)
    except:
        return server_error_file()

def sync_fetch(user_email, password, alarm_before_hour):
    mail_fetch = MailFetch(user_email, password, '')
    if mail_fetch.login() == False:
        return login_fail_file()
    mail_model_list = mail_fetch.get_mails()
    return fetch_new_mails(alarm_before_hour, mail_model_list)

def fetch_new_mails(alarm_before_hour, mail_model_list):
    calendarHelper = CalendarGenerate('12306')
    for mail in mail_model_list:
        event_id = mail['order_id']
        event_title, event_start, event_description = CalendarResovle().generate_calendar_model(mail)
        calendarHelper.add_event(event_id, event_title, event_start, event_end, event_description, alarm_before_hour)
    return response_content(calendarHelper)
def check_args() -> bool:
    try:
        email = request.args.get("u")
        password = request.args.get("p")
        if len(email) == 0 or len(password) == 0 or len(re.findall(re.compile(r'[0-9a-zA-Z.]+@[0-9a-zA-Z.]+?com'), email)) == 0:
            return False
        return True
    except Exception:
        return False

def server_error_file():
    event_title = "服务器出错，正在修复"
    event_info = "程序员小哥哥在努力修复中，请耐心等待，么么哒～～"
    return generate_error_file(event_title, event_info)

def login_fail_file():
    event_title = "登录失败，请检查邮箱和密码"
    event_info = "请检查邮箱以及密码是否正确"
    return generate_error_file(event_title, event_info)

def generate_error_file(event_title, event_info):
    event_id = str(datetime.now())
    calendarHelper = CalendarGenerate('12306')
    event_start = datetime.now().astimezone(tz=pytz.timezone("UTC"))
    calendarHelper.add_event( event_id, event_title, event_start, event_start, event_info)
    return response_content(calendarHelper)

def parameter_invalidate_file(url):
    random_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    event_id = str(datetime.now()) + random_str
    event_title = "登录失败，请检查邮箱和密码"
    event_info = "请检查邮箱以及密码是否正确"
    calendarHelper = CalendarGenerate('12306')
    event_start = datetime.now().astimezone(tz=pytz.timezone("UTC"))
    calendarHelper.add_event(event_id, event_title, event_start, event_start, event_info)
    return response_content(calendarHelper)

def response_content(calendarHelper):
    resp = make_response(calendarHelper._calendar.to_ical())
    resp.headers['Content-Type']= 'text/calendar'
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080', debug=IS_DEBUG_ENV)
