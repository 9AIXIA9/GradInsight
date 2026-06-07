package com.gradinsight.backend.grpc;

import crawler.Crawler;
import io.grpc.CallOptions;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.MethodDescriptor;
import io.grpc.protobuf.ProtoUtils;
import io.grpc.stub.ClientCalls;
import jakarta.annotation.PreDestroy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class CrawlerGrpcClient {
    private static final Logger log = LoggerFactory.getLogger(CrawlerGrpcClient.class);
    private static final String SERVICE_NAME = "crawler.CrawlerService";
    private static final String METHOD_NAME = "StartCrawl";

    private final ManagedChannel channel;
    private final MethodDescriptor<Crawler.CrawlRequest, Crawler.CrawlResponse> startCrawlMethod;

    public CrawlerGrpcClient(@Value("${crawler.grpc.host:localhost}") String host,
                             @Value("${crawler.grpc.port:8999}") int port) {
        this.channel = ManagedChannelBuilder.forAddress(host, port).usePlaintext().build();
        this.startCrawlMethod = MethodDescriptor.<Crawler.CrawlRequest, Crawler.CrawlResponse>newBuilder()
                .setType(MethodDescriptor.MethodType.UNARY)
                .setFullMethodName(MethodDescriptor.generateFullMethodName(SERVICE_NAME, METHOD_NAME))
                .setRequestMarshaller(ProtoUtils.marshaller(Crawler.CrawlRequest.getDefaultInstance()))
                .setResponseMarshaller(ProtoUtils.marshaller(Crawler.CrawlResponse.getDefaultInstance()))
                .build();
        log.info("Initialized CrawlerGrpcClient to {}:{}", host, port);
    }

    public Crawler.CrawlResponse startCrawl(Crawler.CrawlRequest req) {
        return ClientCalls.blockingUnaryCall(channel, startCrawlMethod, CallOptions.DEFAULT, req);
    }

    @PreDestroy
    public void shutdown() {
        if (channel != null && !channel.isShutdown()) {
            channel.shutdownNow();
        }
    }
}
