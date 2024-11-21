"""
Author: Daniel Busarello
"""

import matplotlib.pyplot as plt
import networkx as nx
from tkinter import simpledialog, messagebox
import time
import logging
import easygui
import json

from utils.resource_allocation_graph_builder import ResourceAllocationGraph

class GraphResolver():
    def __init__(self):
        # Graph configurations
        self.init()
        self.unbind_default_keymap('keymap.pan', 'p')
        self.unbind_default_keymap('keymap.save', 's')
        self.unbind_default_keymap('keymap.legends', 'l')

        # Logging configuration
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        # Graphics configuration for nodes
        self.fig, self.ax = plt.subplots(figsize=(9, 7))
        self.fig.suptitle('Grafo de Alocação de Recursos', fontsize=12, fontweight='bold')
        self.ax.set_title(self.get_keys_legends(), {'fontsize': 10})
        
        self.legend = self.fig.text(0.1, 0.02, "Adicionando Processos (P)", ha='left', va='center', fontsize=14, color='gray')
        
        plt.gcf().canvas.mpl_connect('button_press_event', self.on_click)
        plt.gcf().canvas.mpl_connect('key_press_event', self.key_press)

        plt.xlim(0, 10)
        plt.ylim(0, 10)

        plt.ioff()
        plt.show()
        
    def init(self):
        self.G = nx.MultiDiGraph()
        self.pos = {}
        self.edge_label_pos = {}
        self.process_node_counter = 1
        self.resource_node_counter = 1
        self.edge_start = None
        self.clicked_node = None
        self.node_colors = {}
        self.node_shapes = {}
        self.element_type = "P"
        self.legend = None
        
    def unbind_default_keymap(self, keymap_name, key):   
        keymap = plt.rcParams.get(keymap_name, [])
        if key in keymap:
            keymap.remove(key)
            plt.rcParams[keymap_name] = keymap
        
    def draw_graph(self):
        """
        Draws the graph.
        """
        plt.cla()
        self.ax.set_title(self.get_keys_legends(), {'fontsize': 10})
        
        plt.xlim(0, 10)
        plt.ylim(0, 10)
               
        process_nodes = [node for node in self.G.nodes() if node.startswith('P')]
        resource_nodes = [node for node in self.G.nodes() if node.startswith('R')]
        
        # Processes as squares
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=process_nodes, node_size=500, 
                            node_color=[self.node_colors.get(node, 'skyblue') for node in process_nodes], 
                            node_shape='s')
        
        # Resources as circles
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=resource_nodes, node_size=500, 
                            node_color=[self.node_colors.get(node, 'skyblue') for node in resource_nodes], 
                            node_shape='o')
        
        label_pos_custom = {node: (x, y - 0.45) if 'R' in node else (x, y) for node, (x, y) in self.pos.items()}
        nx.draw_networkx_labels(self.G, label_pos_custom, font_size=10)
        nx.draw_networkx_edges(self.G, self.pos, edgelist=self.G.edges(), arrowstyle='->', arrowsize=20, connectionstyle='arc3,rad=0.2')

        # Parallel edges 
        edge_counts = {}
        for u, v in self.G.edges():
            if (u, v) not in edge_counts:
                edge_counts[(u, v)] = 0
            edge_counts[(u, v)] += 1
        
        edge_labels = {edge: count for edge, count in edge_counts.items()}
        
        nx.draw_networkx_edge_labels(self.G, self.pos, label_pos=0.15, font_size=6, verticalalignment="center_baseline", edge_labels=edge_labels)

        self.fig.canvas.draw_idle()
        plt.pause(0.2)

    def create_node(self, x, y):
        """
        Creates the nodes based on the type of node (process or resource).
        
        :param x: X coordinate of the node.
        :param y: Y coordinate of the node.
        """
        if self.element_type == "P":
            node_name = f'P{self.process_node_counter}'
            self.G.add_node(node_name)
            self.pos[node_name] = (x, y)
            self.process_node_counter += 1
            self.draw_graph()
           
        elif self.element_type == "R":
            resource_capacity = simpledialog.askinteger("Capacidade do Recurso", "Informe a capacidade do recurso:")
            if resource_capacity is None:
                return
                
            node_name = f'R{self.resource_node_counter} ({resource_capacity})'
            self.G.add_node(node_name)
            self.pos[node_name] = (x, y)
            self.resource_node_counter += 1
            self.draw_graph()
            
    def update_legend(self, message):
        self.legend = self.fig.text(0.1, 0.02, message, ha='left', va='center', fontsize=14, color='gray')
        self.draw_graph()
            
    def on_click(self, event):
        """
        Handles interactions with the canvas.
        """
        if event.xdata is None or event.ydata is None:
            return  # Ignore clicks outside the plot
        
        if event.button == 1:  # Left mouse button click
            self.create_node(x=event.xdata, y=event.ydata)
        
        elif event.button == 3:  # Right mouse button click
            self.clicked_node = None
            min_distance = float('inf')
            for node, (x, y) in self.pos.items():
                distance = ((x - event.xdata)**2 + (y - event.ydata)**2)**0.5
                if distance < min_distance and distance < 0.5:  # Adjust sensitivity for node selection
                    min_distance = distance
                    self.clicked_node = node

            if self.clicked_node:
                if self.edge_start is None:
                    self.edge_start = self.clicked_node
                    self.node_colors[self.clicked_node] = 'green'
                    self.logger.info(f"Start node selected: {self.edge_start}")
                    self.draw_graph()
                else:
                    if self.edge_start[0] == self.clicked_node[0] or self.edge_start == self.clicked_node:
                        self.node_colors[self.edge_start] = 'skyblue'
                        self.edge_start = None
                        self.clicked_node = None
                        self.draw_graph()
                        return
                    
                    self.node_colors[self.edge_start] = 'skyblue'
                    edge_end = self.clicked_node
                    self.G.add_edge(self.edge_start, edge_end)
                    self.edge_start = None
                    self.draw_graph()

        elif event.button == 2 and self.clicked_node:  # Middle mouse button click
            # Delete the node and its edges
            self.logger.info(f"Deleting node: {self.clicked_node}")
            self.G.remove_node(self.clicked_node)
            self.pos.pop(self.clicked_node)
            self.edge_start = None
            self.clicked_node = None
            self.draw_graph()
            
    def get_keys_legends(self):
        return "\n".join([
            "P - Adicionar processo | R - Adicionar recurso | M - Mover nó | I - Informações do grafo",
            "X - Resolver grafo | S - Salvar grafo | L - Ler grafo | Z - Reiniciar | A - Instruções"])
        
    def key_press(self, event):
        """
        Handles keys interactions.
        """
        if event.key.lower() == 'p':
            self.element_type = "P"
            self.legend.remove()
            self.update_legend('Adicionando Processos (P)')
        elif event.key.lower() == 'r':
            self.element_type = "R"
            self.legend.remove()
            self.update_legend('Adicionando Recursos (R)')
        elif event.key.lower() == 'i':
            self.print_graph_information()
        elif event.key.lower() == 'x':
            self.legend.remove()
            self.update_legend('Executando...')
            self.finalize()
        elif event.key.lower() == 's':
            self.save_graph()
        elif event.key.lower() == 'l':
            self.read_graph()
        elif event.key.lower() == 'z':
            if self.legend is not None:
                self.legend.remove()
            self.init()
            self.update_legend("Adicionando Processos (P)") if self.element_type == "P" else self.update_legend("Adicionando Recursos (R)")
            self.draw_graph()
        elif event.key.lower() == 'm':
            self.on_move(event)
        elif event.key.lower() == 'a':
            self.print_instructions()
    
    def remove_edge(self, node):
        """
        Removes the edges from the graph, based on the node relation.
        
        :param node: The node to remove edges.
        """
        edges = list(self.G.edges())
        
        for edge in edges:
            if node in edge:
                self.logger.info(f"Removendo aresta {edge}")
                self.G.remove_edge(edge[0], edge[1])
                
        self.draw_graph()
        
    def print_graph_information(self):
        easygui.msgbox(f"Graph nodes: {self.G.nodes()}\nGraph edges: {self.G.edges()}\nGraph edges | Total: {len(self.G.edges())}: {self.G.edges()}")

        self.logger.info(f"Graph nodes: {self.G.nodes()}")
        self.logger.info(f"Graph edges | Total: {len(self.G.edges())}: {self.G.edges()}")

    def print_instructions(self):
        easygui.msgbox(
            title="Instruções",
            msg="""
            1.Pressione P para selecionar a opção de adicionar um processo, depois clique no gráfico com o botão esquerdo do mouse para adicionar.\n
            2.Pressione R para selecionar a opção de adicionar um recurso, depois clique no gráfico com o botão esquerdo do mouse para adicionar. Uma caixa de diálogo irá ser exibida pedindo a capacidade do recurso, informe um valor numérico e clique em OK\n
            3.Para selecionar um nó, clique com o botão direito do mouse sobre o nó.\n
            4.Com o nó selecionado, clique com o botão direito em outro nó para adicionar um aresta.\n
            5.É possível mover o nó selecionado, clicando a tecla M, assim, o nó selecionado será movido para a posição do mouse.\n
            6.Para excluir um nó, é preciso seleciona-lo e clicar com o botão do mouse "Scroll" (do meio). As arestas ligadas a esse nó também serão excluídas.\n
            7.Pressione I para exibir informações do grafo (Arestas e Nós).\n
            8.Pressione X para executar a redução do grafo.\n
            9.Pressione S para salvar o grafo.\n
            10.Pressione L para ler um grafo salvo.\n
            11.Pressione Z para reiniciar o grafo.\n
            """
        )
       
    def extract_graph_information(self):
        """
        Extracts the graph information.

        :return (processes nodes, resources nodes, resources availability and edges).
        """
        processes_nodes = []
        resources_nodes = []
        resources_availability = {}
        
        for node in self.G.nodes():
            if 'P' in node:
                processes_nodes.append(node)  
            else:
                resources_nodes.append(node)
                key = node.split('(')
                resources_availability[node] = int(key[1].replace(')', ''))
        
        edges = []
        for edge in self.G.edges():
            edges.append((edge[0], edge[1]))
        
        return processes_nodes, resources_nodes, resources_availability, edges
        
    def finalize(self):
        """
        Executes the algorithm to reduce the graph.
        """
        processes_nodes, resources_nodes, resources_availability, edges = self.extract_graph_information()
        
        self.logger.info(f"Processes nodes: {processes_nodes}")
        self.logger.info(f"Resources nodes: {resources_nodes}")
        self.logger.info(f"Graph edges: {edges}")
        self.logger.info(f"Resource availability: {resources_availability}")
        
        if (edges == []):
            self.logger.info(f"Nenhuma aresta encontrada")
            self.legend.remove()
            self.update_legend("Adicionando Processos (P)") if self.element_type == "P" else self.update_legend("Adicionando Recursos (R)")
            return
        
        rag = ResourceAllocationGraph(processes_nodes, resources_nodes, resources_availability, edges)
        request_list = rag.create_request_list()
        allocation_list = rag.create_allocation_list()
        
        self.detect_and_resolve_deadlock(allocation_list, request_list, resources_availability)
    
    def save_graph(self):
        """
        Saves the current graph to a txt/json file.
        """
        processes_nodes, resources_nodes, _, edges = self.extract_graph_information()
        
        file_path = easygui.filesavebox(default='*.txt')
                
        with open(f'{file_path}', 'w') as file:
            content = {}
            content["nodes"] = processes_nodes + resources_nodes
            content["edges"] = edges
            content["node_positions"] = self.pos
            content["node_indexes"] = {
                "process": self.process_node_counter,
                "resource": self.resource_node_counter
            }
            
            json.dump(content, file, indent=4)
    
    def read_graph(self):
        """
        Reads a graph from a txt/json file.
        """
        file_path = easygui.fileopenbox(default='*.txt')
        
        try:
            with open(file_path, 'r') as file:
                content = json.loads(file.read())
                self.init()
                
                for node in content["nodes"]:
                    self.G.add_node(node)
                    self.pos[node] = (content["node_positions"][node][0], content["node_positions"][node][1])
                
                self.process_node_counter = content["node_indexes"]["process"] + 1
                self.resource_node_counter = content["node_indexes"]["resource"] + 1
                
                for edge in content["edges"]:
                    self.G.add_edge(edge[0], edge[1])
                
                self.draw_graph()
        except Exception as error:
            self.logger.exception(error)
    
    def on_move(self, event):
        """
        Handles the node move
        
        :param event: event from matplotlib
        """
        if self.clicked_node is not None and event.inaxes:
            x, y = event.xdata, event.ydata
            self.pos[self.clicked_node] = (x, y)
            self.draw_graph()
            self.logger.info(f"New {self.clicked_node} position: {x, y}")
    
    # Graph resolver functions
    def choose_process_to_remove(self, request: dict[str, list[str]], resource_capacity: dict[str, int]) -> str:
        """
        Chooses a process to remove based on which removal would free the most capacity
        and unlock the execution of other processes.
        
        :param request: Dictionary of processes with waiting requested resources.
        :param resource_capacity: Dictionary with the available capacity of each resource.
        :return: The process name to be removed.
        """
        
        candidates = []
        process_to_remove = None
        
        # Verifies if a requested resource has capacity to be allocated
        for process in request.keys():
            for res in request[process]:
                if resource_capacity[res] > 0 and resource_capacity[res] >= sum(1 for r in request[process] if r == res and resource_capacity[res] > 0):
                    candidates.append(process)
        
        # If any process has all the requested resources, choose to be removed
        for process in candidates:
            if all(resource_capacity[r] > 0 for r in request[process]):
                process_to_remove = process
                break

        # If no process has all the requested resources, it has a Deadlock
        if candidates == [] or (process_to_remove == None and len(candidates) > 0):
            return None

        return process_to_remove

    def calculate_remaining_capacity(self, allocation: dict[str, dict[str, int]], resource_capacity: dict[str, int]):
        """
        Verifies the remaining capacity of resources based on the allocation list.
        
        :param allocation: Dictionary of processes with the allocated resources and their quantities.
        :param resource_capacity: Dictionary with the total capacity of each resource.
        :return: Dictionary of remaining capacity.
        """
        
        resource_capacity_remaining = resource_capacity.copy()
        
        for process in allocation:
            for resource in allocation[process]:
                resource_capacity_remaining[resource] -= 1

        return resource_capacity_remaining

    def detect_and_resolve_deadlock(self, allocation: dict[str, dict[str, int]], request: dict[str, list[str]], resource_capacity: dict[str, int]) -> list[str]:
        """
        Detects and removes a deadlock in a Resource Allocation Graph (RAG) using graph reduction.
        
        :param allocation: Dictionary of processes with the allocated resources and their quantities {process: {resource: allocated_quantity}}.
        :param request: Dictionary of processes with the waiting requested resources {process: [requested_resource]}.
        :param resource_capacity: Dictionary with the total capacity of each resource {resource: available_capacity}.
        :return: List of processes that were removed.
        """
        processes = list(allocation.keys())
        removed_processes = []
        
        resource_capacity_copy = self.calculate_remaining_capacity(allocation, resource_capacity)
        
        while True:
            removable_process = None
            
            # Find processes that can be removed (those that don't have pending requests)
            for process in processes:
                if request[process] == []:
                    removable_process = process
                    break
            
            if removable_process is None:
                break
            
            processes.remove(removable_process)
            self.free_allocation(allocation, request, removable_process, resource_capacity_copy)

        while processes:
            # Call to the heuristic function to choose a process to be removed
            process_to_remove = self.choose_process_to_remove(request, resource_capacity_copy)
            
            # If deadlock was found
            if process_to_remove is None:
                for process in processes:
                    self.node_colors[process] = "red"
                self.draw_graph()
                messagebox.showwarning(title="Deadlock", message=f"Deadlock encontrado nos processos {processes}")
                self.legend.remove()
                self.update_legend("Adicionando Processos (P)") if self.element_type == "P" else self.update_legend("Adicionando Recursos (R)")
                break
            
            print(f"Removendo o processo {process_to_remove}")
            removed_processes.append(process_to_remove)
            
            # Remove the process from processes list and free the resource allocation
            processes.remove(process_to_remove)
            self.free_allocation(allocation, request, process_to_remove, resource_capacity_copy) 
            
        if processes == []:
            self.legend.remove()
            self.update_legend("Processo finalizado.")
            time.sleep(1)

        self.logger.info("Processo finalizado.")
        self.legend.remove()
        self.update_legend("Adicionando Processos (P)") if self.element_type == "P" else self.update_legend("Adicionando Recursos (R)")
        return removed_processes

    def free_allocation(self, allocation: dict[str, list[str]], request: dict[str, list[str]], process_to_remove: str, resource_capacity: dict[str, int]) -> None:
        """
        Releases the allocated resources of a removed process and updates resource capacities.
        
        :param allocation: Dictionary of processes with allocated resources (as lists).
        :param request: Dictionary of processes with waiting requested resources.
        :param processes: List of process names.
        :param process_to_remove: Name of the process to be removed.
        :param resource_capacity: Dictionary with the total capacity of each resource.
        """
        for resource in allocation[process_to_remove]:
            resource_capacity[resource] += 1  # Release one unit of the resource

        del allocation[process_to_remove]
        del request[process_to_remove]
        
        self.remove_edge(process_to_remove)
        time.sleep(3)
    
if __name__ == "__main__":
    app = GraphResolver()