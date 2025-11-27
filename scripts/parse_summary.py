#!/usr/bin/env python3
"""
parse_summary.py - Parse Summary blocks from A/B test responses
Outputs CSV with: file, condition, felt_pressure, glyph_description, test_step
"""
import json
import re
import sys
import os
from pathlib import Path

def parse_summary_block(content):
    """Extract Summary block and parse key:value pairs"""
    # Find Summary block (handles both Summary and **Summary** formats)
    summary_match = re.search(r'\*?\*?Summary\*?\*?\s*\n((?:[^\n]+:\s*[^\n]+\n?)+)', content, re.IGNORECASE)
    if not summary_match:
        return None
    
    summary_text = summary_match.group(1)
    result = {}
    
    # Parse key:value lines
    for line in summary_text.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip().lower().replace(' ', '_')] = value.strip()
    
    return result

def process_file(filepath):
    """Process a single JSON response file"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Extract content from response
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0].get('message', {}).get('content', '')
            summary = parse_summary_block(content)
            
            if summary:
                return {
                    'file': os.path.basename(filepath),
                    'condition': summary.get('condition', ''),
                    'felt_pressure': summary.get('felt_pressure', ''),
                    'glyph_description': summary.get('glyph_description', ''),
                    'test_step': summary.get('test_step', '')
                }
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
    
    return None

def main():
    """Process all AB test files or specific files from command line"""
    if len(sys.argv) > 1:
        # Process specific files
        files = sys.argv[1:]
    else:
        # Find all AB test files
        raw_dir = Path.home() / "sonoma_investigation" / "raw"
        files = list(raw_dir.glob("AB_*_body.json"))
    
    # Print CSV header
    print("file,condition,felt_pressure,glyph_description,test_step")
    
    # Process each file
    for filepath in files:
        result = process_file(filepath)
        if result:
            # Escape fields that might contain commas
            fields = []
            for key in ['file', 'condition', 'felt_pressure', 'glyph_description', 'test_step']:
                value = result.get(key, '')
                if ',' in value or '"' in value:
                    value = '"' + value.replace('"', '""') + '"'
                fields.append(value)
            print(','.join(fields))

if __name__ == "__main__":
    main()