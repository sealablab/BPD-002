#!/usr/bin/env python3
"""
Replace all references to BPD-002 with BPD-002 in the codebase.

This script performs case-preserving replacements:
- BPD-002 → BPD-002
- bpd-002 → bpd-002
- BPD_002 → BPD_002
- bpd_002 → bpd_002
- etc.
"""

import os
import re
from pathlib import Path
from typing import Dict, List
import argparse
import shutil


class OldReferencesReplacer:
    """Replace old repository references with new ones."""

    # Replacement mappings (preserving case)
    REPLACEMENTS = {
        'BPD-002': 'BPD-002',
        'bpd-002': 'bpd-002',
        'BPD_002': 'BPD_002',
        'bpd_002': 'bpd_002',
        'BPD002': 'BPD002',
        'bpd002': 'bpd002',
        'Bpd-002': 'Bpd-002',
        'Bpd_002': 'Bpd_002',
    }

    # File extensions to process
    TEXT_EXTENSIONS = {
        '.py', '.md', '.txt', '.yaml', '.yml', '.toml', '.cfg', '.ini',
        '.json', '.xml', '.rst', '.sh', '.bash', '.zsh',
        '.vhd', '.vhdl', '.tcl',
        '.c', '.h', '.cpp', '.hpp',
        '.html', '.css', '.js', '.ts',
        '.gitignore', '.gitattributes', '.gitmodules',
        '',  # Files without extension
    }

    # Directories to skip
    SKIP_DIRS = {
        '.git', '__pycache__', '.pytest_cache', '.mypy_cache',
        'node_modules', '.venv', 'venv', 'env',
        '.tox', '.nox', 'dist', 'build', 'eggs', '*.egg-info',
        '.cache', '.coverage', 'htmlcov',
    }

    def __init__(self, root_dir: str, dry_run: bool = True, backup: bool = True):
        self.root_dir = Path(root_dir).resolve()
        self.dry_run = dry_run
        self.backup = backup
        self.modified_files: List[Path] = []
        self.total_replacements = 0

    def should_skip_dir(self, dir_path: Path) -> bool:
        """Check if directory should be skipped."""
        dir_name = dir_path.name
        return any(skip in str(dir_path) or dir_name == skip
                   for skip in self.SKIP_DIRS)

    def is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file we should process."""
        return file_path.suffix.lower() in self.TEXT_EXTENSIONS

    def replace_in_file(self, file_path: Path) -> int:
        """Replace old references in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()

            # Perform all replacements
            new_content = original_content
            replacements_made = 0

            for old, new in self.REPLACEMENTS.items():
                if old in new_content:
                    new_content = new_content.replace(old, new)
                    replacements_made += new_content.count(new) - original_content.count(new)

            # If changes were made
            if new_content != original_content:
                if self.dry_run:
                    print(f"  [DRY RUN] Would modify: {file_path.relative_to(self.root_dir)}")
                else:
                    # Backup if requested
                    if self.backup:
                        backup_path = Path(str(file_path) + '.bak')
                        shutil.copy2(file_path, backup_path)

                    # Write changes
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    print(f"  ✓ Modified: {file_path.relative_to(self.root_dir)}")

                self.modified_files.append(file_path)
                return replacements_made

        except Exception as e:
            print(f"  ✗ Error processing {file_path}: {e}")

        return 0

    def process(self) -> Dict:
        """Process all files in directory tree."""
        mode = "DRY RUN" if self.dry_run else "LIVE MODE"
        print(f"{'=' * 80}")
        print(f"REPLACING BPD-002 → BPD-002 ({mode})")
        print(f"{'=' * 80}")
        print()

        if self.dry_run:
            print("⚠️  Running in DRY RUN mode - no files will be modified")
            print("   Run with --execute to perform actual replacements")
            print()
        else:
            backup_status = "enabled" if self.backup else "disabled"
            print(f"✓ LIVE MODE - files will be modified (backup: {backup_status})")
            print()

        file_count = 0
        processed_count = 0

        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)

            # Skip unwanted directories
            dirs[:] = [d for d in dirs if not self.should_skip_dir(root_path / d)]

            for file_name in files:
                file_path = root_path / file_name
                file_count += 1

                # Process text files
                if self.is_text_file(file_path):
                    replacements = self.replace_in_file(file_path)
                    if replacements > 0:
                        self.total_replacements += replacements
                        processed_count += 1

        print()
        print(f"{'=' * 80}")
        print("SUMMARY")
        print(f"{'=' * 80}")
        print(f"Files scanned:        {file_count}")
        print(f"Files modified:       {len(self.modified_files)}")
        print(f"Total replacements:   {self.total_replacements}")

        if self.dry_run:
            print()
            print("⚠️  This was a DRY RUN - no files were actually modified")
            print("   Run with --execute to perform the replacements")
        else:
            print()
            print("✓ Replacements complete!")
            if self.backup:
                print("  Backups saved with .bak extension")

        return {
            'files_scanned': file_count,
            'files_modified': len(self.modified_files),
            'total_replacements': self.total_replacements,
        }

    def restore_backups(self):
        """Restore all backed up files."""
        if not self.backup:
            print("No backups were created")
            return

        restored = 0
        for file_path in self.modified_files:
            backup_path = Path(str(file_path) + '.bak')
            if backup_path.exists():
                shutil.copy2(backup_path, file_path)
                backup_path.unlink()
                restored += 1
                print(f"  ✓ Restored: {file_path.relative_to(self.root_dir)}")

        print(f"\n✓ Restored {restored} files from backup")

    def clean_backups(self):
        """Remove all backup files."""
        cleaned = 0
        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)

            # Skip unwanted directories
            dirs[:] = [d for d in dirs if not self.should_skip_dir(root_path / d)]

            for file_name in files:
                if file_name.endswith('.bak'):
                    backup_path = root_path / file_name
                    backup_path.unlink()
                    cleaned += 1
                    print(f"  ✓ Removed: {backup_path.relative_to(self.root_dir)}")

        print(f"\n✓ Cleaned {cleaned} backup files")


def main():
    parser = argparse.ArgumentParser(
        description='Replace all references to BPD-002 with BPD-002',
        epilog='''
Examples:
  # Dry run (preview changes)
  python replace_old_references.py

  # Execute replacements with backup
  python replace_old_references.py --execute

  # Execute without backup
  python replace_old_references.py --execute --no-backup

  # Restore from backups
  python replace_old_references.py --restore

  # Clean up backup files
  python replace_old_references.py --clean-backups
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to process (default: current directory)'
    )

    parser.add_argument(
        '-e', '--execute',
        action='store_true',
        help='Execute replacements (default is dry run)'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files'
    )

    parser.add_argument(
        '--restore',
        action='store_true',
        help='Restore files from .bak backups'
    )

    parser.add_argument(
        '--clean-backups',
        action='store_true',
        help='Remove all .bak backup files'
    )

    args = parser.parse_args()

    replacer = OldReferencesReplacer(
        args.directory,
        dry_run=not args.execute,
        backup=not args.no_backup
    )

    # Handle special operations
    if args.restore:
        print("Restoring from backups...")
        replacer.restore_backups()
        return 0

    if args.clean_backups:
        print("Cleaning backup files...")
        replacer.clean_backups()
        return 0

    # Normal processing
    result = replacer.process()

    # Return exit code based on whether changes were made
    return 0 if result['files_modified'] == 0 else 0


if __name__ == '__main__':
    exit(main())
