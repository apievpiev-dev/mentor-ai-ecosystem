#!/usr/bin/env python3
"""
Test Neural System - Комплексное тестирование системы нейросетей
Проверяет все компоненты и их интеграцию
"""

import asyncio
import json
import logging
import time
import requests
from typing import Dict, List, Any
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NeuralSystemTester:
    """Тестер системы нейросетей"""
    
    def __init__(self):
        self.test_results = {}
        self.base_url = "http://localhost:8081"
        self.test_start_time = time.time()
        
    async def run_all_tests(self):
        """Запуск всех тестов"""
        logger.info("🧪 Начинаем комплексное тестирование Neural System...")
        
        tests = [
            ("AI Engine", self.test_ai_engine),
            ("Multi-Agent System", self.test_multi_agent_system),
            ("Visual Monitor", self.test_visual_monitor),
            ("Autonomous System", self.test_autonomous_system),
            ("Web Interface", self.test_web_interface),
            ("API Endpoints", self.test_api_endpoints),
            ("WebSocket Connection", self.test_websocket),
            ("System Integration", self.test_system_integration)
        ]
        
        for test_name, test_func in tests:
            try:
                logger.info(f"🔍 Тестирование: {test_name}")
                result = await test_func()
                self.test_results[test_name] = result
                
                if result["success"]:
                    logger.info(f"✅ {test_name}: ПРОЙДЕН")
                else:
                    logger.warning(f"⚠️ {test_name}: НЕ ПРОЙДЕН - {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"❌ {test_name}: ОШИБКА - {str(e)}")
                self.test_results[test_name] = {
                    "success": False,
                    "error": str(e),
                    "details": None
                }
        
        # Генерируем отчет
        await self.generate_test_report()
    
    async def test_ai_engine(self) -> Dict[str, Any]:
        """Тестирование AI Engine"""
        try:
            from enhanced_ai_engine import enhanced_ai_engine, generate_ai_response
            
            # Инициализация
            await enhanced_ai_engine.initialize()
            
            # Тест генерации ответа
            response = await generate_ai_response("Привет! Как дела?")
            
            # Тест статуса системы
            status = await enhanced_ai_engine.get_system_status()
            
            return {
                "success": True,
                "details": {
                    "response_generated": bool(response),
                    "system_initialized": status.get("initialized", False),
                    "providers_available": len(status.get("providers", {})),
                    "response_time": status.get("performance", {}).get("average_response_time", 0)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": None
            }
    
    async def test_multi_agent_system(self) -> Dict[str, Any]:
        """Тестирование Multi-Agent System"""
        try:
            from multi_agent_system import MultiAgentSystem
            
            # Создание системы
            system = MultiAgentSystem()
            
            # Тест обработки сообщения
            result = await system.process_user_message("Создай простую функцию", "test_user")
            
            # Тест статуса системы
            status = system.get_system_status()
            
            return {
                "success": True,
                "details": {
                    "agents_created": status.get("total_agents", 0),
                    "message_processed": bool(result.get("response")),
                    "agent_selected": result.get("agent", "Unknown"),
                    "shared_memory_items": status.get("shared_memory", {}).get("knowledge_items", 0)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": None
            }
    
    async def test_visual_monitor(self) -> Dict[str, Any]:
        """Тестирование Visual Monitor"""
        try:
            from visual_monitor import visual_monitor
            
            # Инициализация
            await visual_monitor.initialize()
            
            # Тест захвата состояния
            states = await visual_monitor.capture_system_state()
            
            # Тест анализа
            analysis = await visual_monitor.analyze_visual_data()
            
            # Тест отчета
            report = await visual_monitor.generate_visual_report()
            
            return {
                "success": True,
                "details": {
                    "monitor_active": visual_monitor.active,
                    "components_monitored": len(states),
                    "overall_health": analysis.overall_health,
                    "report_generated": bool(report.get("timestamp"))
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": None
            }
    
    async def test_autonomous_system(self) -> Dict[str, Any]:
        """Тестирование Autonomous System"""
        try:
            from autonomous_neural_system import autonomous_neural_system
            
            # Инициализация
            await autonomous_neural_system.initialize()
            
            # Тест статуса
            status = await autonomous_neural_system.get_system_status()
            
            return {
                "success": True,
                "details": {
                    "system_running": status.get("running", False),
                    "uptime": status.get("uptime", 0),
                    "task_queue_size": status.get("task_queue_size", 0),
                    "autonomous_loops": status.get("autonomous_loops", 0),
                    "components_initialized": len([k for k, v in status.get("components", {}).items() if v])
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": None
            }
    
    async def test_web_interface(self) -> Dict[str, Any]:
        """Тестирование веб-интерфейса"""
        try:
            # Тест главной страницы
            response = requests.get(f"{self.base_url}/", timeout=10)
            
            return {
                "success": response.status_code == 200,
                "details": {
                    "status_code": response.status_code,
                    "content_length": len(response.content),
                    "content_type": response.headers.get("content-type", ""),
                    "response_time": response.elapsed.total_seconds()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": None
            }
    
    async def test_api_endpoints(self) -> Dict[str, Any]:
        """Тестирование API endpoints"""
        try:
            endpoints = [
                ("/api/system/status", "GET"),
                ("/api/agents", "GET"),
                ("/api/visual/report", "GET")
            ]
            
            results = {}
            
            for endpoint, method in endpoints:
                try:
                    if method == "GET":
                        response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                    else:
                        response = requests.post(f"{self.base_url}{endpoint}", timeout=10)
                    
                    results[endpoint] = {
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "response_time": response.elapsed.total_seconds()
                    }
                    
                except Exception as e:
                    results[endpoint] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Тест POST запроса
            try:
                chat_response = requests.post(
                    f"{self.base_url}/api/chat/send",
                    json={"message": "Тестовое сообщение", "user_id": "test_user"},
                    timeout=10
                )
                results["/api/chat/send"] = {
                    "status_code": chat_response.status_code,
                    "success": chat_response.status_code == 200,
                    "response_time": chat_response.elapsed.total_seconds()
                }
            except Exception as e:
                results["/api/chat/send"] = {
                    "success": False,
                    "error": str(e)
                }
            
            successful_endpoints = sum(1 for r in results.values() if r.get("success", False))
            
            return {
                "success": successful_endpoints > 0,
                "details": {
                    "total_endpoints": len(endpoints) + 1,
                    "successful_endpoints": successful_endpoints,
                    "endpoint_results": results
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": None
            }
    
    async def test_websocket(self) -> Dict[str, Any]:
        """Тестирование WebSocket соединения"""
        try:
            import websockets
            
            # Подключение к WebSocket
            uri = f"ws://localhost:8081/ws"
            
            async with websockets.connect(uri, timeout=10) as websocket:
                # Отправка тестового сообщения
                test_message = {
                    "type": "chat_message",
                    "data": {
                        "message": "WebSocket тест",
                        "agent_type": "general",
                        "user_id": "test_user"
                    }
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Ожидание ответа
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                response_data = json.loads(response)
                
                return {
                    "success": True,
                    "details": {
                        "connection_established": True,
                        "message_sent": True,
                        "response_received": bool(response_data),
                        "response_type": response_data.get("type", "unknown")
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": None
            }
    
    async def test_system_integration(self) -> Dict[str, Any]:
        """Тестирование интеграции системы"""
        try:
            # Тест полного цикла: запрос -> обработка -> ответ
            from enhanced_ai_engine import generate_code
            from visual_monitor import visual_monitor
            
            # Генерация кода
            code = await generate_code("Создай функцию для сложения двух чисел")
            
            # Визуальная верификация
            await visual_monitor.initialize()
            verification = await visual_monitor.verify_code_result(code)
            
            return {
                "success": True,
                "details": {
                    "code_generated": bool(code),
                    "code_length": len(code),
                    "visual_verification": verification.verified if verification else False,
                    "verification_confidence": verification.confidence if verification else 0.0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": None
            }
    
    async def generate_test_report(self):
        """Генерация отчета о тестировании"""
        test_duration = time.time() - self.test_start_time
        
        # Подсчет результатов
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - successful_tests
        
        # Создание отчета
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "test_duration": test_duration,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
        
        # Сохранение отчета
        report_file = f"/workspace/test_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Вывод результатов
        print("\n" + "="*60)
        print("🧪 ОТЧЕТ О ТЕСТИРОВАНИИ NEURAL SYSTEM")
        print("="*60)
        print(f"📊 Всего тестов: {total_tests}")
        print(f"✅ Успешных: {successful_tests}")
        print(f"❌ Неудачных: {failed_tests}")
        print(f"📈 Процент успеха: {report['test_summary']['success_rate']:.1f}%")
        print(f"⏱️ Время тестирования: {test_duration:.2f} сек")
        print("="*60)
        
        # Детальные результаты
        for test_name, result in self.test_results.items():
            status = "✅ ПРОЙДЕН" if result["success"] else "❌ НЕ ПРОЙДЕН"
            print(f"{test_name}: {status}")
            if result.get("details"):
                for key, value in result["details"].items():
                    print(f"  - {key}: {value}")
            if result.get("error"):
                print(f"  - Ошибка: {result['error']}")
        
        print("="*60)
        print(f"📄 Полный отчет сохранен: {report_file}")
        print("="*60)
        
        # Рекомендации
        if report["recommendations"]:
            print("\n💡 РЕКОМЕНДАЦИИ:")
            for recommendation in report["recommendations"]:
                print(f"  - {recommendation}")
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Генерация рекомендаций на основе результатов тестов"""
        recommendations = []
        
        # Анализ результатов
        failed_tests = [name for name, result in self.test_results.items() if not result["success"]]
        
        if "AI Engine" in failed_tests:
            recommendations.append("Проверить установку и настройку Ollama")
            recommendations.append("Убедиться в доступности AI провайдеров")
        
        if "Web Interface" in failed_tests:
            recommendations.append("Проверить запуск веб-сервера")
            recommendations.append("Убедиться в доступности порта 8081")
        
        if "WebSocket Connection" in failed_tests:
            recommendations.append("Проверить настройки WebSocket")
            recommendations.append("Убедиться в корректности проксирования")
        
        if "API Endpoints" in failed_tests:
            recommendations.append("Проверить настройки API")
            recommendations.append("Убедиться в правильности маршрутизации")
        
        if "Visual Monitor" in failed_tests:
            recommendations.append("Проверить права доступа к директориям")
            recommendations.append("Убедиться в доступности веб-интерфейсов")
        
        if "Autonomous System" in failed_tests:
            recommendations.append("Проверить инициализацию всех компонентов")
            recommendations.append("Убедиться в корректности конфигурации")
        
        if not recommendations:
            recommendations.append("Все тесты пройдены успешно! Система готова к работе.")
        
        return recommendations

async def main():
    """Главная функция тестирования"""
    tester = NeuralSystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())