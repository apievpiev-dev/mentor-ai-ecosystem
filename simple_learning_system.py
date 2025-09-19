#!/usr/bin/env python3
"""
Simple Learning System for JARVIS
Упрощенная система обучения для JARVIS без сложных зависимостей
"""

import os
import sys
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import sqlite3

logger = logging.getLogger(__name__)

@dataclass
class LearningEvent:
    """Событие обучения"""
    id: str
    timestamp: str
    event_type: str
    context: Dict[str, Any]
    outcome: Dict[str, Any]
    success: bool
    performance_impact: float

@dataclass
class Pattern:
    """Обнаруженный паттерн"""
    id: str
    pattern_type: str
    description: str
    conditions: Dict[str, Any]
    actions: List[str]
    confidence: float
    usage_count: int
    success_rate: float
    created_at: str

class SimpleLearningDatabase:
    """Простая база данных для обучения"""
    
    def __init__(self, db_path: str = "/workspace/simple_learning.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    event_type TEXT,
                    context TEXT,
                    outcome TEXT,
                    success INTEGER,
                    performance_impact REAL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    id TEXT PRIMARY KEY,
                    pattern_type TEXT,
                    description TEXT,
                    conditions TEXT,
                    actions TEXT,
                    confidence REAL,
                    usage_count INTEGER,
                    success_rate REAL,
                    created_at TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ База данных обучения инициализирована")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации БД: {e}")
    
    def save_event(self, event: LearningEvent):
        """Сохранение события"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO events 
                (id, timestamp, event_type, context, outcome, success, performance_impact)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event.id, event.timestamp, event.event_type,
                json.dumps(event.context), json.dumps(event.outcome),
                1 if event.success else 0, event.performance_impact
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Ошибка сохранения события: {e}")
    
    def get_recent_events(self, hours: int = 24) -> List[LearningEvent]:
        """Получение недавних событий"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute("""
                SELECT * FROM events WHERE timestamp > ? ORDER BY timestamp DESC
            """, (since_time,))
            
            events = []
            for row in cursor.fetchall():
                event = LearningEvent(
                    id=row[0],
                    timestamp=row[1],
                    event_type=row[2],
                    context=json.loads(row[3]),
                    outcome=json.loads(row[4]),
                    success=bool(row[5]),
                    performance_impact=row[6]
                )
                events.append(event)
            
            conn.close()
            return events
            
        except Exception as e:
            logger.error(f"Ошибка получения событий: {e}")
            return []
    
    def save_pattern(self, pattern: Pattern):
        """Сохранение паттерна"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO patterns 
                (id, pattern_type, description, conditions, actions, confidence, 
                 usage_count, success_rate, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.id, pattern.pattern_type, pattern.description,
                json.dumps(pattern.conditions), json.dumps(pattern.actions),
                pattern.confidence, pattern.usage_count, pattern.success_rate,
                pattern.created_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Ошибка сохранения паттерна: {e}")
    
    def get_patterns(self) -> List[Pattern]:
        """Получение всех паттернов"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM patterns ORDER BY confidence DESC")
            
            patterns = []
            for row in cursor.fetchall():
                pattern = Pattern(
                    id=row[0],
                    pattern_type=row[1],
                    description=row[2],
                    conditions=json.loads(row[3]),
                    actions=json.loads(row[4]),
                    confidence=row[5],
                    usage_count=row[6],
                    success_rate=row[7],
                    created_at=row[8]
                )
                patterns.append(pattern)
            
            conn.close()
            return patterns
            
        except Exception as e:
            logger.error(f"Ошибка получения паттернов: {e}")
            return []

class SimpleLearningSystem:
    """Упрощенная система обучения"""
    
    def __init__(self):
        self.db = SimpleLearningDatabase()
        self.enabled = True
        self.patterns_cache = []
        self.learning_stats = {
            "events_processed": 0,
            "patterns_detected": 0,
            "adaptations_applied": 0,
            "success_rate": 0.0
        }
        
        # Запускаем циклы обучения
        self.start_learning_cycles()
        
        logger.info("🧠 Simple Learning System инициализирована")
    
    def start_learning_cycles(self):
        """Запуск циклов обучения"""
        def learning_loop():
            while self.enabled:
                try:
                    # Анализируем события и ищем паттерны
                    self.analyze_and_learn()
                    time.sleep(120)  # Каждые 2 минуты
                except Exception as e:
                    logger.error(f"Ошибка цикла обучения: {e}")
                    time.sleep(300)
        
        threading.Thread(target=learning_loop, daemon=True).start()
        logger.info("🔄 Цикл обучения запущен")
    
    def record_event(self, event_type: str, context: Dict[str, Any], 
                    outcome: Dict[str, Any], success: bool, performance_impact: float = 0.0):
        """Запись события обучения"""
        try:
            event = LearningEvent(
                id=f"{event_type}_{int(time.time())}_{hash(str(context)) % 1000}",
                timestamp=datetime.now().isoformat(),
                event_type=event_type,
                context=context,
                outcome=outcome,
                success=success,
                performance_impact=performance_impact
            )
            
            self.db.save_event(event)
            self.learning_stats["events_processed"] += 1
            
            logger.info(f"📚 Событие записано: {event_type} (успех: {success}, влияние: {performance_impact:+.2f})")
            
        except Exception as e:
            logger.error(f"Ошибка записи события: {e}")
    
    def analyze_and_learn(self):
        """Анализ событий и обучение"""
        try:
            # Получаем недавние события
            events = self.db.get_recent_events(hours=6)
            
            if len(events) < 3:
                return
            
            logger.info(f"🔍 Анализ {len(events)} событий за последние 6 часов")
            
            # Ищем паттерны
            patterns = self.detect_simple_patterns(events)
            
            if patterns:
                logger.info(f"🎯 Обнаружено {len(patterns)} паттернов")
                
                for pattern in patterns:
                    self.db.save_pattern(pattern)
                    self.apply_pattern_learning(pattern)
                    self.learning_stats["patterns_detected"] += 1
            
            # Обновляем статистику успешности
            successful_events = [e for e in events if e.success]
            self.learning_stats["success_rate"] = len(successful_events) / len(events)
            
        except Exception as e:
            logger.error(f"Ошибка анализа и обучения: {e}")
    
    def detect_simple_patterns(self, events: List[LearningEvent]) -> List[Pattern]:
        """Обнаружение простых паттернов"""
        patterns = []
        
        try:
            # Группируем события по типам
            event_groups = defaultdict(list)
            for event in events:
                event_groups[event.event_type].append(event)
            
            # Анализируем каждую группу
            for event_type, type_events in event_groups.items():
                if len(type_events) >= 3:
                    pattern = self.analyze_event_group(event_type, type_events)
                    if pattern:
                        patterns.append(pattern)
            
            # Ищем временные паттерны
            temporal_pattern = self.detect_temporal_pattern(events)
            if temporal_pattern:
                patterns.append(temporal_pattern)
            
            # Ищем паттерны производительности
            performance_pattern = self.detect_performance_pattern(events)
            if performance_pattern:
                patterns.append(performance_pattern)
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения паттернов: {e}")
        
        return patterns
    
    def analyze_event_group(self, event_type: str, events: List[LearningEvent]) -> Optional[Pattern]:
        """Анализ группы событий одного типа"""
        try:
            success_rate = sum(1 for e in events if e.success) / len(events)
            avg_performance = sum(e.performance_impact for e in events) / len(events)
            
            # Если есть четкий паттерн
            if success_rate > 0.8 and avg_performance > 0.05:
                # Успешный паттерн
                pattern = Pattern(
                    id=f"success_{event_type}_{int(time.time())}",
                    pattern_type="success",
                    description=f"Высокая успешность для {event_type}: {success_rate:.1%}",
                    conditions={
                        "event_type": event_type,
                        "min_success_rate": 0.8,
                        "min_performance": 0.05
                    },
                    actions=[
                        f"Приоритизировать задачи типа {event_type}",
                        "Изучить факторы успеха",
                        "Применить аналогичный подход к другим задачам"
                    ],
                    confidence=min(0.9, success_rate),
                    usage_count=0,
                    success_rate=success_rate,
                    created_at=datetime.now().isoformat()
                )
                return pattern
                
            elif success_rate < 0.5 or avg_performance < -0.1:
                # Проблемный паттерн
                pattern = Pattern(
                    id=f"problem_{event_type}_{int(time.time())}",
                    pattern_type="problem",
                    description=f"Низкая успешность для {event_type}: {success_rate:.1%}",
                    conditions={
                        "event_type": event_type,
                        "max_success_rate": 0.5,
                        "max_performance": -0.1
                    },
                    actions=[
                        f"Исследовать причины неудач в {event_type}",
                        "Оптимизировать процесс выполнения",
                        "Добавить дополнительные проверки"
                    ],
                    confidence=min(0.8, 1.0 - success_rate),
                    usage_count=0,
                    success_rate=success_rate,
                    created_at=datetime.now().isoformat()
                )
                return pattern
            
        except Exception as e:
            logger.error(f"Ошибка анализа группы событий: {e}")
        
        return None
    
    def detect_temporal_pattern(self, events: List[LearningEvent]) -> Optional[Pattern]:
        """Обнаружение временного паттерна"""
        try:
            if len(events) < 5:
                return None
            
            # Группируем по часам
            hourly_events = defaultdict(int)
            for event in events:
                hour = datetime.fromisoformat(event.timestamp).hour
                hourly_events[hour] += 1
            
            # Находим пиковые часы
            max_events = max(hourly_events.values()) if hourly_events else 0
            avg_events = sum(hourly_events.values()) / len(hourly_events) if hourly_events else 0
            
            peak_hours = [hour for hour, count in hourly_events.items() if count > avg_events * 1.5]
            
            if peak_hours and max_events > avg_events * 1.5:
                pattern = Pattern(
                    id=f"temporal_{int(time.time())}",
                    pattern_type="temporal",
                    description=f"Пиковая активность в часы: {peak_hours}",
                    conditions={
                        "peak_hours": peak_hours,
                        "peak_threshold": 1.5
                    },
                    actions=[
                        "Планировать ресурсы на пиковые часы",
                        "Оптимизировать производительность в пиковое время",
                        "Избегать обслуживания в пиковые часы"
                    ],
                    confidence=0.7,
                    usage_count=0,
                    success_rate=0.8,
                    created_at=datetime.now().isoformat()
                )
                return pattern
                
        except Exception as e:
            logger.error(f"Ошибка обнаружения временного паттерна: {e}")
        
        return None
    
    def detect_performance_pattern(self, events: List[LearningEvent]) -> Optional[Pattern]:
        """Обнаружение паттерна производительности"""
        try:
            performance_events = [e for e in events if abs(e.performance_impact) > 0.05]
            
            if len(performance_events) < 3:
                return None
            
            # Анализируем тренд производительности
            positive_impact = [e for e in performance_events if e.performance_impact > 0]
            negative_impact = [e for e in performance_events if e.performance_impact < 0]
            
            if len(positive_impact) > len(negative_impact) * 2:
                # Положительный тренд
                avg_improvement = sum(e.performance_impact for e in positive_impact) / len(positive_impact)
                
                pattern = Pattern(
                    id=f"performance_positive_{int(time.time())}",
                    pattern_type="performance_improvement",
                    description=f"Положительный тренд производительности: +{avg_improvement:.2f}",
                    conditions={
                        "positive_events": len(positive_impact),
                        "negative_events": len(negative_impact),
                        "avg_improvement": avg_improvement
                    },
                    actions=[
                        "Продолжить текущую стратегию оптимизации",
                        "Изучить факторы улучшения",
                        "Применить успешные методы к другим компонентам"
                    ],
                    confidence=0.8,
                    usage_count=0,
                    success_rate=0.9,
                    created_at=datetime.now().isoformat()
                )
                return pattern
                
            elif len(negative_impact) > len(positive_impact):
                # Негативный тренд
                avg_degradation = sum(e.performance_impact for e in negative_impact) / len(negative_impact)
                
                pattern = Pattern(
                    id=f"performance_negative_{int(time.time())}",
                    pattern_type="performance_degradation",
                    description=f"Деградация производительности: {avg_degradation:.2f}",
                    conditions={
                        "negative_events": len(negative_impact),
                        "avg_degradation": avg_degradation
                    },
                    actions=[
                        "Исследовать причины деградации",
                        "Откатить недавние изменения",
                        "Усилить мониторинг производительности"
                    ],
                    confidence=0.7,
                    usage_count=0,
                    success_rate=0.6,
                    created_at=datetime.now().isoformat()
                )
                return pattern
                
        except Exception as e:
            logger.error(f"Ошибка обнаружения паттерна производительности: {e}")
        
        return None
    
    def apply_pattern_learning(self, pattern: Pattern):
        """Применение обучения на основе паттерна"""
        try:
            logger.info(f"🎯 Применение обучения: {pattern.description}")
            
            # Простое применение действий
            for action in pattern.actions[:2]:  # Применяем только первые 2 действия
                logger.info(f"  🔧 Действие: {action}")
            
            # Обновляем статистику
            pattern.usage_count += 1
            self.learning_stats["adaptations_applied"] += 1
            
            # Сохраняем обновленный паттерн
            self.db.save_pattern(pattern)
            
        except Exception as e:
            logger.error(f"Ошибка применения обучения: {e}")
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Получение статистики обучения"""
        try:
            # Получаем недавние события
            recent_events = self.db.get_recent_events(hours=24)
            patterns = self.db.get_patterns()
            
            return {
                "events_24h": len(recent_events),
                "success_rate_24h": sum(1 for e in recent_events if e.success) / len(recent_events) if recent_events else 0,
                "avg_performance_impact": sum(e.performance_impact for e in recent_events) / len(recent_events) if recent_events else 0,
                "total_patterns": len(patterns),
                "active_patterns": len([p for p in patterns if p.usage_count > 0]),
                "learning_enabled": self.enabled,
                "stats": self.learning_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {"error": str(e)}

def test_simple_learning():
    """Тестирование простой системы обучения"""
    try:
        logger.info("🧪 Тестирование Simple Learning System")
        
        # Создаем систему
        learning = SimpleLearningSystem()
        
        # Записываем тестовые события
        test_events = [
            ("task_completion", {"task_type": "optimization", "agent": "optimizer"}, {"result": "success"}, True, 0.1),
            ("task_completion", {"task_type": "analysis", "agent": "analyzer"}, {"result": "success"}, True, 0.05),
            ("task_completion", {"task_type": "coordination", "agent": "coordinator"}, {"result": "partial"}, False, -0.02),
            ("visual_analysis", {"elements": 84, "issues": 0}, {"accessibility": 0.3}, True, 0.02),
            ("performance_check", {"cpu": 15.2, "memory": 12.1}, {"status": "good"}, True, 0.01),
            ("task_completion", {"task_type": "optimization", "agent": "optimizer"}, {"result": "success"}, True, 0.12),
            ("error_occurred", {"component": "analyzer", "error_type": "timeout"}, {"recovered": True}, False, -0.05)
        ]
        
        for event_type, context, outcome, success, impact in test_events:
            learning.record_event(event_type, context, outcome, success, impact)
            time.sleep(0.1)
        
        # Ждем анализа
        logger.info("⏳ Ожидание анализа паттернов...")
        time.sleep(3)
        
        # Принудительно запускаем анализ
        learning.analyze_and_learn()
        
        # Получаем статистику
        stats = learning.get_learning_statistics()
        logger.info("📊 Статистика обучения:")
        logger.info(f"  События за 24ч: {stats.get('events_24h', 0)}")
        logger.info(f"  Успешность: {stats.get('success_rate_24h', 0):.1%}")
        logger.info(f"  Влияние на производительность: {stats.get('avg_performance_impact', 0):+.3f}")
        logger.info(f"  Всего паттернов: {stats.get('total_patterns', 0)}")
        logger.info(f"  Активные паттерны: {stats.get('active_patterns', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_simple_learning()