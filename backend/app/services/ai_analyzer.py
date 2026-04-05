from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com" # 注意参考 DeepSeek 官方文档确认 endpoint
)

# 后续的调用逻辑：传入 PDF 清洗后的文本和招聘岗位需求，要求输出严格的 JSON