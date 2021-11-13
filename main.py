import networkx as nx
import geopandas as gp
import matplotlib.pyplot as plt

if __name__ == '__main__':
    roma = nx.read_gml('map/roma_road_graph.gml')
    print(nx.number_of_nodes(roma))
    print(nx.number_of_edges(roma))
    print(roma.degree())

    degree_list = roma.degree()
    j = 0
    for degree in degree_list:
        if degree[1] < 1:
            print(degree[0])
            j += 1
    print(j)
    m = 0
    print(nx.nodes(roma))
    for i in nx.nodes(roma):
        if roma.nodes[i]['length'] <= 20:
            print(i)
            m += 1
    print(m)
    # pos = {}
    # print(road_graph.nodes[str(1)]['geometry'])
    # for i in range(len(road_graph.nodes)):
    #     geometry = road_graph.nodes[str(i)]['geometry']
    #     geometry = geometry.split(",")
    #     geometry = str(geometry[0])
    #     geometry = geometry.strip().split(" ")
    #     lon = "%.7f" % float(format(float(geometry[0]), '.7f'))
    #     lat = "%.7f" % float(format(float(geometry[1]), '.7f'))
    #     print(type(lat))
    #     pos[str(i)] = (float(lon), float(lat))
    # nx.draw(road_graph, pos=pos, node_size=8)
    # plt.show()
