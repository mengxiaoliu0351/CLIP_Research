"""CPU-only checks for the organized source and captured experiment evidence."""
import ast
import hashlib
import json
from pathlib import Path

import nbformat
import numpy as np


def main():
    root = Path(__file__).resolve().parents[1]
    report = {'scope': 'CPU syntax/schema/metric/evidence checks; no GPU model execution',
              'notebooks': [], 'checks': []}
    snapshot = json.loads((root / 'source_snapshot.json').read_text(encoding='utf-8'))
    original = snapshot['cells']

    for path in sorted((root / 'notebooks').glob('*.ipynb')):
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        cells = [c for c in notebook.cells if c.cell_type == 'code']
        for index, cell in enumerate(cells):
            compile(cell.source, f'{path.name}:code{index}', 'exec')
        report['notebooks'].append({'file': path.name, 'code_cells': len(cells),
                                    'syntax': 'passed', 'schema': 'passed'})
        if path.name.startswith('01_'):
            assert len(cells) == 24
            for index, cell in enumerate(cells):
                assert cell.source == original[index]['source']
                assert len(cell.outputs) == original[index]['outputs']
                assert cell.execution_count == original[index]['execution_count']
            images = sum('image/png' in output.get('data', {})
                         for cell in cells for output in cell.get('outputs', []))
            assert images == 10
        else:
            assert all(not c.outputs and c.execution_count is None for c in cells)
            for cell in cells:
                assert '/kaggle/input/datasets/' not in cell.source
    report['checks'].append('24 original code cells and output counts preserved; 10 embedded figures')

    # Executes only the original NumPy metric checks; no image or model is synthesized.
    namespace = {}
    exec(compile(original[4]['source'], 'original_retrieval_metric_checks', 'exec'), namespace)
    assert namespace['boundary']['MedianRank'] == 5.5
    report['checks'].append('I2T multi-positive minimum rank, T2I mapping, R@K boundaries, even median and reordered captions')

    payload = json.loads((root / 'evidence/saved_experiment_records.json').read_text(encoding='utf-8'))
    experiments = payload['experiments']
    assert set(experiments) == {f'{g}_seed{s}' for g in ('B', 'C') for s in (42, 43, 44)}
    for label, experiment in experiments.items():
        assert len(experiment['history']) == 5
        assert experiment['best_epoch'] == 5
        expected = 262144 if label.startswith('B') else 458752
        assert experiment['trainable_params'] == expected
        assert experiment['epochs'] == 5 and experiment['batch_size'] == 64
        assert experiment['learning_rate'] == 1e-5 and experiment['weight_decay'] == .01
        assert all(item['skipped_updates'] == 0 for item in experiment['history'])
    for seed in (42, 43, 44):
        assert experiments[f'B_seed{seed}']['sampling_plan_sha256'] == experiments[f'C_seed{seed}']['sampling_plan_sha256']
    report['checks'].append('Six saved summaries contain 30 epochs; paired sampling hashes and controlled hyperparameters match')

    runs = json.loads((root / 'evidence/test_results_from_notebook.json').read_text(encoding='utf-8'))['runs']
    assert len(runs) == 7
    for group, expected_mean in [('A', 84.12666666666667), ('B', 87.81888888888888), ('C', 89.20666666666666)]:
        values = [run['metrics']['mR'] for run in runs if run['group'] == group]
        assert len(values) == (1 if group == 'A' else 3)
        assert np.isclose(np.mean(values), expected_mean, atol=1e-10)
    differences = [next(r['metrics']['mR'] for r in runs if r['group']=='C' and r['seed']==s)
                   - next(r['metrics']['mR'] for r in runs if r['group']=='B' and r['seed']==s)
                   for s in (42,43,44)]
    assert np.isclose(np.mean(differences), 1.38777777777778)
    assert all(delta > 0 for delta in differences)
    report['checks'].append('Seven captured test results and paired C-B deltas agree with reported values')

    provenance = json.loads((root / 'source_provenance.json').read_text(encoding='utf-8'))
    for item in provenance:
        assert hashlib.sha256(original[item['source_cell_index']]['source'].encode()).hexdigest() == item['original_source_sha256']
        notebook = json.loads((root / 'notebooks' / item['notebook']).read_text(encoding='utf-8'))
        source = notebook['cells'][item['cell_index']]['source']
        assert hashlib.sha256(source.encode()).hexdigest() == item['organized_source_sha256']
    for path in (root / 'tools').glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    report['checks'].append('Organized source hashes match provenance; helper scripts parse')
    restore_report = root / 'evidence/restore_runtime_validation.json'
    if restore_report.exists():
        restore = json.loads(restore_report.read_text(encoding='utf-8'))
        exported = nbformat.read(root / 'evidence/restore_source_only_export.ipynb', as_version=4)
        nbformat.validate(exported)
        exported_sources = [c.source for c in exported.cells if c.cell_type == 'code']
        assert len(exported_sources) == 12
        filtered = [s for s in exported_sources if '关键成果完整性检查通过，未重新执行测试。' not in s]
        entry = nbformat.read(root / 'notebooks/03_restore_saved_results.ipynb', as_version=4)
        assert filtered == [c.source for c in entry.cells if c.cell_type == 'code']
        assert restore['validation']['max_absolute_metric_difference'] == 0
        report['gpu_validation'] = {
            'restore': 'Validated through user-reported Kaggle console outputs; 11 organized code cells match the source-only export.',
            'source_export_embedded_outputs': 0,
            'full_training': 'Static/CPU checks only; not rerun in a new Kaggle session.',
        }
        report['checks'].append('Uploaded restore source matches the validated entry; runtime evidence provenance is explicit')
    else:
        report['gpu_validation'] = 'Not executed for the newly organized entry notebooks. Original captured GPU runs are preserved in the record.'
    (root / 'verification_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
