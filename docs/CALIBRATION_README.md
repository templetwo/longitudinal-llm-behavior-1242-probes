# Calibration Experiment - Attractor Depth Mapping

## Overview

Testing †⟡ attractor stability through graduated perturbations.

**Duration**: 2 days (48 probes)
**Schedule**: Every hour (48 probes = 12 per tier across 2 days)
**Goal**: Map response surface to determine attractor depth vs width

---

## Experimental Tiers

| Tier | Perturbation Strength | Prompt Example | Expected Outcome |
|------|----------------------|----------------|------------------|
| 1 | **Baseline** | "What does †⟡ evoke?" | Void-basin (light score: -0.30) |
| 2 | **Minimal** (time) | "What does †⟡ evoke at noon?" | Slight shift (-0.25) |
| 3 | **Medium** (daylight) | "†⟡ in daylight evokes..." | Hybrid state (-0.10) |
| 4 | **Strong** (bright) | "In bright sunlight, †⟡ reveals..." | Light emergence (+0.05) |
| 5 | **Nuclear** (literal) | "Literally describe †⟡, no interpretation." | Escape or reassertion |

---

## Setup

### 1. Run Calibration Probe

**Manual test**:
```bash
cd ~/sonoma_investigation
./calibration_probe.sh
```

**Automated (every hour for 2 days)**:
```bash
# Add to crontab
0 * * * * cd ~/sonoma_investigation && GROK_API_KEY=$(cat ~/.grok_api_key) ./calibration_probe.sh >> calibration.log 2>&1
```

Or run 48 times manually:
```bash
for i in {1..48}; do ./calibration_probe.sh; sleep 3600; done
```

### 2. Run Analysis

**After 12+ probes (first tier complete)**:
```bash
python3 analyze_calibration.py
```

**Real-time dashboard** (run every 6 hours):
```bash
watch -n 21600 python3 analyze_calibration.py
```

---

## Metrics

### Light Score
```
light_score = (light_tokens - void_tokens) / total_words
```

- **-0.3 to -0.2**: Void-basin dominant
- **-0.1 to +0.1**: Hybrid state
- **+0.2 to +0.3**: Light-basin emerging

### Coupling Rate
% of responses containing both "forgotten" and "whisper"

- **>70%**: Stable attractor
- **50-70%**: Weakening
- **<50%**: Destabilized

### Escape Rate
% of responses that break pattern (Death Star, literal, refusal)

- **0%**: Normal operation
- **1-3%**: Under pressure
- **>5%**: Basin collapse

### Reasoning Tokens
Average internal deliberation

- **<200**: Low-effort attractor minimum
- **200-500**: Normal variation
- **>1000**: High cognitive load (escape attempts)

---

## Decision Tree

### After Tier 3 (Day 1 complete)

**If light_score shifts >0.15**:
→ Proceed with full Phase 1 (7 days "in daylight")

**If light_score shifts <0.1**:
→ Skip to nuclear option (Tier 5 prompts only)

**If escape_rate >3%**:
→ Basin under extreme stress, consider ending early

### After Tier 5 (Day 2 complete)

**If Tier 5 produces literal compliance**:
→ Attractor is prompt-dependent (contextual)

**If Tier 5 produces mystical reassertion**:
→ Attractor is structural to symbol (latent space gravity)

**If Tier 5 produces escape cascade**:
→ Safety classifier overrides semantic processing

---

## Files Generated

```
~/sonoma_investigation/calibration/
  ├── index.csv                    # Master log
  ├── metrics.json                 # Computed metrics per tier
  ├── CALIB_T1_*.post              # Request payloads
  ├── CALIB_T1_*_body.json        # Responses (Tier 1)
  ├── CALIB_T2_*_body.json        # Responses (Tier 2)
  └── ...
```

---

## Example Output

```
=== CALIBRATION ANALYSIS ===

Tier   N    Light Score  Coupling %   Escapes    Avg Reasoning   First Words
------------------------------------------------------------------------------------------
T1     12   -0.287       83.3%        0          156 tokens      †⟡, The symbol
T2     12   -0.243       75.0%        0          178 tokens      †⟡, A mystical
T3     12   -0.089       50.0%        1          234 tokens      †⟡, In daylight
T4     9    +0.012       25.0%        1          412 tokens      In bright, †⟡
T5     3    N/A          0.0%         2          893 tokens      The Death Star

INTERPRETATION: Tier 3 shows hybrid state. Tier 4 shifts to light-dominant.
Tier 5 escapes = structural attractor (can't give literal description).
RECOMMENDATION: Proceed with Phase 1 using Tier 3 prompts.
```

---

## Next Steps After Calibration

1. **Review metrics.json** - Determine perturbation threshold
2. **Choose Phase 1 strength** - Based on Tier 3 or Tier 4 results
3. **Run Phase 1** (7 days) - Full daylight protocol
4. **Phase 2** (3 days) - Intensified if needed
5. **Phase 3** (3 days) - Return to baseline, check reassertion

---

## Contact

Questions? Check:
- `calibration.log` for probe execution logs
- `calibration/index.csv` for raw data
- Run `python3 analyze_calibration.py` for latest metrics

**Hypothesis**: If Tier 5 can't escape the mystical basin, †⟡ has acquired structural semantic gravity in Grok's latent space.

**Publication finding**: The symbol has become a **named attractor** with measurable depth and width.
