package com.gradinsight.backend.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
public class AnalysisService {
    private static final Logger log = LoggerFactory.getLogger(AnalysisService.class);

    private final RestTemplate restTemplate;
    private final String baseUrl;

    public AnalysisService(RestTemplate restTemplate, @Value("${analysis.service.url}") String baseUrl) {
        this.restTemplate = restTemplate;
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length()-1) : baseUrl;
    }

    public Map<?,?> cluster(Object payload) {
        try {
            ResponseEntity<Map> resp = restTemplate.postForEntity(baseUrl + "/cluster", payload, Map.class);
            return resp.getBody();
        } catch (Exception ex) {
            log.error("cluster call failed", ex);
            return Map.of("success", false, "error", ex.getMessage());
        }
    }

    public Map<?,?> keywords(Object payload) {
        try {
            ResponseEntity<Map> resp = restTemplate.postForEntity(baseUrl + "/keywords", payload, Map.class);
            return resp.getBody();
        } catch (Exception ex) {
            log.error("keywords call failed", ex);
            return Map.of("success", false, "error", ex.getMessage());
        }
    }

    public Map<?,?> sentiment(Object payload) {
        try {
            ResponseEntity<Map> resp = restTemplate.postForEntity(baseUrl + "/sentiment", payload, Map.class);
            return resp.getBody();
        } catch (Exception ex) {
            log.error("sentiment call failed", ex);
            return Map.of("success", false, "error", ex.getMessage());
        }
    }
}
