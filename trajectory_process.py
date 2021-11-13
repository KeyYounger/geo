import pandas as pd
from utils import time_difference
import networkx as nx


def extract_trajectory(parsed_trajectory_df, G, verb=False, time_gap=2, stay_duration=1):
    trajectory_df = pd.DataFrame(columns=['taxi_id', 'trajectory_id', 'timestamp', 'road_id'])
    for i, row in parsed_trajectory_df.iterrows():
        if i == 0:  # Scenario 0.1: for the first reading, just record
            trajectory_id = 0
            stay_start_time = row['timestamp']
        else:
            if row['taxi_id'] == previous_row['taxi_id']:
                # same timing for multiple records, skip the following records
                if row['timestamp'] == previous_row['timestamp']:
                    if verb: print('Point %s S0.2. same timing for multiple records, skip the following records' % (i))
                    continue
                # stay at the same road segment for too long
                if time_difference(row['timestamp'], stay_start_time) > 60 * stay_duration:
                    if verb: print('Point %s S1.2. stay at the same road segment for too long' % (i))
                    drop_indices = trajectory_df[trajectory_df['timestamp'].apply(
                        lambda t: (time_difference(t, stay_start_time) > 0) & (
                                    time_difference(row['time'], t) > 0))].index
                    trajectory_df = trajectory_df.drop(drop_indices)  # drop intermediate points
                    trajectory_id += 1  # keep the two end points, but in different trajectories
                if row['road_id'] != previous_row['road_id']:
                    stay_start_time = row['timestamp']
                # time gap is too long
                if time_difference(row['timestamp'], previous_row['timestamp']) > 60 * time_gap:
                    if verb: print('Point %s S1.1. time gap is too long' % (i))
                    stay_start_time = row['timestamp']
                    trajectory_id += 1
                # cannot find path between two points
                elif not nx.has_path(G, previous_row['road_id'], row['road_id']):
                    if verb: print('Point %s S1.3. cannot find path between two points' % (i))
                    trajectory_id += 1
            else:
                trajectory_id = 0
                stay_start_time = row['timestamp']
        row['trajectory_id'] = trajectory_id
        trajectory_df = trajectory_df.append(row, ignore_index=True)
        previous_row = row
    return trajectory_df


if __name__ == '__main__':
    # 读取cd_parsed_trajectory_df.csv
    parsed_trajectory_df = pd.read_csv('data/cd_parsed_trajectory_df.csv', delimiter=',')
    # 读取路网图
    road_graph = nx.read_gml('data/cd_road_graph.gml')
    # 写入文件
    trajectory_df = extract_trajectory(parsed_trajectory_df, road_graph)
    trajectory_df.to_csv('data/cd_cleaned_trajectory_df.csv', index=False)
