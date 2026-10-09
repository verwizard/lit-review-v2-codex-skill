# Lit Review v2

`lit-review-v2` 是一个用于构建 **targeted evidence review（目标证据综述）** 的 Codex Skill。它支持候选集构建、两阶段筛选、证据表、主张到文献的追溯、技术路线综合、冲突分析和结构化 lint。

## 安装

将整个 `lit-review-v2` 文件夹复制到用户 Skill 目录。下面的目录是 Windows 的示例位置，`%USERPROFILE%` 会展开为当前用户目录；也可以按本机 Codex 配置使用其他 Skill 目录：

```text
%USERPROFILE%\.codex\skills\lit-review-v2\SKILL.md
```

重新打开 Codex 或刷新 Skill 列表后，使用：

```text
$lit-review-v2
```

## 创建综述项目

需要 Python 3.10 或更高版本；脚本只使用 Python 标准库。

调用 `$lit-review-v2` 时，主题、年份范围、截止日期、文献类型和筛选标准应由用户当前任务提供；Skill 不把下面示例中的任何主题或日期固定下来。命令中的 `D:\review-project` 也是占位输出路径，请替换成希望保存项目的本机目录。

```powershell
python .\scripts\init_review_project.py `
  --output "D:\review-project" `
  --topic "your topic" `
  --start-year <start-year> `
  --end-year <end-year> `
  --cutoff-date <YYYY-MM-DD>
```

完成候选集、筛选和证据表后运行：

```powershell
python .\scripts\review_lint.py "D:\review-project"
```

## 重要边界

- 输出应称为 targeted evidence review（目标证据综述），不要把定向检索描述为系统综述。
- 只能写入已核验的论文、DOI、结果和 evidence locator（证据定位）；部分来源必须区分 `verified` 和 `not_verified`。
- 不要在数据集、划分、额外训练数据、模型规模或硬件不一致时直接排名论文。
- `bibliometrics.csv` 用于带来源和日期的影响因子、分区、会议层次和引用量标注；未核验指标保留为 `not_verified`，不作为硬门槛。
- 用户要求双语术语时，在 Markdown 正文中使用 `English term（中文术语）` 格式；正式论文题名和 venue 名称保持原样。

## 目录

- `SKILL.md`：Skill 主说明
- `agents/openai.yaml`：Codex 界面元数据
- `scripts/`：项目初始化和 lint 脚本
- `references/`：工作流、字段 schema 和安装说明
- `examples/`：示例项目压缩包
