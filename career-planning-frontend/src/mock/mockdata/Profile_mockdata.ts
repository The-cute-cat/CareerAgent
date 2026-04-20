/**
 * Profile.vue 测试数据
 */

/**
 * 进度条颜色配置（Element Plus 格式）
 * 与 DevelopmentMap_mockdata.ts 共用
 */
export const progressColors = [
  { color: '#409eff', percentage: 0 },
  { color: '#67c23a', percentage: 100 },
]

/** 学历选项 */
export const educationLevels = [
  { label: '专科', value: 'college' },
  { label: '本科', value: 'bachelor' },
  { label: '硕士', value: 'master' },
  { label: '博士', value: 'doctor' },
]

/** 毕业年份选项（2024-2035年） */
export const graduationYearOptions = Array.from({ length: 12 }, (_, i) => {
  const year = 2024 + i
  return {
    label: `${year} 年`,
    value: year,
  }
})

/** 个人档案表单测试数据 */
export const profileFormData = {
  id: 1001,
  userId: 1001,
  realName: '李明',
  github: 'https://github.com/',
  gitee: 'https://gitee.com/',
  school: 'XX 大学',
  major: '计算机科学与技术',
  startYear: 2024,
  graduationYear: 2028,
  careerIntention: '想从事前端开发工作',
  email: 'liming@example.com',
  phone: '138****8888',
  bio: '985 院校背景，GPA 前 5%，热爱编程和技术研究',
}

/** 隐私设置测试数据 */
export const privacySettingsData = {
  resumeVisibility: 'private' as const,
  profileVisibility: 'private' as const,
  careerPathVisibility: 'public' as const,
  allowRecommendations: true,
  allowCompanyView: false,
}
