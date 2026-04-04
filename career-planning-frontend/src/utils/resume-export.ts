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
}

/** 导出 Word 的配置。 */
export interface ResumeWordExportOptions {
  /** 导出文件名。 */
  fileName?: string
}

/** 将任意值标准化为文本。 */
function asText(value?: string | null): string {
  return typeof value === 'string' ? value.trim() : ''
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
  const targetHeight = (canvas.height * targetWidth) / canvas.width
  const imageData = canvas.toDataURL('image/png')

  let renderedHeight = targetHeight
  let offsetY = 0

  pdf.addImage(imageData, 'PNG', margin, margin, targetWidth, targetHeight)
  renderedHeight -= pageHeight - margin * 2

  while (renderedHeight > 0) {
    offsetY += pageHeight - margin * 2
    pdf.addPage()
    pdf.addImage(imageData, 'PNG', margin, margin - offsetY, targetWidth, targetHeight)
    renderedHeight -= pageHeight - margin * 2
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
