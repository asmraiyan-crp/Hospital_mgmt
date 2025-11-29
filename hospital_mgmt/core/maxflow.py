from collections import deque, defaultdict

class maxflow:
    def __init__(self):
        # Graph: {u: {v: capacity}}
        self.graph = defaultdict(dict)
        # Store flow for each edge
        self.flow = defaultdict(dict)

    def add_edge(self, u, v, capacity):
        self.graph[u][v] = capacity
        self.graph[v].setdefault(u, 0)  # Add reverse edge with 0 capacity
        self.flow[u][v] = 0
        self.flow[v][u] = 0

    # Renamed from 'bsf' to 'bfs' (Breadth First Search)
    def bfs(self, source, sink, parent):
        visited = set()
        queue = deque([source])
        visited.add(source)
        parent.clear()

        while queue:
            u = queue.popleft()
            for v, cap in self.graph[u].items():
                # Check residual capacity
                if v not in visited and cap - self.flow[u][v] > 0:
                    visited.add(v)
                    parent[v] = u
                    if v == sink:
                        return True
                    queue.append(v)
        return False

    def mflow(self, source, sink):
        parent = {}
        max_flow = 0

        # Updated to call self.bfs
        while self.bfs(source, sink, parent):
            path_flow = float('inf')
            s = sink
            while s != source:
                path_flow = min(path_flow, self.graph[parent[s]][s] - self.flow[parent[s]][s])
                s = parent[s]

            v = sink
            while v != source:
                u = parent[v]
                self.flow[u][v] += path_flow
                self.flow[v][u] -= path_flow
                v = u

            max_flow += path_flow

        return max_flow

    def get_flow(self):
        """
        Returns a nested dict: { u: { v: flow_amount } }
        Only includes edges with positive flow.
        """
        assignments = defaultdict(dict)
        for u in self.flow:
            for v, f in self.flow[u].items():
                if f > 0:
                    assignments[u][v] = f
        return assignments