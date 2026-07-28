#!/usr/bin/env bash
# =============================================================================
# compile-to-gguf.sh - Export BSL AI training data for LLM fine-tuning and GGUF
#
# This script exports the BSL training corpus and patterns into formats
# compatible with LLM fine-tuning pipelines, which can then be converted
# to GGUF format using llama.cpp or similar tools.
#
# GGUF (GPT-Generated Unified Format) is a file format for storing
# quantized LLM models. This script creates the training dataset needed
# to fine-tune a model to generate BSL scripts.
#
# The workflow is:
#   1. Run this script to export training data
#   2. Use the exported JSONL with a fine-tuning framework
#   3. Convert the fine-tuned model to GGUF using llama.cpp
#
# Usage:
#   ./compile-to-gguf.sh                          # Export all formats
#   ./compile-to-gguf.sh --train                   # Also train/save state first
#   ./compile-to-gguf.sh --output-dir ./gguf-data  # Custom output directory
#   ./compile-to-gguf.sh --help                    # Show this help
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/gguf-export"
TRAIN_FIRST=false

# ── Parse Arguments ──────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            sed -n '2,/^$/p' "${BASH_SOURCE[0]}" | head -n -1
            exit 0
            ;;
        --train)
            TRAIN_FIRST=true
            shift
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--train] [--output-dir <dir>]"
            exit 1
            ;;
    esac
done

mkdir -p "${OUTPUT_DIR}"

echo "═══════════════════════════════════════════════════════════════"
echo "  BSL AI → GGUF Export"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Output directory: ${OUTPUT_DIR}"
echo ""

# ── Step 1: Optionally train/save state first ────────────────────────────────

if [ "$TRAIN_FIRST" = true ]; then
    echo "┌─ Step 1: Training and saving state ──────────────────────────┐"
    echo "│                                                               │"
    python3 "${SCRIPT_DIR}/bsl_train.py" --save-state "${OUTPUT_DIR}/bsl-ai-state.json"
    echo "│                                                               │"
    echo "└───────────────────────────────────────────────────────────────┘"
    echo ""
    STATE_FILE="${OUTPUT_DIR}/bsl-ai-state.json"
else
    STATE_FILE=""
    echo "┌─ Step 1: Using default training data ────────────────────────┐"
    echo "│                                                               │"
    python3 "${SCRIPT_DIR}/bsl_train.py" 2>&1 | head -8
    echo "│                                                               │"
    echo "└───────────────────────────────────────────────────────────────┘"
    echo ""
fi

# ── Step 2: Export training dataset in JSONL format ──────────────────────────

echo "┌─ Step 2: Exporting training dataset (JSONL) ──────────────────┐"
echo "│                                                               │"

JSONL_FILE="${OUTPUT_DIR}/bsl-training-dataset.jsonl"
if [ -n "$STATE_FILE" ] && [ -f "$STATE_FILE" ]; then
    python3 "${SCRIPT_DIR}/bsl_train.py" --resume "${STATE_FILE}" \
        --export-dataset "${JSONL_FILE}" 2>&1
else
    python3 "${SCRIPT_DIR}/bsl_train.py" --export-dataset "${JSONL_FILE}" 2>&1
fi

JSONL_COUNT=$(wc -l < "${JSONL_FILE}" 2>/dev/null || echo 0)
echo "│  Examples exported: ${JSONL_COUNT}                                │"
echo "│                                                               │"
echo "└───────────────────────────────────────────────────────────────┘"
echo ""

# ── Step 3: Export structured corpus JSON ────────────────────────────────────

echo "┌─ Step 3: Exporting structured corpus (JSON) ──────────────────┐"
echo "│                                                               │"

CORPUS_FILE="${OUTPUT_DIR}/bsl-corpus.json"
if [ -n "$STATE_FILE" ] && [ -f "$STATE_FILE" ]; then
    python3 "${SCRIPT_DIR}/bsl_train.py" --resume "${STATE_FILE}" \
        --export "${CORPUS_FILE}" 2>&1
else
    python3 "${SCRIPT_DIR}/bsl_train.py" --export "${CORPUS_FILE}" 2>&1
fi

echo "│                                                               │"
echo "└───────────────────────────────────────────────────────────────┘"
echo ""

# ── Step 4: Create GGUF metadata and conversion config ───────────────────────

echo "┌─ Step 4: Creating GGUF metadata and conversion config ────────┐"
echo "│                                                               │"

# Create GGUF metadata file
cat > "${OUTPUT_DIR}/gguf-model-config.json" << 'GGUFEOF'
{
    "description": "BSL AI Script Generator - Fine-Tuning Configuration",
    "format": "gguf",
    "version": "1.0.0",

    "model": {
        "name": "BSL-AI-Script-Generator",
        "architecture": "llama",
        "context_length": 2048,
        "vocab_size": 32000,
        "hidden_size": 4096,
        "intermediate_size": 11008,
        "num_attention_heads": 32,
        "num_hidden_layers": 32
    },

    "training": {
        "dataset_format": "jsonl",
        "dataset_file": "bsl-training-dataset.jsonl",
        "prompt_template": {
            "instruction": "Create a BSL script that {instruction}",
            "response_prefix": "\n\nHere is a valid BSL script:\n",
            "response_suffix": "\n\nThis script follows BSL conventions."
        },
        "recommended_base_model": [
            "codellama-7b",
            "deepseek-coder-6.7b",
            "mistral-7b"
        ]
    },

    "gguf_conversion": {
        "tool": "llama.cpp",
        "repository": "https://github.com/ggerganov/llama.cpp",
        "steps": [
            "1. Clone llama.cpp: git clone https://github.com/ggerganov/llama.cpp",
            "2. Place base model in llama.cpp/models/",
            "3. Fine-tune using the JSONL dataset",
            "4. Run convert.py to create .gguf file",
            "5. Run quantize for 4-bit or 8-bit quantization"
        ],
        "convert_command": "python llama.cpp/convert.py --outfile bsl-ai.gguf --ctx 2048 model.pt",
        "quantize_command": "llama.cpp/quantize bsl-ai.gguf bsl-ai-q4_0.gguf q4_0"
    },

    "inference": {
        "prompt_prefix": "### Instruction:\nCreate a BSL script that ",
        "prompt_suffix": "\n\n### Response:\nHere is a valid BSL script:\n",
        "stop_tokens": ["\n###"]
    }
}
GGUFEOF

echo "│  Created: gguf-model-config.json                              │"
echo "│                                                               │"

# Create conversion helper script
cat > "${OUTPUT_DIR}/convert-to-gguf.py" << 'PYEOF'
#!/usr/bin/env python3
"""
convert-to-gguf.py - BSL AI → GGUF Conversion Helper

This script packages the BSL training data into a format compatible
with llama.cpp's GGUF conversion pipeline.

Usage:
    python convert-to-gguf.py                   # Show instructions
    python convert-to-gguf.py --prepare         # Prepare dataset for training
    python convert-to-gguf.py --stats           # Show dataset statistics

For actual GGUF conversion, follow the instructions in gguf-model-config.json
using llama.cpp (https://github.com/ggerganov/llama.cpp).
"""

import json
import os
import sys
from collections import Counter


# Find dataset relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(SCRIPT_DIR, "bsl-training-dataset.jsonl")


def show_instructions():
    print("=" * 60)
    print("  BSL AI → GGUF Conversion Guide")
    print("=" * 60)
    print()
    print("  This dataset can be used to fine-tune an LLM to generate")
    print("  BSL scripts. The workflow is:")
    print()
    print("  1. Choose a base model (recommended: CodeLlama, DeepSeek Coder)")
    print("  2. Clone llama.cpp:")
    print("     git clone https://github.com/ggerganov/llama.cpp")
    print()
    print("  3. Fine-tune using the dataset:")
    print("     python -m llama.cpp.finetune \\")
    print("       --model base-model.pt \\")
    print(f"       --dataset {DATASET_FILE} \\")
    print("       --output-dir ./finetuned")
    print()
    print("  4. Convert to GGUF:")
    print("     python llama.cpp/convert.py \\")
    print("       --outfile bsl-ai.gguf \\")
    print("       --ctx 2048 \\")
    print("       ./finetuned/model.pt")
    print()
    print("  5. Quantize (optional, reduces size):")
    print("     llama.cpp/quantize bsl-ai.gguf \\")
    print("       bsl-ai-q4_0.gguf q4_0")
    print()
    print("  6. Run inference:")
    print("     ./llama.cpp/main -m bsl-ai-q4_0.gguf \\")
    print('       -p "Create a BSL script that monitors disk space"')
    print()


def show_stats():
    if not os.path.exists(DATASET_FILE):
        print(f"Dataset file not found: {DATASET_FILE}")
        print("Run 'compile-to-gguf.sh' first to create the dataset.")
        return

    with open(DATASET_FILE, "r") as f:
        lines = f.readlines()

    examples = [json.loads(line) for line in lines if line.strip()]

    # Analyze dataset
    output_lengths = [len(ex.get("output", "")) for ex in examples]
    instruction_topics = Counter()
    for ex in examples:
        instr = ex.get("instruction", "").lower()
        for topic in ["system", "python", "docker", "git", "backup",
                       "network", "disk", "download", "file", "project"]:
            if topic in instr:
                instruction_topics[topic] += 1

    print("=" * 60)
    print("  Dataset Statistics")
    print("=" * 60)
    print(f"  Total examples:      {len(examples)}")
    print(f"  Avg output length:   {sum(output_lengths) // len(output_lengths)} chars")
    print(f"  Min output length:   {min(output_lengths)} chars")
    print(f"  Max output length:   {max(output_lengths)} chars")
    print()
    print("  Topics:")
    for topic, count in instruction_topics.most_common():
        print(f"    {topic:12s}: {count} examples")
    print()
    print(f"  Recommended base models:")
    print("    - codellama/CodeLlama-7b-Python-hf")
    print("    - deepseek-ai/deepseek-coder-6.7b-instruct")
    print("    - mistralai/Mistral-7B-Instruct-v0.2")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--stats":
            show_stats()
        elif sys.argv[1] == "--prepare":
            show_instructions()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Usage: python convert-to-gguf.py [--stats | --prepare]")
    else:
        show_instructions()
PYEOF
chmod +x "${OUTPUT_DIR}/convert-to-gguf.py"

echo "│  Created: convert-to-gguf.py (helper script)                  │"
echo "│                                                               │"
echo "└───────────────────────────────────────────────────────────────┘"
echo ""

# ── Step 5: Create a README for the export ──────────────────────────────────

cat > "${OUTPUT_DIR}/README-GGUF.txt" << READMEEOF
================================================================================
                     BSL AI - GGUF Export
================================================================================

This directory contains the exported training data and configuration for
converting the BSL AI Script Generator into GGUF format.

GGUF is the file format used by llama.cpp and other LLM inference engines.
It stores quantized neural network weights for efficient inference.

FILES IN THIS DIRECTORY:
  bsl-training-dataset.jsonl    - Training examples in JSONL format
                                  (one JSON object per line)
  bsl-corpus.json               - Full structured corpus with metadata
  gguf-model-config.json        - GGUF model configuration and conversion
                                  instructions
  convert-to-gguf.py            - Helper script for dataset analysis and
                                  conversion guidance
  bsl-ai-state.json             - (if --train used) Saved AI training state

USING THE DATASET:

  1. Choose a base model (CodeLlama, DeepSeek Coder, or similar)
  2. Use the JSONL dataset for fine-tuning
  3. Convert to GGUF using llama.cpp's convert.py
  4. Quantize for smaller file size (optional)
  5. Run inference with llama.cpp

For detailed instructions, run:
  python convert-to-gguf.py

For dataset statistics:
  python convert-to-gguf.py --stats

See gguf-model-config.json for the recommended fine-tuning parameters.
================================================================================
READMEEOF

# ── Summary ──────────────────────────────────────────────────────────────────

echo "┌─ Summary ─────────────────────────────────────────────────────┐"
echo "│                                                               │"
echo "│  All files exported to: ${OUTPUT_DIR}             │"
echo "│                                                               │"
echo "│  Files created:                                                │"
ls -lh "${OUTPUT_DIR}/" | awk '{print "│    " $9 " (" $5 ")"}' | while read -r line; do
    printf "  %-60s│\n" "$line"
done
echo "│                                                               │"
echo "│  Next steps:                                                  │"
echo "│    1. Review bsl-training-dataset.jsonl                       │"
echo "│    2. Fine-tune a base model with the dataset                 │"
echo "│    3. Convert to GGUF with llama.cpp's convert.py             │"
echo "│    4. Run inference with llama.cpp or any GGUF-compatible tool│"
echo "│                                                               │"
echo "└───────────────────────────────────────────────────────────────┘"
