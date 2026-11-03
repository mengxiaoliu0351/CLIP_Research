# Reviewer 2

## Overall assessment

这是定位克制、论证连贯的 IEEE 课程项目。中心结论是既定 Flickr30k 划分、固定训练预算下，投影训练改善零样本检索，加入文本 Q/V LoRA 进一步改善指标，并付出延迟代价。评审仅依据不可变审阅包及技能参考，不重新训练或推理。训练源码、完整 Notebook 和权重位于另一个代码包，未在本次证据范围内。

## Who would be interested in the results, and why

资源有限的多模态学习实践者和神经网络课程读者会关注如何控制训练变量，以及可训练参数、检索质量与实际运行时间为何不成比例。跨学科价值主要在这一实验方法和成本解释，尚非广泛科学发现。

## Major strengths

Introduction 明确把贡献限定为实现与实验，并承认 CLIP 和 LoRA 来自既有工作，Related Work 的归属清楚。A/B/C 比较拆开了总体适配收益与增加 LoRA 的收益，避免将全部提升归于 LoRA。Main Retrieval Results 区分种子波动和统计显著性，失败案例与逐查询退化记录也约束了结论。Encoding Speed and Cached Matching 没有把缓存匹配时间等同完整请求延迟。

## Major Concerns

依据所供材料未识别有充分证据支持的 Major Concern。单数据集、单 rank 和有限预算已被明确承认，不应仅因未达到 Nature 的新颖性或广泛影响标准而成为课程项目的阻断项。

## Minor Comments

**Concern ID** R2-m1  
**Severity** Minor  
**Axis** reproducibility / writing-clarity  
**Affected element / Claim pointer** Abstract 的离线恢复流程承诺，以及 main.tex 的 Reproducibility and Limitations 所述训练、恢复入口。  
**Evidence pointer** main.tex，Reproducibility and Limitations；README.md，提交前需人工完成；scripts/ 下仅列有制图、表格重建和验证脚本。  
**Issue** 正文没有列出独立代码包名称和入口路径。README 虽提到 CLIP_Flickr30k_code_package_20261030.zip，读者仍难从论文直接定位训练、恢复和原始输出。此处是交付物指引问题，不能据此断言训练未发生或代码不存在。  
**Required correction** 在复现段列明代码包名称、可核验哈希及训练、恢复、结果 Notebook 的相对路径，并明确其与排版项目的对应关系。

## Technical failings that need to be addressed before the case is established

未识别已证实的 Blocking Yes 项。保存的六次训练历史、最终指标与协议描述支持有限范围的经验结论；原始训练实现、图像解码检查及恢复过程的执行证据无法在当前包内独立审查，结论不应扩大为全面复现认证。

## Assessment against Nature-style criteria

**Originality** 是既有方法的自主实现和受控评估，未证明新算法，也未冒称新算法。  
**Scientific importance** 支持具体资源预算下的实践判断，未建立普遍性能优势。  
**Interdisciplinary readership** 成本与质量的取舍有教学传播价值，应用外推仍有限。  
**Technical soundness** 图像级划分、完整候选库、配对种子及独立验证选模的描述合理，执行真实性的审查受源码范围限制。  
**Readability for nonspecialists** 引言、方法图、指标定义和语义相关但标签不匹配的案例解释清楚，主张与证据相互衔接。

## Recommendation posture

支持其作为课程项目报告，补足 R2-m1 的复现指引后提交。无需为满足 Nature 风格评审而添加未经实施的新颖性、机制或跨数据集结论。