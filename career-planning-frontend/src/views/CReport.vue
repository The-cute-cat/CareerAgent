<template>
  <div class="career-report-page">
    <!-- 顶部导航栏 -->
    <nav class="top-nav">
      <div class="nav-brand">
        <span class="nav-logo">📊</span>
        <span class="nav-title">Career Planning</span>
      </div>
      <div class="nav-actions">
        <el-button type="primary" :icon="Edit" @click="openEditor(selectedSection)">编辑报告</el-button>
        <el-button :icon="Check" @click="runCompletenessCheck">完整性检查</el-button>
        <el-button :icon="MagicStick" @click="polishAllSections">AI 润色</el-button>
        <el-button :icon="DocumentChecked" @click="handleSave">保存</el-button>
        <el-button type="success" :icon="Document" @click="exportPdf">导出 PDF</el-button>
        <el-button type="warning" :icon="DocumentCopy" @click="exportWord">导出 Word</el-button>
      </div>
    </nav>

    <!-- Hero 区域 -->
    <section class="hero-panel">
      <div class="hero-content">
        <div class="hero-badge">
          <el-icon><Trophy /></el-icon>
          <span>AI 生成报告</span>
        </div>
        <h1>{{ report.target_position || '职业发展报告' }}</h1>
        <p class="hero-desc">
          结构化展示职业目标、能力差距、短中期路径规划与行动建议，支持智能润色和一键导出
        </p>
        <div class="hero-meta">
          <span class="meta-item">
            <el-icon><Calendar /></el-icon>
            {{ new Date().toLocaleDateString('zh-CN') }}
          </span>
          <span class="meta-item">
            <el-icon><Timer /></el-icon>
            完整度 {{ completenessScore }}%
          </span>
        </div>
      </div>

      <div class="hero-export hero-export--summary">
        <div class="export-title">报告状态</div>
        <div class="hero-summary-mini">
          <span>目标岗位：{{ reportWorkbenchSummary.targetPosition }}</span>
          <span>导出范围：仅正文工作区</span>
        </div>
      </div>
    </section>

    <section class="summary-strip summary-strip--workbench">
      <article class="summary-card">
        <span>目标岗位</span>
        <strong>{{ reportWorkbenchSummary.targetPosition }}</strong>
      </article>
      <article class="summary-card">
        <span>优势摘要</span>
        <p>{{ reportWorkbenchSummary.advantage }}</p>
      </article>
      <article class="summary-card">
        <span>关键差距</span>
        <p>{{ reportWorkbenchSummary.gap }}</p>
      </article>
      <article class="summary-card">
        <span>短期最重要行动</span>
        <p>{{ reportWorkbenchSummary.shortAction }}</p>
      </article>
      <article class="summary-card">
        <span>中期发展方向</span>
        <p>{{ reportWorkbenchSummary.midDirection }}</p>
      </article>
    </section>

    <!-- 数据概览卡片 -->
    <section class="stats-grid">
      <article class="stat-card stat-card--primary">
        <div class="stat-icon"><el-icon><Flag /></el-icon></div>
        <div class="stat-info">
          <span class="stat-label">短期里程碑</span>
          <strong class="stat-value">{{ report.short_term_plan.milestones.length }}</strong>
        </div>
      </article>
      <article class="stat-card stat-card--success">
        <div class="stat-icon"><el-icon><Aim /></el-icon></div>
        <div class="stat-info">
          <span class="stat-label">中期里程碑</span>
          <strong class="stat-value">{{ report.mid_term_plan.milestones.length }}</strong>
        </div>
      </article>
      <article class="stat-card stat-card--warning">
        <div class="stat-icon"><el-icon><OfficeBuilding /></el-icon></div>
        <div class="stat-info">
          <span class="stat-label">推荐实习</span>
          <strong class="stat-value">{{ report.mid_term_plan.recommended_internships.length }}</strong>
        </div>
      </article>
      <article class="stat-card stat-card--info">
        <div class="stat-icon">
          <el-progress type="circle" :percentage="progressPercent" :width="48" :stroke-width="4" color="#fff" />
        </div>
        <div class="stat-info">
          <span class="stat-label">行动完成度</span>
          <strong class="stat-value">{{ progressPercent }}%</strong>
        </div>
      </article>
    </section>

    <div class="report-layout">
      <main class="report-main">
        <section class="report-outline">
          <div class="outline-head">
            <div>
              <p class="section-group-kicker">Report Outline</p>
              <h2>报告目录</h2>
            </div>
            <span class="section-group-desc">点击即可快速跳转到对应章节，导出时不会包含此导航。</span>
          </div>
          <div class="outline-links">
            <button
              v-for="anchor in reportSectionAnchors"
              :key="anchor.key"
              type="button"
              class="outline-chip"
              @click="scrollToReportSection(anchor.id)"
            >
              {{ anchor.label }}
            </button>
          </div>
        </section>

        <div ref="reportRef" class="report-canvas report-export-surface">
          <div class="section-group-header">
            <div>
              <p class="section-group-kicker">Module 01</p>
              <h2>职业画像</h2>
            </div>
            <span class="section-group-desc">聚焦目标岗位、个人画像与核心差距。</span>
          </div>
          <div class="section-summary-bar">
            <div v-for="item in moduleHighlights.profile" :key="item" class="section-summary-item">
              {{ item }}
            </div>
          </div>
          <section id="report-profile" class="report-section section-grid">
            <article class="content-card content-card--wide">
              <div class="card-head">
                <div>
                  <p class="card-kicker">Profile</p>
                  <h2>学生画像摘要</h2>
                  <span class="card-subtitle">章节结论：明确当前背景优势与目标岗位的匹配起点。</span>
                </div>
                <el-button text type="primary" @click="openEditor('student_summary')">编辑</el-button>
              </div>
              <div class="rich-preview" v-html="richContent.student_summary" />
            </article>

            <article id="report-gap" class="content-card">
              <div class="card-head">
                <div>
                  <p class="card-kicker">Gap</p>
                  <h2>能力差距分析</h2>
                  <span class="card-subtitle">章节结论：先看最大差距，再看补齐路径。</span>
                </div>
                <div class="inline-actions">
                  <el-button text @click="polishOneSection('current_gap')">润色</el-button>
                  <el-button text type="primary" @click="openEditor('current_gap')">编辑</el-button>
                </div>
              </div>
              <div class="rich-preview" v-html="richContent.current_gap" />
            </article>
          </section>

          <div class="section-group-header">
            <div>
              <p class="section-group-kicker">Module 02</p>
              <h2>路径规划</h2>
            </div>
            <span class="section-group-desc">梳理短中期发展路径、里程碑与阶段成果。</span>
          </div>
          <div class="section-summary-bar">
            <div v-for="item in moduleHighlights.short" :key="item" class="section-summary-item">
              {{ item }}
            </div>
          </div>
          <section id="report-short" class="report-section">
            <article class="content-card">
              <div class="card-head">
                <div>
                  <p class="card-kicker">Short Term</p>
                  <h2>短期行动计划</h2>
                  <span class="card-subtitle">{{ report.short_term_plan.duration }}</span>
                </div>
                <div class="inline-actions">
                  <el-button text @click="polishOneSection('short_goal')">润色目标</el-button>
                  <el-button text type="primary" @click="openEditor('short_goal')">编辑目标</el-button>
                </div>
              </div>

              <div class="goal-box">
                <span class="goal-label">阶段目标</span>
                <div class="rich-preview" v-html="richContent.short_goal" />
              </div>

              <div class="chip-block">
                <span class="block-title">重点领域</span>
                <div v-if="report.short_term_plan.focus_areas.length" class="chip-list">
                  <el-tag v-for="item in report.short_term_plan.focus_areas" :key="item" round>
                    {{ item }}
                  </el-tag>
                </div>
                <el-empty v-else description="暂无重点领域" :image-size="60" />
              </div>

              <div class="milestone-block">
                <span class="block-title">短期里程碑</span>
                <div v-if="!report.short_term_plan.milestones.length" class="empty-state">
                  <el-empty description="暂无里程碑数据" :image-size="80">
                    <el-button type="primary" text @click="openEditor('short_goal')">添加目标</el-button>
                  </el-empty>
                </div>
                <div v-else class="milestone-stack">
                  <article
                    v-for="milestone in report.short_term_plan.milestones"
                    :key="milestone.milestone_name"
                    class="milestone-card"
                  >
                    <div class="milestone-head">
                      <div>
                        <h3>{{ milestone.milestone_name }}</h3>
                        <span>{{ milestone.target_date }}</span>
                      </div>
                    </div>

                    <div class="milestone-body">
                      <div class="result-box">
                        <span class="mini-title">关键成果</span>
                        <ul class="plain-list">
                          <li v-for="result in milestone.key_results" :key="result">{{ result }}</li>
                        </ul>
                      </div>

                      <div class="task-grid">
                        <article v-for="task in milestone.tasks" :key="task.task_name" class="task-card">
                          <div class="task-top">
                            <strong>{{ task.task_name }}</strong>
                            <el-tag :type="priorityType(task.priority)" size="small" round>
                              {{ task.priority }}优先级</el-tag>
                          </div>

                          <div class="task-meta">
                            <span>预计时间：{{ task.estimated_time }}</span>
                            <span>目标能力：{{ task.skill_target }}</span>
                          </div>

                          <p class="task-desc">{{ task.description }}</p>

                          <div class="task-bottom">
                            <div>
                              <span class="mini-title">成功标准</span>
                              <p>{{ task.success_criteria }}</p>
                            </div>
                            <el-button
                              v-if="getTaskResources(task).length"
                              size="small"
                              @click="openResourceList(getTaskResources(task))"
                            >
                              查看资源（{{ getTaskResources(task).length }}）</el-button>
                            <el-tag v-else size="small" type="info" round>暂无资源</el-tag>
                          </div>
                        </article>
                      </div>
                    </div>
                  </article>
                </div>
              </div>

              <div class="timeline-block">
                <span class="block-title">快速见效行动</span>
                <el-timeline v-if="report.short_term_plan.quick_wins.length">
                  <el-timeline-item
                    v-for="(item, index) in report.short_term_plan.quick_wins"
                    :key="item"
                    :type="index === 0 ? 'primary' : 'info'"
                    hollow
                  >
                    <span class="timeline-item-text">{{ item }}</span>
                  </el-timeline-item>
                </el-timeline>
                <div v-else class="empty-state">
                  <el-empty description="暂无快速行动" :image-size="60" />
                </div>
              </div>
            </article>
          </section>

          <section id="report-resources" class="report-section">
            <article class="content-card">
              <div class="card-head">
                <div>
                  <p class="card-kicker">Resources</p>
                  <h2>推荐资源概览</h2>
                  <span class="card-subtitle">章节结论：优先使用与当前里程碑直接关联的学习资源，减少无效学习。</span>
                </div>
                <el-tag round type="primary">{{ aggregatedResources.length }} 项资源</el-tag>
              </div>

              <div class="goal-box resource-section-note">
                <span class="goal-label">资源说明</span>
                <p class="detail-block">
                  本节自动汇总短期与中期任务中已关联的推荐资源，方便在导出前统一检查学习材料是否完整。
                </p>
              </div>

              <div v-if="aggregatedResources.length" class="resource-overview-grid">
                <article
                  v-for="item in aggregatedResources"
                  :key="item.id"
                  class="resource-card resource-overview-card"
                >
                  <div class="resource-card-top">
                    <div>
                      <h3 class="resource-title">{{ resourceTitle(item) }}</h3>
                      <p class="resource-sub">{{ resourceType(item) }}</p>
                    </div>
                    <el-tag size="small" round type="info">{{ item.originLabel }}</el-tag>
                  </div>

                  <p class="resource-text">{{ item.reason || item.description || item.content || '暂无说明' }}</p>

                  <div class="resource-overview-meta">
                    <span>关联任务：{{ item.taskName || '未标注任务' }}</span>
                    <span>阶段：{{ item.planLabel }}</span>
                  </div>

                  <div class="internship-actions">
                    <el-button size="small" @click="openResourceList([item.raw])">查看详情</el-button>
                    <el-button
                      v-if="item.raw.url"
                      size="small"
                      type="primary"
                      plain
                      @click="openLink(item.raw.url)"
                    >
                      打开链接
                    </el-button>
                  </div>
                </article>
              </div>

              <div v-else class="empty-state resource-overview-empty">
                <el-empty description="当前里程碑中暂无推荐资源" :image-size="72">
                  <template #description>
                    <span>可在编辑页的任务资源中补充课程、书籍、项目仓库等学习材料。</span>
                  </template>
                </el-empty>
              </div>
            </article>
          </section>

          <div class="section-summary-bar section-summary-bar--mid">
            <div v-for="item in moduleHighlights.mid" :key="item" class="section-summary-item">
              {{ item }}
            </div>
          </div>
          <section id="report-mid" class="report-section">
            <article class="content-card">
              <div class="card-head">
                <div>
                  <p class="card-kicker">Mid Term</p>
                  <h2>中期路径规划</h2>
                  <span class="card-subtitle">{{ report.mid_term_plan.duration }}</span>
                </div>
                <div class="inline-actions">
                  <el-button text @click="polishOneSection('mid_goal')">润色目标</el-button>
                  <el-button text type="primary" @click="openEditor('mid_goal')">编辑目标</el-button>
                </div>
              </div>

              <div class="goal-box">
                <span class="goal-label">阶段目标</span>
                <div class="rich-preview" v-html="richContent.mid_goal" />
              </div>

              <div class="roadmap-block">
                <span class="block-title">技能路线图</span>
                <div v-if="!report.mid_term_plan.skill_roadmap.length" class="empty-state">
                  <el-empty description="暂无技能路线" :image-size="60" />
                </div>
                <div v-else class="roadmap-list">
                  <div
                    v-for="(item, index) in report.mid_term_plan.skill_roadmap"
                    :key="item"
                    class="roadmap-item"
                  >
                    <span class="roadmap-index">{{ index + 1 }}</span>
                    <span class="roadmap-text">{{ item }}</span>
                  </div>
                </div>
              </div>

              <div class="milestone-block">
                <span class="block-title">中期里程碑</span>
                <div v-if="!report.mid_term_plan.milestones.length" class="empty-state">
                  <el-empty description="暂无中期里程碑" :image-size="80">
                    <el-button type="primary" text @click="openEditor('mid_goal')">添加中期目标</el-button>
                  </el-empty>
                </div>
                <div v-else class="milestone-stack">
                  <article
                    v-for="milestone in report.mid_term_plan.milestones"
                    :key="milestone.milestone_name"
                    class="milestone-card"
                  >
                    <div class="milestone-head">
                      <div>
                        <h3>{{ milestone.milestone_name }}</h3>
                        <span>{{ milestone.target_date }}</span>
                      </div>
                    </div>

                    <div class="milestone-body">
                      <div class="result-box">
                        <span class="mini-title">关键成果</span>
                        <ul class="plain-list">
                          <li v-for="result in milestone.key_results" :key="result">{{ result }}</li>
                        </ul>
                      </div>

                      <div v-if="milestone.tasks.length" class="task-grid">
                        <article v-for="task in milestone.tasks" :key="task.task_name" class="task-card">
                          <div class="task-top">
                            <strong>{{ task.task_name }}</strong>
                            <el-tag :type="priorityType(task.priority)" size="small" round>
                              {{ task.priority }}优先级</el-tag>
                          </div>
                          <div class="task-meta">
                            <span>预计时间：{{ task.estimated_time }}</span>
                            <span>目标能力：{{ task.skill_target }}</span>
                          </div>
                          <p class="task-desc">{{ task.description }}</p>
                          <div class="task-bottom">
                            <div>
                              <span class="mini-title">成功标准</span>
                              <p>{{ task.success_criteria }}</p>
                            </div>
                            <el-button
                              v-if="getTaskResources(task).length"
                              size="small"
                              @click="openResourceList(getTaskResources(task))"
                            >
                              查看资源（{{ getTaskResources(task).length }}）</el-button>
                            <el-tag v-else size="small" type="info" round>暂无资源</el-tag>
                          </div>
                        </article>
                      </div>
                    </div>
                  </article>
                </div>
              </div>

              <div class="goal-box">
                <div class="goal-head">
                  <span class="goal-label">职业发展预期</span>
                  <div class="inline-actions">
                    <el-button text @click="polishOneSection('career_progression')">润色</el-button>
                    <el-button text type="primary" @click="openEditor('career_progression')">编辑</el-button>
                  </div>
                </div>
                <div class="rich-preview" v-html="richContent.career_progression" />
              </div>

              <div id="report-internship" class="internship-block">
                <span class="block-title">推荐实习岗位</span>
                <div v-if="!report.mid_term_plan.recommended_internships.length" class="empty-state">
                  <el-empty description="暂无推荐实习" :image-size="80">
                    <template #description>
                      <span>暂无推荐实习岗位</span>
                    </template>
                  </el-empty>
                </div>
                <div v-else class="internship-grid">
                  <article
                    v-for="job in report.mid_term_plan.recommended_internships"
                    :key="job.id"
                    class="internship-card"
                  >
                    <div class="internship-top">
                      <div>
                        <h3>{{ job.job_title }}</h3>
                        <p>{{ job.company_name }}</p>
                      </div>
                      <el-tag round>{{ job.city || '待定' }}</el-tag>
                    </div>

                    <div class="internship-meta">
                      <span>{{ job.salary || '薪资面议' }}</span>
                      <span>{{ job.degree || '学历不限' }}</span>
                      <span>{{ job.job_type || '实习' }}</span>
                    </div>

                    <div class="chip-list">
                      <el-tag v-if="job.tech_stack" size="small" round>{{ job.tech_stack }}</el-tag>
                      <el-tag size="small" type="success" round>{{ job.days_per_week }}天/周</el-tag>
                      <el-tag size="small" type="warning" round>{{ job.months }}个月</el-tag>
                    </div>

                    <p class="internship-reason">{{ job.reason }}</p>

                    <div class="internship-actions">
                      <el-button
                        v-if="job.url"
                        size="small"
                        type="primary"
                        @click="openLink(job.url)"
                      >
                        查看岗位
                      </el-button>
                      <el-button size="small" @click="openInternshipDetail(job)">查看详情</el-button>
                    </div>
                  </article>
                </div>
              </div>
            </article>
          </section>
          <div class="section-group-header">
            <div>
              <p class="section-group-kicker">Module 03</p>
              <h2>行动计划</h2>
            </div>
            <span class="section-group-desc">用清单和建议把目标转成能立即执行的动作。</span>
          </div>
          <div class="section-summary-bar">
            <div v-for="item in moduleHighlights.action" :key="item" class="section-summary-item">
              {{ item }}
            </div>
          </div>
          <section class="report-section section-grid">
            <article class="content-card">
              <div class="card-head">
                <div>
                  <p class="card-kicker">Actions</p>
                  <h2>立即行动清单</h2>
                </div>
                <span class="light-text">{{ checkedActions.length }}/{{ report.action_checklist.length }} 已完成</span>
              </div>

              <el-progress :percentage="progressPercent" :stroke-width="10" class="progress-bar" />

              <div id="report-actions" class="checklist-area">
                <el-empty v-if="!report.action_checklist.length" description="暂无行动清单" :image-size="60" />
                <el-checkbox-group v-else v-model="checkedActions">
                  <div v-for="item in report.action_checklist" :key="item" class="check-item">
                    <el-checkbox :label="item">
                      <span class="check-item-text">{{ item }}</span>
                    </el-checkbox>
                  </div>
                </el-checkbox-group>
              </div>
            </article>

            <article class="content-card">
              <div class="card-head">
                <div>
                  <p class="card-kicker">Tips</p>
                  <h2>学习建议</h2>
                </div>
                <span class="light-text">{{ report.tips.length }} 条</span>
              </div>

              <div id="report-tips" class="tips-area">
                <el-empty v-if="!report.tips.length" description="暂无学习建议" :image-size="60" />
                <div v-for="tip in report.tips" :key="tip" class="tip-card">
                  <span class="tip-dot"></span>
                  <span class="tip-text">{{ tip }}</span>
                </div>
              </div>
            </article>
          </section>
        </div>
      </main>

      <div v-if="assistantPanelVisible" class="assistant-overlay" @click="assistantPanelVisible = false"></div>
      <aside class="assistant-panel" :class="{ 'is-open': assistantPanelVisible }">
        <section class="assistant-card">
          <div class="assistant-title-row">
            <div>
              <p class="card-kicker">Assistant</p>
              <h2>智能润色助手</h2>
              <p class="assistant-subtitle">检查报告完整性，并对关键文本做措辞优化。</p>
            </div>
            <div class="assistant-title-actions">
              <el-tag type="success" round>可接入 AI 接口</el-tag>
              <el-button text class="assistant-close" @click="assistantPanelVisible = false">收起</el-button>
            </div>
          </div>

          <div class="assistant-score">
            <span>报告完整度</span>
            <el-progress type="dashboard" :percentage="completenessScore" />
          </div>

          <div class="tool-block">
            <span class="tool-title">编辑区块</span>
            <el-select v-model="selectedSection">
              <el-option
                v-for="item in editableSections"
                :key="item.key"
                :label="item.label"
                :value="item.key"
              />
            </el-select>
            <div class="tool-actions">
              <el-button @click="openEditor(selectedSection)">打开编辑器</el-button>
              <el-button type="primary" plain @click="polishOneSection(selectedSection)">润色当前区块</el-button>
            </div>
          </div>

          <div class="tool-block">
            <span class="tool-title">当前区块上下文</span>
            <div class="context-card">
              <strong>{{ sectionLabel(selectedSection) }}</strong>
              <p>{{ htmlToText(getSectionContent(selectedSection)) || '当前区块还没有形成可导出的正文内容，建议先补充关键信息。' }}</p>
            </div>
          </div>

          <div class="tool-block">
            <span class="tool-title">内容优化</span>
            <div class="tool-actions">
              <el-button @click="runCompletenessCheck">检查完整性</el-button>
              <el-button type="primary" @click="polishAllSections">润色整份报告</el-button>
            </div>
          </div>

          <div class="tool-block">
            <span class="tool-title">完整性结果</span>
            <div class="audit-grid">
              <div class="audit-card">
                <span>缺失内容</span>
                <p>{{ completenessBreakdown.missing.length ? completenessBreakdown.missing.join('、') : '暂无缺失项' }}</p>
              </div>
              <div class="audit-card">
                <span>表达偏弱</span>
                <p>{{ completenessBreakdown.weak.length ? completenessBreakdown.weak.join('、') : '当前表达较完整' }}</p>
              </div>
              <div class="audit-card">
                <span>已完成项</span>
                <p>{{ completenessBreakdown.good.length ? completenessBreakdown.good.join('、') : '暂无已完成项' }}</p>
              </div>
            </div>
          </div>

          <div class="tool-block">
            <span class="tool-title">助手建议</span>
            <el-empty v-if="!assistantNotes.length" description="点击上方按钮开始分析" />
            <el-timeline v-else>
              <el-timeline-item
                v-for="(note, index) in assistantNotes"
                :key="`${note.message}-${index}`"
                :type="note.type"
                :timestamp="note.time"
                hollow
              >
                {{ note.message }}
              </el-timeline-item>
            </el-timeline>
          </div>
        </section>
      </aside>
    </div>

    <button class="assistant-fab" type="button" @click="assistantPanelVisible = true">
      AI 助手
    </button>

    <el-drawer v-model="resourceDrawerVisible" title="推荐资源" size="520px">
      <div v-if="currentResources.length" class="resource-list">
        <article v-for="item in currentResources" :key="item.id" class="resource-card">
          <div class="resource-card-top">
            <div>
              <h3 class="resource-title">{{ resourceTitle(item) }}</h3>
              <p class="resource-sub">{{ resourceType(item) }}</p>
            </div>
            <el-tag round>{{ item.reason ? '推荐' : '资源' }}</el-tag>
          </div>

          <p class="resource-text">{{ item.reason || item.description || item.content || '暂无说明' }}</p>

          <el-button v-if="item.url" size="small" type="primary" plain @click="openLink(item.url)">
            打开链接
          </el-button>
        </article>
      </div>
      <el-empty v-else description="暂无资源" />
    </el-drawer>

    <el-drawer v-model="internshipDrawerVisible" title="实习岗位详情" size="560px">
      <div v-if="currentInternship" class="internship-detail">
        <h3>{{ currentInternship.job_title }}</h3>
        <div class="detail-meta">
          <el-tag round>{{ currentInternship.company_name }}</el-tag>
          <el-tag round type="success">{{ currentInternship.city || '待定城市' }}</el-tag>
          <el-tag round type="warning">{{ currentInternship.salary || '薪资面议' }}</el-tag>
        </div>
        <p class="detail-block">{{ currentInternship.reason || '暂无推荐理由' }}</p>
        <p class="detail-block">{{ currentInternship.content || '暂无岗位描述' }}</p>
        <el-button v-if="currentInternship.url" type="primary" @click="openLink(currentInternship.url)">
          前往岗位链接
        </el-button>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Edit,
  Check,
  MagicStick,
  DocumentChecked,
  Document,
  DocumentCopy,
  Trophy,
  Calendar,
  Timer,
  Flag,
  Aim,
  OfficeBuilding,
} from '@element-plus/icons-vue'
import {
  exportGrowthPlanToWord,
  exportResumePreviewToPdf,
} from '@/utils/resume-export'
import { useRouter } from 'vue-router'
import {
  createEmptyCareerReport,
  type EditableSectionKey,
  type GrowthPlanData,
  type InternshipItem,
  type PlanTask,
  type ResourceItem,
} from '@/types/career-report'

type AssistantNote = {
  message: string
  type: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  time: string
}

const props = withDefaults(
  defineProps<{
    data?: GrowthPlanData
  }>(),
  {
    data: undefined,
  },
)

const emit = defineEmits<{
  (e: 'save', data: GrowthPlanData): void
  (e: 'polish-request', payload: { section: EditableSectionKey; content: string }): void
}>()

const router = useRouter()

const emptyReport = createEmptyCareerReport

/**
 * 开发环境下的示例报告数据
 */
const generateMockData = (): GrowthPlanData => ({
  student_summary: '计算机专业学生，具备基础编程能力和项目实践经历，当前目标是进入后端开发岗位。',
  target_position: 'Java 后端开发工程师',
  current_gap: '当前还需要继续补齐工程化经验、微服务理解、性能优化案例和真实业务项目成果。',
  short_term_plan: {
    duration: '1-3个月',
    goal: '完成后端基础能力补强，输出一套可展示的项目成果，并开始投递实习。',
    focus_areas: ['Java鍩虹', 'Spring Boot', 'MySQL', 'Redis'],
    milestones: [
      {
        milestone_name: '完成后端基础巩固',
        target_date: '第1个月',
        key_results: ['整理知识笔记', '完成基础项目', '补齐常见面试题'],
        tasks: [
          {
            task_name: '复习 Java 与集合并发',
            description: '系统梳理核心语法、集合框架和并发基础。',
            priority: '高',
            estimated_time: '2周',
            skill_target: '后端基础',
            success_criteria: '形成结构化笔记并完成练习',
            resources: [
              { id: 'mock-resource-1', title: 'Java 核心知识整理', description: '用于建立知识框架的学习材料', reason: '适合快速回顾' },
            ],
          } as PlanTask,
        ],
      },
    ],
    quick_wins: ['完善 GitHub 项目说明', '整理一份岗位技能对照表'],
  },
  mid_term_plan: {
    duration: '3-12个月',
    goal: '形成中型项目开发与优化能力，具备独立承接模块的经验。',
    skill_roadmap: ['Spring Cloud', 'Docker', '消息队列', '监控与日志'],
    milestones: [
      {
        milestone_name: '完成微服务项目实践',
        target_date: '第6个月',
        key_results: ['拆分服务', '接入网关', '完成部署'],
        tasks: [
          {
            task_name: '搭建微服务练手项目',
            description: '围绕用户、权限、缓存等模块完成项目拆分。',
            priority: '中',
            estimated_time: '1个月',
            skill_target: '微服务工程化',
            success_criteria: '可以稳定运行并完成接口联调',
            resources: [],
          } as PlanTask,
        ],
      },
    ],
    career_progression: '先完成入门岗位胜任力，再逐步向独立负责模块和系统设计方向发展。',
    recommended_internships: [
      {
        id: 'mock-job-1',
        job_title: '后端开发实习生',
        company_name: '示例科技',
        salary: '4k-6k',
        city: '上海',
        degree: '本科',
        days_per_week: 4,
        months: 3,
        job_type: '实习',
        tech_stack: 'Java / Spring',
        url: '',
        content: '参与基础后端接口开发和联调工作。',
        reason: '与当前能力提升路径高度匹配。',
      },
    ],
  },
  action_checklist: ['完成项目复盘', '更新简历', '开始岗位投递'],
  tips: ['每周复盘一次学习进度', '优先沉淀可展示的项目成果'],
})
function deepClone<T>(data: T): T {
  if (typeof structuredClone === 'function') {
    return structuredClone(data)
  }
  // Fallback: JSON method (has limitations with Dates, undefined, functions, etc.)
  return JSON.parse(JSON.stringify(data))
}

/**
 * Escape HTML entities to prevent XSS attacks
 * Order matters: & must be replaced first to avoid double-escaping
 */
function escapeHtml(str: string): string {
  if (!str) return ''
  return str
    .replace(/&/g, '&amp;')      // Must be first
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function normalizeText(text: string) {
  return text
    .replace(/\r\n/g, '\n')
    .replace(/[ \t]+/g, ' ')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

function textToHtml(text: string) {
  const source = normalizeText(text)
  if (!source) return '<p>暂无内容</p>'

  return source
    .split('\n')
    .filter(Boolean)
    .map(line => `<p>${escapeHtml(line)}</p>`)
    .join('')
}

/**
 * Convert HTML to plain text safely without executing scripts
 * Uses regex-based stripping instead of innerHTML for XSS safety
 */
function htmlToText(html: string): string {
  if (!html) return ''
  // Remove script/style tags and their contents first (XSS prevention)
  let text = html
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]+>/g, ' ')     // Replace remaining tags with space
    .replace(/\s+/g, ' ')          // Collapse whitespace
    .trim()
  return normalizeText(text)
}

function smartPolishHtml(html: string) {
  const text = htmlToText(html)
  if (!text) return '<p>暂无内容</p>'

  const polished = normalizeText(
    text
      .replace(/;/g, '；')
      .replace(/:/g, '：')
      .replace(/\bSpringboot\b/gi, 'Spring Boot')
      .replace(/\bmysql\b/gi, 'MySQL'),
  )

  return textToHtml(polished)
}

const report = ref<GrowthPlanData>(emptyReport())

const richContent = reactive<Record<EditableSectionKey, string>>({
  student_summary: '<p>暂无内容</p>',
  current_gap: '<p>暂无内容</p>',
  short_goal: '<p>暂无内容</p>',
  mid_goal: '<p>暂无内容</p>',
  career_progression: '<p>暂无内容</p>',
})

// 避免在初始化阶段触发未定义引用
const checkedActions = ref<string[]>([])
const checklistStorageKey = computed(
  () => `career-report-checklist:${report.value.target_position || 'default'}`,
)

function syncReport(data?: GrowthPlanData) {
  // 开发环境或显式开启 mock 时使用示例数据
  const useMock = !data && (import.meta.env.DEV || import.meta.env.VITE_USE_MOCK === 'true')
  const value = deepClone(data || (useMock ? generateMockData() : emptyReport()))
  report.value = value
  richContent.student_summary = textToHtml(value.student_summary)
  richContent.current_gap = textToHtml(value.current_gap)
  richContent.short_goal = textToHtml(value.short_term_plan.goal)
  richContent.mid_goal = textToHtml(value.mid_term_plan.goal)
  richContent.career_progression = textToHtml(value.mid_term_plan.career_progression)
  restoreChecklist()
}

watch(
  () => props.data,
  val => {
    syncReport(val)
  },
  { immediate: true, deep: true },
)

const editableSections = [
  { key: 'student_summary' as EditableSectionKey, label: '学生画像摘要' },
  { key: 'current_gap' as EditableSectionKey, label: '能力差距分析' },
  { key: 'short_goal' as EditableSectionKey, label: '短期目标' },
  { key: 'mid_goal' as EditableSectionKey, label: '中期目标' },
  { key: 'career_progression' as EditableSectionKey, label: '职业发展预期' },
]

const selectedSection = ref<EditableSectionKey>('student_summary')
const assistantPanelVisible = ref(false)

const reportSectionAnchors = [
  { key: 'profile', label: '职业画像', id: 'report-profile' },
  { key: 'gap', label: '差距分析', id: 'report-gap' },
  { key: 'short', label: '短期计划', id: 'report-short' },
  { key: 'mid', label: '中期计划', id: 'report-mid' },
  { key: 'resources', label: '推荐资源', id: 'report-resources' },
  { key: 'internship', label: '推荐实习', id: 'report-internship' },
  { key: 'actions', label: '行动清单', id: 'report-actions' },
  { key: 'tips', label: '学习建议', id: 'report-tips' },
] as const

function sectionLabel(key: EditableSectionKey) {
  return editableSections.find(item => item.key === key)?.label || key
}

function getSectionContent(key: EditableSectionKey) {
  return richContent[key]
}

function setSectionContent(key: EditableSectionKey, value: string) {
  richContent[key] = value
}

function openEditor(key: EditableSectionKey) {
  selectedSection.value = key
  router.push({
    name: 'report-editor',
    query: { section: key },
  })
}

function polishOneSection(key: EditableSectionKey) {
  const polished = smartPolishHtml(getSectionContent(key))
  setSectionContent(key, polished)
  pushAssistantNote(`已润色 ${sectionLabel(key)}`, 'success')
  emit('polish-request', {
    section: key,
    content: htmlToText(polished),
  })
}

function polishAllSections() {
  editableSections.forEach(item => {
    setSectionContent(item.key, smartPolishHtml(getSectionContent(item.key)))
  })
  pushAssistantNote('已对整份报告的核心文本进行统一润色', 'success')
  ElMessage.success('全文润色完成')
}

function buildSubmitData(): GrowthPlanData {
  const result = deepClone(report.value)
  result.student_summary = htmlToText(richContent.student_summary)
  result.current_gap = htmlToText(richContent.current_gap)
  result.short_term_plan.goal = htmlToText(richContent.short_goal)
  result.mid_term_plan.goal = htmlToText(richContent.mid_goal)
  result.mid_term_plan.career_progression = htmlToText(richContent.career_progression)
  return result
}

function handleSave(showMessage = true) {
  const payload = buildSubmitData()
  emit('save', payload)
  if (showMessage) {
    ElMessage.success('已保存当前报告')
  }
}

/**
 * Safely restore checklist from localStorage with SSR compatibility
 */
function restoreChecklist(): void {
  // Check for SSR environment
  if (typeof window === 'undefined' || !window.localStorage) {
    checkedActions.value = []
    return
  }
  try {
    const raw = localStorage.getItem(checklistStorageKey.value)
    if (raw) {
      const parsed = JSON.parse(raw)
      // Validate that parsed data is an array of strings
      if (Array.isArray(parsed) && parsed.every(item => typeof item === 'string')) {
        checkedActions.value = parsed
      } else {
        checkedActions.value = []
      }
    } else {
      checkedActions.value = []
    }
  } catch {
    checkedActions.value = []
  }
}

/**
 * Safely persist checklist to localStorage with quota handling
 */
function persistChecklist(val: string[]): void {
  if (typeof window === 'undefined' || !window.localStorage) return
  try {
    localStorage.setItem(checklistStorageKey.value, JSON.stringify(val))
  } catch (e) {
    // Handle quota exceeded error
    if (e instanceof DOMException && e.name === 'QuotaExceededError') {
      console.warn('localStorage quota exceeded')
      ElMessage.warning('存储空间不足，无法保存勾选状态')
    }
  }
}

watch(
  checkedActions,
  val => {
    persistChecklist(val)
  },
  { deep: true },
)

const progressPercent = computed(() => {
  const total = report.value.action_checklist.length
  if (!total) return 0
  return Math.round((checkedActions.value.length / total) * 100)
})

const reportWorkbenchSummary = computed(() => {
  const advantage = htmlToText(richContent.student_summary) || '建议先补充学生画像摘要，明确你的当前优势。'
  const gap = htmlToText(richContent.current_gap) || '建议先补充关键差距，帮助快速锁定最优提升方向。'
  const shortAction =
    report.value.short_term_plan.quick_wins[0] ||
    report.value.action_checklist[0] ||
    htmlToText(richContent.short_goal) ||
    '建议先明确一条本周可以执行的短期行动。'
  const midDirection =
    report.value.mid_term_plan.skill_roadmap[0] ||
    htmlToText(richContent.mid_goal) ||
    htmlToText(richContent.career_progression) ||
    '建议补充中期发展方向与阶段成长路径。'

  return {
    targetPosition: report.value.target_position || '待明确目标岗位',
    advantage: advantage.slice(0, 72),
    gap: gap.slice(0, 72),
    shortAction: shortAction.slice(0, 56),
    midDirection: midDirection.slice(0, 56),
  }
})

const moduleHighlights = computed(() => ({
  profile: [
    `目标岗位：${reportWorkbenchSummary.value.targetPosition}`,
    `优势摘要：${reportWorkbenchSummary.value.advantage}`,
    `关键差距：${reportWorkbenchSummary.value.gap}`,
  ],
  short: [
    `短期优先事项：${reportWorkbenchSummary.value.shortAction}`,
    `重点领域 ${report.value.short_term_plan.focus_areas.length} 项`,
    `短期里程碑 ${report.value.short_term_plan.milestones.length} 个`,
  ],
  mid: [
    `中期发展方向：${reportWorkbenchSummary.value.midDirection}`,
    `技能路线 ${report.value.mid_term_plan.skill_roadmap.length} 条`,
    `推荐实习 ${report.value.mid_term_plan.recommended_internships.length} 个`,
  ],
  action: [
    `行动完成度 ${progressPercent.value}%`,
    `待执行行动 ${Math.max(report.value.action_checklist.length - checkedActions.value.length, 0)} 项`,
    `学习建议 ${report.value.tips.length} 条`,
  ],
}))

const aggregatedResources = computed(() => {
  const buckets = [
    {
      planLabel: '短期计划',
      milestones: report.value.short_term_plan.milestones,
    },
    {
      planLabel: '中期计划',
      milestones: report.value.mid_term_plan.milestones,
    },
  ]

  const items: Array<{
    id: string
    raw: ResourceItem
    title: string
    reason: string
    description: string
    content: string
    planLabel: string
    taskName: string
    originLabel: string
  }> = []

  buckets.forEach(bucket => {
    bucket.milestones.forEach(milestone => {
      milestone.tasks.forEach(task => {
        getTaskResources(task).forEach((resource, index) => {
          items.push({
            id: resource.id || `${bucket.planLabel}-${milestone.milestone_name}-${task.task_name}-${index}`,
            raw: resource,
            title: resourceTitle(resource),
            reason: resource.reason || '',
            description: resource.description || '',
            content: resource.content || '',
            planLabel: bucket.planLabel,
            taskName: task.task_name || '',
            originLabel: milestone.milestone_name || bucket.planLabel,
          })
        })
      })
    })
  })

  const deduped = new Map<string, (typeof items)[number]>()
  items.forEach(item => {
    const key = [item.title, item.raw.url || '', item.originLabel].join('::')
    if (!deduped.has(key)) {
      deduped.set(key, item)
    }
  })

  return Array.from(deduped.values()).slice(0, 8)
})

const completenessBreakdown = computed(() => {
  const missing: string[] = []
  const weak: string[] = []
  const good: string[] = []

  if (!htmlToText(richContent.student_summary)) missing.push('职业画像摘要')
  else good.push('职业画像摘要')

  if (!htmlToText(richContent.current_gap)) missing.push('差距分析')
  else good.push('差距分析')

  if (!htmlToText(richContent.short_goal)) weak.push('短期目标表达偏弱')
  else good.push('短期目标')

  if (!htmlToText(richContent.mid_goal)) weak.push('中期目标表达偏弱')
  else good.push('中期目标')

  if (!report.value.action_checklist.length) missing.push('行动清单')
  else good.push('行动清单')

  if (!report.value.tips.length) weak.push('学习建议可继续增强')
  else good.push('学习建议')

  return { missing, weak, good }
})

function priorityType(priority: string) {
  if (priority === '高') return 'danger'
  if (priority === '中') return 'warning'
  return 'info'
}

/**
 * Safely get task resources with proper type inference
 * Works around Vue template type inference limitations
 * Uses type assertion since Vue template cannot infer nested array types correctly
 */
function getTaskResources(task: unknown): ResourceItem[] {
  const t = task as PlanTask
  return t.resources || []
}

const resourceDrawerVisible = ref(false)
const currentResources = ref<ResourceItem[]>([])

function openResourceList(list: ResourceItem[]) {
  currentResources.value = list || []
  resourceDrawerVisible.value = true
}

function resourceTitle(item: ResourceItem) {
  return item.title || item.name || '未命名资源'
}

function resourceType(item: ResourceItem) {
  if (item.duration) return '视频资源'
  if (item.isbn) return '书籍资源'
  if (typeof item.stars === 'number') return '开源项目'
  return '学习资源'
}

function scrollToReportSection(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const internshipDrawerVisible = ref(false)
const currentInternship = ref<InternshipItem | null>(null)

function openInternshipDetail(item: InternshipItem) {
  currentInternship.value = item
  internshipDrawerVisible.value = true
}

/**
 * Open URL in new tab with security validation
 * Prevents javascript: protocol XSS attacks
 */
function openLink(url?: string): void {
  if (!url) return
  // Validate URL protocol to prevent XSS via javascript: URLs
  try {
    const parsed = new URL(url, window.location.href)
    // Only allow safe protocols
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      console.warn('Blocked potentially unsafe URL protocol:', parsed.protocol)
      ElMessage.warning('不安全的链接格式')
      return
    }
    window.open(url, '_blank', 'noopener,noreferrer')
  } catch {
    // Invalid URL format
    ElMessage.error('链接格式无效')
  }
}

const assistantNotes = ref<AssistantNote[]>([])

function pushAssistantNote(message: string, type: AssistantNote['type'] = 'primary') {
  assistantNotes.value.unshift({
    message,
    type,
    time: new Date().toLocaleTimeString(),
  })
}

/**
 * Check if HTML content has meaningful text (cached per computation)
 */
function hasMeaningfulContent(html: string): boolean {
  // Quick check: if no text content between tags, skip full parsing
  const textContent = html.replace(/<[^>]*>/g, '').trim()
  if (!textContent) return false
  // Full check with normalization
  return !!htmlToText(html)
}

/**
 * Report completeness score (0-100)
 * Optimized to avoid redundant DOM operations
 */
const completenessScore = computed(() => {
  // Batch text extraction to minimize processing
  const checks = [
    hasMeaningfulContent(richContent.student_summary),
    hasMeaningfulContent(richContent.current_gap),
    hasMeaningfulContent(richContent.short_goal),
    hasMeaningfulContent(richContent.mid_goal),
    hasMeaningfulContent(richContent.career_progression),
    report.value.short_term_plan.focus_areas.length > 0,
    report.value.short_term_plan.milestones.length > 0,
    report.value.mid_term_plan.skill_roadmap.length > 0,
    report.value.mid_term_plan.milestones.length > 0,
    report.value.action_checklist.length > 0,
    report.value.tips.length > 0,
  ]
  const hit = checks.filter(Boolean).length
  return Math.round((hit / checks.length) * 100)
})

function runCompletenessCheck() {
  const warnings: string[] = []

  if (!htmlToText(richContent.student_summary)) warnings.push('缺少学生画像摘要')
  if (!htmlToText(richContent.current_gap)) warnings.push('缺少能力差距分析')
  if (!htmlToText(richContent.short_goal)) warnings.push('缺少短期目标描述')
  if (!htmlToText(richContent.mid_goal)) warnings.push('缺少中期目标描述')
  if (report.value.short_term_plan.focus_areas.length === 0) warnings.push('短期重点领域为空')
  if (report.value.short_term_plan.milestones.length === 0) warnings.push('短期里程碑为空')
  if (report.value.mid_term_plan.skill_roadmap.length === 0) warnings.push('中期技能路线图为空')
  if (report.value.mid_term_plan.milestones.length === 0) warnings.push('中期里程碑为空')
  if (report.value.action_checklist.length === 0) warnings.push('行动清单为空')
  if (report.value.tips.length === 0) warnings.push('学习建议为空')

  if (!warnings.length) {
    pushAssistantNote('完整性检查通过，当前报告核心结构完整', 'success')
    ElMessage.success('完整性检查通过')
    return
  }

  warnings.forEach(item => pushAssistantNote(item, 'warning'))
  ElMessage.warning(`发现 ${warnings.length} 处建议补充的内容`)
}

const reportRef = ref<HTMLElement | null>(null)

async function exportPdf() {
  if (!reportRef.value) return

  try {
    await exportResumePreviewToPdf(reportRef.value, {
      fileName: `${report.value.target_position || 'career-report'}.pdf`,
      margin: 8,
    })
    pushAssistantNote('PDF 导出成功', 'success')
  } catch (error) {
    console.error(error)
    ElMessage.error('PDF 导出失败')
    pushAssistantNote('PDF 导出失败，请检查页面内容是否已渲染完成', 'danger')
  }
}

async function exportWord() {
  try {
    await exportGrowthPlanToWord(buildSubmitData(), {
      fileName: `${report.value.target_position || 'career-report'}.docx`,
    })
    pushAssistantNote('Word 导出成功', 'success')
  } catch (error) {
    console.error(error)
    ElMessage.error('Word 导出失败')
  }
}
</script>

<style scoped>
/* ===== CSS Variables for Design System - Unified with CReportEditor ===== */
.career-report-page {
  --primary-gradient: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #2563eb 100%);
  --card-shadow: 0 16px 36px rgba(15, 23, 42, 0.06);
  --card-shadow-hover: 0 24px 48px rgba(15, 23, 42, 0.12);
  --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --border-glow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  --radius-xl: 24px;
  --radius-lg: 20px;
  --radius-md: 16px;
  --radius-sm: 12px;

  min-height: 100vh;
  padding: 24px;
  background:
    radial-gradient(circle at top left, rgba(250, 204, 21, 0.15), transparent 24%),
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.12), transparent 26%),
    linear-gradient(180deg, #fffdf8 0%, #f8fbff 100%);
}

/* ===== Top Navigation Bar - Unified with CReportEditor ===== */
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  margin-bottom: 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: var(--radius-lg);
  box-shadow: var(--card-shadow);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-logo {
  font-size: 24px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.nav-title {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.nav-actions :deep(.el-button) {
  border-radius: 10px;
  font-weight: 500;
  transition: var(--transition-smooth);
}

.nav-actions :deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

/* ===== Hero Panel ===== */
.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 32px;
  border-radius: var(--radius-xl);
  background: var(--primary-gradient);
  color: #fff;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.12);
  position: relative;
  overflow: hidden;
}

.hero-panel::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  pointer-events: none;
}

.hero-copy {
  max-width: 760px;
}

.hero-summary-mini {
  display: grid;
  gap: 10px;
  margin-top: 10px;
  color: rgba(255, 255, 255, 0.86);
  font-size: 13px;
}

.eyebrow,
.card-kicker {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.hero-copy h1,
.card-head h2,
.assistant-title-row h2,
.editor-dialog-head h3,
.milestone-head h3,
.internship-top h3 {
  margin: 0;
}

.hero-desc {
  margin: 12px 0 0;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.82);
}

.hero-actions,
.inline-actions,
.tool-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-actions :deep(.el-button) {
  border-radius: 10px;
  font-weight: 500;
  transition: var(--transition-smooth);
}

.hero-actions :deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.hero-actions :deep(.el-button--primary) {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
}

.hero-actions :deep(.el-button--success) {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
}

.hero-actions :deep(.el-button--warning) {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border: none;
}

/* ===== Stats Grid - Unified Style ===== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
  margin: 24px 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: var(--radius-xl);
  box-shadow: var(--card-shadow);
  transition: var(--transition-smooth);
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-shadow-hover);
}

.stat-card--primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #fff;
}

.stat-card--success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
}

.stat-card--warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #fff;
}

.stat-card--info {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  color: #fff;
}

.stat-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-md);
  font-size: 24px;
}

.stat-card--info .stat-icon {
  background: transparent;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 13px;
  font-weight: 500;
  opacity: 0.9;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
}

.summary-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-top: 18px;
}

.summary-strip--workbench {
  grid-template-columns: repeat(5, minmax(0, 1fr));
  margin-bottom: 24px;
}

@keyframes countUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.summary-card,
.content-card,
.assistant-card,
.milestone-card,
.task-card,
.internship-card,
.resource-card {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: var(--radius-xl);
  box-shadow: var(--card-shadow);
  transition: var(--transition-smooth);
}

.summary-card {
  padding: 20px 24px;
  transition: var(--transition-smooth);
  cursor: pointer;
}

.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-shadow-hover);
}

.summary-card span,
.card-subtitle,
.light-text,
.assistant-subtitle,
.resource-sub,
.internship-top p {
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
}

.summary-card strong {
  display: block;
  margin-top: 10px;
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
  background: linear-gradient(135deg, #0f172a 0%, #2563eb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.summary-card p {
  margin: 10px 0 0;
  color: #475569;
  line-height: 1.7;
  font-size: 14px;
}

.report-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.9fr) minmax(320px, 0.95fr);
  gap: 28px;
  margin-top: 20px;
  align-items: start;
  position: relative;
}

.report-outline {
  margin-bottom: 18px;
  padding: 18px 20px;
  border-radius: var(--radius-xl);
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: var(--card-shadow);
}

.outline-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 14px;
}

.outline-head h2 {
  margin: 0;
  color: #0f172a;
  font-size: 20px;
}

.outline-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.outline-chip {
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: #fff;
  color: #334155;
  border-radius: 999px;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-smooth);
}

.outline-chip:hover {
  border-color: rgba(59, 130, 246, 0.3);
  color: #1d4ed8;
  transform: translateY(-1px);
}

.report-canvas {
  display: grid;
  gap: 22px;
}

.report-export-surface {
  padding: 22px;
  border-radius: 26px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(148, 163, 184, 0.14);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.06);
}

.section-group-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: end;
  padding: 0 4px 4px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}

.section-group-kicker {
  margin: 0 0 6px;
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #2563eb;
  font-weight: 700;
}

.section-group-header h2 {
  margin: 0;
  font-size: 26px;
  color: #0f172a;
}

.section-group-desc {
  max-width: 320px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.7;
}

.section-summary-bar {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: -6px;
  margin-bottom: 18px;
}

.section-summary-item {
  padding: 14px 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f8fbff 0%, #ffffff 100%);
  border: 1px solid rgba(148, 163, 184, 0.12);
  color: #475569;
  font-size: 13px;
  line-height: 1.7;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
}

.section-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 0.8fr);
  gap: 16px;
}

.content-card {
  padding: 24px;
  position: relative;
  overflow: hidden;
}

.content-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease;
}

.content-card:hover::before {
  transform: scaleX(1);
}

.content-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--card-shadow-hover);
}

.content-card--wide {
  min-height: 100%;
}

.card-head,
.assistant-title-row,
.milestone-head,
.task-top,
.internship-top,
.goal-head,
.editor-dialog-head,
.resource-card-top {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.card-head {
  margin-bottom: 20px;
}

.card-head h2 {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.card-kicker {
  color: #3b82f6;
  font-weight: 600;
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.rich-preview {
  line-height: 1.85;
  color: #1e293b;
}

.rich-preview :deep(p) {
  margin: 0 0 10px;
}

.goal-box,
.chip-block,
.milestone-block,
.timeline-block,
.roadmap-block,
.internship-block {
  margin-top: 20px;
}

.goal-box {
  padding: 18px;
  border-radius: 18px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
  border: 1px solid rgba(59, 130, 246, 0.1);
}

.goal-label,
.block-title,
.tool-title,
.mini-title {
  display: block;
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip-list :deep(.el-tag) {
  border-radius: 8px;
  font-weight: 500;
  padding: 4px 12px;
  transition: var(--transition-smooth);
}

.chip-list :deep(.el-tag:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
}

.milestone-stack,
.task-grid,
.internship-grid,
.tips-area,
.resource-list {
  display: grid;
  gap: 16px;
}

.milestone-card {
  padding: 22px;
  transition: var(--transition-smooth);
}

.milestone-card:hover {
  box-shadow: var(--card-shadow-hover);
}

.milestone-head span {
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
}

.milestone-head h3 {
  font-size: 17px;
  font-weight: 600;
  color: #1e293b;
}

.milestone-body {
  display: grid;
  gap: 16px;
  margin-top: 16px;
}

.result-box {
  padding: 14px 16px;
  border-radius: 16px;
  background: #f8fafc;
}

.plain-list {
  margin: 0;
  padding-left: 18px;
  color: #475569;
  line-height: 1.8;
}

.task-grid {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.task-card {
  padding: 20px;
  transition: var(--transition-smooth);
  border-left: 4px solid transparent;
}

.task-card:hover {
  border-left-color: #3b82f6;
  transform: translateX(4px);
  box-shadow: var(--card-shadow-hover);
}

.task-meta {
  display: grid;
  gap: 6px;
  margin-top: 10px;
  font-size: 13px;
  color: #64748b;
}

.task-desc,
.task-bottom p,
.internship-reason,
.resource-text,
.detail-block {
  margin: 10px 0 0;
  color: #475569;
  line-height: 1.75;
}

.task-bottom {
  display: grid;
  gap: 12px;
  margin-top: 14px;
}

.roadmap-list {
  display: grid;
  gap: 12px;
}

.roadmap-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border: 1px solid rgba(148, 163, 184, 0.1);
  transition: var(--transition-smooth);
}

.roadmap-item:hover {
  background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
  border-color: rgba(59, 130, 246, 0.2);
  transform: translateX(8px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.roadmap-index,
.tip-dot {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.roadmap-item:hover .roadmap-index {
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  transform: scale(1.1);
}

.roadmap-text {
  font-size: 14px;
  color: #475569;
  font-weight: 500;
}

.internship-grid {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.internship-card {
  padding: 22px;
  transition: var(--transition-smooth);
  position: relative;
}

.internship-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 0;
  background: linear-gradient(90deg, #10b981, #3b82f6);
  transition: height 0.3s ease;
}

.internship-card:hover::after {
  height: 3px;
}

.internship-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-shadow-hover);
}

.internship-meta,
.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
  color: #64748b;
  font-size: 13px;
}

.internship-actions {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}

.progress-bar {
  margin-bottom: 16px;
}

.checklist-area {
  display: grid;
  gap: 10px;
}

.check-item {
  padding: 14px 18px;
  border-radius: 14px;
  background: #f8fafc;
  transition: var(--transition-smooth);
  border: 2px solid transparent;
}

.check-item:hover {
  background: #ffffff;
  border-color: rgba(59, 130, 246, 0.2);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.08);
}

.check-item :deep(.el-checkbox) {
  align-items: flex-start;
}

.check-item :deep(.el-checkbox__label) {
  white-space: normal;
  line-height: 1.6;
}

.tip-card {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 16px 20px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border: 1px solid rgba(148, 163, 184, 0.1);
  transition: var(--transition-smooth);
}

.tip-card:hover {
  background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
  border-color: rgba(59, 130, 246, 0.2);
  transform: translateX(6px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);
}

.tip-dot {
  width: 10px;
  height: 10px;
  margin-top: 6px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 50%;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
}

.tip-text {
  color: #475569;
  line-height: 1.7;
  font-size: 14px;
}

.timeline-item-text {
  color: #475569;
  font-size: 14px;
  line-height: 1.6;
}

.assistant-card {
  padding: 24px;
  position: sticky;
  top: 96px;
  transition: var(--transition-smooth);
  background: #f8f9fa;
  border-left: 1px solid rgba(148, 163, 184, 0.18);
}

.assistant-card:hover {
  box-shadow: var(--card-shadow-hover);
}

.assistant-title-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-end;
}

.assistant-close {
  display: none;
}

.assistant-quick-export {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin: 18px 0 6px;
}

.assistant-overlay {
  display: none;
}

.assistant-fab {
  display: none;
}

.assistant-score {
  display: grid;
  justify-items: center;
  gap: 12px;
  margin: 24px 0;
  padding: 20px;
  border-radius: 20px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid rgba(59, 130, 246, 0.1);
}

.tool-block {
  padding: 18px;
  margin-top: 16px;
  border-radius: 18px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border: 1px solid rgba(148, 163, 184, 0.1);
  transition: var(--transition-smooth);
}

.tool-block:hover {
  background: linear-gradient(135deg, #f1f5f9 0%, #ffffff 100%);
  border-color: rgba(59, 130, 246, 0.15);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
}

.tool-title {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
  margin-bottom: 12px;
}

.tool-actions {
  margin-top: 12px;
}

.context-card,
.audit-card {
  padding: 14px 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.context-card strong {
  display: block;
  margin-bottom: 8px;
  color: #0f172a;
}

.context-card p,
.audit-card p {
  margin: 0;
  color: #475569;
  line-height: 1.7;
  font-size: 14px;
}

.audit-grid {
  display: grid;
  gap: 12px;
}

.audit-card span {
  display: block;
  margin-bottom: 8px;
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.editor-dialog {
  display: grid;
  gap: 20px;
  animation: fadeInUp 0.4s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.editor-dialog-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

.resource-card {
  padding: 20px;
  transition: var(--transition-smooth);
}

.resource-overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-top: 18px;
}

.resource-overview-card {
  display: grid;
  gap: 14px;
}

.resource-overview-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: #64748b;
  font-size: 13px;
}

.resource-section-note {
  margin-top: 0;
}

.resource-overview-empty {
  margin-top: 18px;
}

.resource-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--card-shadow-hover);
}

.resource-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.resource-text {
  margin-top: 12px;
  color: #64748b;
  line-height: 1.7;
  font-size: 14px;
}

.internship-detail {
  display: grid;
  gap: 16px;
}

/* ===== Empty States ===== */
.empty-state {
  padding: 40px 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border-radius: 18px;
  border: 2px dashed rgba(148, 163, 184, 0.3);
}

.empty-state:hover {
  border-color: rgba(59, 130, 246, 0.4);
  background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%);
}

@media (max-width: 1280px) {
  .report-layout {
    grid-template-columns: 1fr;
  }

  .assistant-card {
    position: static;
  }

  .section-group-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .summary-strip--workbench {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .section-summary-bar {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .hero-panel,
  .section-grid {
    grid-template-columns: 1fr;
    display: grid;
  }

  .summary-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .outline-head {
    flex-direction: column;
  }

  .hero-panel {
    flex-direction: column;
  }

  .hero-copy h1 {
    font-size: 24px;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
  }

  .stat-value {
    font-size: 24px;
  }
}

@media (max-width: 640px) {
  .career-report-page {
    padding: 12px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .summary-strip,
  .section-grid {
    grid-template-columns: 1fr;
  }

  .summary-strip--workbench {
    grid-template-columns: 1fr;
  }

  .hero-panel {
    padding: 20px;
    border-radius: 20px;
  }

  .hero-copy h1 {
    font-size: 20px;
  }

  .hero-actions {
    width: 100%;
  }

  .hero-actions :deep(.el-button) {
    flex: 1;
    min-width: 120px;
  }

  .content-card,
  .summary-card,
  .milestone-card,
  .task-card,
  .internship-card {
    border-radius: 18px;
  }

  .roadmap-item:hover {
    transform: translateX(4px);
  }

  .top-nav {
    flex-direction: column;
    gap: 16px;
    padding: 16px 20px;
  }

  .nav-actions {
    width: 100%;
  }

  .nav-actions :deep(.el-button) {
    flex: 1;
  }

  .assistant-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.32);
    z-index: 18;
  }

  .assistant-panel {
    position: fixed;
    left: 12px;
    right: 12px;
    bottom: 12px;
    z-index: 19;
    transform: translateY(calc(100% + 16px));
    transition: transform 0.28s ease;
    pointer-events: none;
  }

  .assistant-panel.is-open {
    transform: translateY(0);
    pointer-events: auto;
  }

  .assistant-card {
    max-height: 72vh;
    overflow: auto;
    border-left: none;
  }

  .assistant-title-actions {
    align-items: flex-end;
  }

  .assistant-close {
    display: inline-flex;
  }

  .assistant-quick-export {
    grid-template-columns: 1fr;
  }

  .assistant-fab {
    position: fixed;
    right: 16px;
    bottom: 18px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 12px 16px;
    border: 0;
    border-radius: 999px;
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
    color: #fff;
    font-weight: 700;
    box-shadow: 0 16px 32px rgba(37, 99, 235, 0.28);
    z-index: 17;
  }
}

@media print {
  .top-nav,
  .hero-panel,
  .stats-grid,
  .report-outline,
  .assistant-panel,
  .assistant-fab,
  .assistant-overlay,
  :deep(.el-drawer__wrapper) {
    display: none !important;
  }

  .career-report-page,
  .report-layout,
  .report-main,
  .report-export-surface {
    background: #fff !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  .report-layout {
    display: block;
  }

  .content-card,
  .milestone-card,
  .task-card,
  .internship-card,
  .resource-card {
    break-inside: avoid;
    box-shadow: none !important;
  }
}

/* ===== Scrollbar Styling ===== */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(148, 163, 184, 0.1);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(100, 116, 139, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(100, 116, 139, 0.5);
}

/* ===== Focus States for Accessibility ===== */
button:focus-visible,
.el-button:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* ===== Selection Color ===== */
::selection {
  background: rgba(59, 130, 246, 0.2);
  color: #1e3a8a;
}
</style>
