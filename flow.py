# nohup python flow.py -d 20160325 -i 5 >> log/flow0325.log &
import os
import time
import pandas as pd
import numpy as np
import argparse
from datetime import datetime as dt
from datetime import date, timedelta
from utils import time_difference, round_time, df_to_csv
from road_graph import get_road_list, road_graph


def generate_time_intervals(start_date='20160325', end_date='20160325', interval=5):
    start_time = int(time.mktime(dt.strptime(start_date, '%Y-%m-%d').timetuple()))
    end_time = int(time.mktime((dt.strptime(end_date, '%Y-%m-%d') + timedelta(1)).timetuple()))
    interval = interval * 60  # convert minutes to seconds
    time_intervals = []
    for timestamp in range(start_time, end_time, interval):
        time_intervals.append(dt.fromtimestamp(timestamp / interval * interval).strftime('%Y-%m-%d %H:%M:%S'))
    return time_intervals


if __name__ == '__main__':
    # Parameter Settings
    # start_date = '20160325'
    # end_date = '20160325'
    # interval = 5
    start_date = '2008-05-17'
    end_date = '2008-05-17'
    interval = 15  # in minutes
    flow_path = 'data/flow.csv'
    checkpoint_path = 'data/flow.checkpoint'
    trajectory_path = 'data/recovered_trajectory_df.csv'
    road_list_path = 'data/road_list.csv'

    recovered_trajectory_df = pd.read_csv(trajectory_path)

    # initialize flow_df
    print('Creating new flow file')
    road_list = get_road_list(road_df=None, out_path=road_list_path, update=False)
    flow_df = pd.DataFrame(columns=list(road_list['road_id']))
    time_intervals = generate_time_intervals(start_date=start_date, end_date=end_date, interval=interval)
    for time_interval in time_intervals:
        flow_df.loc[time_interval] = 0
    checkpoint = 0

    # aggregate and save flow
    # flow is saved to file in overwrite mode
    print('Total number of points:', len(recovered_trajectory_df))
    start_time = time.time()
    i = -1  # dummy
    for i, row in recovered_trajectory_df.iterrows():
        if i < checkpoint:
            pass
        elif i == 0:
            flow_df.loc[round_time(row['timestamp'], interval=interval), row['road_id']] += 1
        else:
            if i % 10000 == 0:
                print('Saving result at index %s. Time spent: %s s' % (i, int(time.time() - start_time)))
                df_to_csv(flow_df, flow_path, index=True)
                with open(checkpoint_path, 'w') as f:
                    f.write(str(i))
            if row['taxi_id'] != previous_vehicle_id or row['trajectory_id'] != previous_trajectory_id:  # new trajectory
                flow_df.loc[round_time(row['timestamp'], interval=interval), row['road_id']] += 1
            elif row['road_id'] != previous_road_id:  # appear in this road
                flow_df.loc[round_time(row['timestamp'], interval=interval), row['road_id']] += 1
        previous_vehicle_id, previous_trajectory_id, previous_road_id = row['taxi_id'], row['trajectory_id'], row['road_id']
    print('Saving result at index', i)
    df_to_csv(flow_df, flow_path, index=True)
    with open(checkpoint_path, 'w') as f:
        f.write(str(i))
    print('New total flow:', flow_df.sum().sum())
    print('Finished flow aggregation. Total time spent: %.2f hour.' % ((time.time() - start_time) / 3600))
