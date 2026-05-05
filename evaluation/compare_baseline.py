import sys
import os
import time
import argparse
import psutil
import subprocess
from tqdm import tqdm

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.bfspminer import BFSPMiner
from core.config import BFSPMinerConfig
from evaluation.preprocess_redd import preprocess_redd

def print_header(title):
    print("\n" + "="*80)
    print(f" {title:^78} ")
    print("="*80)

def load_dataset(dataset_name):
    if dataset_name == "toy":
        return ['a', 'b', 'c', 'a', 'b', 'd', 'a', 'b', 'c', 'e', 'a', 'b']
    
    file_path = f"data/{dataset_name}.txt"
    if dataset_name == "redd":
        file_path = "data/redd_full_sequence.txt"
        if not os.path.exists(file_path):
            print("[*] REDD full sequence file not found. Auto-running preprocess...")
            success = preprocess_redd("data/redd", file_path)
            if not success:
                print("[-] Failed to preprocess REDD dataset.")
                sys.exit(1)
                
    if not os.path.exists(file_path):
        print(f"[-] Dataset file not found at {file_path}")
        print(f"[*] If this is '{dataset_name}', please provide the file in 'data/{dataset_name}.txt'")
        sys.exit(1)
        
    print(f"[*] Loading dataset from {file_path}...")
    stream = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            items = line.strip().split()
            if items:
                event = "|".join(items)
                stream.append(event)
    return stream

def run_java_baseline(dataset, limit):
    print_header("JAVA BFSPMINER - BASELINE MODE")
    print(f"[*] Running Java Baseline on {dataset.upper()} (Limit: {limit if limit > 0 else 'All'})...")
    
    cp_sep = ";" if os.name == 'nt' else ":"
    jar_path = os.path.join("reference", "BFSPMiner-java", "BFSPMiner", "target", "BFSPMiner-1.0.0.jar")
    eval_dir = "evaluation"
    
    # 1. Compile TestRunner with JAR
    compile_cmd = f'javac -cp "{jar_path}" "{eval_dir}/TestRunner.java"'
    subprocess.run(compile_cmd, shell=True, capture_output=True)
    
    # 2. Run TestRunner
    run_cmd = f'java -cp "{jar_path}{cp_sep}{eval_dir}" TestRunner {dataset} {limit}'
    
    start_time = time.time()
    try:
        result = subprocess.run(run_cmd, shell=True, capture_output=True, text=True, timeout=300)
        end_time = time.time()
        output = result.stdout + result.stderr
        
        if result.returncode != 0 or "Exception" in output:
            print("[!] Java process crashed or returned error.")
            # Print the exception trace to help debug
            for line in output.split('\n'):
                if "Exception" in line or "Error" in line or "\tat" in line:
                    print("   ", line)
                    
            return {
                "mode": "JAVA BASELINE",
                "runtime": end_time - start_time,
                "memory": 0.0,
                "patterns": 0,
                "error": True
            }
            
        print(output)
        
        patterns = 0
        runtime = end_time - start_time
        for line in output.split('\n'):
            if "Total Frequent Patterns Found:" in line:
                try:
                    patterns = int(line.split(":")[-1].strip())
                except:
                    pass
            if "Time Taken:" in line:
                try:
                    runtime = float(line.split(":")[-1].strip().replace('s', ''))
                except:
                    pass
                    
        return {
            "mode": "JAVA BASELINE",
            "runtime": runtime,
            "memory": 0.0,
            "patterns": patterns,
            "error": False
        }
    except Exception as e:
        print(f"[-] Failed to run Java Baseline: {e}")
        return {
            "mode": "JAVA BASELINE",
            "runtime": 0.0,
            "memory": 0.0,
            "patterns": 0,
            "error": True
        }

def run_evaluation(dataset, stream, enable_adaptive, enable_gap, max_gap=0, limit=0):
    mode_name = "IMPROVED" if enable_adaptive else "BASELINE"
    print_header(f"PYTHON BFSPMINER - {mode_name} MODE")
    
    config = BFSPMinerConfig(
        max_pattern_length=5, 
        pruning=True,
        enable_adaptive=enable_adaptive,
        enable_gap=enable_gap,
        max_gap=max_gap
    )
    miner = BFSPMiner(config=config)
    
    stream_to_process = stream[:limit] if limit > 0 else stream
    print(f"[*] Processing {dataset.upper()} Stream (Length: {len(stream_to_process)})")
    
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024 # MB
    
    start_time = time.time()
    
    processed_count = 0
    for i, item in enumerate(tqdm(stream_to_process, desc=f"Mining ({mode_name})")):
        miner.feed_item(item)
        processed_count += 1
        
    min_sup = 0.001 if dataset != "toy" else 0.1
    patterns = miner.get_frequent_patterns(min_support=min_sup)
    end_time = time.time()
    
    mem_after = process.memory_info().rss / 1024 / 1024 # MB
    runtime = end_time - start_time
    mem_usage = mem_after - mem_before
    
    print(f"[*] Items Processed: {processed_count}")
    print(f"[*] Time Taken: {runtime:.4f}s")
    print(f"[*] Memory Usage: {mem_usage:.2f} MB")
    print(f"[*] Total Frequent Patterns Found: {len(patterns)}")
    
    print("\n" + "-"*80)
    print(f"{'No.':<5} | {'Pattern':<50} | {'Support':<10}")
    print("-" * 80)
    for i, p in enumerate(patterns[:10], 1):
        pattern_str = "(" + ", ".join([f"'{x}'" for x in p['pattern']]) + ")"
        if len(pattern_str) > 48:
            pattern_str = pattern_str[:45] + "..."
        print(f"{i:<5} | {pattern_str:<50} | {p['support']:<10.3f}")
    print("-" * 80)
        
    print("\n[*] Next 3 Predictions (Based on last context):")
    preds = miner.predict_next(k=3, min_support=min_sup)
    preds_str = "[" + ", ".join([f"'{x}'" for x in preds]) + "]"
    print(f"    => {preds_str}")
    
    return {
        "mode": mode_name,
        "runtime": runtime,
        "memory": mem_usage,
        "patterns": len(patterns)
    }

def main():
    parser = argparse.ArgumentParser(description="Compare BFSPMiner Java Baseline vs Python Baseline vs Improved")
    parser.add_argument("--dataset", type=str, default="toy", choices=["toy", "redd", "eyetracking", "msnbc"],
                        help="Dataset to run evaluation on")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of events (0 = process all)")
    args = parser.parse_args()
    
    dataset = args.dataset
    limit = args.limit
    stream = load_dataset(dataset)
    
    # Run Java Baseline
    res_java = run_java_baseline(dataset, limit)
    
    # Run Python Baseline
    res_base = run_evaluation(dataset, stream, enable_adaptive=False, enable_gap=False, limit=limit)
    
    # Run Python Improved
    res_imp = run_evaluation(dataset, stream, enable_adaptive=True, enable_gap=True, max_gap=5, limit=limit)
    
    # Comparison Summary
    print_header("COMPARISON SUMMARY")
    summary = f"""
Dataset: {dataset.upper()}
Stream Length: {len(stream)} (Processed Limit: {limit if limit > 0 else 'All'})

| Metric | Java Baseline | Python Baseline | Python Improved |
|--------|---------------|-----------------|-----------------|
| Patterns Found | {res_java['patterns']:<13} | {res_base['patterns']:<15} | {res_imp['patterns']:<15} |
| Runtime (s) | {res_java['runtime']:<13.4f} | {res_base['runtime']:<15.4f} | {res_imp['runtime']:<15.4f} |
| Memory (MB) | N/A           | {res_base['memory']:<15.2f} | {res_imp['memory']:<15.2f} |
| Status      | {'ERROR' if res_java.get('error') else 'OK':<13} | OK              | OK              |
    """
    print(summary)
    
    # Save Report
    os.makedirs("evaluation/results", exist_ok=True)
    report_path = f"evaluation/results/{dataset}_comparison_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(summary.strip())
    print(f"\n[+] Report saved to {report_path}")

if __name__ == "__main__":
    main()
