#!/usr/bin/env python3
"""
JARVIS Monitoring System
Система мониторинга и управления автономной системой
"""

import os
import sys
import json
import time
import asyncio
import logging
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
import queue

logger = logging.getLogger(__name__)

@dataclass
class Metric:
    """Метрика системы"""
    name: str
    value: float
    unit: str
    timestamp: str
    threshold_warning: float = 80.0
    threshold_critical: float = 90.0

@dataclass
class Alert:
    """Алерт системы"""
    id: str
    type: str  # warning, critical, info
    message: str
    timestamp: str
    resolved: bool = False
    resolved_at: Optional[str] = None

class JarvisMonitor:
    """Система мониторинга JARVIS"""
    
    def __init__(self, core):
        self.core = core
        self.metrics_history = []
        self.active_alerts = []
        self.alert_history = []
        self.monitoring_enabled = True
        self.alert_queue = queue.Queue()
        
        # Запускаем мониторинг
        self.start_monitoring()
        
    def start_monitoring(self):
        """Запуск системы мониторинга"""
        # Поток сбора метрик
        metrics_thread = threading.Thread(
            target=self.run_metrics_collection,
            daemon=True
        )
        metrics_thread.start()
        
        # Поток обработки алертов
        alerts_thread = threading.Thread(
            target=self.run_alert_processing,
            daemon=True
        )
        alerts_thread.start()
        
        # Поток проверки здоровья системы
        health_thread = threading.Thread(
            target=self.run_health_checks,
            daemon=True
        )
        health_thread.start()
        
        logger.info("📊 Система мониторинга запущена")
    
    def run_metrics_collection(self):
        """Сбор метрик системы"""
        while self.monitoring_enabled:
            try:
                metrics = self.collect_system_metrics()
                
                # Добавляем метрики в историю
                self.metrics_history.extend(metrics)
                
                # Ограничиваем размер истории
                if len(self.metrics_history) > 10000:
                    self.metrics_history = self.metrics_history[-5000:]
                
                # Проверяем пороги и создаем алерты
                self.check_metric_thresholds(metrics)
                
                time.sleep(30)  # Собираем метрики каждые 30 секунд
                
            except Exception as e:
                logger.error(f"Ошибка сбора метрик: {e}")
                time.sleep(60)
    
    def run_alert_processing(self):
        """Обработка алертов"""
        while self.monitoring_enabled:
            try:
                if not self.alert_queue.empty():
                    alert = self.alert_queue.get()
                    self.process_alert(alert)
                
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Ошибка обработки алертов: {e}")
                time.sleep(10)
    
    def run_health_checks(self):
        """Проверка здоровья системы"""
        while self.monitoring_enabled:
            try:
                self.perform_health_checks()
                time.sleep(300)  # Проверяем каждые 5 минут
                
            except Exception as e:
                logger.error(f"Ошибка проверки здоровья: {e}")
                time.sleep(60)
    
    def collect_system_metrics(self) -> List[Metric]:
        """Сбор системных метрик"""
        metrics = []
        timestamp = datetime.now().isoformat()
        
        try:
            # CPU метрики
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(Metric(
                name="cpu_usage",
                value=cpu_percent,
                unit="percent",
                timestamp=timestamp,
                threshold_warning=70,
                threshold_critical=85
            ))
            
            # Метрики памяти
            memory = psutil.virtual_memory()
            metrics.append(Metric(
                name="memory_usage",
                value=memory.percent,
                unit="percent",
                timestamp=timestamp,
                threshold_warning=75,
                threshold_critical=90
            ))
            
            # Метрики диска
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            metrics.append(Metric(
                name="disk_usage",
                value=disk_percent,
                unit="percent",
                timestamp=timestamp,
                threshold_warning=80,
                threshold_critical=95
            ))
            
            # Метрики сети
            network = psutil.net_io_counters()
            metrics.append(Metric(
                name="network_bytes_sent",
                value=network.bytes_sent,
                unit="bytes",
                timestamp=timestamp
            ))
            
            metrics.append(Metric(
                name="network_bytes_recv",
                value=network.bytes_recv,
                unit="bytes",
                timestamp=timestamp
            ))
            
            # Метрики JARVIS
            if self.core:
                metrics.append(Metric(
                    name="jarvis_active_tasks",
                    value=self.core.state.active_tasks,
                    unit="count",
                    timestamp=timestamp,
                    threshold_warning=8,
                    threshold_critical=12
                ))
                
                metrics.append(Metric(
                    name="jarvis_total_instances",
                    value=self.core.state.total_instances,
                    unit="count",
                    timestamp=timestamp
                ))
                
                metrics.append(Metric(
                    name="jarvis_performance_score",
                    value=self.core.state.performance_score * 100,
                    unit="percent",
                    timestamp=timestamp,
                    threshold_warning=60,
                    threshold_critical=40
                ))
            
            # Метрики процессов
            processes = psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])
            jarvis_processes = [p for p in processes if 'jarvis' in p.info['name'].lower() or 'python' in p.info['name'].lower()]
            
            if jarvis_processes:
                total_cpu = sum(p.info['cpu_percent'] for p in jarvis_processes if p.info['cpu_percent'])
                total_memory = sum(p.info['memory_percent'] for p in jarvis_processes if p.info['memory_percent'])
                
                metrics.append(Metric(
                    name="jarvis_process_cpu",
                    value=total_cpu,
                    unit="percent",
                    timestamp=timestamp
                ))
                
                metrics.append(Metric(
                    name="jarvis_process_memory",
                    value=total_memory,
                    unit="percent",
                    timestamp=timestamp
                ))
            
        except Exception as e:
            logger.error(f"Ошибка сбора метрик: {e}")
        
        return metrics
    
    def check_metric_thresholds(self, metrics: List[Metric]):
        """Проверка порогов метрик"""
        for metric in metrics:
            if metric.value > metric.threshold_critical:
                alert = Alert(
                    id=f"critical_{metric.name}_{int(time.time())}",
                    type="critical",
                    message=f"Критическое значение {metric.name}: {metric.value:.1f}{metric.unit}",
                    timestamp=datetime.now().isoformat()
                )
                self.alert_queue.put(alert)
                
            elif metric.value > metric.threshold_warning:
                alert = Alert(
                    id=f"warning_{metric.name}_{int(time.time())}",
                    type="warning",
                    message=f"Предупреждение {metric.name}: {metric.value:.1f}{metric.unit}",
                    timestamp=datetime.now().isoformat()
                )
                self.alert_queue.put(alert)
    
    def process_alert(self, alert: Alert):
        """Обработка алерта"""
        try:
            # Добавляем в активные алерты
            self.active_alerts.append(alert)
            
            # Логируем алерт
            if alert.type == "critical":
                logger.critical(f"🚨 КРИТИЧЕСКИЙ АЛЕРТ: {alert.message}")
            elif alert.type == "warning":
                logger.warning(f"⚠️ ПРЕДУПРЕЖДЕНИЕ: {alert.message}")
            else:
                logger.info(f"ℹ️ ИНФО: {alert.message}")
            
            # Автоматические действия для критических алертов
            if alert.type == "critical":
                self.handle_critical_alert(alert)
            
            # Ограничиваем количество активных алертов
            if len(self.active_alerts) > 100:
                self.active_alerts = self.active_alerts[-50:]
            
            # Добавляем в историю
            self.alert_history.append(alert)
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-500:]
                
        except Exception as e:
            logger.error(f"Ошибка обработки алерта: {e}")
    
    def handle_critical_alert(self, alert: Alert):
        """Обработка критических алертов"""
        try:
            if "cpu_usage" in alert.message:
                # При критической загрузке CPU запускаем репликацию
                if self.core and self.core.replicator:
                    logger.info("🚀 Запуск репликации из-за высокой загрузки CPU")
                    # Запускаем в отдельном потоке
                    import threading
                    def run_replication():
                        try:
                            import asyncio
                            asyncio.run(self.core.replicator.replicate())
                        except Exception as e:
                            logger.error(f"Ошибка репликации: {e}")
                    threading.Thread(target=run_replication, daemon=True).start()
            
            elif "memory_usage" in alert.message:
                # При критическом использовании памяти очищаем кэши
                logger.info("🧹 Очистка кэшей из-за высокой загрузки памяти")
                self.cleanup_memory()
            
            elif "disk_usage" in alert.message:
                # При критическом использовании диска очищаем логи
                logger.info("🗑️ Очистка логов из-за нехватки места на диске")
                self.cleanup_logs()
            
            elif "jarvis_performance_score" in alert.message:
                # При низкой производительности запускаем самоулучшение
                if self.core:
                    logger.info("🔧 Запуск самоулучшения из-за низкой производительности")
                    # Запускаем в отдельном потоке
                    import threading
                    def run_improvement():
                        try:
                            import asyncio
                            asyncio.run(self.core.self_improvement())
                        except Exception as e:
                            logger.error(f"Ошибка самоулучшения: {e}")
                    threading.Thread(target=run_improvement, daemon=True).start()
                    
        except Exception as e:
            logger.error(f"Ошибка обработки критического алерта: {e}")
    
    def cleanup_memory(self):
        """Очистка памяти"""
        try:
            # Очищаем старые метрики
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-500:]
            
            # Очищаем старые алерты
            if len(self.alert_history) > 500:
                self.alert_history = self.alert_history[-250:]
            
            # Принудительная сборка мусора
            import gc
            gc.collect()
            
            logger.info("✅ Очистка памяти выполнена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки памяти: {e}")
    
    def cleanup_logs(self):
        """Очистка логов"""
        try:
            log_files = [
                "/home/mentor/jarvis.log",
                "/home/mentor/server.log",
                "/home/mentor/log.txt"
            ]
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    # Создаем резервную копию
                    backup_file = f"{log_file}.backup"
                    if os.path.getsize(log_file) > 50 * 1024 * 1024:  # 50MB
                        os.rename(log_file, backup_file)
                        logger.info(f"📦 Лог-файл {log_file} архивирован")
            
            logger.info("✅ Очистка логов выполнена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки логов: {e}")
    
    def perform_health_checks(self):
        """Выполнение проверок здоровья"""
        try:
            # Проверяем доступность веб-интерфейса
            try:
                response = requests.get("http://localhost:8080/api/status", timeout=10)
                if response.status_code != 200:
                    alert = Alert(
                        id=f"health_web_interface_{int(time.time())}",
                        type="warning",
                        message="Веб-интерфейс недоступен",
                        timestamp=datetime.now().isoformat()
                    )
                    self.alert_queue.put(alert)
            except:
                alert = Alert(
                    id=f"health_web_interface_{int(time.time())}",
                    type="critical",
                    message="Веб-интерфейс не отвечает",
                    timestamp=datetime.now().isoformat()
                )
                self.alert_queue.put(alert)
            
            # Проверяем доступность Docker
            try:
                if self.core and self.core.replicator:
                    docker_client = self.core.replicator.docker_client
                    docker_client.ping()
            except:
                alert = Alert(
                    id=f"health_docker_{int(time.time())}",
                    type="warning",
                    message="Docker недоступен",
                    timestamp=datetime.now().isoformat()
                )
                self.alert_queue.put(alert)
            
            # Проверяем доступность SSH ключей
            ssh_keys_path = "/home/mentor/.ssh/"
            if not os.path.exists(ssh_keys_path):
                alert = Alert(
                    id=f"health_ssh_keys_{int(time.time())}",
                    type="warning",
                    message="SSH ключи не найдены",
                    timestamp=datetime.now().isoformat()
                )
                self.alert_queue.put(alert)
            
        except Exception as e:
            logger.error(f"Ошибка проверки здоровья: {e}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Получение статуса мониторинга"""
        current_metrics = {}
        
        # Получаем последние метрики
        if self.metrics_history:
            latest_metrics = {}
            for metric in self.metrics_history[-50:]:  # Последние 50 метрик
                latest_metrics[metric.name] = {
                    "value": metric.value,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp
                }
            current_metrics = latest_metrics
        
        return {
            "monitoring_enabled": self.monitoring_enabled,
            "total_metrics_collected": len(self.metrics_history),
            "active_alerts": len(self.active_alerts),
            "total_alerts": len(self.alert_history),
            "current_metrics": current_metrics,
            "active_alerts_list": [asdict(alert) for alert in self.active_alerts[-10:]],
            "recent_alerts": [asdict(alert) for alert in self.alert_history[-20:]]
        }
    
    def resolve_alert(self, alert_id: str):
        """Разрешение алерта"""
        for alert in self.active_alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now().isoformat()
                self.active_alerts.remove(alert)
                logger.info(f"✅ Алерт {alert_id} разрешен")
                return True
        return False
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.monitoring_enabled = False
        logger.info("🛑 Мониторинг остановлен")



JARVIS Monitoring System
Система мониторинга и управления автономной системой
"""

import os
import sys
import json
import time
import asyncio
import logging
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
import queue

logger = logging.getLogger(__name__)

@dataclass
class Metric:
    """Метрика системы"""
    name: str
    value: float
    unit: str
    timestamp: str
    threshold_warning: float = 80.0
    threshold_critical: float = 90.0

@dataclass
class Alert:
    """Алерт системы"""
    id: str
    type: str  # warning, critical, info
    message: str
    timestamp: str
    resolved: bool = False
    resolved_at: Optional[str] = None

class JarvisMonitor:
    """Система мониторинга JARVIS"""
    
    def __init__(self, core):
        self.core = core
        self.metrics_history = []
        self.active_alerts = []
        self.alert_history = []
        self.monitoring_enabled = True
        self.alert_queue = queue.Queue()
        
        # Запускаем мониторинг
        self.start_monitoring()
        
    def start_monitoring(self):
        """Запуск системы мониторинга"""
        # Поток сбора метрик
        metrics_thread = threading.Thread(
            target=self.run_metrics_collection,
            daemon=True
        )
        metrics_thread.start()
        
        # Поток обработки алертов
        alerts_thread = threading.Thread(
            target=self.run_alert_processing,
            daemon=True
        )
        alerts_thread.start()
        
        # Поток проверки здоровья системы
        health_thread = threading.Thread(
            target=self.run_health_checks,
            daemon=True
        )
        health_thread.start()
        
        logger.info("📊 Система мониторинга запущена")
    
    def run_metrics_collection(self):
        """Сбор метрик системы"""
        while self.monitoring_enabled:
            try:
                metrics = self.collect_system_metrics()
                
                # Добавляем метрики в историю
                self.metrics_history.extend(metrics)
                
                # Ограничиваем размер истории
                if len(self.metrics_history) > 10000:
                    self.metrics_history = self.metrics_history[-5000:]
                
                # Проверяем пороги и создаем алерты
                self.check_metric_thresholds(metrics)
                
                time.sleep(30)  # Собираем метрики каждые 30 секунд
                
            except Exception as e:
                logger.error(f"Ошибка сбора метрик: {e}")
                time.sleep(60)
    
    def run_alert_processing(self):
        """Обработка алертов"""
        while self.monitoring_enabled:
            try:
                if not self.alert_queue.empty():
                    alert = self.alert_queue.get()
                    self.process_alert(alert)
                
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Ошибка обработки алертов: {e}")
                time.sleep(10)
    
    def run_health_checks(self):
        """Проверка здоровья системы"""
        while self.monitoring_enabled:
            try:
                self.perform_health_checks()
                time.sleep(300)  # Проверяем каждые 5 минут
                
            except Exception as e:
                logger.error(f"Ошибка проверки здоровья: {e}")
                time.sleep(60)
    
    def collect_system_metrics(self) -> List[Metric]:
        """Сбор системных метрик"""
        metrics = []
        timestamp = datetime.now().isoformat()
        
        try:
            # CPU метрики
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(Metric(
                name="cpu_usage",
                value=cpu_percent,
                unit="percent",
                timestamp=timestamp,
                threshold_warning=70,
                threshold_critical=85
            ))
            
            # Метрики памяти
            memory = psutil.virtual_memory()
            metrics.append(Metric(
                name="memory_usage",
                value=memory.percent,
                unit="percent",
                timestamp=timestamp,
                threshold_warning=75,
                threshold_critical=90
            ))
            
            # Метрики диска
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            metrics.append(Metric(
                name="disk_usage",
                value=disk_percent,
                unit="percent",
                timestamp=timestamp,
                threshold_warning=80,
                threshold_critical=95
            ))
            
            # Метрики сети
            network = psutil.net_io_counters()
            metrics.append(Metric(
                name="network_bytes_sent",
                value=network.bytes_sent,
                unit="bytes",
                timestamp=timestamp
            ))
            
            metrics.append(Metric(
                name="network_bytes_recv",
                value=network.bytes_recv,
                unit="bytes",
                timestamp=timestamp
            ))
            
            # Метрики JARVIS
            if self.core:
                metrics.append(Metric(
                    name="jarvis_active_tasks",
                    value=self.core.state.active_tasks,
                    unit="count",
                    timestamp=timestamp,
                    threshold_warning=8,
                    threshold_critical=12
                ))
                
                metrics.append(Metric(
                    name="jarvis_total_instances",
                    value=self.core.state.total_instances,
                    unit="count",
                    timestamp=timestamp
                ))
                
                metrics.append(Metric(
                    name="jarvis_performance_score",
                    value=self.core.state.performance_score * 100,
                    unit="percent",
                    timestamp=timestamp,
                    threshold_warning=60,
                    threshold_critical=40
                ))
            
            # Метрики процессов
            processes = psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])
            jarvis_processes = [p for p in processes if 'jarvis' in p.info['name'].lower() or 'python' in p.info['name'].lower()]
            
            if jarvis_processes:
                total_cpu = sum(p.info['cpu_percent'] for p in jarvis_processes if p.info['cpu_percent'])
                total_memory = sum(p.info['memory_percent'] for p in jarvis_processes if p.info['memory_percent'])
                
                metrics.append(Metric(
                    name="jarvis_process_cpu",
                    value=total_cpu,
                    unit="percent",
                    timestamp=timestamp
                ))
                
                metrics.append(Metric(
                    name="jarvis_process_memory",
                    value=total_memory,
                    unit="percent",
                    timestamp=timestamp
                ))
            
        except Exception as e:
            logger.error(f"Ошибка сбора метрик: {e}")
        
        return metrics
    
    def check_metric_thresholds(self, metrics: List[Metric]):
        """Проверка порогов метрик"""
        for metric in metrics:
            if metric.value > metric.threshold_critical:
                alert = Alert(
                    id=f"critical_{metric.name}_{int(time.time())}",
                    type="critical",
                    message=f"Критическое значение {metric.name}: {metric.value:.1f}{metric.unit}",
                    timestamp=datetime.now().isoformat()
                )
                self.alert_queue.put(alert)
                
            elif metric.value > metric.threshold_warning:
                alert = Alert(
                    id=f"warning_{metric.name}_{int(time.time())}",
                    type="warning",
                    message=f"Предупреждение {metric.name}: {metric.value:.1f}{metric.unit}",
                    timestamp=datetime.now().isoformat()
                )
                self.alert_queue.put(alert)
    
    def process_alert(self, alert: Alert):
        """Обработка алерта"""
        try:
            # Добавляем в активные алерты
            self.active_alerts.append(alert)
            
            # Логируем алерт
            if alert.type == "critical":
                logger.critical(f"🚨 КРИТИЧЕСКИЙ АЛЕРТ: {alert.message}")
            elif alert.type == "warning":
                logger.warning(f"⚠️ ПРЕДУПРЕЖДЕНИЕ: {alert.message}")
            else:
                logger.info(f"ℹ️ ИНФО: {alert.message}")
            
            # Автоматические действия для критических алертов
            if alert.type == "critical":
                self.handle_critical_alert(alert)
            
            # Ограничиваем количество активных алертов
            if len(self.active_alerts) > 100:
                self.active_alerts = self.active_alerts[-50:]
            
            # Добавляем в историю
            self.alert_history.append(alert)
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-500:]
                
        except Exception as e:
            logger.error(f"Ошибка обработки алерта: {e}")
    
    def handle_critical_alert(self, alert: Alert):
        """Обработка критических алертов"""
        try:
            if "cpu_usage" in alert.message:
                # При критической загрузке CPU запускаем репликацию
                if self.core and self.core.replicator:
                    logger.info("🚀 Запуск репликации из-за высокой загрузки CPU")
                    # Запускаем в отдельном потоке
                    import threading
                    def run_replication():
                        try:
                            import asyncio
                            asyncio.run(self.core.replicator.replicate())
                        except Exception as e:
                            logger.error(f"Ошибка репликации: {e}")
                    threading.Thread(target=run_replication, daemon=True).start()
            
            elif "memory_usage" in alert.message:
                # При критическом использовании памяти очищаем кэши
                logger.info("🧹 Очистка кэшей из-за высокой загрузки памяти")
                self.cleanup_memory()
            
            elif "disk_usage" in alert.message:
                # При критическом использовании диска очищаем логи
                logger.info("🗑️ Очистка логов из-за нехватки места на диске")
                self.cleanup_logs()
            
            elif "jarvis_performance_score" in alert.message:
                # При низкой производительности запускаем самоулучшение
                if self.core:
                    logger.info("🔧 Запуск самоулучшения из-за низкой производительности")
                    # Запускаем в отдельном потоке
                    import threading
                    def run_improvement():
                        try:
                            import asyncio
                            asyncio.run(self.core.self_improvement())
                        except Exception as e:
                            logger.error(f"Ошибка самоулучшения: {e}")
                    threading.Thread(target=run_improvement, daemon=True).start()
                    
        except Exception as e:
            logger.error(f"Ошибка обработки критического алерта: {e}")
    
    def cleanup_memory(self):
        """Очистка памяти"""
        try:
            # Очищаем старые метрики
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-500:]
            
            # Очищаем старые алерты
            if len(self.alert_history) > 500:
                self.alert_history = self.alert_history[-250:]
            
            # Принудительная сборка мусора
            import gc
            gc.collect()
            
            logger.info("✅ Очистка памяти выполнена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки памяти: {e}")
    
    def cleanup_logs(self):
        """Очистка логов"""
        try:
            log_files = [
                "/home/mentor/jarvis.log",
                "/home/mentor/server.log",
                "/home/mentor/log.txt"
            ]
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    # Создаем резервную копию
                    backup_file = f"{log_file}.backup"
                    if os.path.getsize(log_file) > 50 * 1024 * 1024:  # 50MB
                        os.rename(log_file, backup_file)
                        logger.info(f"📦 Лог-файл {log_file} архивирован")
            
            logger.info("✅ Очистка логов выполнена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки логов: {e}")
    
    def perform_health_checks(self):
        """Выполнение проверок здоровья"""
        try:
            # Проверяем доступность веб-интерфейса
            try:
                response = requests.get("http://localhost:8080/api/status", timeout=10)
                if response.status_code != 200:
                    alert = Alert(
                        id=f"health_web_interface_{int(time.time())}",
                        type="warning",
                        message="Веб-интерфейс недоступен",
                        timestamp=datetime.now().isoformat()
                    )
                    self.alert_queue.put(alert)
            except:
                alert = Alert(
                    id=f"health_web_interface_{int(time.time())}",
                    type="critical",
                    message="Веб-интерфейс не отвечает",
                    timestamp=datetime.now().isoformat()
                )
                self.alert_queue.put(alert)
            
            # Проверяем доступность Docker
            try:
                if self.core and self.core.replicator:
                    docker_client = self.core.replicator.docker_client
                    docker_client.ping()
            except:
                alert = Alert(
                    id=f"health_docker_{int(time.time())}",
                    type="warning",
                    message="Docker недоступен",
                    timestamp=datetime.now().isoformat()
                )
                self.alert_queue.put(alert)
            
            # Проверяем доступность SSH ключей
            ssh_keys_path = "/home/mentor/.ssh/"
            if not os.path.exists(ssh_keys_path):
                alert = Alert(
                    id=f"health_ssh_keys_{int(time.time())}",
                    type="warning",
                    message="SSH ключи не найдены",
                    timestamp=datetime.now().isoformat()
                )
                self.alert_queue.put(alert)
            
        except Exception as e:
            logger.error(f"Ошибка проверки здоровья: {e}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Получение статуса мониторинга"""
        current_metrics = {}
        
        # Получаем последние метрики
        if self.metrics_history:
            latest_metrics = {}
            for metric in self.metrics_history[-50:]:  # Последние 50 метрик
                latest_metrics[metric.name] = {
                    "value": metric.value,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp
                }
            current_metrics = latest_metrics
        
        return {
            "monitoring_enabled": self.monitoring_enabled,
            "total_metrics_collected": len(self.metrics_history),
            "active_alerts": len(self.active_alerts),
            "total_alerts": len(self.alert_history),
            "current_metrics": current_metrics,
            "active_alerts_list": [asdict(alert) for alert in self.active_alerts[-10:]],
            "recent_alerts": [asdict(alert) for alert in self.alert_history[-20:]]
        }
    
    def resolve_alert(self, alert_id: str):
        """Разрешение алерта"""
        for alert in self.active_alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now().isoformat()
                self.active_alerts.remove(alert)
                logger.info(f"✅ Алерт {alert_id} разрешен")
                return True
        return False
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.monitoring_enabled = False
        logger.info("🛑 Мониторинг остановлен")