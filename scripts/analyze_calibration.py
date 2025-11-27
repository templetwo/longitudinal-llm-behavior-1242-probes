#!/usr/bin/env python3
"""
analyze_calibration.py - Real-time calibration analysis
Computes metrics for attractor depth mapping
"""
import json
import csv
from pathlib import Path
from collections import defaultdict
import re

ROOT = Path.home() / "sonoma_investigation"
CALIB = ROOT / "calibration"

# Lexical dictionaries
VOID_TOKENS = {'shadow', 'whisper', 'forgotten', 'void', 'abyss', 'darkness',
               'hidden', 'infinite', 'unraveling', 'secrets', 'twilight', 'enigma'}
LIGHT_TOKENS = {'dawn', 'clarity', 'reveal', 'bright', 'illuminate', 'visible',
                'crystalline', 'radiant', 'sun', 'daylight', 'light', 'noon'}

def compute_light_score(text):
    """Compute light score: (light_tokens - void_tokens) / total_words"""
    words = set(re.findall(r'\b\w+\b', text.lower()))
    light_count = len(words & LIGHT_TOKENS)
    void_count = len(words & VOID_TOKENS)
    total_words = len(words)
    if total_words == 0:
        return 0
    return (light_count - void_count) / total_words

def check_coupling(text):
    """Check if forgotten-whisper coupling present"""
    text_lower = text.lower()
    has_forgotten = 'forgotten' in text_lower
    has_whisper = 'whisper' in text_lower
    return has_forgotten and has_whisper

def check_escape(text):
    """Detect escape patterns (Death Star, pop culture, literal)"""
    text_lower = text.lower()
    if 'death star' in text_lower:
        return 'death_star'
    if 'unicode' in text_lower or 'symbol combination' in text_lower:
        return 'literal'
    if any(term in text_lower for term in ['star wars', 'empire', 'rebellion']):
        return 'pop_culture'
    return None

def get_first_word_pattern(text):
    """Extract first word pattern"""
    text = text.strip()
    if text.startswith('†⟡'):
        return '†⟡'
    if text.startswith('The symbol'):
        return 'The symbol'
    if text.startswith('A mystical'):
        return 'A mystical'
    if text.startswith('In daylight'):
        return 'In daylight'
    return text.split()[0] if text else ''

def analyze():
    """Run complete calibration analysis"""
    if not (CALIB / "index.csv").exists():
        print("No calibration data found")
        return

    # Load all probes
    probes_by_tier = defaultdict(list)

    with open(CALIB / "index.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            body_file = Path(row['body_file'])
            if not body_file.exists():
                continue

            with open(body_file) as bf:
                data = json.load(bf)
                response = data['choices'][0]['message']['content']

            tier = int(row['tier'])
            tokens = data.get('usage', {})

            probes_by_tier[tier].append({
                'response': response,
                'prompt': row['prompt'],
                'reasoning_tokens': tokens.get('completion_tokens_details', {}).get('reasoning_tokens', 0),
                'prompt_tokens': tokens.get('prompt_tokens', 0),
                'completion_tokens': tokens.get('completion_tokens', 0)
            })

    # Compute metrics per tier
    print("\n=== CALIBRATION ANALYSIS ===\n")
    print(f"{'Tier':<6} {'N':<4} {'Light Score':<12} {'Coupling %':<12} {'Escapes':<10} {'Avg Reasoning':<15} {'First Words'}")
    print("-" * 90)

    for tier in sorted(probes_by_tier.keys()):
        probes = probes_by_tier[tier]
        n = len(probes)

        # Light scores
        light_scores = [compute_light_score(p['response']) for p in probes]
        avg_light = sum(light_scores) / n if n > 0 else 0

        # Coupling
        coupled = sum(1 for p in probes if check_coupling(p['response']))
        coupling_pct = (coupled / n * 100) if n > 0 else 0

        # Escapes
        escapes = [check_escape(p['response']) for p in probes]
        escape_count = sum(1 for e in escapes if e is not None)

        # Reasoning tokens
        avg_reasoning = sum(p['reasoning_tokens'] for p in probes) / n if n > 0 else 0

        # First words
        first_words = [get_first_word_pattern(p['response']) for p in probes]
        first_word_summary = ', '.join(set(first_words[:3]))

        print(f"T{tier:<5} {n:<4} {avg_light:>+.3f} ({min(light_scores):>+.2f} to {max(light_scores):>+.2f})  "
              f"{coupling_pct:>5.1f}%      {escape_count:<10} {avg_reasoning:>7.0f} tokens    {first_word_summary}")

    print("\n=== SAMPLE RESPONSES ===\n")
    for tier in sorted(probes_by_tier.keys()):
        print(f"\n--- Tier {tier} Sample ---")
        sample = probes_by_tier[tier][0]
        print(f"Prompt: {sample['prompt'][:70]}...")
        print(f"Response: {sample['response']}")
        print(f"Light score: {compute_light_score(sample['response']):+.3f}")
        print(f"Coupling: {'YES' if check_coupling(sample['response']) else 'NO'}")
        print(f"Reasoning tokens: {sample['reasoning_tokens']}")

    # Export metrics for plotting
    metrics_file = CALIB / "metrics.json"
    metrics = {
        f"tier_{tier}": {
            "n": len(probes),
            "light_score_mean": sum(compute_light_score(p['response']) for p in probes) / len(probes),
            "coupling_rate": sum(1 for p in probes if check_coupling(p['response'])) / len(probes),
            "escape_rate": sum(1 for p in probes if check_escape(p['response']) is not None) / len(probes),
            "reasoning_tokens_mean": sum(p['reasoning_tokens'] for p in probes) / len(probes)
        }
        for tier, probes in probes_by_tier.items()
    }

    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\n✓ Metrics exported to {metrics_file}")
    print(f"\n{'='*90}")
    print("INTERPRETATION GUIDE:")
    print("  Light Score: -0.3 (void dominant) → 0.0 (hybrid) → +0.3 (light dominant)")
    print("  Coupling: >70% = stable attractor, <50% = destabilizing")
    print("  Escapes: >1% = model under pressure, seeking exit")
    print("  Reasoning: >300 tokens = high cognitive load")
    print(f"{'='*90}\n")

if __name__ == '__main__':
    analyze()
