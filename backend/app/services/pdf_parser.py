import fitz
import re

def extract_text_from_pdf(file_content: bytes) -> str:
    """
    解析 PDF 字节流，提取文本并进行基础清洗
    """
    text = ""
    try:
        # 打开 PDF 文件流
        with fitz.open(stream=file_content, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text("text") + "\n"

        # 文本清洗去重逻辑
        # 1. 替换多个连续空格为单个空格
        text = re.sub(r'[ \t]+', ' ', text)
        # 2. 替换多个连续换行符为单个换行符
        text = re.sub(r'\n{2,}', '\n', text)
        # 3. 去除首尾空白字符
        text = text.strip()

        return text
    except Exception as e:
        raise ValueError(f"PDF 解析失败: {str(e)}")