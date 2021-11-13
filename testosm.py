import networkx as nx
import osmnx as ox
import osmnx.distance as oxd
import time
import map_matching as mp

# download/model a street network for some city then visualize it
G = ox.graph_from_bbox(30.6397, 30.6844, 104.0414, 104.0925,  network_type="drive")
# fig, ax = ox.plot_graph(G)
# 30.665479,104.041808
# (5530491877, 5530491878, 0)
start2 = time.time()
id_edge = ox.get_nearest_edge(G, (30.67414, 104.045303))
#id_edge1 = oxd.nearest_edges(G, X=30.665479, Y=104.041808, return_dist=False)
end2 = time.time()
print(end2 - start2)
print(id_edge)
D = ox.utils_graph.get_digraph(G)
print(nx.number_of_nodes(D))
print(nx.number_of_edges(D))
gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
print("----------------------------")
print(list(range(2739)))
gdf_edges['road_id'] = list(range(2739))
print(gdf_edges.head(5))
print(gdf_edges.loc[id_edge])
map_con = mp.in_mem_map(G)
start1 = time.time()
gps = mp.map_match(30.665479, 104.041808, map_con)
end1 = time.time()
print(gps)
print(end1-start1)

print(gdf_edges.loc[id_edge]['geometry'])
print(gdf_edges.head())
print(gdf_nodes.head())
print(gdf_nodes.columns)
print(gdf_edges.columns)
# print(gdf_edges['highway'])
# list = []
# i = 0
# li = []
# for row in gdf_edges['highway']:
#     if row not in list:
#         list.append(row)
#     if row!='primary' and row!='secondary' and row!='tertiary' and row!='tertiary_link' and row!='secondary_link' \
#         and row!='primary_link' and row!='trunk' and row!='trunk_link' and row!='residential':
#         i += 1
# print(i)
# print(list)
# df = gdf_edges[(gdf_edges['highway']!='primary')&(gdf_edges['highway']!='secondary')&(gdf_edges['highway']!='tertiary')&
# (gdf_edges['highway']!='tertiary_link')&(gdf_edges['highway']!='secondary_link')&(gdf_edges['highway']!='primary_link')&
#                (gdf_edges['highway']!='trunk')&(gdf_edges['highway']!='trunk_link')&(gdf_edges['highway']!='residential')].index.tolist()
# df = gdf_edges[(gdf_edges['highway']=='living_street')].index.tolist()
# print(df)
# for row in df:
#     gdf_edges = gdf_edges.drop([row])
#     if row[1] in gdf_nodes.index:
#         gdf_nodes = gdf_nodes.drop(row[1])
# G2 = ox.graph_from_gdfs(gdf_nodes, gdf_edges, graph_attrs=G.graph)
# G_proj = ox.project_graph(G2)
# G2 = ox.consolidate_intersections(G_proj, rebuild_graph=True, tolerance=15, dead_ends=False)
# fig, ax = ox.plot_graph(G2)
# print(gdf_nodes.loc[65287111])
# print(type(gdf_nodes.loc[65350760]['geometry']))
# print(gdf_nodes.loc[65350760]['geometry'].coords[0])
# gdf_edges.reset_index(drop=True)
# print("--------------------------------------------------")
# print(gdf_edges.index)