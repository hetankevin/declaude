#!/usr/bin/env python3
"""Install the skill for the current user; existing copies are backed up."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--personal', action='store_true', help='include the untracked personal paper reading list')
    args = parser.parse_args()
    source = Path(__file__).resolve().parent / 'skill'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    for application in ('.claude', '.codex'):
        destination = args.home / application / 'skills' / 'declaude'
        if destination.is_symlink():
            raise SystemExit(f'Refusing to replace symlink: {destination}')
        if destination.exists():
            backup = args.home / application / 'skill-backups' / f'declaude-{stamp}'
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(destination, backup)
        destination.mkdir(parents=True, exist_ok=True)
        for item in source.rglob('*'):
            if not item.is_file() or '__pycache__' in item.parts:
                continue
            if item.name.endswith('.local.md') and not args.personal:
                continue
            target = destination / item.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
        print(f'Installed {destination}')


if __name__ == '__main__':
    main()
