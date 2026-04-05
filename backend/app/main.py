from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.pdf_parser import extract_text_from_pdf
from app.services.ai_analyzer import analyze_resume_with_ai
from app.models import ResumeAnalysisResponse

app = FastAPI(title="AI Resume Analyzer API")

# 配置 CORS，允许 Vue 前端调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 生产环境需替换为实际前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
        file: UploadFile = File(..., description="上传的 PDF 简历文件"),
        job_description: str = Form(..., description="招聘岗位需求文本")
):
    # 1. 校验文件类型
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="仅支持 PDF 格式的文件")

    try:
        # 2. 读取并解析 PDF
        file_content = await file.read()
        resume_text = extract_text_from_pdf(file_content)

        if not resume_text:
            raise HTTPException(status_code=400, detail="无法从 PDF 中提取文本，请检查文件")

        # 3. 调用 AI 进行分析
        analysis_result = analyze_resume_with_ai(resume_text, job_description)

        # 4. 返回结果 (FastAPI 会自动根据 Pydantic 模型进行校验和序列化)
        return analysis_result

    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")