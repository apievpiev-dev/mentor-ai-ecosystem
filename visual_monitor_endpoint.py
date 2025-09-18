#!/usr/bin/env python3
"""
Endpoint для визуального монитора JARVIS
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import os
import glob
import json
from datetime import datetime

app = FastAPI(title="JARVIS Visual Monitor API")

@app.get("/")
async def visual_monitor_dashboard():
    """Панель визуального монитора"""
    try:
        # Находим последний отчет
        report_files = glob.glob("/home/mentor/visual_reports/visual_report_*.html")
        if report_files:
            latest_report = max(report_files, key=os.path.getctime)
            return HTMLResponse(open(latest_report, encoding='utf-8').read())
        else:
            return HTMLResponse("<h1>Отчеты визуального монитора не найдены</h1>")
    except Exception as e:
        return HTMLResponse(f"<h1>Ошибка загрузки отчета: {e}</h1>")

@app.get("/api/reports")
async def get_reports_list():
    """Список всех отчетов"""
    try:
        report_files = glob.glob("/home/mentor/visual_reports/visual_report_*.json")
        reports = []
        
        for report_file in sorted(report_files, key=os.path.getctime, reverse=True):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    reports.append({
                        "filename": os.path.basename(report_file),
                        "timestamp": data.get("timestamp"),
                        "summary": data.get("summary", {})
                    })
            except Exception as e:
                continue
        
        return {"reports": reports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/{filename}")
async def get_report(filename: str):
    """Получить конкретный отчет"""
    try:
        report_path = f"/home/mentor/visual_reports/{filename}"
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise HTTPException(status_code=404, detail="Report not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/screenshots/{filename}")
async def get_screenshot(filename: str):
    """Получить скриншот"""
    try:
        screenshot_path = f"/home/mentor/visual_screenshots/{filename}"
        if os.path.exists(screenshot_path):
            return FileResponse(screenshot_path)
        else:
            raise HTTPException(status_code=404, detail="Screenshot not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
