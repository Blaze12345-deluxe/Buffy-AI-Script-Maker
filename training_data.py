"""
training_data.py - BSL Training Corpus

Provides a corpus of ~50 BSL script examples organized by category.
Each example includes:
  - The BSL source code
  - A natural language description of what it does
  - Tags for categorization
  - Required arguments (if any)
  - The shell commands it depends on

This corpus is used by bsl_generator.py to match user prompts
to the most relevant script patterns and generate new scripts.
"""

import json
from typing import List, Dict, Optional

# ─── Training Examples ───────────────────────────────────────────────────────

TRAINING_EXAMPLES = [
    # ═══════════════════════════════════════════════════════════════════════════
    # ── Section 1: System & Diagnostics
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "system-info",
        "description": "Displays detailed system information including OS, user, memory, and disk usage.",
        "prompt_keywords": ["system", "info", "information", "details", "specs", "specifications"],
        "tags": ["system", "diagnostics", "info"],
        "dependencies": ["uname", "free", "df"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Displays detailed system information."
OUTPUT = false

CLEAR

WRITE "========================================="
WRITE "  System Information"
WRITE "========================================="
WRITE ""

WRITE "  User:       ${USER}"
WRITE "  Home:       ${HOME}"
WRITE "  Directory:  ${PWD}"
WRITE "  Date:       ${DATE}"
WRITE "  Time:       ${TIME}"
WRITE "  Temp:       ${TEMP}"
WRITE ""

WRITE "-----------------------------------------"
WRITE "  Operating System"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "uname -a"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Memory Usage"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "free -h | head -3"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Disk Usage"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "df -h / | tail -1"
OUTPUT = false

WRITE ""
WRITE "========================================="
EXIT"""
    },
    {
        "name": "system-benchmark",
        "description": "Runs basic system benchmarks: CPU, memory, and disk I/O performance tests.",
        "prompt_keywords": ["benchmark", "performance", "speed test", "cpu test", "memory test", "disk test"],
        "tags": ["system", "benchmark", "performance", "diagnostics"],
        "dependencies": ["dd", "sysbench", "uname"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Runs basic system benchmarks for CPU, memory, and disk."
OUTPUT = false

CLEAR

WRITE "========================================="
WRITE "  System Benchmark"
WRITE "========================================="
WRITE ""
WRITE "Date: ${DATE}  Time: ${TIME}"
WRITE ""

WRITE "-----------------------------------------"
WRITE "  CPU Information"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "uname -m && nproc"
OUTPUT = false
WRITE ""

WRITE "-----------------------------------------"
WRITE "  Disk Write Test (1GB)"
WRITE "-----------------------------------------"
WRITE "Writing 1GB test file..."
OUTPUT = true
RUN "dd if=/dev/zero of=/tmp/bsl-benchmark-test bs=1M count=1024 2>&1 | tail -1"
OUTPUT = false
WRITE "Cleaning up..."
RUN "rm -f /tmp/bsl-benchmark-test"

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Memory Info"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "free -h"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Benchmark Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "system-update",
        "description": "Updates system packages using apt: update, upgrade, autoremove.",
        "prompt_keywords": ["update", "upgrade", "apt", "system update", "package update", "debian", "ubuntu"],
        "tags": ["system", "update", "apt", "maintenance"],
        "dependencies": ["sudo", "apt"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Updates system packages using apt."
OUTPUT = true

CLEAR

WRITE "========================================="
WRITE "  System Update"
WRITE "========================================="
WRITE ""

WRITE "Step 1: Updating package lists..."
RUN "sudo apt update"

WRITE ""
WRITE "Step 2: Upgrading packages..."
RUN "sudo apt upgrade -y"

WRITE ""
WRITE "Step 3: Removing unused packages..."
RUN "sudo apt autoremove -y"

WRITE ""
WRITE "========================================="
WRITE "  Update Complete"
WRITE "========================================="
WRITE "System update finished successfully."

EXIT"""
    },
    {
        "name": "process-monitor",
        "description": "Lists top processes by CPU and memory usage with sort options.",
        "prompt_keywords": ["process", "processes", "monitor", "ps", "top", "running", "cpu"],
        "tags": ["system", "monitor", "processes", "diagnostics"],
        "dependencies": ["ps"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Shows top processes by CPU and memory usage."
OUTPUT = false

CLEAR

WRITE "========================================="
WRITE "  Process Monitor"
WRITE "========================================="
WRITE ""
WRITE "Time: ${TIME}  Date: ${DATE}"
WRITE ""

WRITE "-----------------------------------------"
WRITE "  Top 10 Processes by CPU"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "ps aux --sort=-%cpu | head -11"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Top 10 Processes by Memory"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "ps aux --sort=-%mem | head -11"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Process Count"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "echo 'Total processes:'; ps aux | wc -l"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Monitor Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "service-status",
        "description": "Checks the status of common systemd services and shows their active state.",
        "prompt_keywords": ["service", "services", "systemd", "status", "running services", "daemon"],
        "tags": ["system", "systemd", "services", "diagnostics"],
        "dependencies": ["systemctl"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Checks status of common systemd services."
OUTPUT = false

WRITE "========================================="
WRITE "  Systemd Service Status"
WRITE "========================================="
WRITE ""

WRITE "Checking common services..."
RUN "test -x /bin/systemctl || test -x /usr/bin/systemctl || echo 'systemctl not available'"

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Service: sshd"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "systemctl is-active sshd 2>/dev/null && echo 'sshd: active' || echo 'sshd: inactive/not found'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Service: docker"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "systemctl is-active docker 2>/dev/null && echo 'docker: active' || echo 'docker: inactive/not found'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Service: nginx"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "systemctl is-active nginx 2>/dev/null && echo 'nginx: active' || echo 'nginx: inactive/not found'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  All Running Services"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "systemctl list-units --type=service --state=running 2>/dev/null | head -20"
OUTPUT = false

WRITE ""
WRITE "========================================="
EXIT"""
    },
    {
        "name": "disk-usage",
        "description": "Shows disk usage report: largest subdirectories, largest files, and overall summary.",
        "prompt_keywords": ["disk", "usage", "space", "storage", "du", "disk usage", "size"],
        "tags": ["system", "disk", "storage", "report"],
        "dependencies": ["du", "find"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Shows disk usage for the current directory."
OUTPUT = false

CLEAR

WRITE "========================================="
WRITE "  Disk Usage Report"
WRITE "========================================="
WRITE ""

WRITE "Directory: ${PWD}"
WRITE ""
WRITE "-----------------------------------------"
WRITE "  Top 10 Largest Subdirectories"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "du -sh */ 2>/dev/null | sort -rh | head -10"

OUTPUT = false
WRITE ""
WRITE "-----------------------------------------"
WRITE "  Top 10 Largest Files"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "find . -maxdepth 2 -type f -exec du -sh '{}' ';' 2>/dev/null | sort -rh | head -10"

OUTPUT = false
WRITE ""
WRITE "-----------------------------------------"
WRITE "  Summary"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "du -sh ."
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Report Complete"
WRITE "========================================="

EXIT"""
    },
    # ═══════════════════════════════════════════════════════════════════════════
    # ── Section 2: File Operations
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "file-organizer",
        "description": "Organizes files in a directory by moving them into subdirectories based on file extension.",
        "prompt_keywords": ["organize", "organizer", "sort files", "arrange", "organize files", "clean"],
        "tags": ["files", "organize", "utility"],
        "dependencies": ["mkdir", "mv"],
        "args": ["target_directory"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Organizes files by extension into category folders."
OUTPUT = false

WRITE "========================================="
WRITE "  File Organizer"
WRITE "========================================="
WRITE ""

WRITE "Target: ${1:-.}"
WRITE ""

RUN "test -d '${1:-.}' && echo 'Directory exists' || echo 'Warning: directory not found'"

WRITE "Creating category folders..."
RUN "mkdir -p '${1:-.}'/Images '${1:-.}'/Documents '${1:-.}'/Archives '${1:-.}'/Code '${1:-.}'/Other"

WRITE ""
WRITE "Moving images (jpg, png, gif)..."
RUN "mv '${1:-.}'/*.jpg '${1:-.}'/Images/ 2>/dev/null || echo '  No jpg files'"
RUN "mv '${1:-.}'/*.png '${1:-.}'/Images/ 2>/dev/null || echo '  No png files'"
RUN "mv '${1:-.}'/*.gif '${1:-.}'/Images/ 2>/dev/null || echo '  No gif files'"

WRITE "Moving documents (pdf, doc, txt)..."
RUN "mv '${1:-.}'/*.pdf '${1:-.}'/Documents/ 2>/dev/null || echo '  No pdf files'"
RUN "mv '${1:-.}'/*.doc* '${1:-.}'/Documents/ 2>/dev/null || echo '  No doc files'"
RUN "mv '${1:-.}'/*.txt '${1:-.}'/Documents/ 2>/dev/null || echo '  No txt files'"

WRITE "Moving archives (zip, tar, gz)..."
RUN "mv '${1:-.}'/*.zip '${1:-.}'/Archives/ 2>/dev/null || echo '  No zip files'"
RUN "mv '${1:-.}'/*.tar* '${1:-.}'/Archives/ 2>/dev/null || echo '  No tar files'"
RUN "mv '${1:-.}'/*.gz '${1:-.}'/Archives/ 2>/dev/null || echo '  No gz files'"

WRITE "Moving code files (py, js, rs)..."
RUN "mv '${1:-.}'/*.py '${1:-.}'/Code/ 2>/dev/null || echo '  No py files'"
RUN "mv '${1:-.}'/*.js '${1:-.}'/Code/ 2>/dev/null || echo '  No js files'"
RUN "mv '${1:-.}'/*.rs '${1:-.}'/Code/ 2>/dev/null || echo '  No rs files'"
RUN "mv '${1:-.}'/*.ts '${1:-.}'/Code/ 2>/dev/null || echo '  No ts files'"

WRITE ""
WRITE "========================================="
WRITE "  Organization Complete"
WRITE "========================================="
OUTPUT = true
RUN "ls -la '${1:-.}'/"
OUTPUT = false

EXIT"""
    },
    {
        "name": "duplicate-finder",
        "description": "Finds duplicate files in a directory using md5sum checksums.",
        "prompt_keywords": ["duplicate", "duplicates", "duplicate files", "find duplicates", "dedup", "identical"],
        "tags": ["files", "search", "duplicate", "utility"],
        "dependencies": ["md5sum", "find", "sort", "uniq"],
        "args": ["search_directory"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Finds duplicate files in a directory using checksums."
OUTPUT = false

WRITE "========================================="
WRITE "  Duplicate File Finder"
WRITE "========================================="
WRITE ""

WRITE "Searching: ${1:-.}"
WRITE ""
WRITE "Computing checksums... (this may take a while)"
WRITE ""

RUN "find '${1:-.}' -type f -exec md5sum '{}' ';' 2>/dev/null > /tmp/bsl-dups.txt"
RUN "sort /tmp/bsl-dups.txt > /tmp/bsl-dups-sorted.txt"
RUN "cut -d' ' -f1 /tmp/bsl-dups-sorted.txt | uniq -d > /tmp/bsl-dups-ids.txt"

OUTPUT = true
WRITE "Duplicate files found:"
RUN "wc -l < /tmp/bsl-dups-ids.txt || echo 0"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Duplicates"
WRITE "-----------------------------------------"
OUTPUT = true

RUN "while read hash; do echo 'Hash: $hash'; grep \"$hash\" /tmp/bsl-dups-sorted.txt | cut -d' ' -f2-; echo ''; done < /tmp/bsl-dups-ids.txt | head -50 || echo 'No duplicates found'"

OUTPUT = false
WRITE ""

RUN "rm -f /tmp/bsl-dups.txt /tmp/bsl-dups-sorted.txt /tmp/bsl-dups-ids.txt"

WRITE "========================================="
WRITE "  Scan Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "bulk-rename",
        "description": "Renames multiple files by replacing a pattern with new text in their filenames.",
        "prompt_keywords": ["rename", "bulk rename", "rename files", "mass rename", "batch rename"],
        "tags": ["files", "rename", "utility"],
        "dependencies": ["mv"],
        "args": ["pattern", "replacement", "target_directory"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Bulk renames files by replacing a pattern in their names."
OUTPUT = false

WRITE "========================================="
WRITE "  Bulk File Renamer"
WRITE "========================================="
WRITE ""

WRITE "Pattern:    ${1}"
WRITE "Replace:    ${2}"
WRITE "Directory:  ${3:-.}"
WRITE ""

RUN "test -d '${3:-.}' && echo 'Directory exists' || echo 'Warning: directory not found'"

WRITE ""
WRITE "Preview of changes:"
OUTPUT = true
RUN "for f in '${3:-.}'/*${1}*; do [ -f \"$f\" ] && echo \"$(basename \"$f\") -> $(basename \"$f\" | sed 's/${1}/${2}/g')\"; done"
OUTPUT = false

WRITE ""
WRITE "Proceeding with rename..."
OUTPUT = true
RUN "for f in '${3:-.}'/*${1}*; do [ -f \"$f\" ] && mv \"$f\" \"$(echo \"$f\" | sed 's/${1}/${2}/g')\" 2>/dev/null && echo \"Renamed: $(basename \"$f\")\" || echo \"Skipped: $(basename \"$f\")\"; done"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Rename Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "directory-tree",
        "description": "Displays a visual directory tree structure using the tree command or fallback find method.",
        "prompt_keywords": ["tree", "directory tree", "folder structure", "ls tree", "show structure"],
        "tags": ["files", "tree", "utility"],
        "dependencies": ["tree", "find"],
        "args": ["target_directory"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Shows a visual directory tree structure."
OUTPUT = false

WRITE "========================================="
WRITE "  Directory Tree"
WRITE "========================================="
WRITE ""

WRITE "Directory: ${1:-.}"
WRITE ""

OUTPUT = true

RUN "tree '${1:-.}' 2>/dev/null || find '${1:-.}' -print 2>/dev/null | sed -e 's;[^/]*/;|___;g;s;___|; |;g' | head -50"

OUTPUT = false

WRITE ""
WRITE "========================================="

EXIT"""
    },
    {
        "name": "file-permissions-fix",
        "description": "Fixes file permissions: directories to 755, files to 644, and scripts to 755.",
        "prompt_keywords": ["permissions", "chmod", "fix permissions", "chmod fix", "file permissions", "mode"],
        "tags": ["files", "permissions", "utility", "security"],
        "dependencies": ["chmod", "find"],
        "args": ["target_directory"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Fixes file permissions: dirs 755, files 644, scripts 755."
OUTPUT = false

WRITE "========================================="
WRITE "  File Permissions Fixer"
WRITE "========================================="
WRITE ""

WRITE "Target: ${1:-.}"
WRITE ""

RUN "test -d '${1:-.}' && echo 'Directory exists' || echo 'Warning: directory not found'"

WRITE ""
WRITE "Setting directories to 755..."
OUTPUT = true
RUN "find '${1:-.}' -type d -exec chmod 755 '{}' '+' 2>/dev/null && echo 'Done'"
OUTPUT = false

WRITE ""
WRITE "Setting regular files to 644..."
OUTPUT = true
RUN "find '${1:-.}' -type f ! -name '*.sh' ! -name '*.py' ! -name '*.pl' ! -name '*.rb' -exec chmod 644 '{}' '+' 2>/dev/null && echo 'Done'"
OUTPUT = false

WRITE ""
WRITE "Setting script files to 755..."
OUTPUT = true
RUN "find '${1:-.}' -type f \\( -name '*.sh' -o -name '*.py' -o -name '*.pl' -o -name '*.rb' \\) -exec chmod 755 '{}' '+' 2>/dev/null && echo 'Done'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Permissions Fixed"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "backup-directory",
        "description": "Backs up a directory to a compressed tar.gz archive.",
        "prompt_keywords": ["backup", "archive", "compress", "tar", "back up", "save"],
        "tags": ["backup", "archive", "files"],
        "dependencies": ["tar"],
        "args": ["source_directory", "destination_file"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Backs up a directory to a compressed archive."
OUTPUT = false

WRITE "========================================="
WRITE "  Directory Backup"
WRITE "========================================="
WRITE ""

WRITE "Source:      ${1}"
WRITE "Destination: ${2}"
WRITE ""

RUN "test -d '${1}' && echo 'Source exists' || echo 'WARNING: Source does not exist'"

OUTPUT = true
RUN "tar -czf '${2}' '${1}'"
OUTPUT = false

WRITE ""
WRITE "Backup created!"
RUN "ls -lh '${2}'"
WRITE ""
WRITE "To restore: tar -xzf '${2}'"

EXIT"""
    },
    {
        "name": "file-encrypt",
        "description": "Encrypts or decrypts a file using OpenSSL AES-256-CBC with a password prompt.",
        "prompt_keywords": ["encrypt", "decrypt", "openssl", "aes", "cipher", "secure file", "protection"],
        "tags": ["files", "security", "encrypt", "utility"],
        "dependencies": ["openssl"],
        "args": ["input_file", "action"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Encrypts or decrypts a file using OpenSSL AES-256."
OUTPUT = false

WRITE "========================================="
WRITE "  File Encrypt / Decrypt"
WRITE "========================================="
WRITE ""

WRITE "File:   ${1}"
WRITE "Action: ${2:-encrypt}"
WRITE ""

RUN "test -f '${1}' && echo 'File exists' || echo 'Error: File not found'"

WRITE ""
WRITE "Processing..."

OUTPUT = true
RUN "if [ '${2:-encrypt}' = 'decrypt' ]; then openssl enc -aes-256-cbc -d -in '${1}' -out '${1%.enc}' -pbkdf2 2>&1; else openssl enc -aes-256-cbc -salt -in '${1}' -out '${1}.enc' -pbkdf2 2>&1; fi"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Operation Complete"
WRITE "========================================="

EXIT"""
    },
    # ═══════════════════════════════════════════════════════════════════════════
    # ── Section 3: Development
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "pip-env",
        "description": "Creates a Python virtual environment, upgrades pip, and sets up .gitignore.",
        "prompt_keywords": ["python", "venv", "virtual", "environment", "pip", "python env"],
        "tags": ["python", "development", "setup"],
        "dependencies": ["python3"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Creates a Python virtual environment in the current directory."
OUTPUT = false

WRITE "Creating Python virtual environment..."
RUN "python3 -m venv .venv"

WRITE "Virtual environment created."
WRITE "Upgrading pip..."
RUN ".venv/bin/python -m pip install --upgrade pip"

WRITE "Creating requirements.txt (if missing)..."
RUN "test -f requirements.txt || touch requirements.txt"

WRITE "Adding .venv to .gitignore (if missing)..."
RUN "test -f .gitignore || touch .gitignore"
RUN "grep -qxF .venv/ .gitignore || echo .venv/ >> .gitignore"

WRITE ""
WRITE "Setup Complete!"
WRITE ""
WRITE "To activate: source .venv/bin/activate"
WRITE ""

EXIT"""
    },
    {
        "name": "project-setup",
        "description": "Scaffolds a new project directory with src, tests, docs folders, README, .gitignore, Makefile, and LICENSE.",
        "prompt_keywords": ["project", "scaffold", "create project", "new project", "init", "template"],
        "tags": ["development", "scaffolding", "setup"],
        "dependencies": ["mkdir", "echo"],
        "args": ["project_name"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Scaffolds a new project with directory structure."
OUTPUT = false

WRITE "Creating project: ${1}"
WRITE ""

RUN "mkdir -p ${1}/src ${1}/tests ${1}/docs"

WRITE "Creating README.md..."
RUN "echo '# ${1}' > ${1}/README.md"
RUN "echo '## Description' >> ${1}/README.md"
RUN "echo '## Installation' >> ${1}/README.md"
RUN "echo '## Usage' >> ${1}/README.md"

WRITE "Creating .gitignore..."
RUN "echo '.venv/' > ${1}/.gitignore"
RUN "echo '__pycache__/' >> ${1}/.gitignore"
RUN "echo '*.pyc' >> ${1}/.gitignore"
RUN "echo '.env' >> ${1}/.gitignore"
RUN "echo 'target/' >> ${1}/.gitignore"
RUN "echo 'dist/' >> ${1}/.gitignore"

WRITE "Creating Makefile..."
RUN "echo 'all: test' > ${1}/Makefile"
RUN "echo '' >> ${1}/Makefile"
RUN "echo 'test:' >> ${1}/Makefile"
RUN "echo '\t@echo Running tests...' >> ${1}/Makefile"

WRITE "Creating LICENSE..."
RUN "echo 'MIT License' > ${1}/LICENSE"
RUN "echo 'Copyright (c) ${DATE}' >> ${1}/LICENSE"

WRITE ""
WRITE "========================================="
WRITE "  Project '${1}' Created!"
WRITE "========================================="
WRITE "  Location: ${PWD}/${1}"
WRITE ""
WRITE "  cd ${1} && git init"
WRITE ""

EXIT"""
    },
    {
        "name": "git-quick-setup",
        "description": "Initializes a Git repository, creates a .gitignore, and makes the first commit.",
        "prompt_keywords": ["git", "repository", "init", "git init", "version control", "commit"],
        "tags": ["git", "version control", "setup"],
        "dependencies": ["git"],
        "args": ["project_name"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Initializes a Git repository with standard setup."
OUTPUT = false

RUN "git --version"
RUN "test -d .git && echo 'already a repo' || echo 'not a repo'"

WRITE ""
WRITE "Initializing Git repository..."
WRITE ""
RUN "git init"

WRITE "Creating .gitignore..."
RUN "test -f .gitignore && echo 'exists' || echo '.venv/' >> .gitignore"
RUN "echo '__pycache__/' >> .gitignore"
RUN "echo '*.pyc' >> .gitignore"
RUN "echo '.env' >> .gitignore"
RUN "echo 'node_modules/' >> .gitignore"
RUN "echo 'target/' >> .gitignore"
RUN "echo 'dist/' >> .gitignore"
RUN "echo '.DS_Store' >> .gitignore"

WRITE ""
WRITE "Creating initial commit..."
RUN "git add .gitignore"
RUN "git commit -m 'Initial commit: add .gitignore'"

WRITE ""
WRITE "========================================="
WRITE "  Git Repository Ready!"
WRITE "========================================="
WRITE "  Next steps:"
WRITE "    git add ."
WRITE "    git commit -m 'Add project files'"
WRITE "    git remote add origin <url>"
WRITE "    git push -u origin main"
WRITE ""

EXIT"""
    },
    {
        "name": "git-branch-cleanup",
        "description": "Deletes local Git branches that have been merged into the current branch.",
        "prompt_keywords": ["git branch", "branches", "cleanup", "delete branches", "merged branches", "git cleanup"],
        "tags": ["git", "cleanup", "development", "maintenance"],
        "dependencies": ["git"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Deletes local Git branches that have been merged."
OUTPUT = false

WRITE "========================================="
WRITE "  Git Branch Cleanup"
WRITE "========================================="
WRITE ""

WRITE "Current branch:"
OUTPUT = true
RUN "git branch --show-current"
OUTPUT = false
WRITE ""

WRITE "Merged branches (safe to delete):"
OUTPUT = true
RUN "git branch --merged | grep -v '\\*' | grep -v 'main' | grep -v 'master' || echo 'No merged branches to clean'"
OUTPUT = false

WRITE ""
WRITE "Deleting merged branches (except main/master)..."
OUTPUT = true
RUN "git branch --merged | grep -v '\\*' | grep -v 'main' | grep -v 'master' | xargs -r git branch -d 2>&1 || echo 'Nothing to delete'"
OUTPUT = false

WRITE ""
WRITE "Remaining branches:"
OUTPUT = true
RUN "git branch"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Cleanup Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "git-log-report",
        "description": "Shows a formatted Git log with author, date, and commit message for the last 20 commits.",
        "prompt_keywords": ["git log", "history", "commits", "git history", "changelog", "git report"],
        "tags": ["git", "report", "development"],
        "dependencies": ["git"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Shows a formatted Git log of recent commits."
OUTPUT = false

CLEAR

WRITE "========================================="
WRITE "  Git Log Report"
WRITE "========================================="
WRITE ""

RUN "test -d .git || echo 'Warning: Not a git repository'"

WRITE "Recent commits:"
WRITE ""

OUTPUT = true
RUN "git log --oneline -20 2>/dev/null || echo 'No commits found'"

OUTPUT = false
WRITE ""
WRITE "-----------------------------------------"
WRITE "  Detailed Log"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "git log --pretty=format:'%h | %an | %ar | %s' -20 2>/dev/null"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Statistics"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "echo 'Total commits:' && git rev-list --count HEAD 2>/dev/null || echo 0"
RUN "echo 'Contributors:' && git shortlog -sn 2>/dev/null | wc -l || echo 0"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Report Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "cargo-clean",
        "description": "Recursively finds and cleans Rust target directories to free up disk space.",
        "prompt_keywords": ["cargo", "rust", "clean", "target", "disk space", "cargo clean"],
        "tags": ["development", "rust", "cleanup", "maintenance"],
        "dependencies": ["cargo", "find", "du"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Recursively finds and cleans Rust target directories."
OUTPUT = false

WRITE "========================================="
WRITE "  Cargo Target Cleanup"
WRITE "========================================="
WRITE ""

WRITE "Searching for Rust target directories..."
OUTPUT = true
RUN "find . -maxdepth 4 -type d -name 'target' -not -path '*/target/debug' -not -path '*/target/release' 2>/dev/null | head -10"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Current Project"
WRITE "-----------------------------------------"
WRITE "Checking if cargo project exists at ${PWD}..."
OUTPUT = true
RUN "test -f Cargo.toml && echo 'Cargo project found' || echo 'Not a cargo project root'"
OUTPUT = false

WRITE ""
WRITE "Cleaning this project..."
OUTPUT = true
RUN "cargo clean 2>/dev/null && echo 'Cleaned' || echo 'No target to clean'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Subproject Target Directories"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "for dir in $(find . -maxdepth 3 -type d -name 'target' 2>/dev/null); do size=$(du -sh \"$dir\" 2>/dev/null | cut -f1); echo \"Removing $dir ($size)\"; rm -rf \"$dir\" 2>/dev/null; done || echo 'No subproject targets'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Cleanup Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "docker-compose-up",
        "description": "Builds and starts Docker Compose services with logs and status monitoring.",
        "prompt_keywords": ["docker compose", "docker-compose", "compose", "containers", "docker up"],
        "tags": ["docker", "development", "compose", "setup"],
        "dependencies": ["docker", "docker-compose"],
        "args": ["service_name"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Builds and starts Docker Compose services with status monitoring."
OUTPUT = false

WRITE "========================================="
WRITE "  Docker Compose Manager"
WRITE "========================================="
WRITE ""

WRITE "Service: ${1:-all}"
WRITE ""

RUN "test -f docker-compose.yml || test -f docker-compose.yaml || echo 'Warning: docker-compose.yml not found'"

WRITE ""
WRITE "Checking Docker status..."
OUTPUT = true
RUN "docker info > /dev/null 2>&1 && echo 'Docker is running' || echo 'Docker is not running'"
OUTPUT = false

WRITE ""
WRITE "Building services..."
OUTPUT = true
RUN "docker-compose build ${1} 2>&1 || echo 'Build completed or skipped'"
OUTPUT = false

WRITE ""
WRITE "Starting services..."
OUTPUT = true
RUN "docker-compose up -d ${1} 2>&1"
OUTPUT = false

WRITE ""
WRITE "Service status:"
OUTPUT = true
RUN "docker-compose ps ${1} 2>/dev/null"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Services Running"
WRITE "========================================="
WRITE "  To view logs:  docker-compose logs -f ${1}"
WRITE "  To stop:       docker-compose down"
WRITE ""

EXIT"""
    },
    # ═══════════════════════════════════════════════════════════════════════════
    # ── Section 4: Network
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "network-diagnostic",
        "description": "Runs network diagnostics: DNS lookup, ping test, traceroute, and HTTP connection test.",
        "prompt_keywords": ["network", "diagnostic", "ping", "dns", "traceroute", "connectivity", "net"],
        "tags": ["network", "diagnostics", "troubleshooting"],
        "dependencies": ["ping", "nslookup", "traceroute", "curl"],
        "args": ["hostname_or_ip"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Runs network diagnostics: ping and traceroute."
OUTPUT = false

WRITE "Network Diagnostic Tool"
WRITE ""
WRITE "Target: ${1}"
WRITE ""

WRITE "========================================="
WRITE "  Step 1: DNS Resolution"
WRITE "========================================="
OUTPUT = true
RUN "nslookup ${1} 2>/dev/null || host ${1} 2>/dev/null || echo 'DNS lookup tools not available'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Step 2: Ping Test"
WRITE "========================================="
OUTPUT = true
RUN "ping -c 4 ${1} 2>/dev/null || echo 'Ping failed'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Step 3: Traceroute"
WRITE "========================================="
OUTPUT = true
RUN "traceroute ${1} 2>/dev/null || echo 'Traceroute not available'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Step 4: Connection Test"
WRITE "========================================="
OUTPUT = true
RUN "curl -sI https://${1} 2>/dev/null | head -5 || echo 'Connection check failed'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Diagnostic Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "port-scan",
        "description": "Scans common ports on a remote host to check which services are accessible.",
        "prompt_keywords": ["port", "scan", "ports", "port scan", "network scan", "open ports", "nmap"],
        "tags": ["network", "security", "scan", "diagnostics"],
        "dependencies": ["nc", "curl"],
        "args": ["hostname"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Scans common ports on a host to check which are open."
OUTPUT = false

WRITE "========================================="
WRITE "  Port Scanner"
WRITE "========================================="
WRITE ""

WRITE "Target: ${1}"
WRITE ""

WRITE "Scanning common ports..."
WRITE ""

OUTPUT = true
RUN "for port in 22 80 443 3306 5432 6379 8080 8443 27017; do nc -zv -w2 '${1}' $port 2>&1 | grep -E 'succeeded|open' && echo \"Port $port: OPEN\" || true; done | head -20"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  HTTP Service Check"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "curl -sI --connect-timeout 3 http://${1}:8080 2>/dev/null | head -1 && echo 'Port 8080: HTTP responding' || true"
RUN "curl -sI --connect-timeout 3 https://${1}:8443 2>/dev/null | head -1 && echo 'Port 8443: HTTPS responding' || true"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Scan Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "wifi-info",
        "description": "Shows current WiFi connection details: SSID, signal strength, and interface info.",
        "prompt_keywords": ["wifi", "wireless", "network", "signal", "ssid", "connection", "wireless info"],
        "tags": ["network", "wifi", "diagnostics", "info"],
        "dependencies": ["iwconfig", "iwgetid", "ip"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Shows current WiFi connection details and signal strength."
OUTPUT = false

CLEAR

WRITE "========================================="
WRITE "  WiFi Information"
WRITE "========================================="
WRITE ""

WRITE "-----------------------------------------"
WRITE "  Connection Details"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "iwgetid 2>/dev/null || echo 'WiFi: not available'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Signal Strength"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "iwconfig 2>/dev/null | grep -E 'ESSID|Signal|Quality' | head -5 || echo 'iwconfig not available'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Network Interfaces"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "ip addr show 2>/dev/null | grep -E '^[0-9]|inet ' | head -10 || ifconfig 2>/dev/null | head -10"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Default Route"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "ip route 2>/dev/null | grep default || route -n 2>/dev/null | grep '^0.0.0.0'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Report Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "firewall-check",
        "description": "Displays current firewall rules using iptables or ufw status.",
        "prompt_keywords": ["firewall", "iptables", "ufw", "rules", "netfilter", "security"],
        "tags": ["network", "security", "firewall", "diagnostics"],
        "dependencies": ["iptables", "ufw"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Displays current firewall rules and status."
OUTPUT = false

WRITE "========================================="
WRITE "  Firewall Status Check"
WRITE "========================================="
WRITE ""

WRITE "Checking UFW (Uncomplicated Firewall)..."
OUTPUT = true
RUN "ufw status 2>/dev/null || echo 'UFW not available'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  IPTables Filter Rules"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "iptables -L -n --line-numbers 2>/dev/null | head -30 || echo 'iptables not available (try with sudo)'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  IPTables NAT Rules"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "iptables -t nat -L -n 2>/dev/null | head -15 || echo 'NAT rules not available'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Check Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "ssl-cert-check",
        "description": "Checks SSL certificate details and expiry date for a given domain.",
        "prompt_keywords": ["ssl", "certificate", "cert", "tls", "expiry", "https", "domain check"],
        "tags": ["network", "security", "ssl", "diagnostics"],
        "dependencies": ["openssl", "curl"],
        "args": ["domain"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Checks SSL certificate details and expiry date."
OUTPUT = false

WRITE "========================================="
WRITE "  SSL Certificate Check"
WRITE "========================================="
WRITE ""

WRITE "Domain: ${1}"
WRITE ""

OUTPUT = true
RUN "echo 'Certificate details:' && openssl s_client -connect '${1}':443 -servername '${1}' </dev/null 2>/dev/null | openssl x509 -noout -dates -subject -issuer 2>/dev/null || echo 'Could not retrieve certificate (check domain or connectivity)'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Additional Checks"
WRITE "-----------------------------------------"
WRITE "HTTP status check..."
OUTPUT = true
RUN "curl -sI --connect-timeout 5 https://${1} 2>/dev/null | head -5 || echo 'HTTP check failed'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Check Complete"
WRITE "========================================="

EXIT"""
    },
    # ═══════════════════════════════════════════════════════════════════════════
    # ── Section 5: Docker & Containers
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "docker-cleanup",
        "description": "Cleans up unused Docker resources: stopped containers, unused images, volumes, and build cache.",
        "prompt_keywords": ["docker", "clean", "cleanup", "docker clean", "prune", "containers"],
        "tags": ["docker", "containers", "cleanup", "maintenance"],
        "dependencies": ["docker"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Cleans up unused Docker resources."
OUTPUT = false

WRITE "========================================="
WRITE "  Docker Cleanup"
WRITE "========================================="
WRITE ""

WRITE "Step 1: Checking Docker is running..."
RUN "docker info > /dev/null 2>&1 && echo 'Docker is running' || echo 'Docker is not running'"

WRITE ""
WRITE "Step 2: Stopping all running containers..."
OUTPUT = true
RUN "docker stop $(docker ps -q) 2>/dev/null || echo 'No running containers'"
OUTPUT = false

WRITE ""
WRITE "Step 3: Removing unused containers..."
OUTPUT = true
RUN "docker container prune -f"
OUTPUT = false

WRITE ""
WRITE "Step 4: Removing unused images..."
OUTPUT = true
RUN "docker image prune -af"
OUTPUT = false

WRITE ""
WRITE "Step 5: Removing unused volumes..."
OUTPUT = true
RUN "docker volume prune -f"
OUTPUT = false

WRITE ""
WRITE "Step 6: Removing build cache..."
OUTPUT = true
RUN "docker builder prune -af"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Docker Cleanup Complete!"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "docker-logs",
        "description": "Tails logs from a Docker container with timestamps and line count options.",
        "prompt_keywords": ["docker logs", "container logs", "logs", "docker log", "tail", "container"],
        "tags": ["docker", "containers", "logs", "troubleshooting"],
        "dependencies": ["docker"],
        "args": ["container_name", "lines"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Shows recent logs from a Docker container."
OUTPUT = false

WRITE "========================================="
WRITE "  Docker Log Viewer"
WRITE "========================================="
WRITE ""

WRITE "Container: ${1}"
WRITE "Lines:     ${2:-50}"
WRITE ""

RUN "docker ps 2>/dev/null | grep '${1}' || echo 'Warning: Container may not be running'"

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Recent Logs"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "docker logs --tail '${2:-50}' --timestamps '${1}' 2>&1"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  End of Logs"
WRITE "========================================="
WRITE "To follow: docker logs -f ${1}"

EXIT"""
    },
    {
        "name": "docker-stats",
        "description": "Shows live resource usage statistics for running Docker containers.",
        "prompt_keywords": ["docker stats", "container stats", "resource usage", "cpu", "memory", "docker monitor"],
        "tags": ["docker", "containers", "monitor", "performance"],
        "dependencies": ["docker"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Shows resource usage statistics for running containers."
OUTPUT = false

WRITE "========================================="
WRITE "  Docker Container Stats"
WRITE "========================================="
WRITE ""

RUN "docker info > /dev/null 2>&1 && echo 'Docker is running' || echo 'Docker is not running'"

WRITE ""
WRITE "Running containers:"
OUTPUT = true
RUN "docker ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Image}}' 2>/dev/null"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Resource Usage (one-time snapshot)"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "docker stats --no-stream --format 'table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}\\t{{.NetIO}}\\t{{.BlockIO}}' 2>/dev/null || echo 'No running containers to monitor'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Stats Collected"
WRITE "========================================="
WRITE "For live monitoring: docker stats"

EXIT"""
    },
    {
        "name": "docker-image-list",
        "description": "Lists Docker images with size, tag, and age. Optionally removes dangling images.",
        "prompt_keywords": ["docker images", "images", "docker image", "list images", "image list"],
        "tags": ["docker", "containers", "images", "utility"],
        "dependencies": ["docker"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Lists all Docker images with size and creation date."
OUTPUT = false

WRITE "========================================="
WRITE "  Docker Image Manager"
WRITE "========================================="
WRITE ""

RUN "docker info > /dev/null 2>&1 && echo 'Docker is running' || echo 'Docker is not running'"

WRITE ""
WRITE "-----------------------------------------"
WRITE "  All Images"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "docker images 2>/dev/null || echo 'No images found'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Dangling Images"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "docker images -f dangling=true 2>/dev/null | head -10"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Image Summary"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "echo -n 'Total images: ' && docker images -q 2>/dev/null | wc -l"
RUN "echo -n 'Total size: ' && docker system df 2>/dev/null | grep Images || echo 'N/A'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  List Complete"
WRITE "========================================="

EXIT"""
    },
    # ═══════════════════════════════════════════════════════════════════════════
    # ── Section 6: Backup & Sync
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "rsync-backup",
        "description": "Backs up a directory to a remote host using rsync over SSH with compression and progress.",
        "prompt_keywords": ["rsync", "sync", "remote sync", "backup", "rsync backup", "ssh backup"],
        "tags": ["backup", "sync", "network"],
        "dependencies": ["rsync"],
        "args": ["source_path", "destination_path"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Backs up a directory using rsync with compression."
OUTPUT = false

WRITE "========================================="
WRITE "  Rsync Backup"
WRITE "========================================="
WRITE ""

WRITE "Source:      ${1}"
WRITE "Destination: ${2}"
WRITE ""

RUN "test -d '${1}' && echo 'Source exists' || echo 'Error: Source not found'"
RUN "test -d '${2}' && echo 'Destination exists' || echo 'Warning: Creating destination...'"

WRITE ""
WRITE "Running rsync..."
WRITE ""

OUTPUT = true
RUN "rsync -avz --progress --delete '${1}' '${2}' 2>&1 | tail -5"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Backup Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "gpg-encrypt-file",
        "description": "Encrypts a file with GPG symmetric encryption and sets appropriate permissions.",
        "prompt_keywords": ["gpg", "encrypt", "gnupg", "symmetric", "password protect", "cipher"],
        "tags": ["security", "encrypt", "gpg", "files"],
        "dependencies": ["gpg"],
        "args": ["input_file"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Encrypts a file using GPG symmetric encryption."
OUTPUT = false

WRITE "========================================="
WRITE "  GPG File Encryption"
WRITE "========================================="
WRITE ""

WRITE "File: ${1}"
WRITE ""

RUN "test -f '${1}' && echo 'File exists' || echo 'Error: File not found'"

WRITE ""
WRITE "Encrypting with GPG (symmetric)..."
OUTPUT = true
RUN "gpg --symmetric --cipher-algo AES256 --output '${1}.gpg' '${1}' 2>&1"
OUTPUT = false

WRITE ""
WRITE "Removing original file after encryption..."
WRITE "If you want to keep the original, press Ctrl+C now."
WAIT 3
RUN "rm '${1}' && echo 'Original removed' || echo 'Could not remove original'"

WRITE ""
WRITE "========================================="
WRITE "  Encryption Complete"
WRITE "========================================="
RUN "ls -lh '${1}.gpg'"
WRITE ""
WRITE "To decrypt: gpg --decrypt ${1}.gpg"

EXIT"""
    },
    {
        "name": "system-restore-point",
        "description": "Creates a system restore snapshot by backing up critical configuration files.",
        "prompt_keywords": ["restore", "snapshot", "system restore", "backup config", "preserve", "recovery"],
        "tags": ["backup", "system", "maintenance"],
        "dependencies": ["tar", "mkdir"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Creates a restore point by backing up critical system configs."
OUTPUT = false

WRITE "========================================="
WRITE "  System Restore Point"
WRITE "========================================="
WRITE ""

RESTORE_DIR="${HOME}/restore-points/restore-${DATE}"
RUN "mkdir -p '${RESTORE_DIR}'"

WRITE "Creating restore point at: ${RESTORE_DIR}"
WRITE ""

WRITE "Backing up shell configs..."
RUN "cp -r '${HOME}/.bashrc' '${RESTORE_DIR}/' 2>/dev/null || echo 'No .bashrc found'"
RUN "cp -r '${HOME}/.zshrc' '${RESTORE_DIR}/' 2>/dev/null || echo 'No .zshrc found'"
RUN "cp -r '${HOME}/.config' '${RESTORE_DIR}/config-backup' 2>/dev/null || echo 'No .config found'"

WRITE ""
WRITE "Backing up SSH config..."
RUN "cp -r '${HOME}/.ssh' '${RESTORE_DIR}/ssh-backup' 2>/dev/null || echo 'No .ssh found'"

WRITE ""
WRITE "Creating compressed archive..."
OUTPUT = true
RUN "cd '${HOME}/restore-points' && tar -czf 'restore-${DATE}.tar.gz' 'restore-${DATE}' && rm -rf 'restore-${DATE}'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Restore Point Created"
WRITE "========================================="
RUN "ls -lh '${HOME}/restore-points/restore-${DATE}.tar.gz'"
WRITE ""

EXIT"""
    },
    # ═══════════════════════════════════════════════════════════════════════════
    # ── Section 7: Security & Auditing
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "ssh-key-generate",
        "description": "Generates an SSH key pair (Ed25519) with configurable comment and output path.",
        "prompt_keywords": ["ssh", "key", "ssh key", "generate key", "ssh-keygen", "authentication"],
        "tags": ["security", "ssh", "setup"],
        "dependencies": ["ssh-keygen"],
        "args": ["key_name"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Generates an Ed25519 SSH key pair."
OUTPUT = false

WRITE "========================================="
WRITE "  SSH Key Generator"
WRITE "========================================="
WRITE ""

KEY_PATH="${HOME}/.ssh/${1:-id_ed25519}"
WRITE "Key path: ${KEY_PATH}"
WRITE ""

RUN "test -f '${KEY_PATH}' && echo 'Warning: Key already exists!' || echo 'No existing key found'"

WRITE ""
WRITE "Generating Ed25519 key pair..."
OUTPUT = true
RUN "ssh-keygen -t ed25519 -f '${KEY_PATH}' -N '' -C '${USER}@${HOSTNAME}-${DATE}' 2>&1"
OUTPUT = false

WRITE ""
WRITE "Setting permissions..."
RUN "chmod 600 '${KEY_PATH}'"
RUN "chmod 644 '${KEY_PATH}.pub'"

WRITE ""
WRITE "========================================="
WRITE "  Key Generated"
WRITE "========================================="
WRITE "Private: ${KEY_PATH}"
WRITE "Public:  ${KEY_PATH}.pub"
WRITE ""
OUTPUT = true
RUN "cat '${KEY_PATH}.pub'"
OUTPUT = false
WRITE ""
WRITE "To copy to server: ssh-copy-id -i ${KEY_PATH}.pub user@host"

EXIT"""
    },
    {
        "name": "user-audit",
        "description": "Lists all human users, groups, and recently logged-in users on the system.",
        "prompt_keywords": ["users", "audit", "user audit", "list users", "groups", "accounts"],
        "tags": ["security", "system", "audit", "diagnostics"],
        "dependencies": ["cat", "grep", "lastlog"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Lists all users, groups, and login history on the system."
OUTPUT = false

CLEAR

WRITE "========================================="
WRITE "  System User Audit"
WRITE "========================================="
WRITE ""

WRITE "-----------------------------------------"
WRITE "  Human Users (UID >= 1000)"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "grep -E ':[0-9]{4,}:' /etc/passwd 2>/dev/null | cut -d: -f1,5,7 | column -t -s: || echo 'Cannot read /etc/passwd'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Sudo/Admin Users"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "grep -E '^sudo|^admin|^wheel' /etc/group 2>/dev/null | cut -d: -f1,4 | column -t -s: || echo 'Cannot read groups'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Recent Logins"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "last -5 2>/dev/null || echo 'No login history available'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Audit Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "failed-logins",
        "description": "Analyzes failed SSH login attempts from system auth logs.",
        "prompt_keywords": ["failed", "login", "auth", "ssh", "brute force", "security", "log analysis"],
        "tags": ["security", "audit", "logs", "diagnostics"],
        "dependencies": ["grep", "sort", "uniq"],
        "args": ["lines"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Analyzes failed SSH login attempts from auth logs."
OUTPUT = false

WRITE "========================================="
WRITE "  Failed Login Analysis"
WRITE "========================================="
WRITE ""

WRITE "Checking auth logs..."
OUTPUT = true
RUN "test -r /var/log/auth.log && echo 'Found /var/log/auth.log' || test -r /var/log/secure && echo 'Found /var/log/secure' || echo 'No auth log found (try with sudo)'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Recent Failed SSH Attempts"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "grep -i 'Failed password' /var/log/auth.log 2>/dev/null | tail -${1:-20} || grep -i 'Failed password' /var/log/secure 2>/dev/null | tail -${1:-20} || echo 'No log access (need sudo or log file not found)'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Top Attacking IPs"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "grep -i 'Failed password' /var/log/auth.log 2>/dev/null | grep -oP 'from \\K[0-9.]+' | sort | uniq -c | sort -rn | head -10 || grep -i 'Failed password' /var/log/secure 2>/dev/null | grep -oP 'from \\K[0-9.]+' | sort | uniq -c | sort -rn | head -10 || echo 'No data available'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Analysis Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "file-integrity",
        "description": "Generates or verifies SHA-256 checksums for all files in a directory to detect changes.",
        "prompt_keywords": ["integrity", "checksum", "verify", "hash", "sha256", "tamper", "detect changes"],
        "tags": ["security", "files", "integrity", "diagnostics"],
        "dependencies": ["sha256sum", "find"],
        "args": ["target_directory", "checksum_file"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Generates or verifies SHA-256 checksums for file integrity."
OUTPUT = false

WRITE "========================================="
WRITE "  File Integrity Checker"
WRITE "========================================="
WRITE ""

WRITE "Directory: ${1:-.}"
WRITE "Checksum:  ${2:-checksums.sha256}"
WRITE ""

RUN "test -d '${1:-.}' && echo 'Directory exists' || echo 'Error: directory not found'"

WRITE ""
WRITE "Generating checksums..."
OUTPUT = true
RUN "find '${1:-.}' -type f -not -name '${2:-checksums.sha256}' -exec sha256sum '{}' ';' 2>/dev/null | tee '${2:-checksums.sha256}' | wc -l"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Summary"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "echo -n 'Files checksummed: ' && wc -l < '${2:-checksums.sha256}'"
RUN "echo 'Checksum file: ${PWD}/${2:-checksums.sha256}'"
OUTPUT = false
WRITE ""
WRITE "To verify later: sha256sum -c ${2:-checksums.sha256}"
WRITE ""

EXIT"""
    },
    {
        "name": "log-analyzer",
        "description": "Analyzes system logs for errors, warnings, and critical events with frequency counts.",
        "prompt_keywords": ["log", "logs", "analyze", "log analysis", "error", "journalctl", "syslog"],
        "tags": ["system", "logs", "diagnostics", "troubleshooting"],
        "dependencies": ["journalctl", "grep"],
        "args": ["hours"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Analyzes system logs for errors, warnings, and critical events."
OUTPUT = false

WRITE "========================================="
WRITE "  System Log Analyzer"
WRITE "========================================="
WRITE ""

WRITE "Time window: Last ${1:-1} hour(s)"
WRITE ""

SINCE="${1:-1}"

WRITE "-----------------------------------------"
WRITE "  Error Count by Service"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "journalctl --since '${SINCE} hours ago' -p err 2>/dev/null | grep -oP '\\w+\\[?' | sort | uniq -c | sort -rn | head -10 || echo 'journalctl not available or no errors'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Recent Critical Events"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "journalctl --since '${SINCE} hours ago' -p crit 2>/dev/null | tail -10 || echo 'No critical events found'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Summary"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "echo -n 'Errors:   ' && journalctl --since '${SINCE} hours ago' -p err 2>/dev/null | wc -l || echo 0"
RUN "echo -n 'Warnings: ' && journalctl --since '${SINCE} hours ago' -p warning 2>/dev/null | wc -l || echo 0"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Analysis Complete"
WRITE "========================================="

EXIT"""
    },
    # ═══════════════════════════════════════════════════════════════════════════
    # ── Section 8: Download & Network Tools
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "download-file",
        "description": "Downloads a file using curl or wget with progress output.",
        "prompt_keywords": ["download", "curl", "wget", "fetch", "get file", "download file"],
        "tags": ["download", "network", "files"],
        "dependencies": ["curl", "wget"],
        "args": ["url", "output_filename"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Downloads a file using curl or wget with progress."
OUTPUT = true

WRITE "========================================="
WRITE "  File Downloader"
WRITE "========================================="
WRITE ""

WRITE "URL: ${1}"
WRITE "Output: ${2}"
WRITE ""

RUN "curl -L -o '${2}' '${1}' 2>/dev/null || wget -O '${2}' '${1}' 2>/dev/null || echo 'Download failed'"

WRITE ""
WRITE "Download complete."

EXIT"""
    },
    {
        "name": "find-large-files",
        "description": "Finds files larger than a specified size in the current directory.",
        "prompt_keywords": ["find", "large", "files", "search", "big files", "large files"],
        "tags": ["files", "search", "disk"],
        "dependencies": ["find", "du"],
        "args": ["min_size_mb"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Finds files larger than a specified size (default: 10MB)."
OUTPUT = true

WRITE "========================================="
WRITE "  Finding Large Files"
WRITE "========================================="
WRITE ""

WRITE "Searching for files larger than ${1:-10}MB in ${PWD}"
WRITE ""

RUN "find . -type f -size +${1:-10}M -exec ls -lh '{}' ';' 2>/dev/null | sort -rh -k5 | head -20"

WRITE ""
WRITE "Search complete."

EXIT"""
    },
    # ═══════════════════════════════════════════════════════════════════════════
    # ── Section 9: Database
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "postgres-backup",
        "description": "Backs up a PostgreSQL database using pg_dump with compression.",
        "prompt_keywords": ["postgres", "postgresql", "database", "pg_dump", "backup", "db backup"],
        "tags": ["database", "postgresql", "backup", "development"],
        "dependencies": ["pg_dump"],
        "args": ["database_name", "output_file"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Backs up a PostgreSQL database with compression."
OUTPUT = false

WRITE "========================================="
WRITE "  PostgreSQL Backup"
WRITE "========================================="
WRITE ""

WRITE "Database: ${1}"
WRITE "Output:   ${2:-${1}_backup.sql.gz}"
WRITE ""

RUN "pg_dump --version 2>/dev/null || echo 'Warning: pg_dump not found. Install postgresql-client.'"

WRITE ""
WRITE "Creating backup..."
OUTPUT = true
RUN "pg_dump '${1}' 2>/dev/null | gzip > '${2:-${1}_backup.sql.gz}' && echo 'Backup successful' || echo 'Backup failed (check database name and permissions)'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Backup Complete"
WRITE "========================================="
RUN "ls -lh '${2:-${1}_backup.sql.gz}'"
WRITE ""
WRITE "To restore: gunzip -c ${2:-${1}_backup.sql.gz} | psql ${1}"

EXIT"""
    },
    {
        "name": "mysql-backup",
        "description": "Backs up a MySQL/MariaDB database using mysqldump with compression.",
        "prompt_keywords": ["mysql", "mariadb", "database", "mysqldump", "db backup", "sql backup"],
        "tags": ["database", "mysql", "backup", "development"],
        "dependencies": ["mysqldump"],
        "args": ["database_name", "user"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Backs up a MySQL/MariaDB database with compression."
OUTPUT = false

WRITE "========================================="
WRITE "  MySQL Database Backup"
WRITE "========================================="
WRITE ""

WRITE "Database: ${1}"
WRITE "User:     ${2:-root}"
WRITE ""

RUN "mysqldump --version 2>/dev/null || echo 'Warning: mysqldump not found'"

WRITE ""
WRITE "Creating backup (you may be prompted for password)..."
OUTPUT = true
RUN "mysqldump -u '${2:-root}' -p '${1}' 2>/dev/null | gzip > '${1}_${DATE}.sql.gz' && echo 'Backup successful' || echo 'Backup failed (check credentials)'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Backup Complete"
WRITE "========================================="
RUN "ls -lh '${1}_${DATE}.sql.gz'"
WRITE ""
WRITE "To restore: gunzip -c ${1}_${DATE}.sql.gz | mysql -u ${2:-root} -p ${1}"

EXIT"""
    },
    {
        "name": "sqlite-query",
        "description": "Runs a SQL query on a SQLite database and displays results in table format.",
        "prompt_keywords": ["sqlite", "sqlite3", "query", "database", "sql", "select"],
        "tags": ["database", "sqlite", "development", "utility"],
        "dependencies": ["sqlite3"],
        "args": ["database_file", "query"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Runs a SQL query on a SQLite database."
OUTPUT = false

WRITE "========================================="
WRITE "  SQLite Query Runner"
WRITE "========================================="
WRITE ""

WRITE "Database: ${1}"
WRITE "Query:    ${2}"
WRITE ""

RUN "test -f '${1}' && echo 'Database found' || echo 'Error: Database file not found'"

WRITE ""
WRITE "Running query..."
WRITE ""

OUTPUT = true
RUN "sqlite3 -header -column '${1}' '${2}' 2>&1 || echo 'Query failed (check syntax or table names)'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Query Complete"
WRITE "========================================="

EXIT"""
    },
    # ═══════════════════════════════════════════════════════════════════════════
    # ── Section 10: Utility & Productivity
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "extract-archive",
        "description": "Automatically detects and extracts compressed archives (zip, tar.gz, tar.bz2, rar, 7z).",
        "prompt_keywords": ["extract", "archive", "unzip", "untar", "unpack", "decompress", "extract files"],
        "tags": ["files", "utility", "archives"],
        "dependencies": ["unzip", "tar", "unrar", "7z"],
        "args": ["archive_file", "output_directory"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Automatically extracts compressed archives by format."
OUTPUT = false

WRITE "========================================="
WRITE "  Archive Extractor"
WRITE "========================================="
WRITE ""

WRITE "Archive: ${1}"
WRITE "Output:  ${2:-.}"
WRITE ""

RUN "test -f '${1}' && echo 'Archive found' || echo 'Error: Archive not found'"

WRITE ""
WRITE "Detecting format and extracting..."

OUTPUT = true
RUN "case '${1}' in
  *.tar.gz|*.tgz) tar -xzf '${1}' -C '${2:-.}' && echo 'Extracted tar.gz' ;;
  *.tar.bz2|*.tbz2) tar -xjf '${1}' -C '${2:-.}' && echo 'Extracted tar.bz2' ;;
  *.tar.xz|*.txz) tar -xJf '${1}' -C '${2:-.}' && echo 'Extracted tar.xz' ;;
  *.tar) tar -xf '${1}' -C '${2:-.}' && echo 'Extracted tar' ;;
  *.zip) unzip -q '${1}' -d '${2:-.}' && echo 'Extracted zip' ;;
  *.rar) unrar x '${1}' '${2:-.}' && echo 'Extracted rar' ;;
  *.7z) 7z x '${1}' -o'${2:-.}' && echo 'Extracted 7z' ;;
  *) echo 'Unknown archive format' ;;
esac 2>&1"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Extraction Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "image-optimize",
        "description": "Optimizes PNG and JPEG images in a directory to reduce file size while preserving quality.",
        "prompt_keywords": ["optimize", "images", "compress", "png", "jpeg", "jpg", "image optimization", "reduce size"],
        "tags": ["files", "utility", "images"],
        "dependencies": ["optipng", "jpegoptim", "find"],
        "args": ["target_directory", "quality"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Optimizes PNG and JPEG images to reduce file sizes."
OUTPUT = false

WRITE "========================================="
WRITE "  Image Optimizer"
WRITE "========================================="
WRITE ""

WRITE "Directory: ${1:-.}"
WRITE "Quality:   ${2:-85}%"
WRITE ""

RUN "test -d '${1:-.}' && echo 'Directory found' || echo 'Error: directory not found'"

WRITE ""
WRITE "Original sizes:"
OUTPUT = true
RUN "find '${1:-.}' -type f \\( -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' \\) -exec du -sh '{}' ';' 2>/dev/null | sort -rh | head -10"
OUTPUT = false

WRITE ""
WRITE "Optimizing PNG files..."
OUTPUT = true
RUN "find '${1:-.}' -type f -name '*.png' -exec optipng -o5 '{}' ';' 2>/dev/null || echo 'optipng not available'"
OUTPUT = false

WRITE ""
WRITE "Optimizing JPEG files at ${2:-85}% quality..."
OUTPUT = true
RUN "find '${1:-.}' -type f \\( -name '*.jpg' -o -name '*.jpeg' \\) -exec jpegoptim --max=${2:-85} --strip-all '{}' ';' 2>/dev/null || echo 'jpegoptim not available'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Optimization Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "text-search",
        "description": "Recursively searches for text patterns in files with context lines and colorized output.",
        "prompt_keywords": ["search", "grep", "find text", "text search", "search files", "content search"],
        "tags": ["files", "search", "utility"],
        "dependencies": ["grep"],
        "args": ["pattern", "search_directory"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Recursively searches for text patterns in files."
OUTPUT = false

WRITE "========================================="
WRITE "  Text Search"
WRITE "========================================="
WRITE ""

WRITE "Pattern: ${1}"
WRITE "Search:  ${2:-.}"
WRITE ""

RUN "test -d '${2:-.}' && echo 'Directory exists' || echo 'Error: directory not found'"

WRITE ""
WRITE "Searching..."
WRITE ""

OUTPUT = true
RUN "grep -rn --color=always '${1}' '${2:-.}' 2>/dev/null | head -50 || echo 'No matches found'"
OUTPUT = false

WRITE ""
WRITE "-----------------------------------------"
WRITE "  Search Summary"
WRITE "-----------------------------------------"
OUTPUT = true
RUN "echo -n 'Matches found: ' && grep -rl '${1}' '${2:-.}' 2>/dev/null | wc -l || echo 0"
RUN "echo -n 'Files with matches: ' && grep -rl '${1}' '${2:-.}' 2>/dev/null | wc -l || echo 0"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Search Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "weather-report",
        "description": "Fetches a weather forecast for a given city using curl from wttr.in.",
        "prompt_keywords": ["weather", "forecast", "temperature", "climate", "curl weather", "wttr"],
        "tags": ["network", "utility", "info"],
        "dependencies": ["curl"],
        "args": ["city"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Fetches current weather for a city."
OUTPUT = false

CLEAR

WRITE "========================================="
WRITE "  Weather Report"
WRITE "========================================="
WRITE ""

WRITE "Location: ${1:-${USER}}"
WRITE ""

OUTPUT = true
RUN "curl -s 'wttr.in/${1:-${USER}}?0' 2>/dev/null | head -20 || echo 'Could not fetch weather (check internet connection)'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Report Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "countdown-timer",
        "description": "Sets a countdown timer with visual progress and notification when time expires.",
        "prompt_keywords": ["timer", "countdown", "time", "reminder", "alarm", "notify"],
        "tags": ["utility", "time", "productivity"],
        "dependencies": ["sleep", "notify-send"],
        "args": ["seconds"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Sets a countdown timer with a completion notification."
OUTPUT = false

WRITE "========================================="
WRITE "  Countdown Timer"
WRITE "========================================="
WRITE ""

WRITE "Timer set for: ${1:-60} seconds"
WRITE "Started at:    ${TIME}"
WRITE ""

REMAINING="${1:-60}"

RUN "while [ ${REMAINING} -gt 0 ]; do
  printf '\\rTime remaining: %3d seconds' ${REMAINING}
  sleep 1
  REMAINING=$((REMAINING - 1))
done"

WRITE ""
WRITE ""
WRITE "========================================="
WRITE "  Time's Up!"
WRITE "========================================="
WRITE "Timer completed at ${TIME}"

OUTPUT = true
RUN "notify-send 'Timer Complete' 'Your ${1:-60}-second timer has finished.' 2>/dev/null || echo 'Desktop notification not available'"
OUTPUT = false

WRITE ""

EXIT"""
    },
    {
        "name": "system-notify",
        "description": "Sends a desktop notification with a custom title and message.",
        "prompt_keywords": ["notify", "notification", "popup", "alert", "message", "desktop notify"],
        "tags": ["utility", "system", "productivity"],
        "dependencies": ["notify-send"],
        "args": ["title", "message"],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Sends a desktop notification with a custom message."
OUTPUT = false

WRITE "========================================="
WRITE "  Desktop Notifier"
WRITE "========================================="
WRITE ""

WRITE "Title:   ${1:-Buffy Notification}"
WRITE "Message: ${2:-Hello from Buffy!}"
WRITE ""

OUTPUT = true
RUN "notify-send '${1:-Buffy Notification}' '${2:-Hello from Buffy!}' 2>/dev/null && echo 'Notification sent' || echo 'notify-send not available (install libnotify-bin)'"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Notification Sent"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "system-cleanup",
        "description": "Performs general system cleanup: clears temp files, caches, and old logs.",
        "prompt_keywords": ["cleanup", "clean", "system clean", "free space", "disk cleanup", "temp"],
        "tags": ["system", "maintenance", "cleanup"],
        "dependencies": ["sudo", "apt", "journalctl"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Performs general system cleanup to free disk space."
OUTPUT = false

CLEAR

WRITE "========================================="
WRITE "  System Cleanup"
WRITE "========================================="
WRITE ""

WRITE "Current disk usage:"
OUTPUT = true
RUN "df -h / | tail -1"
OUTPUT = false

WRITE ""
WRITE "Step 1: Cleaning apt cache..."
OUTPUT = true
RUN "sudo apt clean -y 2>/dev/null && echo 'apt cache cleaned' || echo 'apt not available'"
OUTPUT = false

WRITE ""
WRITE "Step 2: Removing old journal logs..."
OUTPUT = true
RUN "sudo journalctl --vacuum-time=7d 2>/dev/null && echo 'Journal cleaned' || echo 'journalctl not available'"
OUTPUT = false

WRITE ""
WRITE "Step 3: Cleaning temp directories..."
RUN "rm -rf /tmp/* 2>/dev/null || true"
OUTPUT = true
RUN "du -sh ${HOME}/.cache 2>/dev/null | head -1"
OUTPUT = false

WRITE ""
WRITE "Step 4: Removing thumbnail cache..."
RUN "rm -rf ${HOME}/.thumbnails/* 2>/dev/null || true"
RUN "rm -rf ${HOME}/.cache/thumbnails/* 2>/dev/null || true"
WRITE "Thumbnail cache cleared."

WRITE ""
WRITE "Updated disk usage:"
OUTPUT = true
RUN "df -h / | tail -1"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Cleanup Complete"
WRITE "========================================="

EXIT"""
    },
    {
        "name": "npm-clean-install",
        "description": "Cleans node_modules and re-installs npm dependencies from scratch.",
        "prompt_keywords": ["npm", "node", "install", "npm install", "clean install", "node_modules"],
        "tags": ["development", "npm", "nodejs", "maintenance"],
        "dependencies": ["npm", "rm"],
        "args": [],
        "source": """VERSION = "2026.07.28"
AUTHOR = "Buffy Community"
DESCRIPTION = "Removes node_modules and re-installs npm dependencies."
OUTPUT = false

WRITE "========================================="
WRITE "  npm Clean Install"
WRITE "========================================="
WRITE ""

RUN "test -f package.json && echo 'package.json found' || echo 'Warning: No package.json in current directory'"

WRITE ""
WRITE "Step 1: Removing existing node_modules..."
OUTPUT = true
RUN "rm -rf node_modules package-lock.json && echo 'Removed node_modules and lock file'"
OUTPUT = false

WRITE ""
WRITE "Step 2: Cache verification..."
OUTPUT = true
RUN "npm cache verify 2>&1 | tail -2"
OUTPUT = false

WRITE ""
WRITE "Step 3: Fresh install..."
OUTPUT = true
RUN "npm install 2>&1 | tail -5"
OUTPUT = false

WRITE ""
WRITE "========================================="
WRITE "  Install Complete"
WRITE "========================================="
OUTPUT = true
RUN "echo 'Installed packages:' && ls node_modules/.package-lock.json 2>/dev/null && du -sh node_modules/"
OUTPUT = false

EXIT"""
    },
]


# ── Pattern Templates for Script Generation ─────────────────────────────────

PATTERN_TEMPLATES = {
    "system_info": {
        "structure": [
            "metadata",
            "clear_screen",
            "header",
            "display_variables (USER, HOME, PWD, DATE, TIME)",
            "section (OS info)",
            "run_command (uname -a)",
            "section (Memory)",
            "run_command (free -h)",
            "section (Disk)",
            "run_command (df -h)",
            "footer",
            "exit",
        ],
        "variables_used": ["${USER}", "${HOME}", "${PWD}", "${DATE}", "${TIME}", "${TEMP}"],
    },
    "step_by_step": {
        "structure": [
            "metadata",
            "header",
            "step_narratives",
            "run_commands (with OUTPUT toggles)",
            "footer",
            "exit",
        ],
        "variables_used": ["${1}", "${2}"],
    },
    "file_operation": {
        "structure": [
            "metadata",
            "header",
            "argument_display",
            "validation_checks (test -d, test -f)",
            "run_commands",
            "completion_message",
            "exit",
        ],
        "variables_used": ["${1}", "${2}", "${PWD}"],
    },
    "diagnostic": {
        "structure": [
            "metadata",
            "header",
            "argument_display",
            "multiple_sections (each with header + run_command)",
            "summary_section",
            "exit",
        ],
        "variables_used": ["${1}", "${DATE}", "${TIME}"],
    },
    "multi_step_automation": {
        "structure": [
            "metadata",
            "header",
            "step_counter",
            "multiple steps (narrative + run_command per step)",
            "completion_footer",
            "exit",
        ],
        "variables_used": ["${1}", "${DATE}"],
    },
    "utility": {
        "structure": [
            "metadata",
            "simple_header",
            "argument_check",
            "single_or_multiple_commands",
            "result_summary",
            "exit",
        ],
        "variables_used": ["${1}", "${2}"],
    },
}

# ── Instruction Patterns ────────────────────────────────────────────────────

INSTRUCTION_PATTERNS = {
    "WRITE": {
        "description": "Display a text message to the user",
        "pattern": 'WRITE "message"',
        "usage_notes": [
            "Use for headers, progress messages, and results",
            "Empty WRITE \"\" prints a blank line",
            "Variables like ${HOME} are expanded automatically",
        ],
    },
    "RUN": {
        "description": "Execute a shell command",
        "pattern": 'RUN "shell command"',
        "usage_notes": [
            "Use for all system commands",
            "Wrap arguments in quotes: RUN \"mkdir '${1}'\"",
            "OUTPUT = true shows output; OUTPUT = false hides it",
            "Non-zero exit stops execution immediately",
        ],
    },
    "WAIT": {
        "description": "Pause execution for N seconds or until user presses Enter",
        "pattern": 'WAIT 5  or  WAIT "Press Enter to continue..."',
        "usage_notes": [
            "WAIT with a number pauses for that many seconds",
            "WAIT with a string shows the message and waits for Enter",
        ],
    },
    "CLEAR": {
        "description": "Clear the terminal screen",
        "pattern": "CLEAR",
        "usage_notes": [
            "Use at the start of scripts that show formatted output",
        ],
    },
    "EXIT": {
        "description": "Stop script execution immediately",
        "pattern": "EXIT",
        "usage_notes": [
            "Use at the end of every script",
            "Use for early exit after displaying results",
        ],
    },
    "OUTPUT": {
        "description": "Toggle whether RUN command output is shown",
        "pattern": "OUTPUT = true  or  OUTPUT = false",
        "usage_notes": [
            "Set OUTPUT = false at the start for automation scripts",
            "Toggle to true for specific commands the user should see",
            "Can be set multiple times throughout the script",
        ],
    },
}


def get_examples_by_tag(tag: str) -> List[Dict]:
    """Return all training examples that match a given tag."""
    return [ex for ex in TRAINING_EXAMPLES if tag in ex["tags"]]


def get_examples_by_keyword(keyword: str) -> List[Dict]:
    """Return all training examples that match a keyword (case-insensitive)."""
    keyword_lower = keyword.lower()
    results = []
    for ex in TRAINING_EXAMPLES:
        if any(keyword_lower in kw.lower() for kw in ex["prompt_keywords"]):
            results.append(ex)
        elif keyword_lower in ex["description"].lower():
            results.append(ex)
        elif keyword_lower in ex["name"].lower():
            results.append(ex)
    return results


def get_all_tags() -> List[str]:
    """Return a sorted list of all unique tags in the corpus."""
    tags = set()
    for ex in TRAINING_EXAMPLES:
        tags.update(ex["tags"])
    return sorted(tags)


def get_all_dependencies() -> List[str]:
    """Return a sorted list of all unique shell dependencies."""
    deps = set()
    for ex in TRAINING_EXAMPLES:
        deps.update(ex["dependencies"])
    return sorted(deps)


def summary() -> Dict:
    """Return a summary of the training corpus."""
    return {
        "total_examples": len(TRAINING_EXAMPLES),
        "total_tags": len(get_all_tags()),
        "total_dependencies": len(get_all_dependencies()),
        "tags": get_all_tags(),
        "dependencies": get_all_dependencies(),
        "script_names": [ex["name"] for ex in TRAINING_EXAMPLES],
        "template_count": len(PATTERN_TEMPLATES),
    }


if __name__ == "__main__":
    print(json.dumps(summary(), indent=2))
