import logging
from typing import List, Dict, Any
from .config import BFSPMinerConfig
from .inverted_t0_tree import InvertedT0Tree
from .adaptive_max_length import AdaptiveMaxPatternLength
from .episode_extension import EpisodeMiningExtension

logger = logging.getLogger(__name__)

class BFSPMiner:
    """
    Python implementation of BFSPMiner algorithm based on the paper:
    BFSPMiner: An Effective and Efficient Batch-Free Algorithm for Mining Sequential Patterns over Data Streams
    """
    def __init__(self, config: BFSPMinerConfig = None, **kwargs):
        self.config = config if config else BFSPMinerConfig(**kwargs)
        
        self.tree = InvertedT0Tree(self.config.max_pattern_length)
        self.processed_items = 0
        self.batch = 0
        self.pruned = True
        self.frequent_patterns = []
        
        # Extensions
        if self.config.enable_adaptive:
            self.adaptive_length = AdaptiveMaxPatternLength(self.config)
        if self.config.enable_gap:
            self.episode_extension = EpisodeMiningExtension(
                max_gap=self.config.max_gap, 
                window_size=self.config.window_size
            )

    def feed_item(self, item: str) -> None:
        if self.config.enable_adaptive:
            new_len = self.adaptive_length.update(item)
            self.tree.max_pattern_length = new_len
            self.config.max_pattern_length = new_len
            
        if self.config.enable_gap:
            self.tree.events.append(item)
            current_time = len(self.tree.events) - 1
            patterns = self.episode_extension.generate_patterns_with_gap(
                self.tree.events, current_time, self.tree.max_pattern_length)
            self.tree.events.pop()
            self.tree.add_event_with_patterns(item, patterns, self.batch)
        else:
            self.tree.add_event(item, self.batch)
        
        self.processed_items += 1
        if self.processed_items % self.config.batch_length == 0:
            self.batch += 1
            self.pruned = False
            
        if self.config.pruning:
            if self.batch % self.config.delta == 0 and not self.pruned:
                self.tree.prune(self.batch, self.config.alpha, self.config.eps, self.config.delta)
                self.pruned = True

    def get_frequent_patterns(self, min_support: float) -> List[Dict[str, Any]]:
        self.frequent_patterns = self.tree.extract_patterns(min_support, max(0, self.processed_items - 1))
        self.frequent_patterns.sort(key=lambda x: x['support'], reverse=True)
        return self.frequent_patterns

    def predict_next(self, k: int = 3, min_support: float = 0.01) -> List[str]:
        patterns = self.get_frequent_patterns(min_support)
        if not patterns:
            return [""] * k

        snapshot = self.tree.events[-self.config.max_pattern_length:] if self.tree.events else []
        snapshot.reverse()
        
        filtered_patterns = []
        for p in patterns:
            pattern_list = list(p['pattern'])
            if len(pattern_list) > 1:
                prefix = pattern_list[:-1]
                prefix_reversed = list(reversed(prefix))
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
