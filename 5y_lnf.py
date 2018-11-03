import networkx as nx
import matplotlib.pyplot as plt
from cpn import G
from demand_real_new import D


"""
Create the network model
"""
cpnx = nx.MultiDiGraph(G)


for s_node in cpnx.nodes():
    for n_node in GG[s_node]:
#        print(GG[s_node][n_node][0]['bw'])
         GG[s_node][n_node][0]['bw'] = 0   #set GG bw to 0, we will use this parameter to aggregate bw's after demand calc
#         print(GG[s_node][n_node][0]['bw'])  #check all bw parameters are 0
