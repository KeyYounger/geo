import geopy.distance
import pandas as pd
from datetime import datetime as dt

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
    # format: '25/03/2016 00:00:04'
    # time_difference = time1 - time2
    return (dt.strptime(time1, '%Y/%m/%d %H:%M:%S') - dt.strptime(time2, '%Y/%m/%d %H:%M:%S')).total_seconds()
