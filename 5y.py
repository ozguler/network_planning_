
import networkx as nx
import matplotlib.pyplot as plt
import csv
from cpn import G
from demand_real_new import D

cpnx = nx.MultiDiGraph(G)
GG = G
# print (cpnx.nodes())
# print (cpnx.edges())
#
# print("Number of nodes is:", cpnx.number_of_nodes())
# print("Number of edges is:", cpnx.number_of_edges())
# path_f = nx.dijkstra_path(cpnx, "PE90TZL23", "PE90ADN03_9K", weight = "distance")
# path_r = nx.dijkstra_path(cpnx, "PE90ADN03_9K", "PE90TZL23", weight = "distance")
# print(path_f)
# print(path_r)
# print("----------------------------------------------------")
# print(cpnx["PE90TZL23"]["3RD90TZL03"])  #this notation corresponds to the link between node PE90TZL23 and node 3RD90TZL03
# print("Traffic demand from PE90TZL23 to PE90PSK23 is", D["PE90TZL23"]["PE90ADN23"], "kbps")
# print("Traffic demand from PE90TZL23 to PE90PSK23 is", D["PE90TZL23"]["PE90GZM23"], "kbps")
# print("----------------------------------------------------")

#set all bw paramters to 0, some values are non-zero in the initial data
def set_bw_to_zero():
    for s_node in cpnx.nodes():
        for n_node in GG[s_node]:
            GG[s_node][n_node][0]['bw'] = 0   #set GG bw to 0, we will use this parameter to aggregate bw's after demand calc


def set_bw_to_maxsim_bw():

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
    for path_bw in demand_d:
        path_bw_len = len((path_bw[0]))
        for i in range (path_bw_len-1): #walk through the node elements for eahc path in demend_d
            s_node = path_bw[0][i]
            d_node = path_bw[0][i+1]
            GG[s_node][d_node][0]['bw'] += path_bw[1] #e.g. node1-node2 - add path_bw[1] to the bw parameter in the network model
    return 0                                              #GG to the link under s_node to its neighboring d_node
                                                  #in the next iteration at the same bw, to the network model bw between node2 and node3.
"""
Present the data
"""
def present_output():
    output = []
    for s_node in cpnx.nodes():
        for n_node in GG[s_node]:   #n_node neighboring node
            s = s_node+";"+n_node+";"+ str(GG[s_node][n_node][0]['bw'])
            output.append(s)
    return output

"""
Write to .xls
"""
def write_to_excel(output):
    with open("output2.csv", 'a') as outcsv:
        writer = csv.writer(outcsv)
        for row in output:
            writer.writerow([row])

"""
Write to excel for link failure sims
What we want to do is write the failed link top most and generate bw at the boom
"""
def write_to_excel_lf(output, edge):
    s = str(edge[0])+"-"+str(edge[1])+".csv"
    with open(s, 'a') as outcsv:
        writer = csv.writer(outcsv)
        for row in output:
            writer.writerow([row])


import xlwt

def write_to_excel_lff(LL):
    book = xlwt.Workbook(encoding="utf-8")
    for keyx in LL.keys():
        sheetx = book.add_sheet(str(keyx))
        i=0
        for row in LL[keyx]:
            sheetx.write(i,0,row)
            i+=1

    book.save("ozguler.xls")
"""
Program Body
"""
set_bw_to_zero()
demand_d = calc_spf(D)   #calculate shortest paths
calc_bw(demand_d)
output = present_output()
#print(output)
write_to_excel(output)

print(cpnx.number_of_nodes(), cpnx.number_of_edges())

"""
Simulate SINGLE LINK FAILURES
Find the demands under single link failure conditions - keep only the max demands store the info for each link and when it occurs
First we need to find the list of links
Put them through a foor loop which removes them from the topology and runs the simulation
"""
#nodes = list(G.keys())

set_bw_to_zero()   #open a clean sheet

def single_link_loss(cpnx):
    LL = {}
    i = 0
    for edge in list(cpnx.edges()):
#    print("removing link", edge[0],edge[1], "and", edge[1], edge[0])
        if i<=5:
#            set_bw_to_zero()
            cpnx.remove_edge(edge[0], edge[1])
            cpnx.remove_edge(edge[1], edge[0])

            demand_d = calc_spf(D)                          #create an array of  (path, bw tuple)
            calc_bw(demand_d)                               #creates aggregate bw for each edge

            output = present_output()
            LL[edge] = output     #This doesn't work as requires too much memory

    #    write_to_excel_lf(output, edge)
        #add the links back before the next iteration
    #    print("adding link", edge[0],edge[1], "and", edge[1], edge[0])
            cpnx.add_edge(edge[0],edge[1])
            cpnx.add_edge(edge[1],edge[0])
            i+=1

    return LL
#.xls'e yazarken en ust row'a remove edilen'link'i
#.en alt satira da

LL = single_link_loss(cpnx)
print(LL)
write_to_excel_lff(LL)
