package com.backend.careerplanningbackend.domain.po;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Result<T> {
    private int code;
    private String msg;
    private T data;

    public static <T> Result<T> ok() {
        return new Result<>(200, null, null);
    }

    public static <T> Result<T> ok(T data) {
        return new Result<>(200, null, data);
    }

    public static Result<List<?>> ok(String msg,List<?> data) {
        return new Result<>(200, null, data);
    }

    public static <T> Result<T> fail(String msg) {
        return new Result<>(401, msg, null);
    }

    public static <T> Result<T> fail(Integer code, String msg) {
        return new Result<>(code, msg, null);
    }
}
