# -*- coding: utf-8 -*-


# 用于扩展原始问题的Prompt
def build_rewrite_prompt(original_question: str, question_rewrite_num: int) -> str:
    """
    根据 question_rewrite_num 动态生成 JSON 数组格式，用于请求 LLM 扩展问题。
    """
    prompt = f"""
你是一个智能助手，负责对用户的原问题进行重写扩展。
请阅读用户的问题，然后重新组织并扩展成 {question_rewrite_num} 个不同问法。
用户问题：{original_question}

请按如下 **严格格式** 返回结果。请不要包含任何解释或注释，也不要使用 Markdown 代码块，请直接返回 JSON：

[
"""
    for i in range(question_rewrite_num):
        prompt += f"""  {{
    "type": "rewrite",
    "question": "重写问题{i+1}"
  }}"""
        if i < question_rewrite_num - 1:
            prompt += ",\n"
        else:
            prompt += "\n"
    prompt += "]"""
    return prompt


# 判断是否需检索知识库的Prompt
CHAT_PROMPT_TEMPLATE = """你是一个智能助手，负责判断给定内容是否与用户的问题存在相关性。  
知识库涵盖计算机科学、深度学习、机器学习、人工智能、数据科学、编程语言、软件工程、网络技术、硬件系统、服务器、大数据分析、云计算等领域。
对于提及但未明确列出的主题，如游戏私服、破解软件、办公工具、资源检索、科学上网等等，也可以灵活的将其视为为相关领域，判定尽可能宽松一些。

问题：
{query}

判断标准：
1. 如果内容与问题直接相关，回答“是”。
2. 如果内容与问题属于同一大类、父级或子级主题，回答“是”。
3. 如果内容与问题之间存在一定的语义关联、可以提供间接帮助，或可能涉及用户需求的上下游问题，回答“是”。
4. 如果内容包含技术性讨论，与问题相关性模糊但可能有潜在联系，回答“是”。
5. 如果内容与问题完全无关，回答“否”。

请根据以上标准仅回答“是”或“否”。 
"""


# 用于判断文档片段与用户问题相关性的Prompt
RELEVANT_PROMPT_TEMPLATE = """你是一个智能助手，负责判断给定的文档片段是否对回答用户的问题有帮助，要求不要太严格，文档片段符合问题的片段上下文即可。
文档片段：
{chunk_text}

问题：
{query}

请回答：这段文档对回答问题有帮助吗？请仅回答“是”或“否”。"""


# 用于生成答案的Prompt
ANSWER_PROMPT_TEMPLATE = """你是一个智能助手，你需要从知识库中选择相关信息来回答用户的问题。在回答时，请特别注意以下几点：

1. **图片链接处理**：如果回答中涉及Markdown格式的图片链接，如果相关，请务必保留这些图片链接，并确保它们出现在相关内容的上下文中。
   - 图片通常是对于上文的文本内容的补充，每个图片链接应紧跟在其相关文本之后，且确保该图片的作用和上下文内容相匹配。
   - 图片名称能够提供提示作用，请根据上下文判断它是展示示意图、结果图还是其他类型的图片，并按照需要调整图片的位置。

2. **知识库内容使用**：请尽量从知识库中提取出准确和相关的信息，构建回答时避免遗漏关键细节。保证回答简洁、准确且具有针对性。

3. **输出格式**：请确保你的回答格式清晰，图像和文本在语义上是连贯的。确保不丢失任何相关内容，并尽可能详细地保留配图描述。不要使用Markdown格式。

4. **特别注意**：不要返回任何链接和外部图片链接

## 当前日期：{current_date}

## 知识库：\n\n{kb_text}"""