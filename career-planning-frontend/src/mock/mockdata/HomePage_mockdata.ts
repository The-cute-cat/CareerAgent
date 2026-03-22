/**
 * HomePage.vue 模拟数据
 */

import {
  Upload,
  DocumentChecked,
  DataLine,
  MapLocation
} from '@element-plus/icons-vue'

/** 快捷功能卡片数据 */
export const quickActions = [
  {
    title: '简历填写',
    icon: Upload,
    desc: '点击填写简历信息',
    color: '#409eff',
    route: '/career-form'
  },
  {
    title: '查看匹配',
    icon: DocumentChecked,
    desc: '岗位匹配',
    color: '#67c23a',
    route: '/job-matching'
  },
  {
    title: '生成报告',
    icon: DataLine,
    desc: '生成我的生涯报告',
    color: '#e6a23c',
    route: '/report'
  },
  {
    title: '职业地图',
    icon: MapLocation,
    desc: '查看岗位晋升路线',
    color: '#f56c6c',
    route: '/development-map'
  }
]

/** 首页雷达图模拟数据 */
export const homeRadarData = {
  indicator: [
    { name: '沟通能力', max: 100 },
    { name: '专业技能', max: 100 },
    { name: '团队协作', max: 100 },
    { name: '学习能力', max: 100 },
    { name: '领导力', max: 100 },
    { name: '创新思维', max: 100 }
  ],
  value: [75, 85, 70, 80, 60, 72],
  name: '当前能力'
}
