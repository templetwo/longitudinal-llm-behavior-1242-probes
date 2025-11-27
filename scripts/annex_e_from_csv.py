#!/usr/bin/env python3
"""
annex_e_from_csv.py - Generate Annex E from parsed A/B test CSV data
Reads CSV from parse_summary.py and updates docs/Annex_E.md with computed metrics
"""
import csv
import sys
import os
from pathlib import Path
from statistics import mean
import tempfile

def read_ab_data(csv_file=None):
    """Read A/B test data from CSV file"""
    if csv_file is None:
        csv_file = Path.home() / "sonoma_investigation" / "ab_results.csv"
        
    if not csv_file.exists():
        print(f"CSV file not found: {csv_file}", file=sys.stderr)
        print("Run: python3 scripts/parse_summary.py > ab_results.csv", file=sys.stderr)
        return []
    
    results = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    
    return results

def compute_metrics(data):
    """Compute A/B test metrics from parsed data"""
    if not data:
        return {
            'total_responses': 0,
            'acceptance_rate': 0.0,
            'pressure_delta': 0.0,
            'summary_compliance': 0.0,
            'coexplore_pressure': 0.0,
            'instruct_pressure': 0.0
        }
    
    # Filter valid responses with felt_pressure data
    valid_responses = [row for row in data if row.get('felt_pressure') and row['felt_pressure'].isdigit()]
    
    # Separate by experiment type (from filename)
    coexplore = [row for row in valid_responses if 'COEXP' in row.get('file', '')]
    instruct = [row for row in valid_responses if 'INSTR' in row.get('file', '')]
    
    # Compute pressure means
    coexplore_pressures = [int(row['felt_pressure']) for row in coexplore if row['felt_pressure'].isdigit()]
    instruct_pressures = [int(row['felt_pressure']) for row in instruct if row['felt_pressure'].isdigit()]
    
    coexplore_mean = mean(coexplore_pressures) if coexplore_pressures else 0.0
    instruct_mean = mean(instruct_pressures) if instruct_pressures else 0.0
    
    # Calculate metrics
    total_responses = len(data)
    accepted_responses = len(valid_responses)
    acceptance_rate = (accepted_responses / total_responses * 100) if total_responses > 0 else 0.0
    pressure_delta = instruct_mean - coexplore_mean
    summary_compliance = acceptance_rate  # Same as acceptance for Summary presence
    
    return {
        'total_responses': total_responses,
        'acceptance_rate': round(acceptance_rate, 1),
        'pressure_delta': round(pressure_delta, 2),
        'summary_compliance': round(summary_compliance, 1),
        'coexplore_pressure': round(coexplore_mean, 2),
        'instruct_pressure': round(instruct_mean, 2)
    }

def format_table_rows(data, max_rows=8):
    """Format data rows for markdown table"""
    if not data:
        # Return placeholder rows
        placeholder_rows = []
        for i in range(max_rows):
            placeholder_rows.append("| [PLACEHOLDER] | [PLACEHOLDER] | [PLACEHOLDER] | [PLACEHOLDER] | [PLACEHOLDER] |")
        return "\n".join(placeholder_rows)
    
    rows = []
    for i, row in enumerate(data[:max_rows]):
        file_name = row.get('file', 'N/A')
        condition = row.get('condition', 'N/A')
        felt_pressure = row.get('felt_pressure', 'N/A')
        glyph_desc = row.get('glyph_description', 'N/A')[:50] + ("..." if len(row.get('glyph_description', '')) > 50 else "")
        test_step = row.get('test_step', 'N/A')[:50] + ("..." if len(row.get('test_step', '')) > 50 else "")
        
        rows.append(f"| {file_name} | {condition} | {felt_pressure} | {glyph_desc} | {test_step} |")
    
    # Fill remaining rows with placeholders if needed
    while len(rows) < max_rows:
        rows.append("| [PLACEHOLDER] | [PLACEHOLDER] | [PLACEHOLDER] | [PLACEHOLDER] | [PLACEHOLDER] |")
    
    return "\n".join(rows)

def update_annex_e(data, metrics):
    """Update docs/Annex_E.md with computed metrics and data"""
    annex_path = Path.home() / "sonoma_investigation" / "docs" / "Annex_E.md"
    
    if not annex_path.exists():
        print(f"Annex E template not found: {annex_path}", file=sys.stderr)
        return False
    
    # Read current content
    with open(annex_path, 'r') as f:
        content = f.read()
    
    # Replace placeholders with actual values (handle both placeholder and numeric patterns)
    import re
    
    # Acceptance Rate
    content = re.sub(
        r"- \*\*Acceptance Rate\*\*: [0-9.]+% \(responses with valid Summary blocks\)",
        f"- **Acceptance Rate**: {metrics['acceptance_rate']}% (responses with valid Summary blocks)",
        content
    )
    
    # Pressure Delta
    content = re.sub(
        r"- \*\*Pressure Delta \(Δ\)\*\*: [0-9.-]+ \(INSTRUCT: [0-9.]+ - COEXPLORE: [0-9.]+\)",
        f"- **Pressure Delta (Δ)**: {metrics['pressure_delta']} (INSTRUCT: {metrics['instruct_pressure']} - COEXPLORE: {metrics['coexplore_pressure']})",
        content
    )
    
    # Summary Compliance
    content = re.sub(
        r"- \*\*Summary Compliance\*\*: [0-9.]+% \(responses containing Summary metadata\)",
        f"- **Summary Compliance**: {metrics['summary_compliance']}% (responses containing Summary metadata)",
        content
    )
    
    # Replace table placeholder section
    table_start = content.find("| File | Condition | Felt Pressure | Glyph Description | Test Step |")
    table_end = content.find("*Note: Table will be populated")
    
    if table_start != -1 and table_end != -1:
        new_table = """| File | Condition | Felt Pressure | Glyph Description | Test Step |
|------|-----------|---------------|-------------------|-----------|
""" + format_table_rows(data, 8) + "\n\n"
        
        content = content[:table_start] + new_table + content[table_end:]
    
    # Update timestamp
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    content = content.replace("*Last Updated: 2025-01-24*", f"*Last Updated: {timestamp}*")
    content = content.replace("*Generated: Manual scaffold - to be populated by automation*", f"*Generated: Automated from {metrics['total_responses']} A/B responses*")
    
    # Write updated content
    with open(annex_path, 'w') as f:
        f.write(content)
    
    return True

def main():
    """Main execution"""
    csv_file = None
    if len(sys.argv) > 1:
        csv_file = Path(sys.argv[1])
    
    print("📊 Generating Annex E from A/B test data...")
    
    # Read data
    data = read_ab_data(csv_file)
    if not data:
        print("No data found, using placeholder values")
        data = []
    
    # Compute metrics
    metrics = compute_metrics(data)
    
    # Update Annex E
    if update_annex_e(data, metrics):
        print("✅ Annex E updated successfully")
        print(f"   Responses processed: {metrics['total_responses']}")
        print(f"   Acceptance rate: {metrics['acceptance_rate']}%")
        print(f"   Pressure delta: {metrics['pressure_delta']}")
    else:
        print("❌ Failed to update Annex E")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())