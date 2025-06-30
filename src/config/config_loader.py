"""
Configuration loader for YAML-based configurations
"""

import yaml
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

from src.models.data_models import DataSourceConfig, DataSourceType, DataType, AlertRule, AnomalyType, Severity


logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and manages YAML-based configurations"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._data_sources_config = None
        self._detection_rules_config = None
        self._alert_rules_config = None
    
    def load_data_sources(self) -> List[DataSourceConfig]:
        """Load data source configurations from YAML"""
        try:
            config_file = self.config_dir / "data_sources.yaml"
            
            if not config_file.exists():
                logger.warning(f"Data sources config file not found: {config_file}")
                return []
            
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            self._data_sources_config = config_data
            data_sources = []
            
            for ds_config in config_data.get('data_sources', []):
                try:
                    # Parse data source type
                    ds_type = DataSourceType(ds_config['type'])
                    
                    # Parse expected data types
                    expected_data_types = []
                    for dt in ds_config.get('expected_data_types', []):
                        try:
                            expected_data_types.append(DataType(dt))
                        except ValueError:
                            logger.warning(f"Unknown data type: {dt}")
                    
                    # Create DataSourceConfig
                    data_source = DataSourceConfig(
                        name=ds_config['name'],
                        type=ds_type,
                        connection_params=ds_config.get('connection_params', {}),
                        expected_symbols=ds_config.get('expected_symbols', []),
                        expected_data_types=expected_data_types,
                        update_frequency_minutes=ds_config.get('update_frequency_minutes', 1),
                        market_open_time=ds_config.get('market_open_time', '09:30'),
                        market_close_time=ds_config.get('market_close_time', '16:00'),
                        timezone=ds_config.get('timezone', 'US/Eastern'),
                        enable_missing_data_detection=ds_config.get('detection_settings', {}).get('enable_missing_data_detection', True),
                        enable_price_movement_detection=ds_config.get('detection_settings', {}).get('enable_price_movement_detection', True),
                        enable_stale_data_detection=ds_config.get('detection_settings', {}).get('enable_stale_data_detection', True),
                        missing_data_threshold_minutes=ds_config.get('detection_settings', {}).get('missing_data_threshold_minutes'),
                        price_movement_threshold_percent=ds_config.get('detection_settings', {}).get('price_movement_threshold_percent'),
                        stale_data_threshold_minutes=ds_config.get('detection_settings', {}).get('stale_data_threshold_minutes')
                    )
                    
                    data_sources.append(data_source)
                    logger.info(f"Loaded data source config: {data_source.name}")
                    
                except Exception as e:
                    logger.error(f"Error parsing data source config {ds_config.get('name', 'unknown')}: {e}")
                    continue
            
            return data_sources
            
        except Exception as e:
            logger.error(f"Error loading data sources configuration: {e}")
            return []
    
    def load_detection_rules(self) -> Dict[str, Any]:
        """Load detection rules configuration from YAML"""
        try:
            config_file = self.config_dir / "detection_rules.yaml"
            
            if not config_file.exists():
                logger.warning(f"Detection rules config file not found: {config_file}")
                return {}
            
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            self._detection_rules_config = config_data
            logger.info("Loaded detection rules configuration")
            return config_data
            
        except Exception as e:
            logger.error(f"Error loading detection rules configuration: {e}")
            return {}
    
    def load_alert_rules(self) -> List[AlertRule]:
        """Load alert rules configuration from YAML"""
        try:
            config_file = self.config_dir / "alert_rules.yaml"
            
            if not config_file.exists():
                logger.warning(f"Alert rules config file not found: {config_file}")
                return []
            
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            self._alert_rules_config = config_data
            alert_rules = []
            
            for rule_config in config_data.get('alert_rules', []):
                try:
                    # Parse anomaly types
                    anomaly_types = []
                    for at in rule_config.get('anomaly_types', []):
                        try:
                            anomaly_types.append(AnomalyType(at))
                        except ValueError:
                            logger.warning(f"Unknown anomaly type: {at}")
                    
                    # Parse severity
                    min_severity = Severity.MEDIUM
                    try:
                        min_severity = Severity(rule_config.get('min_severity', 'medium'))
                    except ValueError:
                        logger.warning(f"Unknown severity: {rule_config.get('min_severity')}")
                    
                    # Create AlertRule
                    alert_rule = AlertRule(
                        name=rule_config['name'],
                        description=rule_config.get('description', ''),
                        symbols=rule_config.get('symbols', []),
                        data_sources=[DataSourceType(ds) for ds in rule_config.get('data_sources', [])],
                        anomaly_types=anomaly_types,
                        min_severity=min_severity,
                        email_recipients=rule_config.get('email_recipients', []),
                        sms_recipients=rule_config.get('sms_recipients', []),
                        webhook_urls=rule_config.get('webhook_urls', []),
                        active_hours_start=rule_config.get('active_hours_start', '00:00'),
                        active_hours_end=rule_config.get('active_hours_end', '23:59'),
                        timezone=rule_config.get('timezone', 'US/Eastern'),
                        max_alerts_per_hour=rule_config.get('max_alerts_per_hour', 10),
                        cooldown_minutes=rule_config.get('cooldown_minutes', 15),
                        enabled=rule_config.get('enabled', True)
                    )
                    
                    alert_rules.append(alert_rule)
                    logger.info(f"Loaded alert rule: {alert_rule.name}")
                    
                except Exception as e:
                    logger.error(f"Error parsing alert rule {rule_config.get('name', 'unknown')}: {e}")
                    continue
            
            return alert_rules
            
        except Exception as e:
            logger.error(f"Error loading alert rules configuration: {e}")
            return []
    
    def get_detection_rule_config(self, rule_type: str, rule_name: str) -> Optional[Dict[str, Any]]:
        """Get specific detection rule configuration"""
        if not self._detection_rules_config:
            self.load_detection_rules()
        
        if not self._detection_rules_config:
            return None
        
        rules = self._detection_rules_config.get('detection_rules', {}).get(rule_type, [])
        
        for rule in rules:
            if rule.get('name') == rule_name:
                return rule
        
        return None
    
    def get_global_settings(self) -> Dict[str, Any]:
        """Get global detection settings"""
        if not self._detection_rules_config:
            self.load_detection_rules()
        
        return self._detection_rules_config.get('global_settings', {})
    
    def reload_configurations(self) -> bool:
        """Reload all configurations"""
        try:
            logger.info("Reloading all configurations...")
            
            self._data_sources_config = None
            self._detection_rules_config = None
            self._alert_rules_config = None
            
            # Reload all configs
            self.load_data_sources()
            self.load_detection_rules()
            self.load_alert_rules()
            
            logger.info("All configurations reloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error reloading configurations: {e}")
            return False
    
    def validate_configuration(self) -> Dict[str, List[str]]:
        """Validate all configurations and return any errors"""
        errors = {
            'data_sources': [],
            'detection_rules': [],
            'alert_rules': []
        }
        
        try:
            # Validate data sources
            data_sources = self.load_data_sources()
            if not data_sources:
                errors['data_sources'].append("No data sources configured")
            
            # Check for duplicate names
            names = [ds.name for ds in data_sources]
            if len(names) != len(set(names)):
                errors['data_sources'].append("Duplicate data source names found")
            
            # Validate detection rules
            detection_rules = self.load_detection_rules()
            if not detection_rules:
                errors['detection_rules'].append("No detection rules configured")
            
            # Validate alert rules
            alert_rules = self.load_alert_rules()
            if not alert_rules:
                errors['alert_rules'].append("No alert rules configured")
            
        except Exception as e:
            errors['general'] = [f"Configuration validation error: {e}"]
        
        return errors
