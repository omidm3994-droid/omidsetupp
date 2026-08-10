from datetime import datetime
import jdatetime

def get_jalali_datetime():
    now = datetime.now()
    j_now = jdatetime.datetime.fromgregorian(datetime=now)
    return j_now.strftime("%Y/%m/%d - %H:%M")
