# CLIP Research · Flickr30k 双向图文检索

冻结 CLIP 视觉塔，比较零样本 CLIP、仅文本投影微调，以及手写文本侧 LoRA + 投影微调。使用 Flickr30k 固定划分和完整候选库评估，保留代码、真实实验记录、中文报告与英文 IEEE 论文。

## 阅读入口

| 内容 | 文件 |
|---|---|
| 从头训练与评估 | [训练 Notebook](code/notebooks/02_train_from_scratch.ipynb) |
| 原始带输出实验记录 | [实验记录](code/notebooks/01_experiment_record.ipynb) |
| 恢复已保存实验 | [恢复 Notebook](code/notebooks/03_restore_saved_results.ipynb) |
| 环境、输入挂载、运行步骤与证据边界 | [代码说明](code/README.md) |
| 中文项目报告 | [PDF](reports/CLIP_Flickr30k_Project_Report_ZH_20261102.pdf) · [Word](reports/CLIP_Flickr30k_Project_Report_ZH_20261102.docx) · [Markdown](reports/CLIP_Flickr30k_Project_Report_ZH_20261102.md) |
| 英文 IEEE 论文与可编译源文件 | [论文 PDF](paper/main.pdf) · [LaTeX](paper/main.tex) · [编译说明](paper/README.md) |
| 实验数据、图表与复算脚本 | [数据](paper/data) · [图表](paper/figures) · [脚本](paper/scripts) |
| 研究评审、修订说明与文献核验 | [研究材料](research) |
| 外部输入和原始归档校验值 | [成果可用性说明](CODE_AND_ARTIFACT_AVAILABILITY.md) |

## 实验设计与测试结果

数据按 image_id 使用标注中的固定 train/val/test 划分：29,000 / 1,014 / 1,000 张图，每图5句。评估覆盖双向 R@1/5/10、MedianRank，以及六项 Recall 的平均值 mR。测试候选库为1,000张图和5,000条文本。

| 组别 | 方法 | 可训练参数 | 测试 mR (%) |
|---|---|---:|---:|
| A | 原始 CLIP ViT-B/32 零样本 | 0 | 84.13 |
| B | 仅 text_projection | 262,144 | 87.82 ± 0.14 |
| C | 文本 Q/V 手写 LoRA，r=8、alpha=8，加 text_projection | 458,752 | 89.21 ± 0.11 |

B/C 使用42、43、44三个配对训练种子，±表示样本标准差。每轮在完整验证候选库上选取最佳 epoch；测试集只用于最终评估。视觉塔与基础文本骨干冻结，LoRA 不依赖 peft。训练为5 epochs、batch 64、lr 1e-5；使用单张 T4。

## 复现

1. 按 [代码说明](code/README.md) 准备 Flickr30k 图片、Karpathy 标注和离线 CLIP 模型/processor，核验输入 SHA256。
2. 在 Kaggle 启用 T4、关闭 Internet，导入训练 Notebook，按顺序执行。路径可通过首个配置单元格或环境变量指定。
3. 已有完整实验归档时，使用恢复 Notebook；仅有小权重文件不足以恢复全部分析。

CPU 证据检查：`python code/tools/check_submission.py`。论文表格可由 `python paper/scripts/rebuild_tables.py` 复算；完整论文验证还需要编译产生的 `paper/main.log`。这些检查不等于重新训练或运行模型推理。

## 材料范围与状态

本仓库包含代码和研究材料。数据集原图、基础模型与约102 MiB的原始实验权重/缓存归档作为外部输入，未随仓库上传；其路径和校验值见成果可用性说明。数据集及模型的获取和使用须遵循各自许可，不授予额外再分发权利。

作者、院系、学校和邮箱仍待填写（`paper/author.tex`）；演示视频未制作。原始 GPU 实验与恢复验证的来源在代码证据中说明；整理后的从头训练入口通过静态与 CPU 检查，未在本次上传中重新进行完整 GPU 训练。
