package com.backend.careerplanningbackend.domain.dto;

import lombok.Data;

@Data
public class LoginFormDTO {
    private String username;
    private String password;
    private String passwordConfirm;
    private String email;
    private String code;
}
