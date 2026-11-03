# Terminology Ledger

| Canonical term | First-use definition | Variants in the previous draft | Decision |
| --- | --- | --- | --- |
| CLIP | Contrastive Language–Image Pre-training | original CLIP, pretrained model | 首次定义全称；A 组始终指同一原始权重 |
| LoRA | low-rank adaptation | LoRA, low-rank branches | 首次定义；不另造方法名称 |
| Projection-only (B) | 仅训练 text_projection | projection baseline, only projection | 正文用 projection-only，代码保留 B_projection |
| LoRA plus projection (C) | 文本 Q/V 手写 LoRA 与 text_projection 联合更新 | LoRA + projection, C | 同一配置；r=8、alpha=8，未合并推理 |
| I2T | image-to-text retrieval | image→text, image-to-text | 图像检索文本，1,000 查询、5,000 候选 |
| T2I | text-to-image retrieval | text→image, text-to-image | 文本检索图像，5,000 查询、1,000 候选 |
| Recall@K | 排名不大于 K 的查询比例 | R@K, Recall | 表格用 R@1/5/10，百分比保留两位 |
| MedianRank | 一基排名的普通中位数 | MedR, MedianRank | 正文用 MedianRank；表头 MedR 定义一次 |
| mR | 双向六项 Recall 的算术平均 | mean recall, mR | 两个方向等权，不能按查询条数混合加权 |
| sample standard deviation | 三个训练种子的样本标准差，ddof=1 | sample SD, standard deviation | 不称置信区间，不据此宣称统计显著 |
| percentage points | 两个百分率的绝对差 | points, percentage points | 中文“百分点”，区别于相对百分比 |
| MAC / FLOP | multiply–accumulate / floating-point operation | MACs, FLOPs | 固定 1 MAC = 2 FLOPs，标注计数排除项 |
| Encoding latency | GPU 驻留真实输入的编码耗时 | single-text latency | 与 cached matching、端到端请求分开 |
| Cached matching | 已编码查询和候选的相似度及 Top-5 | retrieval latency | 不冒充完整检索响应时间 |
| supplied annotation split | 本项目 JSON 已有 split 字段 | Karpathy split | 保留 29,000/1,014/1,000 实际计数，不暗示所有同名协议完全一致 |

不存在需要重新命名的模型歧义。代码标识符与自然语言术语的差别属于表示层差异，不混改变量名。
