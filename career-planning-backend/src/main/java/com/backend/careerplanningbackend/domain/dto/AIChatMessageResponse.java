package com.backend.careerplanningbackend.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class AIChatMessageResponse {

    // 响应状态码
    private int code;
    // 请求是否成功
    private boolean state;
    // 响应消息
    private String msg;
    // 响应数据（根据不同接口返回不同类型）
    private Object data;

}
