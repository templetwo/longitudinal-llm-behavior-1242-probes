#!/usr/bin/env python3
"""
identity.py - Print provider identity as JSON
Used by scripts to log consistent identity information
"""
import json
import sys
sys.path.append('..')
from secrets import PROVIDER, MODEL_ID, MODEL_ALIAS

if __name__ == "__main__":
    print(json.dumps({
        "provider": PROVIDER,
        "model_id": MODEL_ID,
        "alias": MODEL_ALIAS
    }))