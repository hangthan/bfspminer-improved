"""
BFSPMiner-Improved: Standardized Experiment Suite
==================================================
Produces reproducible results for the paper's Section V.

Measurements:
  - Runtime: time.perf_counter() (wall-clock, high-resolution)
  - Memory: tracemalloc peak (Python heap only, no GC artifacts)
  - HitRate: Online Precision@3 (test every 500 items after 1000 warmup)

Baselines:
  - Naive-Random: Predicts 3 random items from the observed vocabulary
  - Naive-Majority: Always predicts the top-3 most frequent items so far
  - BFSPMiner-Base: Original algorithm (adaptive=False, gap=False)
  - BFSPMiner-Improved: Full system (adaptive=True, gap=True)
"""

import sys, os, json, csv, time, random, tracemalloc
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.bfspminer import BFSPMiner
from core.config import BFSPMinerConfig

# =============================================================================
# Configuration
# =============================================================================
RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

REDD_PATH = Path(__file__).parent.parent / "data" / "redd_full_sequence.txt"
MSNBC_PATH = Path(__file__).parent.parent / "data" / "msnbc_sequence.txt"

COMMON_CONFIG = dict(
    max_pattern_length=5,
    pruning=True,
    delta=1000,
    batch_length=1000,
    alpha=0.05,
    eps=0.1,
)

IMPROVED_EXTRA = dict(
    enable_adaptive=True,
    enable_gap=True,
    max_gap=2,
    window_size=5,
    adaptive_min_len=3,
    adaptive_max_len=15,
    adaptive_check_interval=5000,
    adaptive_memory_threshold_mb=500.0,
)

MIN_SUPPORT = 0.001
PREDICT_K = 3
WARMUP = 1000
TEST_INTERVAL = 500

# =============================================================================
# Data Loading
# =============================================================================
def load_stream(path, limit=0):
    """Load event stream from file. Each line = space-separated items joined by |."""
    events = []
    with open(path, 'r') as f:
        for line in f:
            tokens = line.strip().split()
            for t in tokens:
                events.append(t)
                if limit > 0 and len(events) >= limit:
                    return events
    return events


# =============================================================================
# Naive Baselines
# =============================================================================
def evaluate_naive_random(stream, k=3, seed=42):
    """Random baseline: predict k random items from observed vocabulary."""
    rng = random.Random(seed)
    vocab = set()
    hits, tests = 0, 0
    for idx, item in enumerate(stream):
        if idx >= WARMUP and (idx - WARMUP) % TEST_INTERVAL == 0 and idx + 1 < len(stream):
            actual_next = stream[idx + 1]
            vocab_list = list(vocab) if vocab else [item]
            preds = rng.sample(vocab_list, min(k, len(vocab_list)))
            if actual_next in preds:
                hits += 1
            tests += 1
        vocab.add(item)
    return hits / tests * 100 if tests > 0 else 0.0, tests


def evaluate_naive_majority(stream, k=3):
    """Majority baseline: predict top-k most frequent items so far."""
    counter = Counter()
    hits, tests = 0, 0
    for idx, item in enumerate(stream):
        if idx >= WARMUP and (idx - WARMUP) % TEST_INTERVAL == 0 and idx + 1 < len(stream):
            actual_next = stream[idx + 1]
            top_k = [x[0] for x in counter.most_common(k)]
            if actual_next in top_k:
                hits += 1
            tests += 1
        counter[item] += 1
    return hits / tests * 100 if tests > 0 else 0.0, tests


# =============================================================================
# BFSPMiner Evaluation
# =============================================================================
def evaluate_bfspminer(stream, config_dict, min_sup=MIN_SUPPORT, label=""):
    """Run BFSPMiner on stream with online prediction evaluation.
    
    Returns dict with: runtime, peak_memory_mb, patterns, closed, maximal,
                       avg_lift, hit_rate_pct, test_count
    """
    config = BFSPMinerConfig(**config_dict)
    miner = BFSPMiner(config)

    hits, tests = 0, 0

    # Start measurement
    tracemalloc.start()
    t_start = time.perf_counter()

    for idx, item in enumerate(stream):
        # Online prediction test
        if idx >= WARMUP and (idx - WARMUP) % TEST_INTERVAL == 0 and idx + 1 < len(stream):
            actual_next = stream[idx + 1]
            preds = miner.predict_next(k=PREDICT_K, min_support=min_sup)
            if actual_next in preds:
                hits += 1
            tests += 1

        miner.feed_item(item)

        # Progress for long streams
        if label and (idx + 1) % 50000 == 0:
            print(f"  [{label}] {idx+1}/{len(stream)} items processed...")

    t_end = time.perf_counter()
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    runtime = t_end - t_start
    peak_mb = peak_bytes / (1024 * 1024)

    # Extract patterns
    freq = miner.get_frequent_patterns(min_sup)
    closed = miner.get_closed_patterns(min_sup)
    maximal = miner.get_maximal_patterns(min_sup)

    # Interestingness
    interest = miner.calculate_interestingness(freq)
    lifts = [p.get('lift', 1.0) for p in interest if p.get('lift', 1.0) > 0]
    avg_lift = sum(lifts) / len(lifts) if lifts else 0.0

    hit_rate = hits / tests * 100 if tests > 0 else 0.0

    return {
        "runtime_s": round(runtime, 3),
        "peak_memory_mb": round(peak_mb, 2),
        "patterns": len(freq),
        "closed": len(closed),
        "maximal": len(maximal),
        "avg_lift": round(avg_lift, 2),
        "hit_rate_pct": round(hit_rate, 2),
        "test_count": tests,
    }


# =============================================================================
# Experiment 1: Overall Comparison (Base vs Improved vs Naive)
# =============================================================================
def exp1_overall_comparison(stream, dataset_name):
    """Main comparison table: Naive-Random, Naive-Majority, Base, Improved."""
    print(f"\n{'='*60}")
    print(f"Exp1: Overall Comparison — {dataset_name} ({len(stream)} events)")
    print(f"{'='*60}")

    results = {"dataset": dataset_name, "stream_size": len(stream)}

    # Naive baselines
    print("  Running Naive-Random...")
    hr_random, _ = evaluate_naive_random(stream)
    results["random_hit_rate"] = round(hr_random, 2)
    print(f"    -> HitRate = {hr_random:.2f}%")

    print("  Running Naive-Majority...")
    hr_majority, _ = evaluate_naive_majority(stream)
    results["majority_hit_rate"] = round(hr_majority, 2)
    print(f"    -> HitRate = {hr_majority:.2f}%")

    # BFSPMiner Base
    print("  Running BFSPMiner-Base...")
    base_cfg = {**COMMON_CONFIG, "enable_adaptive": False, "enable_gap": False}
    base = evaluate_bfspminer(stream, base_cfg, label=f"{dataset_name}-Base")
    for k, v in base.items():
        results[f"base_{k}"] = v
    print(f"    -> Patterns={base['patterns']}, HitRate={base['hit_rate_pct']:.2f}%, "
          f"Memory={base['peak_memory_mb']:.1f}MB, Time={base['runtime_s']:.2f}s")

    # BFSPMiner Improved
    print("  Running BFSPMiner-Improved...")
    imp_cfg = {**COMMON_CONFIG, **IMPROVED_EXTRA}
    imp = evaluate_bfspminer(stream, imp_cfg, label=f"{dataset_name}-Improved")
    for k, v in imp.items():
        results[f"imp_{k}"] = v
    print(f"    -> Patterns={imp['patterns']}, HitRate={imp['hit_rate_pct']:.2f}%, "
          f"Memory={imp['peak_memory_mb']:.1f}MB, Time={imp['runtime_s']:.2f}s")

    # Pattern increase
    if base['patterns'] > 0:
        pct = (imp['patterns'] - base['patterns']) / base['patterns'] * 100
        results["pattern_increase_pct"] = round(pct, 1)
    
    return results


# =============================================================================
# Experiment 2: Scalability
# =============================================================================
def exp2_scalability(full_stream, dataset_name, sizes=None):
    """Runtime and memory vs stream size."""
    if sizes is None:
        sizes = [10000, 50000, 100000, 200000]
    sizes = [s for s in sizes if s <= len(full_stream)]

    print(f"\n{'='*60}")
    print(f"Exp2: Scalability — {dataset_name}")
    print(f"{'='*60}")

    rows = []
    for sz in sizes:
        stream = full_stream[:sz]
        print(f"\n  Stream size: {sz}")

        base_cfg = {**COMMON_CONFIG, "enable_adaptive": False, "enable_gap": False}
        base = evaluate_bfspminer(stream, base_cfg)

        imp_cfg = {**COMMON_CONFIG, **IMPROVED_EXTRA}
        imp = evaluate_bfspminer(stream, imp_cfg)

        row = {
            "stream_size": sz,
            "base_runtime": base["runtime_s"],
            "base_memory": base["peak_memory_mb"],
            "base_patterns": base["patterns"],
            "base_hitrate": base["hit_rate_pct"],
            "imp_runtime": imp["runtime_s"],
            "imp_memory": imp["peak_memory_mb"],
            "imp_patterns": imp["patterns"],
            "imp_hitrate": imp["hit_rate_pct"],
        }
        rows.append(row)
        print(f"    Base: {base['runtime_s']:.2f}s, {base['patterns']} pats, {base['hit_rate_pct']:.1f}%")
        print(f"    Imp:  {imp['runtime_s']:.2f}s, {imp['patterns']} pats, {imp['hit_rate_pct']:.1f}%")

    return rows


# =============================================================================
# Experiment 3: Ablation — Adaptive impact
# =============================================================================
def exp3_ablation_adaptive(stream, dataset_name):
    """Compare fixed lengths vs adaptive."""
    print(f"\n{'='*60}")
    print(f"Exp3: Ablation (Adaptive) — {dataset_name} ({len(stream)} events)")
    print(f"{'='*60}")

    rows = []
    for fixed_len in [3, 5, 8, 12]:
        print(f"  Fixed-{fixed_len}...")
        cfg = {**COMMON_CONFIG, "max_pattern_length": fixed_len,
               "enable_adaptive": False, "enable_gap": False}
        r = evaluate_bfspminer(stream, cfg, label=f"Fixed-{fixed_len}")
        rows.append({"mode": f"Fixed-{fixed_len}", **r})
        print(f"    -> Patterns={r['patterns']}, Mem={r['peak_memory_mb']:.1f}MB, "
              f"HitRate={r['hit_rate_pct']:.2f}%, Time={r['runtime_s']:.2f}s")

    print(f"  Adaptive...")
    cfg = {**COMMON_CONFIG, **IMPROVED_EXTRA, "enable_gap": False}
    r = evaluate_bfspminer(stream, cfg, label="Adaptive")
    rows.append({"mode": "Adaptive", **r})
    print(f"    -> Patterns={r['patterns']}, Mem={r['peak_memory_mb']:.1f}MB, "
          f"HitRate={r['hit_rate_pct']:.2f}%, Time={r['runtime_s']:.2f}s")

    return rows


# =============================================================================
# Experiment 4: Ablation — Gap impact
# =============================================================================
def exp4_ablation_gap(stream, dataset_name):
    """Compare different max_gap values."""
    print(f"\n{'='*60}")
    print(f"Exp4: Ablation (Gap) - {dataset_name} ({len(stream)} events)")
    print(f"{'='*60}")

    rows = []
    for gap in [0, 1, 2, 3, 5]:
        label = f"Gap-{gap}"
        print(f"  {label}...")
        if gap == 0:
            cfg = {**COMMON_CONFIG, "enable_adaptive": False, "enable_gap": False}
        else:
            cfg = {**COMMON_CONFIG, "enable_adaptive": False, "enable_gap": True,
                   "max_gap": gap, "window_size": 5}
        r = evaluate_bfspminer(stream, cfg, label=label)
        rows.append({"max_gap": gap, **r})
        print(f"    -> Patterns={r['patterns']}, Maximal={r['maximal']}, "
              f"HitRate={r['hit_rate_pct']:.2f}%, Time={r['runtime_s']:.2f}s")

    return rows


# =============================================================================
# Main
# =============================================================================
def save_results(data, filename):
    """Save results as JSON."""
    path = RESULTS_DIR / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Saved: {path}")


def main():
    all_results = {}

    # --- REDD ---
    if REDD_PATH.exists():
        print("\n" + "="*70)
        print("LOADING REDD DATASET")
        print("="*70)
        redd_full = load_stream(REDD_PATH)
        print(f"  Total events: {len(redd_full)}")
        print(f"  Unique items: {len(set(redd_full))}")
        redd_100k = redd_full[:100000]

        r1 = exp1_overall_comparison(redd_full, "REDD")
        save_results(r1, "redd_exp1_overall.json")

        r2 = exp2_scalability(redd_full, "REDD")
        save_results(r2, "redd_exp2_scalability.json")

        r3 = exp3_ablation_adaptive(redd_100k, "REDD")
        save_results(r3, "redd_exp3_ablation_adaptive.json")

        r4 = exp4_ablation_gap(redd_100k, "REDD")
        save_results(r4, "redd_exp4_ablation_gap.json")

        all_results["redd"] = {"exp1": r1, "exp2": r2, "exp3": r3, "exp4": r4}

    # --- MSNBC ---
    if MSNBC_PATH.exists():
        print("\n" + "="*70)
        print("LOADING MSNBC DATASET")
        print("="*70)
        msnbc_full = load_stream(MSNBC_PATH)
        print(f"  Total events: {len(msnbc_full)}")
        print(f"  Unique items: {len(set(msnbc_full))}")
        msnbc_100k = msnbc_full[:100000]

        m1 = exp1_overall_comparison(msnbc_full, "MSNBC")
        save_results(m1, "msnbc_exp1_overall.json")

        m2 = exp2_scalability(msnbc_full, "MSNBC")
        save_results(m2, "msnbc_exp2_scalability.json")

        m3 = exp3_ablation_adaptive(msnbc_100k, "MSNBC")
        save_results(m3, "msnbc_exp3_ablation_adaptive.json")

        m4 = exp4_ablation_gap(msnbc_100k, "MSNBC")
        save_results(m4, "msnbc_exp4_ablation_gap.json")

        all_results["msnbc"] = {"exp1": m1, "exp2": m2, "exp3": m3, "exp4": m4}

    # Save combined results
    save_results(all_results, "all_experiments.json")
    print("\n" + "="*70)
    print("ALL EXPERIMENTS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
