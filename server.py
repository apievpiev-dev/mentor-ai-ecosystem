from fastapi import FastAPI
from reports import build_report
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/ctr")
def get_ctr(limit: int = 10, days: int = 30):
    try:
        result = build_report(days=days, limit=limit, return_data=True)
        return JSONResponse(content=result)
    except Exception as e:
        return {"error": str(e)}

