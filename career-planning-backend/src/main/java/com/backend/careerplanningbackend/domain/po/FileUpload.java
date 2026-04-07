package com.backend.careerplanningbackend.domain.po;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@TableName("file_upload")
public class FileUpload {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    private Long userId;
    private String fileUrl;
    @TableField("file_name")
    private String filename;
}
