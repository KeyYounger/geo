import networkx as nx
import osmnx as ox
import pandas as pd
import os

"""
默认参数是美国旧金山SanFrancisco
实际参数是成都市
"""


# 根据边界框下载数据
def download_map(north=37.8009, south=37.7802, east=-122.4462, west=-122.4011):
    G = ox.graph_from_bbox(north, south, east, west, network_type="drive")
    return G


# 生成道路的df
def gen_road_df(road_graph):
    nodes_df, edges_df = ox.graph_to_gdfs(road_graph)
    edges_df['id'] = edges_df.index.to_numpy()
    edges_df['start'] = edges_df.apply(lambda row: nodes_df.loc[row['id'][0]]['geometry'].coords[0], axis=1)
    edges_df['end'] = edges_df.apply(lambda row: nodes_df.loc[row['id'][1]]['geometry'].coords[0], axis=1)
    road_df = edges_df[['osmid', 'start', 'end', 'length']]
    road_df = road_df.reset_index(drop=True)
    road_df['road_id'] = list(range(len(road_df)))
    edges_df['road_id'] = list(range(len(road_df)))
    for i in range(len(road_df)):
        if isinstance(road_df.iloc[i, 0], list):
            li = road_df.iloc[i, 0]
            road_df.iloc[i, 0] = li[0]
    print(road_df)
    return road_df


# 获取道路ID列表
def get_road_list(road_df=None, out_path='data/road_list.csv', update=False):
    if not update and os.path.exists(out_path):
        print('Road list exists')
        road_list = pd.read_csv(out_path)
    else:
        road_list = road_df[['road_id']].reset_index().drop('index', axis=1)
        # print(road_list[0])
        road_list.to_csv(out_path, index=False)
    return road_list


def road_graph(road_df, out_path="data/road_graph.gml"):
    G = nx.DiGraph()
    # 添加节点
    node_list = list(road_df['road_id'])
    G.add_nodes_from(node_list)
    lengths = dict(zip(road_df['road_id'], road_df['length']))
    print(lengths)
    nx.set_node_attributes(G, lengths, 'length')
    # 添加边
    road_df = road_df.copy()
    road_df['key'] = 0
    adj_df = road_df.merge(road_df, on='key', how='inner')
    print(adj_df.columns)
    print(len(adj_df))
    adj_df = adj_df[((adj_df['end_x'] == adj_df['start_y']) & (adj_df['start_x'] != adj_df['end_y']))  # x -> y
                    | (adj_df['road_id_x'] == adj_df['road_id_y'])]  # x self
    adj_df['distance'] = adj_df.apply(lambda row:
                                      (row['length_x'] + row['length_y']) / 2 if row['road_id_x'] != row['road_id_y']
                                      else 0, axis=1)
    adj_df['edge'] = adj_df.apply(lambda row: (row['road_id_x'], row['road_id_y'], {'weight': row['distance']}), axis=1)
    edge_list = list(adj_df['edge'])
    G.add_edges_from(edge_list)
    # 写入文件
    nx.write_gml(G, out_path)
    return G


if __name__ == '__main__':
    road_df = gen_road_df(download_map(30.6844, 30.6397, 104.0925, 104.0414))
    get_road_list(road_df, out_path='data/cd_road_list.csv')
    road_graph(road_df, out_path="data/cd_road_graph.gml")
