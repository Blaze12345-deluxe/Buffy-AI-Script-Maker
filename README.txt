================================================================================
                     BSL AI Script Generator
================================================================================

Location: AI/
Language: Python 3
Purpose:  Train an AI to generate valid BSL scripts from natural language
          prompts and validate them for correct syntax.

Supports saving and resuming training state so you can train, stop,
and resume later. Generated scripts can be imported back as custom
training examples to improve future generations. Training data can be
exported as a valid GGUF binary container.


================================================================================
RELATED RESOURCES
================================================================================

This tool generates scripts for the Buffy CLI Automation Framework.
The following resources provide context on the framework and its
plugin ecosystem:

  Buffy CLI (framework + documentation):
    https://github.com/Blaze12345-deluxe/BuffyCLI

  Buffy CLI documentation (docs/ folder):
    https://github.com/Blaze12345-deluxe/BuffyCLI/tree/master/docs

    SCRIPT_LANGUAGE.txt   - Complete BSL syntax, variables, best practices
    INSTALLATION.txt      - Installing Buffy from source, cargo, or binary
    COMMANDS.txt          - All CLI flags, repo management, aliases
    CONFIGURATION.txt     - ~/.buffy/ layout, package format, SHA files
    TROUBLESHOOTING.txt   - Common problems and diagnostics

  Buffy Plugins (community plugin repository):
    https://github.com/Blaze12345-deluxe/Buffy-Plugins

  Plugin scaffold generator:
    https://github.com/Blaze12345-deluxe/Buffy-AI-Script-Maker/tree/master/template


================================================================================
QUICK START
================================================================================

  Generate a script from a prompt:
    python run.py "create a python virtual environment"

  Generate and save to a file:
    python run.py "backup my home directory" --output backup.bsl

  Generate with syntax validation:
    python run.py "check disk space" --check

  Interactive mode:
    python run.py --interactive

  Show training corpus summary:
    python run.py --train

  Save training state for later:
    python run.py --save-state state.json

  Resume from saved state and generate:
    python run.py --resume state.json "monitor disk usage"

  Import a .bsl file as a custom training example:
    python run.py --learn my-script.bsl --save-state state.json

  Generate and automatically learn the result:
    python run.py "backup my files" --learn --save-state state.json

  Export training data and build a GGUF container:
    bash compile-to-gguf.sh --verify

  Build a GGUF container from existing JSONL data:
    python build-gguf-container.py --dataset bsl-training-dataset.jsonl \
        --output bsl-ai.gguf --verify


================================================================================
FILE DESCRIPTIONS
================================================================================

  run.py                  Main CLI entry point. Parses arguments, orchestrates
                          generation and validation. Supports save-state,
                          resume, and learn flags.

  bsl_generator.py        Core generation engine. Takes a natural language
                          prompt, matches against training examples, adapts
                          or generates from scratch. Returns complete, valid
                          .bsl source. Accepts a trainer for custom corpus.

  bsl_tester.py           Syntax validation engine. Rule-based validation
                          checks metadata placement, instruction syntax,
                          argument quoting, variable usage, dangerous
                          commands, and script structure. Optionally
                          integrates with 'buffy --check' binary.

  bsl_train.py            Training pipeline. Loads the corpus, analyzes
                          patterns, exports training data as JSON/JSONL,
                          and generates format reference documents.
                          Supports save_state() and load_state() for
                          training continuation. The BSLAITrainer class
                          tracks custom_examples, hit_count, and
                          recent_prompts for training analytics.

  training_data.py        Training corpus. Contains 12 BSL example scripts
                          organized by category with descriptions, keywords,
                          tags, and dependencies. Also defines pattern
                          templates and instruction patterns for generation.

  compile-to-gguf.sh      Shell script that runs the full pipeline: exports
                          JSONL and corpus JSON, then builds a valid GGUF
                          v3 binary container with metadata but no tensors.

  build-gguf-container.py Standalone Python script that reads a JSONL
                          dataset and produces a real .gguf binary file
                          using Python struct, conforming to the GGUF v3
                          specification. Includes read-back verification.


================================================================================
HOW IT WORKS
================================================================================

1. PROMPT ANALYSIS
   The user provides a natural language prompt (e.g., "create a script
   that monitors disk space").

2. PATTERN MATCHING
   The generator scores each training example against the prompt using
   keyword matching, tag matching, and description overlap. The best
   match is selected. If a trainer with custom examples is provided,
   those are included in the corpus.

3. SCRIPT GENERATION
   - If a good match is found (score >= 10): the matched example's
     source is adapted (metadata updated, arguments adjusted).
   - If no good match exists: a script is generated from scratch using
     the pattern templates and detected shell commands.

4. SYNTAX VALIDATION
   The generated script is validated against BSL spec rules:
   - Metadata placement (must come before instructions)
   - Instruction validation (WRITE, RUN, WAIT, CLEAR, EXIT)
   - OUTPUT toggle validation
   - Argument quoting
   - Variable usage
   - Dangerous command detection
   - Optional integration with 'buffy --check'

   After generation, you can also validate against the full BSL
   specification using Buffy CLI commands:
     buffy --check script.bsl       (syntax validation)
     buffy --validate script.bsl    (metadata completeness)
     buffy --run script.bsl         (test execution)


================================================================================
TRAINING CONTINUATION (--save-state / --resume)
================================================================================

The training state can be saved to a JSON file and reloaded later,
allowing you to train, stop, resume, and continue across sessions.

Save state (preserves corpus, custom examples, and match history):
    python run.py --save-state state.json

Resume from saved state:
    python run.py --resume state.json

Resume and show training summary:
    python run.py --resume state.json --train

Resume and generate from a prompt:
    python run.py --resume state.json "monitor disk usage"

The saved state includes:
  - The full training corpus (all example scripts with source code)
  - Custom examples added via --learn
  - Pattern templates and instruction definitions
  - Training metrics (hit counts, recent prompts)


================================================================================
LEARNING FROM SCRIPTS (--learn)
================================================================================

The --learn flag imports .bsl scripts as custom training examples,
which are then used in future generations alongside the built-in
corpus. This lets the AI improve over time from user feedback.

Import an existing .bsl file:
    python run.py --learn my-script.bsl --save-state state.json

The parser automatically extracts:
  - Name: from the filename
  - Description: from the DESCRIPTION metadata field
  - Dependencies: from RUN command executables
  - Arguments: from ${N} variable references in the source
  - Tags: auto-generated from description keywords and dependencies

Generate a script and learn the result in one command:
    python run.py "backup my home directory" --learn --save-state state.json

Override the example name and description:
    python run.py --learn my-script.bsl \
        --learn-name "custom-backup" \
        --learn-desc "My custom backup script" \
        --save-state state.json

Interactive mode also supports learning:
  >> learn my-script.bsl
  >> learn /path/to/another-script.bsl

Learned examples are persistent when saved with --save-state and
restored on --resume. The trainer tracks how often each example
is matched (hit_count) for training analytics.


================================================================================
GGUF EXPORT
================================================================================

The repository can export training data as a valid GGUF v3 binary
container. GGUF (GPT-Generated Unified Format) is the file format
used by llama.cpp and other LLM inference engines.

The GGUF container is metadata-only (no tensors/weights) and stores:
  - General model identification (name, description, architecture)
  - Dataset statistics (instruction count, authors, topics, output lengths)
  - BSL-specific metadata (version, num examples, language, file extension)
  - Training configuration (context length, tokenizer availability)

Full pipeline (export + build + verify):
    bash compile-to-gguf.sh --verify

Output directory: gguf-export/
  bsl-ai-minimal.gguf           Valid GGUF v3 container (~1 KB)
  bsl-training-dataset.jsonl    Training examples in JSONL format
  bsl-corpus.json               Full structured corpus with metadata
  bsl-ai-state.json             (if --train used) Saved AI state

Options:
    --train             Train and save state before exporting
    --verify            Validate the generated GGUF file
    --output-dir <dir>  Custom output directory (default: ./gguf-export)

Build a GGUF container from existing data (standalone):
    python build-gguf-container.py \
        --dataset gguf-export/bsl-training-dataset.jsonl \
        --output bsl-ai.gguf \
        --verify


================================================================================
TRAINING CORPUS
================================================================================

The training corpus contains 12 example scripts covering these categories:

  system          - system-info, system-update, disk-usage
  development     - pip-env, project-setup, git-quick-setup
  network         - network-diagnostic
  containers      - docker-cleanup
  backup/archive  - backup-directory
  files/download  - download-file, find-large-files

Each example includes:
  - Full BSL source code
  - Natural language description
  - Keyword list for prompt matching
  - Tags for categorization
  - Shell dependencies
  - Expected arguments

For the complete BSL language specification (syntax rules, metadata
fields, variable resolution order, error handling, command resolution
priorities, and best practices), see the SCRIPT_LANGUAGE.txt guide:
  https://github.com/Blaze12345-deluxe/BuffyCLI/blob/master/docs/SCRIPT_LANGUAGE.txt

Export the corpus for external AI systems:
    python bsl_train.py --export bsl-corpus.json

Export as JSONL fine-tuning dataset:
    python bsl_train.py --export-dataset bsl-training.jsonl

View BSL format reference:
    python bsl_train.py --export-format


================================================================================
COMMAND REFERENCE
================================================================================

  python run.py <prompt>
    Generate a BSL script from a natural language prompt.

  python run.py <prompt> --output <file>
    Generate and save to a specific file.

  python run.py <prompt> --check
    Generate and validate syntax.

  python run.py <prompt> --buffy-check
    Generate and validate using both rules and 'buffy --check'.

  python run.py <prompt> --quiet
    Only output the script source (no diagnostics).

  python run.py <prompt> --author <name>
    Set the author metadata field (default: "AI Generated").

  python run.py --interactive
    Interactive prompt loop for multiple generations.

  python run.py --train
    Show training corpus summary.

  python run.py --save-state <file>
    Save the current training state to a JSON file.

  python run.py --resume <file>
    Resume from a previously saved training state.

  python run.py --learn [<file>]
    Import a .bsl file (or the generated script if no file is given)
    as a custom training example.

  python run.py --learn-name <name>
    Override the name for the learned example.

  python run.py --learn-desc <desc>
    Override the description for the learned example.

  python bsl_tester.py <file.bsl>
    Validate a .bsl file for syntax errors.

  python bsl_train.py --export [file.json]
    Export training corpus as JSON.

  python bsl_train.py --export-format
    Print BSL format reference.

  python bsl_train.py --export-dataset [file.jsonl]
    Export training data as JSONL fine-tuning dataset.

  python bsl_train.py --export-all [dir]
    Export all formats (JSON corpus + format reference).

  python bsl_train.py --save-state [file.json]
    Save training state from bsl_train.py directly.

  python bsl_train.py --resume <file>
    Resume training state from bsl_train.py.

  bash compile-to-gguf.sh [--train] [--verify] [--output-dir <dir>]
    Run the full GGUF export pipeline.

  python build-gguf-container.py --dataset <file> [--output <file>]
    Build a GGUF container from a JSONL dataset. Use --verify to validate.


================================================================================
INTERACTIVE MODE COMMANDS
================================================================================

  <prompt>            Describe the script you want to generate
  quit                Exit interactive mode
  help                Show command help
  train               Show training corpus summary
  save <file>         Save training state (default: bsl-ai-state.json)
  export <file>       Export corpus as JSON or JSONL
  learn <file.bsl>    Import a .bsl file as a custom training example


================================================================================
LEARN MORE & RESOURCES
================================================================================

| Resource | Link |
|----------|------|
| Buffy CLI source + docs   | github.com/Blaze12345-deluxe/BuffyCLI |
| Buffy CLI documentation   | github.com/Blaze12345-deluxe/BuffyCLI/tree/master/docs |
| Buffy Plugins repository  | github.com/Blaze12345-deluxe/Buffy-Plugins |
| Training guide (advanced) | TRAINING_GUIDE.txt (in this repository) |
| Plugin scaffold generator | github.com/Blaze12345-deluxe/Buffy-AI-Script-Maker/tree/master/template |
| Official releases         | github.com/Blaze12345-deluxe/BuffyCLI/releases |


================================================================================
REQUIREMENTS
================================================================================

  - Python 3.6+ (no external dependencies required for generation)
  - Optional: 'buffy' binary in PATH for full validation
  - Optional: llama.cpp for actual model fine-tuning (see README-GGUF.txt)

================================================================================
