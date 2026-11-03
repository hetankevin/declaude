#!/usr/bin/env python3
"""Install the skill for the current user; existing copies are backed up."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--apps', nargs='+', choices=('claude', 'codex', 'antigravity'),
                        default=['claude', 'codex', 'antigravity'],
                        help='applications to install for (default: all three)')
    parser.add_argument('--personal', action='store_true', help='include the untracked personal paper reading list')
    args = parser.parse_args()
    source = Path(__file__).resolve().parent / 'skill'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    roots = {'claude': '.claude', 'codex': '.codex', 'antigravity': '.gemini/config'}
    applications = [roots[name] for name in dict.fromkeys(args.apps)]
    # Refresh existing discovery copies so they cannot shadow the new install.
    if 'codex' in args.apps and (args.home / '.agents/skills/declaude').exists():
        applications.append('.agents')
    if 'antigravity' in args.apps:
        for legacy in ('.gemini/antigravity', '.gemini/antigravity-cli', '.gemini'):
            if (args.home / legacy / 'skills/declaude').exists():
                applications.append(legacy)
    for application in applications:
        destination = args.home / application / 'skills' / 'declaude'
        if destination.is_symlink() or any(p.is_symlink() for p in destination.rglob('*')):
            raise SystemExit(f'Refusing to write through a symlink: {destination}')
    for application in applications:
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
