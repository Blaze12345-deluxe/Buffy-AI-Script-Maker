#!/usr/bin/env python3
"""
.compile.py - Buffy Plugin Scaffolder

Interactive script that:
  1. Prompts for all plugin metadata (name, author, version, description)
  2. Creates the plugin directory and .bsl script files
  3. Generates SHA-256 checksum files for every .bsl file

Usage:
  python .compile.py                # Interactive mode
  python .compile.py --help         # Show help
  python .compile.py --output-dir .  # Specify where to create the plugin
"""

import hashlib
import json
import os
import re
import sys
from datetime import date


# ── Helpers ─────────────────────────────────────────────────────────────────


def read_line(prompt: str, default: str = "", required: bool = False) -> str:
    """Prompt the user for input with an optional default value."""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "

    while True:
        value = input(full_prompt).strip()
        if not value and default:
            return default
        if not value and required:
            print("  This field is required. Please enter a value.")
            continue
        return value



def sanitize_name(name: str) -> str:
    """Convert a name to kebab-case for use as a package/command name."""
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9\\-]", "-", name)
    name = re.sub(r"-+", "-", name)
    name = name.strip("-")
    return name


def sha256_file(filepath: str) -> str:
    """Compute the SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_sha256(filepath: str):
    """Write a .sha256 file alongside the given file."""
    sha = sha256_file(filepath)
    sha_path = filepath + ".sha256"
    filename = os.path.basename(filepath)
    with open(sha_path, "w") as f:
        f.write(f"{sha}  {filename}\n")
    print(f"  Created: {sha_path}")


# ── Scaffolders ────────────────────────────────────────────────────────────


def generate_index_bsl(pkg_name: str, author: str, version: str,
                       description: str, commands: list) -> str:
    """Generate the default index.bsl entry point script."""
    cmd_list = "\n".join(f"  WRITE \"  {cmd}    {desc}\"" for cmd, desc in commands)

    return f'''VERSION = "{version}"
AUTHOR = "{author}"
DESCRIPTION = "{description}"
OUTPUT = false

CLEAR

WRITE "========================================="
WRITE "  {pkg_name}"
WRITE "========================================="
WRITE ""
WRITE "  Version: {version}"
WRITE "  Author:  {author}"
WRITE ""
WRITE "-----------------------------------------"
WRITE "  Description"
WRITE "-----------------------------------------"
WRITE ""
WRITE "  {description}"
WRITE ""
WRITE "-----------------------------------------"
WRITE "  Commands"
WRITE "-----------------------------------------"
WRITE ""
{cmd_list}
WRITE ""
WRITE "========================================="

EXIT
'''


def generate_command_bsl(name: str, author: str, version: str,
                         description: str, pkg_name: str) -> str:
    """Generate a .bsl script for a specific command."""
    safe_name = sanitize_name(name)
    return f'''VERSION = "{version}"
AUTHOR = "{author}"
DESCRIPTION = "{description}"
OUTPUT = false

CLEAR

WRITE "========================================="
WRITE "  {pkg_name}: {name}"
WRITE "========================================="
WRITE ""
WRITE "  Welcome to the {name} command!"
WRITE "  Today is ${{DATE}}."
WRITE "  User: ${{USER}}"
WRITE ""

WRITE "-----------------------------------------"
WRITE "  Action"
WRITE "-----------------------------------------"
WRITE ""
WRITE "  TODO: Replace this section with your"
WRITE "  command logic. Add RUN \"shell command\""
WRITE "  or WRITE \"message\" statements below."
WRITE ""

// TODO: Add your command logic here
// Example:
//   RUN "echo Hello from {pkg_name}!"
//   OUTPUT = true
//   RUN "ls -la"
//   OUTPUT = false

WRITE ""
WRITE "========================================="

EXIT
'''


def generate_index_json(pkg_name: str, author: str, version: str,
                        description: str, commands: list, repo_url: str) -> str:
    """Generate the index.json file for repository distribution."""
    cmd_names = [sanitize_name(c[0]) for c in commands]
    cmd_names.insert(0, "index")

    data = {
        "name": pkg_name,
        "description": description,
        "version": version,
        "author": author,
        "commands": cmd_names,
        "dependencies": [],
        "tags": ["custom", "utility"],
        "repository": repo_url or "",
        "install_path": f"packages/{pkg_name}",
    }
    return json.dumps(data, indent=4)


# ── Main Scaffolding Flow ──────────────────────────────────────────────────


def scaffold():
    print("=" * 60)
    print("  Buffy Plugin Scaffolder")
    print("=" * 60)
    print()

    # ── 1. Package Metadata ──
    print("┌─ Package Metadata ──────────────────────────────────────────┐")
    print()

    pkg_name = sanitize_name(read_line("Package name", required=True))
    author = read_line("Author name", default=os.environ.get("USER", ""), required=True)
    version = read_line("Version", default=date.today().strftime("%Y.%m.%d"))
    description = read_line("Short description", required=True)
    repo_url = read_line("Repository URL (optional)", default="")

    print()
    print("└──────────────────────────────────────────────────────────────┘")
    print()

    # ── 2. Commands ──
    print("┌─ Commands ──────────────────────────────────────────────────┐")
    print()
    print("  Define the commands for your plugin. Each command becomes a")
    print("  .bsl file. At minimum, you need at least one command.")
    print()

    commands = []
    while True:
        raw_name = read_line("  Command name (or blank to finish)", default="")
        if not raw_name:
            if not commands:
                print("  You need at least one command!")
                continue
            break
        cmd_name = sanitize_name(raw_name)
        cmd_desc = read_line(f"  Description for '{cmd_name}'", required=True)
        commands.append((cmd_name, cmd_desc))
        print(f"  Added command: {cmd_name}")
        print()

    print("└──────────────────────────────────────────────────────────────┘")
    print()

    # ── 3. Output directory ──
    if _OUTPUT_BASE_OVERRIDE:
        output_base = _OUTPUT_BASE_OVERRIDE
        print(f"  Output directory: {output_base}")
    else:
        output_base = read_line("Output directory", default=".")
    output_dir = os.path.join(output_base, pkg_name)

    # ── 4. Generate files ──
    print("┌─ Generating Plugin ─────────────────────────────────────────┐")
    print()

    os.makedirs(output_dir, exist_ok=True)
    print(f"  Output: {output_dir}/")
    print()

    # index.bsl
    idx_content = generate_index_bsl(pkg_name, author, version, description, commands)
    idx_path = os.path.join(output_dir, "index.bsl")
    with open(idx_path, "w") as f:
        f.write(idx_content)
    print(f"  Created: {idx_path}")
    write_sha256(idx_path)

    # command .bsl files
    for cmd_name, cmd_desc in commands:
        cmd_content = generate_command_bsl(cmd_name, author, version, cmd_desc, pkg_name)
        cmd_path = os.path.join(output_dir, f"{cmd_name}.bsl")
        with open(cmd_path, "w") as f:
            f.write(cmd_content)
        print(f"  Created: {cmd_path}")
        write_sha256(cmd_path)

    # index.json (if repo URL provided)
    if repo_url:
        json_content = generate_index_json(pkg_name, author, version, description,
                                           commands, repo_url)
        json_path = os.path.join(output_dir, "..", "index.json")
        with open(json_path, "w") as f:
            f.write(json_content)
        print(f"  Created: {json_path}")

    print()
    print("└──────────────────────────────────────────────────────────────┘")
    print()

    # ── 5. Summary ──
    print("=" * 60)
    print("  Plugin Created Successfully!")
    print("=" * 60)
    print()
    print(f"  Package:      {pkg_name}")
    print(f"  Author:       {author}")
    print(f"  Version:      {version}")
    print(f"  Description:  {description}")
    print(f"  Commands:     {len(commands)}")
    print(f"  Location:     {os.path.abspath(output_dir)}")
    print()

    if repo_url:
        print("  To install:")
        print(f"    buffy --repo {repo_url}")
        print(f"    buffy --install {pkg_name}")
        print()

    print("  To install locally:")
    print(f"    buffy --install {os.path.abspath(output_dir)}")
    print()

    print("  To test your plugin:")
    print(f"    buffy --check {os.path.abspath(output_dir)}/index.bsl")
    print(f"    buffy --check {os.path.abspath(output_dir)}/{commands[0][0]}.bsl")
    print()

    print("  To use your plugin:")
    print(f"    buffy {pkg_name}")
    print(f"    buffy {pkg_name} {commands[0][0]}")
    print()
    print("=" * 60)


def show_help():
    print("Usage: python .compile.py [--output-dir <dir>]")
    print()
    print("Interactive plugin scaffolder for Buffy.")
    print()
    print("Options:")
    print("  --output-dir <dir>    Output directory (skip interactive prompt)")
    print("  --help                Show this help")
    print()
    print("Interactive prompts for:")
    print("  - Package name, author, version, description")
    print("  - Command names and descriptions")
    print("  - Repository URL (optional)")
    print("  - Output directory")
    print()
    print("Generates:")
    print("  - Plugin directory with index.bsl and command .bsl files")
    print("  - SHA-256 checksum files for every .bsl file")
    print("  - index.json if repository URL provided")
    print()


def main():
    # Parse optional flags
    output_base_override = None
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] in ("--help", "-h"):
            show_help()
            return
        elif sys.argv[i] == "--output-dir":
            if i + 1 < len(sys.argv):
                output_base_override = sys.argv[i + 1]
                i += 2
            else:
                print("Error: --output-dir requires a path argument.")
                sys.exit(1)
        else:
            print(f"Unknown option: {sys.argv[i]}")
            print("Usage: python .compile.py [--output-dir <dir>]")
            sys.exit(1)

    # Store override in a way scaffold() can access
    global _OUTPUT_BASE_OVERRIDE
    _OUTPUT_BASE_OVERRIDE = output_base_override

    try:
        scaffold()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)
    except EOFError:
        print("\nInput ended. Exiting.")
        sys.exit(1)


_OUTPUT_BASE_OVERRIDE = None


if __name__ == "__main__":
    main()
