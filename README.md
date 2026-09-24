# 论文守意 · Thesis Craft

**用于中文毕业论文审查与润色的 Agent Skill，帮助长篇修改延续作者的研究口径、论述关系和章节上下文。**

论文写到后期，作者往往知道自己想表达什么，却难以一次写得准确、自然、清楚。通用模型有时会压缩过度、混淆论述与解释，或让不同章节承担相同任务。反复补充上下文、改回原意和重做润色，也会消耗大量时间与 token。

创作论文守意，是希望把审查意见、修改目标和论文上下文连在一起，让每一轮修改都能沿着作者原有的意思继续推进。

## 两大模块

| 发现问题 | 解决问题 |
|---|---|
| 从表达、语义关系、论证、章节推进、证据、计算和文档呈现七个层次定位问题 | 按根因选择修句、重组、补强、迁移、删除、核验或版面修复 |
| 先检查当前版本，识别过期或错误的审查意见 | 保留作者的比较、依据、推论、限定、术语和数据归属 |
| 区分表面症状与根因，并给出改后应达到的状态 | 修改后检查定义、图表、引用、摘要、结论及后文承接 |

## 长论文特色

- **章节推进检查**：核对重要地区、类型、指标和案例是否按“定义与方法—结果—讨论—结论”逐步出现，避免后文突然引入重点对象。
- **版本演化审查**：将历史问题标为已解决、部分解决、仍存在、复发、已变化或当前版本不成立，不把旧意见直接套到新稿。
- **审稿意见核实**：先回到当前正文、计算资料和来源确认意见是否成立，再决定修改；不按意见语气或数量改稿。
- **修改影响追踪**：公式、数字、术语、段落或图表变化后，自动提醒复核相关定义、引用、摘要、结论和交叉引用。
- **安全迁移与删除**：整块删除前先识别独有论据、引文和未完成事项；语义结构不使用跨段正则批量处理。
- **作者风格延续**：记录已认可案例、持续偏好、章节要求和当前任务限制，换会话后仍能继续。

短片段可直接使用，不必建立项目。长论文可导入 DOCX、Markdown 或 UTF-8 文本，按章节整理原文、相关定义、图表和作者决定，并生成候选稿与续接记录。

## 实际润色案例

以下为研究背景中的一段文字，展示如何把抽象的衔接表述改为具体的分析关系。

**修改前**

> 这些任务需要一条从逐栋屋顶资源、适装面积、装机和发电潜力，到碳减排、经济效益、负荷匹配和部署路径的连续证据链。本研究据此开展广州全域逐栋评估，并以建筑功能和屋顶形态作为贯穿资源识别、潜力测算和部署分析的共同接口。

**模型润色示例**

> 上述任务要求将逐栋屋顶资源识别、适装面积估算、装机与发电潜力测算，与碳减排、经济效益、负荷匹配及部署路径分析相衔接。基于此，本研究开展广州全域逐栋评估，并以建筑功能和屋顶形态作为贯穿资源识别、潜力测算与部署分析的统一分类依据。

**改写要点**：将“连续证据链”“共同接口”展开为资源识别、潜力测算及部署分析之间的关系，并说明建筑功能和屋顶形态如何贯穿这些环节。

论文摘录仅用于本案例展示，仍归作者所有，不在本项目 MIT 许可范围内；使用或转载该段落需另获作者许可。详见 [NOTICE.md](NOTICE.md)。

## 安装

下载并解压 [thesis-craft-0.6.0.zip](https://github.com/Michaeloan/thesis-craft/raw/refs/heads/main/dist/thesis-craft-0.6.0.zip)，将其中的 `thesis-craft` 文件夹复制到 Codex 的 Skills 目录：

```powershell
$skillHome = Join-Path $HOME ".codex\skills"
New-Item -ItemType Directory -Force -Path $skillHome | Out-Null
Copy-Item -LiteralPath ".\thesis-craft" -Destination $skillHome -Recurse
```

如果使用自定义 `CODEX_HOME`，请将文件夹放入相应的 `skills` 路径。兼容的智能体也可以直接读取 `skills/thesis-craft/SKILL.md`。

源码包：[thesis-craft-0.6.0-source.zip](https://github.com/Michaeloan/thesis-craft/raw/refs/heads/main/dist/thesis-craft-0.6.0-source.zip)。

## 使用示例

只审查：

> 使用 $thesis-craft 审查这一段，指出具体位置、原文依据和修改建议；先不要改写。

只润色：

> 使用 $thesis-craft 润色这一段，保留作者的论点、术语、比较及数据关系，返回一版可直接使用的正文。

审查并润色：

> 使用 $thesis-craft 检查并润色这部分。依据现有数据和上下文处理表达与论述问题；需要补充依据的地方单独指出。

核实审查意见：

> 使用 $thesis-craft 核实这些审查意见。先检查当前稿和已有依据，区分成立、部分成立和当前版本不成立，再修改确实存在的问题。

版本回顾：

> 使用 $thesis-craft 对照旧稿和当前稿，说明历史问题哪些已解决、哪些仍存在或复发，并把剩余问题转成可执行修改。

长篇论文：

> 使用 $thesis-craft 处理这篇论文。先整理章节结构和研究口径，再按小节读取原文与相关材料。保存候选稿、作者决定和待处理事项，方便后续继续。

## 长论文辅助工具

辅助脚本使用 Python 3.10 或更新版本，仅依赖标准库：

```powershell
python -B skills/thesis-craft/scripts/project.py --project local/my-thesis init
python -B skills/thesis-craft/scripts/project.py --project local/my-thesis import PATH_TO_YOUR_COPY.md
python -B skills/thesis-craft/scripts/project.py --project local/my-thesis status
```

还可以按单元组装上下文、记录候选稿、生成续接说明并导出：

```text
project.py --project PATH context --unit ID --task "审查并润色"
project.py --project PATH record --context CONTEXT_ID --candidate TEXT_FILE --review REVIEW.json
project.py --project PATH resume
project.py --project PATH export --output NEW_DIRECTORY
```

## 项目内容与许可

- `skills/thesis-craft/`：Skill、专项规则和辅助脚本。
- `tools/`：安装包与源码包构建工具。
- `dist/`：可下载的安装包、源码包及文件清单。

项目代码、Skill 规则与项目文档采用 MIT 许可。README 中的论文摘录不随 MIT 许可授权，范围见 [NOTICE.md](NOTICE.md)。
