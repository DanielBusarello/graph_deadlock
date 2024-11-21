class ResourceAllocationGraph:
    def __init__(self, processes, resources, availability, edges):
        """
        Inicializa a classe com os nós de processos, nós de recursos, disponibilidade dos recursos e arestas.
        
        :param processes: Lista de nós de processos (ex: ["P1", "P2", "P3"])
        :param resources: Lista de nós de recursos (ex: ["R1", "R2", "R3"])
        :param availability: Dicionário de disponibilidade de recursos (ex: {"R1": 2, "R2": 3, "R3": 2})
        :param edges: Lista de arestas que conectam processos e recursos
                      ex: [("P1", "R2"), ("R1", "P2"), ...]
        """
        self.processes = processes
        self.resources = resources
        self.availability = availability
        self.edges = edges
        self.adjacency_list = {}

        self.initialize_adjacency_list()

    def initialize_adjacency_list(self):
        """Initializes the adjacency list."""
        for process in self.processes:
            self.adjacency_list[process] = []

        for resource in self.resources:
            self.adjacency_list[resource] = []

        for edge in self.edges:
            self.adjacency_list[edge[0]].append(edge[1])

        print("Lista de Adjacência", self.adjacency_list)

    def create_request_list(self):
        """Creates the resource request dictionary for each process."""
        request_list = {process: [] for process in self.processes}

        for process in self.processes:
            for edge in self.adjacency_list[process]:
                request_list[process].append(edge)

        print("Lista de Requisições", request_list)
        return request_list
    
    def create_allocation_list(self):
        """Creates the resource allocation dictionary for each process."""
        allocation_list = {process: [] for process in self.processes}

        for resource in self.resources:
            for process in self.adjacency_list[resource]:
                allocation_list[process].append(resource)

        print("Lista de Alocações", allocation_list)
        return allocation_list