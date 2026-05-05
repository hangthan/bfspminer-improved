import math
from typing import Dict, List, Optional, Any

class TreeObject:
    """
    Represents a node in the Inverted T0 Tree.
    """
    def __init__(self, value: str, parent: Optional['TreeObject'], batch_time: int, time: Optional[int] = None):
        self.value = value
        self.parent = parent
        self.time_stamps: List[int] = []
        self.count = 1
        self.batch_count = 1
        self.tid = batch_time
        
        if time is not None:
            self.time_stamps.append(time)
            
        # Using dictionary for O(1) child lookups instead of O(N) list search in Java
        self.children: Dict[str, 'TreeObject'] = {}

    def get_value(self) -> str:
        return self.value

    def get_count(self) -> int:
        return self.count

    def contains_time(self, x: int) -> bool:
        return x in self.time_stamps


class InvertedT0Tree:
    """
    Equivalent to PatternBuilder in the original Java implementation.
    Constructs and maintains the Inverted T0 Tree and extracts patterns.
    """
    def __init__(self, max_pattern_length: int):
        self.max_pattern_length = max_pattern_length
        self.events: List[str] = []
        self.head = TreeObject("root", None, 0)
        self.head.count = 0  # Root has count 0 initially

    def add_event(self, event_label: str, batch: int) -> None:
        """
        Adds a new event and updates the tree according to Algorithm 1 & 2.
        """
        self.events.append(event_label)
        current_time = len(self.events) - 1
        
        # Build pattern suffix
        pattern_str = self.events[-1]
        for i in range(1, self.max_pattern_length):
            if current_time - i >= 0:
                pattern_str = self.events[current_time - i] + "," + pattern_str
                
        pattern_list = pattern_str.split(",")
        pattern_list.reverse()  # Invert order for T0 tree
        
        visited_nodes = set()
        self._add_list_to_tree(pattern_list, current_time, batch, self.head, visited_nodes)
        self.head.count = len(self.events)  # Total events processed

    def add_event_with_patterns(self, event_label: str, patterns: List[List[str]], batch: int) -> None:
        """
        Adds a new event and updates the tree with multiple patterns (for episode mining).
        """
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
                if id(current_node) not in visited_nodes:
                    current_node.count += 1
                    visited_nodes.add(id(current_node))
                if is_last:
                    if current_time not in current_node.time_stamps:
                        current_node.time_stamps.append(current_time)
            else:
                if is_last:
                    new_node = TreeObject(item, current_node, batch, current_time)
                else:
                    new_node = TreeObject(item, current_node, batch)
                current_node.children[item] = new_node
                current_node = new_node
                visited_nodes.add(id(current_node))

    def prune(self, batch: int, alpha: float, eps: float, delta: int) -> None:
        """
        SS-BE Prune strategy.
        """
        l = len(self.events)
        self._ssbe_prune(self.head, batch, alpha, eps, l, delta)

    def _ssbe_prune(self, t: TreeObject, batch: int, alpha: float, eps: float, l: int, delta: int) -> None:
        children_keys = list(t.children.keys())
        for key in children_keys:
            child = t.children[key]
            last_prune = child.tid
            last_prune = last_prune - (last_prune % delta)
            b = batch - last_prune
            b_prime = b - child.batch_count
            
            if child.count + b_prime * (math.ceil(alpha * l) - 1) <= eps * b * l:
                del t.children[key]
            else:
                self._ssbe_prune(child, batch, alpha, eps, l, delta)

    def extract_patterns(self, min_support_ratio: float, iteration: int) -> List[Dict[str, Any]]:
        """
        Extracts frequent patterns from the tree using DFS.
        Replaces the complex string manipulation in Java.
        """
        patterns = []
        root_count = self.head.count
        if root_count == 0:
            return patterns

        def dfs(node: TreeObject, current_path: List[str]):
            for key, child in node.children.items():
                path = current_path + [key]
                support = child.count / root_count
                
                if support >= min_support_ratio:
                    # Calculate confidence: count(path) / count(path[:-1])
                    conf = child.count / node.count if node != self.head else 0.0
                    
                    # Pattern is inverted in tree, so we reverse it back
                    actual_pattern = list(reversed(path))
                    update = (iteration in child.time_stamps)
                    
                    patterns.append({
                        'pattern': tuple(actual_pattern),
                        'pattern_str': ";".join(actual_pattern),
                        'count': child.count,
                        'support': support,
                        'confidence': conf,
                        'update': update
                    })
                    dfs(child, path)

        dfs(self.head, [])
        return patterns
