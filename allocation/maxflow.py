from collections import deque

class maxflow():
    def __init__(self):
        self.graph = {}
    def add_edge(self,v,u,capacity):
        if u not in self.graph:
            self.graph[u] = {}
        if v not in self.graph:
            self.graph[v] = {}
        self.graph[u][v] = capacity
        self.graph[v][u] = 0
    def get_flow(self):
        flow = []
        for u in self.graph:
            for v, cap in self.graph[u].items():
                if cap == 0 and v!= 'S' and u != 'T' and not u.startswith('H'):
                    flow.append((u,v))
        return flow
    def bsf(self,source,sink,parent):
        visited = set()
        queue = deque([source])
        visited.add(source)
        while queue:
            u = queue.popleft()
            for v, cap in self.graph[u].items():
                if v not in visited and cap > 0:
                    parent[v] = u
                    if v == sink:
                        return True
                    visited.add(v)
                    queue.append(v)
        return False
    def mflow(self , source, sink):
        parent = {}
        max_flow = 0
        while self.bsf(source,sink,parent):
            path_flow = float('inf')
            v = sink
            while v != source:
                u = parent[v]
                path_flow = min(path_flow,self.graph[u][v])
                v = u
            v = sink
            while v != source:
                u = parent[v]
                self.graph[u][v] -= path_flow
                self.graph[v][u] += path_flow
                v = u
            max_flow += path_flow
        return max_flow
