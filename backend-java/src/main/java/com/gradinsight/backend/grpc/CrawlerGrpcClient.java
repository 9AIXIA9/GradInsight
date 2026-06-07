package com.gradinsight.backend.grpc;

import crawler.CrawlRequest;
import crawler.CrawlResponse;
import crawler.CrawlerServiceGrpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import jakarta.annotation.PreDestroy;

@Component
public class CrawlerGrpcClient {
    private static final Logger log = LoggerFactory.getLogger(CrawlerGrpcClient.class);

    private final ManagedChannel channel;
    private final CrawlerServiceGrpc.CrawlerServiceBlockingStub blockingStub;

    public CrawlerGrpcClient(@Value("${crawler.grpc.host:localhost}") String host,
                             @Value("${crawler.grpc.port:8999}") int port) {
        this.channel = ManagedChannelBuilder.forAddress(host, port).usePlaintext().build();
        this.blockingStub = CrawlerServiceGrpc.newBlockingStub(channel);
        log.info("Initialized CrawlerGrpcClient to {}:{}", host, port);
    }

    public CrawlResponse startCrawl(CrawlRequest req) {
        return blockingStub.startCrawl(req);
    }

    @PreDestroy
    public void shutdown() {
        if (channel != null && !channel.isShutdown()) {
            channel.shutdownNow();
        }
    }
}
