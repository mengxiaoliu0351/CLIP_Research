"""Rebuild paper tables from saved measurements, without model inference."""
from pathlib import Path
import csv
import json
import re
import statistics

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def read_json(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))


def write_json(name, value):
    (ROOT / 'data' / name).write_text(json.dumps(value, indent=2), encoding='utf-8')


def set_rows(stem, rows):
    """Keep each complete tabular in one input file for TeX compatibility."""
    body = '\n'.join(rows) + '\n'
    (ROOT / 'tables' / f'{stem}_rows.tex').write_text(body, encoding='utf-8')
    path = ROOT / 'tables' / f'{stem}.tex'
    source = path.read_text(encoding='utf-8')
    pattern = r'(?<=% BEGIN GENERATED ROWS\n).*?(?=% END GENERATED ROWS)'
    source, count = re.subn(pattern, lambda _: body, source, flags=re.DOTALL)
    assert count == 1, f'Missing generated-row markers: {path.name}'
    path.write_text(source, encoding='utf-8')


def main():
    runs = read_json('final_test.json')['runs']
    records = read_json('experiment_records.json')
    stats = {}
    for group in ('A', 'B', 'C'):
        selected = [run for run in runs if run['group'] == group]
        stats[group] = {}
        for direction in ('I2T', 'T2I'):
            for metric in ('R@1', 'R@5', 'R@10', 'MedianRank'):
                values = [run['metrics'][direction][metric] for run in selected]
                stats[group][f'{direction}_{metric}'] = {
                    'mean': statistics.mean(values),
                    'sd': statistics.stdev(values) if len(values) > 1 else None,
                }
        values = [run['metrics']['mR'] for run in selected]
        stats[group]['mR'] = {
            'mean': statistics.mean(values),
            'sd': statistics.stdev(values) if len(values) > 1 else None,
        }
        if group != 'A':
            histories = [entry for label, entry in records['experiments'].items()
                         if label.startswith(group + '_')]
            stats[group]['training'] = {
                'mean_epoch_seconds': statistics.mean(
                    row['train_seconds'] for entry in histories for row in entry['history']),
                'peak_allocated_gib': max(
                    row['peak_allocated_gib'] for entry in histories for row in entry['history']),
            }

    def cell(group, key, median=False):
        value = stats[group][key]
        if median:
            return f"{value['mean']:.0f}"
        if value['sd'] is None:
            return f"{value['mean']:.2f}"
        return f"${value['mean']:.2f} \\pm {value['sd']:.2f}$"

    rows = []
    for group, label in [('A', 'A: Zero-shot'), ('B', 'B: Projection-only'),
                         ('C', 'C: LoRA + projection')]:
        values = [label]
        for direction in ('I2T', 'T2I'):
            values.extend(cell(group, f'{direction}_{metric}', metric == 'MedianRank')
                          for metric in ('R@1', 'R@5', 'R@10', 'MedianRank'))
        values.append(cell(group, 'mR'))
        rows.append(' & '.join(values) + r' \\')
    set_rows('main_results', rows)

    rows = []
    paired = []
    for seed in (42, 43, 44):
        b = next(run['metrics']['mR'] for run in runs
                 if run['group'] == 'B' and run['seed'] == seed)
        c = next(run['metrics']['mR'] for run in runs
                 if run['group'] == 'C' and run['seed'] == seed)
        paired.append(c - b)
        rows.append(f'{seed} & {b:.2f} & {c:.2f} & +{c-b:.2f}' + r' \\')
    set_rows('paired_results', rows)

    with (ROOT / 'data/params_and_compute.csv').open(newline='', encoding='utf-8') as stream:
        params = list(csv.DictReader(stream))
    rows = []
    for row in params:
        group = row['Group']
        timing = '--' if group == 'A' else f"{stats[group]['training']['mean_epoch_seconds']:.2f}"
        memory = '--' if group == 'A' else f"{stats[group]['training']['peak_allocated_gib']:.3f}"
        values = [group, f"{int(row['TotalParams'])/1e6:.3f}",
                  f"{int(row['TrainableParams'])/1000:.3f}",
                  f"{float(row['TrainablePercent']):.4f}",
                  f"{float(row['Image_GMACs']):.4f}",
                  f"{float(row['Text77_GMACs']):.4f}",
                  f"{float(row['Pair_GFLOPs']):.4f}", timing, memory]
        rows.append(' & '.join(values) + r' \\')
    set_rows('complexity', rows)

    with (ROOT / 'data/inference_speed.csv').open(newline='', encoding='utf-8') as stream:
        speeds = list(csv.DictReader(stream))
    rows = [f"{row['Group']} & {float(row['T2I_cached_Top5_mean_ms']):.4f} & "
            f"{float(row['I2T_cached_Top5_mean_ms']):.4f}" + r' \\' for row in speeds]
    set_rows('cached_latency', rows)

    arrays = {}
    for name in ('A_baseline', 'C_seed42'):
        with np.load(ROOT / f'data/{name}_ranks.npz', allow_pickle=False) as archive:
            arrays[name] = {direction: archive[direction].copy()
                            for direction in ('I2T', 'T2I')}
    transitions = []
    for direction in ('I2T', 'T2I'):
        a = arrays['A_baseline'][direction] == 1
        c = arrays['C_seed42'][direction] == 1
        transitions.append({
            'direction': direction, 'queries': len(a),
            'both_top1': int((a & c).sum()), 'A_only_top1': int((a & ~c).sum()),
            'C_only_top1': int((~a & c).sum()), 'neither_top1': int((~a & ~c).sum()),
        })
    rows = [f"{row['direction']} & {row['both_top1']} & {row['A_only_top1']} & "
            f"{row['C_only_top1']} & {row['neither_top1']}" + r' \\'
            for row in transitions]
    set_rows('query_transition', rows)
    write_json('statistics.json', stats)
    write_json('query_transitions_seed42.json', {
        'source': 'saved test rank arrays; no new inference', 'rows': transitions})
    print('Rebuilt five tables from saved records. No training or evaluation was run.')
    print(f'Paired C-B mR: {statistics.mean(paired):.6f} +/- '
          f'{statistics.stdev(paired):.6f} percentage points.')


if __name__ == '__main__':
    main()
