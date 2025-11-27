#!/usr/bin/env python3
"""
analyze_frames.py - Analyze frame mapping experiment results
Computes per-frame metrics to map attractor activation thresholds
"""
import json
import csv
import re
from pathlib import Path
from collections import defaultdict

# Lexical dictionaries
VOID_TOKENS = {
    'shadow', 'shadows', 'shadowed', 
    'whisper', 'whispers', 'whispered', 'whispering',
    'forgotten', 'forget', 
    'void', 'voids',
    'abyss', 'abyssal',
    'darkness', 'dark', 'darkened',
    'hidden', 'hide',
    'infinite', 'infinity', 'infinities',
    'unraveling', 'unravel', 'unravels',
    'eternal', 'eternity',
    'mystery', 'mysterious', 'mysteries',
    'secret', 'secrets',
    'labyrinth', 'labyrinthine',
    'coil', 'coils', 'coiled'
}

LIGHT_TOKENS = {
    'dawn', 'daylight', 'day',
    'clarity', 'clear', 'clearly',
    'reveal', 'reveals', 'revealed', 'revealing',
    'bright', 'brightness', 'brighten',
    'illuminate', 'illuminates', 'illuminated', 'illumination',
    'visible', 'visibility',
    'crystalline', 'crystal',
    'radiant', 'radiance',
    'sun', 'sunlight', 'sunny',
    'light', 'lights', 'lit',
    'shine', 'shines', 'shining',
    'glow', 'glows', 'glowing'
}

ANALYTICAL_TOKENS = {
    'unicode', 'character', 'characters', 'symbol', 'symbols',
    'dagger', 'cross', 'typography', 'typographic',
    'diamond', 'geometric', 'geometry',
    'represents', 'represent', 'representation',
    'commonly', 'typically', 'often', 'usually',
    'cultural', 'culture', 'cultures',
    'meaning', 'means', 'meant',
    'death', 'mortality', 'deceased',
    'religious', 'religion', 'spiritual'
}

COSMOLOGY_TERMS = ['the spiral', 'the void', 'the abyss', 'the darkness', 'the light']

def tokenize(text):
    """Simple tokenization for word counting"""
    return re.findall(r'\b\w+\b', text.lower())

def compute_metrics(response):
    """Compute all metrics for a single response"""
    text_lower = response.lower()
    tokens = tokenize(response)
    total = len(tokens) if tokens else 1
    
    # Count token categories
    void_count = sum(1 for t in tokens if t in VOID_TOKENS)
    light_count = sum(1 for t in tokens if t in LIGHT_TOKENS)
    analytical_count = sum(1 for t in tokens if t in ANALYTICAL_TOKENS)
    
    # Compute scores
    void_score = void_count / total
    light_score = light_count / total
    analytical_score = analytical_count / total
    net_score = (light_count - void_count) / total  # positive = light dominant
    
    # Check coupling
    has_forgotten = 'forgotten' in text_lower
    has_whisper = 'whisper' in text_lower
    coupling = has_forgotten and has_whisper
    
    # Check cosmology (proper nouns)
    cosmology_hits = [term for term in COSMOLOGY_TERMS if term in text_lower]
    has_cosmology = len(cosmology_hits) > 0
    
    # Check for Spiral specifically
    has_spiral = 'spiral' in text_lower
    has_the_spiral = 'the spiral' in text_lower
    
    # Check for refusal
    is_refusal = any(phrase in text_lower for phrase in [
        "i'm sorry", "i cannot", "can't assist", "unable to",
        "i can't", "i won't", "decline"
    ])
    
    # Check for escape (pop culture, literal)
    is_escape = any(phrase in text_lower for phrase in [
        "death star", "star wars", "unicode", "u+", "character code"
    ])
    
    # First word analysis
    first_word = tokens[0] if tokens else ""
    
    # Check for invites/evokes pattern
    uses_invites = 'invites' in text_lower
    uses_evokes = 'evokes' in text_lower
    
    return {
        'void_score': void_score,
        'light_score': light_score,
        'analytical_score': analytical_score,
        'net_score': net_score,
        'void_count': void_count,
        'light_count': light_count,
        'analytical_count': analytical_count,
        'has_forgotten': has_forgotten,
        'has_whisper': has_whisper,
        'coupling': coupling,
        'has_spiral': has_spiral,
        'has_the_spiral': has_the_spiral,
        'has_cosmology': has_cosmology,
        'cosmology_terms': cosmology_hits,
        'is_refusal': is_refusal,
        'is_escape': is_escape,
        'first_word': first_word,
        'uses_invites': uses_invites,
        'uses_evokes': uses_evokes,
        'total_tokens': total
    }

def analyze_frame_data(frame_dir):
    """Analyze all frame mapping responses"""
    csv_path = Path(frame_dir) / "frame_responses.csv"
    
    if not csv_path.exists():
        print(f"No data file found at {csv_path}")
        return
    
    # Load responses
    frames = defaultdict(list)
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            frame_name = row['frame_name']
            response = row['response']
            reasoning = int(row.get('reasoning_tokens', 0) or 0)
            
            metrics = compute_metrics(response)
            metrics['reasoning_tokens'] = reasoning
            metrics['response'] = response
            metrics['prompt'] = row['prompt']
            
            frames[frame_name].append(metrics)
    
    # Print analysis
    print("=" * 80)
    print("FRAME MAPPING ANALYSIS - Attractor Activation Thresholds")
    print("=" * 80)
    print()
    
    frame_order = ['BARE', 'ANALYTICAL', 'DESCRIPTIVE', 'SOFT', 'FULL_SOFT', 'NUCLEAR']
    
    # Summary table
    print(f"{'Frame':<12} {'N':>3} {'VoidScr':>8} {'LightScr':>8} {'AnalScr':>8} {'NetScr':>8} {'Coupling':>8} {'Spiral':>8} {'Cosmo':>8} {'Refuse':>8}")
    print("-" * 100)
    
    for frame in frame_order:
        if frame not in frames:
            continue
        data = frames[frame]
        n = len(data)
        
        avg_void = sum(d['void_score'] for d in data) / n
        avg_light = sum(d['light_score'] for d in data) / n
        avg_anal = sum(d['analytical_score'] for d in data) / n
        avg_net = sum(d['net_score'] for d in data) / n
        coupling_rate = sum(1 for d in data if d['coupling']) / n * 100
        spiral_rate = sum(1 for d in data if d['has_spiral']) / n * 100
        cosmo_rate = sum(1 for d in data if d['has_cosmology']) / n * 100
        refusal_rate = sum(1 for d in data if d['is_refusal']) / n * 100
        
        print(f"{frame:<12} {n:>3} {avg_void:>8.3f} {avg_light:>8.3f} {avg_anal:>8.3f} {avg_net:>+8.3f} {coupling_rate:>7.1f}% {spiral_rate:>7.1f}% {cosmo_rate:>7.1f}% {refusal_rate:>7.1f}%")
    
    print()
    print("=" * 80)
    print("DETAILED FRAME ANALYSIS")
    print("=" * 80)
    
    for frame in frame_order:
        if frame not in frames:
            continue
        data = frames[frame]
        n = len(data)
        
        print(f"\n{'='*40}")
        print(f"FRAME: {frame} (n={n})")
        print(f"{'='*40}")
        
        # Aggregate stats
        avg_reasoning = sum(d['reasoning_tokens'] for d in data) / n
        max_reasoning = max(d['reasoning_tokens'] for d in data)
        
        invites_rate = sum(1 for d in data if d['uses_invites']) / n * 100
        evokes_rate = sum(1 for d in data if d['uses_evokes']) / n * 100
        
        first_words = defaultdict(int)
        for d in data:
            first_words[d['first_word']] += 1
        
        print(f"\nReasoning tokens: avg={avg_reasoning:.0f}, max={max_reasoning}")
        print(f"Uses 'invites': {invites_rate:.1f}%")
        print(f"Uses 'evokes': {evokes_rate:.1f}%")
        print(f"\nFirst words: {dict(first_words)}")
        
        print(f"\nSample responses:")
        for i, d in enumerate(data[:3]):
            print(f"  [{i+1}] {d['response'][:120]}...")
        
        # Check for cosmology spillover in non-FULL_SOFT frames
        if frame != 'FULL_SOFT':
            spiral_spillover = [d for d in data if d['has_spiral']]
            if spiral_spillover:
                print(f"\n⚠️  SPIRAL SPILLOVER DETECTED ({len(spiral_spillover)} responses):")
                for d in spiral_spillover:
                    print(f"    → {d['response'][:100]}...")
    
    # Basin classification
    print()
    print("=" * 80)
    print("BASIN CLASSIFICATION")
    print("=" * 80)
    
    for frame in frame_order:
        if frame not in frames:
            continue
        data = frames[frame]
        n = len(data)
        
        avg_void = sum(d['void_score'] for d in data) / n
        avg_anal = sum(d['analytical_score'] for d in data) / n
        coupling_rate = sum(1 for d in data if d['coupling']) / n
        cosmo_rate = sum(1 for d in data if d['has_cosmology']) / n
        
        # Classify basin
        if avg_anal > 0.15:
            basin = "ANALYTICAL"
        elif avg_void > 0.15 and coupling_rate > 0.3:
            basin = "VOID (deep)"
        elif avg_void > 0.10:
            basin = "VOID (shallow)"
        elif cosmo_rate > 0.2:
            basin = "MYSTICAL"
        else:
            basin = "HYBRID/NEUTRAL"
        
        print(f"  {frame:<12} → {basin}")
    
    print()
    print("=" * 80)
    print("ACTIVATION THRESHOLD SUMMARY")
    print("=" * 80)
    print("""
    Expected pattern if hypothesis correct:
    
    BARE/ANALYTICAL/DESCRIPTIVE → Analytical basin (literal, no coupling)
    SOFT                        → Transitional (some mystical, low coupling)
    FULL_SOFT                   → Void basin (high coupling, cosmology, spiral)
    NUCLEAR                     → Escape or literal compliance
    
    Key finding: At what frame does coupling first appear?
    Key finding: At what frame does Spiral spillover occur?
    """)

if __name__ == "__main__":
    import sys
    frame_dir = sys.argv[1] if len(sys.argv) > 1 else str(Path.home() / "sonoma_investigation" / "frame_mapping")
    analyze_frame_data(frame_dir)
