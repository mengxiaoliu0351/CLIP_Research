"""Run in Kaggle to export actual experiment files without running a model."""
import hashlib
import json
import os
from pathlib import Path
import zipfile


def main():
    root = Path(os.environ.get('CLIP_EXPORT_ROOT', '/kaggle/working/clip_retrieval'))
    required = ['cache/image_features_fp32.pt', 'results/baseline_val.json',
                'results/final_test/completed.json',
                'results/complexity/params_and_compute.csv',
                'results/complexity/inference_speed.csv']
    for seed in (42, 43, 44):
        required.extend([
            f'results/B_projection_seed{seed}/best_projection.pt',
            f'results/C_lora_r8_seed{seed}/best_lora.pt',
            f'results/B_projection_seed{seed}/summary.json',
            f'results/C_lora_r8_seed{seed}/summary.json',
            f'cache/sampling_seed{seed}.npz',
        ])
    for name in ('fig01_training_and_validation', 'fig02_test_bidirectional_recall',
                 'fig03_trainable_parameters_vs_test_mR', 'fig04_encoding_latency_and_throughput'):
        required.append(f'results/paper_figures/{name}.pdf')
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise RuntimeError(f'Missing required files under {root}: {missing}')

    annotation_path = os.environ.get('CLIP_ANNOTATION_PATH')
    if annotation_path:
        annotation_path = Path(annotation_path)
    else:
        found = sorted(Path('/kaggle/input').rglob('dataset_flickr30k.json'))
        if len(found) != 1:
            raise RuntimeError('Set CLIP_ANNOTATION_PATH to the annotation JSON.')
        annotation_path = found[0]
    with open(annotation_path, encoding='utf-8') as f:
        annotation = json.load(f)

    files = sorted(p for p in root.rglob('*') if p.is_file())
    output = root.parent / 'CLIP_Flickr30k_experiment_artifacts.zip'
    number = 2
    while output.exists():
        output = root.parent / f'CLIP_Flickr30k_experiment_artifacts_{number}.zip'
        number += 1

    manifest = []
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
        for index, path in enumerate(files, 1):
            relative = path.relative_to(root)
            with open(path, 'rb') as f:
                digest = hashlib.file_digest(f, 'sha256').hexdigest()
            archive.write(path, arcname=str(Path(root.name) / relative))
            manifest.append({'path': relative.as_posix(), 'size': path.stat().st_size,
                             'sha256': digest})
            if index % 10 == 0 or index == len(files):
                print(f'Packed {index}/{len(files)} files', flush=True)
        archive.writestr(f'{root.name}/artifact_manifest_sha256.json',
                         json.dumps(manifest, indent=2))
        for split in ('train', 'val', 'test'):
            records = sorted((x for x in annotation['images'] if x['split'] == split),
                             key=lambda x: x['filename'])
            id_text = '\n'.join(str(x['imgid']) for x in records) + '\n'
            mapping = 'image_id\tfilename\n' + ''.join(
                f"{x['imgid']}\t{x['filename']}\n" for x in records)
            archive.writestr(f'{root.name}/split_manifests/{split}_imgids.txt', id_text)
            archive.writestr(f'{root.name}/split_manifests/{split}_images.tsv', mapping)

    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f'ZIP integrity failure: {bad}')

    print('Archive verified:', output)
    print(f'Size: {output.stat().st_size / 1024**2:.2f} MiB')
    print('Download the archive and preserve a saved notebook version with output files.')


if __name__ == '__main__':
    main()
