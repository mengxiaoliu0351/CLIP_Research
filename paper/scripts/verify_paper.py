"""Audit paper evidence and compiled output; never trains or runs an encoder."""
from pathlib import Path
import csv
import json
import math
import re
import statistics
import unicodedata

import fitz
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def read_json(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))


def close(actual, expected, message):
    assert math.isclose(float(actual), float(expected), rel_tol=1e-10, abs_tol=1e-8), message


def main():
    checks = []
    final = read_json('final_test.json')
    runs = final['runs']
    assert len(runs) == 7
    with (ROOT / 'data/test_per_run.csv').open(newline='', encoding='utf-8') as stream:
        csv_rows = list(csv.DictReader(stream))
    for run, row in zip(runs, csv_rows, strict=True):
        assert row['Model'] == run['label']
        recalls = []
        for direction in ('I2T', 'T2I'):
            metrics = run['metrics'][direction]
            assert 0 <= metrics['R@1'] <= metrics['R@5'] <= metrics['R@10'] <= 100
            for key in ('R@1', 'R@5', 'R@10', 'MedianRank'):
                close(row[f'{direction}_{key}'], metrics[key], 'CSV/JSON metric mismatch')
            recalls.extend(metrics[key] for key in ('R@1', 'R@5', 'R@10'))
        close(run['metrics']['mR'], statistics.mean(recalls), 'mR must average six Recalls')
        close(row['mR'], run['metrics']['mR'], 'CSV mR mismatch')
    checks.append('All seven final-test records agree with CSV and six-Recall mR definition.')

    stats = read_json('statistics.json')
    paired = []
    for group in ('B', 'C'):
        selected = [run for run in runs if run['group'] == group]
        assert sorted(run['seed'] for run in selected) == [42, 43, 44]
        values = [run['metrics']['mR'] for run in selected]
        close(stats[group]['mR']['mean'], statistics.mean(values), 'Wrong mR mean')
        close(stats[group]['mR']['sd'], statistics.stdev(values), 'Wrong sample SD')
    for seed in (42, 43, 44):
        b = next(run for run in runs if run['group'] == 'B' and run['seed'] == seed)
        c = next(run for run in runs if run['group'] == 'C' and run['seed'] == seed)
        paired.append(c['metrics']['mR'] - b['metrics']['mR'])
    close(final['paired_mR_delta_mean_pp'], statistics.mean(paired), 'Wrong paired gain')
    close(final['paired_mR_delta_sample_std_pp'], statistics.stdev(paired), 'Wrong paired SD')
    checks.append('Three-seed mR mean, sample SD, and paired C-B gain reproduce saved values.')

    records = read_json('experiment_records.json')['experiments']
    assert len(records) == 6
    for seed in (42, 43, 44):
        selected = [entry for entry in records.values() if entry['seed'] == seed]
        assert len(selected) == 2
        for key in ('annotation_sha256', 'base_weight_sha256', 'sampling_plan_sha256',
                    'epochs', 'batch_size', 'learning_rate', 'weight_decay'):
            assert selected[0][key] == selected[1][key], f'Paired controls differ: {key}'
        for entry in selected:
            assert len(entry['history']) == 5 and entry['best_epoch'] == 5
            assert all(row['skipped_updates'] == 0 for row in entry['history'])
            assert all(math.isfinite(row['train_loss']) for row in entry['history'])
            best = max(entry['history'], key=lambda row: row['val']['mR'])
            assert best['epoch'] == entry['best_epoch']
    checks.append('Six saved five-epoch histories use paired data, weights, sampling, and hyperparameters.')

    for name in ('A_baseline', 'C_seed42'):
        run = next(run for run in runs if run['label'] == name)
        with np.load(ROOT / f'data/{name}_ranks.npz', allow_pickle=False) as archive:
            for direction, count in (('I2T', 1000), ('T2I', 5000)):
                ranks = archive[direction]
                assert ranks.shape == (count,) and ranks.min() >= 1
                for k in (1, 5, 10):
                    close((ranks <= k).mean() * 100, run['metrics'][direction][f'R@{k}'],
                          'Saved query ranks do not reproduce Recall')
                close(np.median(ranks), run['metrics'][direction]['MedianRank'],
                      'Saved ranks do not reproduce median')
    checks.append('Saved A/C seed42 query ranks reproduce full-gallery Recall and MedianRank.')

    compute = read_json('compute_counting_details.json')
    rows = {row['Group']: row for row in compute['results']}
    assert rows['A']['TrainableParams'] == 0
    assert rows['B']['TrainableParams'] == 512 * 512
    assert rows['C']['TrainableParams'] == 512 * 512 + 24 * 8 * 1024
    assert rows['C']['TotalParams'] - rows['A']['TotalParams'] == 196608
    extra = (rows['C']['Text77_GMACs'] - rows['A']['Text77_GMACs']) * 1e9
    close(extra, 24 * 77 * 8 * 1024, 'Wrong unmerged LoRA MAC delta')
    for row in rows.values():
        close(row['Pair_GFLOPs'], 2 * (row['Image_GMACs'] + row['Text77_GMACs']),
              'Pair FLOPs convention mismatch')
    checks.append('Parameter counts and theoretical MAC/FLOP arithmetic are consistent.')

    cases = read_json('qualitative_cases.json')['cases']
    for case in cases:
        direction = case['direction']
        field = 'ground_truth_rank' if direction == 'T2I' else 'best_ground_truth_rank'
        for name in ('A_baseline', 'C_seed42'):
            with np.load(ROOT / f'data/{name}_ranks.npz', allow_pickle=False) as archive:
                expected = int(archive[direction][case['query_index']])
            assert case['models'][name][field] == expected
    checks.append('Qualitative-case ground-truth ranks match saved final-test arrays.')

    tex = (ROOT / 'main.tex').read_text(encoding='utf-8')
    bib = (ROOT / 'references.bib').read_text(encoding='utf-8')
    keys = set(re.findall(r'@\w+\s*\{\s*([^,]+),', bib))
    cited = {key.strip() for group in re.findall(r'\\cite\{([^}]+)\}', tex)
             for key in group.split(',')}
    assert cited == keys and len(cited) == 12
    labels = set(re.findall(r'\\label\{([^}]+)\}', tex))
    refs = set(re.findall(r'\\ref\{([^}]+)\}', tex))
    assert refs <= labels
    assert tex.count('\\begin{figure*}') == 5
    assert tex.count('\\begin{table}') + tex.count('\\begin{table*}') == 6
    for name in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', tex):
        assert (ROOT / 'figures' / name).is_file(), name
    log = (ROOT / 'main.log').read_text(encoding='utf-8')
    assert 'Overfull \\hbox' not in log
    assert not re.search(r'Citation .* undefined|Reference .* undefined|Undefined control sequence', log)
    checks.append('All twelve references, labels, five figures, and six tables resolve; no overfull hbox.')

    with fitz.open(ROOT / 'main.pdf') as pdf:
        page_count = len(pdf)
        assert 6 <= page_count <= 9
        assert all(tuple(round(v) for v in page.rect[2:]) == (612, 792) for page in pdf)
        fonts = [font for page in pdf for font in page.get_fonts(full=True)]
        assert not any(font[2] == 'Type3' for font in fonts)
        assert all(pdf.extract_font(font[0])[3] for font in fonts if font[0] > 0)
        text = unicodedata.normalize('NFKC', '\n'.join(page.get_text() for page in pdf))
        assert 'Author Name' in text and 'Email to be confirmed' in text
        for token in ('89.21', '458,752', '31,014', '31,783', '1.3878'):
            assert token in text, token
    checks.append('Compiled PDF has letter pages, embedded fonts, no Type3 fonts, and author placeholders.')

    report = {
        'status': 'passed', 'page_count': page_count, 'figures': 5, 'tables': 6,
        'references': 12, 'training_runs': 6, 'training_epochs': 30,
        'test_records': 7, 'checks': checks,
        'scope': 'Saved-evidence and compiled-document checks. No new training or test inference.',
        'author_information': 'Placeholders pending user confirmation.',
        'build_engine': 'Tectonic 0.17.0',
    }
    (ROOT / 'verification_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
