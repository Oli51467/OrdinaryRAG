from service.config import Config
import asyncio
from service.logger import logger
import requests

class LLM:
    def __init__(self, config: Config):
        self.api_key = config.API_KEY
        self.base_url = config.LLM_BASE_URL
        self.model = config.LLM_MODEL
        self.role = "user"
        self.stream = False
        self.max_tokens = 512
        self.temperature = 0.7
        self.top_p = 0.7
        self.top_k = 50
        self.frequency_penalty = 0.5
        self.n = 1
        self.response_format = {"type": "text"}
        self.tools = [
            {
                "type": "function",
                "function": {
                    "description": "<string>",
                    "name": "<string>",
                    "parameters": {},
                    "strict": False
                }
            }
        ]
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    
    def build_llm_request(self, question: str) -> dict:
        payload = {
            "model": self.model,
            "messages": [
                {"role": self.role, "content": question}
            ],
            "stream": self.stream,
            "max_tokens": self.max_tokens,
            "stop": None,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "frequency_penalty": self.frequency_penalty,
            "n": self.n,
            "response_format": self.response_format,
            "tools": self.tools,
        }
        headers = self.headers

        return payload, headers


    def chat_completion(self, payload: dict, headers: dict) -> str:
        try:
            response = requests.post("POST", self.base_url, json=payload, headers=headers)
            # 检查响应
            if response.status_code == 200:
                result = response.json()
                # 提取回复内容
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                   return f"API调用失败: HTTP {response.status_code}, {response.text}"
            else:
                return f"API调用失败: HTTP {response.status_code}, {response.text}"

        except Exception as e:
            logger.error(f"LLM 请求失败: {e}")
            return f"调用模型时出错: {str(e)}" 
    

    async def async_chat_completion(self, question: str) -> str:
        payload, headers = self.build_llm_request(question)
        return await asyncio.to_thread(self.chat_completion, json=payload, headers=headers)
