from typing import List

class EpisodeMiningExtension:
    """
    Extends sequence mining to support gap constraints and window-based episodes.
    """
    def __init__(self, max_gap: int = 1, window_size: int = 5):
        self.max_gap = max_gap
        self.window_size = window_size
        
    def generate_patterns_with_gap(self, events: List[str], current_time: int, max_pattern_length: int) -> List[List[str]]:
        """
        Generates pattern suffixes allowing gaps up to max_gap within window_size.
        Returns a list of pattern lists, where each pattern is REVERSED 
        (e.g., target event is at index 0) for insertion into the Inverted T0 Tree.
        """
        patterns = []
        target = events[current_time]
        
        def dfs(idx: int, current_pattern: List[str], current_length: int):
            if current_length == max_pattern_length:
                return
            
            # Look backwards from idx - 1 down to idx - 1 - max_gap
            start = max(0, idx - 1 - self.max_gap)
            # Constrain by window_size relative to current_time
            start = max(start, current_time - self.window_size + 1)
            
            for i in range(idx - 1, start - 1, -1):
                new_pattern = current_pattern + [events[i]]
                patterns.append(new_pattern)
                dfs(i, new_pattern, current_length + 1)
                
        patterns.append([target])
        dfs(current_time, [target], 1)
        
        return patterns
