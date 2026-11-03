冻结视觉分支，比较文本投影微调与手写 LoRA 的检索收益和运行代价。

项目报告｜中文说明版｜2026-11-02

作者：待定　　院系与学校：待定

| 最终测试 mR | C−B 配对增益 | C 组可训练比例 |
| --- | --- | --- |
| 89.21% | +1.39 个百分点 | 0.3029% |


## 摘要

本项目使用真实 Flickr30k 图片与人工描述，在固定图像级划分上比较原始 CLIP、仅训练文本投影层、文本 Q/V 手写 LoRA 联合投影层三种配置。视觉分支全程冻结；同种子的训练组共享原始权重、抽样计划与超参数。最终测试覆盖完整的 1,000 张图片和 5,000 条 caption。结果显示，投影层训练已贡献较大收益，加入 LoRA 后三个配对种子均进一步提升；但当前未合并实现增加了文本编码延迟。报告结合训练曲线、全库指标、复杂度、同步计时和真实失败，给出所测配置下的结论与边界。

关键词：CLIP；图文检索；LoRA；参数高效微调；Flickr30k。

本中文报告辅助说明项目。正式课程论文另以英文 IEEE Conference LaTeX/PDF 提交。所有定量数据均读取既有实验记录，本轮未新增训练或测试推理。


## 01　项目问题与课程要求


## 要回答的两个问题

第一，冻结视觉分支后，文本侧微调能否改善零样本检索？第二，在仅训练投影层这一更强基线上，额外训练注意力 Q/V 的 LoRA 是否仍有收益，代价是什么？

CLIP 的图文共享表征来自既有工作 [1]，LoRA 的低秩更新来自既有方法 [2]。本项目的工作是手写实现、受控实验、正确评估和复现材料组织，不将这些基础方法表述为原创算法。

| 老师要求 | 本项目对应实现 |
| --- | --- |
| 至少训练或微调一个网络模块 | B 更新 text_projection；C 更新文本 Q/V LoRA + text_projection |
| 公开数据、来源及划分 | Flickr30k；实际 JSON 31,014 张；29,000/1,014/1,000 固定 split |
| 同图所有 caption 留在同一划分 | 同时检查 image_id 与 filename，无跨集合交集 |
| 至少两组有意义的公平对比 | A–C：总体微调收益；B–C：注意力适配的额外收益 |
| 任务指标与复杂度 | 双向 R@1/5/10、MedianRank；Params、MACs/FLOPs、耗时 |
| 代码与真实可视化 | 手写层、训练/恢复入口；loss、检索 Top-5、成功和失败 |
| 英文 IEEE 论文 | 保留官方 IEEEtran 版式；个人信息待填写 |
| 2–5 分钟视频或现场演示 | 已制作带讲稿的答辩 PPT；视频/现场演示另行完成 |

采用老师原文中较严格的“两组有意义对比”要求。B 不是装饰性实验，它决定能否将增益正确归因到新增注意力适配，而不是把全部提升都算作 LoRA 的作用。


## 02　数据来源与防泄漏协议

图片目录包含 31,783 张 JPEG；挂载的 Karpathy 格式标注仅引用 31,014 张，每图 5 条人工描述，共 155,070 条。全部被引用图片成功匹配并可完整解码，另外 769 张不进入实验。数据规模按实际输入文件报告，不改写成其他论文常见的划分计数。

| 划分 | 图片数 | 可用 caption 数 |
| --- | --- | --- |
| Train | 29,000 | 145,000 |
| Validation | 1,014 | 5,070 |
| Test | 1,000 | 5,000 |
| 合计 | 31,014 | 155,070 |


## 划分与质量控制

直接读取 JSON 的 split 字段，未自行随机重划分。图像 ID 与文件名均唯一，三个集合交集为零；同一张图片的五条描述全部保留在同一集合。图像定位使用 filename，不把内部 imgid 拼成图片文件名。

完整解码检查覆盖 31,014 张被引用图像，损坏或无法解码为 0；检查了非空 caption、重复标识与跨 split 交集。上述检查保证标注身份隔离，不代表已排除视觉近重复，更不能证明与 CLIP 原始预训练数据没有重叠。


## 预处理与使用范围

图片转为 RGB，采用原始 CLIP 的 PIL 预处理，输出 224×224。文本使用配套 tokenizer，最多 77 tokens。训练和测速固定填充 77；评估按批次最长文本填充，但不超过相同上限。

Flickr30k 原始门户 [12] 将图片提供给非商业研究和教育使用，并声明不拥有图片版权，需遵守原始图片与平台条件。不能将“公开可获取”解释为任意用途或任意再分发许可。

标注 SHA256：db779ee2c5df40c25ff0eebeca464f6124b620cc4a9398650aea71fd1b53d4af


## 03　网络、手写 LoRA 与损失

![图 1　C 组计算路径。视觉编码器与投影冻结，文本 Q/V 低秩分支和文本投影可训练。](paper/figures/method.png)

CLIP 先分别编码图片和句子，再通过投影进入 512 维公共空间；L2 归一化后，以点积计算余弦相似度。投影层改变最终对齐，而 Q/V 更新可以改变文本注意力中的匹配与信息聚合。

| 组别 | 可训练部分 | 用途 |
| --- | --- | --- |
| A | 无，原始 CLIP | 零样本基线 |
| B | text_projection | 投影层适配对照 |
| C | 文本 12 层 Q/V 的手写 LoRA + text_projection | 主实验；共 24 个 LoRA 模块 |

手写层计算 y = W₀x + b₀ + (α/r)BAx。设 r=8、α=8，A 以 Kaiming uniform 初始化，B 为零，无 LoRA dropout。初始化时新增分支为零；两次真实更新检查中 LoRA 与投影更新，冻结参数未变化。

文本宽度 512，LoRA 参数为 24×8×(512+512)=196,608；加上 262,144 个投影参数，共 458,752。原始文本权重、视觉编码器、视觉投影和 logit_scale 保持冻结。

每个 epoch 每张训练图像只选择一句 caption，保证一个 batch 内 image_id 不重复。该方案避免重复图片的其他 caption 被对角标签当成负例，但不同图片之间仍可能存在语义相似的负例。

训练使用图到文与文到图交叉熵的平均值。Logits 为冻结温度尺度 exp(logit_scale) 乘余弦相似度；图片特征确定性预计算为 FP32，文本分支在训练中实时前向与反传。


## 04　受控训练与验证选模

| 配置 | 实际记录 |
| --- | --- |
| 硬件 | 单张 Tesla T4；约 14.56 GiB；cuda:0 |
| 模型 | openai/clip-vit-base-patch32，权重与 processor 本地离线加载 |
| 训练预算 | 5 epochs；batch64；每轮 454 次更新，末批 8 张 |
| 优化器 | AdamW；lr=1e-5；weight_decay=0.01 |
| 稳定性 | 梯度范数裁剪 1.0；无学习率调度；初始 GradScaler=1024 |
| 精度 | 文本前向 FP16 autocast；归一化、logits、loss FP32；评估 FP32 |
| 重复实验 | B/C 各用 seed42/43/44，同种子共享数据与抽样计划 |
| 选模 | 每轮完整验证 mR 选最佳；六次实验均选 epoch5 |
| 更新状态 | 30 轮均未跳过优化器更新 |

![图 2　三个训练种子的均值与样本标准差。未平滑；左右纵轴不同。](paper/figures/training_validation.png)

验证集 mR：A 为 84.50%，B 为 88.75±0.05%，C 为 89.56±0.09%。这些数用于选择检查点，不能替代最终测试表现。最优轮次均落在预算末轮，因此不能宣称已经充分收敛。

训练环境记录：Python 3.13.15；torch 2.11.0+cu128；torchvision 0.26.0+cu128；transformers 5.16.1；huggingface_hub 1.29.0；Pillow 13.0.0。


## 05　全候选库评估与主结果

测试候选库固定为 1,000 张去重图片与 5,000 条 caption。先分批提取全部特征，再在完整 1,000×5,000 相似度矩阵上排序。特征提取分 batch，不意味着指标在 batch 内计算。

I2T 以五条正确 caption 中的最佳排名为真值 rank；T2I 以 caption 对应的唯一图片排名为 rank。排名从 1 开始；相同分数按候选索引稳定排序。MedianRank 为普通中位数，偶数查询数取中间两项的平均。mR 为六项 Recall 的算术平均。


## 图像 → 文本

| 模型 | R@1 (%) | R@5 (%) | R@10 (%) | MedianRank |
| --- | --- | --- | --- | --- |
| A 原始 CLIP | 79.30 | 95.00 | 98.10 | 1 |
| B 仅投影 | 81.10 ± 0.52 | 96.53 ± 0.15 | 99.03 ± 0.21 | 1 |
| C LoRA + 投影 | 84.17 ± 0.46 | 97.53 ± 0.15 | 99.40 ± 0.10 | 1 |


## 文本 → 图像

| 模型 | R@1 (%) | R@5 (%) | R@10 (%) | MedianRank |
| --- | --- | --- | --- | --- |
| A 原始 CLIP | 58.84 | 83.44 | 90.08 | 1 |
| B 仅投影 | 66.91 ± 0.13 | 89.29 ± 0.14 | 94.04 ± 0.03 | 1 |
| C LoRA + 投影 | 68.87 ± 0.27 | 90.40 ± 0.02 | 94.87 ± 0.10 | 1 |

| 模型 | mR (%) |
| --- | --- |
| A | 84.13 |
| B | 87.82 ± 0.14 |
| C | 89.21 ± 0.11 |

B/C 显示三个训练种子的均值 ± 样本标准差（ddof=1），不是置信区间。A 只做一次确定配置的零样本评估。全部 MedianRank 为 1，是因为超过半数查询的真值位于首位，不表示其余查询都成功。


## 06　两组对比与结果解释

![图 3　双向 Recall 对比。误差条来自三个训练种子，不能解释为独立测试样本的置信区间。](paper/figures/recall.png)


## A–C：总体适配收益

C 的平均测试 mR 为 89.21%，相对原始 CLIP 提升 5.08 个百分点。该比较支持本项目配置下的微调有效性。B 单独已提升约 3.69 个百分点，说明不能将全部收益归因于 LoRA。


## B–C：注意力适配的额外收益

| 种子 | B mR (%) | C mR (%) | C−B（百分点） |
| --- | --- | --- | --- |
| 42 | 87.72 | 89.19 | +1.47 |
| 43 | 87.98 | 89.32 | +1.34 |
| 44 | 87.76 | 89.10 | +1.35 |

三个配对差均为正，均值为 +1.3878±0.0741 个百分点。C 相对 B 的 I2T R@1 增加约 3.07 个百分点，T2I R@1 增加约 1.95 个百分点。已经接近饱和的 I2T R@10 增益较小。

这些结果支持固定数据、预算和超参条件下的额外收益，不证明 LoRA 优于完整文本微调、其他 PEFT 方法或经过独立超参优化的投影基线。三种子一致也不等于统计显著性检验通过。


## 07　模型复杂度与训练成本

| 组别 | 总参数 | 可训练参数 | 可训练比例 |
| --- | --- | --- | --- |
| A | 151,277,313 | 0 | 0.0000% |
| B | 151,277,313 | 262,144 | 0.1733% |
| C | 151,473,921 | 458,752 | 0.3029% |

| 组别 | 图像 GMACs | 文本77 GMACs | 图文对 GFLOPs |
| --- | --- | --- | --- |
| A | 4.4088 | 2.9798 | 14.7772 |
| B | 4.4088 | 2.9798 | 14.7772 |
| C | 4.4088 | 2.9949 | 14.8074 |

计数输入为一张 224×224 RGB 图像和一条 77-token 文本，约定 1 MAC=2 FLOPs。卷积、线性、注意力两次矩阵乘法及手写 LoRA 的两次投影计入；注意力按全长稠密矩阵计数，包括掩码位置。

不计 bias/残差加法、归一化、激活、Softmax、embedding lookup、LoRA 缩放，以及候选库评分和排序。因此这些值是主要算子的理论计数，不能冒充完整硬件指令或真实耗时。

| 训练组 | 平均每轮训练 (s) | 峰值 allocated (GiB) |
| --- | --- | --- |
| B | 20.25 | 0.696 |
| C | 48.91 | 1.791 |

训练时间对每组 15 个 epoch 求平均；显存是最大 PyTorch allocated 峰值，不是 reserved，更不是整机全部显存。上述 epoch 时间不包含首次缓存构建与验证。视觉特征缓存加速了训练，不代表端到端从图片读取到结果展示的总时长。

C 每条 77-token 文本新增 15,138,816 MACs，约为基础文本编码的 0.51%。图文对理论计算量约增加 0.20%，但训练仍需穿过中间文本激活进行反传，可训练参数比例不能单独预测训练显存与速度。


## 08　真实测速与口径

![图 4　单 T4、FP32、seed42、LoRA 未合并。批量吞吐与单条延迟是两种测量。](paper/figures/speed.png)

| 组别 | 图片均值 ms | 图片 p95 ms | 文本均值 ms | 文本 p95 ms |
| --- | --- | --- | --- | --- |
| A | 6.472 | 7.394 | 7.765 | 8.971 |
| B | 6.864 | 9.806 | 7.596 | 8.599 |
| C | 6.546 | 7.597 | 9.727 | 11.167 |

| 组别 | B32 images/s | B32 texts/s | 缓存 T2I ms | 缓存 I2T ms |
| --- | --- | --- | --- | --- |
| A | 362.46 | 500.98 | 0.0668 | 0.1058 |
| B | 346.22 | 497.04 | 0.0695 | 0.1103 |
| C | 360.80 | 478.20 | 0.0736 | 0.1064 |

编码延迟预热 20 次、同步墙钟采样 100 次；batch32 吞吐预热 10 次、5 轮×10 次前向。缓存匹配预热 20 次、采样 200 次，轮换 64 个预编码查询。p95 来自同次重复调用，不是跨会话或跨种子的误差估计。

输入与候选特征驻留 GPU。不含文件读取、预处理、tokenization、CPU/GPU 传输、候选库构建和结果展示。缓存 Top-5 时间更不能当作完整请求延迟。C 文本单条编码比 A 慢约 25.3%，说明当前未合并实现的运行成本应单独衡量。


## 09　T2I 成功与失败案例

![图 5　来自已保存真实检索结果。绿色 GT 是数据对应，不代表其他候选在语义上都不相关。](paper/figures/qualitative_t2i.png)


## 改善示例：白色帐篷下演奏乐器

查询为 “Four people playing instruments underneath a white tent.”。原始 CLIP 的正确图片为第 2 名，C 组为第 1 名。这是相近候选之间的局部排序改善，不能仅由截图推断模型已经掌握所有关系或数量。


## 失败示例：商店中的年轻人

查询为 “Young people are standing in the store.”，对应图片 110671448.jpg。A 的真值排名为 10，C 为 9，仍不在 Top-5。返回结果中也有商店或室内人物；该句缺少其他人工标注中的帽子、排队、咖啡店等细节，难以唯一定位实例。

失败体现的是短文本、候选库相似场景与实例级标签之间的歧义，不足以证明某一视觉对象完全未识别。图中分数为各模型的余弦相似度，跨模型分数绝对值变化不能直接代替排名比较。


## 10　I2T 失败与逐查询审计

![图 6　C 组真实 Top-5 文本。仓库图改善至 Top-1；拔河图的首个正确 caption 仍排第 6。](paper/figures/qualitative_i2t.png)

仓库图片的首个对应 caption 从第 2 名提高到第 1 名。拔河图片 3483071906.jpg 的五条人工描述包括 “Children are playing tug-of-war.”，但模型优先返回属于其他图片的相似描述，真值由 A 的第 9 名改善为 C 的第 6 名。

“活动语义正确”与“属于该图片的五条标注”不是同一个条件。该例提示对应标签不穷尽所有语义相关候选，但不能在看到失败后修改基准标签来提高分数。

| 方向 | 两者正确 | 仅 A 正确 | 仅 C 正确 | 两者失败 |
| --- | --- | --- | --- | --- |
| I2T | 750 | 43 | 89 | 118 |
| T2I | 2785 | 157 | 673 | 1385 |

表中覆盖 seed42 的全部查询。C 修复的 Top-1 失败多于退化的成功，但并非所有查询均改善。T2I caption 共享图片，不能把 5,000 条 caption 当成互相独立的统计样本。


## 11　复现交付与结论边界


## 现有材料定位

| 材料 | 作用 |
| --- | --- |
| 01_experiment_record.ipynb | 保留关键历史训练、指标与可视化输出 |
| 02_train_from_scratch.ipynb | 完整重新训练入口；原始输入另行挂载 |
| 03_restore_saved_results.ipynb | 恢复检查点并读取/核验已有结果 |
| CLIP_Flickr30k_experiment_artifacts.zip | 保存六份检查点、缓存、抽样计划、日志与结果 |
| CODE_AND_ARTIFACT_AVAILABILITY.md | 列明精确入口、文件 SHA256 与输入映射 |

完整恢复曾在后续 Kaggle 会话执行：76 个文件 SHA256 一致，六份检查点加载与文本前向通过，C_seed42 验证指标与原结果最大差为 0。之后的展示读取保存的测试/测速记录，没有把历史日志伪装成新一轮训练。

本轮 Nature Skills 优化只重算保存数据与检查文件/排版，未重新运行训练或测试推理。保存结果的相互一致不等于新环境从零完整复现，二者在交付说明中分别标记。


## 结论与有针对性的后续实验

在本次固定数据与五轮预算下，投影层训练改善原始 CLIP；增加文本 Q/V LoRA 提供额外增益。与此同时，较小的可训练参数比例没有消除未合并实现的文本编码代价。

| 当前边界 | 它限制的结论 | 能区分问题的后续测试 |
| --- | --- | --- |
| 仅 r=8、五轮预算 | 不能推断最优秩或充分收敛 | 匹配 r=4/8/16 与更长验证选模预算 |
| 单数据集、1k 图片测试库 | 不能直接推广到其他域或大索引 | 其他数据集与更大候选库 |
| 未合并 LoRA、GPU 驻留计时 | 不能代表部署端到端延迟 | 合并/未合并与完整请求同步测量 |
| 单图随机一句训练 | 同轮未覆盖全部 caption | 多正例对比损失与相同训练预算 |
| 无视觉近重复/预训练去重证明 | 身份隔离不等于所有语义独立 | 近重复审计与明确的预训练污染边界 |

r=4/16 尚未运行，不在报告中填造消融结果。姓名、院校和邮箱待确定。PPT 与 2–5 分钟演示仍按确认后的展示方案继续完善。


## 12　参考文献与材料索引

[1] Radford et al. Learning Transferable Visual Models From Natural Language Supervision. ICML, PMLR 139:8748–8763, 2021.
https://proceedings.mlr.press/v139/radford21a.html

[2] Hu et al. LoRA: Low-Rank Adaptation of Large Language Models. ICLR, 2022.
https://arxiv.org/abs/2106.09685

[3] Young, Lai, Hodosh, and Hockenmaier. From image descriptions to visual denotations. TACL 2:67–78, 2014.
https://aclanthology.org/Q14-1006/

[4] Karpathy and Fei-Fei. Deep Visual-Semantic Alignments for Generating Image Descriptions. CVPR, 2015.
https://arxiv.org/abs/1412.2306

[5] Dosovitskiy et al. An Image Is Worth 16x16 Words: Transformers for Image Recognition at Scale. ICLR, 2021.
https://arxiv.org/abs/2010.11929

[6] Houlsby et al. Parameter-Efficient Transfer Learning for NLP. ICML, PMLR 97:2790–2799, 2019.
https://proceedings.mlr.press/v97/houlsby19a.html

[7] Faghri et al. VSE++: Improving Visual-Semantic Embeddings with Hard Negatives. BMVC, 2018.
https://arxiv.org/abs/1707.05612

[8] Loshchilov and Hutter. Decoupled Weight Decay Regularization. ICLR, 2019.
https://arxiv.org/abs/1711.05101

[9] Paszke et al. PyTorch: An Imperative Style, High-Performance Deep Learning Library. NeurIPS 32, 2019.
https://arxiv.org/abs/1912.01703

[10] Wolf et al. Transformers: State-of-the-Art Natural Language Processing. EMNLP Demonstrations, pp. 38–45, 2020.
https://aclanthology.org/2020.emnlp-demos.6/

[11] shtvkumar. Karpathy splits for Image Captioning. Kaggle dataset mirror.
https://www.kaggle.com/datasets/shtvkumar/karpathy-splits

[12] University of Illinois. Flickr30k source dataset download and usage information.
https://hockenmaier.cs.illinois.edu/DenotationGraph/data/

完整作者与字段记录见英文项目的 references.bib 及本次文献核验说明。Kaggle 镜像正文无法被当前检索器完整读取，其实际文件身份由项目标注 SHA256 与本地统计界定。
