package com.marketdata.dataingestionservice.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.marketdata.common.dto.MarketDataPoint;
import com.marketdata.common.enums.DataSourceType;
import org.apache.pulsar.client.api.Producer;
import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.PulsarClientException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.time.LocalDateTime;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Data ingestion service for multiple data sources
 */
@Service
public class DataIngestionService {

    private static final Logger logger = LoggerFactory.getLogger(DataIngestionService.class);

    @Autowired
    private PulsarClient pulsarClient;

    @Value("${pulsar.topics.market-data:market-data-stream}")
    private String marketDataTopic;

    private final ObjectMapper objectMapper = new ObjectMapper();
    private Producer<byte[]> marketDataProducer;
    
    // Statistics tracking
    private final AtomicLong totalMessagesIngested = new AtomicLong(0);
    private final ConcurrentMap<DataSourceType, AtomicLong> sourceStats = new ConcurrentHashMap<>();

    @PostConstruct
    public void initialize() {
        try {
            // Create producer for market data
            marketDataProducer = pulsarClient.newProducer()
                    .topic(marketDataTopic)
                    .create();

            logger.info("Data ingestion service initialized successfully");

        } catch (PulsarClientException e) {
            logger.error("Failed to initialize data ingestion service", e);
            throw new RuntimeException("Failed to initialize data ingestion service", e);
        }
    }

    /**
     * Ingest market data from various sources
     */
    public CompletableFuture<String> ingestMarketData(MarketDataPoint dataPoint) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                // Validate data point
                if (!isValidDataPoint(dataPoint)) {
                    throw new IllegalArgumentException("Invalid data point");
                }

                // Enrich data point
                enrichDataPoint(dataPoint);

                // Convert to JSON
                String jsonData = objectMapper.writeValueAsString(dataPoint);

                // Send to Pulsar
                return marketDataProducer.newMessage()
                        .key(dataPoint.getSymbol())
                        .value(jsonData.getBytes())
                        .property("source", dataPoint.getSource().toString())
                        .property("data_type", dataPoint.getDataType())
                        .property("ingestion_time", LocalDateTime.now().toString())
                        .sendAsync()
                        .thenApply(messageId -> {
                            // Update statistics
                            totalMessagesIngested.incrementAndGet();
                            sourceStats.computeIfAbsent(dataPoint.getSource(), k -> new AtomicLong(0))
                                    .incrementAndGet();

                            logger.debug("Data ingested: {} - {} - {}", 
                                    dataPoint.getSymbol(), dataPoint.getSource(), messageId);
                            
                            return messageId.toString();
                        })
                        .exceptionally(throwable -> {
                            logger.error("Failed to ingest data for {}", dataPoint.getSymbol(), throwable);
                            throw new RuntimeException("Failed to ingest data", throwable);
                        })
                        .join();

            } catch (Exception e) {
                logger.error("Error ingesting market data", e);
                throw new RuntimeException("Error ingesting market data", e);
            }
        });
    }

    /**
     * Batch ingest multiple data points
     */
    public CompletableFuture<List<String>> ingestBatch(List<MarketDataPoint> dataPoints) {
        List<CompletableFuture<String>> futures = dataPoints.stream()
                .map(this::ingestMarketData)
                .toList();

        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
                .thenApply(v -> futures.stream()
                        .map(CompletableFuture::join)
                        .toList());
    }

    /**
     * Validate data point
     */
    private boolean isValidDataPoint(MarketDataPoint dataPoint) {
        if (dataPoint == null) {
            return false;
        }

        if (dataPoint.getSymbol() == null || dataPoint.getSymbol().trim().isEmpty()) {
            logger.warn("Invalid data point: missing symbol");
            return false;
        }

        if (dataPoint.getSource() == null) {
            logger.warn("Invalid data point: missing source");
            return false;
        }

        if (dataPoint.getPrice() != null && dataPoint.getPrice() <= 0) {
            logger.warn("Invalid data point: invalid price {}", dataPoint.getPrice());
            return false;
        }

        if (dataPoint.getVolume() != null && dataPoint.getVolume() < 0) {
            logger.warn("Invalid data point: invalid volume {}", dataPoint.getVolume());
            return false;
        }

        return true;
    }

    /**
     * Enrich data point with additional metadata
     */
    private void enrichDataPoint(MarketDataPoint dataPoint) {
        LocalDateTime now = LocalDateTime.now();
        
        // Set received timestamp if not present
        if (dataPoint.getReceivedAt() == null) {
            dataPoint.setReceivedAt(now);
        }

        // Set data timestamp if not present
        if (dataPoint.getTimestamp() == null) {
            dataPoint.setTimestamp(now);
        }

        // Set data type if not present
        if (dataPoint.getDataType() == null) {
            if (dataPoint.getPrice() != null) {
                dataPoint.setDataType("price");
            } else if (dataPoint.getVolume() != null) {
                dataPoint.setDataType("volume");
            } else {
                dataPoint.setDataType("unknown");
            }
        }
    }

    /**
     * Get ingestion statistics
     */
    public IngestionStats getStats() {
        IngestionStats stats = new IngestionStats();
        stats.setTotalMessagesIngested(totalMessagesIngested.get());
        
        // Convert source stats
        ConcurrentMap<String, Long> sourceStatsMap = new ConcurrentHashMap<>();
        sourceStats.forEach((source, count) -> 
                sourceStatsMap.put(source.toString(), count.get()));
        stats.setSourceStats(sourceStatsMap);
        
        return stats;
    }

    /**
     * Reset statistics
     */
    public void resetStats() {
        totalMessagesIngested.set(0);
        sourceStats.clear();
        logger.info("Ingestion statistics reset");
    }

    @PreDestroy
    public void cleanup() {
        try {
            if (marketDataProducer != null) {
                marketDataProducer.close();
            }
            logger.info("Data ingestion service cleaned up successfully");
        } catch (PulsarClientException e) {
            logger.error("Error during cleanup", e);
        }
    }

    /**
     * Ingestion statistics
     */
    public static class IngestionStats {
        private long totalMessagesIngested;
        private ConcurrentMap<String, Long> sourceStats;

        public long getTotalMessagesIngested() { return totalMessagesIngested; }
        public void setTotalMessagesIngested(long totalMessagesIngested) { 
            this.totalMessagesIngested = totalMessagesIngested; 
        }

        public ConcurrentMap<String, Long> getSourceStats() { return sourceStats; }
        public void setSourceStats(ConcurrentMap<String, Long> sourceStats) { 
            this.sourceStats = sourceStats; 
        }
    }
}
