# 作者偏好、项目事实与一次任务要求

配置是可选输入。片段无需填表，不扫描无关目录找偏好。通用示例见 [../assets/profile.example.json](../assets/profile.example.json)。

分开保存四层：
- author_preferences：持续表达偏好，包括输出形式及少用的空泛措辞。
- facts / protected_phrases：本论文确认的数字、完整术语、对象、单位、分母、年份和边界。
- chapter_roles / school_template：本论文目录分工及学校格式，不推广到其他论文。
- decisions / task_constraints：已确认决定与一次任务限制，例如本轮不加附录；后者不自动永久化。

记录事实时保存提供者、来源定位和核验状态。作者确认不等于工具独立核验、模型已重算或数据公开。仅有规则摘要时把来源标为作者提供，不编造具体文献页码。

作者最新明确指令优先。用户指定旧稿做历史测试时，以该旧稿为该轮基线，不能用当前论文锁定值覆盖；只有明确要求按新口径同步旧文才进行更新。发生冲突时展示具体差异，不静默选旧配置或把多个版本混合。

大项目用record --note建立有触发词及原文定位的term/fact/chapter_role/decision。长文记忆中除数字，还保存“估算/实际、可能/确定、何种时期与条件、比较回答什么”。定义先完成核对，再用于润色。检查清单属于内部工作，不强制进入正文。

现有audit_text.py只消费protected_phrases；project.py可将旧profile作为资料装入上下文。JSON字段本身不会强制模型正确执行语义，仍需按polish.md复核。配置没有提及的旧问题不在每轮重复提醒。
