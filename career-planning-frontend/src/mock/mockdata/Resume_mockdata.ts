/**
 * 简历上传接口模拟数据
 * 用于测试简历上传、解析、填充表单、提交表单的完整流程
 *
 * 流程：上传简历 → 返回表单数据（部分为空）→ 填充到表单 → 提交表单 → 返回 JobMatchResult → 跳转展示
 */

import type { Result } from '@/types/type'
import type { JobMatchItem } from '@/types/job-match'
import type { UploadResponse } from '@/types/careerform_report'
import { mockJobMatchItems } from './JobMatch_mockdata'
import type { AxiosResponse } from 'axios'

/**
 * 将 Result 包装为 AxiosResponse 格式，与真实 API 保持一致
 */
function wrapAsAxiosResponse<T>(result: Result<T>): AxiosResponse<Result<T>> {
  return {
    data: result,
    status: 200,
    statusText: 'OK',
    headers: {},
    config: {} as any
  }
}

// ==================== 1. 简历上传接口模拟数据 ====================

/**
 * 模拟场景1：简历解析成功，返回完整表单数据
 * 用于测试正常流程 - 直接返回表单数据格式
 */
export const mockResumeUploadSuccess: Result<UploadResponse> = {
  code: 200,
  msg: '简历解析成功',
  data: {
    education: '本科',
    educationOther: '',
    major: ['计算机类', '软件工程'],
    graduationDate: '2025-06',
    languages: [
      { type: '英语', level: 'CET-6', other: '' }
    ],
    certificates: ['CET-6', '软件设计师'],
    certificateOther: '',
    skills: [
      { name: 'Java', score: 85 },
      { name: 'Spring Boot', score: 80 },
      { name: 'MySQL', score: 75 },
      { name: 'Redis', score: 70 },
      { name: 'Vue.js', score: 65 },
      { name: 'Docker', score: 60 }
    ],
    tools: [
      { name: 'Git', score: 85 },
      { name: 'IntelliJ IDEA', score: 90 },
      { name: 'VS Code', score: 85 }
    ],
    codeAbility: { links: 'https://github.com/zhangsan' },
    projects: [
      {
        isCompetition: false,
        name: '电商平台后端系统',
        desc: '负责订单模块的设计与开发，使用Spring Boot + MySQL + Redis技术栈，支持高并发场景'
      },
      {
        isCompetition: true,
        name: '校园二手交易平台',
        desc: '获得校级创新创业大赛二等奖，负责整体架构设计和核心功能开发'
      }
    ],
    internships: [
      {
        company: 'ABC科技有限公司',
        role: 'Java开发工程师',
        date: [],
        desc: '参与公司核心业务系统开发，负责订单管理模块的设计与实现'
      }
    ],
    quizDetail:undefined,
    innovation: '通过引入Redis缓存和数据库索引优化，将系统查询性能提升30%',
    targetJob: '', // 故意留空，测试必填检测
    targetIndustries: [], // 故意留空，测试必填检测
    priorities: [
      { value: 'tech', label: '技术成长' },
      { value: 'salary', label: '薪资' },
      { value: 'stable', label: '稳定' }
    ]
  }
}

/**
 * 模拟场景2：简历解析成功，但部分字段缺失
 * 用于测试缺失字段提醒功能 - 直接返回表单数据格式
 */
export const mockResumeUploadPartial: Result<UploadResponse> = {
  code: 200,
  msg: '简历上传成功，部分字段解析失败',
  data: {
    education: '本科',
    major: [], // 缺失
    graduationDate: '', // 缺失
    languages: [], // 缺失
    certificates: [],
    certificateOther: '',
    skills: [
      { name: 'Python', score: 75 },
      { name: '数据分析', score: 70 }
    ],
    tools: [],
    codeAbility: { links: '' },
    projects: [],
    internships: [],
    quizDetail:undefined,
    innovation: '', // 缺失
    targetJob: '', // 缺失
    targetIndustries: [], // 缺失
    priorities: [
      { value: 'tech', label: '技术成长' },
      { value: 'salary', label: '薪资' },
      { value: 'stable', label: '稳定' }
    ]
  }
}

/**
 * 模拟场景3：异步解析模式（解析耗时较长）
 * 用于测试轮询获取结果 - 返回空对象，表示正在处理
 */
export const mockResumeUploadProcessing: Result<UploadResponse> = {
  code: 200,
  msg: '简历上传成功，正在解析中',
  data: {}  // 空对象表示正在处理中
}

/**
 * 模拟场景4：简历解析失败
 * 用于测试错误处理 - 返回空对象
 */
export const mockResumeUploadFailed: Result<UploadResponse> = {
  code: 200,
  msg: '简历上传成功，但解析失败',
  data: {}  // 空对象表示解析失败
}

// ==================== 2. 错误响应模拟数据 ====================

/**
 * 模拟401未登录错误
 */
export const mockErrorUnauthorized: Result<null> = {
  code: 401,
  msg: '登录已过期，请重新登录',
  data: null
}

/**
 * 模拟413文件过大错误
 */
export const mockErrorFileTooLarge: Result<null> = {
  code: 413,
  msg: '文件过大，请上传小于5MB的文件',
  data: null
}

/**
 * 模拟500服务器错误
 */
export const mockErrorServerError: Result<null> = {
  code: 500,
  msg: '服务器繁忙，请稍后重试',
  data: null
}

// ==================== 3. 模拟API函数 ====================

/**
 * 模拟延迟
 * @param ms 延迟毫秒数
 */
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * 模拟简历上传接口
 * @param fileName 文件名
 * @param scenario 模拟场景：'success' | 'partial' | 'processing' | 'failed'
 * @param delayMs 延迟时间（毫秒）
 */
export async function mockUploadResumeApi(
  fileName: string | string[],
  scenario: 'success' | 'partial' | 'processing' | 'failed' = 'success',
  delayMs: number = 1500
): Promise<AxiosResponse<Result<UploadResponse>>> {
  await delay(delayMs)

  switch (scenario) {
    case 'partial':
      return wrapAsAxiosResponse(mockResumeUploadPartial)
    case 'processing':
      return wrapAsAxiosResponse(mockResumeUploadProcessing)
    case 'failed':
      return wrapAsAxiosResponse(mockResumeUploadFailed)
    case 'success':
    default:
      return wrapAsAxiosResponse(mockResumeUploadSuccess)
  }
}

/**
 * 模拟提交表单接口
 * 直接返回人岗匹配结果，无需轮询
 * @param scenario 模拟场景
 * @param delayMs 延迟时间（毫秒）
 */
export async function mockSubmitFormApi(
  scenario: 'success' | 'validation_error' = 'success',
  delayMs: number = 1000
): Promise<AxiosResponse<Result<JobMatchItem[]>>> {
  await delay(delayMs)

  if (scenario === 'validation_error') {
    return wrapAsAxiosResponse({
      code: 400,
      msg: '表单验证失败，请检查必填字段',
      data: null as unknown as JobMatchItem[]
    })
  }

  // 返回人岗匹配结果
  return wrapAsAxiosResponse({
    code: 200,
    msg: '提交成功',
    data: mockJobMatchItems
  })
}

// ==================== 4. 导出所有模拟数据 ====================

export default {
  // 静态数据
  mockResumeUploadSuccess,
  mockResumeUploadPartial,
  mockResumeUploadProcessing,
  mockResumeUploadFailed,
  mockErrorUnauthorized,
  mockErrorFileTooLarge,
  mockErrorServerError,

  // 模拟API函数
  mockUploadResumeApi,
  mockSubmitFormApi
}
