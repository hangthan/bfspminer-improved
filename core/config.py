from dataclasses import dataclass

@dataclass
class BFSPMinerConfig:
    max_pattern_length: int = 5
    pruning: bool = True
    delta: int = 1000
    batch_length: int = 1000
    alpha: float = 0.05
    eps: float = 0.1
    
    # Extensions
    enable_adaptive: bool = False
    enable_gap: bool = False
    max_gap: int = 1
    window_size: int = 5
    
    # Adaptive Params
    adaptive_min_len: int = 3
    adaptive_max_len: int = 15
    adaptive_check_interval: int = 5000
    adaptive_memory_threshold_mb: float = 500.0
