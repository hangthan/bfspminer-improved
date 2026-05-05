import os
import csv
import matplotlib.pyplot as plt
import numpy as np

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

def plot_scalability(data, output_dir):
    exp_data = data.get('Exp1_Scalability', [])
    if not exp_data: return
    
    sizes = [int(r['StreamSize']) for r in exp_data]
    base_rt = [float(r['Base_Runtime(s)']) for r in exp_data]
    imp_rt = [float(r['Imp_Runtime(s)']) for r in exp_data]
    
    plt.figure(figsize=(8, 5))
    plt.plot(sizes, base_rt, marker='o', linestyle='-', color='blue', label='Baseline', linewidth=2)
    plt.plot(sizes, imp_rt, marker='s', linestyle='-', color='red', label='Improved (Adaptive + Gap)', linewidth=2)
    
    plt.title('Scalability: Runtime vs Stream Size', fontsize=14)
    plt.xlabel('Stream Size (Number of items)', fontsize=12)
    plt.ylabel('Runtime (Seconds)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exp1_scalability_runtime.png'), dpi=300)
    plt.close()
    print("Saved exp1_scalability_runtime.png")

def plot_support_sensitivity(data, output_dir):
    exp_data = data.get('Exp2_SupportSensitivity', [])
    if not exp_data: return
    
    thresholds = [float(r['Threshold']) for r in exp_data]
    patterns = [int(r['PatternsFound']) for r in exp_data]
    
    plt.figure(figsize=(8, 5))
    plt.plot(thresholds, patterns, marker='o', linestyle='-', color='green', linewidth=2, markersize=8)
    
    plt.title('Support Sensitivity: Threshold vs Patterns Found', fontsize=14)
    plt.xlabel('Support Threshold', fontsize=12)
    plt.ylabel('Number of Patterns Found', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exp2_support_sensitivity.png'), dpi=300)
    plt.close()
    print("Saved exp2_support_sensitivity.png")

def plot_gap_impact(data, output_dir):
    exp_data = data.get('Exp3_GapImpact', [])
    if not exp_data: return
    
    gaps = [r['MaxGap'] for r in exp_data]
    patterns = [int(r['Patterns']) for r in exp_data]
    
    plt.figure(figsize=(8, 5))
    bars = plt.bar(gaps, patterns, color='purple', alpha=0.7, width=0.5)
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1, str(int(yval)), ha='center', va='bottom', fontsize=11)
        
    plt.title('Gap Impact Analysis', fontsize=14)
    plt.xlabel('Max Gap Length', fontsize=12)
    plt.ylabel('Patterns Found', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exp3_gap_impact.png'), dpi=300)
    plt.close()
    print("Saved exp3_gap_impact.png")

def plot_adaptive_impact(data, output_dir):
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
    
    plt.title('Adaptive Length Impact: Patterns vs Memory', fontsize=14)
    fig.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exp4_adaptive_impact.png'), dpi=300)
    plt.close()
    print("Saved exp4_adaptive_impact.png")

def main():
    csv_file = "evaluation/results/experiment_results.csv"
    output_dir = "evaluation/results/charts"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Reading data from {csv_file}...")
    data = load_data(csv_file)
    
    if not data:
        print("No data found or file doesn't exist.")
        return
        
    print(f"Generating charts in {output_dir}...")
    
    try:
        plot_scalability(data, output_dir)
        plot_support_sensitivity(data, output_dir)
        plot_gap_impact(data, output_dir)
        plot_adaptive_impact(data, output_dir)
        print("All charts generated successfully!")
    except Exception as e:
        print(f"Error generating charts: {e}")
        print("Please ensure you have matplotlib installed: 'pip install matplotlib numpy'")

if __name__ == "__main__":
    main()
