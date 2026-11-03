# Code and artifact availability

## Scope

This package supplies a manuscript, a Chinese project report, saved source data and an existing code archive. It does not claim that saved-data checks rerun training or model inference. The original model, processor and image dataset remain separate inputs.

## CLIP_Flickr30k_code_package_20261030.zip

Size: 7,412,313 bytes

SHA256: `234977b1eeeb1b35d9d51ba8c7ca09fa4aa2f9a96898b1ac10de19064bdb36a8`

Notebook entry points

- `clip_flickr30k_code_package/evidence/restore_source_only_export.ipynb`
- `clip_flickr30k_code_package/notebooks/01_experiment_record.ipynb`
- `clip_flickr30k_code_package/notebooks/02_train_from_scratch.ipynb`
- `clip_flickr30k_code_package/notebooks/03_restore_saved_results.ipynb`

## CLIP_Flickr30k_experiment_artifacts.zip

Size: 107,005,581 bytes

SHA256: `62db2660846b8a69dc63166e66b0d9d0c594c1e12ce2cdd3080852947b2bafc7`

## Input mapping

- Annotation: `/kaggle/input/datasets/shtvkumar/karpathy-splits/dataset_flickr30k.json`
- Images: `/kaggle/input/datasets/mengxiao0351/flickr30k-images-local/flickr30k-images`
- Base model: `/kaggle/input/datasets/mengxiao0351/clip-vit-base-patch32-local/clip-vit-base-patch32-local`
- Restore artifact root: archive folder `clip_retrieval_restored`, copied to a writable Kaggle working directory before running the restore notebook.

## Evidence and limits

The original code archive has been unpacked into `code/` in this repository; the original ZIP is not duplicated. Notebook paths listed above are relative to its original archive and map to `code/` here. The 107,005,581-byte experimental archive is the user-downloaded original and is NOT duplicated inside this documents package. It contains the six trained checkpoint deltas and cached experimental outputs; verify its digest above before restoration.

The captured notebook preserves key original outputs. The fresh-training entry was statically checked; the separate restore workflow was run in Kaggle and its validation reproduction was reported in the project record. The source-only restore export is explicitly labeled and is not evidence of newly executed outputs.

Inference and training are not performed during this writing revision. Existing numerical results are recomputed from saved arrays and summaries for consistency.
