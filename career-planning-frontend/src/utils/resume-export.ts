import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'
import { saveAs } from 'file-saver'
import {
  AlignmentType,
  Document,
  HeadingLevel,
  Packer,
  Paragraph,
  TextRun
} from 'docx'

import type { JsonResume } from '@/types/json-resume'

export interface ManualResumeEditorData {
  name: string
  title: string
  phone: string
  email: string
  location: string
  education: string
  school: string
  summary: string
  skills: string
  awards: string
  languages: string
  portfolio: string
  work: Array<{
    company: string
    position: string
    date: string
    desc: string
  }>
  projects: Array<{
    name: string
    tech: string
    date: string
    desc: string
  }>
}

/** 导出 PDF 的配置。 */
export interface ResumePdfExportOptions {
  /** 导出文件名。 */
  fileName?: string
  /** 内容区域边距。 */
  margin?: number
  /** 画布缩放倍率。 */
  scale?: number
  preferWhitespaceBreaks?: boolean
}

/** 导出 Word 的配置。 */
export interface ResumeWordExportOptions {
  /** 导出文件名。 */
  fileName?: string
}

type HeadingLevelValue = (typeof HeadingLevel)[keyof typeof HeadingLevel]

/** 将任意值标准化为文本。 */
function asText(value?: string | null): string {
  return typeof value === 'string' ? value.trim() : ''
}

/** 清洗下载文件名，避免非法字符影响浏览器保存。 */
function sanitizeDownloadFileName(fileName: string, fallback: string): string {
  const normalized = asText(fileName)
    .replace(/[<>:"/\\|?*\u0000-\u001f]/g, '-')
    .replace(/\s+/g, ' ')
    .trim()

  return normalized || fallback
}

/** 将数组转为段落列表。 */
function toBulletParagraphs(items?: string[]): Paragraph[] {
  return (items ?? [])
    .filter(item => asText(item))
    .map(item => new Paragraph({
      text: item,
      bullet: {
        level: 0
      },
      spacing: {
        after: 120
      }
    }))
}

/** 导出页面中的简历预览为 PDF。 */
export async function exportResumePreviewToPdf(
  element: HTMLElement,
  options?: ResumePdfExportOptions
): Promise<void> {
  const canvas = await html2canvas(element, {
    scale: options?.scale ?? 2,
    useCORS: true,
    backgroundColor: '#ffffff'
  })

  const pdf = new jsPDF('p', 'mm', 'a4')
  const pageWidth = pdf.internal.pageSize.getWidth()
  const pageHeight = pdf.internal.pageSize.getHeight()
  const margin = options?.margin ?? 10
  const targetWidth = pageWidth - margin * 2
  const contentPageHeight = pageHeight - margin * 2
  const pagePixelHeight = Math.floor((contentPageHeight * canvas.width) / targetWidth)
  const preferWhitespaceBreaks = options?.preferWhitespaceBreaks !== false
  const context = canvas.getContext('2d')

  const isMostlyBlankRow = (row: number): boolean => {
    if (!context || row < 0 || row >= canvas.height) return false

    const data = context.getImageData(0, row, canvas.width, 1).data
    let blankCount = 0
    let sampleCount = 0

    for (let x = 0; x < canvas.width; x += 12) {
      const index = x * 4
      const r = data[index] ?? 255
      const g = data[index + 1] ?? 255
      const b = data[index + 2] ?? 255
      const a = data[index + 3] ?? 255
      sampleCount += 1
      if (a < 10 || (r > 245 && g > 245 && b > 245)) {
        blankCount += 1
      }
    }

    return sampleCount > 0 && blankCount / sampleCount >= 0.985
  }

  const findBestPageEnd = (suggestedEnd: number, pageStart: number): number => {
    if (!preferWhitespaceBreaks) return suggestedEnd

    const searchRange = Math.min(160, Math.floor(pagePixelHeight * 0.12))
    for (let offset = 0; offset <= searchRange; offset += 4) {
      const down = suggestedEnd + offset
      if (down < canvas.height && down > pageStart + 80 && isMostlyBlankRow(down)) {
        return down
      }

      const up = suggestedEnd - offset
      if (up > pageStart + 80 && isMostlyBlankRow(up)) {
        return up
      }
    }

    return suggestedEnd
  }

  let pageStartY = 0
  let isFirstPage = true

  while (pageStartY < canvas.height) {
    const remainingHeight = canvas.height - pageStartY
    let sliceHeight = Math.min(pagePixelHeight, remainingHeight)

    if (pageStartY + sliceHeight < canvas.height) {
      const suggestedEnd = pageStartY + sliceHeight
      const adjustedEnd = findBestPageEnd(suggestedEnd, pageStartY)
      sliceHeight = Math.max(adjustedEnd - pageStartY, Math.min(260, remainingHeight))
    }

    const pageCanvas = document.createElement('canvas')
    pageCanvas.width = canvas.width
    pageCanvas.height = sliceHeight
    const pageContext = pageCanvas.getContext('2d')

    if (!pageContext) {
      throw new Error('Failed to create PDF page canvas context')
    }

    pageContext.fillStyle = '#ffffff'
    pageContext.fillRect(0, 0, pageCanvas.width, pageCanvas.height)
    pageContext.drawImage(
      canvas,
      0,
      pageStartY,
      canvas.width,
      sliceHeight,
      0,
      0,
      canvas.width,
      sliceHeight
    )

    const imageData = pageCanvas.toDataURL('image/png')
    const renderHeight = (sliceHeight * targetWidth) / canvas.width

    if (!isFirstPage) {
      pdf.addPage()
    }

    pdf.addImage(imageData, 'PNG', margin, margin, targetWidth, renderHeight)

    pageStartY += sliceHeight
    isFirstPage = false
  }

  pdf.save(options?.fileName ?? 'resume.pdf')
}

/** 导出 JSON Resume 为 JSON 文件。 */
export function exportJsonResumeFile(resume: JsonResume, fileName: string = 'resume.json'): void {
  const blob = new Blob([JSON.stringify(resume, null, 2)], {
    type: 'application/json;charset=utf-8'
  })
  saveAs(blob, fileName)
}

/** 导出 JSON Resume 为 Word 文档。 */
export async function exportJsonResumeToWord(
  resume: JsonResume,
  options?: ResumeWordExportOptions
): Promise<void> {
  const children: Paragraph[] = []
  const basics = resume.basics

  children.push(
    new Paragraph({
      text: basics.name,
      heading: HeadingLevel.TITLE,
      alignment: AlignmentType.CENTER,
      spacing: {
        after: 160
      }
    })
  )

  const metaLine = [
    basics.label,
    basics.email,
    basics.phone,
    basics.location?.city,
    basics.location?.region
  ].filter(item => asText(item)).join(' | ')

  if (metaLine) {
    children.push(new Paragraph({
      text: metaLine,
      alignment: AlignmentType.CENTER,
      spacing: {
        after: 240
      }
    }))
  }

  if (asText(basics.summary)) {
    children.push(
      new Paragraph({
        text: '个人简介',
        heading: HeadingLevel.HEADING_1
      }),
      new Paragraph({
        text: basics.summary
      })
    )
  }

  if (resume.work?.length) {
    children.push(new Paragraph({
      text: '工作经历',
      heading: HeadingLevel.HEADING_1
    }))

    for (const item of resume.work) {
      children.push(
        new Paragraph({
          children: [
            new TextRun({
              text: item.name,
              bold: true
            }),
            new TextRun({
              text: item.position ? `  ${item.position}` : ''
            })
          ],
          spacing: {
            before: 120
          }
        }),
        new Paragraph({
          text: [item.startDate, item.endDate || '至今'].filter(Boolean).join(' - ')
        })
      )

      if (asText(item.summary)) {
        children.push(new Paragraph({ text: item.summary }))
      }

      children.push(...toBulletParagraphs(item.highlights))
    }
  }

  if (resume.projects?.length) {
    children.push(new Paragraph({
      text: '项目经历',
      heading: HeadingLevel.HEADING_1
    }))

    for (const item of resume.projects) {
      children.push(
        new Paragraph({
          children: [
            new TextRun({
              text: item.name,
              bold: true
            })
          ],
          spacing: {
            before: 120
          }
        })
      )

      const dateLine = [item.startDate, item.endDate].filter(Boolean).join(' - ')
      if (dateLine) {
        children.push(new Paragraph({ text: dateLine }))
      }

      if (asText(item.description)) {
        children.push(new Paragraph({ text: item.description }))
      }

      children.push(...toBulletParagraphs(item.highlights))
    }
  }

  if (resume.education?.length) {
    children.push(new Paragraph({
      text: '教育经历',
      heading: HeadingLevel.HEADING_1
    }))

    for (const item of resume.education) {
      children.push(
        new Paragraph({
          children: [
            new TextRun({
              text: item.institution,
              bold: true
            }),
            new TextRun({
              text: item.area ? `  ${item.area}` : ''
            }),
            new TextRun({
              text: item.studyType ? `  ${item.studyType}` : ''
            })
          ],
          spacing: {
            before: 120
          }
        })
      )

      const dateLine = [item.startDate, item.endDate].filter(Boolean).join(' - ')
      if (dateLine) {
        children.push(new Paragraph({ text: dateLine }))
      }
    }
  }

  if (resume.skills?.length) {
    children.push(new Paragraph({
      text: '技能',
      heading: HeadingLevel.HEADING_1
    }))

    for (const item of resume.skills) {
      children.push(new Paragraph({
        text: `${item.name}: ${item.keywords.join(', ')}`
      }))
    }
  }

  const doc = new Document({
    sections: [
      {
        children
      }
    ]
  })

  const blob = await Packer.toBlob(doc)
  saveAs(blob, options?.fileName ?? 'resume.docx')
}

export async function exportManualResumeToWord(
  resume: ManualResumeEditorData,
  options?: ResumeWordExportOptions
): Promise<void> {
  const children: Paragraph[] = []

  children.push(
    new Paragraph({
      text: asText(resume.name) || '简历',
      heading: HeadingLevel.TITLE,
      alignment: AlignmentType.CENTER,
      spacing: {
        after: 160
      }
    })
  )

  const metaLine = [
    asText(resume.title),
    asText(resume.phone),
    asText(resume.email),
    asText(resume.location)
  ].filter(Boolean).join(' | ')

  if (metaLine) {
    children.push(new Paragraph({
      text: metaLine,
      alignment: AlignmentType.CENTER,
      spacing: {
        after: 240
      }
    }))
  }

  if (asText(resume.summary)) {
    children.push(
      new Paragraph({ text: '个人简介', heading: HeadingLevel.HEADING_1 }),
      new Paragraph({ text: resume.summary })
    )
  }

  if (asText(resume.education) || asText(resume.school)) {
    children.push(
      new Paragraph({ text: '教育背景', heading: HeadingLevel.HEADING_1 }),
      new Paragraph({
        children: [
          new TextRun({ text: asText(resume.school), bold: true }),
          new TextRun({ text: asText(resume.education) ? `  ${asText(resume.education)}` : '' })
        ]
      })
    )
  }

  const workItems = resume.work.filter(item =>
    [item.company, item.position, item.date, item.desc].some(value => asText(value))
  )

  if (workItems.length) {
    children.push(new Paragraph({ text: '工作经历', heading: HeadingLevel.HEADING_1 }))

    for (const item of workItems) {
      children.push(
        new Paragraph({
          children: [
            new TextRun({ text: asText(item.company), bold: true }),
            new TextRun({ text: asText(item.position) ? `  ${asText(item.position)}` : '' })
          ],
          spacing: {
            before: 120
          }
        })
      )

      if (asText(item.date)) {
        children.push(new Paragraph({ text: item.date }))
      }

      const lines = item.desc.split('\n').map(line => line.trim()).filter(Boolean)
      if (lines.length <= 1 && asText(item.desc)) {
        children.push(new Paragraph({ text: item.desc }))
      } else {
        children.push(...toBulletParagraphs(lines))
      }
    }
  }

  const projectItems = resume.projects.filter(item =>
    [item.name, item.tech, item.date, item.desc].some(value => asText(value))
  )

  if (projectItems.length) {
    children.push(new Paragraph({ text: '项目经验', heading: HeadingLevel.HEADING_1 }))

    for (const item of projectItems) {
      children.push(
        new Paragraph({
          children: [
            new TextRun({ text: asText(item.name), bold: true }),
            new TextRun({ text: asText(item.tech) ? `  ${asText(item.tech)}` : '' })
          ],
          spacing: {
            before: 120
          }
        })
      )

      if (asText(item.date)) {
        children.push(new Paragraph({ text: item.date }))
      }

      const lines = item.desc.split('\n').map(line => line.trim()).filter(Boolean)
      if (lines.length <= 1 && asText(item.desc)) {
        children.push(new Paragraph({ text: item.desc }))
      } else {
        children.push(...toBulletParagraphs(lines))
      }
    }
  }

  const skillItems = asText(resume.skills)
    .split(/[，,]/)
    .map(item => item.trim())
    .filter(Boolean)

  if (skillItems.length) {
    children.push(
      new Paragraph({ text: '专业技能', heading: HeadingLevel.HEADING_1 }),
      new Paragraph({ text: skillItems.join('、') })
    )
  }

  const awardItems = resume.awards.split('\n').map(item => item.trim()).filter(Boolean)
  if (awardItems.length) {
    children.push(
      new Paragraph({ text: '荣誉证书', heading: HeadingLevel.HEADING_1 }),
      ...toBulletParagraphs(awardItems)
    )
  }

  const otherItems = [
    ...resume.languages.split('\n').map(item => item.trim()).filter(Boolean),
    asText(resume.portfolio)
  ].filter(Boolean)

  if (otherItems.length) {
    children.push(
      new Paragraph({ text: '其他信息', heading: HeadingLevel.HEADING_1 }),
      ...toBulletParagraphs(otherItems)
    )
  }

  const doc = new Document({
    sections: [
      {
        children
      }
    ]
  })

  const blob = await Packer.toBlob(doc)
  saveAs(blob, options?.fileName ?? 'resume.docx')
}

export interface GrowthPlanWordExportData {
  student_summary: string
  target_position: string
  current_gap: string
  short_term_plan: {
    duration: string
    goal: string
    focus_areas: string[]
    milestones: Array<{
      milestone_name: string
      target_date: string
      key_results: string[]
      tasks: Array<{
        task_name: string
        description: string
        priority: string
        estimated_time: string
        skill_target: string
        success_criteria: string
      }>
    }>
    quick_wins: string[]
  }
  mid_term_plan: {
    duration: string
    goal: string
    skill_roadmap: string[]
    milestones: Array<{
      milestone_name: string
      target_date: string
      key_results: string[]
      tasks: Array<{
        task_name: string
        description: string
        priority: string
        estimated_time: string
        skill_target: string
        success_criteria: string
      }>
    }>
    career_progression: string
    recommended_internships: Array<{
      job_title: string
      company_name: string
      city: string
      salary: string
      job_type: string
      reason: string
      tech_stack?: string
      content?: string
    }>
  }
  action_checklist: string[]
  tips: string[]
}

export async function exportGrowthPlanToWord(
  plan: GrowthPlanWordExportData,
  options?: ResumeWordExportOptions
): Promise<void> {
  const children: Paragraph[] = []
  const reportDate = new Date().toLocaleDateString('zh-CN')

  const pushHeading = (text: string, level: HeadingLevelValue = HeadingLevel.HEADING_1) => {
    children.push(
      new Paragraph({
        text,
        heading: level,
        spacing: {
          before: 240,
          after: 120
        }
      })
    )
  }

  const pushCaption = (text?: string) => {
    const value = asText(text)
    if (!value) return

    children.push(
      new Paragraph({
        text: value,
        alignment: AlignmentType.CENTER,
        spacing: {
          after: 120
        }
      })
    )
  }

  const pushBody = (text?: string) => {
    const paragraphs = asText(text)
      .split(/\r?\n+/)
      .map(item => item.trim())
      .filter(Boolean)

    if (!paragraphs.length) return

    children.push(
      ...paragraphs.map(item => new Paragraph({
        text: item,
        spacing: {
          after: 120
        }
      }))
    )
  }

  const pushLabelValue = (label: string, value?: string) => {
    const normalized = asText(value)
    if (!normalized) return

    children.push(
      new Paragraph({
        children: [
          new TextRun({
            text: `${label}：`,
            bold: true
          }),
          new TextRun({
            text: normalized
          })
        ],
        spacing: {
          after: 120
        }
      })
    )
  }

  const pushSummaryBlock = (title: string, content?: string) => {
    const normalized = asText(content)
    if (!normalized) return
    children.push(
      new Paragraph({
        text: title,
        heading: HeadingLevel.HEADING_2
      })
    )
    pushBody(normalized)
  }

  const pushMilestoneSection = (
    title: string,
    milestones: GrowthPlanWordExportData['short_term_plan']['milestones']
  ) => {
    if (!milestones.length) return

    children.push(
      new Paragraph({
        text: title,
        heading: HeadingLevel.HEADING_2
      })
    )

    for (const [index, milestone] of milestones.entries()) {
      children.push(
        new Paragraph({
          children: [
            new TextRun({ text: `${index + 1}. ${milestone.milestone_name || '未命名里程碑'}`, bold: true }),
            new TextRun({ text: milestone.target_date ? `  ${milestone.target_date}` : '' })
          ],
          spacing: {
            before: 140,
            after: 120
          }
        })
      )

      if (milestone.key_results.length) {
        children.push(
          new Paragraph({
            text: '关键成果',
            heading: HeadingLevel.HEADING_3
          }),
          ...toBulletParagraphs(milestone.key_results)
        )
      }

      if (!milestone.tasks.length) continue

      children.push(
        new Paragraph({
          text: '任务拆解',
          heading: HeadingLevel.HEADING_3
        })
      )

      for (const task of milestone.tasks) {
        children.push(
          new Paragraph({
            children: [
              new TextRun({ text: task.task_name || '未命名任务', bold: true }),
              new TextRun({ text: task.priority ? `  [${task.priority}优先级]` : '' })
            ],
            spacing: {
              before: 120,
              after: 120
            }
          })
        )
        pushBody(task.description)
        pushLabelValue('预计时间', task.estimated_time)
        pushLabelValue('目标能力', task.skill_target)
        pushLabelValue('成功标准', task.success_criteria)
      }
    }
  }

  children.push(
    new Paragraph({
      text: asText(plan.target_position) || '\u751f\u6daf\u6210\u957f\u62a5\u544a',
      heading: HeadingLevel.TITLE,
      alignment: AlignmentType.CENTER,
      spacing: {
        after: 160
      }
    }),
    new Paragraph({
      text: '\u804c\u4e1a\u76ee\u6807 / \u8def\u5f84\u89c4\u5212 / \u884c\u52a8\u8ba1\u5212',
      alignment: AlignmentType.CENTER,
      spacing: {
        after: 280
      }
    })
  )

  pushCaption(`生成日期：${reportDate}`)
  pushCaption(`短期周期：${asText(plan.short_term_plan.duration) || '待补充'}  |  中期周期：${asText(plan.mid_term_plan.duration) || '待补充'}`)

  pushHeading('\u6267\u884c\u6458\u8981')
  pushBody(plan.target_position)
  pushSummaryBlock('\u5b66\u751f\u753b\u50cf\u6458\u8981', plan.student_summary)
  pushSummaryBlock('\u80fd\u529b\u5dee\u8ddd\u5206\u6790', plan.current_gap)

  if (plan.action_checklist.length) {
    children.push(
      new Paragraph({
        text: '\u5f53\u524d\u5efa\u8bae\u4f18\u5148\u6267\u884c',
        heading: HeadingLevel.HEADING_2
      }),
      ...toBulletParagraphs(plan.action_checklist.slice(0, 3))
    )
  }

  pushHeading('\u77ed\u671f\u884c\u52a8\u8ba1\u5212')
  pushLabelValue('\u5468\u671f', plan.short_term_plan.duration)
  pushBody(plan.short_term_plan.goal)

  if (plan.short_term_plan.focus_areas.length) {
    children.push(
      new Paragraph({
        text: '\u91cd\u70b9\u65b9\u5411',
        heading: HeadingLevel.HEADING_2
      }),
      ...toBulletParagraphs(plan.short_term_plan.focus_areas)
    )
  }

  if (plan.short_term_plan.quick_wins.length) {
    children.push(
      new Paragraph({
        text: '\u77ed\u671f\u5feb\u901f\u52a8\u4f5c',
        heading: HeadingLevel.HEADING_2
      }),
      ...toBulletParagraphs(plan.short_term_plan.quick_wins)
    )
  }

  pushMilestoneSection('\u77ed\u671f\u91cc\u7a0b\u7891', plan.short_term_plan.milestones)

  pushHeading('\u4e2d\u671f\u8def\u5f84\u89c4\u5212')
  pushLabelValue('\u5468\u671f', plan.mid_term_plan.duration)
  pushBody(plan.mid_term_plan.goal)

  if (plan.mid_term_plan.skill_roadmap.length) {
    children.push(
      new Paragraph({
        text: '\u6280\u80fd\u8def\u7ebf',
        heading: HeadingLevel.HEADING_2
      }),
      ...toBulletParagraphs(plan.mid_term_plan.skill_roadmap)
    )
  }

  pushMilestoneSection('\u4e2d\u671f\u91cc\u7a0b\u7891', plan.mid_term_plan.milestones)

  pushHeading('\u804c\u4e1a\u53d1\u5c55\u9884\u671f')
  pushBody(plan.mid_term_plan.career_progression)

  if (plan.mid_term_plan.recommended_internships.length) {
    children.push(
      new Paragraph({
        text: '\u63a8\u8350\u5b9e\u4e60\u5c97\u4f4d',
        heading: HeadingLevel.HEADING_2
      })
    )

    for (const [index, item] of plan.mid_term_plan.recommended_internships.entries()) {
      children.push(
        new Paragraph({
          children: [
            new TextRun({ text: `${index + 1}. ${item.job_title || '未命名岗位'}`, bold: true }),
            new TextRun({ text: item.company_name ? `  ${item.company_name}` : '' })
          ],
          spacing: {
            before: 120
          }
        })
      )

      pushLabelValue('\u57ce\u5e02/\u85aa\u8d44/\u7c7b\u578b', [asText(item.city), asText(item.salary), asText(item.job_type)].filter(Boolean).join(' | '))
      pushLabelValue('\u63a8\u8350\u7406\u7531', item.reason)
      pushLabelValue('\u6280\u672f\u6808', item.tech_stack)
      pushBody(item.content)
    }
  }

  if (plan.action_checklist.length) {
    children.push(
      new Paragraph({
        text: '\u884c\u52a8\u6e05\u5355',
        heading: HeadingLevel.HEADING_1
      }),
      ...toBulletParagraphs(plan.action_checklist)
    )
  }

  if (plan.tips.length) {
    children.push(
      new Paragraph({
        text: '\u5b66\u4e60\u5efa\u8bae',
        heading: HeadingLevel.HEADING_1
      }),
      ...toBulletParagraphs(plan.tips)
    )
  }

  const doc = new Document({
    sections: [
      {
        children
      }
    ]
  })

  const blob = await Packer.toBlob(doc)
  saveAs(blob, sanitizeDownloadFileName(options?.fileName ?? 'growth-plan.docx', 'growth-plan.docx'))
}
