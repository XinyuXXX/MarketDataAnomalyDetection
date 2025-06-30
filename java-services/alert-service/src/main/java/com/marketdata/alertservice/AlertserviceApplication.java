package com.marketdata.alertservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.kafka.annotation.EnableKafka;

/**
 * Alert Service
 */
@SpringBootApplication
@EnableKafka
public class AlertserviceApplication {
    public static void main(String[] args) {
        SpringApplication.run(AlertserviceApplication.class, args);
    }
}