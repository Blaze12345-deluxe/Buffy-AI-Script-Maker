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
#   ./compile-to-gguf.sh --verify                  # Verify the GGUF container
#   ./compile-to-gguf.sh --output-dir ./gguf-data  # Custom output directory
#   ./compile-to-gguf.sh --help                    # Show this help
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/gguf-export"
TRAIN_FIRST=false
VERIFY=false

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
        --verify)
            VERIFY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--train] [--verify] [--output-dir <dir>]"
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

# ── Step 4: Build the GGUF container ────────────────────────────────────────

echo "┌─ Step 4: Building GGUF container ────────────────────────────┐"
echo "│                                                               │"

GGUF_FILE="${OUTPUT_DIR}/bsl-ai-minimal.gguf"
VERIFY_FLAG=""
if [ "$VERIFY" = true ]; then
    VERIFY_FLAG="--verify"
fi

python3 "${SCRIPT_DIR}/build-gguf-container.py" \
    --dataset "${JSONL_FILE}" \
    --corpus "${CORPUS_FILE}" \
    --output "${GGUF_FILE}" \
    ${VERIFY_FLAG}

echo "│                                                               │"
echo "└───────────────────────────────────────────────────────────────┘"
echo ""

# ── Step 5: Create a README for the export ──────────────────────────────────

echo "┌─ Step 5: Creating README for the export ──────────────────────┐"
echo "│                                                               │"

cat > "${OUTPUT_DIR}/README-GGUF.txt" << READMEEOF
================================================================================
                     BSL AI - GGUF Export
================================================================================

This directory contains the exported training data and a valid GGUF
container for the BSL AI Script Generator.

GGUF is the file format used by llama.cpp and other LLM inference engines.
It stores quantized neural network weights for efficient inference.

FILES IN THIS DIRECTORY:
  bsl-ai-minimal.gguf           - Valid GGUF v3 container with metadata
                                  (metadata only, no tensors/weights)
  bsl-training-dataset.jsonl    - Training examples in JSONL format
                                  (one JSON object per line)
  bsl-corpus.json               - Full structured corpus with metadata
  bsl-ai-state.json             - (if --train used) Saved AI training state

The .gguf file is a real GGUF binary that can be inspected with any
GGUF-compatible tool. Use --verify to validate the file structure.

USING THE DATASET FOR ACTUAL FINE-TUNING:

  1. Choose a base model (CodeLlama, DeepSeek Coder, or similar)
  2. Use the JSONL dataset for fine-tuning
  3. Convert the fine-tuned model to GGUF using llama.cpp's convert.py
  4. Quantize for smaller file size (optional)
  5. Run inference with llama.cpp
================================================================================
READMEEOF

echo "│  Created: README-GGUF.txt                                      │"
echo "│                                                               │"
echo "└───────────────────────────────────────────────────────────────┘"
echo ""

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
echo "│    1. Inspect the .gguf file with any GGUF-compatible tool    │"
echo "│    2. Use bsl-training-dataset.jsonl for LLM fine-tuning      │"
echo "│    3. Convert the fine-tuned model to GGUF with llama.cpp     │"
echo "│    4. Run inference with llama.cpp or any GGUF-compatible tool│"
echo "│                                                               │"
echo "└───────────────────────────────────────────────────────────────┘"
