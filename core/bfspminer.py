import logging
from typing import List, Dict, Any
from .inverted_t0_tree import InvertedT0Tree
from .adaptive_max_length import AdaptiveMaxPatternLength
from .episode_extension import EpisodeMiningExtension

logger = logging.getLogger(__name__)

class BFSPMiner:
    """
    Python implementation of BFSPMiner algorithm based on the paper:
    BFSPMiner: An Effective and Efficient Batch-Free Algorithm for Mining Sequential Patterns over Data Streams
    """
    def __init__(self, 
                 max_pattern_length: int = 5,
                 pruning: bool = True,
                 delta: int = 1000,
                 batch_length: int = 1000,
                 alpha: float = 0.05,
                 eps: float = 0.1,
                 enable_adaptive: bool = False,
                 enable_gap: bool = False,
                 max_gap: int = 1,
                 window_size: int = 5):
        self.max_pattern_length = max_pattern_length
        self.pruning = pruning
        self.delta = delta
        self.batch_length = batch_length
        self.alpha = alpha
        self.eps = eps
        
        self.enable_adaptive = enable_adaptive
        self.enable_gap = enable_gap
        
        self.tree = InvertedT0Tree(max_pattern_length)
        self.processed_items = 0
        self.batch = 0
        self.pruned = True
        
        self.frequent_patterns = []
        
        # Extensions
        if self.enable_adaptive:
            self.adaptive_length = AdaptiveMaxPatternLength(initial_len=max_pattern_length)
        if self.enable_gap:
            self.episode_extension = EpisodeMiningExtension(max_gap=max_gap, window_size=window_size)

    def feed_item(self, item: str) -> None:
        """
        Feeds a single item to the miner and updates internal state.
        """
        if self.enable_adaptive:
            new_len = self.adaptive_length.update(item)
            self.tree.max_pattern_length = new_len
            self.max_pattern_length = new_len
            
        if self.enable_gap:
            # We temporarily add item to events to allow generate_patterns_with_gap to see it
            self.tree.events.append(item)
            current_time = len(self.tree.events) - 1
            patterns = self.episode_extension.generate_patterns_with_gap(
                self.tree.events, current_time, self.tree.max_pattern_length)
            # Remove it so add_event_with_patterns can append it normally
            self.tree.events.pop()
            self.tree.add_event_with_patterns(item, patterns, self.batch)
        else:
            self.tree.add_event(item, self.batch)
        
        self.processed_items += 1
        if self.processed_items % self.batch_length == 0:
            self.batch += 1
            self.pruned = False
            
        if self.pruning:
            if self.batch % self.delta == 0 and not self.pruned:
                self.tree.prune(self.batch, self.alpha, self.eps, self.delta)
                self.pruned = True

    def get_frequent_patterns(self, min_support: float) -> List[Dict[str, Any]]:
        """
        Retrieves all frequent patterns meeting the minimum support threshold.
        """
        self.frequent_patterns = self.tree.extract_patterns(min_support, self.processed_items - 1)
        self.frequent_patterns.sort(key=lambda x: x['support'], reverse=True)
        return self.frequent_patterns

    def predict_next(self, k: int = 3, min_support: float = 0.01) -> List[str]:
        """
        Predicts the next 'k' items based on the current context (snapshot).
        """
        patterns = self.get_frequent_patterns(min_support)
        if not patterns:
            return [""] * k

        snapshot = self.tree.events[-self.max_pattern_length:] if self.tree.events else []
        snapshot.reverse()
        
        filtered_patterns = []
        for p in patterns:
            pattern_list = list(p['pattern'])
            if len(pattern_list) > 1:
                prefix = pattern_list[:-1]
                
                prefix_reversed = list(reversed(prefix))
                # For basic sequence, prefix must match exact sequence.
                # If gap is enabled, prediction logic could be enhanced to allow gaps in snapshot,
                # but for now we stick to exact prefix matching.
                if len(snapshot) >= len(prefix_reversed) and snapshot[:len(prefix_reversed)] == prefix_reversed:
                    filtered_patterns.append(p)
                    
        filtered_patterns.sort(key=lambda x: x['confidence'], reverse=True)
        
        predictions = []
        for p in filtered_patterns:
            if p['confidence'] > 0.0:
                target = p['pattern'][-1]
                if target not in predictions:
                    predictions.append(target)
            if len(predictions) == k:
                break
                
        if len(predictions) < k:
            for p in patterns:
                if len(p['pattern']) == 1:
                    item = p['pattern'][0]
                    if item not in predictions:
                        predictions.append(item)
                if len(predictions) == k:
                    break
                    
        while len(predictions) < k:
            predictions.append("")
            
        return predictions
