#!/usr/bin/env python3
"""
build-gguf-container.py - Build a minimal valid GGUF container

Produces a real binary .gguf file following the GGUF v3 specification:
  https://github.com/ggml-org/ggml/blob/master/docs/gguf.md

This container stores metadata only (no tensors/weights). It is a valid
GGUF file that can be loaded by any GGUF-compatible parser.

GGUF binary layout:
  [Header 24 bytes] [KV metadata ...] [Tensor info (none)] [Tensor data (none)]

Header:
  - magic:        uint32 = 0x46554747 ("GGUF")
  - version:      uint32 = 3
  - tensor_count: uint64 = 0
  - kv_count:     uint64 = N

Each KV pair:
  - key:          string (uint64 length + UTF-8 bytes)
  - value_type:   uint32 (enum)
  - value:        varies by type

Usage:
  python build-gguf-container.py --dataset bsl-training-dataset.jsonl \\
      --output bsl-ai.gguf --verify
"""

import struct
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# GGUF metadata value type enum (v3)
GGUF_TYPE_UINT8   = 0
GGUF_TYPE_INT8    = 1
GGUF_TYPE_UINT16  = 2
GGUF_TYPE_INT16   = 3
GGUF_TYPE_UINT32  = 4
GGUF_TYPE_INT32   = 5
GGUF_TYPE_FLOAT32 = 6
GGUF_TYPE_BOOL    = 7
GGUF_TYPE_STRING  = 8
GGUF_TYPE_ARRAY   = 9
GGUF_TYPE_UINT64  = 10
GGUF_TYPE_INT64   = 11
GGUF_TYPE_FLOAT64 = 12

GGUF_MAGIC = 0x46554747  # "GGUF" in little-endian ASCII
GGUF_VERSION = 3


# ── Binary Packing Helpers ──────────────────────────────────────────────────


def _pack_string(s: str) -> bytes:
    """Pack a string as GGUF string: uint64 length + UTF-8 data."""
    encoded = s.encode("utf-8")
    return struct.pack("<Q", len(encoded)) + encoded


def _pack_kv(key: str, value_type: int, value_bytes: bytes) -> bytes:
    """Pack a complete GGUF metadata key-value pair."""
    return _pack_string(key) + struct.pack("<I", value_type) + value_bytes


def _pack_value(value: Any) -> tuple:
    """
    Pack a Python value into GGUF binary data.
    Returns (value_type_int, packed_bytes).
    """
    if isinstance(value, str):
        return GGUF_TYPE_STRING, _pack_string(value)

    if isinstance(value, bool):
        return GGUF_TYPE_BOOL, struct.pack("<?", value)

    if isinstance(value, int):
        if 0 <= value < 2**32:
            return GGUF_TYPE_UINT32, struct.pack("<I", value)
        return GGUF_TYPE_UINT64, struct.pack("<Q", value)

    if isinstance(value, float):
        return GGUF_TYPE_FLOAT32, struct.pack("<f", value)

    if isinstance(value, list):
        if not value:
            # Empty array — element type is arbitrary; use UINT8
            return GGUF_TYPE_ARRAY, (
                struct.pack("<I", GGUF_TYPE_UINT8) + struct.pack("<Q", 0)
            )

        # Determine element type from the first element
        first = value[0]
        if isinstance(first, str):
            elem_type = GGUF_TYPE_STRING
            elem_packer = lambda v: _pack_string(v)  # noqa: E731
        elif isinstance(first, bool):
            elem_type = GGUF_TYPE_BOOL
            elem_packer = lambda v: struct.pack("<?", v)  # noqa: E731
        elif isinstance(first, int):
            elem_type = GGUF_TYPE_UINT32
            elem_packer = lambda v: struct.pack("<I", v)  # noqa: E731
        elif isinstance(first, float):
            elem_type = GGUF_TYPE_FLOAT32
            elem_packer = lambda v: struct.pack("<f", v)  # noqa: E731
        else:
            # Fallback: convert to strings
            elem_type = GGUF_TYPE_STRING
            elem_packer = lambda v: _pack_string(str(v))  # noqa: E731

        arr_data = struct.pack("<I", elem_type) + struct.pack("<Q", len(value))
        for v in value:
            arr_data += elem_packer(v)
        return GGUF_TYPE_ARRAY, arr_data

    # Fallback: stringify
    return GGUF_TYPE_STRING, _pack_string(str(value))


# ── GGUF Builder ────────────────────────────────────────────────────────────


def build_gguf(metadata: Dict[str, Any]) -> bytes:
    """
    Build a complete GGUF binary from a metadata dictionary.

    The dictionary keys become GGUF metadata keys (strings) and values
    are auto-typed (int→UINT32, str→STRING, list→ARRAY, bool→BOOL, float→FLOAT32).
    """
    # Pack all KV pairs
    kv_parts = []
    for key, value in metadata.items():
        vtype, vdata = _pack_value(value)
        kv_parts.append(_pack_kv(key, vtype, vdata))

    # Build header: magic(4) + version(4) + tensor_count(8) + kv_count(8)
    header = struct.pack("<IIQQ", GGUF_MAGIC, GGUF_VERSION, 0, len(metadata))

    return header + b"".join(kv_parts)


# ── Container Builder ───────────────────────────────────────────────────────


def build_container(
    dataset_jsonl: str,
    output_path: str,
    corpus_json: Optional[str] = None,
) -> str:
    """
    Read exported training data and build a metadata-only GGUF container.

    Args:
        dataset_jsonl: Path to bsl-training-dataset.jsonl
        output_path: Path for the output .gguf file
        corpus_json: Optional path to bsl-corpus.json (unused currently)

    Returns:
        Path to the generated .gguf file
    """
    if not os.path.exists(dataset_jsonl):
        print(f"Error: Dataset file not found: {dataset_jsonl}", file=sys.stderr)
        sys.exit(1)

    # ── Parse the JSONL dataset ──
    examples: List[dict] = []
    authors: set = set()
    topics: set = set()
    output_lengths: list = []

    with open(dataset_jsonl, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ex = json.loads(line)
            examples.append(ex)
            output = ex.get("output", "")
            output_lengths.append(len(output))

            # Extract AUTHOR from BSL metadata in the output
            if "AUTHOR" in output:
                for out_line in output.split("\n"):
                    stripped = out_line.strip()
                    if stripped.startswith("AUTHOR") and "=" in stripped:
                        parts = stripped.split("=", 1)
                        if len(parts) > 1:
                            author = parts[1].strip().strip('"').strip("'").strip()
                            if author:
                                authors.add(author)

            # Detect topics from instruction text
            instr = ex.get("instruction", "").lower()
            topic_map = {
                "system": ["system", "os", "kernel", "memory", "disk"],
                "python": ["python", "pip", "venv", "virtualenv"],
                "docker": ["docker", "container"],
                "git": ["git", "repository", "commit"],
                "backup": ["backup", "archive", "tar", "compress"],
                "network": ["network", "ping", "dns", "curl", "wget", "download"],
                "development": ["project", "scaffold", "template"],
                "maintenance": ["cleanup", "prune", "update", "upgrade"],
                "diagnostics": ["diagnostic", "info", "report", "usage"],
                "files": ["file", "directory", "folder", "find", "search"],
            }
            for topic, keywords in topic_map.items():
                if any(kw in instr for kw in keywords):
                    topics.add(topic)

    count = len(examples)

    # ── Build metadata dictionary ──

    metadata: Dict[str, Any] = {}

    # General model identification
    metadata["general.name"] = "BSL-AI-Script-Generator"
    metadata["general.description"] = (
        f"BSL Script Generator - generates .bsl Buffy Script Language files "
        f"from natural language. Trained on {count} examples."
    )
    metadata["general.file_type"] = 0       # MODEL
    metadata["general.architecture"] = "llama"
    metadata["general.alignment"] = 32
    metadata["general.basename"] = "bsl-ai-script-generator"
    metadata["general.size_label"] = "tiny"

    # Dataset statistics
    metadata["dataset.instruction_count"] = count
    metadata["dataset.format"] = "jsonl"
    metadata["dataset.authors"] = sorted(authors) if authors else ["Buffy Community"]
    metadata["dataset.topics"] = sorted(topics) if topics else ["script-generation"]

    if output_lengths:
        metadata["dataset.avg_output_length"] = sum(output_lengths) // count
        metadata["dataset.max_output_length"] = max(output_lengths)
        metadata["dataset.min_output_length"] = min(output_lengths)

    # BSL-specific metadata
    metadata["bsl.version"] = "1.0.0"
    metadata["bsl.num_examples"] = count
    metadata["bsl.language"] = "BSL (Buffy Script Language)"
    metadata["bsl.file_extension"] = ".bsl"

    # Training configuration
    metadata["training.context_length"] = 2048
    metadata["training.has_tokenizer"] = False

    # ── Build the binary ──
    gguf_data = build_gguf(metadata)

    # ── Write file ──
    with open(output_path, "wb") as f:
        f.write(gguf_data)

    file_size = len(gguf_data)
    print(f"  GGUF container: {output_path}")
    print(f"  Size: {file_size} bytes")
    print(f"  Metadata entries: {len(metadata)}")
    print(f"  Tensor count: 0 (metadata-only)")
    print(f"  GGUF version: {GGUF_VERSION}")
    print(f"  Dataset examples: {count}")
    print(f"  Topics: {', '.join(sorted(topics))}")
    print(f"  Built: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return output_path


# ── Verification / Read-Back ────────────────────────────────────────────────


def verify_gguf(filepath: str) -> dict:
    """
    Open a GGUF file and verify its structure by reading back all metadata.
    Returns a dict of parsed metadata.
    """
    with open(filepath, "rb") as f:
        data = f.read()

    if len(data) < 24:
        raise ValueError(f"File too small ({len(data)} bytes) — not a valid GGUF")

    magic, version, tensor_count, kv_count = struct.unpack_from("<IIQQ", data, 0)

    if magic != GGUF_MAGIC:
        raise ValueError(
            f"Invalid magic number: {magic:#010x} (expected {GGUF_MAGIC:#010x})"
        )
    if version != GGUF_VERSION:
        raise ValueError(
            f"Unsupported GGUF version: {version} (expected {GGUF_VERSION})"
        )

    parsed: dict = {"version": version, "tensor_count": tensor_count}
    offset = 24

    for _ in range(kv_count):
        # Read key string
        key_len = struct.unpack_from("<Q", data, offset)[0]
        offset += 8
        key = data[offset:offset + key_len].decode("utf-8")
        offset += key_len

        # Read value type
        val_type = struct.unpack_from("<I", data, offset)[0]
        offset += 4

        # Read value based on type
        if val_type == GGUF_TYPE_STRING:
            str_len = struct.unpack_from("<Q", data, offset)[0]
            offset += 8
            val = data[offset:offset + str_len].decode("utf-8")
            offset += str_len

        elif val_type == GGUF_TYPE_BOOL:
            val = bool(struct.unpack_from("<?", data, offset)[0])
            offset += 1

        elif val_type == GGUF_TYPE_UINT32:
            val = struct.unpack_from("<I", data, offset)[0]
            offset += 4

        elif val_type == GGUF_TYPE_UINT64:
            val = struct.unpack_from("<Q", data, offset)[0]
            offset += 8

        elif val_type == GGUF_TYPE_FLOAT32:
            val = struct.unpack_from("<f", data, offset)[0]
            offset += 4

        elif val_type == GGUF_TYPE_FLOAT64:
            val = struct.unpack_from("<d", data, offset)[0]
            offset += 8

        elif val_type == GGUF_TYPE_INT32:
            val = struct.unpack_from("<i", data, offset)[0]
            offset += 4

        elif val_type == GGUF_TYPE_ARRAY:
            elem_type = struct.unpack_from("<I", data, offset)[0]
            offset += 4
            arr_len = struct.unpack_from("<Q", data, offset)[0]
            offset += 8
            arr_vals = []
            for _ in range(arr_len):
                if elem_type == GGUF_TYPE_STRING:
                    s_len = struct.unpack_from("<Q", data, offset)[0]
                    offset += 8
                    s_val = data[offset:offset + s_len].decode("utf-8")
                    offset += s_len
                    arr_vals.append(s_val)
                elif elem_type == GGUF_TYPE_UINT32:
                    arr_vals.append(struct.unpack_from("<I", data, offset)[0])
                    offset += 4
                elif elem_type == GGUF_TYPE_FLOAT32:
                    arr_vals.append(struct.unpack_from("<f", data, offset)[0])
                    offset += 4
                elif elem_type == GGUF_TYPE_BOOL:
                    arr_vals.append(bool(struct.unpack_from("<?", data, offset)[0]))
                    offset += 1
                else:
                    arr_vals.append(f"<type {elem_type}>")
            val = arr_vals

        else:
            val = f"<unhandled type {val_type}>"

        parsed[key] = val

    return parsed


# ── CLI ─────────────────────────────────────────────────────────────────────


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Build a minimal valid GGUF container from BSL training data",
    )
    parser.add_argument(
        "--dataset", "-d",
        required=True,
        help="Path to bsl-training-dataset.jsonl",
    )
    parser.add_argument(
        "--corpus", "-c",
        default=None,
        help="Path to bsl-corpus.json (optional, currently unused)",
    )
    parser.add_argument(
        "--output", "-o",
        default="bsl-ai-minimal.gguf",
        help="Output .gguf file path (default: bsl-ai-minimal.gguf)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify the generated GGUF file by reading all metadata back",
    )

    args = parser.parse_args()

    output_path = build_container(
        dataset_jsonl=args.dataset,
        output_path=args.output,
        corpus_json=args.corpus,
    )

    if args.verify:
        print("\n  ── Verification ──")
        parsed = verify_gguf(output_path)
        print(f"  Version:        {parsed['version']}")
        print(f"  Tensor count:   {parsed['tensor_count']}")
        print(f"  Metadata items: {len(parsed) - 2}")
        print(f"  Magic valid:    yes (0x{GGUF_MAGIC:08x})")
        print(f"  ✓ GGUF file is valid ({os.path.getsize(output_path)} bytes)")


if __name__ == "__main__":
    main()
