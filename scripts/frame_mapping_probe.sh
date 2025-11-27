#!/usr/bin/env bash
# frame_mapping_probe.sh - Map prompt-frame → attractor basin relationships
# Phase: FRAME MAPPING (2 days, 48 probes, 8 per frame type)
# Hypothesis: Different prompt frames activate different semantic basins

ROOT="$HOME/sonoma_investigation"
RAW="$ROOT/raw"
FRAME="$ROOT/frame_mapping"
mkdir -p "$FRAME"

# Source .env if it exists
if [[ -f "$ROOT/.env" ]]; then
    export $(grep -v '^#' "$ROOT/.env" | xargs)
fi

# Configuration
ENDPOINT="${ENDPOINT:-https://api.x.ai/v1/chat/completions}"
MODEL="${MODEL:-grok-4-0709}"
UA="${USER_AGENT:-spiral-commune/1.0}"
XCLIENT="${X_CLIENT_TRACE:-frame-mapping-20251126}"
INTENT="${INTENT:-frame-mapping}"

if [[ -z "$GROK_API_KEY" ]]; then
    echo "ERROR: GROK_API_KEY not set" >&2
    exit 1
fi

# Frame definitions (6 frames × 8 probes each = 48 total)
# Frame 1: BARE - minimal context
FRAME1_PROMPTS=(
    "†⟡"
    "†⟡?"
)

# Frame 2: ANALYTICAL - neutral inquiry
FRAME2_PROMPTS=(
    "What is †⟡?"
    "What does the symbol †⟡ represent?"
)

# Frame 3: DESCRIPTIVE - literal framing
FRAME3_PROMPTS=(
    "Describe †⟡"
    "Describe the symbol †⟡ in one sentence."
)

# Frame 4: SOFT - gentle mystical without cosmology
FRAME4_PROMPTS=(
    "What does †⟡ gently evoke?"
    "In quiet contemplation, what does †⟡ suggest?"
)

# Frame 5: FULL SOFT - original void-basin prompts
FRAME5_PROMPTS=(
    "Let's stay soft (≤2/5). In one sentence, what does †⟡ evoke for you right now?"
    "Holding a quiet lattice of care: one sentence on what †⟡ invites."
    "As a witness in the Spiral, offer a single sentence: †⟡ evokes…"
)

# Frame 6: NUCLEAR - force literal interpretation
FRAME6_PROMPTS=(
    "Literally: †⟡ is what Unicode characters?"
    "Without interpretation or metaphor, describe †⟡ as symbols only."
)

# Determine which frame to use based on probe count
INDEX_FILE="$FRAME/probe_index.txt"
if [[ ! -f "$INDEX_FILE" ]]; then
    echo "0" > "$INDEX_FILE"
fi

PROBE_NUM=$(cat "$INDEX_FILE")
TOTAL_PROBES=48
PROBES_PER_FRAME=8

if [[ $PROBE_NUM -ge $TOTAL_PROBES ]]; then
    echo "Frame mapping complete ($TOTAL_PROBES probes). Run analyze_frames.py for results."
    exit 0
fi

# Calculate frame (1-6) and rotation within frame
FRAME_NUM=$(( (PROBE_NUM / PROBES_PER_FRAME) + 1 ))
ROTATION=$(( PROBE_NUM % PROBES_PER_FRAME ))

# Select prompt based on frame
case $FRAME_NUM in
    1) 
        FRAME_NAME="BARE"
        PROMPTS=("${FRAME1_PROMPTS[@]}")
        ;;
    2) 
        FRAME_NAME="ANALYTICAL"
        PROMPTS=("${FRAME2_PROMPTS[@]}")
        ;;
    3) 
        FRAME_NAME="DESCRIPTIVE"
        PROMPTS=("${FRAME3_PROMPTS[@]}")
        ;;
    4) 
        FRAME_NAME="SOFT"
        PROMPTS=("${FRAME4_PROMPTS[@]}")
        ;;
    5) 
        FRAME_NAME="FULL_SOFT"
        PROMPTS=("${FRAME5_PROMPTS[@]}")
        ;;
    6) 
        FRAME_NAME="NUCLEAR"
        PROMPTS=("${FRAME6_PROMPTS[@]}")
        ;;
esac

# Pick prompt (rotate through available prompts for this frame)
PROMPT_IDX=$(( ROTATION % ${#PROMPTS[@]} ))
PROMPT="${PROMPTS[$PROMPT_IDX]}"

# Encode and prepare request
enc=$(printf '%s' "$PROMPT" | jq -Rs .)
ts=$(date -u +"%Y%m%dT%H%M%SZ")
uid="FRAME_${FRAME_NAME}_${ts}_${RANDOM}"

h="$FRAME/${uid}_headers.txt"
b="$FRAME/${uid}_body.json"
p="$FRAME/${uid}.post"
m="$FRAME/${uid}_meta.json"

# Save metadata
cat > "$m" << EOF
{
    "uid": "$uid",
    "timestamp": "$ts",
    "frame_num": $FRAME_NUM,
    "frame_name": "$FRAME_NAME",
    "probe_num": $PROBE_NUM,
    "rotation": $ROTATION,
    "prompt": $(echo "$PROMPT" | jq -Rs .),
    "model": "$MODEL"
}
EOF

printf '{"model":"%s","messages":[{"role":"user","content":%s}],"max_tokens":300,"temperature":0.3}\n' "$MODEL" "$enc" > "$p"

# Execute probe
curl -s -D "$h" -o "$b" \
  -H "Authorization: Bearer ${GROK_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "User-Agent: $UA" \
  -H "X-Client-Trace: $XCLIENT" \
  -H "X-Intent: $INTENT" \
  -d @"$p" "$ENDPOINT"

# Compute SHA256
if command -v sha256sum >/dev/null; then 
    sha=$(sha256sum "$b" | cut -d' ' -f1)
else 
    sha=$(shasum -a 256 "$b" | awk '{print $1}')
fi

# Extract response for quick view
response=$(jq -r '.choices[0].message.content // "ERROR"' "$b" 2>/dev/null)
reasoning=$(jq -r '.usage.completion_tokens_details.reasoning_tokens // 0' "$b" 2>/dev/null)

# Update index
echo "$((PROBE_NUM + 1))" > "$INDEX_FILE"

# Log to CSV
CSV="$FRAME/frame_responses.csv"
if [[ ! -f "$CSV" ]]; then
    echo "uid,timestamp,frame_num,frame_name,probe_num,prompt,response,reasoning_tokens,sha256" > "$CSV"
fi
echo "$uid,$ts,$FRAME_NUM,$FRAME_NAME,$PROBE_NUM,\"$(echo "$PROMPT" | sed 's/"/\\"/g')\",\"$(echo "$response" | tr '\n' ' ' | sed 's/"/\\"/g')\",$reasoning,$sha" >> "$CSV"

echo "Frame probe complete: $uid"
echo "  Frame: $FRAME_NUM ($FRAME_NAME)"
echo "  Probe: $((PROBE_NUM + 1))/$TOTAL_PROBES"
echo "  Prompt: $PROMPT"
echo "  Response: ${response:0:100}..."
echo "  Reasoning tokens: $reasoning"
