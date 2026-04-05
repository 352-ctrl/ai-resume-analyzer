from pydantic import BaseModel, Field
from typing import List, Optional

class CandidateInfo(BaseModel):
    name: str = Field(description="候选人姓名")
    phone: str = Field(description="联系电话")
    email: str = Field(description="电子邮箱")
    address: Optional[str] = Field(default="", description="居住地址")

class JobIntention(BaseModel):
    roles: List[str] = Field(default_factory=list, description="求职意向/期望岗位")
    expected_salary: Optional[str] = Field(default="", description="期望薪资")

class Background(BaseModel):
    work_years: Optional[str] = Field(default="", description="工作年限")
    education: List[str] = Field(default_factory=list, description="学历背景")
    projects: List[str] = Field(default_factory=list, description="核心项目经历简述")

class MatchScore(BaseModel):
    overall_score: int = Field(description="综合匹配度评分，满分100")
    skill_match_rate: str = Field(description="技能匹配率评估，例如 '85%'")
    experience_relevance: str = Field(description="工作经验相关性评估描述")
    reason: str = Field(description="AI 给出的评分理由与总结")

class ResumeAnalysisResponse(BaseModel):
    candidate_info: CandidateInfo
    job_intention: JobIntention
    background: Background
    match_analysis: MatchScore