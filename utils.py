import geopy.distance
import pandas as pd
import time
from datetime import datetime as dt, timedelta
import os


def gps2m(coords_1, coords_2):
    return geopy.distance.great_circle(coords_1, coords_2).m


def cal_length(coord_list):
    i = 0
    length = 0
    while i < len(coord_list) - 1:
        coords_1 = (coord_list[i][1], coord_list[i][0])
        coords_2 = (coord_list[i + 1][1], coord_list[i + 1][0])
        length += gps2m(coords_1, coords_2)
        i += 1
    return length


def unix2time(unixtime, timezone='America/Los_Angeles'):
    return pd.to_datetime(unixtime, unit='s', utc=True).tz_convert(timezone)


def time_difference(time1, time2):
    return (dt.strptime(time1, '%Y-%m-%d %H:%M:%S') - dt.strptime(time2, '%Y-%m-%d %H:%M:%S')).total_seconds()


def df_to_csv(df, file_path, index=False):
    print('Saving to file at %s' % (file_path))
    if os.path.exists(file_path):
        temp_file_path = '%s_temp' % (file_path)
        df.to_csv(temp_file_path, index=index)
        os.system('rm %s' % (file_path))
        os.system('mv %s %s' % (temp_file_path, file_path))
    else:
        df.to_csv(file_path, index=index)
    print('Saved.')


def round_time(t, interval=5):
    # t = '25/03/2016 12:26:45'
    # output: '25/03/2016 12:25:00'
    # interval: in minutes
    interval = interval * 60  # convert minutes to seconds
    datetime = dt.strptime(t, '%Y-%m-%d %H:%M:%S')
    print(datetime)
    new_datetime = dt.fromtimestamp(int(time.mktime(datetime.timetuple())) // interval * interval)
    return new_datetime.strftime('%Y-%m-%d %H:%M:%S')

def date_range(date1, date2):
    # date1, date2 = '20160401', '20160428'
    datetime1 = dt.strptime(date1, '%Y-%m-%d')
    datetime2 = dt.strptime(date2, '%Y-%m-%d')
    days = (datetime2 - datetime1).days + 1
    date_list = [(datetime1 + timedelta(day)).strftime('%Y-%m-%d') for day in range(days)]
    return date_list

def print_log(line, log_path):
    with open(log_path, 'a') as f:
        f.write(str(line)+'\n')