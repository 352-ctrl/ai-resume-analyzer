# backend/app/services/ai_analyzer.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from app.models import ResumeAnalysisResponse

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def analyze_resume_with_ai(resume_text: str, job_description: str) -> dict:
    """
    调用 DeepSeek 提取简历信息并进行岗位匹配评分
    """
    system_prompt = f"""
    你是一个资深的 HR 专家和技术面试官。你需要分析给定的简历文本，并根据给定的岗位需求进行匹配度评估。
    
    请提取简历中的关键信息，并严格按照以下 JSON 格式输出（不要输出任何额外的 markdown 标记或解释文字）：
    {{
        "candidate_info": {{
            "name": "姓名",
            "phone": "电话",
            "email": "邮箱",
            "address": "地址"
        }},
        "job_intention": {{
            "roles": ["期望岗位1", "期望岗位2"],
            "expected_salary": "期望薪资"
        }},
        "background": {{
            "work_years": "工作年限",
            "education": ["学历1", "学历2"],
            "projects": ["项目1简述", "项目2简述"]
        }},
        "match_analysis": {{
            "overall_score": 85, 
            "skill_match_rate": "80%",
            "experience_relevance": "经验相关性描述",
            "reason": "综合评分理由"
        }}
    }}
    
    岗位需求：
    {job_description}
    """

    user_prompt = f"以下是提取清洗后的简历文本：\n{resume_text}"

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}, # 强制输出 JSON
            temperature=0.3 # 降低随机性，保证结构化数据稳定提取
        )

        # 解析返回的 JSON 字符串
        result_json = json.loads(response.choices[0].message.content)
        return result_json
    except Exception as e:
        raise ValueError(f"AI 分析过程出错: {str(e)}")