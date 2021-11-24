import pandas as pd
import networkx as nx
from utils import time_difference


def extract_trajectory(parsed_trajectory_df, G, verb=False, time_gap=4, stay_duration=10):

    trajectory_df = pd.DataFrame(columns=['taxi_id', 'trajectory_id', 'timestamp', 'road_id', 'lat', 'lon'])
    for i, row in parsed_trajectory_df.iterrows():
        if i == 0:  # Scenario 0.1: for the first reading, just record
            trajectory_id = 0
            stay_start_time = row['timestamp']
            trajectory_df.to_csv('data/trajectory_df.csv', index=False)
        else:
            if i % 100 == 0:
                trajectory_df.to_csv('data/trajectory_df.csv', mode='a', index=False, header=False)
                trajectory_df = pd.DataFrame(columns=['taxi_id', 'trajectory_id', 'timestamp', 'road_id', 'lat', 'lon'])
            if row['taxi_id'] == previous_row['taxi_id']:
                # same timing for multiple records, skip the following records
                if row['timestamp'] == previous_row['timestamp']:
                    if verb: print('Point %s S0.2. same timing for multiple records, skip the following records' % (i))
                    continue
                if row['road_id'] != previous_row['road_id']:
                    stay_start_time = row['timestamp']
                # stay at the same road segment for too long
                if time_difference(row['timestamp'], stay_start_time) > 60 * stay_duration:
                    if verb: print('Point %s S1.2. stay at the same road segment for too long' % (i))
                    drop_indices = trajectory_df[trajectory_df['timestamp'].apply(
                        lambda t: (time_difference(t, stay_start_time) > 0) & (
                                    time_difference(row['timestamp'], t) > 0))].index
                    trajectory_df = trajectory_df.drop(drop_indices)  # drop intermediate points
                    trajectory_id += 1  # keep the two end points, but in different trajectories
                # time gap is too long
                if time_difference(row['timestamp'], previous_row['timestamp']) > 60 * time_gap:
                    if verb: print('Point %s S1.1. time gap is too long' % (i))
                    stay_start_time = row['timestamp']
                    trajectory_id += 1
                # cannot find path between two points
                if not nx.has_path(G, str(previous_row['road_id']), str(row['road_id'])):
                    if verb: print('Point %s S1.3. cannot find path between two points' % (i))
                    trajectory_id += 1
            else:
                trajectory_id = 0
                stay_start_time = row['timestamp']
        row['trajectory_id'] = trajectory_id
        trajectory_df = trajectory_df.append(row, ignore_index=True)
        previous_row = row
    trajectory_df.to_csv('data/trajectory_df.csv', mode='a', index=False, header=False)
    return trajectory_df


def clean_trajectory(trajectory_df):
    # Trajectory cleaning
    # Scenario 2.1. Remove trajectories with single point
    drop_indices = []
    for i in range(len(trajectory_df)):
        if i == 0:
            if len(trajectory_df) == 1 or trajectory_df.loc[i, 'trajectory_id'] != trajectory_df.loc[i + 1, 'trajectory_id']:
                drop_indices.append(i)
        elif i == len(trajectory_df) - 1:
            if trajectory_df.loc[i, 'trajectory_id'] != trajectory_df.loc[i - 1, 'trajectory_id']:
                drop_indices.append(i)
        elif trajectory_df.loc[i, 'trajectory_id'] != trajectory_df.loc[i - 1, 'trajectory_id'] and trajectory_df.loc[i, 'trajectory_id'] != trajectory_df.loc[i + 1, 'trajectory_id']:
            drop_indices.append(i)
    trajectory_df = trajectory_df.drop(drop_indices).reset_index().drop('index', axis=1)
    cleaned_trajectory_df = pd.DataFrame(columns=['taxi_id', 'trajectory_id', 'timestamp', 'road_id', 'lat', 'lon'])
    j = 0
    for i, row in trajectory_df.iterrows():
        if i == 0:
            previous_row = row
            # cleaned_trajectory_df.to_csv('data/cleaned_trajectory_df.csv', index=False)  # save header to file
        else:
            # if i % 100 == 0:
            #     print('Appending result to file')
            #     cleaned_trajectory_df.to_csv('data/cleaned_trajectory_df.csv', mode='a', index=False, header=False)
            #     cleaned_trajectory_df = pd.DataFrame(columns=['taxi_id', 'trajectory_id', 'timestamp', 'road_id'])
            if previous_row['trajectory_id'] == row['trajectory_id'] and previous_row['taxi_id'] == row['taxi_id']:
                previous_row['trajectory_id'] = j
                cleaned_trajectory_df = cleaned_trajectory_df.append(previous_row, ignore_index=True)
                previous_row = row
                continue
            if previous_row['trajectory_id'] != row['trajectory_id'] and previous_row['taxi_id'] == row['taxi_id']:
                previous_row['trajectory_id'] = j
                j += 1
                cleaned_trajectory_df = cleaned_trajectory_df.append(previous_row, ignore_index=True)
                previous_row = row
                continue
            if previous_row['taxi_id'] != row['taxi_id']:
                previous_row['trajectory_id'] = j
                j = 0
                cleaned_trajectory_df = cleaned_trajectory_df.append(previous_row, ignore_index=True)
                previous_row = row
    # cleaned_trajectory_df.to_csv('data/cleaned_trajectory_df.csv', mode='a', index=False, header=False)
    del cleaned_trajectory_df['lat']
    del cleaned_trajectory_df['lon']
    return cleaned_trajectory_df


def recover_trajectory(cleaned_trajectory_df, G):
    # Trajectory recovery
    # For points that are not adjacent,
    # apply Dijkstra's shortest path algorithm to recover intermediate points.
    # Timing follows D time in O-D.
    recovered_trajectory_df = pd.DataFrame(columns=['taxi_id', 'trajectory_id', 'timestamp', 'road_id'])
    for i, row in cleaned_trajectory_df.iterrows():
        if i == 0:
            point_index = 0  # index of a point in a trajectory
            previous_row = row
        else:
            point_index = point_index + 1 if previous_row['trajectory_id'] == row['trajectory_id'] else 0
        if point_index == 0:
            recovered_trajectory_df = recovered_trajectory_df.append(row, ignore_index=True)
        if point_index > 0:
            O = str(previous_row['road_id'])
            D = str(row['road_id'])
            if O == D:
                recovered_trajectory_df = recovered_trajectory_df.append(row, ignore_index=True)
            else:  # O != D
                try:
                    road_ids = nx.dijkstra_path(G, O, D)
                    for road_id in road_ids[1:]:  # add intermediate points and end points
                        row['road_id'] = road_id
                        recovered_trajectory_df = recovered_trajectory_df.append(row, ignore_index=True)
                except Exception as e:
                    print(e)
                    continue
        previous_row = row

    return recovered_trajectory_df


if __name__ == '__main__':
    # 读取cd_parsed_trajectory_df.csv
    parsed_trajectory_df = pd.read_csv('data/parsed_trajectory_df.csv', delimiter=',')
    # 读取路网图
    road_graph = nx.read_gml('data/road_graph.gml')
    # # 写入文件
    trajectory_df = extract_trajectory(parsed_trajectory_df, road_graph, verb=True)
    print(trajectory_df)
    trajectory_df = pd.read_csv('data/trajectory_df.csv', delimiter=',')
    clean_trajectory_df = clean_trajectory(trajectory_df)
    print(clean_trajectory_df)
    recover_trajectory_df = recover_trajectory(clean_trajectory_df, road_graph)
    # print(recover_trajectory_df)
    recover_trajectory_df.to_csv('data/recovered_trajectory_df.csv', index=False)
