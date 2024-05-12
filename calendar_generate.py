from icalendar import Calendar, Event, vDatetime, Alarm
from datetime import datetime, timedelta
from pytz import UTC # timezone
import pytz, os

class CalendarGenerate:
    def __init__(self, calendar_name, ics_file_path = './'):
        self._ics_file_path = ics_file_path
        calendar = Calendar()
        calendar.add('prodid', 'zou12306')
        calendar.add('version', '2.0') # 这里的 version 是 Calendar 协议的版本
        calendar.add('X-WR-CALNAME', calendar_name)
        self._calendar = calendar

    def add_event(self, uid, summary, dt_start, dt_end, description, alarm_before_hour = 0):
        create_time = datetime.today()
        organizer = "12306 Calendar"
        event = Event()
        event.add('uid', uid)
        event.add('dtstamp', create_time)
        event.add('summary', summary)
        event.add('dtstart', dt_start)
        event.add('dtend', dt_end)
        event.add('description', description)
        event.add('organizer', organizer)
        event.add('create', create_time)
        event.add('last-modified', create_time)
        event.add('sequence', "0")
        if alarm_before_hour > 0:
            alarm = Alarm()
            alarm.add('action', 'AUDIO')
            alarm.add('attach', 'Chord')
            # The default value type is DURATION. The value type can be set to a DATE-TIME value type, in which case the value MUST specify a UTC formatted DATE-TIME value
            dt_start_utc = dt_start.astimezone(tz=pytz.timezone("UTC"))
            alarm_trigger = dt_start_utc + timedelta(hours=-alarm_before_hour)
            alarm.add('trigger', alarm_trigger)
            event.add_component(alarm)
        self._calendar.add_component(event)

    def save_ics(self):
        dir_path = os.path.dirname(self._ics_file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        f = open(self._ics_file_path, 'wb')
        f.write(self._calendar.to_ical())
        f.close()

if __name__ == '__main__':
    database_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "./database")
    helper = CalendarGenerate('12306', database_path + '/test.ics')
    
    order_id = "order_id"
    summary = "summary123"
    description = "description123"
    calendar_start = datetime.now()  + timedelta(seconds=10)
    calendar_start = calendar_start.astimezone(tz=pytz.timezone("UTC"))
    calendar_end = datetime.now() .astimezone(tz=pytz.timezone("UTC"))
    helper.add_event(order_id,summary,calendar_start,calendar_end,description, 0)
    helper.save_ics()
