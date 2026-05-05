import math
from typing import Dict, List, Optional, Any

class TreeObject:
    __slots__ = ['value', 'parent', 'time_stamps', 'count', 'batch_count', 'tid', 'children']
    
    def __init__(self, value: str, parent: Optional['TreeObject'], batch_time: int, time: Optional[int] = None):
        self.value = value
        self.parent = parent
        self.time_stamps: List[int] = []
        self.count = 1
        self.batch_count = 1
        self.tid = batch_time
        if time is not None:
            self.time_stamps.append(time)
        self.children: Dict[str, 'TreeObject'] = {}

class InvertedT0Tree:
    def __init__(self, max_pattern_length: int):
        self.max_pattern_length = max_pattern_length
        self.events: List[str] = []
        self.head = TreeObject("root", None, 0)
        self.head.count = 0

    def add_event(self, event_label: str, batch: int) -> None:
        self.events.append(event_label)
        current_time = len(self.events) - 1
        
        pattern_list = [self.events[current_time - i] for i in range(self.max_pattern_length) if current_time - i >= 0]
        
        visited_nodes = set()
        self._add_list_to_tree(pattern_list, current_time, batch, self.head, visited_nodes)
        self.head.count = len(self.events)

    def add_event_with_patterns(self, event_label: str, patterns: List[List[str]], batch: int) -> None:
        self.events.append(event_label)
        current_time = len(self.events) - 1
        
        visited_nodes = set()
        for pattern in patterns:
            self._add_list_to_tree(pattern, current_time, batch, self.head, visited_nodes)
        self.head.count = len(self.events)

    def _add_list_to_tree(self, pattern: List[str], current_time: int, batch: int, current_node: TreeObject, visited_nodes: set) -> None:
        for i, item in enumerate(pattern):
            is_last = (i == len(pattern) - 1)
            
            if item in current_node.children:
                current_node = current_node.children[item]
                node_id = id(current_node)
                if node_id not in visited_nodes:
                    current_node.count += 1
                    visited_nodes.add(node_id)
                if is_last and (not current_node.time_stamps or current_node.time_stamps[-1] != current_time):
                    current_node.time_stamps.append(current_time)
            else:
                new_node = TreeObject(item, current_node, batch, current_time if is_last else None)
                current_node.children[item] = new_node
                current_node = new_node
                visited_nodes.add(id(current_node))

    def prune(self, batch: int, alpha: float, eps: float, delta: int) -> None:
        l = len(self.events)
        self._ssbe_prune(self.head, batch, alpha, eps, l, delta)

    def _ssbe_prune(self, t: TreeObject, batch: int, alpha: float, eps: float, l: int, delta: int) -> None:
        children_keys = list(t.children.keys())
        for key in children_keys:
            child = t.children[key]
            last_prune = child.tid - (child.tid % delta)
            b = batch - last_prune
            b_prime = b - child.batch_count
            
            if child.count + b_prime * (math.ceil(alpha * l) - 1) <= eps * b * l:
                del t.children[key]
            else:
                self._ssbe_prune(child, batch, alpha, eps, l, delta)

    def extract_patterns(self, min_support_ratio: float, iteration: int) -> List[Dict[str, Any]]:
        patterns = []
        root_count = self.head.count
        if root_count == 0:
            return patterns

        def dfs(node: TreeObject, current_path: List[str]):
            for key, child in node.children.items():
                path = current_path + [key]
                support = child.count / root_count
                if support >= min_support_ratio:
                    conf = child.count / node.count if node != self.head else 0.0
                    actual_pattern = tuple(reversed(path))
                    patterns.append({
                        'pattern': actual_pattern,
                        'pattern_str': ";".join(actual_pattern),
                        'count': child.count,
                        'support': support,
                        'confidence': conf,
                        'update': (iteration in child.time_stamps)
                    })
                    dfs(child, path)

        dfs(self.head, [])
        return patterns
