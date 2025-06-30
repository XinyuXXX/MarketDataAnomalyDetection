package com.marketdata.dataingestionservice.adapter.impl;

import com.marketdata.common.dto.MarketDataPoint;
import com.marketdata.common.enums.DataSourceType;
import com.marketdata.dataingestionservice.adapter.DataSourceAdapter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Gemfire Cache adapter implementation (simulated)
 * In a real implementation, this would connect to Apache Geode/Gemfire
 */
@Component
public class GemfireAdapter implements DataSourceAdapter {

    private static final Logger logger = LoggerFactory.getLogger(GemfireAdapter.class);

    @Value("${gemfire.locators:localhost[10334]}")
    private String locators;

    @Value("${gemfire.region.name:MarketDataRegion}")
    private String regionName;

    private final AtomicBoolean connected = new AtomicBoolean(false);
    private final AtomicBoolean streaming = new AtomicBoolean(false);
    private final AtomicLong totalFetches = new AtomicLong(0);
    private final AtomicLong failedFetches = new AtomicLong(0);
    private final AtomicLong lastSuccessfulFetch = new AtomicLong(0);

    private ScheduledExecutorService streamingExecutor;
    private DataStreamCallback streamCallback;

    // Simulated cache data
    private final Map<String, MarketDataPoint> simulatedCache = new HashMap<>();
    private final Random random = new Random();

    @Override
    public DataSourceType getSourceType() {
        return DataSourceType.GEMFIRE_CACHE;
    }

    @Override
    public CompletableFuture<Boolean> connect() {
        return CompletableFuture.supplyAsync(() -> {
            try {
                // Simulate connection to Gemfire
                logger.info("Connecting to Gemfire locators: {}", locators);
                
                // Initialize simulated cache with some data
                initializeSimulatedCache();
                
                connected.set(true);
                logger.info("Successfully connected to Gemfire cache");
                return true;

            } catch (Exception e) {
                logger.error("Error connecting to Gemfire", e);
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
            
            if (streamingExecutor != null) {
                streamingExecutor.shutdown();
            }
            
            logger.info("Disconnected from Gemfire cache");
            return true;
        });
    }

    @Override
    public boolean isConnected() {
        return connected.get();
    }

    @Override
    public CompletableFuture<List<MarketDataPoint>> fetchLatestData() {
        return fetchDataForSymbols(List.of("AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"));
    }

    @Override
    public CompletableFuture<List<MarketDataPoint>> fetchDataForSymbols(List<String> symbols) {
        return CompletableFuture.supplyAsync(() -> {
            List<MarketDataPoint> dataPoints = new ArrayList<>();
            totalFetches.incrementAndGet();

            try {
                if (!connected.get()) {
                    throw new IllegalStateException("Not connected to Gemfire");
                }

                for (String symbol : symbols) {
                    MarketDataPoint dataPoint = fetchFromCache(symbol);
                    if (dataPoint != null) {
                        dataPoints.add(dataPoint);
                    }
                }

                if (!dataPoints.isEmpty()) {
                    lastSuccessfulFetch.set(System.currentTimeMillis());
                }

                logger.debug("Fetched {} data points from Gemfire cache", dataPoints.size());
                return dataPoints;

            } catch (Exception e) {
                failedFetches.incrementAndGet();
                logger.error("Error fetching data from Gemfire", e);
                return dataPoints;
            }
        });
    }

    private MarketDataPoint fetchFromCache(String symbol) {
        try {
            // Simulate cache lookup
            MarketDataPoint cachedData = simulatedCache.get(symbol);
            
            if (cachedData != null) {
                // Create a copy with updated timestamp and slight price variation
                MarketDataPoint dataPoint = new MarketDataPoint();
                dataPoint.setSymbol(symbol);
                dataPoint.setSource(DataSourceType.GEMFIRE_CACHE);
                dataPoint.setDataType("cached");
                dataPoint.setTimestamp(LocalDateTime.now());
                dataPoint.setReceivedAt(LocalDateTime.now());

                // Add some random variation to simulate real market movement
                double basePrice = cachedData.getPrice();
                double variation = (random.nextGaussian() * 0.01); // 1% standard deviation
                dataPoint.setPrice(basePrice * (1 + variation));

                double baseVolume = cachedData.getVolume();
                double volumeVariation = (random.nextGaussian() * 0.1); // 10% standard deviation
                dataPoint.setVolume(Math.max(1, baseVolume * (1 + volumeVariation)));

                // Copy payload
                dataPoint.setPayload(new HashMap<>(cachedData.getPayload()));

                return dataPoint;
            }

            return null;

        } catch (Exception e) {
            logger.error("Error fetching data for symbol: {}", symbol, e);
            return null;
        }
    }

    @Override
    public CompletableFuture<Boolean> startStreaming(DataStreamCallback callback) {
        return CompletableFuture.supplyAsync(() -> {
            if (!connected.get()) {
                logger.error("Cannot start streaming: not connected to Gemfire");
                return false;
            }

            streaming.set(true);
            streamCallback = callback;
            
            // Start streaming executor
            streamingExecutor = Executors.newSingleThreadScheduledExecutor();
            
            // Schedule periodic data updates
            streamingExecutor.scheduleAtFixedRate(() -> {
                try {
                    if (streaming.get()) {
                        // Simulate cache updates
                        updateSimulatedCache();
                        
                        // Fetch and stream updated data
                        List<MarketDataPoint> dataPoints = fetchLatestData().get();
                        for (MarketDataPoint dataPoint : dataPoints) {
                            if (streaming.get() && streamCallback != null) {
                                streamCallback.onData(dataPoint);
                            }
                        }
                    }
                } catch (Exception e) {
                    logger.error("Error in Gemfire streaming", e);
                    if (streamCallback != null) {
                        streamCallback.onError(e);
                    }
                }
            }, 0, 5, TimeUnit.SECONDS); // Update every 5 seconds

            logger.info("Started Gemfire cache streaming");
            return true;
        });
    }

    @Override
    public CompletableFuture<Boolean> stopStreaming() {
        return CompletableFuture.supplyAsync(() -> {
            streaming.set(false);
            streamCallback = null;
            
            if (streamingExecutor != null) {
                streamingExecutor.shutdown();
            }
            
            logger.info("Stopped Gemfire cache streaming");
            return true;
        });
    }

    @Override
    public AdapterHealth getHealth() {
        boolean healthy = connected.get() && 
                (System.currentTimeMillis() - lastSuccessfulFetch.get()) < 60000; // 1 minute

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

    private void initializeSimulatedCache() {
        // Initialize with some sample data
        String[] symbols = {"AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"};
        double[] basePrices = {150.0, 2800.0, 300.0, 800.0, 3200.0};
        
        for (int i = 0; i < symbols.length; i++) {
            MarketDataPoint dataPoint = new MarketDataPoint();
            dataPoint.setSymbol(symbols[i]);
            dataPoint.setSource(DataSourceType.GEMFIRE_CACHE);
            dataPoint.setDataType("cached");
            dataPoint.setTimestamp(LocalDateTime.now());
            dataPoint.setPrice(basePrices[i]);
            dataPoint.setVolume(1000000.0 + random.nextInt(5000000));

            Map<String, Object> payload = new HashMap<>();
            payload.put("region", regionName);
            payload.put("cached_at", LocalDateTime.now().toString());
            dataPoint.setPayload(payload);

            simulatedCache.put(symbols[i], dataPoint);
        }
        
        logger.info("Initialized simulated Gemfire cache with {} symbols", symbols.length);
    }

    private void updateSimulatedCache() {
        // Simulate cache updates with small price movements
        for (MarketDataPoint dataPoint : simulatedCache.values()) {
            double currentPrice = dataPoint.getPrice();
            double variation = (random.nextGaussian() * 0.005); // 0.5% standard deviation
            dataPoint.setPrice(currentPrice * (1 + variation));
            dataPoint.setTimestamp(LocalDateTime.now());
        }
    }
}
