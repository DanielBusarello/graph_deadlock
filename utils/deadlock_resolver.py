def choose_process_to_remove(allocation: dict[str, list[str]], request: dict[str, list[str]], resource_capacity: dict[str, int]) -> str:
    """
    Chooses a process to remove based on which removal would free the most capacity
    and unlock the execution of other processes.
    
    :param allocation: Dictionary of processes with allocated resources (as lists).
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

    # If no process has all the requested resources, it has a Deadlock,then choose the process with the lowest allocation
    if candidates == [] or (process_to_remove == None and len(candidates) > 0):
        process_to_remove = min(allocation.keys(), key=lambda p: len(allocation[p]))

    return process_to_remove

def calculate_remaining_capacity(allocation: dict[str, dict[str, int]], resource_capacity: dict[str, int]):
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

def detect_and_resolve_deadlock(allocation: dict[str, dict[str, int]], request: dict[str, list[str]], resource_capacity: dict[str, int]) -> list[str]:
    """
    Detects and removes a deadlock in a Resource Allocation Graph (RAG) using graph reduction.
    
    :param allocation: Dictionary of processes with the allocated resources and their quantities {process: {resource: allocated_quantity}}.
    :param request: Dictionary of processes with the waiting requested resources {process: [requested_resource]}.
    :param resource_capacity: Dictionary with the total capacity of each resource {resource: available_capacity}.
    :return: List of processes that were removed.
    """
    processes = list(allocation.keys())
    removed_processes = []
    
    resource_capacity_copy = calculate_remaining_capacity(allocation, resource_capacity)
    
    while True:
        removable_process = None
        
        # Find processes that can be removed (those that don't have pending requests)
        for process in processes:
            if request[process] == []:
                removable_process = process
                print(f"Removendo o processo {removable_process}")
                break
        
        if removable_process is None:
            break
        
        processes.remove(removable_process)
        free_allocation(allocation, request, processes, removable_process, resource_capacity_copy)

    # Deadlock case
    while processes:
        print(f"Deadlock detectado nos processos: {processes}")
        
        # Call to the heuristic function to choose a process to be removed
        process_to_remove = choose_process_to_remove(allocation, request, resource_capacity_copy)
        print(f"Removendo o processo {process_to_remove}")
        removed_processes.append(process_to_remove)
        
        # Remove the process from processes list and free the resource allocation
        processes.remove(process_to_remove)
        free_allocation(allocation, request, processes, process_to_remove, resource_capacity_copy) 

    print("Deadlock resolvido.")
    return removed_processes

def free_allocation(allocation: dict[str, list[str]], request: dict[str, list[str]], process_to_remove: str, resource_capacity: dict[str, int]) -> None:
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