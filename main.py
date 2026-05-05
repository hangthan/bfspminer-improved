import sys
import logging
import argparse
import os

from core.bfspminer import BFSPMiner
from evaluation.preprocess_redd import preprocess_redd

logging.basicConfig(level=logging.INFO)

def run_toy_demo():
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

    print("\nPredicting next 2 events after current context:")
    preds = miner.predict_next(k=2)
    print(preds)

def main():
    parser = argparse.ArgumentParser(description="BFSPMiner Runner")
    parser.add_argument("--compare", action="store_true", help="Run comparison between Baseline and Improved")
    parser.add_argument("--preprocess", type=str, help="Run preprocess for specific dataset (e.g., redd)")
    parser.add_argument("--demo", type=str, help="Run specific demo (e.g., eyetracking)")
    parser.add_argument("--dataset", type=str, default="redd", help="Dataset to use for comparison")
    
    args = parser.parse_args()
    
    if args.preprocess:
        if args.preprocess.lower() == "redd":
            success = preprocess_redd("data/redd_house1_0.csv", "data/redd_sequence.txt")
            if not success:
                sys.exit(1)
        else:
            print(f"Preprocess for {args.preprocess} is not supported yet.")
    elif args.compare:
        import subprocess
        print(f"[*] Running comparison on {args.dataset} dataset...")
        cmd = [sys.executable, "evaluation/compare_baseline.py", "--dataset", args.dataset]
        subprocess.run(cmd)
    elif args.demo:
        if args.demo.lower() == "eyetracking":
            import subprocess
            cmd = [sys.executable, "evaluation/demo_eyetracking.py"]
            subprocess.run(cmd)
        else:
            print(f"Demo for {args.demo} is not configured.")
    else:
        # Default behavior
        run_toy_demo()

if __name__ == "__main__":
    main()
