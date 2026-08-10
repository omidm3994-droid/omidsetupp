import jdatetime

def get_jalali_datetime():
    now = jdatetime.datetime.now()
    return now.strftime("%Y/%m/%d - %H:%M")
