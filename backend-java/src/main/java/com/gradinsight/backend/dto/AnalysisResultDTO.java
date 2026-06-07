package com.gradinsight.backend.dto;

import lombok.Data;

import java.util.List;

@Data
public class AnalysisResultDTO {
    private String summary;
    private List<String> keywords;
}
