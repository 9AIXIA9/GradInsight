package com.gradinsight.backend.grpc;

import com.gradinsight.proto.analysis.AnalyzeRequest;
import com.gradinsight.proto.analysis.AnalyzeResponse;
import com.gradinsight.proto.analysis.AnalysisServiceGrpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import jakarta.annotation.PreDestroy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class AnalysisGrpcClient {
    private static final Logger log = LoggerFactory.getLogger(AnalysisGrpcClient.class);

    private final ManagedChannel channel;
    private final AnalysisServiceGrpc.AnalysisServiceBlockingStub stub;

    public AnalysisGrpcClient(
            @Value("${analysis.grpc.host:localhost}") String host,
            @Value("${analysis.grpc.port:5001}") int port) {
        this.channel = ManagedChannelBuilder.forAddress(host, port)
                .usePlaintext()
                .build();
        this.stub = AnalysisServiceGrpc.newBlockingStub(channel);
        log.info("AnalysisGrpcClient connected to {}:{}", host, port);
    }

    public AnalyzeResponse analyze(AnalyzeRequest request) {
        log.info("Calling Python analysis gRPC: types={}, keyword={}",
                request.getAnalysisTypesList(), request.getKeywordFilter());
        try {
            return stub.withDeadlineAfter(120, java.util.concurrent.TimeUnit.SECONDS)
                    .analyze(request);
        } catch (Exception e) {
            log.error("gRPC call failed: {}", e.getMessage(), e);
            throw new RuntimeException("Python analysis service unavailable: " + e.getMessage(), e);
        }
    }

    @PreDestroy
    public void shutdown() {
        if (channel != null && !channel.isShutdown()) {
            channel.shutdownNow();
        }
    }
}