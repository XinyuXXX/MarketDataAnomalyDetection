package com.marketdata.streamprocessingservice.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.marketdata.common.dto.MarketDataPoint;
import com.marketdata.common.dto.AnomalyDto;
import org.apache.pulsar.client.api.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

/**
 * Real-time market data stream processor using Pulsar
 */
@Service
public class MarketDataStreamProcessor {

    private static final Logger logger = LoggerFactory.getLogger(MarketDataStreamProcessor.class);

    @Autowired
    private PulsarClient pulsarClient;

    @Autowired
    private AnomalyDetectionService anomalyDetectionService;

    private final ObjectMapper objectMapper = new ObjectMapper();
    
    private Consumer<byte[]> marketDataConsumer;
    private Producer<byte[]> anomalyProducer;

    // Topic names
    private static final String MARKET_DATA_TOPIC = "market-data-stream";
    private static final String ANOMALY_TOPIC = "anomaly-alerts";
    private static final String SUBSCRIPTION_NAME = "stream-processor";

    @PostConstruct
    public void initialize() {
        try {
            // Create consumer for market data
            marketDataConsumer = pulsarClient.newConsumer()
                    .topic(MARKET_DATA_TOPIC)
                    .subscriptionName(SUBSCRIPTION_NAME)
                    .subscriptionType(SubscriptionType.Shared)
                    .messageListener(this::processMarketData)
                    .subscribe();

            // Create producer for anomalies
            anomalyProducer = pulsarClient.newProducer()
                    .topic(ANOMALY_TOPIC)
                    .create();

            logger.info("Market data stream processor initialized successfully");

        } catch (PulsarClientException e) {
            logger.error("Failed to initialize stream processor", e);
            throw new RuntimeException("Failed to initialize stream processor", e);
        }
    }

    /**
     * Process incoming market data messages
     */
    private void processMarketData(Consumer<byte[]> consumer, Message<byte[]> message) {
        try {
            // Parse market data
            String jsonData = new String(message.getData());
            MarketDataPoint dataPoint = objectMapper.readValue(jsonData, MarketDataPoint.class);
            
            logger.debug("Processing market data: {} - {}", dataPoint.getSymbol(), dataPoint.getPrice());

            // Detect anomalies
            CompletableFuture<AnomalyDto> anomalyFuture = anomalyDetectionService.detectAnomalies(dataPoint);
            
            anomalyFuture.thenAccept(anomaly -> {
                if (anomaly != null) {
                    // Send anomaly to alert topic
                    sendAnomalyAlert(anomaly);
                }
            }).exceptionally(throwable -> {
                logger.error("Error detecting anomalies for {}", dataPoint.getSymbol(), throwable);
                return null;
            });

            // Acknowledge message
            consumer.acknowledge(message);

        } catch (Exception e) {
            logger.error("Error processing market data message", e);
            // Negative acknowledge to retry
            consumer.negativeAcknowledge(message);
        }
    }

    /**
     * Send anomaly alert to Pulsar topic
     */
    private void sendAnomalyAlert(AnomalyDto anomaly) {
        try {
            String anomalyJson = objectMapper.writeValueAsString(anomaly);
            
            anomalyProducer.newMessage()
                    .key(anomaly.getSymbol())
                    .value(anomalyJson.getBytes())
                    .property("anomaly_type", anomaly.getAnomalyType().toString())
                    .property("severity", anomaly.getSeverity())
                    .sendAsync()
                    .thenAccept(messageId -> {
                        logger.info("Anomaly alert sent: {} - {} - {}", 
                                anomaly.getSymbol(), anomaly.getAnomalyType(), anomaly.getSeverity());
                    })
                    .exceptionally(throwable -> {
                        logger.error("Failed to send anomaly alert", throwable);
                        return null;
                    });

        } catch (Exception e) {
            logger.error("Error serializing anomaly alert", e);
        }
    }

    /**
     * Send market data to stream for processing
     */
    public CompletableFuture<MessageId> sendMarketData(MarketDataPoint dataPoint) {
        try {
            String jsonData = objectMapper.writeValueAsString(dataPoint);
            
            return pulsarClient.newProducer()
                    .topic(MARKET_DATA_TOPIC)
                    .create()
                    .newMessage()
                    .key(dataPoint.getSymbol())
                    .value(jsonData.getBytes())
                    .property("source", dataPoint.getSource().toString())
                    .property("data_type", dataPoint.getDataType())
                    .sendAsync();

        } catch (Exception e) {
            logger.error("Error sending market data to stream", e);
            CompletableFuture<MessageId> failedFuture = new CompletableFuture<>();
            failedFuture.completeExceptionally(e);
            return failedFuture;
        }
    }

    /**
     * Get stream processing statistics
     */
    public StreamProcessingStats getStats() {
        StreamProcessingStats stats = new StreamProcessingStats();
        
        try {
            if (marketDataConsumer != null) {
                ConsumerStats consumerStats = marketDataConsumer.getStats();
                stats.setMessagesReceived(consumerStats.getNumMsgsReceived());
                stats.setBytesReceived(consumerStats.getNumBytesReceived());
            }
            
            if (anomalyProducer != null) {
                ProducerStats producerStats = anomalyProducer.getStats();
                stats.setAnomaliesSent(producerStats.getNumMsgsSent());
                stats.setBytesSent(producerStats.getNumBytesSent());
            }
            
        } catch (Exception e) {
            logger.error("Error getting stream processing stats", e);
        }
        
        return stats;
    }

    @PreDestroy
    public void cleanup() {
        try {
            if (marketDataConsumer != null) {
                marketDataConsumer.close();
            }
            if (anomalyProducer != null) {
                anomalyProducer.close();
            }
            logger.info("Stream processor cleaned up successfully");
        } catch (PulsarClientException e) {
            logger.error("Error during cleanup", e);
        }
    }

    /**
     * Stream processing statistics
     */
    public static class StreamProcessingStats {
        private long messagesReceived;
        private long bytesReceived;
        private long anomaliesSent;
        private long bytesSent;

        // Getters and setters
        public long getMessagesReceived() { return messagesReceived; }
        public void setMessagesReceived(long messagesReceived) { this.messagesReceived = messagesReceived; }

        public long getBytesReceived() { return bytesReceived; }
        public void setBytesReceived(long bytesReceived) { this.bytesReceived = bytesReceived; }

        public long getAnomaliesSent() { return anomaliesSent; }
        public void setAnomaliesSent(long anomaliesSent) { this.anomaliesSent = anomaliesSent; }

        public long getBytesSent() { return bytesSent; }
        public void setBytesSent(long bytesSent) { this.bytesSent = bytesSent; }
    }
}
