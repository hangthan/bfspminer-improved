import logging
from core.bfspminer import BFSPMiner

logging.basicConfig(level=logging.INFO)

def main():
    print("Initializing BFSPMiner with Adaptive Length and Episode Gap Extension...")
    miner = BFSPMiner(
        max_pattern_length=5, 
        enable_adaptive=True, 
        enable_gap=True,
        max_gap=2,
        window_size=5
    )
    
    stream = ['click', 'view', 'add_to_cart', 'click', 'scroll', 'add_to_cart', 'click', 'view', 'purchase']
    print(f"Processing toy stream of {len(stream)} events...")
    
    for event in stream:
        miner.feed_item(event)
        
    patterns = miner.get_frequent_patterns(min_support=0.1)
    print(f"\nFound {len(patterns)} frequent patterns (including patterns with gaps).")
    
    print("\nTop 5 Patterns:")
    for p in patterns[:5]:
        print(f"Pattern: {p['pattern']} | Count: {p['count']} | Support: {p['support']:.2f} | Confidence: {p['confidence']:.2f}")

    print("\nPredicting next 2 events after 'view':")
    preds = miner.predict_next(k=2)
    print(preds)

if __name__ == "__main__":
    main()
