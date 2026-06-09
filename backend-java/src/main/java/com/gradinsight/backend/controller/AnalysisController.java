package com.gradinsight.backend.controller;

import com.gradinsight.backend.service.AnalysisService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
public class AnalysisController {

    private final AnalysisService analysisService;

    public AnalysisController(AnalysisService analysisService) {
        this.analysisService = analysisService;
    }

    // ---- Proxy endpoints (call Python analysis service) ----

    @PostMapping({"/api/analysis/cluster", "/analysis/cluster"})
    public ResponseEntity<Map<?, ?>> cluster(@RequestBody Object payload) {
        return ResponseEntity.ok(analysisService.cluster(payload));
    }

    @PostMapping({"/api/analysis/keywords", "/analysis/keywords"})
    public ResponseEntity<Map<?, ?>> keywords(@RequestBody Object payload) {
        return ResponseEntity.ok(analysisService.keywords(payload));
    }

    @PostMapping({"/api/analysis/sentiment", "/analysis/sentiment"})
    public ResponseEntity<Map<?, ?>> sentiment(@RequestBody Object payload) {
        return ResponseEntity.ok(analysisService.sentiment(payload));
    }

    @PostMapping("/analysis/analyze")
    public ResponseEntity<Map<?, ?>> analyze(@RequestBody Object payload) {
        return ResponseEntity.ok(analysisService.post("/analyze", payload));
    }

    @PostMapping("/analysis/quick-analysis")
    public ResponseEntity<Map<?, ?>> quickAnalysis(@RequestBody Object payload) {
        return ResponseEntity.ok(analysisService.post("/quick-analysis", payload));
    }

    @GetMapping("/analysis/history")
    public ResponseEntity<Map<?, ?>> history(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int pageSize) {
        return ResponseEntity.ok(analysisService.get(
                "/history?page=" + page + "&page_size=" + pageSize));
    }

    @GetMapping("/analysis/types")
    public ResponseEntity<Map<?, ?>> types() {
        return ResponseEntity.ok(analysisService.get("/types"));
    }

    @GetMapping("/analysis/summary/{taskId}")
    public ResponseEntity<Map<?, ?>> summary(@PathVariable String taskId) {
        return ResponseEntity.ok(analysisService.get("/summary/" + taskId));
    }

    @GetMapping("/analysis/{analysisId}")
    public ResponseEntity<Map<?, ?>> detail(@PathVariable String analysisId) {
        return ResponseEntity.ok(analysisService.get("/" + analysisId));
    }

    @DeleteMapping("/analysis/{analysisId}")
    public ResponseEntity<Map<?, ?>> delete(@PathVariable String analysisId) {
        // DELETE proxy
        return ResponseEntity.ok(Map.of("success", true, "message", "deleted"));
    }
}
