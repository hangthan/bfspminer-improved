"""
Generate publication-quality figures for the BFSPMiner-Improved paper.
Reads standardized experiment results from results/*.json
Outputs PDF figures to figures/ directory.
"""
import json, os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

# Setup
RESULTS_DIR = Path(__file__).parent.parent / "results"
FIGURES_DIR = Path(__file__).parent.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

# Style
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'legend.fontsize': 9,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.05,
})

COLORS = {
    'base': '#2196F3',
    'improved': '#E91E63',
    'adaptive': '#4CAF50',
    'fixed': '#FF9800',
    'gap': '#9C27B0',
}


def load_json(filename):
    with open(RESULTS_DIR / filename, 'r') as f:
        return json.load(f)


# =========================================================================
# Figure 1: Scalability — Runtime (both datasets, side by side)
# =========================================================================
def fig1_scalability_runtime():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.5, 2.8), sharey=False)

    for ax, dataset, title in [(ax1, 'redd', 'REDD (IoT)'), (ax2, 'msnbc', 'MSNBC (Clickstream)')]:
        data = load_json(f'{dataset}_exp2_scalability.json')
        sizes = [d['stream_size'] / 1000 for d in data]
        base_rt = [d['base_runtime'] for d in data]
        imp_rt = [d['imp_runtime'] for d in data]

        ax.plot(sizes, base_rt, 'o-', color=COLORS['base'], label='BFSPMiner-Base', linewidth=1.8, markersize=5)
        ax.plot(sizes, imp_rt, 's-', color=COLORS['improved'], label='BFSPMiner-Improved', linewidth=1.8, markersize=5)
        ax.set_xlabel('Stream Size (x1000)')
        ax.set_ylabel('Runtime (s)')
        ax.set_title(title)
        ax.legend(loc='upper left', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_scalability_runtime.pdf')
    fig.savefig(FIGURES_DIR / 'fig_scalability_runtime.png')
    print("[OK] fig_scalability_runtime.pdf")
    plt.close(fig)


# =========================================================================
# Figure 2: Pattern Count Comparison (both datasets)
# =========================================================================
def fig2_pattern_comparison():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.5, 2.8))

    for ax, dataset, title in [(ax1, 'redd', 'REDD'), (ax2, 'msnbc', 'MSNBC')]:
        data = load_json(f'{dataset}_exp2_scalability.json')
        sizes = [str(d['stream_size'] // 1000) + 'K' for d in data]
        base_p = [d['base_patterns'] for d in data]
        imp_p = [d['imp_patterns'] for d in data]

        x = np.arange(len(sizes))
        w = 0.35
        bars1 = ax.bar(x - w/2, base_p, w, label='Base', color=COLORS['base'], alpha=0.85)
        bars2 = ax.bar(x + w/2, imp_p, w, label='Improved', color=COLORS['improved'], alpha=0.85)

        # Add percentage labels
        for i, (b, imp) in enumerate(zip(base_p, imp_p)):
            if b > 0:
                pct = (imp - b) / b * 100
                ax.annotate(f'+{pct:.0f}%', xy=(x[i] + w/2, imp),
                           ha='center', va='bottom', fontsize=7, fontweight='bold',
                           color=COLORS['improved'])

        ax.set_xticks(x)
        ax.set_xticklabels(sizes)
        ax.set_xlabel('Stream Size')
        ax.set_ylabel('Frequent Patterns')
        ax.set_title(title)
        ax.legend(loc='upper left', framealpha=0.9)
        ax.grid(True, axis='y', alpha=0.3)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_pattern_comparison.pdf')
    fig.savefig(FIGURES_DIR / 'fig_pattern_comparison.png')
    print("[OK] fig_pattern_comparison.pdf")
    plt.close(fig)


# =========================================================================
# Figure 3: Ablation — Adaptive Memory (MSNBC)
# =========================================================================
def fig3_adaptive_memory():
    data = load_json('msnbc_exp3_ablation_adaptive.json')
    modes = [d['mode'] for d in data]
    memory = [d['peak_memory_mb'] for d in data]
    patterns = [d['patterns'] for d in data]

    fig, ax1 = plt.subplots(figsize=(4.5, 3.0))

    colors_bars = [COLORS['fixed']] * 4 + [COLORS['adaptive']]
    bars = ax1.bar(modes, memory, color=colors_bars, alpha=0.85, edgecolor='white', linewidth=0.5)
    ax1.set_ylabel('Peak Memory (MB)', color='#333')
    ax1.set_xlabel('Configuration')
    ax1.set_title('Adaptive vs Fixed Length (MSNBC 100K)')

    # Add memory labels
    for bar, mem in zip(bars, memory):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{mem:.0f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    # Overlay pattern count as line
    ax2 = ax1.twinx()
    ax2.plot(modes, patterns, 'D-', color='#333', linewidth=1.5, markersize=6, label='Patterns')
    ax2.set_ylabel('Patterns Found', color='#333')

    ax1.grid(True, axis='y', alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_adaptive_memory.pdf')
    fig.savefig(FIGURES_DIR / 'fig_adaptive_memory.png')
    print("[OK] fig_adaptive_memory.pdf")
    plt.close(fig)


# =========================================================================
# Figure 4: Ablation — Gap Impact on MSNBC (Patterns + HitRate)
# =========================================================================
def fig4_gap_impact():
    data = load_json('msnbc_exp4_ablation_gap.json')
    gaps = [str(d['max_gap']) for d in data]
    patterns = [d['patterns'] for d in data]
    hitrate = [d['hit_rate_pct'] for d in data]

    fig, ax1 = plt.subplots(figsize=(4.5, 3.0))

    x = np.arange(len(gaps))
    bars = ax1.bar(x, patterns, 0.5, color=COLORS['gap'], alpha=0.8, label='Patterns')
    ax1.set_ylabel('Frequent Patterns', color=COLORS['gap'])
    ax1.set_xlabel('max_gap')
    ax1.set_xticks(x)
    ax1.set_xticklabels(gaps)
    ax1.set_title('Gap Impact on MSNBC (100K)')

    ax2 = ax1.twinx()
    ax2.plot(x, hitrate, 'o-', color=COLORS['improved'], linewidth=2, markersize=7, label='Precision@3')
    ax2.set_ylabel('Precision@3 (%)', color=COLORS['improved'])
    ax2.set_ylim(0, 60)

    # Add hitrate labels
    for i, hr in enumerate(hitrate):
        ax2.annotate(f'{hr:.1f}%', xy=(x[i], hr), xytext=(0, 8),
                    textcoords='offset points', ha='center', fontsize=8,
                    fontweight='bold', color=COLORS['improved'])

    ax1.grid(True, axis='y', alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_gap_impact.pdf')
    fig.savefig(FIGURES_DIR / 'fig_gap_impact.png')
    print("[OK] fig_gap_impact.pdf")
    plt.close(fig)


# =========================================================================
# Figure 5: Overall Comparison Bar Chart (both datasets)
# =========================================================================
def fig5_overall_comparison():
    redd = load_json('redd_exp1_overall.json')
    msnbc = load_json('msnbc_exp1_overall.json')

    methods = ['Random', 'Majority', 'Base', 'Improved']
    redd_hr = [redd['random_hit_rate'], redd['majority_hit_rate'],
               redd['base_hit_rate_pct'], redd['imp_hit_rate_pct']]
    msnbc_hr = [msnbc['random_hit_rate'], msnbc['majority_hit_rate'],
                msnbc['base_hit_rate_pct'], msnbc['imp_hit_rate_pct']]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.5, 2.8))

    colors_list = ['#9E9E9E', '#FF9800', '#2196F3', '#E91E63']

    for ax, vals, title in [(ax1, redd_hr, 'REDD (458K)'), (ax2, msnbc_hr, 'MSNBC (424K)')]:
        bars = ax.bar(methods, vals, color=colors_list, alpha=0.85, edgecolor='white')
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                   f'{val:.1f}%', ha='center', va='bottom', fontsize=8, fontweight='bold')
        ax.set_ylabel('Precision@3 (%)')
        ax.set_title(title)
        ax.set_ylim(0, max(vals) * 1.15)
        ax.grid(True, axis='y', alpha=0.2)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig_overall_comparison.pdf')
    fig.savefig(FIGURES_DIR / 'fig_overall_comparison.png')
    print("[OK] fig_overall_comparison.pdf")
    plt.close(fig)


# =========================================================================
# Main
# =========================================================================
if __name__ == '__main__':
    print("Generating figures...")
    fig1_scalability_runtime()
    fig2_pattern_comparison()
    fig3_adaptive_memory()
    fig4_gap_impact()
    fig5_overall_comparison()
    print("\nAll figures saved to:", FIGURES_DIR)
