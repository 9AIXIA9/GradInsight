package com.gradinsight.backend.controller;

import com.gradinsight.backend.dto.AnalysisResultDTO;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/analysis")
public class AnalysisController {

    @PostMapping("/cluster")
    public ResponseEntity<AnalysisResultDTO> cluster(@RequestBody String payload) {
        // TODO: 调用 Python 分析服务（REST/gRPC），返回聚类结果
        AnalysisResultDTO r = new AnalysisResultDTO();
        r.setSummary("placeholder cluster result");
        return ResponseEntity.ok(r);
    }
}
