package com.backend.careerplanningbackend.domain.dto;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CodeAbilityDTO {
    @JsonProperty("url")
    private String url;

    @JsonAlias({"use_ai", "useAi"})
    @JsonProperty("use_ai")
    private Boolean use_ai;

    @JsonAlias({"cache_enabled", "cacheEnabled"})
    @JsonProperty("cache_enabled")
    private Boolean cache_enabled;
}
