package com.marketdata.dataingestionservice.adapter;

import com.marketdata.common.dto.MarketDataPoint;
import com.marketdata.common.enums.DataSourceType;

import java.util.List;
import java.util.concurrent.CompletableFuture;

/**
 * Interface for data source adapters
 */
public interface DataSourceAdapter {
    
    /**
     * Get the data source type this adapter handles
     */
    DataSourceType getSourceType();
    
    /**
     * Connect to the data source
     */
    CompletableFuture<Boolean> connect();
    
    /**
     * Disconnect from the data source
     */
    CompletableFuture<Boolean> disconnect();
    
    /**
     * Check if connected to the data source
     */
    boolean isConnected();
    
    /**
     * Fetch latest data from the source
     */
    CompletableFuture<List<MarketDataPoint>> fetchLatestData();
    
    /**
     * Fetch data for specific symbols
     */
    CompletableFuture<List<MarketDataPoint>> fetchDataForSymbols(List<String> symbols);
    
    /**
     * Start real-time data streaming
     */
    CompletableFuture<Boolean> startStreaming(DataStreamCallback callback);
    
    /**
     * Stop real-time data streaming
     */
    CompletableFuture<Boolean> stopStreaming();
    
    /**
     * Get adapter health status
     */
    AdapterHealth getHealth();
    
    /**
     * Callback interface for streaming data
     */
    interface DataStreamCallback {
        void onData(MarketDataPoint dataPoint);
        void onError(Exception error);
        void onConnectionLost();
    }
    
    /**
     * Adapter health information
     */
    class AdapterHealth {
        private boolean healthy;
        private String status;
        private long lastSuccessfulFetch;
        private long totalFetches;
        private long failedFetches;
        
        public AdapterHealth(boolean healthy, String status) {
            this.healthy = healthy;
            this.status = status;
        }
        
        // Getters and setters
        public boolean isHealthy() { return healthy; }
        public void setHealthy(boolean healthy) { this.healthy = healthy; }
        
        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }
        
        public long getLastSuccessfulFetch() { return lastSuccessfulFetch; }
        public void setLastSuccessfulFetch(long lastSuccessfulFetch) { 
            this.lastSuccessfulFetch = lastSuccessfulFetch; 
        }
        
        public long getTotalFetches() { return totalFetches; }
        public void setTotalFetches(long totalFetches) { this.totalFetches = totalFetches; }
        
        public long getFailedFetches() { return failedFetches; }
        public void setFailedFetches(long failedFetches) { this.failedFetches = failedFetches; }
    }
}
