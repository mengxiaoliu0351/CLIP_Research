# CLIP–Flickr30k 选题14：代码与实验记录

本包整理截至 **2026-10-30** 的真实实验。原始代码、已有输出和训练历史均有明确来源。模型权重、原图和离线基础模型需要另外挂载；本包不是包含论文及视频的最终完整提交包。

## 先选择入口

| 文件 | 用途 | 是否训练 | 输出情况 |
|---|---|---|---|
| `notebooks/01_experiment_record.ipynb` | 阅读、审查原始实验过程 | 用于阅读，不作为 Run All 入口 | 保留原24个代码单元格及所有已有输出、10张图、六次训练历史 |
| `notebooks/02_train_from_scratch.ipynb` | 在新环境从头复现 | 会执行B/C各3个种子的完整训练 | 新整理入口，未预填执行输出 |
| `notebooks/03_restore_saved_results.ipynb` | 继续已有实验、恢复权重和生成报告 | 不训练 | 已有最终测试和测速结果直接读取；重新核对验证结果 |

**继续当前任务请选择恢复入口。** 从头训练入口留给复现需要，不必为了整理提交材料再训练一次。

两个运行入口使用独立目录，默认分别为：

```text
/kaggle/working/clip_retrieval_reproduction
/kaggle/working/clip_retrieval_restored
```

因此不会直接覆盖原来的 `/kaggle/working/clip_retrieval`。开始运行后应按单元格顺序执行。

## 环境

已完成实验记录的环境：Python 3.13.15，PyTorch 2.11.0+cu128，torchvision 0.26.0+cu128，Transformers 5.16.1，huggingface_hub 1.29.0，Pillow 13.0.0。

还使用 numpy、pandas、matplotlib、tqdm 和 IPython。未记录这些辅助库的精确版本，未虚构版本号。`requirements.txt` 列出已知版本和辅助依赖，供环境核对；Kaggle 离线环境请使用预装依赖，运行过程中不执行联网安装。

Kaggle 选择 T4 GPU，Internet 关闭。虽然机器有两张T4，本实验只使用 **cuda:0 单卡**。训练为FP16 AMP；验证、测试、计算量统计和测速为FP32。没有使用peft。

新Notebook未写入自动挂载的Kaggle数据源元数据，导入后需手动附加输入并启用GPU。

## 必需的三个原始输入

1. Flickr30k图片。31783张原图中，仅使用标注JSON覆盖的31014张；另外769张不参与实验。
2. `dataset_flickr30k.json`。本次文件固定划分为29000张训练、1014张验证、1000张测试，每图5句。按JSON的split读取，不重新随机划分，不根据imgid拼图片文件名。
3. 离线 `openai/clip-vit-base-patch32` 模型与processor文件。

本次已验证的挂载位置：

```text
/kaggle/input/datasets/shtvkumar/karpathy-splits/dataset_flickr30k.json
/kaggle/input/datasets/mengxiao0351/flickr30k-images-local/flickr30k-images
/kaggle/input/datasets/mengxiao0351/clip-vit-base-patch32-local/clip-vit-base-patch32-local
```

模型目录包含 `pytorch_model.bin`、`config.json`、`preprocessor_config.json`、`tokenizer_config.json`、`special_tokens_map.json`、`tokenizer.json`、`vocab.json`、`merges.txt`。

标注SHA256：`db779ee2c5df40c25ff0eebeca464f6124b620cc4a9398650aea71fd1b53d4af`

原始模型SHA256：`a63082132ba4f97a80bea76823f544493bffa8082296d62d71581a4feff1576f`

运行入口的第一个配置单元格会自动查找唯一输入。若路径需要指定，在该单元格设置 `DATA_JSON`、`IMAGE_ROOT`、`CLIP_DIR`、`PROJECT_ROOT`，或通过对应的 `CLIP_ANNOTATION_PATH`、`CLIP_IMAGE_DIR`、`CLIP_MODEL_DIR`、`CLIP_OUTPUT_ROOT` 环境变量设置。只挂载各一份原始输入，避免同名文件歧义。

## 恢复已有实验：当前推荐流程

1. 导入 `03_restore_saved_results.ipynb`。
2. 附加上述三个原始输入，以及**一份完整的已保存Notebook输出**。
3. 已保存输出应包含 `clip_retrieval/cache` 和 `clip_retrieval/results`；仅附加六个小权重文件不足以运行完整恢复流程。
4. 选择T4、关闭Internet，检查第一个配置单元格的路径。
5. 从上到下执行。恢复单元格复制并校验文件；模型单元格加载原始CLIP后注入投影层/LoRA；验证单元格检查与保存指标一致。
6. 若最终测试已有 `completed.json`，展示保存的测试表格；若复杂度或测速CSV已有，展示原记录。绘图与检索样例从缓存重新生成。
7. 完成后使用包含输出文件的Quick Save，并在新版本Output中核实文件。

恢复入口使用原本的验证一致性断言。在不同依赖版本或设备上出现差异时应检查环境、路径和预处理，不能为了通过检查而修改已保存指标。

## 从头复现

1. 导入 `02_train_from_scratch.ipynb`，附加三个原始输入，启用T4，关闭Internet。
2. 默认使用新的 `clip_retrieval_reproduction` 目录。入口会拒绝覆盖非空输出目录；需要另一轮完整复现时使用新的目录名。
3. 从上到下执行数据与指标检查、零样本验证、冻结与梯度检查、图像特征缓存、seed42训练、seed43/44训练、最终测试、检索图、复杂度、测速和汇总绘图。
4. 使用完整候选库计算验证指标，逐种子按验证mR选择训练epoch。固定配置后才进行最终测试。

本项目保存的是最佳训练参数及日志，未保存用于恢复epoch中途训练的optimizer/scaler状态。恢复入口用于已完成实验的继续分析，不声称支持中途训练断点续跑。

## 方法与控制变量

- A：原始CLIP零样本，所有参数冻结。
- B：仅训练 `text_projection`，262144个参数。
- C：12个文本Transformer块的Q/V共24个线性模块添加手写LoRA，r=8、alpha=8，并训练文本投影。LoRA参数196608，总可训练参数458752。
- 所有组视觉塔、视觉投影冻结；B/C从同一原始权重分别开始，不串行继承微调结果；logit_scale冻结。
- 5 epochs、batch=64、AdamW、lr=1e-5、weight_decay=0.01、梯度裁剪1.0、AMP GradScaler初始scale=1024，无学习率调度。最后不足64的batch保留。
- 每个epoch每张训练图恰好一次，并选一条caption。每个种子内B/C共享保存的图片排列和caption抽样计划，避免同图多句进入同一对角对比损失batch。
- 图像预处理确定且视觉分支冻结，所以训练缓存FP32归一化图像特征。缓存准备时间没有包含在记录的每轮训练耗时中。
- 三个种子为42/43/44；B/C全部最佳epoch均为5。未进行r=4/16扫描，参数量图不是rank消融。

## 指标与最终结果

I2T：1000张测试图片查询5000条caption，取五条正确caption中的最小排名。T2I：5000条caption查询1000张去重图片。排名从1开始，同分按候选索引稳定排序，MedianRank使用普通中位数；mR为双向R@1/5/10六项平均。

| 模型 | I2T R@1 (%) | T2I R@1 (%) | 测试mR (%) |
|---|---:|---:|---:|
| A | 79.30 | 58.84 | 84.13 |
| B | 81.10 ± 0.52 | 66.91 ± 0.13 | 87.82 ± 0.14 |
| C | 84.17 ± 0.46 | 68.87 ± 0.27 | 89.21 ± 0.11 |

B/C为三个训练种子的均值±样本标准差(ddof=1)，不是置信区间。C−B配对mR变化为+1.3878±0.0741个百分点。A只有一次确定性零样本评估。

## 计算量和计时口径

图片输入1×3×224×224，文本输入1×77 tokens。计算卷积、线性层、稠密注意力矩阵乘法和未合并LoRA分支，以1 MAC=2 FLOPs。排除偏置/残差加法、激活、归一化、Softmax等，所以这是主要算子的理论计算量。

A/B：图像4.408812 GMACs、文本2.979770 GMACs；C文本2.994909 GMACs。编码一图一句的GFLOPs分别为14.777164、14.777164、14.807441。候选库检索没有计入编码计算量。

测速使用单张T4、FP32、seed42、未合并LoRA。Batch1延迟为预热20次后100次同步墙钟计时均值，包含调用与完成同步开销；吞吐在batch32下预热10次，然后5轮×10次连续前向；缓存Top5检索预热20次、重复200次，轮换64条真实查询，候选库始终完整。

读取文件、图像预处理、tokenization、输入搬运、候选特征预计算、结果传回CPU均在计时之外。图片吞吐单位images/s，文本吞吐单位texts/s。测速重复和训练种子重复是不同统计口径。

## 文件来源与可审查范围

- `01_experiment_record.ipynb`保留原24个代码单元格的内容、输出及执行编号，只插入说明性Markdown。前13格输出在导出前已丢失；最后归档格从保存的summary.json展示六次历史，不把它冒充原始训练stdout。
- `evidence/saved_experiment_records.json`直接取自归档格嵌入的application/json，含六次完整summary及原始验证基线。
- `evidence/test_results_from_notebook.json`从最终测试stdout解析，mR由六项Recall复算。它不是原始`completed.json`文件的字节副本，已注明来源。
- `evidence/*/*.png`从Notebook嵌入输出提取，供审阅；不保证是Kaggle保存的300dpi PNG原件。正式论文优先使用Kaggle `paper_figures` 中的PDF或300dpi PNG。
- `source_snapshot.json`与`source_provenance.json`记录原代码和新入口的来源映射。
- `03_restore_saved_results.ipynb`已在独立Kaggle GPU会话验证：76个文件SHA256匹配，六份权重正常加载，C组seed42全部验证指标差值为0，正确读取保存的测试、计算量和测速结果，并运行至训练历史归档。依据是用户在对话中提供的实际输出，详见`evidence/restore_runtime_validation.json`。
- 本次随后上传的恢复Notebook是纯代码导出，所有outputs为空。`evidence/restore_source_only_export.ipynb`如实保留该文件；未给它虚构执行输出。提交中的带输出实验记录是`01_experiment_record.ipynb`。
- 新恢复导出的11个原入口代码单元格与整理包完全一致，另增加1个只读完整性检查。`02_train_from_scratch.ipynb`仍仅通过语法及CPU检查，尚未在新的Kaggle GPU会话中完整重跑。

## 下一步导出实验文件

`tools/export_kaggle_outputs.py`可在Kaggle中执行，将现有工作目录完整打包，包括六份权重、缓存、原始图表PDF、指标CSV、计时样本及选择记录。默认读取 `/kaggle/working/clip_retrieval`，输出ZIP到其父目录，不包含原始图片和基础CLIP模型。

已有Notebook输出版本仍是重要备份。更新成果后保存包含输出文件的Quick Save，并核验新版本Output；看到Draft saved不足以确认外部权重文件已保存。

最终提交还需附加：实验产物包、英文IEEE论文及源文件、演示视频。当前包完成代码整理与证据归档，不把这些尚未交付的内容标为已完成。
