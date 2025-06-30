package com.marketdata.streamprocessingservice.config;

import org.apache.pulsar.client.api.PulsarClient;
import org.apache.pulsar.client.api.PulsarClientException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Pulsar configuration for stream processing
 */
@Configuration
public class PulsarConfig {

    @Value("${pulsar.service.url:pulsar://localhost:6650}")
    private String pulsarServiceUrl;

    @Bean
    public PulsarClient pulsarClient() throws PulsarClientException {
        return PulsarClient.builder()
                .serviceUrl(pulsarServiceUrl)
                .build();
    }
}
