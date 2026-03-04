package com.backend.careerplanningbackend;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.backend.careerplanningbackend.mapper")
public class CareerPlanningBackendApplication {

    public static void main(String[] args) {
        SpringApplication.run(CareerPlanningBackendApplication.class, args);
    }

}
