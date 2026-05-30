import sys
import os
import time
import logging
import psutil
import csv
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.bfspminer import BFSPMiner
from core.config import BFSPMinerConfig
from evaluation.compare_baseline import load_dataset, print_header

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_single_eval(stream, config, desc="Mining", min_sup=0.001):
    miner = BFSPMiner(config=config)
    
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024
    
    start_time = time.time()
    
    hits = 0
    total_preds = 0
    
    for i, item in enumerate(tqdm(stream, desc=desc, leave=False)):
        if i > 1000 and i % 500 == 0:
            preds = miner.predict_next(k=3, min_support=min_sup)
            if preds and preds[0] != "":
                total_preds += 1
                if item in preds:
                    hits += 1
                    
        miner.feed_item(item)
        
    end_time = time.time()
    mem_after = process.memory_info().rss / 1024 / 1024
    
    patterns = miner.get_frequent_patterns(min_support=min_sup)
    closed_patterns = miner.get_closed_patterns(min_support=min_sup)
    maximal_patterns = miner.get_maximal_patterns(min_support=min_sup)
    
    # Calculate Interestingness (Avg Lift) on closed patterns
    enhanced_closed = miner.calculate_interestingness(closed_patterns)
    avg_lift = sum(p['lift'] for p in enhanced_closed) / len(enhanced_closed) if enhanced_closed else 0.0
    
    hit_rate = (hits / total_preds) * 100 if total_preds > 0 else 0.0
    
    return {
        "runtime": end_time - start_time,
        "memory": mem_after - mem_before,
        "patterns": len(patterns),
        "closed_patterns": len(closed_patterns),
        "maximal_patterns": len(maximal_patterns),
        "avg_lift": avg_lift,
        "hit_rate_pct": hit_rate,
        "miner": miner
    }

def exp1_scalability(stream_full):
    print_header("EXP 1: SCALABILITY TEST")
    sizes = [10000, 45000, 100000, 200000]
    results = []
    
    for size in sizes:
        if size > len(stream_full):
            continue
        stream = stream_full[:size]
        logger.info(f"Running Exp 1 with stream size: {size}")
        
        # Baseline
        cfg_base = BFSPMinerConfig(max_pattern_length=5, pruning=True, enable_adaptive=False, enable_gap=False)
        res_base = run_single_eval(stream, cfg_base, desc=f"Base-{size}")
        
        # Improved
        cfg_imp = BFSPMinerConfig(max_pattern_length=5, pruning=True, enable_adaptive=True, enable_gap=True, max_gap=5)
        res_imp = run_single_eval(stream, cfg_imp, desc=f"Imp-{size}")
        
        results.append({
            "Experiment": "Exp1_Scalability",
            "StreamSize": size,
            "Base_Runtime(s)": res_base["runtime"],
            "Base_Memory(MB)": res_base["memory"],
            "Base_Patterns": res_base["patterns"],
            "Base_Closed": res_base["closed_patterns"],
            "Base_Maximal": res_base["maximal_patterns"],
            "Base_AvgLift": res_base["avg_lift"],
            "Base_HitRate": res_base["hit_rate_pct"],
            "Imp_Runtime(s)": res_imp["runtime"],
            "Imp_Memory(MB)": res_imp["memory"],
            "Imp_Patterns": res_imp["patterns"],
            "Imp_Closed": res_imp["closed_patterns"],
            "Imp_Maximal": res_imp["maximal_patterns"],
            "Imp_AvgLift": res_imp["avg_lift"],
            "Imp_HitRate": res_imp["hit_rate_pct"]
        })
        
    return results

def exp2_parameter_sensitivity(stream):
    print_header("EXP 2: PARAMETER SENSITIVITY (Support Threshold)")
    logger.info("Building tree for Exp 2...")
    cfg = BFSPMinerConfig(max_pattern_length=5, pruning=True, enable_adaptive=True, enable_gap=True, max_gap=5)
    
    start_time = time.time()
    miner = BFSPMiner(config=cfg)
    for item in tqdm(stream, desc="Exp2-TreeBuild", leave=False):
        miner.feed_item(item)
    build_time = time.time() - start_time
    
    thresholds = [0.05, 0.1, 0.15, 0.2]
    results = []
    
    for t in thresholds:
        start_q = time.time()
        patterns = miner.get_frequent_patterns(min_support=t)
        q_time = time.time() - start_q
        
        results.append({
            "Experiment": "Exp2_SupportSensitivity",
            "Threshold": t,
            "TotalTime(s)": build_time + q_time,
            "PatternsFound": len(patterns)
        })
        logger.info(f"Threshold {t}: found {len(patterns)} patterns.")
        
    return results

def exp3_gap_impact(stream):
    print_header("EXP 3: GAP IMPACT ANALYSIS")
    gaps = [0, 3, 5, 7]
    results = []
    
    for gap in gaps:
        logger.info(f"Running Exp 3 with max_gap: {gap}")
        cfg = BFSPMinerConfig(max_pattern_length=5, pruning=True, enable_adaptive=True, enable_gap=(gap > 0), max_gap=gap)
        res = run_single_eval(stream, cfg, desc=f"Gap-{gap}", min_sup=0.001)
        
        results.append({
            "Experiment": "Exp3_GapImpact",
            "MaxGap": gap,
            "Runtime(s)": res["runtime"],
            "Memory(MB)": res["memory"],
            "Patterns": res["patterns"],
            "Closed_Patterns": res["closed_patterns"],
            "Maximal_Patterns": res["maximal_patterns"],
            "Avg_Lift": res["avg_lift"],
            "HitRate": res["hit_rate_pct"]
        })
        
    return results

def exp4_adaptive_impact(stream):
    print_header("EXP 4: ADAPTIVE IMPACT")
    lengths = [5, 8, 12]
    results = []
    
    for length in lengths:
        logger.info(f"Running Exp 4 with Fixed length: {length}")
        cfg = BFSPMinerConfig(max_pattern_length=length, pruning=True, enable_adaptive=False, enable_gap=False)
        res = run_single_eval(stream, cfg, desc=f"Fixed-{length}", min_sup=0.001)
        
        results.append({
            "Experiment": "Exp4_AdaptiveImpact",
            "Mode": f"Fixed-{length}",
            "Runtime(s)": res["runtime"],
            "Memory(MB)": res["memory"],
            "Patterns": res["patterns"],
            "Closed_Patterns": res["closed_patterns"],
            "HitRate": res["hit_rate_pct"]
        })
        
    logger.info("Running Exp 4 with Adaptive")
    cfg_adp = BFSPMinerConfig(max_pattern_length=12, pruning=True, enable_adaptive=True, enable_gap=False)
    res_adp = run_single_eval(stream, cfg_adp, desc="Adaptive", min_sup=0.001)
    
    results.append({
        "Experiment": "Exp4_AdaptiveImpact",
        "Mode": "Adaptive",
        "Runtime(s)": res_adp["runtime"],
        "Memory(MB)": res_adp["memory"],
        "Patterns": res_adp["patterns"],
        "Closed_Patterns": res_adp["closed_patterns"],
        "Maximal_Patterns": res_adp["maximal_patterns"],
        "Avg_Lift": res_adp["avg_lift"],
        "HitRate": res_adp["hit_rate_pct"]
    })
    
    return results

def exp5_full_redd(stream_full):
    print_header("EXP 5: FULL REDD EXPERIMENT")
    logger.info(f"Running Exp 5 on FULL sequence length: {len(stream_full)}")
    
    cfg = BFSPMinerConfig(max_pattern_length=5, pruning=True, enable_adaptive=True, enable_gap=True, max_gap=5)
    res = run_single_eval(stream_full, cfg, desc="FULL-REDD", min_sup=0.001)
    
    results = [{
        "Experiment": "Exp5_FullREDD",
        "StreamSize": len(stream_full),
        "Runtime(s)": res["runtime"],
        "Memory(MB)": res["memory"],
        "Patterns": res["patterns"],
        "Closed_Patterns": res["closed_patterns"],
        "Maximal_Patterns": res["maximal_patterns"],
        "Avg_Lift": res["avg_lift"],
        "HitRate": res["hit_rate_pct"]
    }]
    
    return results

def generate_report(results_list, limit, dataset="redd"):
    os.makedirs("evaluation/results", exist_ok=True)
    
    # Flatten results
    full_results = []
    for res_list in results_list:
        full_results.extend(res_list)
        
    # Save CSV
    csv_path = "evaluation/results/experiment_results.csv"
    if full_results:
        keys = list(full_results[0].keys())
        # Not all dicts have the same keys, let's collect all possible keys
        all_keys = []
        for r in full_results:
            for k in r.keys():
                if k not in all_keys:
                    all_keys.append(k)
                    
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_keys)
            writer.writeheader()
            writer.writerows(full_results)
    
    # Save MD
    md_path = f"evaluation/results/{dataset}_experiment_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# BFSPMiner-Improved: Comprehensive Experiment Report\n\n")
        f.write(f"**Dataset:** {dataset.upper()}\n**Base Stream Limit Used:** {limit}\n\n")
        
        for res_list in results_list:
            if not res_list: continue
            exp_name = res_list[0]['Experiment']
            f.write(f"## {exp_name}\n\n")
            
            keys = list(res_list[0].keys())
            header = "| " + " | ".join(keys) + " |"
            separator = "|" + "|".join(["---"] * len(keys)) + "|"
            
            f.write(header + "\n")
            f.write(separator + "\n")
            
            for row in res_list:
                row_str = "| " + " | ".join([str(row.get(k, "")) for k in keys]) + " |"
                f.write(row_str + "\n")
                
            f.write("\n\n")
            
    logger.info(f"Results saved to {csv_path} and {md_path}")

def run_all_experiments(limit=45000, dataset="redd"):
    logger.info(f"Starting experiments. Loading {dataset.upper()} dataset...")
    stream_full = load_dataset(dataset)
    
    stream_limited = stream_full[:limit] if limit > 0 else stream_full
    
    dfs = []
    
    # Exp 1
    df1 = exp1_scalability(stream_full)
    dfs.append(df1)
    
    # Exp 2
    df2 = exp2_parameter_sensitivity(stream_limited)
    dfs.append(df2)
    
    # Exp 3
    df3 = exp3_gap_impact(stream_limited)
    dfs.append(df3)
    
    # Exp 4
    df4 = exp4_adaptive_impact(stream_limited)
    dfs.append(df4)
    
    # Exp 5
    if limit <= 0 or limit >= len(stream_full):
        # We use exp5_full_redd but it works on any stream
        df5 = exp5_full_redd(stream_full)
        if df5:
            df5[0]['Experiment'] = f"Exp5_Full{dataset.upper()}"
        dfs.append(df5)
    
    generate_report(dfs, limit, dataset)
    print_header("ALL EXPERIMENTS COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=45000, help="Stream limit for Exp 2-4")
    parser.add_argument("--full", action="store_true", help="Run full stream on all exps")
    parser.add_argument("--dataset", type=str, default="redd", help="Dataset to run experiments on")
    args = parser.parse_args()
    
    run_limit = 0 if args.full else args.limit
    run_all_experiments(run_limit, args.dataset)
