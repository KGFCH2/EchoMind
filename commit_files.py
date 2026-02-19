#!/usr/bin/env python3
"""Stage and commit each untracked file individually with human like messages

This script finds untracked files (git ls-files --others --exclude-standard)
and for each file performs `git add <file>` and `git commit -m "<Message>"`.

Messages are simple single phrases starting with a capital letter and contain
no punctuation as requested by the user.
"""
import subprocess
import os


def run(cmd):
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def get_untracked_files():
    p = run(["git", "ls-files", "--others", "--exclude-standard"])
    if p.returncode != 0:
        print("Failed to list untracked files", p.stderr)
        return []
    files = [l for l in p.stdout.splitlines() if l.strip()]
    return files


def make_message(path):
    base = os.path.basename(path)
    low = base.lower()
    # Common special cases
    if low.startswith("readme"):
        return "Add README"
    if low == "license" or low == "license.txt":
        return "Add LICENSE"
    if low == "requirements.txt":
        return "Add requirements file"
    if low == ".env.example":
        return "Add env example"
    # Python modules and handlers
    name, ext = os.path.splitext(base)
    cleaned = name.replace('_', ' ').replace('-', ' ').strip()
    cleaned = cleaned.capitalize()
    return f"Add {cleaned}"


def main():
    files = get_untracked_files()
    if not files:
        print("No untracked files to commit")
        return

    for f in files:
        # Skip __pycache__ directories and compiled files
        if "__pycache__" in f or f.endswith(".pyc"):
            continue
        print(f"Adding and committing {f}")
        a = run(["git", "add", f])
        if a.returncode != 0:
            print(f"Failed to add {f}", a.stderr)
            continue
        msg = make_message(f)
        c = run(["git", "commit", "-m", msg])
        if c.returncode != 0:
            print(f"Failed to commit {f}", c.stderr)
        else:
            print(f"Committed {f} with message '{msg}'")


if __name__ == '__main__':
    main()
