#!/usr/bin/env python3
"""Plot pairwise_report summary rates, without recomputing or pooling judgments.

plot_pairwise(summary, out) accepts the decoded summary or its JSON path and
returns eight paths: pairwise-{categories,dimensions}-{light,dark}.{svg,png}.
Unknown/ambiguous split names fail explicitly; missing cells remain NA. Category
counts are shown only when all displayed, available cells have the same case
count, including both splits. Counts are per split, never summed across models.
Requires matplotlib. No model calls or changes to input artifacts.
"""
import argparse
import json
import math
from numbers import Real
from pathlib import Path
import re

try:
    from .plot_matrix import ORDER, LABELS
except ImportError:
    from plot_matrix import ORDER, LABELS

CATEGORIES = [('overall', 'Overall'), ('ordinary', 'Ordinary prose'),
              ('research', 'Research prose'), ('argument', 'Argument'),
              ('proof', 'Proofs'), ('control', 'Controls')]
DIMENSIONS = [('overall', 'Overall'), ('meaning', 'Meaning'),
              ('naturalness', 'Naturalness'), ('progression', 'Progression'),
              ('voice', 'Voice'), ('proof', 'Proof')]


def _split_rows(summary):
    """Use split semantics rather than JSON insertion/alphabetical order."""
    found = {}
    for name, groups in summary.items():
        key = name.lower().replace('_', '-').replace(' ', '-')
        if key in ('is', 'in-sample', 'development', 'dev', 'train', 'training', 'tune'):
            split = 'IS'
        elif key in ('oos', 'out-of-sample', 'test', 'testing', 'holdout', 'held-out') or re.fullmatch(r'(?:heldout|holdout|held-out)(?:-?\d+)?', key):
            split = 'OOS'
        else:
            raise ValueError(f'Unknown split {name!r}; use development/heldout or IS/OOS')
        if split in found:
            raise ValueError(f'Multiple {split} splits cannot be pooled from aggregates')
        if not isinstance(groups, dict):
            raise ValueError(f'Split {name!r} must map configs to aggregates')
        found[split] = groups
    # A missing split is explicitly displayed as NA, never relabeled.
    return [('IS', found.get('IS', {})), ('OOS', found.get('OOS', {}))]


def _cell(groups, config, section, metric):
    group = groups.get(config)
    if group is None:
        return None
    if not isinstance(group, dict):
        raise ValueError(f'Invalid config aggregate for {config}')
    if metric == 'overall':
        return group.get('overall')
    section_data = group.get(section)
    if section_data is None:
        return None
    if not isinstance(section_data, dict):
        raise ValueError(f'Invalid {section} for {config}')
    return section_data.get(metric)


def _percentage(cell):
    if cell is None or (isinstance(cell, str) and cell == 'NA'):
        return None
    if not isinstance(cell, dict):
        raise ValueError('Metric must be an aggregate object, null, or NA')
    preference = cell.get('preference')
    if preference is None or (isinstance(preference, str) and preference == 'NA'):
        return None
    if isinstance(preference, bool) or not isinstance(preference, Real) or not math.isfinite(preference) or not 0 <= preference <= 1:
        raise ValueError(f'Preference must be a finite fraction in [0, 1], got {preference!r}')
    if cell.get('cases') == 0:
        return None
    return 100 * preference


def _category_label(rows, metric, label):
    if metric == 'overall':
        return label
    counts = []
    for _, groups in rows:
        row_counts = []
        for config in ORDER:
            cell = _cell(groups, config, 'categories', metric)
            if _percentage(cell) is None:
                continue
            count = cell.get('cases')
            if type(count) is not int or count <= 0:
                return label
            row_counts.append(count)
        if not row_counts:
            return label
        counts.extend(row_counts)
    return f'{label} ({counts[0]})' if len(set(counts)) == 1 else label


def plot_pairwise(summary, out, show_counts=False):
    """Write both themes/formats for category and dimension heatmaps; return paths."""
    if isinstance(summary, (str, Path)):
        summary = json.loads(Path(summary).read_text(encoding='utf-8'))
    if not isinstance(summary, dict) or not summary:
        raise ValueError('Expected a nonempty pairwise_report summary object')
    rows = _split_rows(summary)
    # Validate and extract before writing any figures. Preserve report case weights.
    matrices = {}
    for section, metrics in (('categories', CATEGORIES), ('dimensions', DIMENSIONS)):
        matrices[section] = [
            [[_percentage(_cell(groups, config, section, metric)) for config in ORDER]
             for _, groups in rows]
            for metric, _ in metrics
        ]

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm, to_rgba
    from matplotlib.patches import Patch, Rectangle

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    norm = TwoSlopeNorm(vmin=0, vcenter=50, vmax=100)
    cmap = LinearSegmentedColormap.from_list('pairwise', ['#b84a48', '#f2f2f2', '#1c5cab'], N=257)
    xs, x = [], 0
    for config in ORDER:
        if config.endswith('-all') or config == 'all':
            x += .22
        xs.append(x)
        x += 1
        if config.endswith('-all'):
            x += .22
    outputs = []
    for mode in ('light', 'dark'):
        bg, fg = ('#ffffff', '#20252b') if mode == 'light' else ('#1a1a19', '#f0efec')
        missing = '#ececea' if mode == 'light' else '#44443f'
        style = {'font.size': 10, 'font.family': 'DejaVu Sans', 'svg.fonttype': 'none',
                 'svg.hashsalt': 'pairwise-heatmaps-v1', 'text.color': fg,
                 'axes.labelcolor': fg, 'xtick.color': fg, 'ytick.color': fg,
                 'figure.facecolor': bg, 'axes.facecolor': bg}
        for section, metrics in (('categories', CATEGORIES), ('dimensions', DIMENSIONS)):
            with plt.rc_context(style):
                fig = plt.figure(figsize=(16.5, 8.2))
                try:
                    ax = fig.add_axes([.18, .17, .80, .69])
                    yticks, ylabels = [], []
                    for mi, (metric, label) in enumerate(metrics):
                        if section == 'categories':
                            label = _category_label(rows, metric, label)
                        for si, (split, groups) in enumerate(rows):
                            y = mi * 2.6 + si
                            yticks.append(y + .5)
                            counts = [cell.get('cases', 0) for config in ORDER
                                      if (cell := _cell(groups, config, section, metric))]
                            count = str(min(counts)) if counts and min(counts) == max(counts) else (
                                f'{min(counts)}–{max(counts)}' if counts else '0')
                            ylabels.append(f'{split} ({count})' if show_counts else split)
                            for ci, config in enumerate(ORDER):
                                value = matrices[section][mi][si][ci]
                                color = missing if value is None else cmap(norm(value))
                                ax.add_patch(Rectangle((xs[ci] + .025, y + .025), .95, .95,
                                                       facecolor=color, edgecolor='none'))
                                rgba = to_rgba(color)
                                lum = .2126 * rgba[0] + .7152 * rgba[1] + .0722 * rgba[2]
                                ink = '#ffffff' if lum < .5 else '#17212b'
                                ax.text(xs[ci] + .5, y + .5, 'NA' if value is None else f'{value:.1f}',
                                        ha='center', va='center', fontsize=9.2, color=ink,
                                        fontweight='bold' if config.endswith('-all') or config == 'all' else 'normal')
                        ax.text(-1.12 if show_counts else -.65, mi * 2.6 + 1, label,
                                ha='right', va='center', color=fg)
                    ax.set_xlim(-.04, x + .04)
                    ax.set_ylim((len(metrics) - 1) * 2.6 + 2.1, -.2)
                    ax.set_xticks([v + .5 for v in xs], LABELS)
                    ax.xaxis.tick_top()
                    ax.tick_params(length=0, pad=9)
                    ax.set_yticks(yticks, ylabels)
                    ax.tick_params(axis='y', pad=5)
                    ax.set_xlabel('Model and reasoning effort', labelpad=12)
                    ax.xaxis.set_label_position('top')
                    for spine in ax.spines.values():
                        spine.set_visible(False)
                    cax = fig.add_axes([.31, .075, .42, .018])
                    cb = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), cax=cax,
                                      orientation='horizontal', ticks=[0, 25, 50, 75, 100])
                    cb.set_label('Tie-adjusted candidate preference (%)')
                    cb.outline.set_edgecolor(fg)
                    if any(v is None for matrix in matrices[section] for row in matrix for v in row):
                        fig.legend(handles=[Patch(facecolor=missing, label='NA: missing / not applicable')],
                                   loc='center left', bbox_to_anchor=(.75, .075), frameon=False,
                                   labelcolor=fg, fontsize=9)
                    for suffix in ('svg', 'png'):
                        path = out / f'pairwise-{section}-{mode}.{suffix}'
                        fig.savefig(path, dpi=140, facecolor=bg, bbox_inches='tight', pad_inches=.12,
                                    metadata={'Date': None} if suffix == 'svg' else None)
                        if suffix == 'svg':
                            text = path.read_text(encoding='utf-8')
                            path.write_text('\n'.join(line.rstrip() for line in text.splitlines()) + '\n', encoding='utf-8')
                        outputs.append(path)
                finally:
                    plt.close(fig)
    return outputs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    for path in plot_pairwise(args.summary, args.out):
        print(path)


if __name__ == '__main__':
    main()
