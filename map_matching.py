import pandas as pd
from leuvenmapmatching.matcher.distance import DistanceMatcher
from leuvenmapmatching.map.inmem import InMemMap
from leuvenmapmatching.matcher.simple import SimpleMatcher
from road_graph import download_map
import osmnx as ox
import time
import logging


logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def in_mem_map(graph):
    map_con = InMemMap("Chengdu", use_latlon=True, index_edges=True, use_rtree=False)
    nodes_df, edges_df = ox.graph_to_gdfs(graph)
    for nid, row in nodes_df[['x', 'y']].iterrows():
        map_con.add_node(nid, (row['y'], row['x']))
    for row in edges_df.index:
        map_con.add_edge(row[0], row[1])
    return map_con


def map_match(lat, lon, map_con=None, graph=None):
    path = [(lat, lon)]
    # id_edge = ox.get_nearest_edge(graph, (lat, lon))
    # matcher = DistanceMatcher(map_con, max_dist_init=200000, max_dist=2000000, obs_noise=1, obs_noise_ne=10,
    #                           non_emitting_states=True, only_edges=True, max_lattice_width=5, use_index=True)
    matcher = SimpleMatcher(map_con, max_dist_init=20000, in_prob_norm=0.5, obs_noise=0.5, non_emitting_states=True,
                            only_edges=True, max_lattice_width=1)
    states, _ = matcher.match(path)
    print(states[0])
    return states[0]


def get_gpsdata(taxi_df, gdf_edges, taxi_id, map_con=None, graph=None):
    taxi_df = taxi_df.loc[taxi_df['taxi_id'] == taxi_id]
    road_id_list = []
    for index, row in taxi_df.iterrows():
        try:
            road_id = map_match(row['lat'], row['lon'], map_con=map_con)
            road_id = gdf_edges.loc[road_id]['road_id']
            road_id_list.append(road_id[0])
        except Exception as e:
            logger.info(row)
            continue
    print(len(road_id_list))
    taxi_df = taxi_df.copy()
    taxi_df['road_id'] = road_id_list
    # taxi_df['road_id'] = taxi_df.apply(
    #     lambda row: gdf_edges.loc[map_match(row['lat'], row['lon'], map_con=map_con)]['road_id'], axis=1)
    return taxi_df


if __name__ == '__main__':
    taxi_df = pd.read_csv("data/cd_cleaned_taxi_data.csv")
    cd_graph = download_map(30.6844, 30.6397, 104.0925, 104.0414)
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(cd_graph)
    gdf_edges['road_id'] = range(len(gdf_edges))
    print(gdf_nodes)
    print(gdf_edges)
    map_con = in_mem_map(cd_graph)
    print(map_con.graph)
    print(map_con.index_edges)
    gdf_edges = gdf_edges.copy()
    gdf_edges = gdf_edges.sort_index()

    taxi_ids = taxi_df['taxi_id'].unique()
    start_time = time.time()
    parsed_trajectory_df = pd.DataFrame(columns=['taxi_id', 'lat', 'lon', 'timestamp', 'road_id'])
    i = 801
    while i < len(taxi_ids):
    # for i in range(len(taxi_ids)):
        taxi_id = taxi_ids[i]
        print('Vehicle #%s: %s. Time spent: %s s' % (i, taxi_id, int(time.time() - start_time)))
        if i == 0:
            print('Saving header to file')
            parsed_trajectory_df.to_csv('data/cd_parsed_trajectory_df.csv', index=False)  # save header to file
        if i % 50 == 0 and i != 0:
            print('Appending result to file')
            parsed_trajectory_df.to_csv('data/cd_parsed_trajectory_df.csv', mode='a', index=False, header=False)
            parsed_trajectory_df = pd.DataFrame(columns=['taxi_id', 'lat', 'lon', 'timestamp', 'road_id'])
            if i == 2000: break
        parsed_trajectory_df = parsed_trajectory_df.append(get_gpsdata(taxi_df, gdf_edges, taxi_id, map_con=map_con))
        i += 1
    print('Appending result to file')
    parsed_trajectory_df.to_csv('data/cd_parsed_trajectory_df.csv', mode='a', index=False, header=False)

# print("States\n------")
# print(states)
# print("Nodes\n------")
# print(nodes)
# print("")
# matcher.print_lattice_stats()

# [(258758554, 258758555), (258758555, 258758552), (258758552, 258758553), (258758553, 258758550),
# (258758550, 258758551), (258758551, 258758549), (258758549, 258758548),
# (258758548, 258758547), (258758547, 258758546), (258758546, 1564279875), (1564279875, 65295340)]
# for row in nodes:
#     print(nodes_df.loc[row])
