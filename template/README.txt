================================================================================
                     BUFFY PLUGIN TEMPLATE
================================================================================

This directory contains a template structure for creating your own
Buffy plugins (packages of .bsl scripts).

PURPOSE:
  Buffy plugins are collections of .bsl scripts organized into packages
  that can be installed with "buffy --install <package-name>". This
  template shows you the required structure, metadata format, SHA
  verification, and distribution setup.

CONTENTS:

  CREATING_PLUGINS.txt    Step-by-step guide to creating, testing,
                          packaging, and distributing your own plugins.

  index.json              Template for a repository index file that
                          Buffy uses to discover installable packages.

  my-plugin/              Example plugin package with sample scripts
    index.bsl             and SHA verification files. Use this as a
    hello.bsl             reference when building your own plugin.
    hello.bsl.sha256
    index.bsl.sha256

QUICK START:
  1. Read CREATING_PLUGINS.txt for the full guide
  2. Copy the my-plugin/ directory and rename it
  3. Replace the .bsl scripts with your own commands
  4. Generate SHA-256 checksums for each .bsl file
  5. Add your package to index.json
  6. Push to a GitHub repository and add it to Buffy

  For more information about Buffy, see:
    https://github.com/Blaze12345-deluxe/BuffyCLI
================================================================================
