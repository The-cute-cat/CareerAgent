import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'
import { saveAs } from 'file-saver'
import {
  AlignmentType,
  BorderStyle,
  Document,
  HeadingLevel,
  ImageRun,
  Packer,
  Paragraph,
  TextRun,
  Footer as DocxFooter,
  Header as DocxHeader,
  PageNumber,
} from 'docx'

import type { JsonResume } from '@/types/json-resume'

export interface ManualResumeEditorData {
  avatar?: string
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

async function resolveImageToUint8Array(image?: string | null): Promise<Uint8Array | null> {
  const value = asText(image)
  if (!value) return null

  if (value.startsWith('data:image/')) {
    const payload = value.split(',', 2)[1]
    if (!payload) return null

    try {
      const binary = atob(payload)
      return Uint8Array.from(binary, char => char.charCodeAt(0))
    } catch {
      return null
    }
  }

  try {
    const response = await fetch(value)
    if (!response.ok) return null
    const buffer = await response.arrayBuffer()
    return new Uint8Array(buffer)
  } catch {
    return null
  }
}

function createSectionHeading(text: string): Paragraph {
  return new Paragraph({
    text,
    heading: HeadingLevel.HEADING_1,
    spacing: {
      before: 300,
      after: 140
    },
    border: {
      bottom: {
        style: BorderStyle.SINGLE,
        color: 'D7E3F6',
        size: 6
      }
    }
  })
}

function createBodyParagraph(text: string, options?: { after?: number; alignment?: AlignmentType }): Paragraph {
  return new Paragraph({
    text,
    alignment: options?.alignment,
    spacing: {
      after: options?.after ?? 120,
      line: 360
    }
  })
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
  const avatarData = await resolveImageToUint8Array(resume.avatar)
  const titleText = asText(resume.name) || 'Resume'

  if (avatarData) {
    children.push(
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: {
          after: 120
        },
        children: [
          new ImageRun({
            data: avatarData,
            transformation: {
              width: 88,
              height: 88
            }
          })
        ]
      })
    )
  }

  children.push(
    new Paragraph({
      text: titleText,
      style: 'ResumeTitle'
    })
  )

  const metaLine = [
    asText(resume.title),
    asText(resume.phone),
    asText(resume.email),
    asText(resume.location)
  ].filter(Boolean).join(' | ')

  if (metaLine) {
    children.push(createBodyParagraph(metaLine, {
      alignment: AlignmentType.CENTER,
      after: 220
    }))
  }

  if (asText(resume.summary)) {
    children.push(
      createSectionHeading('\u4e2a\u4eba\u7b80\u4ecb'),
      createBodyParagraph(asText(resume.summary))
    )
  }

  if (asText(resume.education) || asText(resume.school)) {
    children.push(
      createSectionHeading('\u6559\u80b2\u80cc\u666f'),
      new Paragraph({
        children: [
          new TextRun({ text: asText(resume.school), bold: true }),
          new TextRun({ text: asText(resume.education) ? `  ${asText(resume.education)}` : '' })
        ],
        spacing: {
          after: 120
        }
      })
    )
  }

  const workItems = resume.work.filter(item =>
    [item.company, item.position, item.date, item.desc].some(value => asText(value))
  )

  if (workItems.length) {
    children.push(createSectionHeading('\u5de5\u4f5c\u7ecf\u5386'))

    for (const item of workItems) {
      children.push(
        new Paragraph({
          children: [
            new TextRun({ text: asText(item.company), bold: true }),
            new TextRun({ text: asText(item.position) ? `  ${asText(item.position)}` : '' })
          ],
          spacing: {
            before: 100,
            after: 60
          }
        })
      )

      if (asText(item.date)) {
        children.push(createBodyParagraph(item.date, { after: 80 }))
      }

      const lines = item.desc.split(/\r?\n+/).map(line => line.trim()).filter(Boolean)
      if (lines.length <= 1 && asText(item.desc)) {
        children.push(createBodyParagraph(asText(item.desc)))
      } else {
        children.push(...toBulletParagraphs(lines))
      }
    }
  }

  const projectItems = resume.projects.filter(item =>
    [item.name, item.tech, item.date, item.desc].some(value => asText(value))
  )

  if (projectItems.length) {
    children.push(createSectionHeading('\u9879\u76ee\u7ecf\u9a8c'))

    for (const item of projectItems) {
      children.push(
        new Paragraph({
          children: [
            new TextRun({ text: asText(item.name), bold: true }),
            new TextRun({ text: asText(item.tech) ? `  ${asText(item.tech)}` : '' })
          ],
          spacing: {
            before: 100,
            after: 60
          }
        })
      )

      if (asText(item.date)) {
        children.push(createBodyParagraph(item.date, { after: 80 }))
      }

      const lines = item.desc.split(/\r?\n+/).map(line => line.trim()).filter(Boolean)
      if (lines.length <= 1 && asText(item.desc)) {
        children.push(createBodyParagraph(asText(item.desc)))
      } else {
        children.push(...toBulletParagraphs(lines))
      }
    }
  }

  const skillItems = asText(resume.skills)
    .split(/[\uFF0C,\u3001]/)
    .map(item => item.trim())
    .filter(Boolean)

  if (skillItems.length) {
    children.push(
      createSectionHeading('\u4e13\u4e1a\u6280\u80fd'),
      createBodyParagraph(skillItems.join(' / '))
    )
  }

  const awardItems = resume.awards.split(/\r?\n+/).map(item => item.trim()).filter(Boolean)
  if (awardItems.length) {
    children.push(
      createSectionHeading('\u8363\u8a89\u8bc1\u4e66'),
      ...toBulletParagraphs(awardItems)
    )
  }

  const otherItems = [
    ...resume.languages.split(/\r?\n+/).map(item => item.trim()).filter(Boolean),
    asText(resume.portfolio)
  ].filter(Boolean)

  if (otherItems.length) {
    children.push(
      createSectionHeading('\u5176\u4ed6\u4fe1\u606f'),
      ...toBulletParagraphs(otherItems)
    )
  }

  const doc = new Document({
    styles: {
      default: {
        document: {
          run: {
            font: 'Microsoft YaHei',
            size: 22,
            color: '243B53'
          },
          paragraph: {
            spacing: {
              line: 360
            }
          }
        }
      },
      paragraphStyles: [
        {
          id: 'ResumeTitle',
          name: 'ResumeTitle',
          basedOn: 'Normal',
          quickFormat: true,
          run: {
            font: 'Microsoft YaHei',
            size: 32,
            bold: true,
            color: '18304C'
          },
          paragraph: {
            alignment: AlignmentType.CENTER,
            spacing: {
              after: 80
            }
          }
        }
      ]
    },
    sections: [
      {
        properties: {
          page: {
            margin: {
              top: 900,
              right: 1000,
              bottom: 900,
              left: 1000
            }
          }
        },
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
  // ===== 设计令牌 =====
  const BRAND_PRIMARY = '1E3A8A'      // 深蓝
  const BRAND_ACCENT = '2563EB'        // 亮蓝
  const BRAND_LIGHT = 'DBEAFE'         // 浅蓝背景
  const TEXT_PRIMARY = '1F2937'        // 主文字
  const TEXT_SECONDARY = '6B7280'      // 辅助文字
  const TEXT_LABEL = '374151'          // 标签文字
  const BORDER_COLOR = 'D1D5DB'       // 边框
  const BG_HIGHLIGHT = 'EFF6FF'       // 高亮背景
  const BG_TASK = 'F9FAFB'            // 任务背景
  const HEADING_LINE = '93C5FD'       // 标题底线

  const reportDate = new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  // ===== 封面页 =====
  const coverChildren: Paragraph[] = [
    // 顶部间距
    new Paragraph({ spacing: { before: 3200 } }),
    // 品牌标识线
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 },
      children: [
        new TextRun({ text: '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', color: BRAND_ACCENT, size: 16, font: 'Microsoft YaHei' }),
      ],
    }),
    // 报告标题
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 100 },
      children: [
        new TextRun({
          text: asText(plan.target_position) || '生涯成长报告',
          bold: true,
          size: 48,
          color: BRAND_PRIMARY,
          font: 'Microsoft YaHei',
        }),
      ],
    }),
    // 副标题
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 80 },
      children: [
        new TextRun({
          text: '职业目标  ·  路径规划  ·  行动计划',
          size: 24,
          color: TEXT_SECONDARY,
          font: 'Microsoft YaHei',
        }),
      ],
    }),
    // 品牌标识线
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 600 },
      children: [
        new TextRun({ text: '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', color: BRAND_ACCENT, size: 16, font: 'Microsoft YaHei' }),
      ],
    }),
    // 报告元信息
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 120 },
      children: [
        new TextRun({ text: '生成日期：', color: TEXT_SECONDARY, size: 20, font: 'Microsoft YaHei' }),
        new TextRun({ text: reportDate, color: TEXT_PRIMARY, size: 20, font: 'Microsoft YaHei' }),
      ],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 120 },
      children: [
        new TextRun({ text: '短期周期：', color: TEXT_SECONDARY, size: 20, font: 'Microsoft YaHei' }),
        new TextRun({ text: asText(plan.short_term_plan.duration) || '待补充', color: TEXT_PRIMARY, size: 20, font: 'Microsoft YaHei' }),
        new TextRun({ text: '    中期周期：', color: TEXT_SECONDARY, size: 20, font: 'Microsoft YaHei' }),
        new TextRun({ text: asText(plan.mid_term_plan.duration) || '待补充', color: TEXT_PRIMARY, size: 20, font: 'Microsoft YaHei' }),
      ],
    }),
  ]

  // ===== 正文页 =====
  const bodyChildren: Paragraph[] = []

  // --- 辅助函数 ---
  const pushH1 = (text: string) => {
    bodyChildren.push(
      new Paragraph({
        spacing: { before: 480, after: 60 },
        border: {
          bottom: { style: BorderStyle.SINGLE, color: BRAND_ACCENT, size: 8 },
        },
        children: [
          new TextRun({ text, bold: true, size: 32, color: BRAND_PRIMARY, font: 'Microsoft YaHei' }),
        ],
      })
    )
  }

  const pushH2 = (text: string) => {
    bodyChildren.push(
      new Paragraph({
        spacing: { before: 320, after: 80 },
        border: {
          bottom: { style: BorderStyle.SINGLE, color: HEADING_LINE, size: 4 },
        },
        children: [
          new TextRun({ text, bold: true, size: 26, color: BRAND_PRIMARY, font: 'Microsoft YaHei' }),
        ],
      })
    )
  }

  const pushH3 = (text: string) => {
    bodyChildren.push(
      new Paragraph({
        spacing: { before: 200, after: 60 },
        children: [
          new TextRun({ text: '▸ ', color: BRAND_ACCENT, size: 22, font: 'Microsoft YaHei' }),
          new TextRun({ text, bold: true, size: 22, color: TEXT_PRIMARY, font: 'Microsoft YaHei' }),
        ],
      })
    )
  }

  const pushBody = (text?: string) => {
    const paragraphs = asText(text)
      .split(/\r?\n+/)
      .map(item => item.trim())
      .filter(Boolean)
    if (!paragraphs.length) return
    bodyChildren.push(
      ...paragraphs.map(item =>
        new Paragraph({
          spacing: { after: 100, line: 360 },
          indent: { firstLine: 420 },
          children: [
            new TextRun({ text: item, size: 21, color: TEXT_PRIMARY, font: 'Microsoft YaHei' }),
          ],
        })
      )
    )
  }

  const pushBodyNoIndent = (text?: string) => {
    const paragraphs = asText(text)
      .split(/\r?\n+/)
      .map(item => item.trim())
      .filter(Boolean)
    if (!paragraphs.length) return
    bodyChildren.push(
      ...paragraphs.map(item =>
        new Paragraph({
          spacing: { after: 100, line: 360 },
          children: [
            new TextRun({ text: item, size: 21, color: TEXT_PRIMARY, font: 'Microsoft YaHei' }),
          ],
        })
      )
    )
  }

  const pushLabelValue = (label: string, value?: string, inline = false) => {
    const normalized = asText(value)
    if (!normalized) return
    bodyChildren.push(
      new Paragraph({
        spacing: { after: 80, line: 360 },
        indent: inline ? { left: 420 } : undefined,
        children: [
          new TextRun({ text: `${label}：`, bold: true, size: 21, color: TEXT_LABEL, font: 'Microsoft YaHei' }),
          new TextRun({ text: normalized, size: 21, color: TEXT_PRIMARY, font: 'Microsoft YaHei' }),
        ],
      })
    )
  }

  const pushTagGroup = (label: string, items: string[]) => {
    if (!items.length) return
    bodyChildren.push(
      new Paragraph({
        spacing: { before: 80, after: 60 },
        children: [
          new TextRun({ text: `${label}：`, bold: true, size: 21, color: TEXT_LABEL, font: 'Microsoft YaHei' }),
          new TextRun({ text: items.join('  ·  '), size: 21, color: BRAND_ACCENT, font: 'Microsoft YaHei' }),
        ],
      })
    )
  }

  const pushBulletList = (items: string[]) => {
    bodyChildren.push(
      ...(items.filter(i => asText(i)).map(item =>
        new Paragraph({
          bullet: { level: 0 },
          spacing: { after: 60, line: 340 },
          children: [
            new TextRun({ text: item, size: 21, color: TEXT_PRIMARY, font: 'Microsoft YaHei' }),
          ],
        })
      ))
    )
  }

  const pushHighlightBox = (text: string) => {
    bodyChildren.push(
      new Paragraph({
        spacing: { before: 120, after: 120 },
        border: {
          left: { style: BorderStyle.SINGLE, color: BRAND_ACCENT, size: 12 },
        },
        indent: { left: 360 },
        children: [
          new TextRun({ text, size: 21, color: TEXT_PRIMARY, font: 'Microsoft YaHei', italics: true }),
        ],
      })
    )
  }

  const pushInfoRow = (label: string, value: string) => {
    bodyChildren.push(
      new Paragraph({
        spacing: { after: 60, line: 340 },
        indent: { left: 420 },
        children: [
          new TextRun({ text: `◆ `, color: BRAND_ACCENT, size: 18, font: 'Microsoft YaHei' }),
          new TextRun({ text: `${label}：`, bold: true, size: 20, color: TEXT_LABEL, font: 'Microsoft YaHei' }),
          new TextRun({ text: value, size: 20, color: TEXT_PRIMARY, font: 'Microsoft YaHei' }),
        ],
      })
    )
  }

  // --- 第一章：职业画像 ---
  pushH1('一、职业画像')

  pushH2('1.1 目标岗位')
  pushBodyNoIndent(plan.target_position)

  pushH2('1.2 学生画像摘要')
  pushBody(plan.student_summary)

  pushH2('1.3 能力差距分析')
  pushBody(plan.current_gap)

  if (plan.action_checklist.length) {
    pushH2('1.4 优先执行建议')
    pushHighlightBox('以下为当前建议优先执行的 Top 3 事项：')
    pushBulletList(plan.action_checklist.slice(0, 3))
  }

  // --- 第二章：短期行动计划 ---
  pushH1('二、短期行动计划')

  pushLabelValue('周期', plan.short_term_plan.duration)

  pushH2('2.1 阶段目标')
  pushBody(plan.short_term_plan.goal)

  if (plan.short_term_plan.focus_areas.length) {
    pushH2('2.2 重点方向')
    pushTagGroup('聚焦领域', plan.short_term_plan.focus_areas)
  }

  if (plan.short_term_plan.quick_wins.length) {
    pushH2('2.3 快速见效行动')
    pushBulletList(plan.short_term_plan.quick_wins)
  }

  // 短期里程碑
  if (plan.short_term_plan.milestones.length) {
    pushH2('2.4 短期里程碑')

    for (const [index, milestone] of plan.short_term_plan.milestones.entries()) {
      pushH3(`里程碑 ${index + 1}：${milestone.milestone_name || '未命名里程碑'}`)
      if (milestone.target_date) {
        pushInfoRow('目标日期', milestone.target_date)
      }

      if (milestone.key_results.length) {
        bodyChildren.push(
          new Paragraph({
            spacing: { before: 60, after: 40 },
            indent: { left: 420 },
            children: [
              new TextRun({ text: '关键成果', bold: true, size: 20, color: BRAND_ACCENT, font: 'Microsoft YaHei' }),
            ],
          })
        )
        pushBulletList(milestone.key_results)
      }

      if (milestone.tasks.length) {
        bodyChildren.push(
          new Paragraph({
            spacing: { before: 80, after: 40 },
            indent: { left: 420 },
            children: [
              new TextRun({ text: '任务拆解', bold: true, size: 20, color: BRAND_ACCENT, font: 'Microsoft YaHei' }),
            ],
          })
        )

        for (const task of milestone.tasks) {
          // 任务名称行
          bodyChildren.push(
            new Paragraph({
              spacing: { before: 100, after: 40 },
              indent: { left: 560 },
              border: {
                left: { style: BorderStyle.SINGLE, color: HEADING_LINE, size: 4 },
              },
              children: [
                new TextRun({ text: task.task_name || '未命名任务', bold: true, size: 21, color: TEXT_PRIMARY, font: 'Microsoft YaHei' }),
                new TextRun({
                  text: task.priority ? `  [${task.priority}优先级]` : '',
                  size: 18,
                  color: task.priority === '高' ? 'DC2626' : task.priority === '中' ? 'D97706' : TEXT_SECONDARY,
                  font: 'Microsoft YaHei',
                }),
              ],
            })
          )

          // 任务详情
          if (asText(task.description)) {
            bodyChildren.push(
              new Paragraph({
                spacing: { after: 40, line: 340 },
                indent: { left: 700 },
                children: [
                  new TextRun({ text: task.description, size: 20, color: TEXT_PRIMARY, font: 'Microsoft YaHei' }),
                ],
              })
            )
          }

          // 任务元信息
          const taskMetaItems: Array<[string, string]> = []
          if (asText(task.estimated_time)) taskMetaItems.push(['预计时间', task.estimated_time])
          if (asText(task.skill_target)) taskMetaItems.push(['目标能力', task.skill_target])
          if (asText(task.success_criteria)) taskMetaItems.push(['成功标准', task.success_criteria])

          for (const [metaLabel, metaValue] of taskMetaItems) {
            bodyChildren.push(
              new Paragraph({
                spacing: { after: 30, line: 320 },
                indent: { left: 700 },
                children: [
                  new TextRun({ text: `${metaLabel}：`, bold: true, size: 19, color: TEXT_LABEL, font: 'Microsoft YaHei' }),
                  new TextRun({ text: metaValue, size: 19, color: TEXT_SECONDARY, font: 'Microsoft YaHei' }),
                ],
              })
            )
          }
        }
      }
    }
  }

  // --- 第三章：中期路径规划 ---
  pushH1('三、中期路径规划')

  pushLabelValue('周期', plan.mid_term_plan.duration)

  pushH2('3.1 阶段目标')
  pushBody(plan.mid_term_plan.goal)

  if (plan.mid_term_plan.skill_roadmap.length) {
    pushH2('3.2 技能路线')
    pushBulletList(plan.mid_term_plan.skill_roadmap)
  }

  // 中期里程碑
  if (plan.mid_term_plan.milestones.length) {
    pushH2('3.3 中期里程碑')

    for (const [index, milestone] of plan.mid_term_plan.milestones.entries()) {
      pushH3(`里程碑 ${index + 1}：${milestone.milestone_name || '未命名里程碑'}`)
      if (milestone.target_date) {
        pushInfoRow('目标日期', milestone.target_date)
      }

      if (milestone.key_results.length) {
        bodyChildren.push(
          new Paragraph({
            spacing: { before: 60, after: 40 },
            indent: { left: 420 },
            children: [
              new TextRun({ text: '关键成果', bold: true, size: 20, color: BRAND_ACCENT, font: 'Microsoft YaHei' }),
            ],
          })
        )
        pushBulletList(milestone.key_results)
      }

      if (milestone.tasks.length) {
        bodyChildren.push(
          new Paragraph({
            spacing: { before: 80, after: 40 },
            indent: { left: 420 },
            children: [
              new TextRun({ text: '任务拆解', bold: true, size: 20, color: BRAND_ACCENT, font: 'Microsoft YaHei' }),
            ],
          })
        )

        for (const task of milestone.tasks) {
          bodyChildren.push(
            new Paragraph({
              spacing: { before: 100, after: 40 },
              indent: { left: 560 },
              border: {
                left: { style: BorderStyle.SINGLE, color: HEADING_LINE, size: 4 },
              },
              children: [
                new TextRun({ text: task.task_name || '未命名任务', bold: true, size: 21, color: TEXT_PRIMARY, font: 'Microsoft YaHei' }),
                new TextRun({
                  text: task.priority ? `  [${task.priority}优先级]` : '',
                  size: 18,
                  color: task.priority === '高' ? 'DC2626' : task.priority === '中' ? 'D97706' : TEXT_SECONDARY,
                  font: 'Microsoft YaHei',
                }),
              ],
            })
          )

          if (asText(task.description)) {
            bodyChildren.push(
              new Paragraph({
                spacing: { after: 40, line: 340 },
                indent: { left: 700 },
                children: [
                  new TextRun({ text: task.description, size: 20, color: TEXT_PRIMARY, font: 'Microsoft YaHei' }),
                ],
              })
            )
          }

          const taskMetaItems: Array<[string, string]> = []
          if (asText(task.estimated_time)) taskMetaItems.push(['预计时间', task.estimated_time])
          if (asText(task.skill_target)) taskMetaItems.push(['目标能力', task.skill_target])
          if (asText(task.success_criteria)) taskMetaItems.push(['成功标准', task.success_criteria])

          for (const [metaLabel, metaValue] of taskMetaItems) {
            bodyChildren.push(
              new Paragraph({
                spacing: { after: 30, line: 320 },
                indent: { left: 700 },
                children: [
                  new TextRun({ text: `${metaLabel}：`, bold: true, size: 19, color: TEXT_LABEL, font: 'Microsoft YaHei' }),
                  new TextRun({ text: metaValue, size: 19, color: TEXT_SECONDARY, font: 'Microsoft YaHei' }),
                ],
              })
            )
          }
        }
      }
    }
  }

  // --- 第四章：职业发展预期 ---
  pushH1('四、职业发展预期')
  pushBody(plan.mid_term_plan.career_progression)

  // --- 第五章：推荐实习岗位 ---
  if (plan.mid_term_plan.recommended_internships.length) {
    pushH1('五、推荐实习岗位')

    for (const [index, item] of plan.mid_term_plan.recommended_internships.entries()) {
      pushH3(`${index + 1}. ${item.job_title || '未命名岗位'}`)
      if (item.company_name) {
        pushInfoRow('公司', item.company_name)
      }
      const locationInfo = [asText(item.city), asText(item.salary), asText(item.job_type)].filter(Boolean).join('  |  ')
      if (locationInfo) {
        pushInfoRow('地点/薪资/类型', locationInfo)
      }
      if (asText(item.reason)) {
        pushInfoRow('推荐理由', item.reason)
      }
      if (asText(item.tech_stack)) {
        pushInfoRow('技术栈', item.tech_stack)
      }
      if (asText(item.content)) {
        pushBodyNoIndent(item.content)
      }
    }
  }

  // --- 第六章：行动清单 ---
  if (plan.action_checklist.length) {
    pushH1('六、行动清单')
    pushBulletList(plan.action_checklist)
  }

  // --- 第七章：学习建议 ---
  if (plan.tips.length) {
    pushH1('七、学习建议')
    pushBulletList(plan.tips)
  }

  // --- 页脚信息 ---
  bodyChildren.push(
    new Paragraph({ spacing: { before: 600 } }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      border: {
        top: { style: BorderStyle.SINGLE, color: BORDER_COLOR, size: 4 },
      },
      spacing: { before: 200 },
      children: [
        new TextRun({
          text: `本报告由 Career Planning AI 生成  |  ${reportDate}`,
          size: 16,
          color: TEXT_SECONDARY,
          font: 'Microsoft YaHei',
        }),
      ],
    })
  )

  // ===== 组装文档 =====
  const doc = new Document({
    styles: {
      default: {
        document: {
          run: {
            font: 'Microsoft YaHei',
            size: 21,
            color: TEXT_PRIMARY,
          },
          paragraph: {
            spacing: {
              line: 360,
            },
          },
        },
      },
    },
    sections: [
      // 封面页
      {
        properties: {
          page: {
            margin: {
              top: 1200,
              right: 1200,
              bottom: 1200,
              left: 1200,
            },
          },
        },
        headers: {
          default: new DocxHeader({
            children: [
              new Paragraph({
                alignment: AlignmentType.RIGHT,
                children: [
                  new TextRun({
                    text: 'Career Planning',
                    size: 16,
                    color: TEXT_SECONDARY,
                    font: 'Microsoft YaHei',
                    italics: true,
                  }),
                ],
              }),
            ],
          }),
        },
        footers: {
          default: new DocxFooter({
            children: [
              new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({
                    children: [PageNumber.CURRENT],
                    size: 16,
                    color: TEXT_SECONDARY,
                    font: 'Microsoft YaHei',
                  }),
                ],
              }),
            ],
          }),
        },
        children: coverChildren,
      },
      // 正文页
      {
        properties: {
          page: {
            margin: {
              top: 1000,
              right: 1100,
              bottom: 1000,
              left: 1100,
            },
          },
        },
        headers: {
          default: new DocxHeader({
            children: [
              new Paragraph({
                alignment: AlignmentType.RIGHT,
                children: [
                  new TextRun({
                    text: asText(plan.target_position) || '生涯成长报告',
                    size: 16,
                    color: TEXT_SECONDARY,
                    font: 'Microsoft YaHei',
                    italics: true,
                  }),
                ],
              }),
            ],
          }),
        },
        footers: {
          default: new DocxFooter({
            children: [
              new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({
                    text: 'Career Planning  |  ',
                    size: 16,
                    color: TEXT_SECONDARY,
                    font: 'Microsoft YaHei',
                  }),
                  new TextRun({
                    children: [PageNumber.CURRENT],
                    size: 16,
                    color: TEXT_SECONDARY,
                    font: 'Microsoft YaHei',
                  }),
                ],
              }),
            ],
          }),
        },
        children: bodyChildren,
      },
    ],
  })

  const blob = await Packer.toBlob(doc)
  saveAs(blob, sanitizeDownloadFileName(options?.fileName ?? 'growth-plan.docx', 'growth-plan.docx'))
}
