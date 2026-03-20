/**
 * UserStuInfo
 */
export interface UserStuInfo {
  /**
   * 就业意愿描述
   */
  career_intention?: null | string
  /**
   * 创建时间
   */
  create_time?: Date | null
  /**
   * 学历: 本科, 硕士, 博士
   */
  edu_level?: null | string
  /**
   * gitee_name
   */
  gitee_name?: null | string
  /**
   * github_name
   */
  github_name?: null | string
  /**
   * 毕业年份
   */
  grad_year?: number | null
  /**
   * 学生学历信息表
   */
  id?: number
  /**
   * 逻辑删除-1表示逻辑删除
   */
  is_deleted?: number | null
  /**
   * 专业
   */
  major?: null | string
  /**
   * 真实姓名
   */
  real_name?: null | string
  /**
   * 就读高校
   */
  school?: null | string
  /**
   * 入学年份（如 2023）
   */
  start_year?: null | string
  /**
   * 修改时间
   */
  update_time?: Date | null
  /**
   * 关联sys_user ID
   */
  user_id?: number
  [property: string]: any
}
