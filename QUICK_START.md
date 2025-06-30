# 🚀 快速开始指南

## 立即体验 (30秒)

```bash
# 运行核心算法演示 (无需任何依赖)
python3 demo.py
```

这将展示：
- ✅ 数据丢失检测
- ✅ 价格波动检测  
- ✅ 实时模拟
- ✅ API接口模拟

## 完整系统部署

### 前置要求
- Java 17+
- Maven 3.6+
- Docker & Docker Compose
- Python 3.9+

### 一键启动
```bash
# 生成代码 + 构建 + 部署 + 测试
./start-system.sh
```

### 手动步骤
```bash
# 1. 生成所有代码
python3 generate-code.py

# 2. 启动基础设施
cd infrastructure && docker-compose up -d

# 3. 构建并启动Java服务
cd java-services
mvn clean package -DskipTests
docker-compose up -d

# 4. 启动Python服务
cd python-services && docker-compose up -d

# 5. 运行测试
python3 run-tests.py
```

## 服务访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| API网关 | http://localhost:8080 | 统一入口 |
| 数据接入 | http://localhost:8081 | 数据源管理 |
| 流处理 | http://localhost:8082 | 实时处理 |
| 告警服务 | http://localhost:8083 | 告警管理 |
| 监控API | http://localhost:8084 | 监控数据 |
| 检测引擎 | http://localhost:8085 | Python算法 |
| Grafana | http://localhost:3000 | 监控面板 |
| Prometheus | http://localhost:9090 | 指标收集 |

## 核心API示例

### 检测缺失数据
```bash
curl -X POST http://localhost:8085/detect/missing-data \
  -H "Content-Type: application/json" \
  -d '[{
    "symbol": "AAPL",
    "timestamp": "2024-01-01T10:00:00",
    "source": "gemfire",
    "data_type": "price",
    "payload": {"price": 150.0},
    "price": 150.0
  }]'
```

### 检测价格异动
```bash
curl -X POST http://localhost:8085/detect/price-movement \
  -H "Content-Type: application/json" \
  -d '[{
    "symbol": "AAPL", 
    "timestamp": "2024-01-01T10:00:00",
    "source": "gemfire",
    "data_type": "price", 
    "payload": {"price": 160.0},
    "price": 160.0
  }]'
```

## 配置说明

### 检测规则配置
编辑 `shared/config/detection_rules.yaml`:
```yaml
missing_data_rules:
  - name: "realtime_data_missing"
    threshold_minutes: 5
    severity: "high"

price_movement_rules:
  - name: "large_price_movement"
    threshold_percent: 5.0
    severity: "high"
```

### 数据源配置
编辑 `shared/config/data_sources.yaml`:
```yaml
data_sources:
  - name: "gemfire_realtime"
    type: "gemfire"
    connection_params:
      locators: "localhost:10334"
    expected_symbols: ["AAPL", "GOOGL"]
```

## 常用命令

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f detection-engine
```

### 重启服务
```bash
# 重启检测引擎
cd python-services && docker-compose restart detection-engine

# 重启API网关
cd java-services && docker-compose restart api-gateway
```

### 停止系统
```bash
# 一键停止
./stop-system.sh

# 或手动停止
cd python-services && docker-compose down
cd java-services && docker-compose down  
cd infrastructure && docker-compose down
```

## 故障排除

### 端口冲突
如果端口被占用，修改各服务的 `docker-compose.yml` 中的端口映射。

### 内存不足
```bash
# 增加Docker内存限制
docker-compose up -d --scale detection-engine=1
```

### 服务启动失败
```bash
# 检查服务状态
docker-compose ps

# 查看详细错误
docker-compose logs [service-name]
```

## 扩展开发

### 添加新的检测算法
1. 在 `python-services/detection-engine/src/algorithms/` 创建新文件
2. 实现检测逻辑
3. 在 `main.py` 中添加API端点

### 添加新的数据源
1. 在 `java-services/data-ingestion-service/` 添加适配器
2. 更新配置文件
3. 重新构建服务

### 自定义告警规则
1. 修改 `shared/config/detection_rules.yaml`
2. 重启相关服务

## 生产部署建议

1. **安全性**: 配置防火墙和SSL证书
2. **监控**: 集成Prometheus和Grafana
3. **备份**: 定期备份配置和数据
4. **扩展**: 根据负载调整服务实例数量

## 获取帮助

- 查看 `PROJECT_SUMMARY.md` 了解系统架构
- 运行 `python3 demo.py` 查看算法演示
- 检查各服务的健康状态: `/health` 端点
