package com.marketdata.streamprocessingservice.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.marketdata.common.dto.MarketDataPoint;
import com.marketdata.common.dto.AnomalyDto;
import com.marketdata.common.enums.AnomalyType;
import com.marketdata.common.enums.DataSourceType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.LocalDateTime;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

/**
 * Service for detecting anomalies in market data
 * Integrates with Python detection engine
 */
@Service
public class AnomalyDetectionService {

    private static final Logger logger = LoggerFactory.getLogger(AnomalyDetectionService.class);

    @Value("${detection.engine.url:http://localhost:8085}")
    private String detectionEngineUrl;

    private final WebClient webClient;
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    // Cache for recent data points to enable time-series analysis
    private final ConcurrentMap<String, List<MarketDataPoint>> recentDataCache = new ConcurrentHashMap<>();
    private final int MAX_CACHE_SIZE = 100;

    public AnomalyDetectionService() {
        this.webClient = WebClient.builder()
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(1024 * 1024))
                .build();
    }

    /**
     * Detect anomalies in market data point
     */
    public CompletableFuture<AnomalyDto> detectAnomalies(MarketDataPoint dataPoint) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                // Update cache with recent data
                updateDataCache(dataPoint);
                
                // Get recent data for the symbol
                List<MarketDataPoint> recentData = recentDataCache.get(dataPoint.getSymbol());
                
                if (recentData == null || recentData.size() < 2) {
                    // Not enough data for anomaly detection
                    return null;
                }

                // Call Python detection engine for missing data detection
                AnomalyDto missingDataAnomaly = detectMissingData(recentData);
                if (missingDataAnomaly != null) {
                    return missingDataAnomaly;
                }

                // Call Python detection engine for price movement detection
                AnomalyDto priceMovementAnomaly = detectPriceMovement(recentData);
                if (priceMovementAnomaly != null) {
                    return priceMovementAnomaly;
                }

                // Local data stale detection
                AnomalyDto staleDataAnomaly = detectStaleData(dataPoint);
                if (staleDataAnomaly != null) {
                    return staleDataAnomaly;
                }

                return null;

            } catch (Exception e) {
                logger.error("Error detecting anomalies for symbol: {}", dataPoint.getSymbol(), e);
                return null;
            }
        });
    }

    /**
     * Update data cache with recent data points
     */
    private void updateDataCache(MarketDataPoint dataPoint) {
        recentDataCache.compute(dataPoint.getSymbol(), (symbol, existingData) -> {
            if (existingData == null) {
                existingData = new java.util.ArrayList<>();
            }
            
            existingData.add(dataPoint);
            
            // Keep only recent data points
            if (existingData.size() > MAX_CACHE_SIZE) {
                existingData = existingData.subList(existingData.size() - MAX_CACHE_SIZE, existingData.size());
            }
            
            return existingData;
        });
    }

    /**
     * Detect missing data anomalies using Python engine
     */
    private AnomalyDto detectMissingData(List<MarketDataPoint> dataPoints) {
        try {
            String response = webClient.post()
                    .uri(detectionEngineUrl + "/detect/missing-data")
                    .bodyValue(dataPoints)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();

            if (response != null && !response.equals("[]")) {
                // Parse response and return first anomaly
                List<AnomalyDto> anomalies = objectMapper.readValue(response, 
                        objectMapper.getTypeFactory().constructCollectionType(List.class, AnomalyDto.class));
                
                if (!anomalies.isEmpty()) {
                    return anomalies.get(0);
                }
            }

        } catch (Exception e) {
            logger.error("Error calling missing data detection", e);
        }
        
        return null;
    }

    /**
     * Detect price movement anomalies using Python engine
     */
    private AnomalyDto detectPriceMovement(List<MarketDataPoint> dataPoints) {
        try {
            String response = webClient.post()
                    .uri(detectionEngineUrl + "/detect/price-movement")
                    .bodyValue(dataPoints)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();

            if (response != null && !response.equals("[]")) {
                // Parse response and return first anomaly
                List<AnomalyDto> anomalies = objectMapper.readValue(response, 
                        objectMapper.getTypeFactory().constructCollectionType(List.class, AnomalyDto.class));
                
                if (!anomalies.isEmpty()) {
                    return anomalies.get(0);
                }
            }

        } catch (Exception e) {
            logger.error("Error calling price movement detection", e);
        }
        
        return null;
    }

    /**
     * Detect stale data locally (simple time-based check)
     */
    private AnomalyDto detectStaleData(MarketDataPoint dataPoint) {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime dataTime = dataPoint.getTimestamp();
        
        if (dataTime != null) {
            long minutesDiff = java.time.Duration.between(dataTime, now).toMinutes();
            
            // Consider data stale if older than 30 minutes during market hours
            if (minutesDiff > 30) {
                AnomalyDto anomaly = new AnomalyDto();
                anomaly.setSymbol(dataPoint.getSymbol());
                anomaly.setAnomalyType(AnomalyType.DATA_STALE);
                anomaly.setSeverity(minutesDiff > 60 ? "high" : "medium");
                anomaly.setDetectedAt(now);
                anomaly.setDataTimestamp(dataTime);
                anomaly.setDescription(String.format("Data is %d minutes old", minutesDiff));
                anomaly.setDataSource(dataPoint.getSource());
                anomaly.setDataType(dataPoint.getDataType());
                
                return anomaly;
            }
        }
        
        return null;
    }

    /**
     * Get detection service health status
     */
    public boolean isHealthy() {
        try {
            String response = webClient.get()
                    .uri(detectionEngineUrl + "/health")
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();
            
            return response != null && response.contains("UP");
            
        } catch (Exception e) {
            logger.error("Health check failed for detection engine", e);
            return false;
        }
    }

    /**
     * Get cache statistics
     */
    public CacheStats getCacheStats() {
        CacheStats stats = new CacheStats();
        stats.setCachedSymbols(recentDataCache.size());
        stats.setTotalDataPoints(recentDataCache.values().stream()
                .mapToInt(List::size)
                .sum());
        return stats;
    }

    /**
     * Cache statistics
     */
    public static class CacheStats {
        private int cachedSymbols;
        private int totalDataPoints;

        public int getCachedSymbols() { return cachedSymbols; }
        public void setCachedSymbols(int cachedSymbols) { this.cachedSymbols = cachedSymbols; }

        public int getTotalDataPoints() { return totalDataPoints; }
        public void setTotalDataPoints(int totalDataPoints) { this.totalDataPoints = totalDataPoints; }
    }
}
