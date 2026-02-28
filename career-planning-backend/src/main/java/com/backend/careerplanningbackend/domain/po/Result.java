package com.backend.careerplanningbackend.domain.po;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Result<T> {
    private int code;// 成功为 --200  失败为 401
    private String msg;// 提示消息
    private T data;// 返回数据

    /*   返回一个正确的消息   */
    public static Result ok(){
        return new Result(200,null,null);
    }
    /*   返回一个查询到的消息   */
    public static<T> Result ok(T data){
        return new Result(200,null,data);
    }
    /*   返回一个列表查询的正确消息   */
    public static Result ok(List<?> data){
        return new Result(200,null,data);
    }
    /*   返回一个错误消息   */
    public static Result fail(String msg){
        return new Result(401,msg,null);
    }
    public static Result fail(Integer code,String msg){
        return new Result(code,msg,null);
    }
}
