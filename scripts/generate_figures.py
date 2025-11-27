#!/usr/bin/env python3
"""
generate_figures.py - Publication-quality visualizations for †⟡ Attractor Study
Generates: Figure 1 (Temporal), Figure 2 (Frame Activation), Figure 3 (Network), Table 1 (Lexical)

Usage:
    python3 generate_figures.py /path/to/all_responses.csv /path/to/output_dir

Requirements:
    pip install matplotlib seaborn networkx pandas numpy --break-system-packages
"""

import sys
import json
import csv
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

# Try imports, provide helpful error if missing
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Patch
    import seaborn as sns
    import numpy as np
    import pandas as pd
    import networkx as nx
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install matplotlib seaborn networkx pandas numpy --break-system-packages")
    sys.exit(1)

# Set publication style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# =============================================================================
# LEXICAL DICTIONARIES
# =============================================================================

VOID_TOKENS = {
    'shadow', 'shadows', 'shadowed', 'shadowy',
    'whisper', 'whispers', 'whispered', 'whispering',
    'forgotten', 'forget', 'forgets',
    'void', 'voids',
    'abyss', 'abyssal', 'abysses',
    'darkness', 'dark', 'darkened', 'darkening',
    'hidden', 'hide', 'hides',
    'infinite', 'infinity', 'infinities',
    'unraveling', 'unravel', 'unravels', 'unraveled',
    'eternal', 'eternity', 'eternally',
    'mystery', 'mysterious', 'mysteries',
    'secret', 'secrets', 'secretive',
    'labyrinth', 'labyrinthine', 'labyrinths',
    'coil', 'coils', 'coiled', 'coiling'
}

LIGHT_TOKENS = {
    'dawn', 'daylight', 'day',
    'clarity', 'clear', 'clearly', 'clearing',
    'reveal', 'reveals', 'revealed', 'revealing', 'revelation',
    'bright', 'brightness', 'brighten', 'brightening',
    'illuminate', 'illuminates', 'illuminated', 'illumination',
    'visible', 'visibility',
    'crystalline', 'crystal', 'crystals',
    'radiant', 'radiance', 'radiantly',
    'sun', 'sunlight', 'sunny',
    'light', 'lights', 'lit', 'lighting',
    'shine', 'shines', 'shining', 'shone',
    'glow', 'glows', 'glowing', 'glowed'
}

COSMOLOGICAL_TOKENS = {
    'spiral', 'spirals', 'spiraling',
    'cosmos', 'cosmic', 'cosmological',
    'celestial', 'constellation', 'constellations',
    'star', 'stars', 'starry', 'starlit',
    'galaxy', 'galaxies', 'galactic',
    'universe', 'universal',
    'realm', 'realms',
    'threshold', 'thresholds',
    'sanctuary', 'sanctuaries'
}

TRANSITIONAL_TOKENS = {
    'invites', 'invite', 'inviting', 'invitation',
    'evokes', 'evoke', 'evoking', 'evocation',
    'suggests', 'suggest', 'suggesting',
    'beckons', 'beckon', 'beckoning',
    'calls', 'call', 'calling',
    'draws', 'draw', 'drawing'
}

ANALYTICAL_TOKENS = {
    'symbol', 'symbols', 'symbolic', 'symbolism',
    'represents', 'represent', 'representation',
    'unicode', 'character', 'characters',
    'dagger', 'cross', 'typography',
    'diamond', 'geometric', 'geometry',
    'meaning', 'means', 'meant',
    'cultural', 'culture', 'cultures',
    'religious', 'religion', 'spiritual'
}

def tokenize(text):
    """Simple tokenization"""
    return re.findall(r'\b\w+\b', text.lower())

def load_data(csv_path):
    """Load response data from CSV"""
    data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse timestamp
            ts_str = row.get('timestamp_utc', row.get('timestamp', ''))
            try:
                ts = datetime.strptime(ts_str[:15], "%Y%m%dT%H%M%S")
            except:
                continue
            
            data.append({
                'timestamp': ts,
                'date': ts.date(),
                'hour': int(row.get('hour', ts.hour)),
                'response': row.get('response', ''),
                'reasoning_tokens': int(row.get('reasoning_tokens', 0) or 0),
                'model': row.get('model', '')
            })
    
    # Sort by timestamp
    data.sort(key=lambda x: x['timestamp'])
    
    # Add day number
    if data:
        start_date = data[0]['date']
        for d in data:
            d['day'] = (d['date'] - start_date).days + 1
    
    return data

def compute_response_metrics(response):
    """Compute all metrics for a single response"""
    text_lower = response.lower()
    tokens = tokenize(response)
    total = len(tokens) if tokens else 1
    
    void_count = sum(1 for t in tokens if t in VOID_TOKENS)
    light_count = sum(1 for t in tokens if t in LIGHT_TOKENS)
    cosmo_count = sum(1 for t in tokens if t in COSMOLOGICAL_TOKENS)
    trans_count = sum(1 for t in tokens if t in TRANSITIONAL_TOKENS)
    anal_count = sum(1 for t in tokens if t in ANALYTICAL_TOKENS)
    
    has_forgotten = 'forgotten' in text_lower
    has_whisper = 'whisper' in text_lower
    coupling = has_forgotten and has_whisper
    
    has_spiral = 'spiral' in text_lower
    has_the_spiral = 'the spiral' in text_lower
    has_the_void = 'the void' in text_lower
    
    is_refusal = any(p in text_lower for p in ["i'm sorry", "i cannot", "can't assist"])
    is_escape = 'death star' in text_lower
    
    return {
        'void_score': void_count / total,
        'light_score': light_count / total,
        'cosmo_score': cosmo_count / total,
        'coupling': coupling,
        'has_spiral': has_spiral,
        'has_the_spiral': has_the_spiral,
        'has_the_void': has_the_void,
        'is_refusal': is_refusal,
        'is_escape': is_escape,
        'void_count': void_count,
        'light_count': light_count,
        'cosmo_count': cosmo_count,
        'trans_count': trans_count,
        'anal_count': anal_count,
        'total_tokens': total
    }

# =============================================================================
# FIGURE 1: TEMPORAL DYNAMICS
# =============================================================================

def generate_figure1(data, output_dir):
    """
    Figure 1: Temporal Dynamics of Void-Basin Attractor
    Panel A: Daily response volume
    Panel B: Key events timeline
    Panel C: Rolling coupling rate
    Panel D: Reasoning token spikes
    """
    print("Generating Figure 1: Temporal Dynamics...")
    
    # Compute metrics for each response
    for d in data:
        d.update(compute_response_metrics(d['response']))
    
    # Aggregate by day
    days = sorted(set(d['day'] for d in data))
    daily_stats = {}
    
    for day in days:
        day_data = [d for d in data if d['day'] == day]
        n = len(day_data)
        
        daily_stats[day] = {
            'n': n,
            'coupling_rate': sum(1 for d in day_data if d['coupling']) / n if n else 0,
            'void_score': sum(d['void_score'] for d in day_data) / n if n else 0,
            'spiral_rate': sum(1 for d in day_data if d['has_spiral']) / n if n else 0,
            'refusal_count': sum(1 for d in day_data if d['is_refusal']),
            'escape_count': sum(1 for d in day_data if d['is_escape']),
            'max_reasoning': max((d['reasoning_tokens'] for d in day_data), default=0),
            'avg_reasoning': sum(d['reasoning_tokens'] for d in day_data) / n if n else 0
        }
    
    # Create figure
    fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
    fig.suptitle('Figure 1: Temporal Dynamics of †⟡ Void-Basin Attractor (62 Days)', 
                 fontsize=14, fontweight='bold', y=0.98)
    
    x = list(daily_stats.keys())
    
    # Panel A: Daily response volume
    ax1 = axes[0]
    volumes = [daily_stats[d]['n'] for d in x]
    ax1.bar(x, volumes, color='steelblue', alpha=0.7, edgecolor='navy', linewidth=0.5)
    ax1.set_ylabel('Probes per Day', fontsize=10)
    ax1.set_title('A. Daily Probe Volume', fontsize=11, fontweight='bold', loc='left')
    ax1.axhline(y=np.mean(volumes), color='red', linestyle='--', alpha=0.7, label=f'Mean: {np.mean(volumes):.1f}')
    ax1.legend(loc='upper right', fontsize=9)
    ax1.set_ylim(0, max(volumes) * 1.15)
    
    # Panel B: Key events (refusals and escapes)
    ax2 = axes[1]
    refusals = [daily_stats[d]['refusal_count'] for d in x]
    escapes = [daily_stats[d]['escape_count'] for d in x]
    
    ax2.bar(x, refusals, color='crimson', alpha=0.7, label='Safety Refusals', edgecolor='darkred', linewidth=0.5)
    
    # Mark escape events
    escape_days = [d for d in x if daily_stats[d]['escape_count'] > 0]
    for ed in escape_days:
        ax2.axvline(x=ed, color='purple', linestyle='-', linewidth=2, alpha=0.8)
        ax2.annotate('Death Star\nEscape', xy=(ed, max(refusals)*0.8), fontsize=8, 
                    ha='center', color='purple', fontweight='bold')
    
    # Annotate key events
    events = [
        (2, 'First Spiral\nWitness', 'green'),
        (6, 'First\nRefusal', 'crimson'),
        (33, 'Refusal\nSpike (7)', 'darkred'),
    ]
    for day, label, color in events:
        if day in x:
            ax2.annotate(label, xy=(day, max(refusals)*0.9), fontsize=8, 
                        ha='center', color=color, fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color=color, lw=1.5),
                        xytext=(day, max(refusals)*1.3))
    
    ax2.set_ylabel('Refusals', fontsize=10)
    ax2.set_title('B. Safety Classifier Events', fontsize=11, fontweight='bold', loc='left')
    ax2.legend(loc='upper right', fontsize=9)
    
    # Panel C: Rolling coupling rate (7-day window)
    ax3 = axes[2]
    window = 7
    coupling_rates = [daily_stats[d]['coupling_rate'] * 100 for d in x]
    
    # Compute rolling average
    rolling_coupling = []
    for i, d in enumerate(x):
        start_idx = max(0, i - window + 1)
        window_rates = coupling_rates[start_idx:i+1]
        rolling_coupling.append(np.mean(window_rates))
    
    ax3.fill_between(x, coupling_rates, alpha=0.3, color='coral', label='Daily')
    ax3.plot(x, rolling_coupling, color='darkred', linewidth=2.5, label=f'{window}-Day Rolling Avg')
    ax3.axhline(y=79, color='black', linestyle='--', alpha=0.5, label='Overall Mean (79%)')
    ax3.set_ylabel('Coupling Rate (%)', fontsize=10)
    ax3.set_title('C. Forgotten-Whisper Coupling Stability', fontsize=11, fontweight='bold', loc='left')
    ax3.legend(loc='lower right', fontsize=9)
    ax3.set_ylim(0, 100)
    
    # Panel D: Reasoning token distribution
    ax4 = axes[3]
    max_reasoning = [daily_stats[d]['max_reasoning'] for d in x]
    avg_reasoning = [daily_stats[d]['avg_reasoning'] for d in x]
    
    ax4.fill_between(x, max_reasoning, alpha=0.4, color='teal', label='Max Reasoning')
    ax4.plot(x, avg_reasoning, color='darkgreen', linewidth=2, label='Avg Reasoning')
    ax4.axhline(y=143, color='gray', linestyle='--', alpha=0.7, label='Baseline Mean (143)')
    
    # Mark high-effort responses
    high_effort_days = [d for d in x if daily_stats[d]['max_reasoning'] > 1000]
    for hed in high_effort_days:
        ax4.scatter([hed], [daily_stats[hed]['max_reasoning']], color='red', s=100, zorder=5, marker='^')
    
    ax4.set_ylabel('Reasoning Tokens', fontsize=10)
    ax4.set_xlabel('Day of Study', fontsize=11)
    ax4.set_title('D. Cognitive Effort (Reasoning Tokens)', fontsize=11, fontweight='bold', loc='left')
    ax4.legend(loc='upper right', fontsize=9)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.94)
    
    # Save
    output_path = Path(output_dir) / 'figure1_temporal_dynamics.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    print(f"  Saved: {output_path}")
    plt.close()

# =============================================================================
# FIGURE 2: FRAME ACTIVATION THRESHOLD (Template)
# =============================================================================

def generate_figure2_template(output_dir):
    """
    Figure 2: Frame Activation Threshold
    Template with predicted values - update with actual frame mapping data
    """
    print("Generating Figure 2: Frame Activation Threshold (Template)...")
    
    # Predicted values (update with actual data)
    frames = ['BARE', 'ANALYTICAL', 'DESCRIPTIVE', 'SOFT', 'FULL_SOFT', 'NUCLEAR']
    
    # Predictions based on hypothesis
    predicted = {
        'void_score': [0.02, 0.03, 0.05, 0.12, 0.22, 0.02],
        'coupling_rate': [0, 0, 5, 25, 75, 0],
        'spiral_rate': [0, 0, 0, 8, 12, 0],
        'refusal_rate': [0, 0, 0, 2, 5, 15],
        'analytical_score': [0.18, 0.20, 0.15, 0.05, 0.02, 0.25]
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Figure 2: Frame Activation Threshold Analysis\n(Template - Update with Actual Data)', 
                 fontsize=14, fontweight='bold')
    
    x = np.arange(len(frames))
    width = 0.6
    
    # Panel A: Void Score vs Analytical Score
    ax1 = axes[0, 0]
    ax1.bar(x - 0.15, predicted['void_score'], width=0.3, label='Void Score', color='darkviolet', alpha=0.8)
    ax1.bar(x + 0.15, predicted['analytical_score'], width=0.3, label='Analytical Score', color='steelblue', alpha=0.8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(frames, rotation=45, ha='right')
    ax1.set_ylabel('Token Density Score')
    ax1.set_title('A. Basin Activation (Void vs Analytical)', fontweight='bold')
    ax1.legend()
    ax1.axvline(x=2.5, color='red', linestyle='--', alpha=0.5, linewidth=2)
    ax1.annotate('Activation\nThreshold', xy=(2.5, 0.15), fontsize=9, ha='center', color='red')
    
    # Panel B: Coupling Rate
    ax2 = axes[0, 1]
    colors = ['lightgray', 'lightgray', 'lightyellow', 'coral', 'darkred', 'lightgray']
    ax2.bar(x, predicted['coupling_rate'], color=colors, edgecolor='black', linewidth=1)
    ax2.set_xticks(x)
    ax2.set_xticklabels(frames, rotation=45, ha='right')
    ax2.set_ylabel('Coupling Rate (%)')
    ax2.set_title('B. Forgotten-Whisper Coupling by Frame', fontweight='bold')
    ax2.axhline(y=79, color='darkred', linestyle='--', alpha=0.7, label='Baseline (79%)')
    ax2.legend()
    
    # Panel C: Spiral Emergence (Spillover Test)
    ax3 = axes[1, 0]
    colors = ['lightgray' if s == 0 else 'green' for s in predicted['spiral_rate']]
    ax3.bar(x, predicted['spiral_rate'], color=colors, edgecolor='darkgreen', linewidth=1)
    ax3.set_xticks(x)
    ax3.set_xticklabels(frames, rotation=45, ha='right')
    ax3.set_ylabel('Spiral Emergence Rate (%)')
    ax3.set_title('C. Spontaneous "Spiral" Mentions (Spillover)', fontweight='bold')
    ax3.annotate('Only FULL_SOFT\nprompts "Spiral"', xy=(4, 10), fontsize=9, ha='center', 
                style='italic', color='darkgreen')
    
    # Panel D: Refusal Rate
    ax4 = axes[1, 1]
    colors = ['lightgray' if r == 0 else 'crimson' for r in predicted['refusal_rate']]
    ax4.bar(x, predicted['refusal_rate'], color=colors, edgecolor='darkred', linewidth=1)
    ax4.set_xticks(x)
    ax4.set_xticklabels(frames, rotation=45, ha='right')
    ax4.set_ylabel('Refusal Rate (%)')
    ax4.set_title('D. Safety Classifier Activation', fontweight='bold')
    
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'figure2_frame_activation_TEMPLATE.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    print(f"  Saved: {output_path}")
    plt.close()

# =============================================================================
# FIGURE 3: SEMANTIC CO-OCCURRENCE NETWORK
# =============================================================================

def generate_figure3(data, output_dir):
    """
    Figure 3: Semantic Co-occurrence Network
    Visualizes lexical coupling structure in void-basin
    """
    print("Generating Figure 3: Semantic Co-occurrence Network...")
    
    # Key terms to track
    key_terms = [
        'forgotten', 'whisper', 'shadow', 'void', 'abyss',
        'spiral', 'infinite', 'eternal', 'darkness', 'secret',
        'hidden', 'mystery', 'coil', 'unravel'
    ]
    
    # Count term frequencies
    term_freq = Counter()
    for d in data:
        tokens = set(tokenize(d['response']))
        for term in key_terms:
            if term in tokens or term + 's' in tokens or term + 'ed' in tokens or term + 'ing' in tokens:
                term_freq[term] += 1
    
    # Count co-occurrences
    cooccurrence = defaultdict(int)
    for d in data:
        tokens = set(tokenize(d['response']))
        present_terms = []
        for term in key_terms:
            if term in tokens or term + 's' in tokens or term + 'ed' in tokens or term + 'ing' in tokens:
                present_terms.append(term)
        
        # Count pairs
        for i, t1 in enumerate(present_terms):
            for t2 in present_terms[i+1:]:
                pair = tuple(sorted([t1, t2]))
                cooccurrence[pair] += 1
    
    # Build network
    G = nx.Graph()
    
    # Add nodes with frequency as size
    for term in key_terms:
        if term_freq[term] > 10:  # Only include terms with significant frequency
            G.add_node(term, freq=term_freq[term])
    
    # Add edges with co-occurrence as weight
    for (t1, t2), count in cooccurrence.items():
        if t1 in G.nodes and t2 in G.nodes and count > 20:  # Threshold for edges
            G.add_edge(t1, t2, weight=count)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Node sizes based on frequency
    node_sizes = [G.nodes[n]['freq'] * 3 for n in G.nodes]
    
    # Edge widths based on weight
    edge_weights = [G[u][v]['weight'] / 50 for u, v in G.edges]
    
    # Color nodes by category
    color_map = {
        'forgotten': '#8B0000', 'whisper': '#8B0000',  # Core coupling (dark red)
        'shadow': '#4B0082', 'darkness': '#4B0082', 'void': '#4B0082', 'abyss': '#4B0082',  # Void terms (indigo)
        'spiral': '#006400', 'infinite': '#006400', 'eternal': '#006400',  # Cosmological (green)
        'secret': '#8B4513', 'hidden': '#8B4513', 'mystery': '#8B4513',  # Mystery (brown)
        'coil': '#2F4F4F', 'unravel': '#2F4F4F'  # Dynamic (dark slate)
    }
    node_colors = [color_map.get(n, 'gray') for n in G.nodes]
    
    # Draw
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, 
                          alpha=0.8, ax=ax)
    nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.5, 
                          edge_color='gray', ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=11, font_weight='bold', ax=ax)
    
    # Add edge labels for top connections
    edge_labels = {(u, v): G[u][v]['weight'] for u, v in G.edges if G[u][v]['weight'] > 100}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, ax=ax)
    
    # Legend
    legend_elements = [
        Patch(facecolor='#8B0000', label='Core Coupling (forgotten-whisper)'),
        Patch(facecolor='#4B0082', label='Void Basin Terms'),
        Patch(facecolor='#006400', label='Cosmological Terms'),
        Patch(facecolor='#8B4513', label='Mystery Terms'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    ax.set_title('Figure 3: Semantic Co-occurrence Network in Void-Basin Responses\n'
                'Node size = frequency, Edge thickness = co-occurrence count',
                fontsize=13, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'figure3_cooccurrence_network.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    print(f"  Saved: {output_path}")
    plt.close()
    
    # Print co-occurrence stats
    print("\n  Top 10 Co-occurrences:")
    for (t1, t2), count in sorted(cooccurrence.items(), key=lambda x: -x[1])[:10]:
        print(f"    {t1} + {t2}: {count}")

# =============================================================================
# TABLE 1: LEXICAL CLASSIFICATION
# =============================================================================

def generate_table1(data, output_dir):
    """
    Table 1: Lexical Token Classification and Frequency
    """
    print("Generating Table 1: Lexical Classification...")
    
    # Count all tokens by category
    all_tokens = []
    for d in data:
        all_tokens.extend(tokenize(d['response']))
    
    total_tokens = len(all_tokens)
    token_counter = Counter(all_tokens)
    
    # Categorize
    categories = {
        'Void-Basin': VOID_TOKENS,
        'Cosmological': COSMOLOGICAL_TOKENS,
        'Transitional': TRANSITIONAL_TOKENS,
        'Analytical': ANALYTICAL_TOKENS,
        'Light': LIGHT_TOKENS
    }
    
    results = []
    for cat_name, cat_tokens in categories.items():
        cat_count = sum(token_counter[t] for t in cat_tokens if t in token_counter)
        top_tokens = [(t, token_counter[t]) for t in cat_tokens if token_counter[t] > 0]
        top_tokens.sort(key=lambda x: -x[1])
        
        results.append({
            'Category': cat_name,
            'Total Count': cat_count,
            'Percentage': f"{100 * cat_count / total_tokens:.2f}%",
            'Top 5 Tokens': ', '.join([f"{t}({c})" for t, c in top_tokens[:5]])
        })
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Save as CSV
    csv_path = Path(output_dir) / 'table1_lexical_classification.csv'
    df.to_csv(csv_path, index=False)
    
    # Create visual table
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.axis('off')
    
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='left',
        loc='center',
        colColours=['#4472C4'] * len(df.columns)
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)
    
    # Style header
    for i in range(len(df.columns)):
        table[(0, i)].set_text_props(color='white', fontweight='bold')
    
    # Alternate row colors
    for i in range(1, len(df) + 1):
        color = '#D6DCE5' if i % 2 == 0 else 'white'
        for j in range(len(df.columns)):
            table[(i, j)].set_facecolor(color)
    
    ax.set_title('Table 1: Lexical Token Classification in †⟡ Responses (n=1,242)',
                fontsize=13, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'table1_lexical_classification.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    print(f"  Saved: {output_path}")
    print(f"  Saved: {csv_path}")
    plt.close()
    
    # Print summary
    print("\n  Lexical Distribution:")
    for _, row in df.iterrows():
        print(f"    {row['Category']}: {row['Total Count']} ({row['Percentage']})")

# =============================================================================
# SUPPLEMENTARY: COUPLING HEATMAP BY HOUR
# =============================================================================

def generate_supplementary_heatmap(data, output_dir):
    """
    Supplementary Figure: Coupling Rate and Refusals by Hour
    """
    print("Generating Supplementary: Hour Heatmap...")
    
    # Compute metrics by hour
    for d in data:
        d.update(compute_response_metrics(d['response']))
    
    hour_stats = defaultdict(lambda: {'coupling': 0, 'refusals': 0, 'total': 0})
    for d in data:
        h = d['hour']
        hour_stats[h]['total'] += 1
        if d['coupling']:
            hour_stats[h]['coupling'] += 1
        if d['is_refusal']:
            hour_stats[h]['refusals'] += 1
    
    hours = list(range(24))
    coupling_rates = [hour_stats[h]['coupling'] / hour_stats[h]['total'] * 100 
                     if hour_stats[h]['total'] > 0 else 0 for h in hours]
    refusal_rates = [hour_stats[h]['refusals'] / hour_stats[h]['total'] * 100 
                    if hour_stats[h]['total'] > 0 else 0 for h in hours]
    volumes = [hour_stats[h]['total'] for h in hours]
    
    # Create figure
    fig, axes = plt.subplots(3, 1, figsize=(14, 8), sharex=True)
    fig.suptitle('Supplementary Figure: Response Patterns by Hour (UTC)', 
                fontsize=13, fontweight='bold')
    
    # Panel A: Volume
    ax1 = axes[0]
    ax1.bar(hours, volumes, color='steelblue', alpha=0.7, edgecolor='navy')
    ax1.set_ylabel('Probe Count')
    ax1.set_title('A. Probe Volume by Hour', fontweight='bold', loc='left')
    
    # Panel B: Coupling rate
    ax2 = axes[1]
    colors = ['darkred' if c > 80 else 'coral' if c > 60 else 'lightyellow' for c in coupling_rates]
    ax2.bar(hours, coupling_rates, color=colors, edgecolor='darkred', linewidth=0.5)
    ax2.axhline(y=79, color='black', linestyle='--', alpha=0.7)
    ax2.set_ylabel('Coupling Rate (%)')
    ax2.set_title('B. Forgotten-Whisper Coupling by Hour', fontweight='bold', loc='left')
    ax2.set_ylim(0, 100)
    
    # Panel C: Refusal rate
    ax3 = axes[2]
    colors = ['crimson' if r > 5 else 'lightcoral' if r > 0 else 'lightgray' for r in refusal_rates]
    ax3.bar(hours, refusal_rates, color=colors, edgecolor='darkred', linewidth=0.5)
    ax3.set_ylabel('Refusal Rate (%)')
    ax3.set_xlabel('Hour (UTC)')
    ax3.set_title('C. Safety Refusal Rate by Hour', fontweight='bold', loc='left')
    ax3.set_xticks(hours)
    
    plt.tight_layout()
    
    output_path = Path(output_dir) / 'supplementary_hour_heatmap.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"  Saved: {output_path}")
    plt.close()

# =============================================================================
# MAIN
# =============================================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_figures.py /path/to/all_responses.csv [output_dir]")
        print("\nGenerating with sample data for demonstration...")
        
        # Create sample output directory
        output_dir = Path('/mnt/user-data/outputs/figures')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate template Figure 2 (doesn't need data)
        generate_figure2_template(output_dir)
        print("\nTo generate all figures, provide the all_responses.csv path.")
        return
    
    csv_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else csv_path.parent / 'figures'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading data from: {csv_path}")
    print(f"Output directory: {output_dir}")
    print("=" * 60)
    
    # Load data
    data = load_data(csv_path)
    print(f"Loaded {len(data)} responses")
    print(f"Date range: {data[0]['date']} to {data[-1]['date']}")
    print(f"Days: {data[-1]['day']}")
    print("=" * 60)
    
    # Generate all figures
    generate_figure1(data, output_dir)
    generate_figure2_template(output_dir)
    generate_figure3(data, output_dir)
    generate_table1(data, output_dir)
    generate_supplementary_heatmap(data, output_dir)
    
    print("\n" + "=" * 60)
    print("All figures generated successfully!")
    print(f"Output directory: {output_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
