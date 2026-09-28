"""Search algorithms for pathfinding."""

from collections import deque
from typing import List, Tuple, Dict, Optional


def bfs(graph: Dict, start, goal) -> Optional[List]:
    """
    Breadth-First Search.

    Args:
        graph: Adjacency list representation
        start: Starting node
        goal: Goal node

    Returns:
        Path from start to goal, or None if not found
    """
    visited = {start}
    queue = deque([(start, [start])])

    while queue:
        node, path = queue.popleft()

        if node == goal:
            return path

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None


def dfs(graph: Dict, start, goal) -> Optional[List]:
    """
    Depth-First Search.

    Args:
        graph: Adjacency list representation
        start: Starting node
        goal: Goal node

    Returns:
        Path from start to goal, or None if not found
    """
    visited = {start}
    stack = [(start, [start])]

    while stack:
        node, path = stack.pop()

        if node == goal:
            return path

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append((neighbor, path + [neighbor]))

    return None
