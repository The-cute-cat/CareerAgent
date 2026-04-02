package com.backend.careerplanningbackend.controller;

import com.backend.careerplanningbackend.domain.dto.ResumeData;
import com.deepoove.poi.XWPFTemplate;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpHeaders;
import org.springframework.web.bind.annotation.*;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

@RestController
@RequestMapping("/api/resume")
public class ResumeExportController {

    // 假设这是前端传过来的 JSON 对应的 Java 实体类
//     public class ResumeData { String name; String phone; List<WorkExp> workExp; ... }

    @PostMapping("/export/{format}")
    public void exportResume(
            @PathVariable("format") String format,
            @RequestBody ResumeData resumeData,
            HttpServletResponse response) throws Exception {

        // 1. 获取输出流
        OutputStream out = response.getOutputStream();

        // 2. 根据不同格式设置响应头和执行渲染逻辑
        switch (format.toLowerCase()) {
            case "word":
                // 设置 Word 的 Content-Type 和下载文件名
                response.setContentType("application/vnd.openxmlformats-officedocument.wordprocessingml.document");
                response.setHeader(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=resume.docx");
                
                // 伪代码：调用 POI-tl 渲染 Word 并写入流
                 XWPFTemplate template = XWPFTemplate.compile("template.docx").render(resumeData);
                 template.write(out);
                 template.close();
                break;

            case "pdf":
                // 设置 PDF 的 Content-Type
                response.setContentType("application/pdf");
                // inline 表示在浏览器直接预览（如果浏览器支持），attachment 表示直接下载
                response.setHeader(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=resume.pdf");
                
                // 伪代码：HTML 转 PDF 并写入流
//                 String html = thymeleafEngine.process("resume", resumeData);
//                 PdfUtil.generatePdfFromHtml(html, out);
                break;

            case "md":
                // 设置 Markdown 的 Content-Type
                response.setContentType("text/markdown");
                response.setHeader(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=resume.md");
                
                // 伪代码：拼接 Markdown 字符串并转为字节写入流
//                 String markdownText = generateMarkdownString(resumeData);
//                 out.write(markdownText.getBytes(StandardCharsets.UTF_8));
                break;

            default:
                throw new IllegalArgumentException("不支持的导出格式");
        }

        // 3. 刷新并关闭流
        out.flush();
        out.close();
    }
}