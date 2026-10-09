# Lit Review v2

`lit-review-v2` 是一个给 Codex 使用的文献综述 Skill。你提供研究主题和要求，Codex 负责检索、筛选、整理证据、撰写综述并检查引用关系。

这个仓库是 Skill 本身。主题、年份和筛选条件由你每次调用时决定。

## 第一次使用，只需要做两件事

### 1. 安装 Skill

把整个仓库文件夹放入 Codex 的 Skill 目录，并确保路径最终类似：

```text
%USERPROFILE%\.codex\skills\lit-review-v2\SKILL.md
```

`%USERPROFILE%` 表示 Windows 当前用户目录，例如 `C:\Users\你的用户名`。安装后重新打开 Codex 或刷新 Skill 列表。

### 2. 在 Codex 中描述你的综述需求

你可以直接输入：

```text
使用 $lit-review-v2 做一次文献综述。

研究主题：[填写主题]
时间范围：[起始年份]—[结束年份]
重点方向：[可选]
已有 PDF、DOI 或参考文献：[有就提供，没有写“暂无”]
纳入和排除标准：[可选]
输出格式：Markdown
```

如果信息不完整，Skill 会询问主题、时间范围、文献类型、重点方向、筛选标准和输出格式。示例中的方括号是等待你填写的内容，不是固定参数。

## 最后会得到什么

Codex 会新建一个独立的综述项目文件夹。普通用户建议先看以下文件：

1. `review_draft.md`：最终综述正文，优先阅读。
2. `evidence_table.csv`：每篇纳入文献的方法、数据集、结果、局限及证据位置。
3. `screening.csv`：候选文献是否纳入，以及排除理由。
4. `review_lint_report.json`：引用、文件关系和结构检查是否通过。

需要审计或继续更新时，再查看：

- `search_log.csv`：检索来源、检索式和停止规则。
- `reference_map.csv`：正文编号与论文之间的对应关系。
- `claim_registry.csv`：综述结论由哪些论文支持或限制。
- `comparison_matrix.csv`：哪些跨论文结果可比较，哪些不可比较。
- `evidence_matrix_by_route.csv`：按技术路线汇总的证据。
- `conflict_matrix.csv`：论文间冲突及可能的异质性来源。
- `coverage_audit.csv`：年份、venue 和证据强度覆盖情况。
- `bibliometrics.csv`：影响因子、分区、会议层次和引用量；无法核实的内容标记为 `not_verified`。
- `metadata.json`：研究范围、截止日期、纳排标准和统计数量。

简单来说：`review_draft.md` 是给人阅读的综述，其余文件说明这篇综述是怎样检索、筛选和得到结论的。

## 这个仓库里的文件是什么

- `SKILL.md`：Codex 执行文献综述时遵循的核心说明。
- `agents/openai.yaml`：Skill 在 Codex 界面中的名称和默认提示语。
- `scripts/init_review_project.py`：创建空白综述项目。
- `scripts/review_lint.py`：检查项目结构、编号引用和表格关系。
- `scripts/schema.py`：定义各个 CSV 文件的字段。
- `references/`：详细工作流、字段说明和安装说明。
- `examples/`：完整示例项目，可用于了解产物结构。
- `requirements.txt`：运行环境说明；当前脚本只使用 Python 标准库。

通常不需要手动修改 `SKILL.md`、`scripts/` 或 `references/`，也不需要自己填写所有 CSV。正常做法是在 Codex 中调用 `$lit-review-v2`，让它完成工作并返回综述项目。

## 可选：手动运行脚本

需要自己创建项目目录时，可使用 Python 3.10 或更高版本：

```powershell
python .\scripts\init_review_project.py `
  --output "D:\review-project" `
  --topic "your topic" `
  --start-year <start-year> `
  --end-year <end-year> `
  --cutoff-date <YYYY-MM-DD>
```

`D:\review-project` 是示例输出位置，需要替换为自己的目录。填写项目内容后运行：

```powershell
python .\scripts\review_lint.py "D:\review-project"
```

## 证据边界

- 定向检索结果称为 targeted evidence review（目标证据综述），不能声称数据库穷尽覆盖。
- 论文、DOI、结果和 evidence locator（证据定位）必须经过核验。
- 只有摘要或部分正文可用时，必须区分 `verified` 和 `not_verified`。
- 数据集、划分、额外训练数据、模型规模或硬件不一致时，不能直接按指标排名。
- 影响因子、分区和引用量要记录来源与日期；无法核实就保留为 `not_verified`。
