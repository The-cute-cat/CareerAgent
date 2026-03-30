package com.backend.careerplanningbackend.util;

import java.time.LocalDateTime;

public class SystemActivityConstant {

    /**
     * 积分有效期 1 年
     */
    public static final int Points_Validity_Year = 1;

    /**
     * 邀请码活动进行 10 年
     */
    public static final int Activity_Duration_Year = 10;

    /**
     * 邀请码活动开始时间
     */
    public static final LocalDateTime Activity_Start_Time = 
            LocalDateTime.of(2026,1,1,0,0,0);


    /**
     * 邀请码活动结束时间
     */
    public static final LocalDateTime Activity_End_Time =
            LocalDateTime.of(2035,1,1,0,0,0);

    
    
}
