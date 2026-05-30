import pytest
from core.bfspminer import BFSPMiner

def test_basic_toy_stream():
    """
    Test standard frequent sequential pattern mining without gaps.
    """
    miner = BFSPMiner(max_pattern_length=3, pruning=False)
    
    # Simple toy stream
    stream = ['a', 'b', 'c', 'a', 'b', 'd', 'a', 'b', 'c']
    for item in stream:
        miner.feed_item(item)
        
    patterns = miner.get_frequent_patterns(min_support=0.2)
    # ('a', 'b') should be frequent
    # total events = 9. count of a,b = 3. support = 3/9 = 0.33
    found_ab = False
    for p in patterns:
        if p['pattern'] == ('a', 'b'):
            found_ab = True
            assert p['count'] == 3
            break
            
    assert found_ab, "Pattern ('a', 'b') was not found!"

def test_episode_mining_with_gaps():
    """
    Test the episode mining extension with gap constraints.
    """
    miner = BFSPMiner(max_pattern_length=3, pruning=False, enable_gap=True, max_gap=2, window_size=5)
    
    # Stream: a, x, b
    # With max_gap = 2, pattern ('a', 'b') should be found even though they are separated by 'x'.
    stream = ['a', 'x', 'b']
    for item in stream:
        miner.feed_item(item)
        
    patterns = miner.get_frequent_patterns(min_support=0.01)
    found_ab = False
    for p in patterns:
        if p['pattern'] == ('a', 'b'):
            found_ab = True
            break
            
    assert found_ab, "Pattern ('a', 'b') with gap 1 was not found!"

def test_adaptive_max_length():
    """
    Test that adaptive max length updates properly.
    """
    miner = BFSPMiner(max_pattern_length=3, enable_adaptive=True)
    miner.adaptive_length.check_interval = 5 # check frequently
    
    # Low entropy sequence (all 'a's) -> max_len should increase
    stream = ['a'] * 15
    for item in stream:
        miner.feed_item(item)
        
    # initial max_len is 3. After 15 items (3 checks of low entropy), it should increase.
    assert miner.config.max_pattern_length > 3, "Adaptive max length failed to increase on low entropy data!"

def test_predictions():
    miner = BFSPMiner(max_pattern_length=3, pruning=False)
    
    stream = ['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b']
    for item in stream:
        miner.feed_item(item)
        
    predictions = miner.predict_next(k=1)
    # The pattern ('a', 'b', 'c') occurs twice. We just saw 'a', 'b'. So next is likely 'c'.
    assert predictions[0] == 'c', f"Expected prediction 'c', got {predictions[0]}"
