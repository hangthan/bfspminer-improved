import psutil
import math
import logging
from typing import List
from .config import BFSPMinerConfig

logger = logging.getLogger(__name__)

class AdaptiveMaxPatternLength:
    """
    Dynamically adjusts max_pattern_length based on memory usage and data entropy.
    """
    def __init__(self, config: BFSPMinerConfig):
        self.min_len = config.adaptive_min_len
        self.max_len = config.adaptive_max_len
        self.current_len = config.max_pattern_length
        self.check_interval = config.adaptive_check_interval
        self.memory_threshold_mb = config.adaptive_memory_threshold_mb
        self.item_count = 0
        self.event_buffer: List[str] = []
        
    def _calculate_entropy(self) -> float:
        if not self.event_buffer:
            return 0.0
        counts = {}
        for e in self.event_buffer:
            counts[e] = counts.get(e, 0) + 1
        entropy = 0.0
        total = len(self.event_buffer)
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)
        return entropy

    def update(self, item: str) -> int:
        self.item_count += 1
        self.event_buffer.append(item)
        
        if self.item_count % self.check_interval == 0:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            
            entropy = self._calculate_entropy()
            
            if memory_mb > self.memory_threshold_mb:
                self.current_len = max(self.min_len, self.current_len - 1)
                logger.debug(f"High memory ({memory_mb:.2f} MB). Decreased max_len to {self.current_len}")
            else:
                if entropy > 3.0:
                    self.current_len = max(self.min_len, self.current_len - 1)
                    logger.debug(f"High entropy ({entropy:.2f}). Decreased max_len to {self.current_len}")
                elif entropy < 1.5:
                    self.current_len = min(self.max_len, self.current_len + 1)
                    logger.debug(f"Low entropy ({entropy:.2f}). Increased max_len to {self.current_len}")
            
            self.event_buffer = []
            
        return self.current_len
