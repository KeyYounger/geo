import networkx as nx
import osmnx as ox
import osmnx.distance as oxd
import time
import map_matching as mp
from leuvenmapmatching.matcher.distance import DistanceMatcher
from leuvenmapmatching.map.inmem import InMemMap
from leuvenmapmatching.matcher.simple import SimpleMatcher
import pandas as pd

# download/model a street network for some city then visualize it
from road_graph import download_map
from utils import time_difference


# taxi_df = pd.read_csv('data/cleaned_taxi_data.csv', parse_dates=[3])
# taxi_df = taxi_df.loc[(taxi_df['timestamp'] >= '2008-05-17 00:00:00') & (taxi_df['timestamp']<='2008-05-18 00:00:00')]

G = download_map()
nodes_df, edges_df = ox.graph_to_gdfs(G)
edges_df['road_id'] = list(range(len(edges_df)))
edges_df.to_csv('data/road_df', index=False)