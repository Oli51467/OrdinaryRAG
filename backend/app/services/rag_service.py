import os
from typing import List, Dict, Any, Optional, Tuple

from app.services.document_service import DocumentService
from langchain.schema.document import Document


class RAGService:
    """检索增强生成服务"""
    
    def __init__(self):
        """初始化服务"""
        self.document_service = DocumentService()
    
    def retrieve_relevant_documents(self, query: str, model_type: int, top_k: int = 5) -> List[Tuple[Document, float]]:
        """
        根据用户输入检索相关文档
        
        Args:
            query: 用户输入文本
            model_type: 大模型类型 (1: DeepSeek, 2: Qwen)
            top_k: 返回的相关文档数量
            
        Returns:
            包含文档和相似度分数的列表
        """
        try:
            # 使用向量数据库检索相关文档
            docs_with_scores = self.document_service.search_documents(query, top_k)
            
            # 根据模型类型调整检索结果（可以在此处添加特定于模型的处理逻辑）
            if model_type == 1:
                # DeepSeek模型的处理方式
                pass
            elif model_type == 2:
                # Qwen模型的处理方式
                pass
            
            return docs_with_scores
        except Exception as e:
            print(f"检索相关文档失败: {str(e)}")
            return []
    
    def format_context_for_llm(self, docs_with_scores: List[Tuple[Document, float]]) -> str:
        """
        将检索到的文档格式化为大模型可用的上下文
        
        Args:
            docs_with_scores: 检索到的文档和相似度分数列表
            
        Returns:
            格式化后的上下文文本
        """
        context = ""
        
        for i, (doc, score) in enumerate(docs_with_scores):
            # 添加文档标题（如果可用）
            source = doc.metadata.get("source", "未知来源")
            file_name = doc.metadata.get("file_name", "未知文件")
            
            # 格式化文档内容
            context += f"[文档 {i+1}] 来源: {source}, 文件: {file_name}\n"
            context += f"内容: {doc.page_content}\n"
            context += f"相关度得分: {score:.4f}\n\n"
        
        return context
    
    def generate_rag_prompt(self, query: str, model_type: int, top_k: int = 5) -> str:
        """
        生成RAG的完整提示
        
        Args:
            query: 用户输入文本
            model_type: 大模型类型 (1: DeepSeek, 2: Qwen)
            top_k: 返回的相关文档数量
            
        Returns:
            格式化后的提示文本，可以直接发送给大模型
        """
        # 获取相关文档
        docs_with_scores = self.retrieve_relevant_documents(query, model_type, top_k)
        
        # 如果没有找到相关文档
        if not docs_with_scores:
            return f"用户问题: {query}\n\n没有找到相关文档，请根据您的知识来回答这个问题。"
        
        # 格式化上下文
        context = self.format_context_for_llm(docs_with_scores)
        
        # 根据不同的模型类型构建不同的提示
        prompt_template = ""
        
        if model_type == 1:  # DeepSeek
            prompt_template = f"""请回答下面的问题。请使用以下提供的文档内容来帮助回答，如果文档内容不足以回答问题，请使用您自己的知识。

相关文档:
{context}

用户问题: {query}

请根据以上信息提供详细回答:"""
            
        elif model_type == 2:  # Qwen
            prompt_template = f"""我将提供一些相关文档的内容，请基于这些内容回答我随后的问题。如果文档内容不足以回答问题，请使用您自己的知识。

相关文档内容:
{context}

问题: {query}

回答:"""
            
        else:
            # 默认提示模板
            prompt_template = f"""以下是一些可能与问题相关的文档内容:

{context}

问题: {query}

请基于以上信息提供回答:"""
            
        return prompt_template 