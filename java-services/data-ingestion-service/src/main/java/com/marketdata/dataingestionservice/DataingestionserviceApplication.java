package com.marketdata.dataingestionservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Data Ingestion Service - Multi-source data ingestion with Apache Pulsar
 */
@SpringBootApplication
public class DataingestionserviceApplication {
    public static void main(String[] args) {
        SpringApplication.run(DataingestionserviceApplication.class, args);
    }
}