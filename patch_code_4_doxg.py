#!/usr/bin/env python3
"""
Doxygen Source Code Patcher
Author: asaeppel4231 & AI
License: MIT
Description: Patches complex multiline C macros so Doxygen can parse them correctly.
"""

import os
import re
import sys
import argparse

# Regular expression to catch multiline macros.
# Captures #define, the macro name with optional parameters, and all lines ending with a backslash '\'.
MULTILINE_MACRO_REGEX = re.compile(
    r'(^[ \t]*#define\s+(\w+)(?:\([^\)]*\))?\s+.*?(?:\\\s*\n.*?)*)(?<!\\)\n',
    re.MULTILINE
)

def find_line_number(full_content, match_start_pos):
    """Calculates the 1-based line number of a character position."""
    return full_content.count('\n', 0, match_start_pos) + 1

def patch_content(content, rel_path, remote_repo_path):
    """
    Searches for multiline macros and replaces their bodies.
    """
    # Standardize path separators to forward slashes for URLs
    url_file_path = rel_path.replace(os.sep, '/')

    def replace_macro(match):
        full_match = match.group(1)
        macro_name = match.group(2)
        
        # Calculate the exact original line number
        line_no = find_line_number(content, match.start())
        
        header_match = re.match(r'^[ \t]*#define\s+\w+(?:\([^\)]*\))?', full_match)
        macro_header = header_match.group(0) if header_match else f"#define {macro_name}"
        
        if remote_repo_path:
            base_url = remote_repo_path.rstrip('/')
            # Target relative path and append line number anchor
            comment = f"/* View complete macro content at: {base_url}/{url_file_path}#L{line_no} */"
        else:
            comment = "/* */"
            
        return f"{macro_header} {comment}\n"

    return MULTILINE_MACRO_REGEX.sub(replace_macro, content)

def patch_file(input_path, output_path, base_dir, remote_repo_path):
    """Reads a file, patches its macro definitions, and writes the output."""
    try:
        # Calculate relative path from the base directory
        rel_path = os.path.relpath(input_path, base_dir)
        
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Pass the relative path instead of just the filename
        patched = patch_content(content, rel_path, remote_repo_path)
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(patched)
        print(f"✓ Patched: {input_path} -> {output_path}")
    except Exception as e:
        print(f"✗ Error patching {input_path}: {e}", file=sys.stderr)

def process_path(target_path, is_ci, output_arg, remote_repo_path):
    """Processes either a single file or a directory recursively based on CLI flags."""
    target_path = os.path.abspath(target_path)
    
    # FIX: Always resolve relative paths from the current working directory (CWD)
    # to ensure the full repository folder structure (like src/errors/) is preserved.
    base_dir = os.getcwd()
    
    # Case 1: Input is a single file
    if os.path.isfile(target_path):
        filename = os.path.basename(target_path)
        # Calculate the proper relative path from the repository root
        rel_path = os.path.relpath(target_path, base_dir)
        
        if is_ci:
            patch_file(target_path, target_path, base_dir, remote_repo_path)
        elif output_arg:
            patch_file(target_path, output_arg, base_dir, remote_repo_path)
        else:
            # Reconstruct .tmp path relative to the file's own directory
            tmp_path = os.path.join(os.path.dirname(target_path), ".tmp", filename)
            patch_file(target_path, tmp_path, base_dir, remote_repo_path)

    # Case 2: Input is a directory
    elif os.path.isdir(target_path):
        for root, _, files in os.walk(target_path):
            if ".tmp" in root or ".git" in root:
                continue
                
            for file in files:
                if file.endswith(('.c', '.h')):
                    file_input_path = os.path.join(root, file)
                    # rel_path is automatically calculated relative to base_dir (CWD)
                    rel_path = os.path.relpath(file_input_path, base_dir)
                    
                    if is_ci:
                        patch_file(file_input_path, file_input_path, base_dir, remote_repo_path)
                    elif output_arg:
                        file_output_path = os.path.join(output_arg, rel_path)
                        patch_file(file_input_path, file_output_path, base_dir, remote_repo_path)
                    else:
                        file_output_path = os.path.join(target_path, ".tmp", os.path.relpath(file_input_path, target_path))
                        patch_file(file_input_path, file_output_path, base_dir, remote_repo_path)
    else:
        print(f"✗ Input path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Doxygen Source Code Patcher")
    parser.add_argument("--input", required=True, help="Path to the file or directory to patch")
    parser.add_argument("--ci", action="store_true", help="Modify files directly (In-place) instead of creating a .tmp directory")
    parser.add_argument("--output", help="Alternative output file name or directory name")
    parser.add_argument("--remote-repository-path", help="Path to the remote repository used for generating the link comment")
    
    args = parser.parse_args()
    process_path(args.input, args.ci, args.output, args.remote_repository_path)

if __name__ == "__main__":
    main()

