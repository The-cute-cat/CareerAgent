package com.backend.careerplanningbackend.domain.dto;

import lombok.Data;

@Data
public class UserDTO {
    private Long id;

    private String username;
    private String nickname;
    private String avatar;
    private String email;
    private String info;
}
