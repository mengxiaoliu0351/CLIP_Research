# Reviewer 1

**Overall assessment**
本文对固定 Flickr30k 划分上的文本侧适配进行了可信的描述性比较。现有证据支持五轮预算下 C 优于 B/A，尚不能推广为普遍最优方案。按 IEEE 课程项目评价，无须以 Nature 级新颖性作为通过前提。本评审仅依据不可变稿件包及技能参考，未重训或推理。

**Who would be interested in the results, and why**
资源受限的多模态检索实践者和课程学习者，可据此理解投影微调、注意力适配及运行成本之间的取舍。

**Major strengths**
`main.tex` 的 Setup and Fair Comparisons 与 Full-Gallery Retrieval Metrics 明确共享采样计划、图像级隔离、完整候选库及双向指标。`data/experiment_records.json` 保存六次训练历史；`data/final_test.json` 显示三个种子的 C−B 均为正。正文区分种子标准差与测试样本不确定性，并报告延迟代价、失败和回退，结论边界恰当。

## Major Concerns

### R1-M1 [reproducibility]

**Severity** Major  
**Blocking** No  
**Claim pointer** Reproducibility and Limitations 声称提供训练、恢复入口，并在后续会话恢复六个检查点。  
**Evidence pointer** `main.tex` 同名小节；`README.md` 文件说明及末段；`scripts/verify_paper.py`；`verification_report.json` 的 scope。  
**Concern** 当前包提供保存结果的复核脚本，但训练/检索实现、关键 notebook 输出和所述恢复日志位于另一个代码包，未随包提供。因此独立复现能力尚不可评估；不能据此断言代码不存在。  
**Why it matters** 保存摘要相互一致不能独立检验冻结实现、划分检查及测试流程，也不能完成教师要求的代码与关键输出核验；这不否定现有描述性增益。  
**Resolution test** 提供所指代码包的可访问位置、入口与结果文件对应表，以及支撑恢复声明的 notebook 输出和哈希清单。无需新增训练。

## Minor Comments

### R1-m1 [figures-and-tables]

**Severity** Minor  
**Affected element** Encoding Speed and Cached Matching 的延迟展示。  
**Evidence pointer** Fig. speed；`data/inference_speed.csv` 的 `Image_B1_p95_ms`、`Text77_B1_p95_ms`；`data/inference_speed_details.json` 的 protocol。  
**Issue** 主图仅显示均值，已有 p95 未呈现，读者难判断尾部延迟；正文已正确承认相同视觉分支的测量波动。  
**Required correction** 在附表补现有 p95，标明它来自同次重复调用，而非独立会话的不确定性估计。

**Technical failings that need to be addressed before the case is established**
未识别 Blocking Yes 项。R1-M1 是重要的可核查性缺口，现有设计仍支持限定条件下的核心比较。

**Assessment against Nature-style criteria**
原创性体现为实现和实验组织，基础算法来源交代清楚。科学意义是课程及任务内的经验价值，未建立广泛科学突破。跨学科兴趣主要来自低成本多模态适配。技术可靠性总体较强，复现证据仍受包边界限制。非专业可读性良好，方法图及对应标签与语义相关性的区分有帮助。单数据集、单秩和三种子限制已明示，不应另行要求未经主张的机制或泛化证据。

**Recommendation posture**
支持在补齐可访问的复现材料、完善延迟展示后作为课程报告提交。未据此作期刊录用判断。