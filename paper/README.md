# Flickr30k 英文 IEEE 课程论文优化版

标题：Text-Side Low-Rank Adaptation of CLIP for Flickr30k Retrieval。

当前 main.pdf 共9页，正文8页、参考文献1页；5幅图、6张表、12条文献。使用未修改的官方IEEEtran conference类与bst。作者、院系、学校、邮箱仍在 author.tex 中保留待填。

## 编译

将本文件夹内容上传Overleaf，主文件设为main.tex，选择pdfLaTeX。也可在TeX Live/MiKTeX中依次运行pdflatex、bibtex、pdflatex、pdflatex。本次实际编译使用Tectonic0.17；未宣称本机另行运行过pdfLaTeX。无需GPU、模型权重或原始数据即可编译现有图表。标准模板未缩小字号或压缩页边距；正文浮动体在参考文献前清空。

## 数值与证据

实际划分：29,000/1,014/1,000张图片，每图5句；并非将常见论文计数套到当前输入。训练组B为仅投影，C为手写文本Q/V LoRA与投影，r=8、alpha=8、五轮，三个配对种子。最终测试mR：A84.1267%，B87.8189±0.1407%，C89.2067±0.1106%；C−B配对增益1.3878±0.0741个百分点。所有±均为样本标准差，不是置信区间。没有r=4/16新结果。

data保留原实验结果、30轮历史、秩数组、计时与理论算量。figures含论文实际插图与备选图；正文删除一幅重复的召回率图以减少冗余，原数据和图文件保留。表格由scripts/rebuild_tables.py生成；scripts/make_paper_figures.py可重绘；scripts/verify_paper.py核对保存数据与编译PDF。以上检查不执行新训练或测试推理。

## 代码及归档

本仓库已将完整代码包解压至 ../code/，可直接查看Notebook和实验记录。训练、历史记录和恢复Notebook的具体入口及原实验归档SHA256见CODE_AND_ARTIFACT_AVAILABILITY.md。约102MiB实验权重归档是用户先前下载的原文件，不重复塞入此文档包。

## 提交前

填写author.tex并重编译；亲自通读结果和失败解释。课程演示视频尚未生成；本仓库仅收录代码与研究材料。本优化使用Nature写作/润色/评审流程，最终版式仍为IEEE，不改投Nature期刊格式。
