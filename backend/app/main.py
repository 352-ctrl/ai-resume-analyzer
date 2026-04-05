# backend/app/main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.pdf_parser import extract_text_from_pdf
from app.services.ai_analyzer import analyze_resume_with_ai
from app.models import ResumeAnalysisResponse
import hashlib
import json
import redis
import logging

app = FastAPI(title="AI Resume Analyzer API")

# 配置简单的日志输出
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 Redis 客户端 (设置 decode_responses=True 自动将字节解码为字符串)
# 设定一个较短的 socket_timeout，防止未开启 Redis 时请求阻塞过久
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=2
)

def generate_cache_key(file_bytes: bytes, jd_text: str) -> str:
    """生成唯一的缓存 Key：合并文件 MD5 和 岗位需求 MD5"""
    file_md5 = hashlib.md5(file_bytes).hexdigest()
    jd_md5 = hashlib.md5(jd_text.encode('utf-8')).hexdigest()
    return f"resume_eval:{file_md5}:{jd_md5}"

@app.post("/api/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
        file: UploadFile = File(..., description="上传的 PDF 简历文件"),
        job_description: str = Form(..., description="招聘岗位需求文本")
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="仅支持 PDF 格式的文件")

    try:
        file_content = await file.read()

        # --- 1. 尝试命中缓存 ---
        cache_key = generate_cache_key(file_content, job_description)
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.info(f"🚀 命中 Redis 缓存! Key: {cache_key}")
                # 将缓存的 JSON 字符串反序列化为字典直接返回
                return json.loads(cached_data)
        except redis.ConnectionError:
            logger.warning("⚠️ Redis 连接失败，跳过缓存，执行直接计算...")
        except Exception as e:
            logger.warning(f"⚠️ 读取缓存发生未知错误: {str(e)}")

        # --- 2. 缓存未命中，执行深度解析与大模型调用 ---
        logger.info("⏳ 未命中缓存，开始解析 PDF 并调用 DeepSeek...")
        resume_text = extract_text_from_pdf(file_content)

        if not resume_text:
            raise HTTPException(status_code=400, detail="无法从 PDF 中提取文本，请检查文件")

        analysis_result = analyze_resume_with_ai(resume_text, job_description)

        # --- 3. 异步写入缓存 (设置 24 小时过期) ---
        try:
            # 将分析结果序列化为 JSON 字符串存入 Redis，过期时间 86400 秒 (24h)
            redis_client.setex(cache_key, 86400, json.dumps(analysis_result))
            logger.info("✅ 分析结果已成功写入 Redis 缓存")
        except redis.ConnectionError:
            pass # 写入失败不影响正常结果返回

        return analysis_result

    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")