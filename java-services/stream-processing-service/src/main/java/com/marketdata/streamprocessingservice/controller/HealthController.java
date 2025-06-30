package com.marketdata.streamprocessingservice.controller;

import com.marketdata.streamprocessingservice.service.MarketDataStreamProcessor;
import com.marketdata.streamprocessingservice.service.AnomalyDetectionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.ResponseEntity;
import java.util.Map;
import java.util.HashMap;
import java.time.LocalDateTime;

@RestController
public class HealthController {

    @Autowired
    private MarketDataStreamProcessor streamProcessor;

    @Autowired
    private AnomalyDetectionService anomalyDetectionService;

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "UP");
        response.put("service", "stream-processing-service");
        response.put("timestamp", LocalDateTime.now());

        // Add component health status
        response.put("detection_engine_healthy", anomalyDetectionService.isHealthy());

        return ResponseEntity.ok(response);
    }

    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        Map<String, Object> response = new HashMap<>();

        // Stream processing stats
        MarketDataStreamProcessor.StreamProcessingStats streamStats = streamProcessor.getStats();
        response.put("stream_stats", streamStats);

        // Cache stats
        AnomalyDetectionService.CacheStats cacheStats = anomalyDetectionService.getCacheStats();
        response.put("cache_stats", cacheStats);

        response.put("timestamp", LocalDateTime.now());

        return ResponseEntity.ok(response);
    }
}