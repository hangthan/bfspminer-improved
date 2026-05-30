import os
import csv
import matplotlib.pyplot as plt
import numpy as np
import sys

def load_data(csv_file):
    data = {}
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
        return data
        
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            exp = row.get('Experiment', '')
            if not exp: continue
            if exp not in data:
                data[exp] = []
            data[exp].append(row)
    return data

def plot_scalability(data, output_dir, prefix):
    exp_data = data.get('Exp1_Scalability', [])
    if not exp_data: return
    
    sizes = [int(r['StreamSize']) for r in exp_data]
    base_rt = [float(r['Base_Runtime(s)']) for r in exp_data]
    imp_rt = [float(r['Imp_Runtime(s)']) for r in exp_data]
    
    plt.figure(figsize=(8, 5))
    plt.plot(sizes, base_rt, marker='o', linestyle='-', color='blue', label='Baseline', linewidth=2)
    plt.plot(sizes, imp_rt, marker='s', linestyle='-', color='red', label='Improved (Adaptive + Gap)', linewidth=2)
    
    plt.title(f'[{prefix.upper()}] Scalability: Runtime vs Stream Size', fontsize=14)
    plt.xlabel('Stream Size (Number of items)', fontsize=12)
    plt.ylabel('Runtime (Seconds)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{prefix}_exp1_scalability_runtime.png'), dpi=300)
    plt.close()
    print(f"Saved {prefix}_exp1_scalability_runtime.png")

def plot_support_sensitivity(data, output_dir, prefix):
    exp_data = data.get('Exp2_SupportSensitivity', [])
    if not exp_data: return
    
    thresholds = [float(r['Threshold']) for r in exp_data]
    patterns = [int(r['PatternsFound']) for r in exp_data]
    
    plt.figure(figsize=(8, 5))
    plt.plot(thresholds, patterns, marker='o', linestyle='-', color='green', linewidth=2, markersize=8)
    
    plt.title(f'[{prefix.upper()}] Support Sensitivity', fontsize=14)
    plt.xlabel('Support Threshold', fontsize=12)
    plt.ylabel('Number of Patterns Found', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{prefix}_exp2_support_sensitivity.png'), dpi=300)
    plt.close()
    print(f"Saved {prefix}_exp2_support_sensitivity.png")

def plot_gap_impact(data, output_dir, prefix):
    exp_data = data.get('Exp3_GapImpact', [])
    if not exp_data: return
    
    gaps = [r['MaxGap'] for r in exp_data]
    patterns = [int(float(r['Patterns'])) for r in exp_data]
    closed = [int(float(r.get('Closed_Patterns', r['Patterns']))) for r in exp_data]
    maximal = [int(float(r.get('Maximal_Patterns', 0))) for r in exp_data]
    
    x = np.arange(len(gaps))
    width = 0.25
    
    plt.figure(figsize=(10, 6))
    bars1 = plt.bar(x - width, patterns, width, label='Raw Patterns', color='skyblue')
    bars2 = plt.bar(x, closed, width, label='Closed Patterns', color='orange')
    bars3 = plt.bar(x + width, maximal, width, label='Maximal Patterns', color='green')
    
    plt.title(f'[{prefix.upper()}] Pattern Compression (Raw vs Closed vs Maximal)', fontsize=14)
    plt.xlabel('Max Gap Length', fontsize=12)
    plt.ylabel('Number of Patterns', fontsize=12)
    plt.xticks(x, gaps)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, str(int(yval)), ha='center', va='bottom', fontsize=9)
            
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{prefix}_exp3_gap_impact.png'), dpi=300)
    plt.close()
    print(f"Saved {prefix}_exp3_gap_impact.png")

def plot_lift(data, output_dir, prefix):
    exp_data = data.get('Exp3_GapImpact', [])
    if not exp_data: return
    
    gaps = [r['MaxGap'] for r in exp_data]
    lifts = [float(r.get('Avg_Lift', 0)) for r in exp_data]
    
    plt.figure(figsize=(8, 5))
    plt.plot(gaps, lifts, marker='D', linestyle='-', color='purple', linewidth=2, markersize=8)
    plt.title(f'[{prefix.upper()}] Average Lift Score by Gap Size', fontsize=14)
    plt.xlabel('Max Gap Length', fontsize=12)
    plt.ylabel('Average Lift', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{prefix}_exp3_lift_impact.png'), dpi=300)
    plt.close()
    print(f"Saved {prefix}_exp3_lift_impact.png")

def plot_adaptive_impact(data, output_dir, prefix):
    exp_data = data.get('Exp4_AdaptiveImpact', [])
    if not exp_data: return
    
    modes = [r['Mode'] for r in exp_data]
    patterns = [int(r['Patterns']) for r in exp_data]
    memory = [float(r['Memory(MB)']) for r in exp_data]
    
    x = np.arange(len(modes))
    width = 0.35
    
    fig, ax1 = plt.subplots(figsize=(9, 5))
    
    color1 = 'tab:blue'
    ax1.set_xlabel('Length Configuration', fontsize=12)
    ax1.set_ylabel('Patterns Found', color=color1, fontsize=12)
    bars1 = ax1.bar(x - width/2, patterns, width, color=color1, label='Patterns', alpha=0.8)
    ax1.tick_params(axis='y', labelcolor=color1)
    
    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel('Memory (MB)', color=color2, fontsize=12)
    bars2 = ax2.bar(x + width/2, memory, width, color=color2, label='Memory (MB)', alpha=0.8)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(modes)
    
    plt.title(f'[{prefix.upper()}] Adaptive Length Impact: Patterns vs Memory', fontsize=14)
    fig.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{prefix}_exp4_adaptive_impact.png'), dpi=300)
    plt.close()
    print(f"Saved {prefix}_exp4_adaptive_impact.png")

def main():
    dataset_prefix = "msnbc" if len(sys.argv) > 1 and sys.argv[1].lower() == "msnbc" else "redd"
    csv_file = "evaluation/results/experiment_results.csv"
    output_dir = "evaluation/results/charts"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Reading data from {csv_file}...")
    data = load_data(csv_file)
    
    if not data:
        print("No data found or file doesn't exist.")
        return
        
    print(f"Generating charts for {dataset_prefix.upper()} in {output_dir}...")
    
    try:
        plot_scalability(data, output_dir, dataset_prefix)
        plot_support_sensitivity(data, output_dir, dataset_prefix)
        plot_gap_impact(data, output_dir, dataset_prefix)
        plot_lift(data, output_dir, dataset_prefix)
        plot_adaptive_impact(data, output_dir, dataset_prefix)
        print("All charts generated successfully!")
    except Exception as e:
        print(f"Error generating charts: {e}")

if __name__ == "__main__":
    main()
