import datetime


def timelog(str):
    time = datetime.datetime.now().strftime("[%Y-%m-%d,%H:%M:%S]")
    print(time + ' ' + str)
