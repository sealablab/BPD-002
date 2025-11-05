#!/usr/bin/env python3
"""
Find all references to BPD-002 in the codebase for migration to BPD-002.

This script performs a case-insensitive, exhaustive search for:
- BPD-002 / bpd-002 (various case combinations)
- File paths containing bpd-002
- Git URLs and references
- Documentation references
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Set
import argparse


class OldReferencesFinder:
    """Find old repository references in codebase."""

    # Patterns to search for (case-insensitive)
    PATTERNS = [
        r'bpd-002',
        r'bpd_002',
        r'BPD-002',
        r'BPD_002',
        r'bpd002',
        r'BPD002',
    ]

    # File extensions to search
    TEXT_EXTENSIONS = {
        '.py', '.md', '.txt', '.yaml', '.yml', '.toml', '.cfg', '.ini',
        '.json', '.xml', '.rst', '.sh', '.bash', '.zsh',
        '.vhd', '.vhdl', '.tcl',
        '.c', '.h', '.cpp', '.hpp',
        '.html', '.css', '.js', '.ts',
        '.gitignore', '.gitattributes', '.gitmodules',
        '',  # Files without extension (README, LICENSE, etc.)
    }

    # Directories to skip
    SKIP_DIRS = {
        '.git', '__pycache__', '.pytest_cache', '.mypy_cache',
        'node_modules', '.venv', 'venv', 'env',
        '.tox', '.nox', 'dist', 'build', 'eggs', '*.egg-info',
        '.cache', '.coverage', 'htmlcov',
    }

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.matches: List[Dict] = []

    def should_skip_dir(self, dir_path: Path) -> bool:
        """Check if directory should be skipped."""
        dir_name = dir_path.name
        return any(skip in str(dir_path) or dir_name == skip
                   for skip in self.SKIP_DIRS)

    def is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file we should search."""
        return file_path.suffix.lower() in self.TEXT_EXTENSIONS

    def search_file_content(self, file_path: Path) -> List[Dict]:
        """Search for patterns in file content."""
        matches = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line_lower = line.lower()

                    # Check each pattern
                    for pattern in self.PATTERNS:
                        if re.search(pattern, line, re.IGNORECASE):
                            matches.append({
                                'file': file_path.relative_to(self.root_dir),
                                'line_num': line_num,
                                'line': line.rstrip(),
                                'pattern': pattern,
                                'type': 'content'
                            })
                            break  # Only record once per line
        except Exception as e:
            # Skip files that can't be read
            pass

        return matches

    def search_file_path(self, file_path: Path) -> Dict | None:
        """Check if file path itself contains old references."""
        path_str = str(file_path).lower()

        for pattern in self.PATTERNS:
            if re.search(pattern, path_str, re.IGNORECASE):
                return {
                    'file': file_path.relative_to(self.root_dir),
                    'line_num': 0,
                    'line': str(file_path.relative_to(self.root_dir)),
                    'pattern': pattern,
                    'type': 'filepath'
                }

        return None

    def scan(self) -> List[Dict]:
        """Scan entire directory tree."""
        print(f"Scanning {self.root_dir}...")
        print(f"Searching for patterns: {', '.join(self.PATTERNS)}")
        print()

        file_count = 0

        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)

            # Skip unwanted directories
            dirs[:] = [d for d in dirs if not self.should_skip_dir(root_path / d)]

            for file_name in files:
                file_path = root_path / file_name
                file_count += 1

                # Check file path
                path_match = self.search_file_path(file_path)
                if path_match:
                    self.matches.append(path_match)

                # Check file content
                if self.is_text_file(file_path):
                    content_matches = self.search_file_content(file_path)
                    self.matches.extend(content_matches)

        print(f"Scanned {file_count} files")
        print(f"Found {len(self.matches)} references to old repo name")
        print()

        return self.matches

    def print_results(self, group_by_file: bool = True):
        """Print results in human-readable format."""
        if not self.matches:
            print("✅ No references to BPD-002 found!")
            return

        print("=" * 80)
        print("FOUND REFERENCES TO BPD-002")
        print("=" * 80)
        print()

        if group_by_file:
            # Group by file
            by_file: Dict[Path, List[Dict]] = {}
            for match in self.matches:
                file_path = match['file']
                if file_path not in by_file:
                    by_file[file_path] = []
                by_file[file_path].append(match)

            # Print grouped results
            for file_path in sorted(by_file.keys()):
                matches = by_file[file_path]

                # Check if it's a filepath match
                filepath_matches = [m for m in matches if m['type'] == 'filepath']
                content_matches = [m for m in matches if m['type'] == 'content']

                if filepath_matches:
                    print(f"📁 FILE PATH: {file_path}")
                    print(f"   → Rename this file/directory")
                    print()

                if content_matches:
                    print(f"📄 {file_path} ({len(content_matches)} occurrence{'s' if len(content_matches) > 1 else ''})")
                    for match in content_matches:
                        print(f"   Line {match['line_num']:4d}: {match['line'][:100]}")
                    print()
        else:
            # Print all matches sequentially
            for match in self.matches:
                if match['type'] == 'filepath':
                    print(f"📁 FILE PATH: {match['file']}")
                else:
                    print(f"📄 {match['file']}:{match['line_num']}")
                    print(f"   {match['line'][:100]}")
                print()

    def save_to_file(self, output_file: str):
        """Save results to a file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("BPD-002 References Found\n")
            f.write("=" * 80 + "\n\n")

            # Group by file
            by_file: Dict[Path, List[Dict]] = {}
            for match in self.matches:
                file_path = match['file']
                if file_path not in by_file:
                    by_file[file_path] = []
                by_file[file_path].append(match)

            # Write grouped results
            for file_path in sorted(by_file.keys()):
                matches = by_file[file_path]

                filepath_matches = [m for m in matches if m['type'] == 'filepath']
                content_matches = [m for m in matches if m['type'] == 'content']

                if filepath_matches:
                    f.write(f"FILE PATH: {file_path}\n")
                    f.write(f"  ACTION: Rename this file/directory\n\n")

                if content_matches:
                    f.write(f"FILE: {file_path} ({len(content_matches)} occurrences)\n")
                    for match in content_matches:
                        f.write(f"  Line {match['line_num']:4d}: {match['line']}\n")
                    f.write("\n")

        print(f"✅ Results saved to: {output_file}")

    def generate_summary(self) -> Dict:
        """Generate summary statistics."""
        if not self.matches:
            return {
                'total_matches': 0,
                'files_affected': 0,
                'filepath_matches': 0,
                'content_matches': 0,
            }

        files: Set[Path] = set()
        filepath_count = 0
        content_count = 0

        for match in self.matches:
            files.add(match['file'])
            if match['type'] == 'filepath':
                filepath_count += 1
            else:
                content_count += 1

        return {
            'total_matches': len(self.matches),
            'files_affected': len(files),
            'filepath_matches': filepath_count,
            'content_matches': content_count,
        }


def main():
    parser = argparse.ArgumentParser(
        description='Find all references to BPD-002 in codebase'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to search (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Save results to file'
    )
    parser.add_argument(
        '--no-group',
        action='store_true',
        help='Do not group results by file'
    )

    args = parser.parse_args()

    # Create finder and scan
    finder = OldReferencesFinder(args.directory)
    matches = finder.scan()

    # Print results
    finder.print_results(group_by_file=not args.no_group)

    # Print summary
    summary = finder.generate_summary()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total matches:      {summary['total_matches']}")
    print(f"Files affected:     {summary['files_affected']}")
    print(f"File path matches:  {summary['filepath_matches']}")
    print(f"Content matches:    {summary['content_matches']}")
    print()

    # Save to file if requested
    if args.output:
        finder.save_to_file(args.output)

    # Exit with error code if matches found
    return 1 if matches else 0


if __name__ == '__main__':
    exit(main())
