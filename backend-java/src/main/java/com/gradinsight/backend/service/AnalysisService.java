package com.gradinsight.backend.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
public class AnalysisService {
    private static final Logger log = LoggerFactory.getLogger(AnalysisService.class);

    private final RestTemplate restTemplate;
    private final String baseUrl;

    public AnalysisService(RestTemplate restTemplate,
                           @Value("${analysis.service.url}") String baseUrl) {
        this.restTemplate = restTemplate;
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
    }

    /** POST proxy */
    public Map<?, ?> post(String path, Object payload) {
        try {
            ResponseEntity<Map> resp = restTemplate.postForEntity(
                    baseUrl + path, payload, Map.class);
            return resp.getBody();
        } catch (Exception ex) {
            log.error("analysis POST {} failed", path, ex);
            return Map.of("success", false, "error", ex.getMessage());
        }
    }

    /** GET proxy */
    public Map<?, ?> get(String path) {
        try {
            ResponseEntity<Map> resp = restTemplate.getForEntity(
                    baseUrl + path, Map.class);
            return resp.getBody();
        } catch (Exception ex) {
            log.error("analysis GET {} failed", path, ex);
            return Map.of("success", false, "error", ex.getMessage());
        }
    }

    public Map<?, ?> cluster(Object payload) { return post("/cluster", payload); }
    public Map<?, ?> keywords(Object payload) { return post("/keywords", payload); }
    public Map<?, ?> sentiment(Object payload) { return post("/sentiment", payload); }
}
