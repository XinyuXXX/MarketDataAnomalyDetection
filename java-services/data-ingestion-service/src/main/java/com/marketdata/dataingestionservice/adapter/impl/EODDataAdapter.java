package com.marketdata.dataingestionservice.adapter.impl;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.marketdata.common.dto.MarketDataPoint;
import com.marketdata.common.enums.DataSourceType;
import com.marketdata.dataingestionservice.adapter.DataSourceAdapter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;

/**
 * EOD (End of Day) Data adapter implementation
 */
@Component
public class EODDataAdapter implements DataSourceAdapter {

    private static final Logger logger = LoggerFactory.getLogger(EODDataAdapter.class);

    @Value("${eod.api.url:https://eodhistoricaldata.com/api}")
    private String eodApiUrl;

    @Value("${eod.api.token:demo}")
    private String apiToken;

    private final WebClient webClient;
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final AtomicBoolean connected = new AtomicBoolean(false);
    private final AtomicBoolean streaming = new AtomicBoolean(false);
    private final AtomicLong totalFetches = new AtomicLong(0);
    private final AtomicLong failedFetches = new AtomicLong(0);
    private final AtomicLong lastSuccessfulFetch = new AtomicLong(0);

    public EODDataAdapter() {
        this.webClient = WebClient.builder()
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(1024 * 1024))
                .build();
    }

    @Override
    public DataSourceType getSourceType() {
        return DataSourceType.EOD_DATA;
    }

    @Override
    public CompletableFuture<Boolean> connect() {
        return CompletableFuture.supplyAsync(() -> {
            try {
                // Test connection by fetching a simple quote
                String testUrl = String.format("%s/real-time/AAPL.US?api_token=%s&fmt=json", 
                        eodApiUrl, apiToken);
                
                String response = webClient.get()
                        .uri(testUrl)
                        .retrieve()
                        .bodyToMono(String.class)
                        .block();

                if (response != null && !response.contains("error")) {
                    connected.set(true);
                    logger.info("Successfully connected to EOD Data API");
                    return true;
                } else {
                    logger.error("Failed to connect to EOD Data API: {}", response);
                    return false;
                }

            } catch (Exception e) {
                logger.error("Error connecting to EOD Data API", e);
                connected.set(false);
                return false;
            }
        });
    }

    @Override
    public CompletableFuture<Boolean> disconnect() {
        return CompletableFuture.supplyAsync(() -> {
            connected.set(false);
            streaming.set(false);
            logger.info("Disconnected from EOD Data API");
            return true;
        });
    }

    @Override
    public boolean isConnected() {
        return connected.get();
    }

    @Override
    public CompletableFuture<List<MarketDataPoint>> fetchLatestData() {
        return fetchDataForSymbols(List.of("AAPL.US", "GOOGL.US", "MSFT.US", "TSLA.US"));
    }

    @Override
    public CompletableFuture<List<MarketDataPoint>> fetchDataForSymbols(List<String> symbols) {
        return CompletableFuture.supplyAsync(() -> {
            List<MarketDataPoint> dataPoints = new ArrayList<>();
            totalFetches.incrementAndGet();

            try {
                for (String symbol : symbols) {
                    MarketDataPoint dataPoint = fetchSingleSymbol(symbol);
                    if (dataPoint != null) {
                        dataPoints.add(dataPoint);
                    }
                }

                if (!dataPoints.isEmpty()) {
                    lastSuccessfulFetch.set(System.currentTimeMillis());
                }

                logger.debug("Fetched {} data points from EOD Data", dataPoints.size());
                return dataPoints;

            } catch (Exception e) {
                failedFetches.incrementAndGet();
                logger.error("Error fetching data from EOD Data", e);
                return dataPoints;
            }
        });
    }

    private MarketDataPoint fetchSingleSymbol(String symbol) {
        try {
            String url = String.format("%s/real-time/%s?api_token=%s&fmt=json", 
                    eodApiUrl, symbol, apiToken);

            String response = webClient.get()
                    .uri(url)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();

            if (response == null || response.contains("error")) {
                logger.warn("No data received for symbol: {}", symbol);
                return null;
            }

            // Parse JSON response
            JsonNode jsonNode = objectMapper.readTree(response);
            
            MarketDataPoint dataPoint = new MarketDataPoint();
            dataPoint.setSymbol(symbol);
            dataPoint.setSource(DataSourceType.EOD_DATA);
            dataPoint.setDataType("real-time");
            dataPoint.setTimestamp(LocalDateTime.now());
            dataPoint.setReceivedAt(LocalDateTime.now());

            // Extract price data
            if (jsonNode.has("close")) {
                dataPoint.setPrice(jsonNode.get("close").asDouble());
            }

            // Extract volume data
            if (jsonNode.has("volume")) {
                dataPoint.setVolume(jsonNode.get("volume").asDouble());
            }

            // Add additional payload data
            Map<String, Object> payload = new HashMap<>();
            if (jsonNode.has("open")) {
                payload.put("open", jsonNode.get("open").asDouble());
            }
            if (jsonNode.has("high")) {
                payload.put("high", jsonNode.get("high").asDouble());
            }
            if (jsonNode.has("low")) {
                payload.put("low", jsonNode.get("low").asDouble());
            }
            if (jsonNode.has("change")) {
                payload.put("change", jsonNode.get("change").asDouble());
            }
            if (jsonNode.has("change_p")) {
                payload.put("change_percent", jsonNode.get("change_p").asDouble());
            }

            dataPoint.setPayload(payload);

            return dataPoint;

        } catch (Exception e) {
            logger.error("Error fetching data for symbol: {}", symbol, e);
            return null;
        }
    }

    @Override
    public CompletableFuture<Boolean> startStreaming(DataStreamCallback callback) {
        return CompletableFuture.supplyAsync(() -> {
            if (!connected.get()) {
                logger.error("Cannot start streaming: not connected to EOD Data");
                return false;
            }

            streaming.set(true);
            logger.info("Started EOD Data streaming (simulated)");

            // EOD Data doesn't provide real-time streaming, so we simulate it
            // by polling at regular intervals
            CompletableFuture.runAsync(() -> {
                while (streaming.get()) {
                    try {
                        List<MarketDataPoint> dataPoints = fetchLatestData().get();
                        for (MarketDataPoint dataPoint : dataPoints) {
                            if (streaming.get()) {
                                callback.onData(dataPoint);
                            }
                        }

                        // Wait 30 seconds before next poll
                        Thread.sleep(30000);

                    } catch (Exception e) {
                        logger.error("Error in EOD Data streaming", e);
                        callback.onError(e);
                        break;
                    }
                }
            });

            return true;
        });
    }

    @Override
    public CompletableFuture<Boolean> stopStreaming() {
        return CompletableFuture.supplyAsync(() -> {
            streaming.set(false);
            logger.info("Stopped EOD Data streaming");
            return true;
        });
    }

    @Override
    public AdapterHealth getHealth() {
        boolean healthy = connected.get() && 
                (System.currentTimeMillis() - lastSuccessfulFetch.get()) < 300000; // 5 minutes

        String status = healthy ? "healthy" : "unhealthy";
        if (!connected.get()) {
            status = "disconnected";
        }

        AdapterHealth health = new AdapterHealth(healthy, status);
        health.setLastSuccessfulFetch(lastSuccessfulFetch.get());
        health.setTotalFetches(totalFetches.get());
        health.setFailedFetches(failedFetches.get());

        return health;
    }
}
