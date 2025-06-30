package com.marketdata.common.enums;

public enum DataSourceType {
    GEMFIRE_CACHE("gemfire", "Gemfire Cache"),
    EOD_DATA("eod", "End of Day Data"),
    MSSQL("mssql", "Microsoft SQL Server"),
    HBASE("hbase", "Apache HBase");

    private final String code;
    private final String description;

    DataSourceType(String code, String description) {
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