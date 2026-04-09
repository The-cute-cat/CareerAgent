/*
 Navicat Premium Dump SQL

 Source Server         : SQLPub
 Source Server Type    : MySQL
 Source Server Version : 80403 (8.4.3-SQLPub-0.0.1)
 Source Host           : mysql6.sqlpub.com:3311
 Source Schema         : career_backend

 Target Server Type    : MySQL
 Target Server Version : 80403 (8.4.3-SQLPub-0.0.1)
 File Encoding         : 65001

 Date: 09/04/2026 20:07:23
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for action_plan
-- ----------------------------
DROP TABLE IF EXISTS `action_plan`;
CREATE TABLE `action_plan`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '为了这份工作岗位的行动计划表',
  `report_id` bigint NOT NULL COMMENT '关联报告ID',
  `phase` tinyint NOT NULL COMMENT '阶段: 1短期, 2中期',
  `plan_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '具体计划内容',
  `indicators` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '评估指标',
  `status` tinyint NULL DEFAULT 0 COMMENT '执行状态: 0未开始, 1进行中, 2已完成',
  `is_deleted` tinyint NULL DEFAULT 0 COMMENT '逻辑删除',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_report_id`(`report_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '行动计划表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for career_report
-- ----------------------------
DROP TABLE IF EXISTS `career_report`;
CREATE TABLE `career_report`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID(职业规划报告表)返回给界面',
  `student_id` bigint NOT NULL COMMENT '关联 student_profile.id',
  `target_job_id` bigint NOT NULL COMMENT '匹配的目标岗位ID',
  `match_score` decimal(5, 2) NULL DEFAULT NULL COMMENT '人岗匹配度综合得分',
  `path_plan` json NULL COMMENT '职业发展路径规划 (JSON)',
  `action_plan` json NULL COMMENT '行动计划 (短期、中期的具体建议 JSON)',
  `report_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '完整报告的 Markdown 文本',
  `creat_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_student_id`(`student_id` ASC) USING BTREE,
  INDEX `idx_target_job_id`(`target_job_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '智能职业规划报告表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for conversation_sessions
-- ----------------------------
DROP TABLE IF EXISTS `conversation_sessions`;
CREATE TABLE `conversation_sessions`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '会话ID',
  `user_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户ID',
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '会话标题',
  `compressed_summary` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '压缩后的摘要',
  `message_count` int NOT NULL DEFAULT 0 COMMENT '消息数量',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_session_id`(`session_id` ASC) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  UNIQUE INDEX `uq_user_session`(`user_id` ASC, `session_id` ASC) USING BTREE,
  INDEX `idx_user_session`(`user_id` ASC, `session_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 37 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '会话表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for feedback
-- ----------------------------
DROP TABLE IF EXISTS `feedback`;
CREATE TABLE `feedback`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `response` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `user_id` bigint NULL DEFAULT NULL,
  `contact` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `images_list` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `status` int NULL DEFAULT NULL,
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for file_upload
-- ----------------------------
DROP TABLE IF EXISTS `file_upload`;
CREATE TABLE `file_upload`  (
  `id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `user_id` int NULL DEFAULT NULL,
  `file_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `file_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`(4)) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for interview_reminder
-- ----------------------------
DROP TABLE IF EXISTS `interview_reminder`;
CREATE TABLE `interview_reminder`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `company_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `job_title` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `interview_time` datetime NOT NULL COMMENT '面试时间',
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '面试地点/会议链接',
  `remind_status` tinyint NULL DEFAULT 0 COMMENT '提醒状态: 0未提醒, 1已发送通知',
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '面试准备备注',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_time`(`user_id` ASC, `interview_time` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '面试提醒记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for job_match_record
-- ----------------------------
DROP TABLE IF EXISTS `job_match_record`;
CREATE TABLE `job_match_record`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `stu_id` bigint NOT NULL COMMENT '关联学生账号id',
  `job_id` bigint NOT NULL,
  `score_basic` decimal(5, 2) NULL DEFAULT 0.00 COMMENT '基础要求得分',
  `score_skill` decimal(5, 2) NULL DEFAULT 0.00 COMMENT '职业技能得分',
  `score_soft` decimal(5, 2) NULL DEFAULT 0.00 COMMENT '职业素养得分',
  `score_potential` decimal(5, 2) NULL DEFAULT 0.00 COMMENT '发展潜力得分',
  `total_score` decimal(5, 2) NULL DEFAULT 0.00 COMMENT '综合匹配度',
  `gap_analysis` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '差距分析描述',
  `is_deleted` tinyint NULL DEFAULT 0 COMMENT '逻辑删除',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_stu_job`(`stu_id` ASC, `job_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '人岗匹配记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for job_original
-- ----------------------------
DROP TABLE IF EXISTS `job_original`;
CREATE TABLE `job_original`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `job_profile_id` int NULL DEFAULT NULL COMMENT '指向合并后的岗位id，默认为空',
  `job_title` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '岗位名称',
  `location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '地址',
  `salary_range` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '薪资范围',
  `company_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '公司名称',
  `industry` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '所属行业',
  `company_size` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '公司规模',
  `company_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '公司类型',
  `job_code` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '岗位编码',
  `job_desc` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '岗位详情',
  `company_desc` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '公司详情',
  `job_source_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '岗位来源地址',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日期',
  `is_deleted` tinyint NULL DEFAULT 0 COMMENT '逻辑删除-1表示逻辑删除',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_job_title`(`job_title` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10152 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '岗位基础数据表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for job_profile
-- ----------------------------
DROP TABLE IF EXISTS `job_profile`;
CREATE TABLE `job_profile`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '一个岗位所需要的能力,学习抗压之类的',
  `job_title` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '合并后的岗位总名称',
  `tech_skills` json NULL COMMENT '专业技能关键词 (JSON数组)',
  `certificates` json NULL COMMENT '证书要求',
  `score_innovation` int NULL DEFAULT 0 COMMENT '创新能力要求(0-100)',
  `score_learning` int NULL DEFAULT 0 COMMENT '学习能力要求',
  `score_stress` int NULL DEFAULT 0 COMMENT '抗压能力要求',
  `score_communication` int NULL DEFAULT 0 COMMENT '沟通能力要求',
  `intern_req` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '实习经验要求',
  `potential_dir` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '发展潜力描述',
  `is_deleted` tinyint NULL DEFAULT 0 COMMENT '逻辑删除',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `skills_req` json NOT NULL COMMENT '岗位要求画像 (JSON)',
  `radar_data` json NULL COMMENT '岗位雷达图基准数据(JSON）',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_job_id`(`job_title` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 140 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '岗位画像表（合并之后）' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for job_relation
-- ----------------------------
DROP TABLE IF EXISTS `job_relation`;
CREATE TABLE `job_relation`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '一个岗位晋升关系',
  `source_job_id` bigint NOT NULL COMMENT '起始岗位ID',
  `target_job_id` bigint NOT NULL COMMENT '目标岗位ID',
  `relation_type` tinyint NOT NULL COMMENT '关系类型: 1垂直晋升, 2横向换岗',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '路径说明',
  `is_deleted` tinyint NULL DEFAULT 0 COMMENT '逻辑删除',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_source_job`(`source_job_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '岗位关系图谱表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for knowledge_base
-- ----------------------------
DROP TABLE IF EXISTS `knowledge_base`;
CREATE TABLE `knowledge_base`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '分类: 行业报告, 政策, 技能库',
  `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '知识内容/摘要',
  `vector_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '对应向量数据库中的ID',
  `is_deleted` tinyint NULL DEFAULT 0 COMMENT '逻辑删除',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '本地知识库表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for learning_node_analysis
-- ----------------------------
DROP TABLE IF EXISTS `learning_node_analysis`;
CREATE TABLE `learning_node_analysis`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `report_id` bigint NOT NULL COMMENT '关联 career_report.id',
  `knowledge_point` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '知识点名称(如:Spring Boot)',
  `ai_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT 'AI 生成的详细内容讲解',
  `learning_tips` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '学习建议与避坑指南',
  `resource_links` json NULL COMMENT '推荐学习资源(JSON数组)',
  `is_mastered` tinyint NULL DEFAULT 0 COMMENT '是否已掌握: 0否, 1是',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_report`(`report_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = 'AI 学习路径节点解析表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for memories
-- ----------------------------
DROP TABLE IF EXISTS `memories`;
CREATE TABLE `memories`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户ID',
  `session_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '会话ID',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '记忆内容',
  `memory_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '记忆类型：preference/decision/fact/goal',
  `importance_score` float NOT NULL DEFAULT 0.5 COMMENT '重要性评分(0-1)',
  `relevance_score` float NOT NULL DEFAULT 0.5 COMMENT '相关性评分(0-1)',
  `recency_score` float NOT NULL DEFAULT 0.5 COMMENT '时效性评分(0-1)',
  `uniqueness_score` float NOT NULL DEFAULT 0.5 COMMENT '独特性评分(0-1)',
  `total_score` float NOT NULL DEFAULT 0.5 COMMENT '综合评分(0-1)',
  `metadata_json` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '额外元数据(JSON格式)',
  `vector_id` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '向量数据库中的ID',
  `is_active` tinyint NOT NULL DEFAULT 1 COMMENT '是否激活',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_session_id`(`session_id` ASC) USING BTREE,
  INDEX `idx_user_session`(`user_id` ASC, `session_id` ASC) USING BTREE,
  INDEX `idx_total_score`(`total_score` ASC) USING BTREE,
  INDEX `idx_created_at`(`created_at` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 29 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '长期记忆表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for package
-- ----------------------------
DROP TABLE IF EXISTS `package`;
CREATE TABLE `package`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT ' 1-积分 2 会员--套餐',
  `amount` decimal(10, 2) NULL DEFAULT NULL COMMENT '金额',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '套餐描述',
  `points` int NULL DEFAULT NULL COMMENT '积分',
  `status` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '是否启用：0-禁用，1-启用',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for payment_order
-- ----------------------------
DROP TABLE IF EXISTS `payment_order`;
CREATE TABLE `payment_order`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `package_id` int NULL DEFAULT NULL COMMENT '积分或者套餐id',
  `amount` decimal(10, 2) NULL DEFAULT NULL COMMENT '金额',
  `points` int NULL DEFAULT NULL COMMENT '积分',
  `pay_type` tinyint NOT NULL COMMENT '支付方式: 1微信, 2支付宝',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '备注',
  `status` tinyint NULL DEFAULT 0 COMMENT '支付状态: 0待支付, 1已支付, 2已取消, 3已退款',
  `pay_time` datetime NULL DEFAULT NULL COMMENT '支付完成时间',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '支付订单完成',
  `update_time` datetime NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '交易完成时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2041126985192407042 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '支付订单记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for points_transaction
-- ----------------------------
DROP TABLE IF EXISTS `points_transaction`;
CREATE TABLE `points_transaction`  (
  `id` bigint NOT NULL COMMENT '积分交易订单',
  `user_id` bigint NOT NULL,
  `amount` decimal(10, 2) NULL DEFAULT NULL COMMENT '金额变动',
  `points` int NULL DEFAULT NULL COMMENT '积分变动值(正值为加，负值为减)',
  `package_id` int NULL DEFAULT NULL COMMENT '套餐id',
  `type` tinyint NOT NULL COMMENT '0:会员充值, 1:充值积分, 2:购买AI报告, 3:AI知识讲解消费, 4:推广奖励, 5:系统赠送,',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '流水描述',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `vip` tinyint NULL DEFAULT 0 COMMENT '会员等级，0:非会员, 1:普通会员, 2:高级会员, 3:至尊会员',
  `status` tinyint NULL DEFAULT 1 COMMENT '0-支付成功,1-待支付,2超时了,3-退款了已经,',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_type`(`user_id` ASC, `type` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '积分变动流水表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for question_answer
-- ----------------------------
DROP TABLE IF EXISTS `question_answer`;
CREATE TABLE `question_answer`  (
  `id` bigint NOT NULL,
  `select` int NULL DEFAULT NULL COMMENT '1-选择题,2-填空题,3-场景题、架构题,',
  `topic` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'Java后端',
  `question` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `source` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'spring-ai',
  `answer` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `stackLevel` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '技术级别（初级/中级/高级)',
  `raw_payload` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '原始响应内容（便于排查）',
  `language` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '中文',
  `job_category` int NULL DEFAULT NULL,
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for resume
-- ----------------------------
DROP TABLE IF EXISTS `resume`;
CREATE TABLE `resume`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '简历表',
  `stu_id` bigint NOT NULL COMMENT '关联学生账号表',
  `file_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_url` varchar(504) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'OSS或本地存储路径',
  `raw_text` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '解析出的原始文本',
  `is_deleted` tinyint NULL DEFAULT 0 COMMENT '逻辑删除',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_stu_id`(`stu_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '简历表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for resume_template
-- ----------------------------
DROP TABLE IF EXISTS `resume_template`;
CREATE TABLE `resume_template`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `tpl_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模板名称',
  `thumbnail` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '缩略图地址',
  `style_config` json NULL COMMENT '前端样式渲染配置JSON',
  `is_active` tinyint NULL DEFAULT 1 COMMENT '是否启用',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '简历模板配置表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for stu_profile
-- ----------------------------
DROP TABLE IF EXISTS `stu_profile`;
CREATE TABLE `stu_profile`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '学生能力表',
  `stu_id` bigint NOT NULL COMMENT '关联stu_info ID',
  `people_form` json NULL COMMENT '人物表单信息',
  `people_profile` json NULL COMMENT '人物画像信息',
  `tech_skills` json NULL COMMENT '掌握技能专业技能 (JSON数组，如 [\"Java\", \"Spring\"])',
  `radar_data` json NULL COMMENT '雷达图维度分数数据 (JSON)',
  `soft_skills` json NULL COMMENT '软素质评估 (JSON对象，包含创新、抗压、沟通的打分)',
  `score_innovation` int NULL DEFAULT 0,
  `score_learning` int NULL DEFAULT 0,
  `score_stress` int NULL DEFAULT 0,
  `score_communication` int NULL DEFAULT 0,
  `intern_exp` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '实习/项目经历',
  `score_integrity` int NULL DEFAULT 0 COMMENT '画像完整度评分',
  `score_compete` int NULL DEFAULT 0 COMMENT '就业竞争力评分',
  `is_deleted` tinyint NULL DEFAULT 0 COMMENT '逻辑删除',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `skills_stu` json NULL COMMENT '人物画像总',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_stu_id`(`stu_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '学生画像表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_membership
-- ----------------------------
DROP TABLE IF EXISTS `user_membership`;
CREATE TABLE `user_membership`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL COMMENT '关联 user_stu.id',
  `level` tinyint NOT NULL DEFAULT 0 COMMENT '0普通用户, 1月度VIP, 2季度VIP, 3年度VIP,4管理员',
  `expire_time` datetime NULL DEFAULT NULL COMMENT '会员到期时间',
  `is_infinite_points` tinyint NOT NULL DEFAULT 0 COMMENT '是否无限积分(针对VIP1/年度会员)',
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_id`(`user_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户会员状态表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_points
-- ----------------------------
DROP TABLE IF EXISTS `user_points`;
CREATE TABLE `user_points`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL COMMENT '关联 user_stu.id',
  `points_balance` int NULL DEFAULT 0 COMMENT '剩余积分余额',
  `points_remain_amount` int NULL DEFAULT NULL COMMENT '该笔积分剩余可用量(用于精确扣减)',
  `status` tinyint NULL DEFAULT 1 COMMENT '1:有效, 0:已耗尽或已过期',
  `total_consumed` int NULL DEFAULT 0 COMMENT '累计消耗积分',
  `end_time` datetime NULL DEFAULT NULL COMMENT '积分结束时间',
  `activity_end_time` datetime NULL DEFAULT NULL COMMENT '活动结束时间',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_user_id`(`user_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户积分账户表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_referral
-- ----------------------------
DROP TABLE IF EXISTS `user_referral`;
CREATE TABLE `user_referral`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `referrer_id` bigint NULL DEFAULT NULL COMMENT '发出邀请人(大使)ID',
  `user_id` bigint(20) UNSIGNED ZEROFILL NULL DEFAULT NULL COMMENT '接受邀请的新用户ID',
  `invite_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户的专属邀请码(注册成功后生成)',
  `reward_points` int NULL DEFAULT 50 COMMENT '该笔邀请获得的积分奖励',
  `status` int NULL DEFAULT 1 COMMENT '1-正常',
  `end_time` datetime NULL DEFAULT NULL COMMENT '积分结束时间',
  `activity_end_time` datetime NULL DEFAULT NULL COMMENT '活动结束时间',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_referrer`(`referrer_id` ASC) USING BTREE,
  INDEX `idx_user`(`user_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 574636366160199687 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '推广大使邀请关系表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_stu
-- ----------------------------
DROP TABLE IF EXISTS `user_stu`;
CREATE TABLE `user_stu`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID(学生账号原始表)',
  `username` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户名',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '密码',
  `nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户昵称 (默认显示用)',
  `role` tinyint NOT NULL DEFAULT 1 COMMENT '角色：1-学生，2-系统管理员，3-指导老师',
  `avatar` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '用户头像URL',
  `info` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `status` tinyint NOT NULL DEFAULT 1 COMMENT '账号状态：0-禁用，1-启用',
  `email` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '邮箱',
  `is_deleted` tinyint NULL DEFAULT 0 COMMENT '逻辑删除-1表示逻辑删除',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `phone` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '手机号',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_id`(`id` ASC) USING BTREE,
  UNIQUE INDEX `uk_username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1039 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '核心用户主表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_stu_info
-- ----------------------------
DROP TABLE IF EXISTS `user_stu_info`;
CREATE TABLE `user_stu_info`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '学生学历信息表',
  `membershipLevel` int NULL DEFAULT NULL COMMENT '会员等级字段',
  `user_id` bigint NOT NULL COMMENT '关联sys_user ID',
  `real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '真实姓名',
  `github_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'github_name',
  `gitee_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'gitee_name',
  `phone` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '手机号码',
  `bio` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '个人简介',
  `school` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '就读高校',
  `major` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '专业',
  `edu_level` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '学历: 本科, 硕士, 博士',
  `start_year` int NULL DEFAULT NULL COMMENT '入学年份（如 2023）',
  `grad_year` int NULL DEFAULT NULL COMMENT '毕业年份',
  `career_intention` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '就业意愿描述',
  `is_deleted` tinyint NULL DEFAULT 0 COMMENT '逻辑删除-1表示逻辑删除',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1002 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '学生信息表' ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
