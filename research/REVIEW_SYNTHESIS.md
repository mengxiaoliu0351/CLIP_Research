# Nature Skills 修订与审查记录

本轮处理对象是已经完成实验的 IEEE 课程论文。研究问题、实验设置和核心结论均来自原稿与已保存结果；Nature Skills 用于组织、润色与核查，不改变教师要求的 IEEE 格式。

## Review setup

- Input scope 为原始 8 页稿件、同目录数据/图表和课程要求边界说明。
- 三个独立上下文收到同一份不可变 `review_packet`。预先指定的侧重点分别为实验推断、主张与归属、复现与可读性。
- 每份报告先独立完成并冻结，再进行主代理数值审计与综合。未交换意见、追求差异或回写冻结报告。
- 评审不重新运行训练或检索；不把 Nature 的原创性门槛当作课程通过条件。

## Cross-review synthesis (post-review; not shown to reviewers)

### Consensus strengths

三份评审均认可 A/B/C 的比较逻辑、固定数据与抽样计划、完整候选库评估、对种子标准差的限定解释，以及失败与运行成本的诚实展示。方法归属清晰，原稿没有把 CLIP 或 LoRA 冒称为自创新方法。

### Consensus blocking concerns

没有评审识别出 Blocking Yes 项。这不等于独立重现实验已经完成，也不构成期刊录用判断。

### Other consensus major concerns

R1-M1 与 R3-M1 均指出复现材料位于另一代码包，稿件项目缺少直接交付定位。R2-m1 也识别了相同指引问题，但将其视为局部呈现问题。综合保留前两者的 Major、Blocking No 级别，并如实记录分歧。

本轮通过 `CODE_AND_ARTIFACT_AVAILABILITY.md` 给出实际代码包名称、入口、大小、SHA256 和实验原件包映射。最终材料包附上现有代码包副本。正文明确区分保存数据复算、历史恢复记录与新模型推理。原始 102 MiB 实验包由用户另存，不将其误称为已包含在排版项目中。

### Where emphasis differs

R1-m1 希望展示已有 p95 延迟，中文项目报告补充该表，并保留同次测量的解释边界。R3-m1 希望直观解释 Q/V 与投影，英文方法部分已增补。R3-m2 报告中文 README 显示异常，独立审计发现源文件可正常按 UTF-8 解码，包含 1,078 个汉字且没有替换字符。因此，该意见未被升级为已证实的源文件损坏；新说明继续用 UTF-8 写入并做显示检查。

## Forensic consistency findings

| Audit ID | Status | Check and evidence | Result / boundary |
| --- | --- | --- | --- |
| AUD-01 | passed | 最终七条 JSON 与 CSV；每条 mR 重算 | 六项 Recall 均值一致 |
| AUD-02 | passed | 三个种子的均值、ddof=1、配对差 | C−B = 1.3877778 ± 0.0741117 百分点（显示时按实际精度舍入） |
| AUD-03 | passed | 六份历史中的超参与数据/权重/抽样哈希 | 同种子 B/C 主要变量匹配，30 轮均无跳过更新 |
| AUD-04 | passed | A 与 C_seed42 的保存 rank 数组 | 复算 Recall、MedianRank 与原记录一致 |
| AUD-05 | passed | Params、LoRA MAC 差值、FLOP 换算 | 196,608 新增参数；15,138,816 新增文本 MACs |
| AUD-06 | passed | 案例选择 JSON 与最终 rank | 图示真值排名一致 |
| AUD-07 | passed | README 原始字节按 UTF-8 解码 | 不能证实 R3-m2 是源文件损坏 |
| AUD-08 | not_assessable | 本轮未重新运行模型训练/推理 | 不将文档复核宣称为全流程重新训练认证 |
| AUD-09 | not_assessable | 原始预训练数据、视觉近重复 | 不宣称已排除预训练重叠或所有近重复 |

一致性检查器对数字 1 与 1.0 提示精度差异。人工核对后，它们分别表示排名/公式整数和梯度裁剪阈值，未据此认定为同一量的格式错误。

## Revision notes

1. 引言使用“任务与应用 → 具体比较问题”的收敛结构，让投影层对照与运行成本问题更早出现。
2. 摘要围绕同一证据链展开，加入三种子离散程度、配对增益和延迟边界，删除实验清单式尾句。
3. 先呈现主测试比较，再展示验证曲线，避免把实验执行顺序当成论文论证顺序。
4. 独立设置 Discussion and Reproducibility，综合准确率与运行成本，补足材料定位并将未来实验对应到未解决问题。
5. 保留真实失败、查询回退、单数据集/单秩/短预算和计时排除项，不以润色掩盖结论边界。

## Claim-evidence map

| Claim | Evidence | Status |
| --- | --- | --- |
| 文本 LoRA 在固定预算内提供投影层之外的增益 | A/B/C 测试表、三个配对种子 | supported |
| 参数效率不等于当前实现的运行效率 | Params/MAC 表与同步单 GPU 测速 | supported within stated scope |
| 实例对应与广义语义相关并不等价 | 商店 T2I 和拔河 I2T 真实失败案例 | supported qualitative interpretation |
| 延迟差由小矩阵/调度开销引起 | 本轮没有逐内核分析 | inferred; 保留“可能解释” |
| r=4/16 或跨数据集效果 | 未执行 | needs evidence; 只列为后续工作 |

## Main-text discipline audit

- 核心发现是 B/C/A 的测试比较；三种子是必要支持，而非“显著性证明”。
- 参数量、计时和失败是改变结论理解的限定证据，保留在正文。
- 包级哈希和入口清单属于 provenance detail，移至随附 availability 文件，正文只保留稳定指引。
- 完整表格报告所有指标，正文选择具有解释作用的差值，不逐行复述。
- 各节字数变化、句长检查和跨材料数值检查由生成的审计 JSON 记录。

## Risk / unsupported claims

尚未检验完整文本微调、rank 扫描、合并 LoRA、其他数据集和部署规模候选库。三种子样本标准差不代表测试集总体不确定性。作者信息仍待填写。课程演示材料尚需完成，但不影响已保存实验结果的有效性。

如需进一步修改，请指明段落、主张或图表位置；后续只改受影响内容并复核相关数字。
