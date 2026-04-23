<template>
  <div class="career-report-page">
    <!-- 顶部导航栏 -->
    <nav class="top-nav">
      <div class="nav-brand">
        <span class="nav-logo">📊</span>
        <span class="nav-title">Career Planning</span>
      </div>
      <div class="nav-actions">
        <el-button
          v-if="hasActiveJobContext"
          plain
          @click="switchReportView(activeView === 'report' ? 'jobs' : 'report')"
        >
          {{ activeView === 'report' ? '切换岗位界面' : '返回报告界面' }}
        </el-button>
        <el-button type="primary" :icon="Edit" :disabled="!hasActiveJobContext" @click="openEditor(selectedSection)">编辑报告</el-button>
        <el-button :icon="Check" :disabled="!hasActiveJobContext" :loading="checkingWithAi" @click="runCompletenessCheck">完整性检查</el-button>
        <el-button :icon="MagicStick" :disabled="!hasActiveJobContext" :loading="polishingAll" @click="polishAllSections">AI 润色</el-button>
        <el-button :icon="DocumentChecked" :disabled="!hasActiveJobContext" :loading="savingReport" @click="handleSave">保存</el-button>
        <el-button type="success" :icon="Document" :disabled="!hasActiveJobContext" @click="exportPdf">导出 PDF</el-button>
        <el-button type="warning" :icon="DocumentCopy" :disabled="!hasActiveJobContext" @click="exportWord">导出 Word</el-button>
      </div>
    </nav>

    <section
      v-if="showJobSwitcherPanel"
      class="job-picker-panel"
      :class="{ 'job-picker-panel--compact': hasActiveJobContext }"
    >
      <div class="job-picker-head">
        <div>
          <p class="section-group-kicker">Select Target</p>
          <h2>{{ hasActiveJobContext ? '切换查看其他推荐岗位报告' : '先选择要查看的岗位报告' }}</h2>
          <p class="job-picker-desc">
            {{
              hasActiveJobContext
                ? '当前正在查看其中一个岗位报告。你可以直接切换到其他推荐岗位，或为尚未生成的岗位立即生成对应生涯报告。'
                : '侧边栏直接进入报告页时，系统需要先确定目标岗位，才能读取或生成对应的生涯报告。'
            }}
          </p>
        </div>
        <div class="job-picker-actions">
          <el-button v-if="hasActiveJobContext" @click="switchReportView('report')">返回报告界面</el-button>
          <el-button @click="loadJobOptions">刷新岗位列表</el-button>
          <el-button type="primary" @click="goToJobMatching">去人岗匹配页</el-button>
        </div>
      </div>

      <div v-if="availableJobs.length" class="job-picker-list">
        <article
          v-if="currentJobOption"
          :key="currentJobOption.jobId"
          class="job-picker-row is-active"
        >
          <div class="job-picker-index">
            <span>当前</span>
          </div>
          <div class="job-picker-main">
            <div class="job-picker-card-head">
              <div>
                <h3>{{ currentJobOption.jobName }}</h3>
                <p>{{ currentJobOption.jobIdLabel }}</p>
              </div>
              <div class="job-picker-tags">
                <el-tag v-if="currentJobOption.scoreLabel" round type="primary">{{ currentJobOption.scoreLabel }}</el-tag>
                <el-tag v-if="currentJobOption.hasSavedReport" round type="success">已有本地报告</el-tag>
              </div>
            </div>
            <p class="job-picker-summary">{{ currentJobOption.summary }}</p>
            <div class="job-picker-meta">
              <span>{{ currentJobOption.sourceLabel }}</span>
            </div>
            <div class="job-picker-preview">
              <div class="job-picker-preview-item">
                <span>目标</span>
                <p>{{ currentJobOption.previewTarget }}</p>
              </div>
              <div class="job-picker-preview-item">
                <span>差距</span>
                <p>{{ currentJobOption.previewGap }}</p>
              </div>
              <div class="job-picker-preview-item">
                <span>短期重点</span>
                <p>{{ currentJobOption.previewAction }}</p>
              </div>
            </div>
          </div>
          <div class="job-picker-actions-col">
            <div class="job-picker-card-actions">
              <el-button type="primary" plain disabled>当前报告</el-button>
              <el-button
                type="primary"
                :loading="bootstrappingPlan && pendingJobId === currentJobOption.jobId"
                @click="generateReportForJobWithPoints(currentJobOption.jobId)"
              >
                {{ currentJobOption.hasSavedReport ? '重新生成' : '生成并切换' }}
              </el-button>
            </div>
          </div>
        </article>

        <el-collapse v-if="otherJobOptions.length" v-model="jobCollapsePanels" class="job-picker-collapse">
          <el-collapse-item :name="'other-jobs'" :title="`更多推荐岗位（${otherJobOptions.length}）`">
            <div class="job-picker-list job-picker-list--nested">
              <article
                v-for="(item, index) in otherJobOptions"
                :key="item.jobId"
                class="job-picker-row"
              >
                <div class="job-picker-index">
                  <span>{{ index + 1 }}</span>
                </div>
                <div class="job-picker-main">
                  <div class="job-picker-card-head">
                    <div>
                      <h3>{{ item.jobName }}</h3>
                      <p>{{ item.jobIdLabel }}</p>
                    </div>
                    <div class="job-picker-tags">
                      <el-tag v-if="item.scoreLabel" round type="primary">{{ item.scoreLabel }}</el-tag>
                      <el-tag v-if="item.hasSavedReport" round type="success">已有本地报告</el-tag>
                    </div>
                  </div>
                  <p class="job-picker-summary">{{ item.summary }}</p>
                  <div class="job-picker-meta">
                    <span>{{ item.sourceLabel }}</span>
                  </div>
                  <div class="job-picker-preview">
                    <div class="job-picker-preview-item">
                      <span>目标</span>
                      <p>{{ item.previewTarget }}</p>
                    </div>
                    <div class="job-picker-preview-item">
                      <span>差距</span>
                      <p>{{ item.previewGap }}</p>
                    </div>
                    <div class="job-picker-preview-item">
                      <span>短期重点</span>
                      <p>{{ item.previewAction }}</p>
                    </div>
                  </div>
                </div>
                <div class="job-picker-actions-col">
                  <div class="job-picker-card-actions">
                    <el-button
                      type="primary"
                      :loading="bootstrappingPlan && pendingJobId === item.jobId"
                      @click="selectJobContext(item.jobId)"
                    >
                      {{ item.hasSavedReport ? '切换查看' : '生成并切换' }}
                    </el-button>
                  </div>
                </div>
              </article>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <el-empty v-else description="暂未找到可用的岗位匹配结果">
        <template #description>
          <span>先去完成人岗匹配，系统才知道要为哪个岗位生成生涯报告。</span>
        </template>
      </el-empty>
    </section>

    <!-- Hero 区域 -->
    <section v-if="hasActiveJobContext && activeView === 'report'" class="hero-panel">
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
          <span v-if="lastIntegrityCheck" class="meta-item meta-item--accent">
            <el-icon><Check /></el-icon>
            AI 检查 {{ lastIntegrityCheck.overall_score }} 分
          </span>
        </div>
      </div>

      <div class="hero-export hero-export--summary">
        <div class="export-title">报告状态</div>
        <div class="hero-summary-mini">
          <span>目标岗位：{{ reportWorkbenchSummary.targetPosition }}</span>
          <span>岗位画像：{{ reportWorkbenchSummary.targetProfileSummary }}</span>
          <span>导出范围：仅正文工作区</span>
        </div>
      </div>
    </section>

    <section v-if="hasActiveJobContext && activeView === 'report'" class="summary-strip summary-strip--workbench">
      <article class="summary-card">
        <span>目标岗位</span>
        <strong>{{ reportWorkbenchSummary.targetPosition }}</strong>
      </article>
      <article class="summary-card">
        <span>岗位画像参考</span>
        <p>{{ reportWorkbenchSummary.targetProfileSummary }}</p>
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
    <section v-if="hasActiveJobContext && activeView === 'report'" class="stats-grid">
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
          <span class="stat-label">学习资源</span>
          <strong class="stat-value">{{ aggregatedResources.length }}</strong>
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

    <div v-if="hasActiveJobContext && activeView === 'report'" class="report-layout">
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
          <section class="report-cover">
            <div class="report-cover-main">
              <p class="section-group-kicker">Career Planning Report</p>
              <h1>{{ report.target_position || '职业发展报告' }}</h1>
              <p class="report-cover-desc">
                围绕目标岗位、能力差距、短中期路径和行动清单展开，帮助用户快速理解当前状态、下一步重点与导出内容范围。
              </p>
              <div class="report-cover-meta">
                <span v-for="item in reportMetaFacts" :key="item.label" class="report-cover-meta-item">
                  <strong>{{ item.label }}</strong>
                  <span>{{ item.value }}</span>
                </span>
              </div>
            </div>

            <div class="report-cover-side">
              <article class="report-cover-panel">
                <span class="report-cover-panel__label">导出摘要</span>
                <strong>{{ reportWorkbenchSummary.targetPosition }}</strong>
                <p>{{ reportWorkbenchSummary.targetProfileSummary }}</p>
              </article>
              <article class="report-cover-panel report-cover-panel--accent">
                <span class="report-cover-panel__label">当前进度</span>
                <strong>{{ progressPercent }}%</strong>
                <p>{{ checkedActions.length }}/{{ report.action_checklist.length }} 项行动已标记完成</p>
              </article>
            </div>
          </section>

          <section class="report-highlight-grid">
            <article
              v-for="item in reportSnapshotCards"
              :key="item.label"
              class="report-highlight-card"
            >
              <span>{{ item.label }}</span>
              <strong>{{ item.title }}</strong>
              <p>{{ item.desc }}</p>
            </article>
          </section>

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

            <article class="content-card content-card--full">
              <div class="card-head">
                <div>
                  <p class="card-kicker">Target Profile</p>
                  <h2>目标岗位画像摘要</h2>
                  <span class="card-subtitle">根据接口返回的岗位信息摘要，帮助对齐目标岗位要求与发展路径。</span>
                </div>
              </div>
              <div class="goal-box goal-box--soft">
                <p class="detail-block">{{ targetProfileSummaryText }}</p>
              </div>
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

              <div v-if="aggregatedResources.length" class="resource-summary-strip">
                <div class="resource-summary-chip">
                  <span>短期计划资源</span>
                  <strong>{{ shortTermResourceCount }}</strong>
                </div>
                <div class="resource-summary-chip">
                  <span>中期计划资源</span>
                  <strong>{{ midTermResourceCount }}</strong>
                </div>
                <div class="resource-summary-chip">
                  <span>优先查看</span>
                  <strong>{{ aggregatedResources[0]?.title || '暂无' }}</strong>
                </div>
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
                      <span v-if="job.company_industry || job.companyIndustry">{{ job.company_industry || job.companyIndustry }}</span>
                      <span v-if="job.company_scale || job.companyScale">{{ job.company_scale || job.companyScale }}</span>
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

              <div v-if="report.action_checklist.length" class="action-summary-card">
                <span class="goal-label">执行提示</span>
                <p class="detail-block">
                  优先从未完成项里选择 1-2 项安排到本周日程，完成后再回来更新勾选状态，能更直观看到推进进度。
                </p>
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
              <el-tag :type="aiCapabilityTagType" round>{{ aiCapabilityLabel }}</el-tag>
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
              <el-button
                type="primary"
                plain
                :loading="polishingSectionKey === selectedSection"
                @click="polishOneSection(selectedSection)"
              >
                润色当前区块
              </el-button>
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
              <el-button :loading="checkingWithAi" @click="runCompletenessCheck">检查完整性</el-button>
              <el-button type="primary" :loading="polishingAll" @click="polishAllSections">润色整份报告</el-button>
            </div>
          </div>

          <div class="tool-block">
            <span class="tool-title">接口状态</span>
            <div class="audit-grid">
              <div class="audit-card">
                <span>报告来源</span>
                <p>{{ reportSourceLabel }}</p>
              </div>
              <div class="audit-card">
                <span>AI 检查</span>
                <p>{{ lastIntegrityCheck?.summary || '尚未执行 AI 完整性检查' }}</p>
              </div>
              <div class="audit-card">
                <span>最近同步</span>
                <p>{{ lastSyncedAt }}</p>
              </div>
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
          <el-tag v-if="currentInternship.company_industry || currentInternship.companyIndustry" round>
            {{ currentInternship.company_industry || currentInternship.companyIndustry }}
          </el-tag>
          <el-tag v-if="currentInternship.company_scale || currentInternship.companyScale" round type="info">
            {{ currentInternship.company_scale || currentInternship.companyScale }}
          </el-tag>
        </div>
        <p class="detail-block">{{ currentInternship.reason || '暂无推荐理由' }}</p>
        <p class="detail-block">{{ currentInternship.content || '暂无岗位描述' }}</p>
        <el-button v-if="currentInternship.url" type="primary" @click="openLink(currentInternship.url)">
          前往岗位链接
        </el-button>
      </div>
    </el-drawer>

    <!-- AI 完整性检查等待动画 -->
    <transition name="ai-processing-fade">
      <div v-if="checkingWithAi" class="ai-processing-overlay">
        <div class="ai-processing-card">
          <div class="ai-processing-badge">AI 完整性检查中</div>
          <el-icon class="loading-icon ai-processing-icon" :size="54">
            <Loading />
          </el-icon>
          <h3>正在分析报告完整性</h3>
          <p>我们正在检查报告各区块的完整度，识别缺失内容和可优化表达。</p>
          <div class="ai-processing-progress">
            <span class="progress-dot"></span>
            <span class="progress-dot"></span>
            <span class="progress-dot"></span>
          </div>
          <div class="ai-processing-tip">检查完成后将显示详细结果，请稍候片刻。</div>
        </div>
      </div>
    </transition>

    <!-- AI 润色等待动画 -->
    <transition name="ai-processing-fade">
      <div v-if="polishingAll || polishingSectionKey" class="ai-processing-overlay">
        <div class="ai-processing-card">
          <div class="ai-processing-badge">AI 智能润色中</div>
          <el-icon class="loading-icon ai-processing-icon" :size="54">
            <MagicStick />
          </el-icon>
          <h3>正在优化文本表达</h3>
          <p>{{ polishingSectionKey ? `正在润色${sectionLabel(polishingSectionKey)}内容，提升措辞专业性...` : '正在逐段润色整份报告，优化表达清晰度...' }}</p>
          <div class="ai-processing-progress">
            <span class="progress-dot"></span>
            <span class="progress-dot"></span>
            <span class="progress-dot"></span>
          </div>
          <div class="ai-processing-tip">润色完成后将自动更新内容，请稍候片刻。</div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, toRaw, watch } from 'vue'
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
import { useRoute, useRouter } from 'vue-router'
import {
  checkReportIntegrityApi,
  getReportPlanApi,
  polishReportParagraphApi,
  type ReportIntegrityCheckResponse,
  type ReportPolishType,
} from '@/api/report'
import { useCareerReportStore } from '@/stores'
import {
  createEmptyCareerReport,
  normalizeGrowthPlanData,
  type EditableSectionKey,
  type GrowthPlanData,
  type InternshipItem,
  type PlanTask,
  type ResourceItem,
} from '@/types/career-report'
import type { JobMatchItem } from '@/types/job-match'
import { getMockCareerReportByJobId, mockCareerReportData } from '@/mock/mockdata/CareerReport_mockdata'
import { usePoints } from '@/composables/usePoints'

type AssistantNote = {
  message: string
  type: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  time: string
}

type ReportSource = 'props' | 'store' | 'api' | 'mock' | 'empty'
type ReportViewMode = 'report' | 'jobs'
type JobOption = {
  jobId: string
  jobName: string
  summary: string
  scoreLabel: string
  sourceLabel: string
  jobIdLabel: string
  hasSavedReport: boolean
  previewTarget: string
  previewGap: string
  previewAction: string
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

const route = useRoute()
const router = useRouter()
const reportStore = useCareerReportStore()
const ENABLE_MOCK = import.meta.env.VITE_ENABLE_MOCK === 'true'

// 积分系统
const { consumePoints } = usePoints()

// 生成报告（带积分检查）
async function generateReportForJobWithPoints(jobId: string) {
  // 扣除积分
  const result = await consumePoints('careerReport', '生涯规划报告')
  if (!result.success) {
    // 积分不足，已弹出提示
    return
  }
  // 积分扣除成功，继续生成报告
  await generateReportForJob(jobId)
}

const emptyReport = createEmptyCareerReport
function deepClone<T>(data: T): T {
  const source = toRaw(data)
  if (typeof structuredClone === 'function') {
    try {
      return structuredClone(source)
    } catch (error) {
      console.warn('structuredClone failed, fallback to JSON clone:', error)
    }
  }
  // Fallback: JSON method (has limitations with Dates, undefined, functions, etc.)
  return JSON.parse(JSON.stringify(source))
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
    // 去除Markdown标题符号
    .replace(/^#{1,6}\s+/gm, '')
    // 去除其他Markdown符号
    .replace(/\*\*|__/g, '')
    .replace(/[`*_~]/g, '')
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

function htmlToExportText(html: string): string {
  if (!html) return ''

  const text = html
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/p>/gi, '\n')
    .replace(/<\/div>/gi, '\n')
    .replace(/<\/li>/gi, '\n')
    .replace(/<li[^>]*>/gi, '• ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n[ \t]+/g, '\n')
    .replace(/[ \t]{2,}/g, ' ')
    .replace(/\n{3,}/g, '\n\n')
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

/**
 * 清理AI润色返回的内容，去除特殊符号和Markdown标记
 */
function cleanAiPolishedContent(text: string): string {
  return text
    // 去除Markdown标题符号 (### 标题)
    .replace(/^#{1,6}\s+/gm, '')
    // 去除加粗和斜体标记
    .replace(/\*\*|__/g, '')
    .replace(/\*|_/g, '')
    // 去除行内代码
    .replace(/`([^`]+)`/g, '$1')
    // 去除删除线
    .replace(/~~([^~]+)~~/g, '$1')
    // 去除链接标记，保留文本 [文本](链接) -> 文本
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    // 去除图片标记
    .replace(/!\[[^\]]*\]\([^)]+\)/g, '')
    // 去除引用符号
    .replace(/^>\s*/gm, '')
    // 去除列表符号
    .replace(/^[-*+]\s+/gm, '')
    .replace(/^\d+\.\s+/gm, '')
    // 去除水平线
    .replace(/^-{3,}$/gm, '')
    // 去除多余的空行
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

const report = ref<GrowthPlanData>(emptyReport())
const reportSource = ref<ReportSource>('empty')
const lastSyncedAt = ref('未同步')
const checkingWithAi = ref(false)
const polishingAll = ref(false)
const polishingSectionKey = ref<EditableSectionKey | null>(null)
const savingReport = ref(false)
const bootstrappingPlan = ref(false)
const pendingJobId = ref('')
const lastIntegrityCheck = ref<ReportIntegrityCheckResponse | null>(null)
const availableJobs = ref<JobOption[]>([])
const jobCollapsePanels = ref<string[]>(['other-jobs'])
const activeView = ref<ReportViewMode>('jobs')

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
  const useMock = !data && ENABLE_MOCK
  const mockData = useMock ? getMockCareerReportByJobId(getRouteJobIdString() || reportStore.currentJobId || undefined) : null
  const value = normalizeGrowthPlanData(deepClone(data || mockData || emptyReport()))
  report.value = value
  richContent.student_summary = textToHtml(value.student_summary)
  richContent.current_gap = textToHtml(value.current_gap)
  richContent.short_goal = textToHtml(value.short_term_plan.goal)
  richContent.mid_goal = textToHtml(value.mid_term_plan.goal)
  richContent.career_progression = textToHtml(value.mid_term_plan.career_progression)
  restoreChecklist()
}

function markReportSynced(source: ReportSource) {
  reportSource.value = source
  lastSyncedAt.value = new Date().toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function getRouteJobIdString() {
  const raw = route.query.jobId ?? route.query.job_id
  if (Array.isArray(raw)) return raw[0] || ''
  return typeof raw === 'string' ? raw : ''
}

const activeJobId = computed(() => getRouteJobIdString() || reportStore.currentJobId || '')
const hasActiveJobContext = computed(() => !!activeJobId.value)
const showJobSwitcherPanel = computed(() => !hasActiveJobContext.value || activeView.value === 'jobs')

function switchReportView(view: ReportViewMode) {
  activeView.value = view
}

function hasPersistedReportData(data?: GrowthPlanData) {
  if (!data) return false
  const candidate = data.target_position?.trim()
  const defaultTarget = createEmptyCareerReport().target_position
  return Boolean(
    (candidate && candidate !== defaultTarget) ||
    data.target_position_profile_summary ||
    data.student_summary ||
    data.current_gap ||
    data.short_term_plan.goal ||
    data.mid_term_plan.goal ||
    data.short_term_plan.focus_areas.length ||
    data.short_term_plan.milestones.length ||
    data.mid_term_plan.skill_roadmap.length ||
    data.mid_term_plan.milestones.length ||
    data.action_checklist.length ||
    data.tips.length,
  )
}

function getInitialReportData(data?: GrowthPlanData) {
  const routeJobId = getRouteJobIdString()

  if (data) {
    return { source: 'props' as const, data }
  }

  // 优先检查当前 routeJobId 对应的存储报告
  if (routeJobId) {
    const reportForJob = reportStore.getReportByJob(routeJobId)
    if (reportForJob && hasPersistedReportData(reportForJob)) {
      reportStore.setCurrentJobId(routeJobId)
      return { source: 'store' as const, data: reportForJob }
    }
    // 如果有 routeJobId 但没有存储数据，使用 mock 数据
    if (ENABLE_MOCK) {
      const mockData = getMockCareerReportByJobId(routeJobId)
      if (mockData && hasPersistedReportData(mockData)) {
        return { source: 'mock' as const, data: mockData }
      }
    }
  }

  if (reportStore.currentJobId) {
    const currentStoredReport = reportStore.getReportByJob(reportStore.currentJobId)
    if (currentStoredReport && hasPersistedReportData(currentStoredReport)) {
      return { source: 'store' as const, data: currentStoredReport }
    }
  }

  // 只有当没有 routeJobId 时，才使用默认的 reportStore.report
  if (!routeJobId && reportStore.hasHydrated && hasPersistedReportData(reportStore.report)) {
    return { source: 'store' as const, data: reportStore.report }
  }

  if (ENABLE_MOCK) {
    return {
      source: 'mock' as const,
      data: getMockCareerReportByJobId(routeJobId || reportStore.currentJobId || undefined),
    }
  }

  return { source: 'empty' as const, data: emptyReport() }
}

function syncReportWithSource(data?: GrowthPlanData) {
  const initial = getInitialReportData(data)
  syncReport(initial.data)
  markReportSynced(initial.source)
}

function buildJobOptions() {
  let parsedItems: JobMatchItem[] = []

  try {
    const stored = localStorage.getItem('jobMatchResult')
    parsedItems = stored ? JSON.parse(stored) as JobMatchItem[] : []
  } catch (error) {
    console.error('加载岗位匹配结果失败:', error)
  }

  availableJobs.value = parsedItems
    .map((item) => {
      const jobId = String(item.job_id || item.raw_data?.job_id || '')
      if (!jobId) return null
      const savedReport = reportStore.getReportByJob(jobId)
      const previewReport = normalizeGrowthPlanData(
        deepClone(savedReport || getMockCareerReportByJobId(jobId)),
      )
      const scorePercent = typeof item.score === 'number' ? Math.round(item.score * 100) : null
      return {
        jobId,
        jobName: item.raw_data?.job_name || `岗位 ${jobId}`,
        summary: item.deep_analysis?.actionable_advice || item.deep_analysis?.all_analysis || '可基于当前匹配结果生成对应岗位报告。',
        scoreLabel: scorePercent !== null ? `匹配度 ${scorePercent}%` : '',
        sourceLabel: item.deep_analysis?.can_apply ? '来自人岗匹配结果' : '建议进一步补齐能力后尝试',
        jobIdLabel: `job_id: ${jobId}`,
        hasSavedReport: hasPersistedReportData(savedReport || undefined),
        previewTarget: previewReport.target_position || item.raw_data?.job_name || '待生成目标岗位报告',
        previewGap: previewReport.current_gap || '生成后可查看该岗位的关键能力差距。',
        previewAction:
          previewReport.short_term_plan.quick_wins[0] ||
          previewReport.action_checklist[0] ||
          previewReport.short_term_plan.goal ||
          '生成后可查看短期行动重点。',
      } satisfies JobOption
    })
    .filter((item): item is JobOption => !!item)
}

function loadJobOptions() {
  buildJobOptions()
}

const currentJobOption = computed(() => {
  if (!activeJobId.value) return null
  return availableJobs.value.find(item => item.jobId === activeJobId.value) || null
})

const otherJobOptions = computed(() => {
  if (!activeJobId.value) return availableJobs.value
  return availableJobs.value.filter(item => item.jobId !== activeJobId.value)
})

watch(
  () => props.data,
  val => {
    syncReportWithSource(val)
  },
  { immediate: true, deep: true },
)

watch(
  () => route.query.jobId ?? route.query.job_id,
  () => {
    const routeJobId = getRouteJobIdString()
    activeView.value = routeJobId ? 'report' : 'jobs'
    if (!routeJobId) return

    syncRouteJobContext(routeJobId)
    const storedReport = reportStore.getReportByJob(routeJobId)
    if (storedReport && hasPersistedReportData(storedReport)) {
      syncReport(storedReport)
      markReportSynced('store')
      return
    }

    void bootstrapReportPlan()
  },
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

function getPolishReportType(key: EditableSectionKey): ReportPolishType {
  if (key === 'current_gap') return 'match_analysis'
  if (key === 'short_goal' || key === 'mid_goal') return 'action_plan'
  return 'other'
}

function buildPolishContext(key: EditableSectionKey) {
  return {
    section_key: key,
    section_label: sectionLabel(key),
    job_title: report.value.target_position,
    short_term_duration: report.value.short_term_plan.duration,
    mid_term_duration: report.value.mid_term_plan.duration,
  }
}

function getSectionContent(key: EditableSectionKey) {
  return richContent[key]
}

function setSectionContent(key: EditableSectionKey, value: string) {
  richContent[key] = value
}

function openEditor(key: EditableSectionKey) {
  if (!activeJobId.value) return
  selectedSection.value = key
  router.push({
    name: 'report-editor',
    query: { section: key, jobId: activeJobId.value },
  })
}

async function polishOneSection(key: EditableSectionKey) {
  const originalText = htmlToText(getSectionContent(key))

  if (!originalText) {
    ElMessage.warning(`请先补充${sectionLabel(key)}内容`)
    return
  }

  polishingSectionKey.value = key

  try {
    if (originalText.length >= 20) {
      const res = await polishReportParagraphApi({
        original_content: originalText,
        report_type: getPolishReportType(key),
        context: buildPolishContext(key),
      })
      const result = res.data

      if (result?.code === 200 && result.data?.polished_content) {
        // 清理AI返回的特殊符号
        const cleanedContent = cleanAiPolishedContent(result.data.polished_content)
        const polished = textToHtml(cleanedContent)
        setSectionContent(key, polished)
        pushAssistantNote(`已通过 AI 润色 ${sectionLabel(key)}`, 'success')
        emit('polish-request', {
          section: key,
          content: cleanedContent,
        })
        return
      }

      throw new Error(result?.msg || 'AI 润色失败')
    }

    const polished = smartPolishHtml(getSectionContent(key))
    setSectionContent(key, polished)
    pushAssistantNote(`${sectionLabel(key)}内容较短，已使用本地润色兜底`, 'info')
    emit('polish-request', {
      section: key,
      content: htmlToText(polished),
    })
  } catch (error: any) {
    console.error(error)
    const polished = smartPolishHtml(getSectionContent(key))
    setSectionContent(key, polished)
    pushAssistantNote(`AI 润色失败，已使用本地润色兜底：${sectionLabel(key)}`, 'warning')
    ElMessage.warning(error?.message || 'AI 润色失败，已切换为本地润色')
    emit('polish-request', {
      section: key,
      content: htmlToText(polished),
    })
  } finally {
    polishingSectionKey.value = null
  }
}

async function polishAllSections() {
  polishingAll.value = true

  try {
    for (const item of editableSections) {
      await polishOneSection(item.key)
    }
    pushAssistantNote('已完成整份报告的文本润色', 'success')
    ElMessage.success('全文润色完成')
  } finally {
    polishingAll.value = false
  }
}

function buildSubmitData(options?: { preserveLineBreaks?: boolean }): GrowthPlanData {
  const toText = options?.preserveLineBreaks ? htmlToExportText : htmlToText
  const result = normalizeGrowthPlanData(deepClone(report.value))
  result.student_summary = toText(richContent.student_summary)
  result.current_gap = toText(richContent.current_gap)
  result.short_term_plan.goal = toText(richContent.short_goal)
  result.mid_term_plan.goal = toText(richContent.mid_goal)
  result.mid_term_plan.career_progression = toText(richContent.career_progression)
  return result
}

function persistReport(payload: GrowthPlanData) {
  const normalized = normalizeGrowthPlanData(deepClone(payload))
  if (activeJobId.value) {
    reportStore.setReportForJob(activeJobId.value, normalized)
  } else {
    reportStore.setReport(normalized)
  }
  markReportSynced('store')
  buildJobOptions()
}

function handleSave(showMessage = true) {
  const payload = buildSubmitData()
  savingReport.value = true
  persistReport(payload)
  emit('save', payload)
  if (showMessage) {
    ElMessage.success('已保存当前报告')
  }
  savingReport.value = false
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

const targetProfileSummaryText = computed(() => {
  return report.value.target_position_profile_summary || '暂无岗位画像摘要，可继续通过接口或编辑页补充目标岗位要求。'
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
    targetProfileSummary: targetProfileSummaryText.value.slice(0, 120),
    advantage: advantage.slice(0, 72),
    gap: gap.slice(0, 72),
    shortAction: shortAction.slice(0, 56),
    midDirection: midDirection.slice(0, 56),
  }
})

const reportMetaFacts = computed(() => [
  {
    label: '生成日期',
    value: new Date().toLocaleDateString('zh-CN'),
  },
  {
    label: '短期周期',
    value: report.value.short_term_plan.duration || '待补充',
  },
  {
    label: '中期周期',
    value: report.value.mid_term_plan.duration || '待补充',
  },
  {
    label: '报告来源',
    value: reportSourceLabel.value,
  },
])

const reportSnapshotCards = computed(() => [
  {
    label: '当前优势',
    title: '你已经具备的基础',
    desc: reportWorkbenchSummary.value.advantage,
  },
  {
    label: '关键差距',
    title: '优先补齐的能力',
    desc: reportWorkbenchSummary.value.gap,
  },
  {
    label: '最近行动',
    title: '短期最值得先做',
    desc: reportWorkbenchSummary.value.shortAction,
  },
  {
    label: '中期方向',
    title: '后续成长路线',
    desc: reportWorkbenchSummary.value.midDirection,
  },
])

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

const shortTermResourceCount = computed(() =>
  aggregatedResources.value.filter(item => item.planLabel === '短期计划').length,
)

const midTermResourceCount = computed(() =>
  aggregatedResources.value.filter(item => item.planLabel === '中期计划').length,
)

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
  if (item.category_name || item.categoryName) return item.category_name || item.categoryName || '学习资源'
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

const reportSourceLabel = computed(() => {
  if (bootstrappingPlan.value) return '正在从后端生成报告'
  if (reportSource.value === 'api') return '后端报告接口'
  if (reportSource.value === 'store') return '本地已保存报告'
  if (reportSource.value === 'props') return '父组件传入数据'
  if (reportSource.value === 'mock') return '开发示例数据'
  return '空白报告模板'
})

const aiCapabilityLabel = computed(() => {
  if (polishingAll.value || polishingSectionKey.value) return 'AI 润色进行中'
  if (checkingWithAi.value) return 'AI 检查进行中'
  if (lastIntegrityCheck.value) return 'AI 接口已同步'
  return 'AI 接口可用'
})

const aiCapabilityTagType = computed(() => {
  if (polishingAll.value || polishingSectionKey.value || checkingWithAi.value) return 'warning'
  if (lastIntegrityCheck.value?.is_complete === false) return 'danger'
  return 'success'
})

function syncRouteJobContext(jobId?: string) {
  const normalized = jobId || ''
  if (normalized) {
    reportStore.setCurrentJobId(normalized)
  }
}

function resolveRouteJobId(): string | null {
  const raw = route.query.jobId ?? route.query.job_id
  if (Array.isArray(raw)) return raw[0] || null
  return typeof raw === 'string' && raw.trim() ? raw.trim() : null
}

async function selectJobContext(jobId: string) {
  syncRouteJobContext(jobId)
  const storedReport = reportStore.getReportByJob(jobId)
  const hasReport = storedReport && hasPersistedReportData(storedReport)

  await router.replace({
    name: 'report',
    query: { ...route.query, jobId },
  })

  // 如果已生成过报告，直接切换查看（不消耗积分）
  if (hasReport) {
    syncReport(storedReport)
    markReportSynced('store')
    activeView.value = 'report'
    return
  }

  // 未生成过，先消耗积分再执行生成
  await generateReportForJobWithPoints(jobId)
}

async function generateReportForJob(jobId: string) {
  pendingJobId.value = jobId
  syncRouteJobContext(jobId)

  await router.replace({
    name: 'report',
    query: { ...route.query, jobId },
  })

  await bootstrapReportPlan()
  pendingJobId.value = ''
  activeView.value = 'report'
}

function goToJobMatching() {
  router.push({ name: 'job-matching' })
}

async function bootstrapReportPlan() {
  const jobId = resolveRouteJobId()
  const jobIdKey = jobId || ''

  if (!jobId) {
    return
  }

  const storedReport = jobIdKey ? reportStore.getReportByJob(jobIdKey) : null

  // 优先检查 mock 模式下是否有对应数据（避免被旧 store 数据覆盖）
  if (ENABLE_MOCK) {
    const mockData = getMockCareerReportByJobId(jobId)
    if (mockData && hasPersistedReportData(mockData)) {
      console.log('[bootstrapReportPlan] 使用 Mock 数据:', jobId, '->', mockData.target_position)
      syncReport(mockData)
      persistReport(mockData)
      syncRouteJobContext(jobIdKey)
      markReportSynced('mock')
      pushAssistantNote(`已加载 ${mockData.target_position} 的示例报告数据`, 'success')
      return
    }
  }

  // 使用已存储的报告（对应岗位）
  if (hasPersistedReportData(storedReport || undefined)) {
    syncReport(storedReport)
    markReportSynced('store')
    return
  }

  bootstrappingPlan.value = true

  try {
    const res = await getReportPlanApi({ jobId })
    const result = res.data

    if (result?.code === 200 && result.data) {
      syncReport(result.data)
      persistReport(result.data)
      syncRouteJobContext(jobIdKey)
      markReportSynced('api')
      pushAssistantNote(`已根据岗位 ${jobId} 生成职业发展报告`, 'success')
      return
    }

    throw new Error(result?.msg || '报告生成失败')
  } catch (error: any) {
    console.error(error)
    // API 失败时，尝试使用 mock 数据
    if (ENABLE_MOCK) {
      const mockData = getMockCareerReportByJobId(jobId)
      if (mockData && hasPersistedReportData(mockData)) {
        syncReport(mockData)
        persistReport(mockData)
        markReportSynced('mock')
        pushAssistantNote(`已加载岗位 ${jobId} 的示例报告数据`, 'success')
        bootstrappingPlan.value = false
        return
      }
    }
    pushAssistantNote('报告生成接口调用失败，当前保留本地数据', 'warning')
    ElMessage.warning(error?.message || '报告生成失败，已保留当前页面数据')
  } finally {
    bootstrappingPlan.value = false
  }
}

function buildReportContentForCheck() {
  const payload = buildSubmitData({ preserveLineBreaks: true })

  const shortMilestones = payload.short_term_plan.milestones
    .map(item => {
      const results = item.key_results.length ? `关键成果：${item.key_results.join('；')}` : ''
      const tasks = item.tasks
        .map(task => {
          const taskResources = getTaskResources(task)
          const resources = taskResources.length
            ? `资源：${taskResources.map(resource => resource.title || resource.name || '未命名资源').join('、')}`
            : ''
          return [
            `任务：${task.task_name}`,
            task.description ? `说明：${task.description}` : '',
            task.skill_target ? `目标能力：${task.skill_target}` : '',
            task.success_criteria ? `成功标准：${task.success_criteria}` : '',
            resources,
          ].filter(Boolean).join('；')
        })
        .filter(Boolean)
        .join('\n')

      return [
        `里程碑：${item.milestone_name}`,
        item.target_date ? `目标日期：${item.target_date}` : '',
        results,
        tasks,
      ].filter(Boolean).join('\n')
    })
    .join('\n\n')

  const midMilestones = payload.mid_term_plan.milestones
    .map(item => {
      const results = item.key_results.length ? `关键成果：${item.key_results.join('；')}` : ''
      const tasks = item.tasks
        .map(task => {
          const taskResources = getTaskResources(task)
          const resources = taskResources.length
            ? `资源：${taskResources.map(resource => resource.title || resource.name || '未命名资源').join('、')}`
            : ''
          return [
            `任务：${task.task_name}`,
            task.description ? `说明：${task.description}` : '',
            task.skill_target ? `目标能力：${task.skill_target}` : '',
            task.success_criteria ? `成功标准：${task.success_criteria}` : '',
            resources,
          ].filter(Boolean).join('；')
        })
        .filter(Boolean)
        .join('\n')

      return [
        `里程碑：${item.milestone_name}`,
        item.target_date ? `目标日期：${item.target_date}` : '',
        results,
        tasks,
      ].filter(Boolean).join('\n')
    })
    .join('\n\n')

  return [
    `目标岗位：${payload.target_position}`,
    '',
    '【学生画像摘要】',
    payload.student_summary,
    '',
    '【能力差距分析】',
    payload.current_gap,
    '',
    '【短期计划】',
    `周期：${payload.short_term_plan.duration}`,
    `阶段目标：${payload.short_term_plan.goal}`,
    `重点领域：${payload.short_term_plan.focus_areas.join('、') || '暂无'}`,
    `快速行动：${payload.short_term_plan.quick_wins.join('、') || '暂无'}`,
    shortMilestones || '暂无短期里程碑',
    '',
    '【中期计划】',
    `周期：${payload.mid_term_plan.duration}`,
    `阶段目标：${payload.mid_term_plan.goal}`,
    `技能路线：${payload.mid_term_plan.skill_roadmap.join('、') || '暂无'}`,
    `职业发展预期：${payload.mid_term_plan.career_progression}`,
    midMilestones || '暂无中期里程碑',
    '',
    '【推荐实习】',
    payload.mid_term_plan.recommended_internships.length
      ? payload.mid_term_plan.recommended_internships
        .map(item => [item.job_title, item.company_name, item.reason].filter(Boolean).join(' - '))
        .join('\n')
      : '暂无推荐实习',
    '',
    '【行动清单】',
    payload.action_checklist.join('；') || '暂无行动清单',
    '',
    '【学习建议】',
    payload.tips.join('；') || '暂无学习建议',
  ].join('\n')
}

function runLocalCompletenessCheck() {
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

async function runCompletenessCheck() {
  // 优先调用后端 AI 接口进行完整性检查
  const reportContent = buildReportContentForCheck()

  // 内容太短时使用本地检查
  if (reportContent.replace(/\s+/g, '').length < 50) {
    checkingWithAi.value = true
    await new Promise(resolve => setTimeout(resolve, 500))
    try {
      runLocalCompletenessCheck()
    } finally {
      checkingWithAi.value = false
    }
    return
  }

  checkingWithAi.value = true

  try {
    const res = await checkReportIntegrityApi({
      report_content: reportContent,
      job_title: report.value.target_position || undefined,
    })
    const result = res.data

    if (result?.code === 200 && result.data) {
      lastIntegrityCheck.value = result.data
      pushAssistantNote(`AI 完整性检查完成，评分 ${result.data.overall_score}`, result.data.is_complete ? 'success' : 'warning')
      result.data.missing_items.forEach(item => pushAssistantNote(`待补充：${item}`, 'warning'))
      ElMessage[result.data.is_complete ? 'success' : 'warning'](
        result.data.is_complete
          ? 'AI 完整性检查通过'
          : `AI 检查提示 ${result.data.missing_items.length} 项待补充内容`,
      )
      return
    }

    throw new Error(result?.msg || 'AI 完整性检查失败')
  } catch (error: any) {
    console.error('AI 完整性检查失败:', error)
    pushAssistantNote('AI 完整性检查失败，已切换为本地检查', 'warning')
    ElMessage.warning(error?.message || 'AI 完整性检查失败，已切换为本地检查')
    runLocalCompletenessCheck()
  } finally {
    checkingWithAi.value = false
  }
}

const reportRef = ref<HTMLElement | null>(null)

/**
 * 创建用于PDF导出的临时容器，展开所有折叠内容并内嵌Drawer内容
 */
async function exportPdf() {
  if (!reportRef.value) return

  // 创建临时导出容器
  const exportContainer = document.createElement('div')
  exportContainer.className = 'pdf-export-container'
  exportContainer.style.cssText = `
    position: fixed;
    left: -9999px;
    top: 0;
    width: 1200px;
    background: white;
    z-index: -1;
    padding: 40px;
  `

  // 克隆报告内容
  const reportClone = reportRef.value.cloneNode(true) as HTMLElement
  reportClone.classList.add('report-export-mode')

  // 1. 展开所有 el-collapse 折叠面板
  const collapseItems = reportClone.querySelectorAll('.el-collapse-item')
  collapseItems.forEach(item => {
    item.classList.add('is-active')
    const header = item.querySelector('.el-collapse-item__header')
    const wrap = item.querySelector('.el-collapse-item__wrap')
    const content = item.querySelector('.el-collapse-item__content')
    if (header) {
      (header as HTMLElement).style.display = 'none' // 隐藏折叠头部
    }
    if (wrap) {
      const wrapEl = wrap as HTMLElement
      wrapEl.style.display = 'block'
      wrapEl.style.height = 'auto'
      wrapEl.style.visibility = 'visible'
    }
    if (content) {
      const contentEl = content as HTMLElement
      contentEl.style.display = 'block'
      contentEl.style.paddingBottom = '20px'
    }
  })

  // 2. 隐藏顶部导航、AI助手按钮等不需要导出的元素
  const topNav = reportClone.querySelector('.top-nav')
  const assistantFab = reportClone.querySelector('.assistant-fab')
  const outline = reportClone.querySelector('.report-outline')
  if (topNav) (topNav as HTMLElement).style.display = 'none'
  if (assistantFab) (assistantFab as HTMLElement).style.display = 'none'
  if (outline) (outline as HTMLElement).style.display = 'none'

  // 3. 将彩色面板转换为适合 PDF 的浅色样式
  const statCards = reportClone.querySelectorAll('.stat-card')
  statCards.forEach(card => {
    const el = card as HTMLElement
    el.style.background = '#f8fafc'
    el.style.color = '#475569'
    el.style.border = '1px solid #e2e8f0'
    // 恢复图标颜色
    const icon = el.querySelector('.stat-icon')
    if (icon) {
      const iconEl = icon as HTMLElement
      iconEl.style.background = '#eff6ff'
      iconEl.style.color = '#3b82f6'
    }
    const label = el.querySelector('.stat-label')
    if (label) (label as HTMLElement).style.color = '#64748b'
    const value = el.querySelector('.stat-value')
    if (value) (value as HTMLElement).style.color = '#1e293b'
  })

  const exportPanels = reportClone.querySelectorAll(
    '.report-cover, .report-cover-panel, .report-highlight-card, .section-summary-item, .goal-box, .result-box, .resource-summary-chip',
  )
  exportPanels.forEach(panel => {
    const el = panel as HTMLElement
    el.style.background = '#ffffff'
    el.style.border = '1px solid #d1d5db'
    el.style.boxShadow = 'none'
    el.style.color = '#374151'
  })

  // 处理其他渐变背景卡片
  const gradientElements = reportClone.querySelectorAll('[class*="gradient"], [class*="--primary"], [class*="--success"], [class*="--warning"], [class*="--info"]')
  gradientElements.forEach(el => {
    const element = el as HTMLElement
    if (element.classList.contains('stat-card')) {
      return
    }
    element.style.background = 'transparent'
  })

  // 4. 在推荐资源部分添加详细的资源列表
  const resourcesSection = reportClone.querySelector('#report-resources')
  if (resourcesSection && aggregatedResources.value.length > 0) {
    const detailSection = document.createElement('div')
    detailSection.className = 'pdf-resource-detail-section'
    detailSection.style.cssText = 'margin-top: 24px; padding: 20px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;'
    detailSection.innerHTML = `
      <h3 style="font-size: 18px; font-weight: 600; color: #1e293b; margin-bottom: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">
        详细资源列表
      </h3>
      <div style="display: flex; flex-direction: column; gap: 16px;">
        ${aggregatedResources.value.map((item, index) => `
          <div style="padding: 16px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
            <div style="font-weight: 600; font-size: 15px; color: #1e293b; margin-bottom: 8px;">
              ${index + 1}. ${item.title}
            </div>
            <div style="font-size: 13px; color: #475569; margin-bottom: 4px;">
              <span style="color: #0369a1; font-weight: 500;">类型：</span>${resourceType(item.raw)}
            </div>
            <div style="font-size: 13px; color: #475569; margin-bottom: 4px;">
              <span style="color: #0369a1; font-weight: 500;">阶段：</span>${item.planLabel} · ${item.originLabel}
            </div>
            ${item.taskName ? `<div style="font-size: 13px; color: #475569; margin-bottom: 4px;"><span style="color: #0369a1; font-weight: 500;">关联任务：</span>${item.taskName}</div>` : ''}
            ${item.reason || item.description ? `<div style="font-size: 13px; color: #334155; margin-top: 8px; line-height: 1.6;">${item.reason || item.description}</div>` : ''}
            ${item.raw.url ? `<div style="font-size: 12px; color: #0369a1; margin-top: 8px; word-break: break-all;">链接：${item.raw.url}</div>` : ''}
          </div>
        `).join('')}
      </div>
    `
    resourcesSection.appendChild(detailSection)
  }

  // 5. 在实习岗位部分添加详细的岗位描述
  const internshipSection = reportClone.querySelector('#report-internship')
  if (internshipSection && report.value.mid_term_plan.recommended_internships.length > 0) {
    const detailSection = document.createElement('div')
    detailSection.className = 'pdf-internship-detail-section'
    detailSection.style.cssText = 'margin-top: 24px; padding: 20px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;'
    detailSection.innerHTML = `
      <h3 style="font-size: 18px; font-weight: 600; color: #1e293b; margin-bottom: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">
        岗位详细描述
      </h3>
      <div style="display: flex; flex-direction: column; gap: 20px;">
        ${(report.value.mid_term_plan.recommended_internships as InternshipItem[]).map((job, index) => `
          <div style="padding: 20px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
            <div style="font-weight: 600; font-size: 16px; color: #1e293b; margin-bottom: 8px;">
              ${index + 1}. ${job.job_title}
            </div>
            <div style="font-size: 14px; color: #0369a1; margin-bottom: 12px; font-weight: 500;">
              ${job.company_name}
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
              ${job.city ? `<span style="padding: 4px 12px; background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 12px; font-size: 12px; color: #475569;">${job.city}</span>` : ''}
              ${job.salary ? `<span style="padding: 4px 12px; background: #fef3c7; border: 1px solid #fde68a; border-radius: 12px; font-size: 12px; color: #92400e;">${job.salary}</span>` : ''}
              <span style="padding: 4px 12px; background: #eff6ff; border: 1px solid #dbeafe; border-radius: 12px; font-size: 12px; color: #1e40af;">${job.days_per_week || '-'}天/周 · ${job.months || '-'}个月</span>
            </div>
            ${job.tech_stack ? `<div style="font-size: 13px; color: #475569; margin-bottom: 8px;"><span style="color: #047857; font-weight: 500;">技术栈：</span>${job.tech_stack}</div>` : ''}
            ${job.reason ? `<div style="font-size: 13px; color: #334155; margin-bottom: 8px; line-height: 1.6;"><span style="color: #047857; font-weight: 500;">推荐理由：</span>${job.reason}</div>` : ''}
            ${job.content ? `<div style="font-size: 13px; color: #334155; line-height: 1.6;"><span style="color: #047857; font-weight: 500;">岗位描述：</span>${job.content}</div>` : ''}
            ${job.url ? `<div style="font-size: 12px; color: #0369a1; margin-top: 8px; word-break: break-all;">投递链接：${job.url}</div>` : ''}
          </div>
        `).join('')}
      </div>
    `
    internshipSection.appendChild(detailSection)
  }

  // 6. 添加PDF导出专用样式 - 确保浅色背景和清晰文字
  const styleEl = document.createElement('style')
  styleEl.textContent = `
    .pdf-export-container * {
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }
    .pdf-export-container {
      background: #ffffff !important;
      color: #1e293b !important;
    }
    /* 隐藏所有按钮 */
    .pdf-export-container .el-button {
      display: none !important;
    }
    .pdf-export-container .report-export-mode {
      gap: 18px !important;
    }
    /* 将el-tag转为文本样式 */
    .pdf-export-container .el-tag {
      background: #ffffff !important;
      color: #374151 !important;
      border: 1px solid #d1d5db !important;
      padding: 2px 8px !important;
      border-radius: 4px !important;
      font-size: 12px !important;
      display: inline-block !important;
      height: auto !important;
      line-height: 1.5 !important;
    }
    /* 强制所有背景为浅色 */
    .pdf-export-container [class*="gradient"] {
      background: #ffffff !important;
      background-image: none !important;
    }
    .pdf-export-container .content-card,
    .pdf-export-container .milestone-card,
    .pdf-export-container .task-card,
    .pdf-export-container .internship-card,
    .pdf-export-container .resource-card,
    .pdf-export-container .goal-box,
    .pdf-export-container .result-box,
    .pdf-export-container .roadmap-item,
    .pdf-export-container .tip-card,
    .pdf-export-container .resource-summary-chip,
    .pdf-export-container .report-highlight-card,
    .pdf-export-container .report-cover-panel,
    .pdf-export-container .report-cover-meta-item,
    .pdf-export-container .check-item {
      background: #ffffff !important;
      border-color: #d1d5db !important;
      box-shadow: none !important;
    }
    .pdf-export-container .report-cover,
    .pdf-export-container .report-cover *,
    .pdf-export-container .report-highlight-card *,
    .pdf-export-container .report-cover-panel * {
      color: #1e293b !important;
      -webkit-text-fill-color: #1e293b !important;
    }
    .pdf-export-container .report-cover {
      background: #ffffff !important;
      border: 1px solid #d1d5db !important;
    }
    .pdf-export-container .card-head h2,
    .pdf-export-container .summary-card strong,
    .pdf-export-container .report-cover h1 {
      background: none !important;
      color: #0f172a !important;
      -webkit-text-fill-color: #0f172a !important;
    }
    .pdf-export-container .stat-card {
      background: #ffffff !important;
      border: 1px solid #d1d5db !important;
      color: #4b5563 !important;
    }
    .pdf-export-container .stat-card * {
      color: #4b5563 !important;
      -webkit-text-fill-color: #4b5563 !important;
    }
    .pdf-export-container .stat-value {
      color: #111827 !important;
      -webkit-text-fill-color: #111827 !important;
      font-weight: 600 !important;
    }
    .pdf-export-container .stat-icon {
      background: #f3f4f6 !important;
      color: #374151 !important;
      border: 1px solid #d1d5db !important;
    }
    /* 确保所有文字颜色可见 */
    .pdf-export-container h1, .pdf-export-container h2, .pdf-export-container h3,
    .pdf-export-container h4, .pdf-export-container h5, .pdf-export-container h6 {
      color: #111827 !important;
      -webkit-text-fill-color: #111827 !important;
    }
    .pdf-export-container p, .pdf-export-container span, .pdf-export-container div {
      color: #4b5563 !important;
    }
    .pdf-export-container .card-kicker,
    .pdf-export-container .section-group-kicker,
    .pdf-export-container .report-highlight-card span,
    .pdf-export-container .report-cover-panel__label,
    .pdf-export-container .report-cover-meta-item strong {
      color: #6b7280 !important;
      -webkit-text-fill-color: #6b7280 !important;
    }
    .pdf-export-container .roadmap-index,
    .pdf-export-container .tip-dot {
      background: #e5e7eb !important;
      color: #374151 !important;
      box-shadow: none !important;
      border: 1px solid #d1d5db !important;
    }
    .pdf-export-container .outline-chip,
    .pdf-export-container .meta-item,
    .pdf-export-container .job-picker-preview-item,
    .pdf-export-container .empty-state {
      background: #ffffff !important;
      color: #4b5563 !important;
      border-color: #d1d5db !important;
      box-shadow: none !important;
    }
    .pdf-export-container .el-progress-bar__outer,
    .pdf-export-container .el-progress-dashboard__track,
    .pdf-export-container .el-progress-circle__track {
      background: #e5e7eb !important;
      stroke: #d1d5db !important;
    }
    .pdf-export-container .el-progress-bar__inner,
    .pdf-export-container .el-progress-dashboard__path,
    .pdf-export-container .el-progress-circle__path {
      background: #9ca3af !important;
      stroke: #9ca3af !important;
    }
    .pdf-export-container .el-checkbox__inner {
      border-color: #9ca3af !important;
      background: #ffffff !important;
    }
    /* 移除装饰性渐变 */
    .pdf-export-container .report-cover {
      page-break-inside: avoid;
    }
    .pdf-export-container .report-highlight-grid,
    .pdf-export-container .resource-summary-strip {
      display: grid !important;
      gap: 12px !important;
    }
  `
  exportContainer.appendChild(styleEl)

  // 7. 将克隆内容添加到导出容器
  exportContainer.appendChild(reportClone)
  document.body.appendChild(exportContainer)

  // 8. 等待渲染完成
  await new Promise(resolve => setTimeout(resolve, 500))

  try {
    await exportResumePreviewToPdf(exportContainer, {
      fileName: `${report.value.target_position || 'career-report'}.pdf`,
      margin: 8,
    })
    pushAssistantNote('PDF 导出成功', 'success')
  } catch (error) {
    console.error(error)
    ElMessage.error('PDF 导出失败')
    pushAssistantNote('PDF 导出失败，请检查页面内容是否已渲染完成', 'danger')
  } finally {
    // 9. 清理临时元素
    if (exportContainer.parentNode) {
      document.body.removeChild(exportContainer)
    }
  }
}

async function exportWord() {
  try {
    await exportGrowthPlanToWord(buildSubmitData({ preserveLineBreaks: true }), {
      fileName: `${report.value.target_position || 'career-report'}.docx`,
    })
    pushAssistantNote('Word 导出成功', 'success')
  } catch (error) {
    console.error(error)
    ElMessage.error('Word 导出失败')
  }
}

onMounted(() => {
  buildJobOptions()

  const routeJobId = getRouteJobIdString()
  activeView.value = routeJobId ? 'report' : 'jobs'
  if (routeJobId) {
    syncRouteJobContext(routeJobId)

    // 强制使用 mock 数据模式下的最新模拟数据
    if (ENABLE_MOCK) {
      const mockData = getMockCareerReportByJobId(routeJobId)
      if (mockData && hasPersistedReportData(mockData)) {
        console.log('[CReport] 使用 Mock 数据:', routeJobId, '->', mockData.target_position)
        syncReport(mockData)
        persistReport(mockData)
        markReportSynced('mock')
        pushAssistantNote(`已加载 ${mockData.target_position} 的示例报告数据`, 'success')
      } else {
        console.warn('[CReport] Mock 数据无效或缺失:', routeJobId)
        void bootstrapReportPlan()
      }
    } else {
      // 非 mock 模式：优先使用存储数据
      const storedReport = reportStore.getReportByJob(routeJobId)
      if (storedReport && hasPersistedReportData(storedReport)) {
        syncReport(storedReport)
        markReportSynced('store')
      } else {
        void bootstrapReportPlan()
      }
    }
    return
  }

  if (reportStore.currentJobId) {
    void router.replace({
      name: 'report',
      query: { ...route.query, jobId: reportStore.currentJobId },
    })
  }
})
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
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 55%, #60a5fa 100%);
  color: #fff;
  box-shadow: 0 18px 40px rgba(37, 99, 235, 0.2);
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
  grid-template-columns: repeat(3, minmax(0, 1fr));
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

.job-picker-panel {
  padding: 24px 26px;
  margin-bottom: 22px;
  border-radius: var(--radius-xl);
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: var(--card-shadow);
}

.job-picker-panel--compact {
  padding: 18px 20px;
}

.job-picker-panel--compact .job-picker-head {
  margin-bottom: 14px;
}

.job-picker-panel--compact .job-picker-list {
  gap: 10px;
}

.job-picker-panel--compact .job-picker-row {
  padding: 16px 18px;
}

.job-picker-head {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.job-picker-head h2 {
  margin: 0;
  color: #0f172a;
  font-size: 24px;
}

.job-picker-desc {
  margin: 10px 0 0;
  max-width: 720px;
  color: #64748b;
  line-height: 1.8;
}

.job-picker-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.job-picker-list {
  display: grid;
  gap: 14px;
}

.job-picker-list--nested {
  margin-top: 12px;
}

.job-picker-collapse :deep(.el-collapse) {
  border-top: none;
  border-bottom: none;
}

.job-picker-collapse :deep(.el-collapse-item__header) {
  height: auto;
  min-height: 48px;
  padding: 0 2px;
  font-size: 15px;
  font-weight: 700;
  color: #173a5d;
  border-bottom: none;
}

.job-picker-collapse :deep(.el-collapse-item__wrap) {
  border-bottom: none;
  background: transparent;
}

.job-picker-collapse :deep(.el-collapse-item__content) {
  padding-bottom: 0;
}

.job-picker-row {
  display: grid;
  grid-template-columns: 54px minmax(0, 1fr) auto;
  gap: 18px;
  align-items: center;
  padding: 18px 20px;
  border-radius: 20px;
  background: linear-gradient(135deg, #fbfdff 0%, #f7fbff 100%);
  border: 1px solid rgba(148, 163, 184, 0.15);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
  transition: var(--transition-smooth);
}

.job-picker-row:hover {
  transform: translateY(-2px);
  box-shadow: var(--card-shadow-hover);
  border-color: rgba(59, 130, 246, 0.18);
}

.job-picker-row.is-active {
  border-color: rgba(37, 99, 235, 0.32);
  background: linear-gradient(135deg, #eff6ff 0%, #f8fbff 100%);
  box-shadow: 0 14px 32px rgba(37, 99, 235, 0.12);
}

.job-picker-index {
  display: flex;
  align-items: center;
  justify-content: center;
}

.job-picker-index span {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
}

.job-picker-main {
  min-width: 0;
}

.job-picker-card-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.job-picker-card-head h3 {
  margin: 0;
  color: #0f172a;
  font-size: 18px;
}

.job-picker-card-head p {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 13px;
}

.job-picker-tags,
.job-picker-meta,
.job-picker-card-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.job-picker-summary {
  margin: 10px 0 0;
  color: #475569;
  line-height: 1.75;
  font-size: 14px;
}

.job-picker-meta {
  margin-top: 12px;
  color: #64748b;
  font-size: 13px;
}

.job-picker-preview {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.job-picker-preview-item {
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.job-picker-preview-item span {
  display: block;
  margin-bottom: 6px;
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.job-picker-preview-item p {
  margin: 0;
  color: #475569;
  line-height: 1.7;
  font-size: 13px;
}

.job-switcher-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  margin-bottom: 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(148, 163, 184, 0.14);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
}

.job-switcher-bar__main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.job-switcher-bar__label {
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.job-switcher-bar__main strong {
  color: #173a5d;
  font-size: 16px;
}

.job-switcher-bar__hint {
  color: #64748b;
  font-size: 13px;
}

.job-switcher-bar__actions {
  display: flex;
  gap: 10px;
}

.job-picker-actions-col {
  display: flex;
  justify-content: flex-end;
}

.job-picker-card-actions {
  justify-content: flex-end;
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

.report-cover {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.8fr);
  gap: 18px;
  padding: 26px;
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 251, 255, 0.96) 100%);
  border: 1px solid rgba(148, 163, 184, 0.16);
  color: #0f172a;
  box-shadow: var(--card-shadow);
}

.report-cover h1 {
  margin: 0;
  font-size: 34px;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: #0f172a;
}

.report-cover .section-group-kicker {
  color: #2563eb;
}

.report-cover-desc {
  margin: 14px 0 0;
  max-width: 720px;
  color: #475569;
  line-height: 1.8;
}

.report-cover-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 22px;
}

.report-cover-meta-item,
.report-cover-panel {
  padding: 16px 18px;
  border-radius: 18px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
  border: 1px solid rgba(148, 163, 184, 0.14);
}

.report-cover-meta-item {
  display: grid;
  gap: 6px;
}

.report-cover-meta-item strong,
.report-cover-panel__label {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #64748b;
}

.report-cover-meta-item span,
.report-cover-panel strong {
  font-size: 16px;
  font-weight: 700;
  color: #173a5d;
}

.report-cover-side {
  display: grid;
  gap: 14px;
}

.report-cover-panel {
  display: grid;
  gap: 10px;
  align-content: start;
}

.report-cover-panel p {
  margin: 0;
  color: #475569;
  line-height: 1.7;
}

.report-cover-panel--accent {
  background: linear-gradient(180deg, #f3f8ff 0%, #ffffff 100%);
  border-color: rgba(59, 130, 246, 0.16);
}

.report-highlight-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.report-highlight-card {
  padding: 18px 18px 20px;
  border-radius: 18px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
  border: 1px solid rgba(148, 163, 184, 0.14);
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.05);
}

.report-highlight-card span {
  display: block;
  margin-bottom: 10px;
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.report-highlight-card strong {
  display: block;
  margin-bottom: 8px;
  color: #0f172a;
  font-size: 16px;
}

.report-highlight-card p {
  margin: 0;
  color: #475569;
  line-height: 1.75;
  font-size: 13px;
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

.content-card--full {
  grid-column: 1 / -1;
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

.goal-box--soft {
  margin-top: 0;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
  border-color: rgba(148, 163, 184, 0.16);
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

.action-summary-card {
  margin-top: 18px;
  padding: 16px 18px;
  border-radius: 16px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
  border: 1px solid rgba(59, 130, 246, 0.1);
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

.resource-summary-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
}

.resource-summary-chip {
  padding: 14px 16px;
  border-radius: 16px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.resource-summary-chip span {
  display: block;
  margin-bottom: 8px;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
}

.resource-summary-chip strong {
  color: #173a5d;
  font-size: 15px;
  line-height: 1.6;
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
  .report-cover,
  .report-highlight-grid,
  .resource-summary-strip {
    grid-template-columns: 1fr;
  }

  .job-picker-preview {
    grid-template-columns: 1fr;
  }

  .job-picker-row {
    grid-template-columns: 48px minmax(0, 1fr);
  }

  .job-picker-actions-col {
    grid-column: 2;
    justify-content: flex-start;
  }

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
  .report-cover-meta {
    grid-template-columns: 1fr;
  }

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
  .job-switcher-bar {
    flex-direction: column;
    align-items: flex-start;
  }

  .job-switcher-bar__actions {
    width: 100%;
  }

  .job-switcher-bar__actions :deep(.el-button) {
    width: 100%;
  }

  .job-picker-preview-item {
    padding: 10px 12px;
  }

  .job-picker-panel {
    padding: 18px;
  }

  .job-picker-head,
  .job-picker-card-head {
    flex-direction: column;
  }

  .job-picker-row {
    grid-template-columns: 1fr;
    padding: 16px;
    gap: 14px;
  }

  .job-picker-index {
    justify-content: flex-start;
  }

  .job-picker-actions-col,
  .job-picker-card-actions {
    justify-content: stretch;
  }

  .job-picker-card-actions :deep(.el-button) {
    flex: 1;
  }

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

  .report-cover {
    padding: 20px;
    border-radius: 20px;
  }

  .report-cover h1 {
    font-size: 24px;
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
  .resource-card,
  .report-cover,
  .report-cover-panel,
  .report-highlight-card {
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

/* ===== AI Processing Overlay ===== */
.ai-processing-overlay {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(241, 247, 255, 0.82);
  backdrop-filter: blur(10px);
}

.ai-processing-card {
  width: min(100%, 520px);
  padding: 32px 32px 28px;
  border-radius: 28px;
  text-align: center;
  background:
    radial-gradient(circle at top left, rgba(139, 92, 246, 0.2), transparent 32%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(246, 250, 255, 0.98));
  border: 1px solid rgba(191, 219, 254, 0.85);
  box-shadow: 0 24px 60px rgba(139, 92, 246, 0.14);
}

.ai-processing-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  padding: 0 14px;
  margin-bottom: 16px;
  border-radius: 999px;
  background: rgba(139, 92, 246, 0.12);
  color: #7c3aed;
  font-size: 13px;
  font-weight: 600;
}

.ai-processing-icon {
  margin-bottom: 18px;
  color: #8b5cf6;
  animation: aiProcessingPulse 2s ease-in-out infinite;
}

.ai-processing-card h3 {
  margin: 0 0 12px;
  color: #173a5d;
  font-size: 30px;
  font-weight: 800;
}

.ai-processing-card p {
  margin: 0 auto;
  max-width: 420px;
  color: #5f738b;
  font-size: 15px;
  line-height: 1.8;
}

.ai-processing-progress {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin: 22px 0 16px;
}

.ai-processing-progress .progress-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #8b5cf6;
  animation: aiProcessingBounce 1.4s ease-in-out infinite both;
}

.ai-processing-progress .progress-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.ai-processing-progress .progress-dot:nth-child(2) {
  animation-delay: -0.16s;
}

.ai-processing-tip {
  color: #7b91a7;
  font-size: 13px;
  line-height: 1.7;
}

@keyframes aiProcessingPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

@keyframes aiProcessingBounce {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.ai-processing-fade-enter-active,
.ai-processing-fade-leave-active {
  transition: opacity 0.2s ease;
}

.ai-processing-fade-enter-from,
.ai-processing-fade-leave-to {
  opacity: 0;
}
</style>
