import pandas as pd
import os
import utils

"""
默认参数是美国旧金山SanFrancisco
实际参数是成都市
"""


def read_to_df(path_dir='C:\\Users\YK\Downloads\San Francisco'):
    all_file_list = os.listdir(path_dir)
    i = 1
    for file in all_file_list:
        df = pd.read_csv(os.path.join(path_dir, file), header=None, delimiter=" ",
                         names=['lat', 'lon', 'passenger', 'timestamp'])
        df['taxi_id'] = i
        if file == all_file_list[0]:
            all_df = df
        else:
            all_df = pd.concat([all_df, df], ignore_index=True)
        i += 1
    return all_df



def cleaning_data(taxi_df, minlat=37.7802, maxlat=37.8009, minlon=-122.4462, maxlon=-122.4011,
                  out_path="data/cleaned_taxi_data.csv", start_date='2008-05-17 00:00:00', end_date='2008-05-18 00:00:00'):
    taxi_df = taxi_df[(taxi_df['lat'] >= minlat) & (taxi_df['lat'] <= maxlat) & (taxi_df['lon'] >= minlon) & (
            taxi_df['lon'] <= maxlon)]
    taxi_df = taxi_df.copy()
    # taxi_df['time'] = taxi_df.apply(lambda row: utils.unix2time(row['timestamp']), axis=1)  # San需要转换时间格式
    taxi_df = taxi_df.sort_values(by=['taxi_id', 'time'], ignore_index=True)
    # df['time'] = pd.to_datetime(taxi_df['time'])
    # taxi_df = taxi_df.loc[
    #     (df['time'] >= start_date) & (df['time'] <= end_date)]
    del taxi_df['passenger']
    del taxi_df['timestamp']
    print(taxi_df)
    taxi_df.to_csv(out_path, index=False, sep=",")
    return taxi_df


if __name__ == '__main__':
    # df = read_to_df()
    df = pd.read_csv("E:\BaiduNetdiskDownload\车速预测\交通赛数据_上\\20140803_train.txt", header=None, delimiter=",",
                     names=['taxi_id', 'lat', 'lon', 'passenger', 'timestamp'])
    cleaning_data(df, 30.6397, 30.6844, 104.0414, 104.0925, out_path="data/cd_cleaned_taxi_data.csv")
    # cleaning_data(df)
