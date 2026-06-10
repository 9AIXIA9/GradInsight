package com.gradinsight.backend.service;

import com.gradinsight.proto.analysis.AnalyzeRequest;
import com.gradinsight.proto.analysis.AnalyzeResponse;
import com.gradinsight.backend.grpc.AnalysisGrpcClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class AnalysisService {
    private static final Logger log = LoggerFactory.getLogger(AnalysisService.class);

    private final AnalysisGrpcClient client;

    public AnalysisService(AnalysisGrpcClient client) {
        this.client = client;
    }

    public AnalyzeResponse analyze(List<String> analysisTypes, String keywordFilter, int minPosts) {
        AnalyzeRequest req = AnalyzeRequest.newBuilder()
                .addAllAnalysisTypes(analysisTypes)
                .setKeywordFilter(keywordFilter != null ? keywordFilter : "")
                .setMinPosts(minPosts > 0 ? minPosts : 5)
                .build();
        return client.analyze(req);
    }
}