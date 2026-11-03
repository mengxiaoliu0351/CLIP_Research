# Reviewer 3

## Overall assessment

本评审仅依据固定材料包，侧重复现、跨文件一致性和非专业读者理解，未重跑训练或推理。作为 IEEE 课程项目，稿件的受控比较与结果解释较成熟。保存的记录支持测试集内的增益，但完整训练和恢复链条仍需交付定位。

## Who would be interested in the results, and why

多模态检索学习者与资源受限的应用开发者会关注，少量可训练参数带来多少收益，以及为何参数节省仍可能增加延迟。

## Major strengths

正文明确区分训练种子波动与置信区间、标注对应与语义相关、缓存匹配与完整请求耗时。`main.tex` 的 Main Retrieval Results 与 `data/final_test.json`、`tables/main_results.tex` 对应。配对采样、全候选库和真实失败示例使比较易于理解。作者承认 CLIP 与 LoRA 来自既有工作，贡献定位适合课程项目。

## Major Concerns

### R3-M1 [reproducibility]

- **Severity** Major
- **Blocking** No
- **Claim pointer** 摘要与 Reproducibility and Limitations 声称提供离线恢复流程，并恢复 76 个文件、载入六个检查点和精确复现验证指标。
- **Evidence pointer** `main.tex` 的 Reproducibility and Limitations；`README.md` 末段所指 `CLIP_Flickr30k_code_package_20261030.zip`；本包 `scripts/` 的三个脚本；`verification_report.json` 的 scope。
- **Concern** 本包包含保存结果核查与绘图脚本，训练入口、恢复入口和所述恢复输出位于另外的材料，缺少可直接核查的交付定位与包级校验值。
- **Why it matters** 现有记录足以支持有限的结果比较，但读者无法沿正文独立检查手写 LoRA、冻结检查和恢复声明；课程要求的代码及关键输出尚不能从本包闭合核验。
- **Resolution test** 给出独立代码包与原件包的可访问位置、SHA256、入口及输入映射，附已有恢复核验输出，并区分保存数据复算与模型实际重算的范围。

## Minor Comments

### R3-m1 [writing-clarity]

- **Severity** Minor
- **Affected element** Q/V 与 projection 的直观含义。
- **Evidence pointer** `main.tex` 的 Embedding Model and Adaptation Strategies；`figures/method.png`。
- **Issue** 非专业读者能看到哪些模块训练，却较难理解为何选择这些模块。
- **Required correction** 首次出现时简释 query/value 在注意力中的作用，以及投影如何将两种模态映射到共同空间。

### R3-m2 [writing-clarity]

- **Severity** Minor
- **Affected element** 中文交付说明。
- **Evidence pointer** `README.md` 的标题、正文及 `--images` 命令示例。
- **Issue** 中文显示为乱码，影响输入目录与操作步骤的理解。
- **Required correction** 恢复可读中文并以 UTF-8 保存，逐项核对代码块和文件名。

## Technical failings that need to be addressed before the case is established

未识别 Blocking Yes 项。R3-M1 限制复现声明的独立核验。

## Assessment against Nature-style criteria

原创性体现为实现与对照实验，未提出新方法。科学重要性主要是教学与工程价值。跨学科兴趣在于准确率、参数量与延迟并不等价。技术证据支持所测数据集和固定预算内的结论。非专业可读性整体较好，术语与交付说明仍可改善。没有依据要求本课程项目达到 Nature 的重大原创门槛。

## Recommendation posture

支持在补齐复现交付定位和局部说明后作为课程报告使用。完整训练实现及恢复核验材料在所供包外，评审对其保持不可评估。
