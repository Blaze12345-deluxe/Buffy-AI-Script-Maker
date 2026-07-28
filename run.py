#!/usr/bin/env python3
"""
run.py - BSL AI Script Generator CLI

Main entry point for the AI module. Takes a natural language prompt
and generates a complete .bsl script with syntax validation.

Supports saving and resuming training state so you can train,
stop, and resume later.

Usage:
    python run.py "create a script that backs up my home directory"
    python run.py "show system information" --output system-info.bsl
    python run.py "monitor disk space" --check
    python run.py --train                    # Show training corpus summary
    python run.py --save-state state.json    # Save training state
    python run.py --resume state.json        # Resume from saved state
    python run.py --interactive              # Interactive mode
"""

import sys
import os
import re
import argparse
import textwrap

from bsl_generator import generate_bsl, find_best_match
from bsl_tester import validate_bsl, format_as_bsl
from bsl_train import BSLAITrainer


def main():
    parser = argparse.ArgumentParser(
        prog="buffy-ai",
        description="Generate BSL scripts from natural language prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python run.py \"create a python virtual environment\"
              python run.py \"backup my project directory\" --output backup.bsl
              python run.py \"check disk usage\" --check
              python run.py --interactive
              python run.py --train
              python run.py --save-state state.json
              python run.py --resume state.json --train
              python run.py --learn existing-script.bsl --save-state state.json
              python run.py "backup my files" --learn --save-state state.json
        """),
    )

    # Main arguments
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Natural language description of the script to generate",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path for the generated .bsl script",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run syntax validation on the generated script",
    )
    parser.add_argument(
        "--buffy-check",
        action="store_true",
        help="Also run buffy --check for full validation (requires buffy in PATH)",
    )
    parser.add_argument(
        "--author",
        default="AI Generated",
        help="Author name for the script (default: AI Generated)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start interactive mode",
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Show training corpus summary",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output the generated script (no diagnostics)",
    )

    # ── Training continuation flags ──
    parser.add_argument(
        "--save-state",
        metavar="FILE",
        help="Save the current training state to FILE for later resumption",
    )
    parser.add_argument(
        "--resume",
        metavar="FILE",
        help="Resume from a previously saved training state FILE",
    )
    parser.add_argument(
        "--learn",
        metavar="FILE",
        nargs="?",
        const="__generated__",
        help="Import a .bsl file (or the generated script) as a custom training example. "
             "Reads the file, parses metadata, and adds it to the trainer's custom corpus. "
             "Use --save-state to persist the updated corpus.",
    )
    parser.add_argument(
        "--learn-name",
        metavar="NAME",
        help="Override the name for the learned example (default: derived from filename or prompt)",
    )
    parser.add_argument(
        "--learn-desc",
        metavar="DESC",
        help="Override the description for the learned example (default: parsed from BSL metadata)",
    )

    args = parser.parse_args()

    # ── Load trainer (with optional resume) ──
    if args.resume:
        trainer = BSLAITrainer.load_state(args.resume)
    else:
        trainer = BSLAITrainer()

    # ── Show training summary ──
    if args.train:
        if not args.quiet:
            summary = trainer.train_summary()
            print(f"BSL AI Trainer v{summary['version']}")
            print(f"Trained at: {summary['trained_at']}")
            print(f"Training examples: {summary['corpus']['total_examples']}")
            if summary['corpus']['total_custom'] > 0:
                print(f"  (includes {summary['corpus']['total_custom']} custom examples)")
            print(f"Tags: {len(summary['corpus']['tags'])}")
            print(f"Template patterns: {summary['templates']['count']}")
            print(f"Known instructions: {summary['instructions']['count']}")
            print(f"Dependencies tracked: {summary['corpus']['total_dependencies']}")
            print(f"Match history: {summary['training_metrics']['total_matches']} total matches")
            print(f"\\nAvailable tags: {', '.join(summary['corpus']['tags'])}")
            if summary['corpus']['custom_names']:
                print(f"Custom examples: {', '.join(summary['corpus']['custom_names'])}")
        return

    # ── Learn mode: import a .bsl file (no prompt) ──
    if args.learn and args.learn != "__generated__" and not args.prompt:
        _learn_from_file(trainer, args.learn, args)
        return

    # ── Save state and exit (no generation) ──
    if args.save_state and not args.prompt:
        trainer.save_state(args.save_state)
        return

    # ── Interactive mode ──
    if args.interactive:
        interactive_loop(args, trainer)
        return

    # ── Generate from prompt ──
    if not args.prompt:
        parser.print_help()
        print("\nError: No prompt provided. Describe what script you want to generate.")
        sys.exit(1)

    prompt = " ".join(args.prompt)
    result = generate_bsl(prompt, author=args.author, trainer=trainer)

    # ── Optional: Validate ──
    validation = None
    if args.check or args.buffy_check:
        validation = validate_bsl(
            result["source"],
            use_buffy_check=args.buffy_check,
        )

    # ── Output ──
    if args.quiet:
        # Only output the source code
        sys.stdout.write(result["source"])
    else:
        # Full diagnostic output
        _print_generation_report(result, validation)

        # Write to file if requested
        if args.output:
            _write_to_file(args.output, result["source"])
        else:
            # Print the source with a header
            print(f"\n{'='*60}")
            print(f"  Generated Script: {result['name']}")
            print(f"{'='*60}")
            print(result["source"])

    # Write to default filename if no output specified
    if not args.output and not args.quiet:
        save = input(f"\nSave to {result['name']}? [Y/n]: ").strip().lower()
        if save != "n":
            _write_to_file(result["name"], result["source"])

    # ── Learn mode: import the generated script ──
    if args.learn == "__generated__":
        _learn_generated_script(trainer, result, args)

    # ── Learn mode: also import a file alongside generation ──
    if args.learn and args.learn != "__generated__" and args.prompt:
        _learn_from_file(trainer, args.learn, args)

    # ── Auto-save state if --save-state was given ──
    if args.save_state:
        trainer.save_state(args.save_state)


def interactive_loop(args, trainer=None):
    """Run an interactive prompt loop."""
    if trainer is None:
        trainer = BSLAITrainer()

    print("=" * 60)
    print("  BSL AI Generator - Interactive Mode")
    print("=" * 60)
    print('  Type a description of the script you want to generate.')
    print('  Type "quit" to exit, "help" for commands.')
    print("=" * 60)
    print()

    while True:
        try:
            prompt = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not prompt:
            continue

        if prompt.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if prompt.lower() in ("help", "h", "?"):
            _print_interactive_help()
            continue

        if prompt.lower() == "train":
            summary = trainer.train_summary()
            print(f"\nCorpus: {summary['corpus']['total_examples']} examples, "
                  f"{summary['corpus']['total_tags']} tags, "
                  f"{summary['templates']['count']} templates\n")
            continue

        if prompt.lower().startswith("save"):
            # Save state from interactive mode
            parts = prompt.split(None, 1)
            filepath = parts[1] if len(parts) > 1 else "bsl-ai-state.json"
            trainer.save_state(filepath)
            continue

        if prompt.lower().startswith("export"):
            # Export from interactive mode
            parts = prompt.split(None, 1)
            filepath = parts[1] if len(parts) > 1 else "bsl-training.jsonl"
            if filepath.endswith(".jsonl"):
                trainer.export_training_dataset_jsonl(filepath)
            else:
                trainer.export_corpus_json(filepath)
            continue

        if prompt.lower().startswith("learn"):
            # Learn a .bsl file from interactive mode
            parts = prompt.split(None, 1)
            if len(parts) > 1:
                _learn_from_file(trainer, parts[1].strip(), 
                                 argparse.Namespace(save_state=None, learn_name=None, learn_desc=None))
            else:
                print("Usage: learn <file.bsl>  — Import a .bsl file as a training example")
            continue

        # Generate
        result = generate_bsl(prompt, author="AI Generated", trainer=trainer)
        validation = validate_bsl(result["source"])

        if validation.is_valid:
            print(f"\n  Generated: {result['name']} "
                  f"(matched: {result['matched_example']}, "
                  f"score: {result['match_score']})\n")
        else:
            print(f"\n  Generated: {result['name']} "
                  f"({validation.summary()})\n")

        # Show the script
        print(result["source"])
        print()

        save = input(f"  Save to {result['name']}? [y/N]: ").strip().lower()
        if save == "y":
            _write_to_file(result["name"], result["source"])
            print(f"  Saved to {result['name']}\n")


# ── BSL Metadata Parser (for --learn) ──────────────────────────────────────

def _parse_bsl_file(filepath: str) -> dict:
    """
    Parse a .bsl file and extract metadata for training.

    Returns a dict with:
      - name: filename stem
      - description: from DESCRIPTION metadata
      - source: full file content
      - tags: auto-generated from description and commands
      - dependencies: shell commands mentioned in RUN lines
      - args: argument names derived from ${N} usage
    """
    try:
        with open(filepath, "r") as f:
            source = f.read()
    except IOError as e:
        print(f"Error reading {filepath}: {e}")
        sys.exit(1)

    basename = os.path.splitext(os.path.basename(filepath))[0]

    # Extract DESCRIPTION
    desc_match = re.search(r'DESCRIPTION\s*=\s*"([^"]*)"', source)
    description = desc_match.group(1) if desc_match else f"Imported from {basename}"

    # Extract dependencies from RUN commands
    dep_pattern = re.compile(r'RUN\s+"([^"]+)"')
    run_commands = dep_pattern.findall(source)
    deps = set()
    for cmd in run_commands:
        parts = cmd.split()
        if parts:
            base_cmd = parts[0]
            # Strip path prefixes like ./ or /usr/bin/
            base_cmd = os.path.basename(base_cmd)
            if base_cmd and base_cmd not in ("sudo", "echo", "test", "["):
                deps.add(base_cmd)

    # Extract args from ${N} variable references
    arg_refs = set(re.findall(r'\$\{(\d)\}', source))
    args = [f"arg{i}" for i in range(1, int(max(arg_refs)) + 1)] if arg_refs else []

    # Auto-generate tags from description and commands
    tags = set()
    desc_lower = description.lower()
    tag_keywords = {
        "system": ["system", "os", "kernel", "memory", "disk"],
        "network": ["network", "ping", "dns", "http", "curl", "wget", "download"],
        "python": ["python", "pip", "venv", "virtualenv"],
        "docker": ["docker", "container"],
        "git": ["git", "repository", "commit"],
        "backup": ["backup", "archive", "tar"],
        "development": ["project", "scaffold", "setup", "template"],
        "maintenance": ["cleanup", "prune", "update", "upgrade"],
        "diagnostics": ["diagnostic", "info", "report", "usage"],
        "files": ["file", "directory", "folder", "find", "search"],
    }
    for tag, keywords in tag_keywords.items():
        if any(kw in desc_lower for kw in keywords):
            tags.add(tag)
    for dep in deps:
        if dep in tag_keywords:
            tags.add(dep)

    return {
        "name": basename,
        "description": description,
        "source": source,
        "tags": sorted(tags) or ["custom"],
        "dependencies": sorted(deps),
        "args": args,
    }


def _learn_from_file(trainer, filepath: str, args):
    """
    Import a .bsl file as a custom training example.
    Parses metadata automatically and adds to trainer.
    """
    info = _parse_bsl_file(filepath)

    name = args.learn_name if hasattr(args, "learn_name") and args.learn_name else info["name"]
    description = args.learn_desc if hasattr(args, "learn_desc") and args.learn_desc else info["description"]

    trainer.add_example(
        name=name,
        description=description,
        source=info["source"],
        tags=info["tags"],
        dependencies=info["dependencies"],
        args=info["args"],
        prompt_keywords=[description.lower(), name.replace("-", " ")],
    )

    print(f"\n  Learned: {name}.bsl")
    print(f"    Description: {description}")
    print(f"    Tags: {', '.join(info['tags'])}")
    print(f"    Dependencies: {', '.join(info['dependencies']) or '(none)'}")
    print(f"    Args: {', '.join(info['args']) or '(none)'}")
    print(f"  Custom examples: {len(trainer.custom_examples)}")

    learn_save_guidance(trainer, args)


def _learn_generated_script(trainer, result: dict, args):
    """
    Add the generated script as a custom training example.
    """
    name = args.learn_name if hasattr(args, "learn_name") and args.learn_name else result["name"]
    if name.endswith(".bsl"):
        name = name[:-4]

    description = args.learn_desc if hasattr(args, "learn_desc") and args.learn_desc else result["description"]

    # Auto-generate tags from the prompt
    tags = set(["custom", "ai-generated"])
    for dep in result["dependencies"]:
        tags.add(dep)
    prompt_lower = result["description"].lower()
    if any(kw in prompt_lower for kw in ["system", "os"]):
        tags.add("system")
    if any(kw in prompt_lower for kw in ["network", "ping", "dns", "download"]):
        tags.add("network")
    if "docker" in prompt_lower:
        tags.add("docker")
    if "python" in prompt_lower or "pip" in prompt_lower:
        tags.add("python")
    if "git" in prompt_lower:
        tags.add("git")
    if "backup" in prompt_lower or "archive" in prompt_lower:
        tags.add("backup")

    trainer.add_example(
        name=name,
        description=description,
        source=result["source"],
        tags=sorted(tags),
        dependencies=result["dependencies"],
        args=result["args"],
        prompt_keywords=[description.lower(), name.replace("-", " ")],
    )

    print(f"\n  Learned generated script: {name}")
    print(f"    Description: {description}")
    print(f"    Tags: {', '.join(sorted(tags))}")
    print(f"  Custom examples: {len(trainer.custom_examples)}")

    learn_save_guidance(trainer, args)


def learn_save_guidance(trainer, args):
    """
    Show guidance on how to persist the learned example.
    If --save-state was given, saves automatically; otherwise shows instructions.
    """
    save_state = getattr(args, "save_state", None)
    if save_state:
        trainer.save_state(save_state)
    else:
        print(f"  Tip: Run with --save-state <file> to persist learned examples.")
        print(f"       Or use --resume to load them in future sessions.")


def _print_generation_report(result: dict, validation=None):
    """Print a formatted generation report."""
    print(f"\n{'='*60}")
    print(f"  BSL Script Generation Report")
    print(f"{'='*60}")

    print(f"\n  Prompt:          {result['description']}")
    print(f"  Filename:        {result['name']}")
    print(f"  Dependencies:    {', '.join(result['dependencies']) or '(none)'}")
    print(f"  Arguments:       {', '.join(result['args']) or '(none)'}")

    if result.get("matched_example"):
        print(f"  Best match:      {result['matched_example']} "
              f"(score: {result['match_score']})")
    else:
        print(f"  Generation:      From scratch (no matching example)")

    if validation:
        print(f"  Validation:      {'PASSED' if validation.is_valid else 'HAS ISSUES'}")
        if not validation.is_valid:
            print(validation.detailed_report())


def _write_to_file(filepath: str, source: str):
    """Write the script to a file, ensuring .bsl extension."""
    if not filepath.endswith(".bsl"):
        filepath += ".bsl"
    try:
        with open(filepath, "w") as f:
            f.write(source)
        print(f"\n  Written to: {os.path.abspath(filepath)}")
    except IOError as e:
        print(f"\n  Error writing to {filepath}: {e}")


def _print_interactive_help():
    """Print help for interactive mode."""
    print()
    print("  Commands:")
    print("    <prompt>    Describe the script you want (e.g., 'create a docker cleanup script')")
    print("    quit        Exit interactive mode")
    print("    help        Show this help")
    print("    train       Show training corpus summary")
    print("    save        Save training state (save <file> or save bsl-ai-state.json)")
    print("    export      Export corpus (export <file> or export bsl-training.jsonl)")
    print("    learn       Import a .bsl file as training example (learn <file.bsl>)")
    print()


if __name__ == "__main__":
    main()
