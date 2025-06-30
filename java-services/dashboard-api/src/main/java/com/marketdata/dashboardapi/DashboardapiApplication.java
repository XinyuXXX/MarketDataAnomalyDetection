package com.marketdata.dashboardapi;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.kafka.annotation.EnableKafka;

/**
 * Dashboard API Service
 */
@SpringBootApplication
@EnableKafka
public class DashboardapiApplication {
    public static void main(String[] args) {
        SpringApplication.run(DashboardapiApplication.class, args);
    }
}