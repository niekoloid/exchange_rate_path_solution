# -*- coding: utf-8 -*-
__author__ = 'Sun Sagong'

import re
import sys
import itertools
from collections import defaultdict
from datetime import datetime, timedelta

class Graph:
    
    def __init__(self):
        self.nodes = []
        self.edges = defaultdict(list)
        self.weights = {}
        self.last_updates = {}
    
    def __str__(self):
        res  = "nodes: " + str(self.nodes)
        res += "\nedges: " + str(dict(self.edges))
        res += "\nweights: " + str(self.weights)
        res += "\nlast_updates: " + str(self.last_updates)
        return res
    
    def add_node(self, value):
        self.nodes.append(value)
        # remove duplicates while keeping the same sequence
        self.nodes = sorted(set(self.nodes), key=self.nodes.index)

    def add_edge(self, src_node, dst_node, rate):
        if dst_node not in self.edges[src_node]:
            self.edges[src_node].append(dst_node)
        self.weights[(src_node, dst_node)] = rate

    def update(self, _upd):
        # Example
        # 2017-11-01T09:42:23+00:00 KRAKEN BTC USD 1000.0 0.0009
        
        upd = _upd.split(' ')
        # upd[0]: <timestamp>
        # upd[1]: <exchange>
        # upd[2]: <source_currency>
        # upd[3]: <destination_currency>
        # upd[4]: <forward_factor>
        # upd[5]: <backward_factor>

        timestamp = upd[0]
        year    = int(timestamp[:4])
        month   = int(timestamp[5:7])
        day     = int(timestamp[8:10])
        hour    = int(timestamp[11:13])
        minute  = int(timestamp[14:16])
        second  = int(timestamp[17:19])
        tz      = timestamp[19:25]
        
        if tz[0] == '+':
            delta_hrs = int(tz[1:3])
            delta_min = int(tz[4:6])
        else:
            delta_hrs = -int(tz[1:3])
            delta_min = -int(tz[4:6])
        
        timestamp =  datetime(year, month, day, hour, minute, second) \
                    + timedelta(hours=delta_hrs, minutes=delta_min)
        
        src = upd[1] + '-' + upd[2]
        dst = upd[1] + '-' + upd[3]
        
        pair = src + '->' + dst
        
        # if the update contains new pair, create new key and update timestamp
        if pair not in self.last_updates.keys():
            self.last_updates[pair] = timestamp
        
        # only consider the most recent price update for each src->dst pair
        if self.last_updates[pair] <= timestamp:
            
            self.last_updates[pair] = timestamp
            
            self.add_node(src)
            self.add_node(dst)
            
            self.add_edge(src, dst, float(upd[4]))
            self.add_edge(dst, src, float(upd[5]))
        
            n = []
            for node in self.nodes:
                n.append(node.split("-"))
            
            # create lists that contain exchanges & currencies respectively
            exchanges = [row[0] for row in n]
            ccy       = [row[1] for row in n]
            
            # list up combination of src and dst pairs that have same ccy
            for c_uniq in set(ccy):
                pairs = []
        
                for i, c in enumerate(ccy):
                    if c_uniq == c:
                        node = exchanges[i] + "-" + ccy[i]
                        pairs.append(node)
                
                edges = list(itertools.combinations_with_replacement(pairs, 2))
                
                for edge in edges:
                    if edge[0] != edge[1]:
                        self.add_edge(edge[0], edge[1], 1.0)
                        self.add_edge(edge[1], edge[0], 1.0)
            
    def respond(self, _req):
        # Example
        # EXCHANGE_RATE_REQUEST KRAKEN BTC GDAX USD
        
        req = _req.split(" ")
        # req[0]: EXCHANGE_RATE_REQUEST
        # req[1]: <source_exchange> 
        # req[2]: <source_currency>
        # req[3]: <destination_exchange>
        # req[4]: <destination_currency>
        
        V = self.nodes
        src = req[1] + "-" + req[2]
        dst = req[3] + "-" + req[4]
                
        # return None if node does not exist in the graph.
        try:
            V.index(src)
            V.index(dst)
        except ValueError:
            return None, None, None
            
        # return None if src and dst are identical. 
        if src == dst:
            #sys.stderr.write('src and dst are identical')
            return None, None, None
        
        else:
            # prepare empty len(V) x len(V) lookup tables
            rate_lookup = [[0.0 for x in range(len(V))] for y in range(len(V))]
            next_lookup = [[None for x in range(len(V))] for y in range(len(V))]
            
            # initialize lookup tables by current graph state
            for s, s_str in enumerate(V):
                for d, d_str in enumerate(V): 
                    if d_str in dict(self.edges)[s_str]:
                        rate_lookup[s][d] = dict(self.weights)[(s_str, d_str)]
                        next_lookup[s][d] = d
            
            # modified Floyd-Warshall implementation
            for k in range(0, len(V)):
                for i in range(0, len(V)):
                    for j in range(0, len(V)):
                        if  rate_lookup[i][j] < rate_lookup[i][k] * rate_lookup[k][j]:
                            rate_lookup[i][j] = rate_lookup[i][k] * rate_lookup[k][j]
                            next_lookup[i][j] = next_lookup[i][k]
            
            rate = rate_lookup[V.index(src)][V.index(dst)]
            i_s = V.index(src)
            i_d = V.index(dst)
            
            # return None if path from src to dst does not exist.
            if next_lookup[i_s][i_d] is None:
                #sys.stderr.write('path from src to dst does not exist.')
                return None, None, None
               
            else:
                # initialize path with src
                path = [src]
        
                # traverse paths from src to dst
                while i_s != i_d:
                    i_s = next_lookup[i_s][i_d]
                    path.append(V[i_s])
                
                # generate output string
                res = "BEST_RATES_BEGIN " + req[1] + " " + req[2] + " " \
                                          + req[3] + " " + req[4] + " " \
                                          + str(rate) + "\n"
                
                for i in range(0, len(path)):
                    res += path[i].replace("-",",") + "\n"
                    
                res += "BEST_RATES_END"
                
                # output the response string to stdout
                sys.stdout.write(res)
                return res, rate, path
        
    def run(self):
        
        upd_pattern = re.compile('\d{4}-\d{1,2}-\d{1,2}T' # <timestamp>
                                 '([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]'
                                 '\+([0-1][0-9]|2[0-3]):[0-5][0-9]'
                                 '\s[A-Z]+' # <exchange>
                                 '\s[A-Z]+' # <source_currency>
                                 '\s[A-Z]+' # <destination_currency>
                                 '\s[0-9]+(\.[0-9]*)?'  # <forward_factor>
                                 '\s[0-9]+(\.[0-9]*)?') # <backward_factor>
        
        req_pattern = re.compile('^EXCHANGE_RATE_REQUEST'
                                 '\s[A-Z]+' # <source_exchange>
                                 '\s[A-Z]+' # <source_currency>
                                 '\s[A-Z]+' # <destination_exchange>
                                 '\s[A-Z]') # <destination_currency>
    
        try:
            for line in sys.stdin:
                if upd_pattern.match(line):
                    self.update(line[:-1])
                elif req_pattern.match(line):
                    self.respond(line[:-1])
                else:
                    pass
                    
        except KeyboardInterrupt:
           sys.stdout.flush()
           pass
        
if __name__ == "__main__":
    G = Graph()
    G.run()