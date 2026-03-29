// ReferralDTO.java
package com.backend.careerplanningbackend.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import jakarta.validation.constraints.NotNull;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ReferralDTO {
//    @NotNull(message = "发出邀请人ID不能为空")
    private Long referrerId;
    
//    @NotNull(message = "接受被邀请人ID不能为空")
    private Long userId;
    
//    @NotNull(message = "邀请码不能为空")
    private String inviteCode;
    
    private Integer rewardPoints;
}