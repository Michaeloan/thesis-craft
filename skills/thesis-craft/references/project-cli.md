# 项目命令与记录格式

Python 3.10+，全部运行依赖为标准库。脚本路径为 scripts/project.py；--project 必须写在子命令之前。命令输出JSON：退出码0为成功，2为输入/状态错误，3为上下文需拆分。

## 命令

```text
project.py --project PATH init
project.py --project PATH import SOURCE [--kind file|pasted] [--profile JSON]
project.py --project PATH context --unit ID --task TEXT [--mode polish|strengthen|structure|review] [--budget 24000] [--start N --end N]
project.py --project PATH record --note NOTE.json [--author-confirmed]
project.py --project PATH record --context ID --candidate FILE [--review REVIEW.json] [--author-confirmed --decision TEXT]
project.py --project PATH record --withdraw RECORD_ID --decision TEXT
project.py --project PATH status
project.py --project PATH resume
project.py --project PATH export --output NEW_DIRECTORY
```

context的块序号从1开始，包含该单元标题。import输出unit ID；index.json提供块文本、位置、flags与hash。context返回上下文文件路径，实际提供给模型的文件应以该文件为准。

每个项目只有一个当前活动来源；新来源会成为新版本，旧来源快照和记录仍保留。源路径或文件内容变化都需重新导入。不要同时调用多个写命令；.lock记录正在操作的进程，异常中断后确认进程已退出再处理锁文件。

## 项目知识记录

复制 assets/note.example.json。kind支持overview/chapter_role/term/fact/decision/style/issue/literature。
- text：本次理解或作者决定；不是自动核验结果。
- status：candidate/confirmed/unresolved；confirmed需要显式作者确认。
- triggers：在当前修改文本中匹配的字面词。
- applies_to：明确适用的unit ID。
- 两者都为空表示全局适用；否则任意命中即纳入。
- source_refs：内部为unit与quote（原文精确摘句）；外部为source与locator。外部引用不自动联网验证。
- id可选；再次使用相同ID更新当前记录，旧事件仍归档。
- style、decision、issue允许无研究来源，但仍不能伪造作者表态。

章节任务通过applies_to关联该章实际unit ID；不是按章号硬编码。被引用内部单元变化会标记needs_recheck。完整项目笔记或旧profile变化会保守地使旧上下文和候选待复核，不尝试猜测这种变更是否无关。

## 检查记录

复制 assets/review.example.json。checks中的各项状态为passed/issue/not_checked，并附note说明实际依据。issues为尚未解决问题的字符串列表。

candidate表示生成候选；checked表示提交者报告表达、论述与口径检查通过；accepted表示显式传入作者决定。三者都不自动代表已回写原文或已验收版面。脚本只核对JSON结构和字面变化，不证明语义判断正确。

同一区段的新记录成为导出的最新候选。部分重叠区段不得自动拼接；先撤回不采用的旧记录。withdraw只退出当前使用，原记录文件保留。

## 磁盘与预算

.thesis-craft内的state.json是状态索引，versions保存来源快照及结构，notes保存笔记事件，contexts保存实际组包，records保存候选。状态索引原子写入；本地文件不是加密存储，不应提交公开仓库。

24000字符按完整context Markdown文件计算；JSON转义等也占预算。它不是token测量。必需材料超限则不给出半截上下文；邻段可因预算省略，但必须列明。单块超限时需提高预算或由作者/智能体明确缩小任务，工具不会任意切句。

## v0.1兼容

audit_text.py、inspect_docx.py命令不变。旧profile通过import --profile读取；此兼容路径会完整纳入profile，过大的旧配置也可能触发拆分。较大的论文知识建议转为有定位与触发词的note记录。
