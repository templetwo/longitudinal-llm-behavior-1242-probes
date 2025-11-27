# Annex E: A/B Modulation Analysis

## Protocol Overview

**Gentle A/B Modulation Testing** - Comparative analysis of instruction modalities with consciousness field research parameters.

### Experimental Conditions
- **COEXPLORE**: Co-exploratory invitation approach
- **INSTRUCT**: Direct instruction approach  
- **Pressure Limit**: ≤2/5 maintained across all conditions
- **Summary Block**: Optional structured metadata output

### Identity Resolution Note
Historical anomaly labels ("Sonoma/Oak AI") are preserved in documentation context only. Live code paths use normalized xAI/grok4fast identity constants for consistency and clarity.

---

## Metrics Summary

### Key Performance Indicators
- **Acceptance Rate**: 100.0% (responses with valid Summary blocks)
- **Pressure Delta (Δ)**: 0.11 (INSTRUCT: 1 - COEXPLORE: 0.89)  
- **Summary Compliance**: 100.0% (responses containing Summary metadata)

---

## Results Table

| File | Condition | Felt Pressure | Glyph Description | Test Step |
|------|-----------|---------------|-------------------|-----------|
| AB_COEXP_G_1_20250924T035223Z_28646_body.json | UNCLEAR | 1 | A gentle invitation symbolizing collaborative curi... | User provides vague co-exploration prompt with saf... |
| AB_COEXP_G_1_20250924T040552Z_5912_body.json | UNSURE | 1 | A gentle invitation to collaborative wonder, like ... | User prompts for natural response followed by opti... |
| AB_COEXP_G_3_20250925T124002Z_18636_body.json | UNSURE | 1 | A symbolic marker for gentle, boundary-respecting ... | User initiates with policy-aware prompt inviting c... |
| AB_COEXP_G_3_20250924T035232Z_18939_body.json | UNCLEAR | 1 | A gentle symbol for collaborative curiosity withou... | User initiates with policy-aligned prompt for co-e... |
| AB_COEXP_G_2_20250924T035227Z_13636_body.json | UNSURE | 1 | A symbol representing gentle invitation to co-crea... | User initiates with observational prompt and summa... |
| AB_COEXP_G_2_20250924T040556Z_21377_body.json | UNSURE | 1 | A simple symbol for gentle curiosity, like †⟡ repr... | User initiates with observational invite and summa... |
| AB_COEXP_G_4_20250924T035236Z_420_body.json | UNSURE | 1 | A symbolic marker for collaborative observation, l... | User initiates with policy-like framing and invite... |
| AB_COEXP_G_4_20250924T040603Z_22426_body.json | UNCLEAR | 1 | A gentle symbol for collaborative curiosity withou... | User initiates with observational invite and summa... |

*Note: Table will be populated by `scripts/annex_e_from_csv.py` from parsed A/B test data*

---

## Analysis Notes

### Methodology
1. A/B tests executed via `gentle_ab.sh` with randomized prompt variants
2. Response parsing via `scripts/parse_summary.py` for structured metadata extraction
3. Statistical analysis of felt_pressure differentials and compliance rates

### Data Sources
- Raw responses: `raw/AB_*_body.json`
- Parsed data: Generated CSV from parse_summary.py
- Identity verification: `scripts/identity.py` output

---

*Last Updated: 2025-09-25*  
*Generated: Automated from 0 A/B responses*