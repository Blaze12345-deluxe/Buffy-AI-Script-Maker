"""
bsl_train.py - BSL Training Pipeline

Loads the training corpus, analyzes patterns, and prepares the
generator for use. Supports saving and loading training state
so you can train, stop, and resume later.

Usage:
    python bsl_train.py                      # Show training summary
    python bsl_train.py --export             # Export training data as JSON
    python bsl_train.py --export-format      # Export BSL format reference
    python bsl_train.py --save-state state.json   # Save state for later resume
    python bsl_train.py --resume state.json       # Resume from saved state
"""

import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional

from training_data import (
    TRAINING_EXAMPLES,
    PATTERN_TEMPLATES,
    INSTRUCTION_PATTERNS,
    get_all_tags,
    get_all_dependencies,
    summary as corpus_summary,
)


class BSLAITrainer:
    """
    Trains/loads the BSL generation system.
    In this implementation, "training" means loading the corpus
    and preparing data structures for the generator.

    Supports saving and loading state so training can be resumed
    later without reloading the raw corpus.
    """

    STATE_VERSION = "1.0.0"

    def __init__(self):
        self.corpus = TRAINING_EXAMPLES
        self.templates = PATTERN_TEMPLATES
        self.instructions = INSTRUCTION_PATTERNS
        self.tags = get_all_tags()
        self.dependencies = get_all_dependencies()
        self.trained_at = datetime.now().isoformat()

        # Extended training data (populated during training sessions)
        self.custom_examples: List[Dict] = []       # User-added examples
        self.hit_count: Dict[str, int] = {}         # How often each example was matched
        self.recent_prompts: List[str] = []          # Last 50 prompts for analysis

    # ── State Persistence ──────────────────────────────────────────────────────

    def to_dict(self) -> Dict:
        """Serialize the trainer state to a dictionary."""
        return {
            "state_version": self.STATE_VERSION,
            "exported_at": datetime.now().isoformat(),
            "trained_at": self.trained_at,
            "corpus": {
                "total_examples": len(self.corpus),
                "total_custom": len(self.custom_examples),
                "total_tags": len(self.tags),
                "total_dependencies": len(self.dependencies),
                "tags": self.tags,
                "dependencies": self.dependencies,
                "script_names": [ex["name"] for ex in self.corpus],
                "custom_names": [ex["name"] for ex in self.custom_examples],
            },
            "templates": {
                "count": len(self.templates),
                "names": list(self.templates.keys()),
            },
            "instructions": {
                "count": len(self.instructions),
                "names": list(self.instructions.keys()),
            },
            "training_metrics": {
                "hit_count": self.hit_count,
                "recent_prompts_count": len(self.recent_prompts),
            },
            # Export the corpus examples (full source) for full restoration
            "examples": [
                {
                    "name": ex["name"],
                    "description": ex["description"],
                    "tags": ex["tags"],
                    "dependencies": ex["dependencies"],
                    "args": ex["args"],
                    "source": ex["source"],
                }
                for ex in self.corpus
            ],
            "custom_examples": self.custom_examples,
        }

    def save_state(self, filepath: str) -> str:
        """
        Save the current training state to a JSON file.
        Returns the JSON string (also written to file).
        """
        state = self.to_dict()
        json_str = json.dumps(state, indent=2)
        with open(filepath, "w") as f:
            f.write(json_str)
        print(f"Training state saved to {filepath} ({len(json_str)} bytes)")
        return json_str

    @classmethod
    def load_state(cls, filepath: str) -> "BSLAITrainer":
        """
        Load a previously saved training state from a JSON file.
        Restores all corpus data, patterns, and training metrics.
        """
        if not os.path.exists(filepath):
            print(f"Error: State file not found: {filepath}", file=sys.stderr)
            sys.exit(1)

        try:
            with open(filepath, "r") as f:
                state = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Corrupt state file {filepath}: {e}", file=sys.stderr)
            print("Tip: Delete the state file and re-run training.", file=sys.stderr)
            sys.exit(1)

        # Create a new trainer with minimal init and populate from saved state
        trainer = object.__new__(cls)
        trainer.corpus = TRAINING_EXAMPLES
        trainer.templates = PATTERN_TEMPLATES
        trainer.instructions = INSTRUCTION_PATTERNS
        trainer.tags = get_all_tags()
        trainer.dependencies = get_all_dependencies()
        trainer.custom_examples = []
        trainer.hit_count = {}
        trainer.recent_prompts = []
        trainer.trained_at = state.get("trained_at", datetime.now().isoformat())

        # Restore corpus if saved (otherwise keep the default)
        if "examples" in state and state["examples"]:
            trainer.corpus = state["examples"]

        # Restore custom examples
        trainer.custom_examples = state.get("custom_examples", [])

        # Restore training metrics
        trainer.hit_count = state.get("training_metrics", {}).get("hit_count", {})
        trainer.recent_prompts = state.get("training_metrics", {}).get("recent_prompts", [])

        # Recompute tags and dependencies from restored corpus
        combined = trainer.corpus + trainer.custom_examples
        tags = set()
        deps = set()
        for ex in combined:
            tags.update(ex.get("tags", []))
            deps.update(ex.get("dependencies", []))
        trainer.tags = sorted(tags)
        trainer.dependencies = sorted(deps)

        print(f"Training state loaded from {filepath}")
        print(f"  Examples: {len(trainer.corpus)} (+ {len(trainer.custom_examples)} custom)")
        print(f"  Tags: {len(trainer.tags)}, Dependencies: {len(trainer.dependencies)}")
        if trainer.hit_count:
            print(f"  Match history: {sum(trainer.hit_count.values())} total")
        return trainer

    # ── Extended Training ──────────────────────────────────────────────────────

    def add_example(self, name: str, description: str, source: str,
                    tags: List[str] = None, dependencies: List[str] = None,
                    args: List[str] = None, prompt_keywords: List[str] = None) -> Dict:
        """
        Add a new training example from a generated or user-provided script.
        Returns the example dict that was added.
        """
        example = {
            "name": name,
            "description": description,
            "prompt_keywords": prompt_keywords or [name.replace("-", " ")],
            "tags": tags or [],
            "dependencies": dependencies or [],
            "args": args or [],
            "source": source,
        }
        self.custom_examples.append(example)

        # Update tags and dependencies
        for t in example["tags"]:
            if t not in self.tags:
                self.tags.append(t)
        for d in example["dependencies"]:
            if d not in self.dependencies:
                self.dependencies.append(d)

        return example

    def record_match(self, example_name: str):
        """Record that an example was matched (for hit tracking)."""
        self.hit_count[example_name] = self.hit_count.get(example_name, 0) + 1

    def record_prompt(self, prompt: str):
        """Record a prompt for analysis (keeps last 50)."""
        self.recent_prompts.append(prompt)
        if len(self.recent_prompts) > 50:
            self.recent_prompts = self.recent_prompts[-50:]

    # ── Training Summary ───────────────────────────────────────────────────────

    def train_summary(self) -> Dict:
        """Return a detailed summary of the training state."""
        return {
            "name": "BSL AI Trainer",
            "version": self.STATE_VERSION,
            "trained_at": self.trained_at,
            "corpus": {
                "total_examples": len(self.corpus),
                "total_custom": len(self.custom_examples),
                "total_tags": len(self.tags),
                "total_dependencies": len(self.dependencies),
                "tags": self.tags,
                "dependencies": self.dependencies,
                "script_names": [ex["name"] for ex in self.corpus],
                "custom_names": [ex["name"] for ex in self.custom_examples],
            },
            "templates": {
                "count": len(self.templates),
                "names": list(self.templates.keys()),
            },
            "instructions": {
                "count": len(self.instructions),
                "names": list(self.instructions.keys()),
            },
            "training_metrics": {
                "total_matches": sum(self.hit_count.values()),
                "hit_count": self.hit_count,
                "recent_prompts": self.recent_prompts[-5:],  # Last 5 prompts
            },
        }

    # ── Export ─────────────────────────────────────────────────────────────────

    def export_corpus_json(self, filepath: Optional[str] = None) -> str:
        """
        Export the training corpus as JSON for use by external AI/LLM systems.
        If filepath is provided, writes to file. Returns the JSON string.
        """
        combined = self.corpus + self.custom_examples
        export = {
            "metadata": {
                "format": "bsl-training-corpus",
                "version": self.STATE_VERSION,
                "exported_at": self.trained_at,
                "total_examples": len(combined),
                "description": "BSL (Buffy Script Language) training examples for AI script generation",
            },
            "language_spec": {
                "file_extension": ".bsl",
                "encoding": "UTF-8",
                "metadata_fields": ["VERSION", "AUTHOR", "DESCRIPTION", "OUTPUT"],
                "instructions": [
                    {
                        "name": name,
                        "syntax": info["pattern"],
                        "description": info["description"],
                        "notes": info["usage_notes"],
                    }
                    for name, info in self.instructions.items()
                ],
                "builtin_variables": ["HOME", "USER", "PWD", "TEMP", "DATE", "TIME"],
            },
            "templates": {
                name: tmpl["structure"]
                for name, tmpl in self.templates.items()
            },
            "examples": [
                {
                    "name": ex["name"],
                    "description": ex["description"],
                    "tags": ex.get("tags", []),
                    "dependencies": ex.get("dependencies", []),
                    "args": ex.get("args", []),
                    "source": ex.get("source", ""),
                }
                for ex in combined
            ],
        }

        json_str = json.dumps(export, indent=2)

        if filepath:
            with open(filepath, "w") as f:
                f.write(json_str)
            print(f"Corpus exported to {filepath} ({len(json_str)} bytes)")

        return json_str

    def export_training_dataset_jsonl(self, filepath: str = "bsl-training.jsonl") -> str:
        """
        Export the corpus as a JSONL fine-tuning dataset.
        Each line contains {"instruction": "...", "output": "..."} pairs
        suitable for training LLMs to generate BSL scripts.
        """
        combined = self.corpus + self.custom_examples
        count = 0
        with open(filepath, "w") as f:
            for ex in combined:
                # Create instruction from description and args
                instruction = f"Create a BSL script that {ex['description'].lower()}"
                if ex.get("args"):
                    instruction += f" with arguments: {', '.join(ex['args'])}"

                entry = {
                    "instruction": instruction,
                    "input": "",
                    "output": ex.get("source", ""),
                }
                f.write(json.dumps(entry) + "\n")
                count += 1
        print(f"Training dataset exported to {filepath} ({count} examples)")
        return filepath

    def export_format_reference(self) -> str:
        """Export a human-readable BSL format reference."""
        lines = []
        lines.append("=" * 60)
        lines.append("  BSL (Buffy Script Language) Format Reference")
        lines.append("=" * 60)
        lines.append("")

        # Metadata
        lines.append("METADATA (must appear before any instructions):")
        lines.append("-" * 40)
        lines.append('  VERSION     = "YYYY.MM.DD"')
        lines.append('  AUTHOR      = "Creator name"')
        lines.append('  DESCRIPTION = "What the script does"')
        lines.append("  OUTPUT      = true  (visible) or false (silent)")
        lines.append("")

        # Instructions
        lines.append("INSTRUCTIONS (one per line, executed top-to-bottom):")
        lines.append("-" * 40)
        for name, info in self.instructions.items():
            lines.append(f"  {info['pattern']}")
            lines.append(f"      {info['description']}")
        lines.append("")

        # Variables
        lines.append("BUILT-IN VARIABLES (expanded at runtime):")
        lines.append("-" * 40)
        lines.append("  ${HOME}    - Home directory")
        lines.append("  ${USER}    - Current username")
        lines.append("  ${PWD}     - Current working directory")
        lines.append("  ${TEMP}    - System temp directory")
        lines.append("  ${DATE}    - Current date (YYYY-MM-DD)")
        lines.append("  ${TIME}    - Current time (HH:MM:SS)")
        lines.append("  ${1}-${N}  - Script arguments")
        lines.append("")

        # Comments
        lines.append("COMMENTS:")
        lines.append("-" * 40)
        lines.append("  // This is a comment")
        lines.append('  WRITE "hi"  // Inline comment')
        lines.append("")

        # Examples summary
        combined = self.corpus + self.custom_examples
        lines.append(f"CORPUS: {len(combined)} training examples")
        lines.append("-" * 40)
        for ex in combined:
            args_str = ", ".join(ex.get("args", [])) or "(none)"
            deps_str = ", ".join(ex.get("dependencies", [])) or "(none)"
            lines.append(f"  {ex['name']}")
            lines.append(f"    Description: {ex.get('description', '')}")
            lines.append(f"    Args: {args_str}")
            lines.append(f"    Deps: {deps_str}")
        lines.append("")

        return "\n".join(lines)


def main():
    # Check for --resume first (needs state before creating trainer)
    if "--resume" in sys.argv:
        idx = sys.argv.index("--resume")
        if idx + 1 < len(sys.argv):
            state_file = sys.argv[idx + 1]
            trainer = BSLAITrainer.load_state(state_file)
            # Remove --resume and its argument so other flags work
            sys.argv.pop(idx + 1)
            sys.argv.pop(idx)
        else:
            print("Error: --resume requires a file path", file=sys.stderr)
            sys.exit(1)
    else:
        trainer = BSLAITrainer()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--export":
            filepath = sys.argv[2] if len(sys.argv) > 2 else None
            trainer.export_corpus_json(filepath)

        elif sys.argv[1] == "--export-format":
            print(trainer.export_format_reference())

        elif sys.argv[1] == "--export-all":
            output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
            os.makedirs(output_dir, exist_ok=True)
            corpus_path = os.path.join(output_dir, "bsl-corpus.json")
            fmt_path = os.path.join(output_dir, "bsl-format-reference.txt")
            trainer.export_corpus_json(corpus_path)
            with open(fmt_path, "w") as f:
                f.write(trainer.export_format_reference())
            print(f"Exported to {output_dir}/")

        elif sys.argv[1] == "--save-state":
            filepath = sys.argv[2] if len(sys.argv) > 2 else "bsl-ai-state.json"
            trainer.save_state(filepath)

        elif sys.argv[1] == "--export-dataset":
            filepath = sys.argv[2] if len(sys.argv) > 2 else "bsl-training.jsonl"
            trainer.export_training_dataset_jsonl(filepath)

        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Usage: python bsl_train.py [--export [file] | --export-format |")
            print("       --export-all [dir] | --save-state [file] | --resume <file> |")
            print("       --export-dataset [file]]")

    else:
        # Default: show summary
        summary = trainer.train_summary()
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
