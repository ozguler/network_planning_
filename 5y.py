import networkx as nx
import matplotlib.pyplot as plt
import csv
from cpn import G
from demand_c import D

import easygui
from easygui import *


global cpnx
global sim_type
sim_type = 0


cpnx = nx.MultiDiGraph(G)
GG = G
print("Number of nodes is:", cpnx.number_of_nodes(),"Number of edges is", cpnx.number_of_edges())

#set all bw paramters to 0, some values are non-zero in the initial data

from multiprocessing.dummy import Pool as ThreadPool

def cpnxgui():
#    from multiprocessing.dummy import Pool as ThreadPool

    global sim_type
    msg2 = "Choose the type of SIMULATION you want..."
    title2 = "CPN Traffic Simulator v0.1"
    choices2 = ["Traffic SIM for a given Network Model and Demand Matrix", "Traffic SIM with Single Link Failure",
                "Traffic SIM with Single Node Failure", "Traffic SIM with Double Link Failure" ]
    user_choice = choicebox(msg2, title2, choices2)

    if user_choice == "Traffic SIM for a given Network Model and Demand Matrix":
        sim_type = 1
        vanilla_sim(cpnx)

    elif user_choice == "Traffic SIM with Single Link Failure":
        sim_type = 2
#        pool = ThreadPool(32)
#        pool.map(single_link_loss(cpnx))
        single_link_loss(cpnx)

    elif user_choice == "Traffic SIM with Single Node Failure":
        sim_type = 3

    elif user_choice == "Traffic SIM with Double Link Failure":
        sim_type = 4

    return(sim_type)

def set_bw_to_zero():
    for s_node in cpnx.nodes():
        for n_node in GG[s_node]:
            GG[s_node][n_node][0]['bw'] = 0   #set GG bw to 0, we will use this parameter to aggregate bw's after demand calc
    return GG

def create_bw2(GG):
    for s_node in cpnx.nodes():
        for n_node in GG[s_node]:
            GG[s_node][n_node][0]['bw2'] = (0,"") #create a tuple bw2 where bw2[0] is the simulated bw for that link (edge) and
                                                  #bw2[1] is the edge which was used in the single link failure sim
    return GG

def set_bw_to_max(GG, edge):
    for s_node in cpnx.nodes():
        for n_node in GG[s_node]:
            if (GG[s_node][n_node][0]['bw'] > GG[s_node][n_node][0]['bw2'][0]):
                GG[s_node][n_node][0]['bw2'] = (GG[s_node][n_node][0]['bw'], edge )
            else:
                continue

"""
create a demand_d array in the format of "[path_element1, path_element2, ..], bw"
the actual bw calc requires another step where bw
is added to each link between the nodes listed in path that is executed by networkx
"""
def calc_spf(D):   #D is the demand matrix
    demand_d = []
    for s_pop in D:
        for d_pop in D[s_pop]:
            path_f = nx.dijkstra_path(cpnx, s_pop, d_pop, weight = 'distance')
            demand_d.append((path_f, D[s_pop][d_pop]))    #D[s_pop][d_pop] is the bw parameter that is extracted from the demand dictionary.
    return demand_d                                     #here we are creating a tuple where first elemet is a list of nodes that constitute the disjkstra path
                                                        #and the second element in the tuple is the bw that is required to be
                                                        #reserved along path_f (which is a list of nodes constituting the disjkstra path)
def calc_bw(demand_d):
    global cpnx
    for path_bw in demand_d:
        path_bw_len = len((path_bw[0]))
        for i in range (path_bw_len-1): #walk through the node elements for eahc path in demend_d
            s_node = path_bw[0][i]
            d_node = path_bw[0][i+1]
            GG[s_node][d_node][0]['bw'] += path_bw[1] #e.g. node1-node2 - add path_bw[1] to the bw parameter in the network model
    return 0                                              #GG to the link under s_node to its neighboring d_node
                                                  #in the next iteration at the same bw, to the network model bw between node2 and node3.

def present_output():
    global sim_type
    output = []
    for s_node in cpnx.nodes():
        for n_node in GG[s_node]:   #n_node neighboring node
            if sim_type == 1:
                # s = s_node+";"+n_node+";"+ str(GG[s_node][n_node][0]['bw'])
                s = (s_node+";"+n_node+";", GG[s_node][n_node][0]['bw'])
                output.append(s)
            elif sim_type == 2:
                # s = s_node+";"+n_node+";"+str(GG[s_node][n_node][0]['bw2'][0])+";" + str(GG[s_node][n_node][0]['bw2'][1])
                s = (s_node+";"+n_node+";", GG[s_node][n_node][0]['bw2'][0], str(GG[s_node][n_node][0]['bw2'][1]))
                output.append(s)

    output.sort(key = lambda tup:tup[1], reverse=True)
    print(output)
    return output

import datetime
import os.path

def write_to_excel(output):
    global sim_type

    s = str(datetime.date.today())+"_output_sim_type_" + str(sim_type)+".csv"

    if (os.path.isfile(s)):
        os.remove(s)
        print("File removed!")

    with open(s, 'a') as outcsv:
        writer = csv.writer(outcsv, delimiter=';', quotechar='|')
        for row in output:
            writer.writerow([row])
    return s

import os

def vanilla_sim(cpnx):
    global sim_type
    set_bw_to_zero()
    demand_d = calc_spf(D)   #calculate shortest paths
    calc_bw(demand_d)
    output = present_output()
    s= write_to_excel(output)

    easygui.msgbox('Simulation Complete!', 'Simulation Complete!')

    # print("s is")
    # os.system("open -a 'Microsoft Excel.app'", s)

    sim_type = cpnxgui()


def single_link_loss(cpnx):
    global sim_type
    create_bw2(GG)
    i = 0
    easygui.msgbox('Simulation Started', 'Simulation Started')
    for edge in list(cpnx.edges()):

        if i< cpnx.number_of_edges():   #Chance this parameter to a small number if you would like a quick run for testing
            set_bw_to_zero()
            cpnx.remove_edge(edge[0], edge[1])
            cpnx.remove_edge(edge[1], edge[0])

            demand_d = calc_spf(D)                          #create an array of  (path, bw tuple)
            calc_bw(demand_d)                               #creates aggregate bw for each edge
            set_bw_to_max(GG, str(edge))                    #compare and set the larger value between bw and bw2 to bw2

            cpnx.add_edge(edge[0],edge[1])
            cpnx.add_edge(edge[1],edge[0])
            i+=1

    output = present_output()
    write_to_excel(output)
    easygui.msgbox('Simulation Complete!', 'Simulation Complete!')
    sim_type = cpnxgui()
#    sim_type = cpnxgui()


sim_type = cpnxgui()                #start with simgui
