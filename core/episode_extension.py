from typing import List, Set, Tuple

class EpisodeMiningExtension:
    """
    Extends sequence mining to support gap constraints and window-based episodes.
    Optimized to limit search space and use early pruning.
    """
    def __init__(self, max_gap: int = 1, window_size: int = 5):
        self.max_gap = max_gap
        self.window_size = window_size
        
    def generate_patterns_with_gap(self, events: List[str], current_time: int, max_pattern_length: int) -> List[List[str]]:
        patterns = []
        if current_time >= len(events):
            return patterns
            
        target = events[current_time]
        patterns.append([target])
        
        if max_pattern_length <= 1:
            return patterns

        # Optimized gap pattern generation with Hard Limit for Early Stopping
        start_idx = max(0, current_time - self.window_size + 1)
        paths = [([target], current_time)]
        valid_patterns_set = set([(target,)])
        
        max_combinations = 50  # Hard limit to prevent O(2^W) combinatorial explosion
        
        for _ in range(max_pattern_length - 1):
            new_paths = []
            for current_pattern, last_idx in paths:
                end_search = max(start_idx, last_idx - self.max_gap)
                for i in range(last_idx - 1, end_search - 1, -1):
                    new_pattern = current_pattern + [events[i]]
                    
                    tup = tuple(new_pattern)
                    if tup not in valid_patterns_set:
                        valid_patterns_set.add(tup)
                        patterns.append(new_pattern)
                        new_paths.append((new_pattern, i))
                        
                    if len(new_paths) >= max_combinations:
                        break
                if len(new_paths) >= max_combinations:
                    break
            paths = new_paths
            if not paths:
                break
                
        return patterns
