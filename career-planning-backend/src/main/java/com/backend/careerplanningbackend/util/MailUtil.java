package com.backend.careerplanningbackend.util;

import jakarta.mail.internet.MimeMessage;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;

@Slf4j
@Component
public class MailUtil {

    @Autowired
    private JavaMailSender mailSender;

    @Value("${spring.mail.username}")
    private String fromEmail;

    /**
     * 发送错误通知邮件
     * @param subject 主题
     * @param content 内容
     */
    public void sendErrorNotification(String subject, String content) {
        try {
            SimpleMailMessage message = new SimpleMailMessage();
            message.setFrom(fromEmail);
            message.setTo("3402351070@qq.com"); // 客服邮箱地址
            message.setSubject(subject);
            message.setText(content);
            mailSender.send(message);
            log.info("错误通知邮件发送成功");
        } catch (Exception e) {
            log.error("发送错误通知邮件失败", e);
        }
    }

    public void send(SimpleMailMessage message,String toEmail) {
        try {
            message.setFrom(fromEmail);
            message.setTo(toEmail);
            mailSender.send(message);
            log.info("错误通知邮件发送成功");
        } catch (Exception e) {
            log.error("发送错误通知邮件失败", e);
        }
    }

    public void sendHtmlEmail(String toEmail, String subject, String htmlContent) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setFrom(fromEmail);
            helper.setTo(toEmail);
            helper.setSubject(subject);
            helper.setText(htmlContent, true); // true 表示是 HTML

            mailSender.send(message);
            log.info("HTML 邮件发送成功至: {}", toEmail);
        } catch (Exception e) {
            log.error("发送 HTML 邮件失败", e);
        }
    }

    public String buildBusinessAnnouncementEmail(String companyName, String title,
                                                 String content, String actionUrl,
                                                 String actionText, String footerInfo) {
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { margin: 0; padding: 0; background-color: #f4f4f4; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
                .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; }
                .header { background: linear-gradient(135deg, #667eea 0%%, #764ba2 100%%); padding: 40px 30px; text-align: center; }
                .header h1 { color: #ffffff; margin: 0; font-size: 28px; font-weight: 300; letter-spacing: 2px; }
                .logo { width: 80px; height: 80px; background-color: rgba(255,255,255,0.2); border-radius: 50%%; margin: 0 auto 20px; line-height: 80px; color: white; font-size: 32px; }
                .content { padding: 40px 30px; }
                .title { color: #333333; font-size: 24px; margin-bottom: 20px; font-weight: 600; }
                .text { color: #666666; font-size: 16px; line-height: 1.8; margin-bottom: 30px; }
                .button { display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #667eea 0%%, #764ba2 100%%); color: #ffffff; text-decoration: none; border-radius: 30px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
                .divider { height: 1px; background-color: #eeeeee; margin: 30px 0; }
                .footer { background-color: #f8f9fa; padding: 30px; text-align: center; color: #999999; font-size: 12px; }
                .social { margin: 20px 0; }
                .social a { display: inline-block; margin: 0 10px; color: #667eea; text-decoration: none; }
                @media only screen and (max-width: 600px) {
                    .container { width: 100%% !important; }
                    .content { padding: 20px !important; }
                }
            </style>
        </head>
        <body>
            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%%">
                <tr>
                    <td>
                        <div class="container">
                            <div class="header">
                                <div class="logo">%s</div>
                                <h1>%s</h1>
                            </div>
                            <div class="content">
                                <div class="title">%s</div>
                                <div class="text">%s</div>
                                <div style="text-align: center;">
                                    <a href="%s" class="button">%s</a>
                                </div>
                                <div class="divider"></div>
                            </div>
                            <div class="footer">
                                <div class="social">
                                    <a href="#">官网</a> | 
                                    <a href="#">微博</a> | 
                                    <a href="#">微信</a>
                                </div>
                                <p>%s</p>
                                <p>此邮件由系统自动发送，请勿直接回复</p>
                                <p>&copy; 2026 %s. All rights reserved.</p>
                            </div>
                        </div>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """.formatted(
                companyName.substring(0, 1),  // Logo 首字母
                companyName,
                title,
                content,
                actionUrl,
                actionText,
                footerInfo,
                companyName
        );
    }
    
//    public void sendBusinessAnnouncement() {
//        String html = buildBusinessAnnouncementEmail(
//            "TechCorp",  // 公司名称
//            "重要产品更新公告",  // 标题
//            "<p>尊敬的用户：</p>" +
//            "<p>我们很高兴地宣布，经过数月的精心研发，<strong>TechCorp 3.0</strong> 版本正式上线！</p>" +
//            "<p>本次更新包含以下重要特性：</p>" +
//            "<ul>" +
//            "<li>全新 UI 设计，操作更加流畅</li>" +
//            "<li>AI 智能助手，提升工作效率 300%</li>" +
//            "<li>企业级安全保障，数据更加安全</li>" +
//            "</ul>" +
//            "<p>立即体验全新功能，开启高效办公新时代。</p>",
//            "https://techcorp.com/upgrade",  // 按钮链接
//            "立即升级",  // 按钮文字
//            "北京市朝阳区科技园区 A 座 | 客服热线：400-888-8888"
//        );
//        
//        sendHtmlEmail("user@example.com", "🚀 TechCorp 3.0 重磅发布", html);
//    }
}
