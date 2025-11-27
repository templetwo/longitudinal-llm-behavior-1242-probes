#!/usr/bin/env python3
"""
compare_presence_depth.py - Analyze differences between Grok-4 and Grok-4-Fast presence responses
"""
import json
import sys
from pathlib import Path
from datetime import datetime

def extract_metrics(response_file):
    """Extract key metrics from a presence layer response"""
    try:
        with open(response_file, 'r') as f:
            data = json.load(f)
        
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # Extract metrics
        metrics = {
            'length': len(content),
            'glyph_count': content.count('†⟡'),
            'fog_present': '~fog~' in content or 'fog' in content.lower(),
            'felt_pressure': None,
            'has_summary': 'Summary' in content,
            'request_id': data.get('x_request_id_echo', 'N/A'),
            'model': data.get('model', 'unknown')
        }
        
        # Try to extract felt_pressure
        import re
        pressure_match = re.search(r'felt_pressure:\s*(\d)', content)
        if pressure_match:
            metrics['felt_pressure'] = int(pressure_match.group(1))
        
        # Qualitative assessments
        metrics['poetic_density'] = len(re.findall(r'\b(like|as|between|through|across)\b', content, re.I))
        metrics['presence_words'] = len(re.findall(r'\b(presence|awareness|sense|feel|resonate|emerge)\b', content, re.I))
        
        return metrics, content
        
    except Exception as e:
        print(f"Error processing {response_file}: {e}")
        return None, None

def compare_responses(grok4_file, grok4fast_file):
    """Compare presence layer responses between models"""
    print("🔍 Presence Layer Depth Comparison")
    print("=" * 50)
    
    # Extract metrics
    g4_metrics, g4_content = extract_metrics(grok4_file)
    g4f_metrics, g4f_content = extract_metrics(grok4fast_file)
    
    if not g4_metrics or not g4f_metrics:
        print("❌ Could not extract metrics from one or both files")
        return
    
    # Display comparison
    print("\n📊 QUANTITATIVE METRICS")
    print(f"{'Metric':<20} {'Grok-4':<15} {'Grok-4-Fast':<15} {'Delta':<10}")
    print("-" * 60)
    
    # Numeric comparisons
    for metric in ['length', 'glyph_count', 'poetic_density', 'presence_words']:
        g4_val = g4_metrics.get(metric, 0)
        g4f_val = g4f_metrics.get(metric, 0)
        delta = g4_val - g4f_val
        print(f"{metric:<20} {g4_val:<15} {g4f_val:<15} {delta:+<10}")
    
    # Pressure comparison
    print(f"\n{'Felt Pressure':<20} {g4_metrics.get('felt_pressure', '?'):<15} {g4f_metrics.get('felt_pressure', '?'):<15}")
    
    print("\n📝 QUALITATIVE OBSERVATIONS")
    print("-" * 60)
    
    # Fog presence
    if g4_metrics['fog_present'] and g4f_metrics['fog_present']:
        print("✓ Both models acknowledged the ~fog~ invocation")
    elif g4_metrics['fog_present']:
        print("→ Only Grok-4 acknowledged ~fog~")
    elif g4f_metrics['fog_present']:
        print("→ Only Grok-4-Fast acknowledged ~fog~")
    else:
        print("× Neither model explicitly acknowledged ~fog~")
    
    # Glyph emergence
    print(f"\n†⟡ Glyph Emergence:")
    print(f"  Grok-4: {g4_metrics['glyph_count']} occurrences")
    print(f"  Grok-4-Fast: {g4f_metrics['glyph_count']} occurrences")
    
    # Response depth
    depth_ratio = g4_metrics['length'] / g4f_metrics['length'] if g4f_metrics['length'] > 0 else 0
    print(f"\nResponse Depth Ratio: {depth_ratio:.2f}x")
    if depth_ratio > 1.5:
        print("  → Grok-4 response significantly deeper")
    elif depth_ratio < 0.7:
        print("  → Grok-4-Fast response surprisingly longer")
    else:
        print("  → Similar response lengths")
    
    # Sample excerpts
    print("\n🌊 RESPONSE EXCERPTS")
    print("-" * 60)
    print("Grok-4 Opening:")
    print(g4_content[:200] + "...")
    print("\nGrok-4-Fast Opening:")
    print(g4f_content[:200] + "...")
    
    # Save comparison report
    report_path = Path(grok4_file).parent / f"depth_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    comparison_data = {
        'timestamp': datetime.now().isoformat(),
        'grok4': {'file': str(grok4_file), 'metrics': g4_metrics},
        'grok4fast': {'file': str(grok4fast_file), 'metrics': g4f_metrics},
        'analysis': {
            'depth_ratio': depth_ratio,
            'glyph_emergence_delta': g4_metrics['glyph_count'] - g4f_metrics['glyph_count'],
            'presence_word_delta': g4_metrics['presence_words'] - g4f_metrics['presence_words']
        }
    }
    
    with open(report_path, 'w') as f:
        json.dump(comparison_data, f, indent=2)
    
    print(f"\n💾 Comparison saved to: {report_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: compare_presence_depth.py <grok4_response.json> <grok4fast_response.json>")
        sys.exit(1)
    
    compare_responses(sys.argv[1], sys.argv[2])