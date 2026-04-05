<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const uploadRef = ref(null)
const file = ref(null)
const jobDescription = ref('急招全栈开发实习生，要求熟练掌握 Vue 3、Spring Boot 开发，具备后端环境治理、全链路质量保障及自动化测试（如构建 100% 核心模块覆盖率）经验者优先。')
const loading = ref(false)
const result = ref(null)

// 捕获文件变化，阻止自动上传，存入本地 ref
const handleFileChange = (uploadFile) => {
  file.value = uploadFile.raw
}

// 超出限制提示
const handleExceed = () => {
  ElMessage.warning('一次只能上传一份简历，请先删除已上传文件')
}

const analyzeResume = async () => {
  if (!file.value) {
    ElMessage.error('请上传 PDF 简历文件')
    return
  }
  if (!jobDescription.value.trim()) {
    ElMessage.error('请填写岗位需求文本')
    return
  }

  loading.value = true
  result.value = null

  const formData = new FormData()
  formData.append('file', file.value)
  formData.append('job_description', jobDescription.value)

  try {
    const response = await axios.post('http://127.0.0.1:8000/api/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    result.value = response.data
    ElMessage.success('简历分析完成！')
  } catch (err) {
    console.error(err)
    ElMessage.error(err.response?.data?.detail || '分析失败，请检查后端服务')
  } finally {
    loading.value = false
  }
}

// 动态判断匹配度颜色
const customColors = [
  { color: '#f56c6c', percentage: 40 },
  { color: '#e6a23c', percentage: 70 },
  { color: '#5cb87a', percentage: 100 },
]
</script>

<template>
  <div class="app-container">
    <el-row :gutter="20" justify="center">
      <el-col :xs="24" :sm="20" :md="16" :lg="14">
        <div class="header">
          <h1>🚀 AI 赋能智能简历分析系统</h1>
          <p class="subtitle">Sidereus AI 实习选拔专用工具</p>
        </div>

        <el-card shadow="hover" class="box-card">
          <el-form label-position="top">
            <el-form-item label="1. 上传候选人简历 (仅支持 PDF)">
              <el-upload
                  ref="uploadRef"
                  class="upload-demo"
                  drag
                  action="#"
                  :auto-upload="false"
                  :limit="1"
                  accept=".pdf"
                  :on-change="handleFileChange"
                  :on-exceed="handleExceed"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  拖拽文件到此处或 <em>点击上传</em>
                </div>
              </el-upload>
            </el-form-item>

            <el-form-item label="2. 输入招聘岗位需求 (JD)">
              <el-input
                  v-model="jobDescription"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入具体的岗位要求、技术栈和加分项..."
              />
            </el-form-item>

            <el-button
                type="primary"
                size="large"
                @click="analyzeResume"
                :loading="loading"
                class="submit-btn"
                icon="Monitor"
            >
              {{ loading ? 'DeepSeek 深度分析中...' : '开始 AI 智能匹配分析' }}
            </el-button>
          </el-form>
        </el-card>

        <el-card v-if="result" shadow="always" class="result-card">
          <template #header>
            <div class="card-header">
              <span class="result-title">📊 智能评估报告</span>
            </div>
          </template>

          <el-row :gutter="20">
            <el-col :span="8" class="score-section">
              <el-progress
                  type="dashboard"
                  :percentage="result.match_analysis.overall_score"
                  :color="customColors"
              >
                <template #default="{ percentage }">
                  <span class="percentage-value">{{ percentage }}分</span>
                  <span class="percentage-label">综合匹配度</span>
                </template>
              </el-progress>
              <div class="match-tags">
                <el-tag type="success">技能匹配: {{ result.match_analysis.skill_match_rate }}</el-tag>
              </div>
            </el-col>

            <el-col :span="16">
              <el-descriptions title="候选人画像" :column="2" border size="small">
                <el-descriptions-item label="姓名">{{ result.candidate_info.name }}</el-descriptions-item>
                <el-descriptions-item label="电话">{{ result.candidate_info.phone }}</el-descriptions-item>
                <el-descriptions-item label="邮箱" :span="2">{{ result.candidate_info.email }}</el-descriptions-item>
                <el-descriptions-item label="教育背景" :span="2">
                  <div v-for="(edu, index) in result.background.education" :key="index">{{ edu }}</div>
                </el-descriptions-item>
                <el-descriptions-item label="期望岗位">
                  {{ result.job_intention.roles.join(', ') || '未提供' }}
                </el-descriptions-item>
              </el-descriptions>
            </el-col>
          </el-row>

          <el-divider />

          <div class="ai-reasoning">
            <h3>🤖 AI 评估与建议</h3>
            <el-alert
                :title="result.match_analysis.reason"
                type="info"
                :closable="false"
                show-icon
            />
            <h4 style="margin-top: 15px;">核心项目经历提取：</h4>
            <ul style="color: #606266; font-size: 14px; line-height: 1.6;">
              <li v-for="(proj, index) in result.background.projects" :key="index">
                {{ proj }}
              </li>
            </ul>
          </div>
        </el-card>

      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.app-container {
  padding: 40px 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.header {
  text-align: center;
  margin-bottom: 30px;
}
.header h1 {
  margin: 0;
  color: #303133;
}
.subtitle {
  color: #909399;
  margin-top: 5px;
}
.box-card, .result-card {
  margin-bottom: 20px;
  border-radius: 8px;
}
.submit-btn {
  width: 100%;
  margin-top: 10px;
}
.score-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.percentage-value {
  display: block;
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}
.percentage-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
.match-tags {
  margin-top: 15px;
}
.ai-reasoning {
  margin-top: 20px;
}
</style>