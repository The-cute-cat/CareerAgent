// ReferralDTO.java
package com.backend.careerplanningbackend.domain.dto;

import lombok.Data;
import jakarta.validation.constraints.NotNull;

@Data
public class ReferralDTO {
//    @NotNull(message = "邀请人ID不能为空")
    private Long referrerId;
    
    @NotNull(message = "被邀请人ID不能为空")
    private Long refereeId;
    
    @NotNull(message = "邀请码不能为空")
    private String inviteCode;
}