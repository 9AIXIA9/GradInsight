package com.gradinsight.backend.controller;

import com.gradinsight.backend.service.AnalysisService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/analysis")
public class AnalysisController {

    private final AnalysisService analysisService;

    public AnalysisController(AnalysisService analysisService) {
        this.analysisService = analysisService;
    }

    @PostMapping("/cluster")
    public ResponseEntity<Map<?,?>> cluster(@RequestBody Object payload) {
        Map<?,?> resp = analysisService.cluster(payload);
        return ResponseEntity.ok(resp);
    }

    @PostMapping("/keywords")
    public ResponseEntity<Map<?,?>> keywords(@RequestBody Object payload) {
        Map<?,?> resp = analysisService.keywords(payload);
        return ResponseEntity.ok(resp);
    }

    @PostMapping("/sentiment")
    public ResponseEntity<Map<?,?>> sentiment(@RequestBody Object payload) {
        Map<?,?> resp = analysisService.sentiment(payload);
        return ResponseEntity.ok(resp);
    }
}
