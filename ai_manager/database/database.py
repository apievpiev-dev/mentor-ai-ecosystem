"""
База данных для AI Manager
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# База данных в памяти для демонстрации (можно заменить на PostgreSQL)
DATABASE_URL = "sqlite:///./ai_manager.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class TaskDB(Base):
    """Модель задачи в базе данных"""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    priority = Column(String, nullable=False)
    category = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Метаданные
    metadata_json = Column(JSON, default=dict)
    
    # Результат
    result_json = Column(JSON, default=None)
    error_message = Column(Text, default=None)
    
    # Связанный агент
    agent_id = Column(String, default=None)
    
    # Анализ задачи
    analysis_json = Column(JSON, default=None)
    
    # Время выполнения
    execution_time = Column(Float, default=None)


class AgentDB(Base):
    """Модель агента в базе данных"""
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="idle")
    
    # Описание
    description = Column(Text, default="")
    capabilities_json = Column(JSON, default=list)
    
    # Системный промпт
    system_prompt = Column(Text, nullable=False)
    
    # Конфигурация
    config_json = Column(JSON, default=dict)
    
    # Статистика
    tasks_completed = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    total_execution_time = Column(Float, default=0.0)
    average_quality_score = Column(Float, default=0.0)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Текущая задача
    current_task_id = Column(String, default=None)
    
    # История задач
    task_history_json = Column(JSON, default=list)
    
    # Метрики производительности
    performance_metrics_json = Column(JSON, default=dict)


class TaskResultDB(Base):
    """Модель результата задачи в базе данных"""
    __tablename__ = "task_results"

    id = Column(String, primary_key=True, index=True)
    task_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    result_data_json = Column(JSON, nullable=False)
    execution_time = Column(Float, nullable=False)
    agent_id = Column(String, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    quality_score = Column(Float, default=None)
    feedback = Column(Text, default=None)


class SystemLogDB(Base):
    """Модель системного лога"""
    __tablename__ = "system_logs"

    id = Column(String, primary_key=True, index=True)
    level = Column(String, nullable=False)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    component = Column(String, nullable=False)  # task_analyzer, ai_manager, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, default=dict)


class DatabaseManager:
    """Менеджер базы данных"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    async def init_db(self):
        """Инициализация базы данных"""
        try:
            # Создаем все таблицы
            Base.metadata.create_all(bind=self.engine)
            logger.info("База данных инициализирована успешно")
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def get_db_session(self) -> Session:
        """Получение сессии базы данных"""
        return self.SessionLocal()
    
    async def save_task(self, task_data: dict) -> str:
        """Сохранение задачи в базу данных"""
        db = self.get_db_session()
        try:
            db_task = TaskDB(**task_data)
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            return db_task.id
        except Exception as e:
            logger.error(f"Ошибка сохранения задачи: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def update_task(self, task_id: str, update_data: dict):
        """Обновление задачи в базе данных"""
        db = self.get_db_session()
        try:
            db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
            if not db_task:
                raise ValueError(f"Задача {task_id} не найдена")
            
            for key, value in update_data.items():
                if hasattr(db_task, key):
                    setattr(db_task, key, value)
            
            db_task.updated_at = datetime.utcnow()
            db.commit()
        except Exception as e:
            logger.error(f"Ошибка обновления задачи: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def get_task(self, task_id: str) -> Optional[dict]:
        """Получение задачи из базы данных"""
        db = self.get_db_session()
        try:
            db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
            if not db_task:
                return None
            
            return {
                "id": db_task.id,
                "description": db_task.description,
                "priority": db_task.priority,
                "category": db_task.category,
                "status": db_task.status,
                "created_at": db_task.created_at,
                "updated_at": db_task.updated_at,
                "metadata": db_task.metadata_json or {},
                "result": db_task.result_json,
                "error_message": db_task.error_message,
                "agent_id": db_task.agent_id,
                "analysis": db_task.analysis_json,
                "execution_time": db_task.execution_time
            }
        except Exception as e:
            logger.error(f"Ошибка получения задачи: {e}")
            return None
        finally:
            db.close()
    
    async def save_agent(self, agent_data: dict) -> str:
        """Сохранение агента в базу данных"""
        db = self.get_db_session()
        try:
            db_agent = AgentDB(**agent_data)
            db.add(db_agent)
            db.commit()
            db.refresh(db_agent)
            return db_agent.id
        except Exception as e:
            logger.error(f"Ошибка сохранения агента: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def get_agent(self, agent_id: str) -> Optional[dict]:
        """Получение агента из базы данных"""
        db = self.get_db_session()
        try:
            db_agent = db.query(AgentDB).filter(AgentDB.id == agent_id).first()
            if not db_agent:
                return None
            
            return {
                "id": db_agent.id,
                "name": db_agent.name,
                "type": db_agent.type,
                "status": db_agent.status,
                "description": db_agent.description,
                "capabilities": db_agent.capabilities_json or [],
                "system_prompt": db_agent.system_prompt,
                "config": db_agent.config_json or {},
                "tasks_completed": db_agent.tasks_completed,
                "tasks_failed": db_agent.tasks_failed,
                "total_execution_time": db_agent.total_execution_time,
                "average_quality_score": db_agent.average_quality_score,
                "created_at": db_agent.created_at,
                "last_active": db_agent.last_active,
                "current_task_id": db_agent.current_task_id,
                "task_history": db_agent.task_history_json or [],
                "performance_metrics": db_agent.performance_metrics_json or {}
            }
        except Exception as e:
            logger.error(f"Ошибка получения агента: {e}")
            return None
        finally:
            db.close()
    
    async def save_task_result(self, result_data: dict) -> str:
        """Сохранение результата задачи"""
        db = self.get_db_session()
        try:
            db_result = TaskResultDB(**result_data)
            db.add(db_result)
            db.commit()
            db.refresh(db_result)
            return db_result.id
        except Exception as e:
            logger.error(f"Ошибка сохранения результата задачи: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def log_system_event(self, level: str, message: str, component: str, metadata: dict = None):
        """Логирование системного события"""
        db = self.get_db_session()
        try:
            log_entry = SystemLogDB(
                level=level,
                message=message,
                component=component,
                metadata_json=metadata or {}
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error(f"Ошибка логирования: {e}")
            db.rollback()
        finally:
            db.close()


# Глобальный экземпляр менеджера базы данных
db_manager = DatabaseManager()


async def init_db():
    """Инициализация базы данных"""
    await db_manager.init_db()
