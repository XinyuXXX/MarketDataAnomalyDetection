package com.marketdata.common.enums;

public enum AnomalyType {
    MISSING_DATA("missing_data", "Missing Data"),
    PRICE_MOVEMENT("price_movement", "Price Movement"),
    DATA_STALE("data_stale", "Data Stale"),
    VOLUME_SPIKE("volume_spike", "Volume Spike"),
    DATA_QUALITY("data_quality", "Data Quality");

    private final String code;
    private final String description;

    AnomalyType(String code, String description) {
        this.code = code;
        this.description = description;
    }

    public String getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }
}