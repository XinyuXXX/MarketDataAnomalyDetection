package com.marketdata.dataingestionservice.controller;

import com.marketdata.common.dto.MarketDataPoint;
import com.marketdata.dataingestionservice.service.DataIngestionService;
import com.marketdata.dataingestionservice.adapter.DataSourceAdapter;
import com.marketdata.dataingestionservice.adapter.impl.EODDataAdapter;
import com.marketdata.dataingestionservice.adapter.impl.GemfireAdapter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.time.LocalDateTime;
import java.util.concurrent.CompletableFuture;

@RestController
public class HealthController {

    @Autowired
    private DataIngestionService dataIngestionService;

    @Autowired
    private EODDataAdapter eodDataAdapter;

    @Autowired
    private GemfireAdapter gemfireAdapter;

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "UP");
        response.put("service", "data-ingestion-service");
        response.put("timestamp", LocalDateTime.now());

        // Add adapter health status
        Map<String, Object> adapters = new HashMap<>();
        adapters.put("eod_data", eodDataAdapter.getHealth());
        adapters.put("gemfire", gemfireAdapter.getHealth());
        response.put("adapters", adapters);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/stats")
    public ResponseEntity<DataIngestionService.IngestionStats> getStats() {
        return ResponseEntity.ok(dataIngestionService.getStats());
    }

    @PostMapping("/ingest")
    public CompletableFuture<ResponseEntity<Map<String, Object>>> ingestData(
            @RequestBody MarketDataPoint dataPoint) {

        return dataIngestionService.ingestMarketData(dataPoint)
                .thenApply(messageId -> {
                    Map<String, Object> response = new HashMap<>();
                    response.put("success", true);
                    response.put("message_id", messageId);
                    response.put("timestamp", LocalDateTime.now());
                    return ResponseEntity.ok(response);
                })
                .exceptionally(throwable -> {
                    Map<String, Object> response = new HashMap<>();
                    response.put("success", false);
                    response.put("error", throwable.getMessage());
                    response.put("timestamp", LocalDateTime.now());
                    return ResponseEntity.badRequest().body(response);
                });
    }

    @PostMapping("/ingest/batch")
    public CompletableFuture<ResponseEntity<Map<String, Object>>> ingestBatch(
            @RequestBody List<MarketDataPoint> dataPoints) {

        return dataIngestionService.ingestBatch(dataPoints)
                .thenApply(messageIds -> {
                    Map<String, Object> response = new HashMap<>();
                    response.put("success", true);
                    response.put("message_ids", messageIds);
                    response.put("count", messageIds.size());
                    response.put("timestamp", LocalDateTime.now());
                    return ResponseEntity.ok(response);
                })
                .exceptionally(throwable -> {
                    Map<String, Object> response = new HashMap<>();
                    response.put("success", false);
                    response.put("error", throwable.getMessage());
                    response.put("timestamp", LocalDateTime.now());
                    return ResponseEntity.badRequest().body(response);
                });
    }
}