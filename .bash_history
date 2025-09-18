set -e
cd ~/mentor
set -e
cd ~/mentor
nano docker-compose.yml
nano ~/mentor/docker-compose.yml
curl -s -X POST http://localhost:8000/ask   -H 'Content-Type: application/json'   -d '{"prompt":"У тебя есть разрешение на то, чтобы ты сам себя кодил! если есть, напиши что уже сделал? я хочу с тобой общаться в веб чате!"}' | jq .
NANO ~/mentor/docker-compose.yml
set -e
cd ~/mentor
nano docker-compose.yml
nano ~/mentor/docker-compose.yml
curl -s -X POST http://localhost:8000/ask   -H 'Content-Type: application/json'   -d '{"prompt":"У тебя есть разрешение на то, чтобы ты сам себя кодил! если есть, напиши что уже сделал? я хочу с тобой общаться в веб чате!"}' | jq .
NANO ~/mentor/docker-compose.yml
set -e
cd ~/mentor
nano set -e
nano ~/mentor/docker-compose.yml
curl -s -X POST http://localhost:8000/ask   -H 'Content-Type: application/json'   -d '{"prompt":"Открой ~/mentor/docker-compose.yml и под сервисом api добавь bind‑mount тома:       - ./app:/app/app
      - ./workspace:/app/workspace
"}' | jq .
set -e
cd ~/mentor
scp mentor@5.129.198.210:/home/mentor/mentor/docker-compose.yml .\
nano ~/mentor/docker-compose.yml
docker compose up -d --build api
curl -s http://localhost:8000/mission | jq .
curl -s -X POST http://localhost:8000/ask   -H 'Content-Type: application/json'   -d '{"prompt":"Скажи свою миссию кратко","session_id":"smoke"}' | jq .
curl -s -X POST http://localhost:8000/ask   -H 'Content-Type: application/json'   -d '{"prompt":"Скажи какой прогресс относительно конечной точки проекта?"}' | jq .
curl -s -X POST http://localhost:8000/ask   -H 'Content-Type: application/json'   -d '{"prompt":"ты сначало чат подними, чтобы я стобой там общался"}' | jq .
curl -s -X POST http://localhost:8000/ask   -H 'Content-Type: application/json'   -d '{"prompt":"я имею ввиду веб чат, который мы создали"}' | jq .
mkdir -p /home/mentor/mentor/workspace/system
cat >/home/mentor/mentor/audit.sh <<'BASH'
#!/usr/bin/env bash
set -euo pipefail
OUT="/home/mentor/mentor/workspace/system/audit_$(date +%Y%m%d_%H%M).txt"

redact_env() { sed -E 's#(=).*#=\<redacted\>#g'; }

{
echo "=== TIME ==="; date
echo "=== HOST ==="; uname -a; . /etc/os-release; echo "$PRETTY_NAME"
echo "=== RESOURCES ==="; free -h; df -h
echo "=== PORTS ==="; ss -ltnp | awk 'NR==1 || /:(22|5432|8000|3000|11434)/'
echo "=== DOCKER ==="; docker --version; docker compose version || true
echo "=== DOCKER PS ==="; docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
echo "=== DOCKER DISK ==="; docker system df

echo "=== COMPOSE FILE (paths) ==="; ls -la /home/mentor/mentor
echo "=== COMPOSE CONFIG ==="; (cd /home/mentor/mentor && docker compose config) || true

echo "=== .ENV (redacted) ==="
[ -f /home/mentor/mentor/.env ] && cat /home/mentor/mentor/.env | redact_env || echo "no .env"

echo "=== API HEALTH ==="; curl -sS http://127.0.0.1:8000/health || true
echo "=== WEB CHECK ===";  curl -sS -I http://127.0.0.1:3000 || true
echo "=== OLLAMA TAGS ==="; curl -sS http://127.0.0.1:11434/api/tags || true

echo "=== API: versions ==="
docker compose -f /home/mentor/mentor/docker-compose.yml exec -T api python - <<'PY' || true
import platform, sys
vers={}
for m in ["fastapi","uvicorn","psycopg","fastembed","onnxruntime","requests"]:
    try:
        mod=__import__(m); vers[m]=getattr(mod,"__version__", "n/a")
    except Exception as e:
        vers[m]=f"ERR:{e}"
print("python",platform.python_version())
print(vers)
PY



mkdir -p /home/mentor/mentor/workspace/system
cat >/home/mentor/mentor/audit.sh <<'BASH'
set -euo pipefail
OUT="/home/mentor/mentor/workspace/system/audit_$(date +%Y%m%d_%H%M).txt"

redact_env() { sed -E 's#(=).*#=\<redacted\>#g'; }

{
echo "=== TIME ==="; date
echo "=== HOST ==="; uname -a; . /etc/os-release; echo "$PRETTY_NAME"
echo "=== RESOURCES ==="; free -h; df -h
echo "=== PORTS ==="; ss -ltnp | awk 'NR==1 || /:(22|5432|8000|3000|11434)/'
echo "=== DOCKER ==="; docker --version; docker compose version || true
echo "=== DOCKER PS ==="; docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
echo "=== DOCKER DISK ==="; docker system df

echo "=== COMPOSE FILE (paths) ==="; ls -la /home/mentor/mentor
echo "=== COMPOSE CONFIG ==="; (cd /home/mentor/mentor && docker compose config) || true

echo "=== .ENV (redacted) ==="
[ -f /home/mentor/mentor/.env ] && cat /home/mentor/mentor/.env | redact_env || echo "no .env"

echo "=== API HEALTH ==="; curl -sS http://127.0.0.1:8000/health || true
echo "=== WEB CHECK ===";  curl -sS -I http://127.0.0.1:3000 || true
echo "=== OLLAMA TAGS ==="; curl -sS http://127.0.0.1:11434/api/tags || true

echo "=== API: versions ==="
docker compose -f /home/mentor/mentor/docker-compose.yml exec -T api python - <<'PY' || true
import platform, sys
vers={}
for m in ["fastapi","uvicorn","psycopg","fastembed","onnxruntime","requests"]:
    try:
        mod=__import__(m); vers[m]=getattr(mod,"__version__", "n/a")
    except Exception as e:
        vers[m]=f"ERR:{e}"
print("python",platform.python_version())
print(vers)
PY


echo "=== BOT: versions ==="
docker compose -f /home/mentor/mentor/docker-compose.yml exec -T bot python - <<'PY' || true
import platform
mods=["aiogram","psycopg","fastembed","onnxruntime"]
print("python", platform.python_version())
for m in mods:
    try:
        mod=__import__(m); print(m, getattr(mod,"__version__","n/a"))
    except Exception as e:
        print(m, "ERR:", e)
PY

cat > ~/mentor/audit_simple.sh <<'BASH'
echo "=== CONTAINERS ==="
docker compose ps
echo "=== HEALTH API ==="
curl -s http://127.0.0.1:8000/health || echo "api no response"

echo "=== WEB ==="
curl -s -I http://127.0.0.1:3000 | head -n 1 || echo "web no response"

echo "=== OLLAMA ==="
curl -s http://127.0.0.1:11434/api/tags || echo "ollama no response"

echo "=== DB STATUS ==="
docker compose exec -T db psql -U user -d mentor -c "select count(*) from memories;" || echo "db no response"

echo "=== RECENT LOGS bot ==="
docker compose logs --tail=20 bot
BASH

chmod +x ~/mentor/audit_simple.sh
~/mentor/audit_simple.sh
set -e
cd ~/mentor
docker compose exec ollama ollama ps
cd ~/mentor
docker compose ps
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:11434/api/tags | jq -r '.models[].name'
curl -s http://localhost:8000/openapi.json | jq '.paths["/ask/stream"]'
curl -s -X POST http://localhost:11434/api/generate   -d '{"model":"llama3.1:8b","prompt":"warmup","stream":false,"keep_alive":"30m"}' >/dev/null
grep -q '^OLLAMA_URL=' .env || echo 'OLLAMA_URL=http://ollama:11434' >> .env
grep -q '^OLLAMA_MODEL=' .env || echo 'OLLAMA_MODEL=llama3.1:8b' >> .env
grep -q '^OLLAMA_TIMEOUT=' .env && sed -i 's/^OLLAMA_TIMEOUT=.*/OLLAMA_TIMEOUT=60/' .env || echo 'OLLAMA_TIMEOUT=60' >> .env
grep -q '^OLLAMA_RETRIES=' .env && sed -i 's/^OLLAMA_RETRIES=.*/OLLAMA_RETRIES=3/' .env || echo 'OLLAMA_RETRIES=3' >> .env
grep -q '^SMOKE_INTERVAL_S=' .env || echo 'SMOKE_INTERVAL_S=180' >> .env
curl -s -X POST http://localhost:11434/api/generate   -d '{"model":"llama3.1:8b","prompt":"warmup","stream":false,"keep_alive":"30m"}' >/dev/null
sudo docker compose up -d --build api
curl -s -X POST http://localhost:8000/ask   -H 'Content-Type: application/json' -d '{"prompt":"ping","session_id":"smoke"}' | jq .
python3 - <<'PY'
from pathlib import Path, re
p=Path("app/autopilot.py")
s=p.read_text(encoding="utf-8")

# a) используем llm_multi вместо llm
s = s.replace("from app import llm\n", "from app import llm_multi as llm\n")

# b) в _plan() передаём domain='code'
s = re.sub(r"ans\s*=\s*await\s*llm\.chat\(\[", "ans = await llm.chat([", s)
s = re.sub(r"ans\s*=\s*await\s*llm\.chat\(\[(.*?)\]\)", r"ans = await llm.chat([\1], domain='code')", s, flags=re.S)

# c) усилим smoke: добавим синтакс‑чек Python
if "def _smoke()" in s and "py_compile" not in s:
    s = s.replace(
        "async def _smoke()",
        "async def _smoke()"
    ).replace(
        "return res",
        """\
    # синтакс‑проверка всех *.py
    import subprocess, shlex
    try:
        cmd = "bash -lc \"python - <<'EOF'\\nimport py_compile, pathlib, sys\\nerrs=0\\n" \
              "+ \\"\\n\\".join(["for p in pathlib.Path('app').rglob('*.py'):\\n    try: py_compile.compile(str(p), doraise=True)\\n    except Exception as e: print('PYERR',p, e); errs+=1"]) \
              + "\\nprint('PYERR_COUNT',errs)\\nEOF\""
        cp = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/app")
        res["pycheck"] = (cp.returncode==0 and "PYERR_COUNT 0" in (cp.stdout+cp.stderr))
    except Exception as e:
        res["pycheck"] = False
        res["pycheck_err"] = repr(e)
    return res"""
    )

p.write_text(s, encoding="utf-8")
print("autopilot.py patched for code-mode")
PY

python3 - <<'PY'
from pathlib import Path
p=Path("app/main.py"); s=p.read_text(encoding="utf-8")
if '@app.post("/codex/start")' not in s:
    s += '''

@app.post("/codex/start")
async def codex_start(body: dict):
    what = (body.get("what") or "Ускорить и упростить код: рефакторинг, уменьшение латентности, фиксы ошибок")
    iters = int(body.get("iterations") or 3)
    wait_s = int(body.get("wait_s") or 1)
    goal = f"[CODE] {what}. Сформируй ОДИН JSON (explain, commit, changes[].path, changes[].content). Только разрешённые пути. Минимальные безопасные диффы."
    rid = await autopilot.start(goal, session_id="codex", iterations=iters, wait_s=wait_s)
    return {"run_id": rid, "status": "started", "mode": "codex"}
'''
    p.write_text(s, encoding="utf-8")
    print("main.py: /codex/start added")
else:
    print("main.py: codex route exists")
PY

python3 - <<'PY'
from pathlib import Path
p=Path("app/main.py"); s=p.read_text(encoding="utf-8")
if '@app.post("/codex/start")' not in s:
    s += '''

@app.post("/codex/start")
async def codex_start(body: dict):
    what = (body.get("what") or "Ускорить и упростить код: рефакторинг, уменьшение латентности, фиксы ошибок")
    iters = int(body.get("iterations") or 3)
    wait_s = int(body.get("wait_s") or 1)
    goal = f"[CODE] {what}. Сформируй ОДИН JSON (explain, commit, changes[].path, changes[].content). Только разрешённые пути. Минимальные безопасные диффы."
    rid = await autopilot.start(goal, session_id="codex", iterations=iters, wait_s=wait_s)
    return {"run_id": rid, "status": "started", "mode": "codex"}
'''
    p.write_text(s, encoding="utf-8")
    print("main.py: /codex/start added")
else:
    print("main.py: codex route exists")
PY

sudo docker compose up -d --build api
RUN=$(curl -s -X POST http://localhost:8000/codex/start \
  -H 'Content-Type: application/json' \
  -d '{"what":"Снизить таймауты /ask, добавить ретраи, привести код к одному стилю","iterations":3,"wait_s":1}' | jq -r .run_id)
set -e
cd ~/mentor
RUN=$(curl -s -X POST http://localhost:8000/codex/start \
  -H 'Content-Type: application/json' \
  -d '{"what":"Снизить таймауты /ask, добавить ретраи, привести код к одному стилю","iterations":3,"wait_s":1}' | jq -r .run_id)
set -e
cd ~/mentor
curl -sS -X POST http://localhost:8000/codex/start   -H 'Content-Type: application/json'   -d '{"what":"Снизить таймауты /ask, добавить ретраи, привести код к одному стилю","iterations":3,"wait_s":1}'
python3 - <<'PY'
from pathlib import Path
p=Path("app/main.py"); s=p.read_text(encoding="utf-8")
# импорт llm_multi и autopilot
if "from app import history, llm_multi as llm" not in s:
    s=s.replace("from app import history, llm", "from app import history, llm_multi as llm")
if "from app import autopilot" not in s:
    s=s.replace("from app import history", "from app import history\nfrom app import autopilot")
# сам маршрут
block = '''
@app.post("/codex/start")
async def codex_start(body: dict):
    try:
        what = (body.get("what") or "").strip()
        iterations = int(body.get("iterations") or 3)
        wait_s = int(body.get("wait_s") or 1)
        goal = f"[CODE] {what or 'Снизить таймауты /ask, добавить ретраи, унифицировать стиль'}"
        rid = await autopilot.start(goal, session_id="codex", iterations=iterations, wait_s=wait_s)
        return {"run_id": rid, "status": "started", "iterations": iterations}
    except Exception as e:
        return {"error": repr(e)}
'''
if '@app.post("/codex/start")' not in s:
    s = s.rstrip() + "\n\n" + block + "\n"
p.write_text(s, encoding="utf-8")
print("main.py patched")
PY

sudo docker compose up -d --build api
curl -s http://localhost:8000/openapi.json | jq '.paths["/codex/start"]'
RUN=$(curl -sS -X POST http://localhost:8000/codex/start \
  -H 'Content-Type: application/json' \
  -d '{"what":"Снизить таймауты /ask, добавить ретраи, привести код к одному стилю","iterations":3,"wait_s":1}' \
  | jq -r 'try .run_id // empty'); echo "run_id=$RUN"
[ -n "$RUN" ] && tail -f workspace/runs/$RUN/status.jsonl || echo "нет run_id — смотри логи: docker compose logs -n 200 api"
docker compose logs -n 200 api
Источники
set -e
cd ~/mentor
curl -sS -X POST http://localhost:8000/codex/start   -H 'Content-Type: application/json'   -d '{"what":"Снизить таймауты /ask, добавить ретраи, привести код к одному стилю","iterations":3,"wait_s":1}'
python3 - <<'PY'
from pathlib import Path
p=Path("app/main.py"); s=p.read_text(encoding="utf-8")
# импорт llm_multi и autopilot
if "from app import history, llm_multi as llm" not in s:
    s=s.replace("from app import history, llm", "from app import history, llm_multi as llm")
if "from app import autopilot" not in s:
    s=s.replace("from app import history", "from app import history\nfrom app import autopilot")
# сам маршрут
block = '''
@app.post("/codex/start")
async def codex_start(body: dict):
    try:
        what = (body.get("what") or "").strip()
        iterations = int(body.get("iterations") or 3)
        wait_s = int(body.get("wait_s") or 1)
        goal = f"[CODE] {what or 'Снизить таймауты /ask, добавить ретраи, унифицировать стиль'}"
        rid = await autopilot.start(goal, session_id="codex", iterations=iterations, wait_s=wait_s)
        return {"run_id": rid, "status": "started", "iterations": iterations}
    except Exception as e:
        return {"error": repr(e)}
'''
if '@app.post("/codex/start")' not in s:
    s = s.rstrip() + "\n\n" + block + "\n"
p.write_text(s, encoding="utf-8")
print("main.py patched")
PY

sudo docker compose up -d --build api
curl -s http://localhost:8000/openapi.json | jq '.paths["/codex/start"]'
RUN=$(curl -sS -X POST http://localhost:8000/codex/start \
  -H 'Content-Type: application/json' \
  -d '{"what":"Снизить таймауты /ask, добавить ретраи, привести код к одному стилю","iterations":3,"wait_s":1}' \
  | jq -r 'try .run_id // empty'); echo "run_id=$RUN"
[ -n "$RUN" ] && tail -f workspace/runs/$RUN/status.jsonl || echo "нет run_id — смотри логи: docker compose logs -n 200 api"
docker compose logs -n 200 api
Источники
set -e
cd ~/mentor
echo "==[1] API health=="
curl -s http://localhost:8000/health || true
echo "==[2] Смоук /ask=="
curl -s -X POST http://localhost:8000/ask   -H 'Content-Type: application/json'   -d '{"prompt":"ping","session_id":"smoke"}' || true
curl -s -X POST http://localhost:8000/ask   -H 'Content-Type: application/json'   -d '{"prompt":"ping","session_id":"smoke"}' || true
echo "==[2] Смоук /ask=="
curl -s -X POST http://localhost:8000/ask   -H 'Content-Type: application/json'   -d '{"prompt":"ping","session_id":"smoke"}' || true
echo
grep -q '^NEXT_PUBLIC_API_URL=' .env && sed -i 's#^NEXT_PUBLIC_API_URL=.*#NEXT_PUBLIC_API_URL=http://5.129.198.210:8000#' .env || echo 'NEXT_PUBLIC_API_URL=http://5.129.198.210:8000' >> .env
mkdir -p web
cat > web/.env.local <<'ENV'
NEXT_PUBLIC_API_URL=http://5.129.198.210:8000
ENV

sudo docker compose build web
curl -sI http://localhost:3000 | head -n1 || true
curl -N -H 'Accept: text/event-stream' -H 'Content-Type: application/json'   -X POST http://localhost:8000/ask/stream   -d '{"prompt":"ping","session_id":"sse"}' | head -n 10 || true
echo "-- api logs (tail) --";  docker compose logs -n 80 api  || true
echo "-- web logs (tail) --";  docker compose logs -n 80 web  || true
set -e
cd ~/mentor
# 1) Политика: unrestricted=on
mkdir -p workspace/system
cat > workspace/system/policy.json <<'JSON'
{ "unrestricted": true, "notes": "Полный доступ внутри /app. Внешняя сеть разрешена." }
JSON

python3 - <<'PY'
from pathlib import Path, json
p=Path("app/integrations.py")
s=p.read_text(encoding="utf-8")
if "def is_unrestricted(" not in s:
    s += '''

import os, json as _json
def _load_policy():
    try:
        with open("workspace/system/policy.json","r",encoding="utf-8") as f:
            return _json.load(f)
    except Exception:
        return {}
def is_unrestricted() -> bool:
    return bool(_load_policy().get("unrestricted"))

# override checks
def is_allowed(host: str) -> bool:
    if is_unrestricted(): return True
    from urllib.parse import urlparse
    h = (urlparse(host).hostname or host) if "://" in host else host.split("/")[0]
    try:
        with open("workspace/system/integrations.json","r",encoding="utf-8") as f:
            d=_json.load(f)
        return h in d.get("approved",[])
    except Exception:
        return False
'''
    p.write_text(s, encoding="utf-8")
print("integrations.py patched")
PY

set -e
cd ~/mentor
python3 - <<'PY'
from pathlib import Path
import json   # правильный импорт

p = Path("app/integrations.py")
s = p.read_text(encoding="utf-8")

if "def is_unrestricted(" not in s:
    s += '''

import os, json as _json
def _load_policy():
    try:
        with open("workspace/system/policy.json","r",encoding="utf-8") as f:
            return _json.load(f)
    except Exception:
        return {}

def is_unrestricted() -> bool:
    return bool(_load_policy().get("unrestricted"))

# override checks
def is_allowed(host: str) -> bool:
    if is_unrestricted():
        return True
    from urllib.parse import urlparse
    h = (urlparse(host).hostname or host) if "://" in host else host.split("/")[0]
    try:
        with open("workspace/system/integrations.json","r",encoding="utf-8") as f:
            d = _json.load(f)
        return h in d.get("approved",[])
    except Exception:
        return False
'''
    p.write_text(s, encoding="utf-8")

print("integrations.py patched")
PY

sudo docker compose up -d --build api
sudo apt install cockpit -y
sudo systemctl enable --now cockpit
sudo mkdir -p /usr/share/cockpit/mentor-control
tml
set -e
cd ~/mentor
python3 - <<'PY'
from pathlib import Path
import json   # правильный импорт

p = Path("app/integrations.py")
s = p.read_text(encoding="utf-8")

if "def is_unrestricted(" not in s:
    s += '''

import os, json as _json
def _load_policy():
    try:
        with open("workspace/system/policy.json","r",encoding="utf-8") as f:
            return _json.load(f)
    except Exception:
        return {}

def is_unrestricted() -> bool:
    return bool(_load_policy().get("unrestricted"))

# override checks
def is_allowed(host: str) -> bool:
    if is_unrestricted():
        return True
    from urllib.parse import urlparse
    h = (urlparse(host).hostname or host) if "://" in host else host.split("/")[0]
    try:
        with open("workspace/system/integrations.json","r",encoding="utf-8") as f:
            d = _json.load(f)
        return h in d.get("approved",[])
    except Exception:
        return False
'''
    p.write_text(s, encoding="utf-8")

print("integrations.py patched")
PY

sudo docker compose up -d --build api
sudo apt install cockpit -y
sudo systemctl enable --now cockpit
sudo mkdir -p /usr/share/cockpit/mentor-control
tml
set -e
cd ~/mentor
python3 - <<'PY'
from pathlib import Path
p=Path("app/main.py"); s=p.read_text(encoding="utf-8")
if "from app import autopilot" not in s: s=s.replace("from app import history, llm", "from app import history, llm\nfrom app import autopilot")
block = r'''

# --- control from web ---
@app.post("/control/restart/{svc}")
async def control_restart(svc: str):
    import subprocess
    if svc not in ("api","web"): return {"ok": False, "error":"svc must be api|web"}
    p = subprocess.run(f"docker compose restart {svc}", shell=True, capture_output=True, text=True, cwd="/app")
    return {"ok": p.returncode==0, "stdout": p.stdout[-800:], "stderr": p.stderr[-800:]}

@app.post("/control/autopilot/start")
async def control_autopilot_start(body: dict):
    goal = body.get("goal") or "Аудит и ускорение чата: стрим, таймауты, ретраи, сжатие истории"
    it   = int(body.get("iterations") or 3)
    wait = int(body.get("wait_s") or 1)
    rid  = await autopilot.start(goal, session_id="web", iterations=it, wait_s=wait)
    return {"ok": True, "run_id": rid}

@app.get("/control/autopilot/status/{run_id}")
async def control_autopilot_status(run_id: str):
    return autopilot.status(run_id)
'''
if "/control/restart/" not in s:
    s = s.rstrip()+"\n"+block+"\n"
    p.write_text(s, encoding="utf-8")
    print("main.py patched")
else:
    print("main.py already has control routes")
PY

sudo docker compose up -d --build api
cat > ~/mentor/web/lib/admin.ts <<'TS'
const API = process.env.NEXT_PUBLIC_API_URL || (typeof window!=='undefined'
  ? window.location.origin.replace(':3000', ':8000')
  : 'http://localhost:8000');

export async function restartSvc(svc:'api'|'web'){
  const r = await fetch(`${API}/control/restart/${svc}`, {method:'POST'}); return r.json();
}
export async function startAutopilot(goal:string, iterations=3, wait_s=1){
  const r = await fetch(`${API}/control/autopilot/start`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({goal, iterations, wait_s})
  }); return r.json();
}
export async function getRunStatus(run_id:string){
  const r = await fetch(`${API}/control/autopilot/status/${run_id}`); return r.json();
}
TS

cat > ~/mentor/web/lib/admin.ts <<'TS'
const API = process.env.NEXT_PUBLIC_API_URL || (typeof window!=='undefined'
  ? window.location.origin.replace(':3000', ':8000')
  : 'http://localhost:8000');

export async function restartSvc(svc:'api'|'web'){
  const r = await fetch(`${API}/control/restart/${svc}`, {method:'POST'}); return r.json();
}
export async function startAutopilot(goal:string, iterations=3, wait_s=1){
  const r = await fetch(`${API}/control/autopilot/start`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({goal, iterations, wait_s})
  }); return r.json();
}
export async function getRunStatus(run_id:string){
  const r = await fetch(`${API}/control/autopilot/status/${run_id}`); return r.json();
}
TS

python3 - <<'PY'
from pathlib import Path
p=Path('~/mentor/web/app/page.tsx'.replace('~','/home/mentor'))
s=p.read_text(encoding='utf-8')
if "restartSvc(" not in s:
    s=s.replace("import { askOnce, askStream } from '@/lib/api';",
                "import { askOnce, askStream } from '@/lib/api';\nimport { restartSvc, startAutopilot, getRunStatus } from '@/lib/admin';")
    panel = r"""
      <div className="flex gap-2 text-sm">
        <button onClick={async()=>{const r=await restartSvc('api'); alert('API restart: '+(r.ok?'ok':'fail'));}} className="border rounded px-2 py-1">Restart API</button>
        <button onClick={async()=>{const r=await restartSvc('web'); alert('Web restart: '+(r.ok?'ok':'fail'));}} className="border rounded px-2 py-1">Restart Web</button>
        <button onClick={async()=>{const r=await startAutopilot('Аудит/ускорение чата',3,1); if(r.run_id){let s=await getRunStatus(r.run_id); alert('Autopilot run: '+r.run_id+' state='+s.state);} else alert('start fail');}} className="border rounded px-2 py-1">Start Autopilot</button>
      </div>
    """
    s=s.replace("<h1 className=\"text-xl font-semibold\">Mentor Chat</h1>",
                "<h1 className=\"text-xl font-semibold\">Mentor Chat</h1>"+panel)
    p.write_text(s, encoding='utf-8'); print("page.tsx patched with control panel")
else:
    print("page.tsx already has control panel")
PY

python3 - <<'PY'
from pathlib import Path
p=Path('~/mentor/web/app/page.tsx'.replace('~','/home/mentor'))
s=p.read_text(encoding='utf-8')
if "restartSvc(" not in s:
    s=s.replace("import { askOnce, askStream } from '@/lib/api';",
                "import { askOnce, askStream } from '@/lib/api';\nimport { restartSvc, startAutopilot, getRunStatus } from '@/lib/admin';")
    panel = r"""
      <div className="flex gap-2 text-sm">
        <button onClick={async()=>{const r=await restartSvc('api'); alert('API restart: '+(r.ok?'ok':'fail'));}} className="border rounded px-2 py-1">Restart API</button>
        <button onClick={async()=>{const r=await restartSvc('web'); alert('Web restart: '+(r.ok?'ok':'fail'));}} className="border rounded px-2 py-1">Restart Web</button>
        <button onClick={async()=>{const r=await startAutopilot('Аудит/ускорение чата',3,1); if(r.run_id){let s=await getRunStatus(r.run_id); alert('Autopilot run: '+r.run_id+' state='+s.state);} else alert('start fail');}} className="border rounded px-2 py-1">Start Autopilot</button>
      </div>
    """
    s=s.replace("<h1 className=\"text-xl font-semibold\">Mentor Chat</h1>",
                "<h1 className=\"text-xl font-semibold\">Mentor Chat</h1>"+panel)
    p.write_text(s, encoding='utf-8'); print("page.tsx patched with control panel")
else:
    print("page.tsx already has control panel")
PY

cd ~/mentor
# 1) Клиент API для автопилота
cat > web/lib/admin.ts <<'TS'
const API = process.env.NEXT_PUBLIC_API_URL || (typeof window!=='undefined'
  ? window.location.origin.replace(':3000', ':8000')
  : 'http://localhost:8000');

export async function startAutopilot(goal:string, iterations=3, wait_s=1){
  const r = await fetch(`${API}/control/autopilot/start`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({goal, iterations, wait_s})
  });
  return r.json(); // {ok, run_id}
}
export async function getRunStatus(runId:string){
  const r = await fetch(`${API}/runs/${runId}`); return r.json(); // {run_id,state,logs}
}
export async function listRuns(){
  const r = await fetch(`${API}/runs`); return r.json(); // {runs:[]}
}
TS

mkdir -p web/components
cat > web/components/AutopilotPanel.tsx <<'TSX'
'use client';
import { useEffect, useState } from 'react';
import { startAutopilot, getRunStatus, listRuns } from '@/lib/admin';

export default function AutopilotPanel(){
  const [goal,setGoal]=useState('Аудит и ускорение чата: стрим, таймауты, ретраи, сжатие истории');
  const [runId,setRunId]=useState<string>('');
  const [state,setState]=useState<string>('—');
  const [logs,setLogs]=useState<any[]>([]);
  const [runs,setRuns]=useState<string[]>([]);
  const [auto,setAuto]=useState(true);

  async function refreshList(){
    try{ const d=await listRuns(); setRuns(d.runs?.slice(-20)??[]);}catch{}
  }
  async function refreshStatus(id?:string){
    const rid=id||runId; if(!rid) return;
    try{ const d=await getRunStatus(rid); setState(d.state); setLogs(d.logs||[]);}catch{}
  }
  async function onStart(){
    const d=await startAutopilot(goal,3,1);
    if(d.run_id){ setRunId(d.run_id); setState('running'); refreshList(); refreshStatus(d.run_id); }
  }

  useEffect(()=>{ refreshList(); },[]);
  useEffect(()=>{
    if(!auto || !runId) return;
    const t=setInterval(()=>refreshStatus(), 1500);
    return ()=>clearInterval(t);
  },[auto,runId]);

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <input value={goal} onChange={e=>setGoal(e.target.value)}
               className="flex-1 border rounded px-3 py-2" />
        <button onClick={onStart} className="border rounded px-3 py-2">Старт</button>
      </div>

      <div className="flex items-center gap-3 text-sm">
        <div>run_id: <code>{runId||'—'}</code></div>
        <div>state: <b>{state}</b></div>
        <label className="flex items-center gap-1">
          <input type="checkbox" checked={auto} onChange={e=>setAuto(e.target.checked)} />
          автообновление
        </label>
        <button onClick={()=>refreshStatus()} className="border rounded px-2 py-1">Обновить</button>
      </div>

      <div className="text-sm">
        <div className="font-medium mb-1">Прогоны:</div>
        <div className="flex flex-wrap gap-2">
          {runs.map(r=>(
            <button key={r} onClick={()=>{setRunId(r); refreshStatus(r);}}
              className={`px-2 py-1 border rounded ${r===runId?'bg-black text-white':''}`}>
              {r}
            </button>
          ))}
        </div>
      </div>

      <div className="border rounded p-3 h-[45vh] overflow-auto bg-white text-sm">
        {logs.map((l,i)=>(
          <div key={i}><code>{l.ts}</code> — <b>{l.event}</b> {l.state?`(${l.state})`:''}</div>
        ))}
        {!logs.length && <div className="opacity-60">нет логов</div>}
      </div>
    </div>
  );
}
TSX

python3 - <<'PY'
from pathlib import Path
p=Path('web/app/page.tsx'); s=p.read_text(encoding='utf-8')
if "AutopilotPanel" not in s:
    s = s.replace("import { askOnce, askStream } from '@/lib/api';",
                  "import { askOnce, askStream } from '@/lib/api';\nimport AutopilotPanel from '@/components/AutopilotPanel';")
    s = s.replace("export default function Chat()", "export default function Chat()")
    # простой таббар
    header = """
  const [tab,setTab]=useState<'chat'|'auto'>('chat');
"""
    s = s.replace("export default function Chat() {", "export default function Chat() {"+header)
    s = s.replace("<h1 className=\"text-xl font-semibold\">Mentor Chat</h1>",
                  "<h1 className=\"text-xl font-semibold\">Mentor</h1>\n      <div className='flex gap-2 text-sm mb-2'>\n        <button onClick={()=>setTab('chat')} className={`border rounded px-2 py-1 ${'${tab===\\'chat\\'?\"bg-black text-white\":\"\"}'}`}>Chat</button>\n        <button onClick={()=>setTab('auto')} className={`border rounded px-2 py-1 ${'${tab===\\'auto\\'?\"bg-black text-white\":\"\"}'}`}>Autopilot</button>\n      </div>")
    # обернём основной блок условием
    s = s.replace(
      '<div className="border rounded p-3 h-[60vh] overflow-auto bg-white">',
      '{tab==="chat" && (<div className="border rounded p-3 h-[60vh] overflow-auto bg-white">')
    )
    s = s.replace(
      '</div>\n\n      <div className="flex gap-2">',
      '</div>)}\n\n      {tab==="auto" && (\n        <AutopilotPanel />\n      )}\n\n      <div className="flex gap-2">'
    )
    Path('web/app/page.tsx').write_text(s, encoding='utf-8')
    print("page.tsx: tabs added")
else:
    print("page.tsx: tabs already exist")
PY

set -e
cd ~/mentor
docker compose ps
curl -s http://localhost:8000/health || true
curl -sI http://localhost:3000 | head -n 1 || true
mkdir -p web
grep -q '^NEXT_PUBLIC_API_URL=' .env &&   sed -i 's#^NEXT_PUBLIC_API_URL=.*#NEXT_PUBLIC_API_URL=http://5.129.198.210:8000#' .env ||   echo 'NEXT_PUBLIC_API_URL=http://5.129.198.210:8000' >> .env
NEXT_PUBLIC_API_URL=http://5.129.198.210:8000
ENV
set -e
cd ~/mentor
docker compose ps
curl -s http://localhost:8000/health || true
curl -sI http://localhost:3000 | head -n 1 || true
mkdir -p web
grep -q '^NEXT_PUBLIC_API_URL=' .env &&   sed -i 's#^NEXT_PUBLIC_API_URL=.*#NEXT_PUBLIC_API_URL=http://5.129.198.210:8000#' .env ||   echo 'NEXT_PUBLIC_API_URL=http://5.129.198.210:8000' >> .env
NEXT_PUBLIC_API_URL=http://5.129.198.210:8000
ENV
set -e
cd ~/mentor
from google.oauth2 import service_account
set -e
cd ~/mentor
from google.oauth2 import service_account
unzip wb_project.zip
cd wb_project
sudo apt update
sudo apt install unzip -y
unzip wb_project.zip
cd wb_project
ls -lh
sudo cp /root/wb_project.zip ~/
ls -lh
sudo find / -name "wb_project.zip" 2>/dev/null
ssh root@5.129.198.210
cd C:\Users\Marat\Desktop
ls -lh
unzip wb_project.zip
cd wb_project
pip install fastapi uvicorn requests tabulate matplotlib
uvicorn server:app --host 0.0.0.0 --port 8000
sudo apt update
sudo apt install python3 python3-pip -y
pip3 install fastapi uvicorn requests tabulate matplotlib
ls -lh server.py
nano server.py
uvicorn server:app --host 0.0.0.0 --port 8000
pip3 install uvicorn
uvicorn server:app --host 0.0.0.0 --port 8000
sudo apt install python3-pip -y
pip3 install uvicorn
uvicorn server:app --host 0.0.0.0 --port 8000
sudo apt install uvicorn -y
uvicorn server:app --host 0.0.0.0 --port 8000
pip3 install fastapi requests tabulate matplotlib
sudo apt install python3-venv -y
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn requests tabulate matplotlib
uvicorn server:app --host 0.0.0.0 --port 8000
sudo lsof -i :8000
uvicorn server:app --host 0.0.0.0 --port 8080
http://5.129.198.210:8080/ctr
nohup venv/bin/uvicorn server:app --host 0.0.0.0 --port 8080 > log.txt 2>&1 &
df -h
free -h
top
ls -la
whoami
pwd
ss -tuln
netstat -tuln
ps aux | grep python
ps aux | grep docker
sudo lsof -i :11434
ps aux | grep -E 'ollama|python|stable|llama|api|serve'
curl http://localhost:11434
curl http://localhost:3000
curl http://localhost:11434/api/tags
ls -l /var/log/
ls -l ~/myproject/logs
curl http://localhost:11434/api/chat
git clone https://github.com/python/cpython.git
ls
ps aux | grep -E 'python|torch|tensorflow|train|keras'
#!/bin/bash
# filepath: find_nn_processes.sh
echo "Поиск процессов, связанных с нейросетями..."
# Ключевые слова для поиска
KEYWORDS="python|torch|tensorflow|train|keras|pytorch|jupyter|notebook"
# Поиск процессов
ps aux | grep -E "$KEYWORDS" | grep -v grep
echo "Если нужно узнать подробности о конкретном процессе, используйте команду:"
echo "ps -p <PID> -f"
chmod +x find_nn_processes.sh
./find_nn_processes.sh
docker compose ps
docker compose logs -f trainer
docker compose exec trainer ps aux
chmod +x reset_mentor_project.sh
./reset_mentor_project.sh
#!/bin/bash
# filepath: reset_mentor_project.sh
# 1. Остановить все контейнеры Docker
docker compose down || docker-compose down
# 2. Удалить все контейнеры, образы и тома Docker
docker system prune -a --volumes -f
# 3. Удалить директорию проекта (замените путь, если нужно)
rm -rf ~/mentor-coder100
rm -rf ~/MentorCoder100
rm -rf ~/workspace
rm -rf ~/ollama
rm -rf ~/qdrant
rm -rf ~/redis
rm -rf ~/.cache/ollama ~/.ollama ~/.docker
# 4. (Опционально) Очистить логи и временные файлы
rm -rf /tmp/*
echo "Сервер очищен. Можно начинать новый проект."
mkdir mentor-bot
cd mentor-bot
mkdir app web workspace config
echo "# Mentor Bot" > README.md
cat > docker-compose.yml <<EOF
version: '3.8'
services:
  api:
    build: ./app
    ports:
      - "8000:8000"
    volumes:
      - ./workspace:/app/workspace
    restart: unless-stopped

  web:
    build: ./web
    ports:
      - "3000:3000"
    depends_on:
      - api
    restart: unless-stopped
EOF

cat > app/main.py <<EOF
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
EOF

cat > app/Dockerfile <<EOF
FROM python:3.11-slim
WORKDIR /app
COPY main.py .
RUN pip install fastapi uvicorn
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cd mentor-bot
docker compose up -d --build api
docker compose ps
curl http://localhost:8000/health
cd web
npm init next-app@latest . -- --typescript
sudo apt update
node -v
npm -v
npm init next-app@latest . -- --typescript
sudo apt update
sudo apt install -y nodejs npm
node -v
npm -v
npm init next-app@latest . -- --typescript
npm install
npm run build
npm run start
fuser -k 3000/tcp
cd ..
docker compose ps
cd
npm install -g @openai/codex
brew install codex
codex
cd mentor
git init
git add .
git commit -m "Первый коммит: рабочая версия с сервера"
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
ls -la
ssh -v mentor@5.129.198.210
nmap -p 22,8000,80,443 5.129.198.210
ls -la
cd mentor && ls -la
cd mentor
git init
cd /home/mentor/mentor/app && python -c "import main; print('✅ main.py импортируется успешно')"
cd /home/mentor && ls -la | grep venv
source venv/bin/activate && cd mentor/app && pip install -r requirements.txt
source venv/bin/activate && cd mentor/app && python -c "import main; print('✅ main.py импортируется успешно')"
cd /home/mentor && source venv/bin/activate && cd mentor/app && python -c "import main; print('✅ main.py импортируется успешно')"
cd /home/mentor && source venv/bin/activate && cd mentor/app && python switch_provider.py status
cd /home/mentor && source venv/bin/activate && cd mentor/app && timeout 5 uvicorn main:app --host 0.0.0.0 --port 8000 || echo "Сервер запустился успешно (остановлен по таймауту)"
cd /home/mentor && source venv/bin/activate && cd mentor/app && timeout 5 uvicorn main:app --host 0.0.0.0 --port 8001 || echo "Сервер запустился успешно (остановлен по таймауту)"
cd /home/mentor/mentor && ls -la *.md
cd /home/mentor/mentor/app && ls -la *.py | grep -E "(llm_openai|switch_provider|test_openai)"
cd /home/mentor/mentor && ls -la bot.py
cd /home/mentor/mentor && cat bot.py
cd /home/mentor && source venv/bin/activate && cd mentor/app && pip install schedule
cd /home/mentor && source venv/bin/activate && cd mentor/app && python -c "from autonomous_agent import autonomous_agent; print('✅ Автономный агент импортируется успешно')"
cd /home/mentor && source venv/bin/activate && cd mentor/app && python -c "from task_scheduler import task_scheduler; print('✅ Планировщик задач импортируется успешно')"
cd /home/mentor && source venv/bin/activate && cd mentor/app && python -c "import main; print('✅ Обновленный main.py импортируется успешно')"
cd /home/mentor && source venv/bin/activate && cd mentor/app && python -c "
from autonomous_agent import autonomous_agent
task_id = autonomous_agent.create_task('Тестовая задача', 'Описание тестовой задачи', 'code_review')
print(f'✅ Создана задача: {task_id}')
print(f'📊 Всего задач: {len(autonomous_agent.tasks)}')
"
cd /home/mentor && source venv/bin/activate && cd mentor/app && python -c "
from autonomous_agent import autonomous_agent
plan = autonomous_agent.create_daily_plan()
print(f'✅ Создан план на {plan.date}: {len(plan.tasks)} задач')
for i, task in enumerate(plan.tasks, 1):
    print(f'  {i}. {task.title} ({task.priority.name})')
"
source /home/mentor/venv/bin/activate
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
cd /home/mentor && source venv/bin/activate && cd mentor/app && python quick_server.py
cd /home/mentor && source venv/bin/activate && cd mentor/app && python -c "
import asyncio
from wb_personal import wb_personal

async def test_wb():
    print('🔍 Тестирую интеграцию с Wildberries...')
    try:
        result = await wb_personal.analyze_my_business()
        if result.get('error'):
            print(f'❌ Ошибка: {result[\"error\"]}')
        else:
            print('✅ Интеграция работает!')
            products = result.get('products', {})
            print(f'📊 Товаров: {products.get(\"total_products\", 0)}')
            sales = result.get('sales', {})
            print(f'💰 Выручка за 30 дней: {sales.get(\"total_revenue\", 0):.0f} руб.')
    except Exception as e:
        print(f'❌ Ошибка тестирования: {e}')

asyncio.run(test_wb())
"
cd /home/mentor && source venv/bin/activate && pip install --upgrade urllib3 requests
cd /home/mentor && source venv/bin/activate && cd mentor/app && python -c "
import sys
sys.path.append('/home/mentor')
from wb_api import get_cards
print('🔍 Тестирую базовый API Wildberries...')
try:
    cards = get_cards(limit=5)
    if cards:
        print('✅ API работает!')
        print(f'📊 Получено карточек: {len(cards.get(\"cards\", []))}')
    else:
        print('❌ Нет данных')
except Exception as e:
    print(f'❌ Ошибка: {e}')
"
cd /home/mentor && source venv/bin/activate && python --version && python -c "import queue; print(dir(queue))"
cd /home/mentor && source venv/bin/activate && find . -name "queue.py" -o -name "queue.pyc"
cd /home/mentor/mentor/app && mv queue.py roadmap_queue.py
cd /home/mentor && source venv/bin/activate && cd mentor/app && python -c "
import sys
sys.path.append('/home/mentor')
from wb_api import get_cards
print('🔍 Тестирую базовый API Wildberries...')
try:
    cards = get_cards(limit=5)
    if cards:
        print('✅ API работает!')
        print(f'📊 Получено карточек: {len(cards.get(\"cards\", []))}')
    else:
        print('❌ Нет данных')
except Exception as e:
    print(f'❌ Ошибка: {e}')
"
cd /home/mentor && source venv/bin/activate && cd mentor/app && python -c "
import asyncio
import sys
sys.path.append('/home/mentor')
from wb_personal import wb_personal

async def test_wb():
    print('🔍 Тестирую персональную интеграцию с Wildberries...')
    try:
        result = await wb_personal.analyze_my_business()
        if result.get('error'):
            print(f'❌ Ошибка: {result[\"error\"]}')
        else:
            print('✅ Интеграция работает!')
            products = result.get('products', {})
            print(f'📊 Товаров: {products.get(\"total_products\", 0)}')
            sales = result.get('sales', {})
            print(f'💰 Выручка за 30 дней: {sales.get(\"total_revenue\", 0):.0f} руб.')
            recommendations = result.get('recommendations', [])
            print(f'💡 Рекомендаций: {len(recommendations)}')
    except Exception as e:
        print(f'❌ Ошибка тестирования: {e}')

asyncio.run(test_wb())
"
cd /home/mentor && source venv/bin/activate && cd mentor/app && python -c "
import asyncio
import sys
sys.path.append('/home/mentor')
from personal_ai import personal_ai

async def test_ai():
    print('🤖 Тестирую персонального AI...')
    try:
        result = await personal_ai.get_to_know_me()
        if result.get('error'):
            print(f'❌ Ошибка: {result[\"error\"]}')
        else:
            print('✅ AI изучил ваш профиль!')
            print(f'🏢 Тип бизнеса: {result.get(\"business_type\", \"Неизвестно\")}')
            insights = result.get('business_insights', [])
            print(f'💡 Инсайтов: {len(insights)}')
            for insight in insights[:3]:
                print(f'  - {insight}')
    except Exception as e:
        print(f'❌ Ошибка тестирования: {e}')

asyncio.run(test_ai())
"
cd /home/mentor && source venv/bin/activate && cd mentor/app && python -c "
import asyncio
import sys
sys.path.append('/home/mentor')
from business_tasks import business_task_manager

async def test_business():
    print('📋 Тестирую бизнес-задачи...')
    try:
        result = await business_task_manager.create_business_checklist()
        if result.get('error'):
            print(f'❌ Ошибка: {result[\"error\"]}')
        else:
            print('✅ Бизнес-задачи созданы!')
            checklist = result.get('checklist', {})
            items = checklist.get('items', [])
            print(f'📝 Задач в чек-листе: {len(items)}')
            for item in items[:3]:
                print(f'  - {item.get(\"title\", \"Без названия\")}')
    except Exception as e:
        print(f'❌ Ошибка тестирования: {e}')

asyncio.run(test_business())
"
cd /home/mentor && source venv/bin/activate && cd mentor/app && python -c "
import sys
sys.path.append('/home/mentor')
from main import app
print('🚀 Тестирую FastAPI приложение...')
try:
    print('✅ Приложение загружено успешно!')
    print(f'📊 Всего эндпоинтов: {len(app.routes)}')
    
    # Проверяем основные эндпоинты
    endpoints = [route.path for route in app.routes if hasattr(route, 'path')]
    business_endpoints = [ep for ep in endpoints if 'business' in ep or 'personal' in ep or 'wb' in ep]
    print(f'🏢 Бизнес эндпоинтов: {len(business_endpoints)}')
    for ep in business_endpoints[:5]:
        print(f'  - {ep}')
except Exception as e:
    print(f'❌ Ошибка: {e}')
"
sleep 3 && curl -s http://localhost:8001/health
curl -s http://localhost:8001/health | python -m json.tool
echo "🤖 Тестирую персонального AI..." && curl -s -X POST http://localhost:8001/personal/learn | python -m json.tool
echo "📋 Создаю бизнес-задачи..." && curl -s -X POST http://localhost:8001/business/checklist | python -m json.tool
echo "📰 Получаю ежедневный брифинг..." && curl -s http://localhost:8001/personal/briefing | python -m json.tool
echo "🤖 Проверяю автономного агента..." && curl -s http://localhost:8001/autonomous/status | python -m json.tool
echo "🚀 Запускаю автономного агента..." && curl -s -X POST http://localhost:8001/autonomous/start | python -m json.tool
echo "💬 Тестирую чат с AI..." && curl -s -X POST http://localhost:8001/ask   -H "Content-Type: application/json"   -d '{"prompt": "Привет! Расскажи что ты знаешь о моем бизнесе на Wildberries", "session_id": "test"}' | python -m json.tool
curl -s -X POST http://localhost:8001/ask   -H "Content-Type: application/json"   -d '{"prompt": "Привет! Как дела?", "session_id": "test"}'
curl -s http://localhost:8001/config/llm | python -m json.tool
curl -s http://localhost:8001/smoke | python -m json.tool
curl -s http://localhost:8001/smoke
which ollama
curl -fsSL https://ollama.com/install.sh | sh
echo "🔧 Настраиваю OpenAI вместо Ollama..." && export LLM_PROVIDER=openai && export OPENAI_API_KEY=sk-test-key
curl -s http://localhost:8001/config/llm | python -m json.tool
pkill -f uvicorn
cd /home/mentor && source venv/bin/activate && cd mentor/app && python test_demo.py
curl -s -X POST http://localhost:8001/autonomous/start
curl -s -X POST http://localhost:8001/control/autopilot/start   -H "Content-Type: application/json"   -d '{"goal": "Улучшить систему: исправить ошибки, оптимизировать код, добавить новые функции для MentorCoder100", "iterations": 5, "wait_s": 2}'
curl -s http://localhost:8001/autonomous/status | python -m json.tool
curl -s http://localhost:8001/autonomous/status
pkill -f uvicorn && sleep 2
ps aux | grep uvicorn | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true
sleep 3 && curl -s http://localhost:8002/health
curl -s http://localhost:8002/health
curl -s http://localhost:8002/health && echo ""
curl -s http://localhost:8002/health
cd /home/mentor && source venv/bin/activate && python -c "
import sys
sys.path.append('/home/mentor')
from wb_api import get_cards

print('🔍 Анализирую категории товаров в вашем кабинете WB...')
try:
    cards = get_cards(limit=100)
    if cards and 'cards' in cards:
        categories = {}
        for card in cards['cards']:
            category = card.get('subject', 'Неизвестно')
            categories[category] = categories.get(category, 0) + 1
        
        print(f'📊 Всего категорий: {len(categories)}')
        print('\\n📋 КАТЕГОРИИ ТОВАРОВ:')
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f'  • {category}: {count} товаров')
    else:
        print('❌ Не удалось получить данные о товарах')
except Exception as e:
    print(f'❌ Ошибка: {e}')
"
cd /home/mentor && source venv/bin/activate && python -c "
import sys
sys.path.append('/home/mentor')
from wb_api import get_cards

print('🔍 Получаю все товары из вашего кабинета WB...')
try:
    cards = get_cards(limit=1000)  # Увеличиваем лимит
    if cards and 'cards' in cards:
        print(f'📊 Всего товаров: {len(cards[\"cards\"])}')
        print('\\n📋 ВСЕ ТОВАРЫ:')
        print('=' * 80)
        
        for i, card in enumerate(cards['cards'], 1):
            nm_id = card.get('nmId', 'N/A')
            name = card.get('name', 'Без названия')
            subject = card.get('subject', 'Неизвестно')
            brand = card.get('brand', 'Без бренда')
            price = card.get('priceU', 0) / 100 if card.get('priceU') else 0
            rating = card.get('rating', 0)
            reviews = card.get('feedbacks', 0)
            
            print(f'{i:3d}. ID: {nm_id}')
            print(f'     Название: {name[:60]}...' if len(name) > 60 else f'     Название: {name}')
            print(f'     Категория: {subject}')
            print(f'     Бренд: {brand}')
            print(f'     Цена: {price:.0f} руб.')
            print(f'     Рейтинг: {rating} ({reviews} отзывов)')
            print('-' * 80)
    else:
        print('❌ Не удалось получить данные о товарах')
except Exception as e:
    print(f'❌ Ошибка: {e}')
"
pkill -f "python quick_server.py" && sleep 2
sleep 3 && curl -s http://localhost:8002/health
cd /home/mentor && source venv/bin/activate && pip install python-telegram-bot
source /home/mentor/venv/bin/activate
cd /home/mentor && source venv/bin/activate && cd mentor/app && uvicorn main:app --host 0.0.0.0 --port 8001 --reload
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
cd /home/mentor && source venv/bin/activate && pip install python-telegram-bot
сcd /home/mentor
cd /home/mentor
find /home/mentor -name "*.py" -type f | head -20
find /home/mentor -maxdepth 3 -name "*.py" -type f | grep -v cpython | sort
ls -la /home/mentor/ | grep -E "^d"
cd /home/mentor/mentor/app && python -c "import wb_api_enhanced; print('WB API Enhanced: OK')"
cd /home/mentor/mentor/app && python -c "import analytics; print('Analytics: OK')"
cd /home/mentor && source venv/bin/activate && pip install matplotlib tabulate requests
cd /home/mentor/mentor/app && python -c "import analytics; print('Analytics: OK')"
cd /home/mentor/mentor/app && python -c "import vector_db; print('Vector DB: OK')"
pip install psycopg[binary] fastembed
cd /home/mentor/mentor/app && python -c "import vector_db; print('Vector DB: OK')"
cd /home/mentor/mentor/app && python -c "from fastembed import TextEmbedding; print(TextEmbedding.list_supported_models())"
cd /home/mentor/mentor/app && python -c "import vector_db; print('Vector DB: OK')"
cd /home/mentor/mentor/app && ls -la
cd /home/mentor/mentor && git status
cd /home/mentor/mentor && git restore app/autopilot.py
cd /home/mentor/mentor && git restore app/autonomous_agent.py
cd /home/mentor/mentor && git restore app/autonomous_web.py
cd /home/mentor/mentor/app && python -c "from autonomous_agent import autonomous_agent; print('Autonomous Agent: OK')"
cd /home/mentor/mentor/app && python -c "import autopilot; print('Autopilot: OK')"
sleep 3 && curl -s http://localhost:8002/health
curl -s http://localhost:8002/health
ps aux | grep python
cd /home/mentor/mentor/app && python quick_server.py
cd /home/mentor/mentor/app && python -c "import quick_server; print('Quick server imports: OK')"
cd /home/mentor/mentor/app && python -c "import uvicorn; print('Uvicorn available')"
sleep 3 && curl -s http://localhost:8002/health
curl -v http://localhost:8002/health
ps aux | grep uvicorn
cd /home/mentor/mentor/app && python -c "from quick_server import app; print('App created successfully')"
cd /home/mentor/mentor/app && python quick_server.py 2>&1
sleep 3 && curl -s http://localhost:8002/health
cd /home/mentor && source venv/bin/activate && pip install fastapi uvicorn
pip install fastapi uvicorn
which python
cd /home/mentor/mentor/app && python quick_server.py
cd /home/mentor/mentor/app && uvicorn quick_server:app --host 0.0.0.0 --port 8002 --reload
cd /home/mentor/mentor/app && uvicorn quick_server:app --host 0.0.0.0 --port 8002
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
ps aux | grep python
curl http://localhost:8000/health
pkill -f uvicorn
sleep 3 && curl http://localhost:8001/health
cd /home/mentor/mentor/app && python -c "import main"
cd /home/mentor && source venv/bin/activate && pip install fastapi uvicorn
sleep 5 && curl http://localhost:8001/health
ps aux | grep uvicorn
cd /home/mentor/mentor/app && python -c "import main; print('Import successful')"
sleep 3 && curl http://localhost:8001/health
ps aux | grep uvicorn
cd /home/mentor/mentor/app && uvicorn main:app --host 0.0.0.0 --port 8001 --reload
curl http://localhost:8001/health
cd /home/mentor/mentor/app && nohup uvicorn main:app --host 0.0.0.0 --port 8001 > server.log 2>&1 &
sleep 3 && curl http://localhost:8001/health
curl http://localhost:8001/docs
curl http://localhost:8001/static/unified.html
pkill -f "uvicorn main:app"
cd /home/mentor/mentor/app && nohup uvicorn main:app --host 0.0.0.0 --port 8002 > server2.log 2>&1 &
sleep 3 && curl http://localhost:8002/health
curl http://localhost:8002/static/unified.html
curl http://localhost:8002/ask -X POST -H "Content-Type: application/json" -d '{"question": "Привет! Как дела?", "user_id": 1}'
tail -20 /home/mentor/mentor/app/server2.log
pkill -f "uvicorn main:app --host 0.0.0.0 --port 8002"
cd /home/mentor/mentor/app && nohup uvicorn main:app --host 0.0.0.0 --port 8002 > server2.log 2>&1 &
sleep 3 && curl http://localhost:8002/ask -X POST -H "Content-Type: application/json" -d '{"question": "Привет! Как дела?", "user_id": 1}'
tail -10 /home/mentor/mentor/app/server2.log
curl http://localhost:8002/health
curl -v http://localhost:8002/ask -X POST -H "Content-Type: application/json" -d '{"question": "Привет!", "user_id": 1}'
cd /home/mentor && source venv/bin/activate && pip install psutil requests
pkill -f "uvicorn main:app --host 0.0.0.0 --port 8002"
cd /home/mentor/mentor/app && nohup uvicorn main:app --host 0.0.0.0 --port 8002 > server2.log 2>&1 &
sleep 3 && curl http://localhost:8002/health
curl http://localhost:8002/orchestrator/status
ps aux | grep uvicorn
curl http://localhost:8002/orchestrator/status
curl http://localhost:8002/static/orchestrator.html
cd /home/mentor/mentor/app && ls -la *.json
cd /home/mentor/mentor/app && ls -la .env*
curl http://localhost:8002/health
ps aux | grep uvicorn
cd /home/mentor/mentor/app && python test_wb_api.py
cd /home/mentor/mentor/app && python test_wb_api.py 2>&1
cd /home/mentor/mentor/app && python quick_wb_test.py
ps aux | grep uvicorn
cd /home/mentor/mentor/app && python -c "import main; print('Import OK')"
sleep 3 && curl http://localhost:8003/health
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python direct_wb_test.py
pkill -f "uvicorn main:app --host 0.0.0.0 --port 8002"
cd /home/mentor/mentor/app && nohup uvicorn main:app --host 0.0.0.0 --port 8002 > server2.log 2>&1 &
sleep 3 && curl http://localhost:8002/health
curl "http://localhost:8002/api/files/read?file_path=test_web_editor.py"
pkill -f uvicorn
sleep 3 && curl http://localhost:8002/health
curl http://localhost:8002/health
pkill -f uvicorn
sleep 3 && curl http://localhost:8002/health
curl http://localhost:8002/health
ps aux | grep uvicorn
netstat -tlnp | grep 8002
sleep 5 && curl http://localhost:8002/health
tail -20 server.log
source /home/mentor/venv/bin/activate && python -c "import main; print('Import successful')"
sleep 5 && curl http://localhost:8002/health
curl http://localhost:8002/health
ps aux | grep uvicorn
netstat -tlnp | grep 8002
source /home/mentor/venv/bin/activate && python -c "import main; print('Import successful')"
sleep 3 && curl http://localhost:8002/health
source /home/mentor/venv/bin/activate && pip list | grep fastapi
cd /home/mentor/mentor/app
source /home/mentor/venv/bin/activate && python -c "import main; print('App object:', hasattr(main, 'app'))"
cd /home/mentor/mentor/app && uvicorn main:app --host 0.0.0.0 --port 8001
cd /home/mentor/mentor/app && uvicorn main:app --host 0.0.0.0 --port 8001
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8002
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "import main; print('App object exists:', hasattr(main, 'app')); print('App type:', type(main.app))"
sleep 3 && curl -s http://localhost:8002/health
curl -s http://localhost:8002/static/unified.html | head -5
curl -s http://localhost:8002/static/code_editor.html | head -5
curl -s http://localhost:8002/static/orchestrator.html | head -5
curl -s http://localhost:8002/static/mobile.html | head -5
curl -s "http://localhost:8002/api/files/list?path=." | jq '.files | length'
curl -s "http://localhost:8002/orchestrator/status" | jq '.'
curl -s http://localhost:8002/health
curl -X POST http://localhost:8002/api/ai/code-assist   -H "Content-Type: application/json"   -d '{"request": "создай простую функцию hello world", "current_file": "test.py", "current_code": ""}' | jq '.'
curl -X POST http://localhost:8002/api/ai/code-assist   -H "Content-Type: application/json"   -d '{"request": "создай простую функцию hello world", "current_file": "test.py", "current_code": ""}' | jq '.'
curl -s http://localhost:8002/smoke
curl -X POST http://localhost:8002/api/ai/code-assist   -H "Content-Type: application/json"   -d '{"request": "создай простую функцию hello world", "current_file": "test.py", "current_code": ""}' | jq '.'
curl -X POST http://localhost:8002/api/ai/code-assist   -H "Content-Type: application/json"   -d '{"request": "создай простую функцию hello world", "current_file": "test.py", "current_code": ""}' | jq '.error'
curl -X POST http://localhost:8002/api/ai/code-assist   -H "Content-Type: application/json"   -d '{"request": "создай простую функцию hello world", "current_file": "test.py", "current_code": ""}' | jq '.'
curl -X POST http://localhost:8002/api/ai/code-assist   -H "Content-Type: application/json"   -d '{"request": "создай простую функцию hello world", "current_file": "test.py", "current_code": ""}' > /dev/null 2>&1 &
ps aux | grep uvicorn
curl -X POST http://localhost:8002/api/ai/test   -H "Content-Type: application/json"   -d '{"request": "test"}' | jq '.'
pkill -f "uvicorn main:app"
kill 1124851
sleep 3 && curl -X POST http://localhost:8002/api/ai/test   -H "Content-Type: application/json"   -d '{"request": "test"}' | jq '.'
curl -s http://localhost:8002/health
curl -X POST http://localhost:8002/api/ai/test   -H "Content-Type: application/json"   -d '{"request": "test"}' | jq '.'
curl -X POST http://localhost:8002/api/ai/code-assist   -H "Content-Type: application/json"   -d '{"request": "создай простую функцию hello world", "current_file": "test.py", "current_code": ""}' | jq '.'
curl -X POST http://localhost:8002/api/ai/code-assist   -H "Content-Type: application/json"   -d '{"request": "создай функцию для расчета прибыли от продаж", "current_file": "analytics.py", "current_code": "", "session_id": "test"}' | jq '.'
curl -s http://localhost:8002/api/ai/chat-history | jq '.'
curl -X POST http://localhost:8002/api/ai/code-assist   -H "Content-Type: application/json"   -d '{"request": "покажи файлы", "current_file": "", "current_code": "", "session_id": "test"}' | jq '.'
curl -X POST http://localhost:8002/api/ai/code-assist   -H "Content-Type: application/json"   -d '{"request": "создай файл назови test_voice.py", "current_file": "", "current_code": "", "session_id": "test"}' | jq '.'
curl -X POST http://localhost:8002/api/ai/code-assist   -H "Content-Type: application/json"   -d '{"request": "покажи статус ботов", "current_file": "", "current_code": "", "session_id": "test"}' | jq '.'
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8002 --reload
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8002 --reload
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "
from org_structure import get_org_structure
from agent_manager import get_agent_manager

# Тестируем организационную структуру
org = get_org_structure()
print('�� Организационная структура инициализирована!')
print(f'Всего агентов: {len(org.agents)}')

# Тестируем менеджер агентов
manager = get_agent_manager()
print('🤖 Менеджер агентов инициализирован!')

# Показываем иерархию
hierarchy = org.get_agent_hierarchy()
print('🌳 Иерархия агентов:')
print(f'Корневой агент: {hierarchy[\"agent\"][\"name\"]}')

# Показываем статистику
overview = manager.get_system_overview()
print(f'📊 Статистика: {overview[\"total_agents\"]} агентов, {overview[\"total_tasks\"]} задач')
"
curl -X GET http://localhost:8002/api/org/overview | jq '.'
sleep 3 && curl -X GET http://localhost:8002/api/org/overview | jq '.'
curl -X POST http://localhost:8002/api/ai/code-assist   -H "Content-Type: application/json"   -d '{"request": "покажи статус ботов", "current_file": "", "current_code": "", "session_id": "test"}' | jq '.'
curl -X POST http://localhost:8002/api/ai/code-assist   -H "Content-Type: application/json"   -d '{"request": "создать задачу написать код для анализа продаж", "current_file": "", "current_code": "", "session_id": "test"}' | jq '.'
curl -X GET http://localhost:8002/static/org_dashboard.html | head -20
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8002 --reload
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python get_telegram_chat_id.py
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8003 --reload
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8003 --reload
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8003 --reload
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8003 --reload
curl -fsSL https://ollama.ai/install.sh | sh
wget https://ollama.ai/download/ollama-linux-amd64 -O ollama
docker --version
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
docker ps -a | grep ollama
curl http://localhost:11434/api/tags
docker exec mentor-ollama-1 ollama pull codellama:7b
docker exec mentor-ollama-1 ollama pull neural-chat:7b
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && pip install requests
curl -X GET http://localhost:8002/api/ollama/status
sleep 5 && curl -X GET http://localhost:8002/api/ollama/status
curl -X POST http://localhost:8002/api/ollama/chat -H "Content-Type: application/json" -d '{"messages": [{"role": "user", "content": "Привет! Как дела?"}], "model": "llama3.1:8b"}'
curl -X POST http://localhost:8002/api/ollama/code-assist -H "Content-Type: application/json" -d '{"code": "def hello():\n    print(\"Hello\")", "instruction": "Добавь функцию для приветствия на русском", "model": "codellama:7b"}'
curl -X POST http://localhost:8002/api/agents/chat -H "Content-Type: application/json" -d '{"message": "привет"}'
curl -X POST http://localhost:8002/api/agents/chat -H "Content-Type: application/json" -d '{"message": "создай файл test.py"}'
curl -X POST http://localhost:8002/api/agents/chat -H "Content-Type: application/json" -d '{"message": "привет, как дела?"}'
curl -X POST http://localhost:8002/api/brain/initialize
curl -X GET http://localhost:8002/api/brain/agent/supreme_commander
curl -X GET http://localhost:8002/api/brain/agent/strategic_advisor
curl -X GET http://localhost:8002/api/org/agents
curl -X GET http://localhost:8002/api/brain/agent/ai_strategic_advisor
curl -X POST http://localhost:8002/api/brain/collective/think -H "Content-Type: application/json" -d '{"problem": "Как увеличить продажи на Wildberries в 10 раз?", "context": {"market": "e-commerce", "platform": "wildberries"}}'
curl -X POST http://localhost:8002/api/brain/agent/ai_strategic_advisor/think -H "Content-Type: application/json" -d '{"problem": "Как увеличить продажи на Wildberries в 10 раз?", "context": {"market": "e-commerce", "platform": "wildberries"}}'
curl -X GET http://localhost:8002/api/brain/system/intelligence
curl -X POST http://localhost:8002/api/brain/initialize
curl -X GET http://localhost:8002/api/brain/system/intelligence
curl -X GET http://localhost:8002/api/brain/agent/supreme_commander
curl -X POST http://localhost:8002/api/brain/agent/ai_strategic_advisor/think -H "Content-Type: application/json" -d '{"problem": "Как создать идеальную бизнес-модель для e-commerce?", "context": {"industry": "e-commerce", "target": "profitability"}}'
curl -X GET http://localhost:8002/api/brain/agent/code_assistant
curl -X POST http://localhost:8002/api/brain/agent/code_assistant/train -H "Content-Type: application/json" -d '{"task": "Создание Python API", "result": {"success": true, "performance": 0.95}, "performance": 0.95}'
curl -X GET http://localhost:8002/api/brain/agent/code_assistant
curl -X GET http://localhost:8002/api/brain/system/intelligence
curl -X POST http://localhost:8002/api/brain/agent/supreme_commander/think -H "Content-Type: application/json" -d '{"problem": "Как управлять галактической империей?", "context": {"scale": "galactic", "population": "trillions"}}'
curl -X GET http://localhost:8002/api/brain/agent/business_intelligence
curl -X POST http://localhost:8002/api/brain/agent/business_intelligence/think -H "Content-Type: application/json" -d '{"problem": "Как предсказать кризис на рынке e-commerce?", "context": {"market": "e-commerce", "timeframe": "next_5_years"}}'
curl -X GET http://localhost:8002/api/brain/agent/task_manager
curl -X POST http://localhost:8002/api/brain/agent/task_manager/train -H "Content-Type: application/json" -d '{"task": "Управление 1000 задачами одновременно", "result": {"success": true, "efficiency": 0.99}, "performance": 0.99}'
curl -X GET http://localhost:8002/api/brain/system/intelligence
curl -s -X GET http://localhost:8002/api/brain/system/intelligence
curl -X POST http://localhost:8002/api/agents/chat -H "Content-Type: application/json" -d '{"message": "Привет, Верховный Командующий!"}'
curl -s -X POST http://localhost:8002/api/agents/chat -H "Content-Type: application/json" -d '{"message": "Привет, Верховный Командующий!"}'
curl -X POST http://localhost:8002/api/agents/chat -H "Content-Type: application/json" -d '{"message": "Создай стратегию развития проекта"}'
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && pip install aiohttp
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "import ai_providers; print('AI провайдеры импортированы успешно')"
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "from ai_providers import ai_provider_manager; print('Менеджер AI провайдеров:', ai_provider_manager.agent_providers)"
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "import main; print('main.py импортирован успешно')"
sleep 3 && curl -X GET http://localhost:8002/api/ai/agents/list
curl -X GET http://localhost:8002/api/ai/agents/list
curl -X GET http://localhost:8002/health
ps aux | grep uvicorn
curl -X GET http://localhost:8002/health
curl -v http://localhost:8002/health
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && pip install psutil
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "import monitoring_system; print('Система мониторинга импортирована успешно')"
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "import notification_system; print('Система уведомлений импортирована успешно')"
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "import main; print('main.py с мониторингом импортирован успешно')"
pkill -f "uvicorn main:app"
ps aux | grep uvicorn
sleep 3 && curl -X GET http://localhost:8003/health
curl -v http://localhost:8003/health
curl -X GET http://localhost:8003/api/monitoring/quick-status
curl -X GET http://localhost:8003/api/monitoring/status
curl -X GET http://localhost:8003/api/ai/agents/list
curl -X POST http://localhost:8003/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "Привет! Как дела?"}'
curl -X POST http://localhost:8003/api/ai/agent/code_assistant/chat -H "Content-Type: application/json" -d '{"message": "Создай функцию hello world на Python"}'
curl -X POST http://localhost:8003/api/notifications/test -H "Content-Type: application/json" -d '{"level": "warning", "title": "Тестовое уведомление", "message": "Это тестовое уведомление для проверки системы"}'
curl -X GET http://localhost:8003/api/notifications/web
echo "🌐 Дашборд мониторинга доступен по адресу:"
echo "http://localhost:8003/static/monitoring_dashboard.html"
echo "🤖 AI агенты доступны по адресу:"
echo "http://localhost:8003/static/ai_agents_chat.html"
curl -X POST http://localhost:8003/api/notifications/configure-telegram -H "Content-Type: application/json" -d '{"bot_token": "8325306099:AAG6hk3tG2-XmiJPgegzYFzQcY6WJaEbRxw", "chat_id": "YOUR_CHAT_ID"}'
curl -X POST http://localhost:8003/api/notifications/configure-telegram -H "Content-Type: application/json" -d '{"bot_token": "8325306099:AAG6hk3tG2-XmiJPgegzYFzQcY6WJaEbRxw"}'
echo "🤖 Скрипт запущен! Теперь:"
echo "1. Найди бота @mentor_monitoring_bot в Telegram"
echo "2. Напиши боту любое сообщение (например: /start)"
echo "3. Скрипт автоматически получит твой chat_id"
echo "4. Выполни команду curl для настройки уведомлений"
curl -X POST http://localhost:8003/api/notifications/test -H "Content-Type: application/json" -d '{"level": "info", "title": "Тест Telegram", "message": "Проверка работы Telegram уведомлений"}'
curl -X GET http://localhost:8003/api/notifications/telegram/updates
pkill -f "uvicorn main:app --port 8003"
sleep 3 && curl -X POST http://localhost:8003/api/notifications/configure-telegram -H "Content-Type: application/json" -d '{"bot_token": "8325306099:AAG6hk3tG2-XmiJPgegzYFzQcY6WJaEbRxw"}'
curl -X GET http://localhost:8003/api/notifications/telegram/updates
export TELEGRAM_BOT_TOKEN="8325306099:AAG6hk3tG2-XmiJPgegzYFzQcY6WJaEbRxw"
echo "🤖 ИНСТРУКЦИЯ ПО НАСТРОЙКЕ TELEGRAM УВЕДОМЛЕНИЙ:"
echo ""
echo "1. Открой Telegram и найди бота @mentor_monitoring_bot"
echo "2. Напиши боту любое сообщение (например: /start или 'Привет')"
echo "3. Выполни команду для получения chat_id:"
echo "   curl -X GET http://localhost:8003/api/notifications/telegram/updates"
echo "4. Скопируй chat_id из ответа и выполни:"
echo "   curl -X POST http://localhost:8003/api/notifications/configure-telegram \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"bot_token\": \"8325306099:AAG6hk3tG2-XmiJPgegzYFzQcY6WJaEbRxw\", \"chat_id\": \"ТВОЙ_CHAT_ID\"}'"
echo ""
echo "5. Протестируй уведомления:"
echo "   curl -X POST http://localhost:8003/api/notifications/test \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"level\": \"info\", \"title\": \"Тест\", \"message\": \"Telegram работает\"}'"
curl -X POST http://localhost:8003/api/notifications/configure-telegram -H 'Content-Type: application/json' -d '{"bot_token": "8325306099:AAG6hk3tG2-XmiJPgegzYFzQcY6WJaEbRxw", "chat_id": "458589236"}'
curl -X POST http://localhost:8003/api/notifications/test -H 'Content-Type: application/json' -d '{"level": "info", "title": "🎉 Telegram работает!", "message": "Система мониторинга успешно настроена! Теперь ты будешь получать уведомления о всех событиях."}'
curl -X POST http://localhost:8003/api/notifications/test -H 'Content-Type: application/json' -d '{"level": "critical", "title": "🚨 КРИТИЧЕСКОЕ УВЕДОМЛЕНИЕ", "message": "Тест критического уведомления. Система мониторинга работает в полном объеме!"}'
curl -X GET http://localhost:8003/api/monitoring/quick-status
curl -X GET http://localhost:8003/api/notifications/web
curl -X POST http://localhost:8003/api/ai/agent/code_assistant/chat -H 'Content-Type: application/json' -d '{"message": "Создай простую функцию на Python для сложения двух чисел"}'
curl -X POST http://localhost:8003/api/ai/agents/collective-chat -H 'Content-Type: application/json' -d '{"message": "Как улучшить производительность системы?"}'
curl -X GET http://localhost:8003/health
ps aux | grep uvicorn
curl -X GET http://localhost:8003/api/monitoring/quick-status
cd /home/mentor/mentor/app && echo "HF_API_KEY=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" > .env
cd /home/mentor/mentor/app && echo "REPLICATE_API_TOKEN=" >> .env && echo "COHERE_API_KEY=" >> .env && echo "TELEGRAM_BOT_TOKEN=8325306099:AAG6hk3tG2-XmiJPgegzYFzQcY6WJaEbRxw" >> .env && echo "TELEGRAM_CHAT_ID=458589236" >> .env
cd /home/mentor/mentor/app && cat .env
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && pip install python-dotenv
pkill -f "uvicorn main:app"
ps aux | grep uvicorn
sleep 3 && curl -X GET http://localhost:8003/health
curl -X GET http://localhost:8003/api/ai/providers/status
curl -X POST http://localhost:8003/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "Привет! Тест API ключа"}'
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python test_env.py
curl -X POST http://localhost:8003/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "Привет! Тест API ключа"}'
curl -X GET http://localhost:8003/api/ai/providers/status
curl -X POST http://localhost:8003/api/ai/agents/collective-chat -H "Content-Type: application/json" -d '{"message": "Привет всем агентам! Как дела?"}'
curl -X GET http://localhost:8003/api/ollama/status
curl -X POST http://localhost:8003/api/ollama/chat -H "Content-Type: application/json" -d '{"messages": [{"role": "user", "content": "Привет! Как дела?"}], "model": "llama3.1:8b"}'
curl -X GET http://localhost:8003/api/ai/providers/status
curl -X GET http://localhost:8003/health
curl -X POST http://localhost:8003/api/ai/agent/code_assistant/chat -H "Content-Type: application/json" -d '{"message": "Привет! Помоги с кодом"}'
ps aux | grep uvicorn
curl -X POST http://localhost:8003/api/ai/agent/code_assistant/chat -H "Content-Type: application/json" -d '{"message": "Привет! Помоги с кодом"}'
curl -X GET http://localhost:8003/api/ai/providers/status
curl -X GET http://localhost:8003/api/agent-monitoring/status
ps aux | grep uvicorn
sleep 3 && curl -X GET http://localhost:8003/api/agent-monitoring/status
curl -X GET http://localhost:8003/health
netstat -tlnp | grep :800
ps aux | grep python
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8003 --reload
ps aux | grep uvicorn
curl -X GET http://localhost:8000/health
curl -X GET http://localhost:8003/health
sleep 5 && curl -X GET http://localhost:8003/api/agent-monitoring/status
curl -X POST http://localhost:8003/api/agent-monitoring/start
curl -X GET http://localhost:8003/api/agent-monitoring/status
curl -X POST http://localhost:8003/api/agent-monitoring/test-alert
curl -X GET http://localhost:8003/api/agent-monitoring/alerts
curl -X GET http://localhost:8003/agent-monitoring-dashboard
curl -I http://localhost:8003/agent-monitoring-dashboard
curl -I http://localhost:8003/static/agent_monitoring_dashboard.html
curl -X GET http://localhost:8003/static/ai_agents_chat.html
curl -X GET http://localhost:8003/api/ai/agents/list
curl -X POST http://localhost:8003/api/ai/agent/code_assistant/chat -H "Content-Type: application/json" -d '{"message": "Привет! Как дела?", "context": ""}'
curl -X POST http://localhost:8003/api/ai/agents/collective-chat -H "Content-Type: application/json" -d '{"message": "Расскажите о ваших возможностях", "context": ""}'
curl -X GET http://localhost:8003/api/agent-monitoring/status
curl -X POST http://localhost:8003/api/agent-monitoring/start
curl -X POST http://localhost:8003/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "Привет! Как дела?", "context": ""}'
find /home/mentor -name ".env" -type f
cat /home/mentor/mentor/app/.env
sed -i 's/REPLICATE_API_TOKEN=/REPLICATE_API_TOKEN=r8_aNuy1HsG707y1lHWoCjDz0wMNKxhs5G2aWOvf/' /home/mentor/mentor/app/.env
cat /home/mentor/mentor/app/.env
curl -X POST http://localhost:8003/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "Привет! Расскажи о своих возможностях", "context": ""}'
curl -X POST http://localhost:8003/api/ai/agent/strategic_advisor/chat -H "Content-Type: application/json" -d '{"message": "Привет! Как дела?", "context": ""}'
curl -X POST http://localhost:8003/api/ai/agent/code_assistant/chat -H "Content-Type: application/json" -d '{"message": "Привет! Помоги с кодом", "context": ""}'
curl -X POST http://localhost:8003/api/ai/agents/collective-chat -H "Content-Type: application/json" -d '{"message": "Привет всем! Расскажите о ваших возможностях", "context": ""}'
sed -i 's/COHERE_API_KEY=/COHERE_API_KEY=oeVLFxUG337suC7TcfjMiEkN2ffIMe2EQ6Z6pGC1/' /home/mentor/mentor/app/.env
cat /home/mentor/mentor/app/.env
curl -X POST http://localhost:8003/api/ai/agent/business_intelligence/chat -H "Content-Type: application/json" -d '{"message": "Привет! Расскажи о своих возможностях", "context": ""}'
curl -X POST http://localhost:8003/api/ai/agents/collective-chat -H "Content-Type: application/json" -d '{"message": "Привет всем! Расскажите о ваших возможностях", "context": ""}'
curl -X POST http://localhost:8003/api/ai/agent/business_intelligence/chat -H "Content-Type: application/json" -d '{"message": "Помоги с бизнес-анализом", "context": ""}'
curl -X GET http://localhost:8003/api/ai/providers/status
curl -I http://localhost:8003/static/ai_agents_chat.html
curl -X POST http://localhost:8003/api/ai/agent/strategic_advisor/chat -H "Content-Type: application/json" -d '{"message": "как идет у нас создание проекта?", "context": ""}'
curl -X POST http://localhost:8003/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "как дела с нашей системой?", "context": ""}'
curl -X POST http://localhost:8003/api/ai/agents/collective-chat -H "Content-Type: application/json" -d '{"message": "Расскажите о состоянии нашего проекта MentorCoder100", "context": ""}'
curl -X GET http://localhost:8003/api/autonomous-agents/list
curl -X POST http://localhost:8003/api/autonomous-agents/code_assistant/smart-action -H "Content-Type: application/json" -d '{"description": "Создай файл с API"}'
curl -X POST http://localhost:8003/api/autonomous-agents/code_assistant/smart-action -H "Content-Type: application/json" -d "{\"description\": \"Создай файл с API\"}"
curl -X POST http://localhost:8003/api/autonomous-agents/code_assistant/smart-action -H "Content-Type: application/json" -d @/tmp/test_request.json
ps aux | grep uvicorn
curl http://localhost:8003/api/autonomous-agents/list
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
cd /home/mentor/mentor && python -c "import app.main; print('System status: OK')"
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
cd /home/mentor/mentor/app && python3 main.py
cd /home/mentor/mentor/app && python3 main.py
curl -X POST "https://api.replicate.com/v1/predictions" -H "Authorization: Token r8_2qDdG5zWY8J9zQ5vK8r2xL1nP6mT3fS7hY4cR9wE2" -H "Content-Type: application/json" -d '{"version": "meta/llama-2-7b-chat:meta-llama/Llama-2-7b-chat", "input": {"prompt": "Hello, test message"}}'
curl -X POST "https://api-inference.huggingface.co/models/gpt2" -H "Authorization: Bearer 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" -H "Content-Type: application/json" -d '{"inputs": "Hello, how are you?"}'
curl -X POST "https://api.cohere.ai/v1/generate" -H "Authorization: Bearer ymOCG3esFisxQIPR0TwbYg5XWQ47BQNRnbRVZUI2" -H "Content-Type: application/json" -d '{"model": "command", "prompt": "Hello, test message", "max_tokens": 50}'
curl -X POST "http://localhost:11434/api/generate" -H "Content-Type: application/json" -d '{"model": "llama2", "prompt": "Hello, test message", "stream": false}'
curl -s http://localhost:8004/api/ai/providers/status
ps aux | grep ollama
curl -s http://localhost:11434/api/tags
curl -X POST "http://localhost:11434/api/generate" -H "Content-Type: application/json" -d '{"model": "llama3.1:8b", "prompt": "Hello, test message", "stream": false}'
curl -X POST "http://localhost:8004/api/agents/chat" -H "Content-Type: application/json" -d '{"message": "Привет! Как дела?"}'
curl -s http://localhost:8004/api/ai/providers/status | python3 -m json.tool
curl -X POST "http://localhost:8004/api/agents/chat" -H "Content-Type: application/json" -d '{"message": "Привет! Как дела?"}' | python3 -m json.tool
curl -X POST "http://localhost:8004/api/ai/agents/supreme_commander/chat" -H "Content-Type: application/json" -d '{"message": "Привет! Расскажи о себе"}' | python3 -m json.tool
curl -s http://localhost:8004/docs | grep -o 'href="[^"]*"' | head -10
curl -s http://localhost:8004/api/monitoring/status | python3 -m json.tool
echo "🌐 Доступные интерфейсы:"
echo "1. Организационная структура: http://localhost:8004/org-dashboard"
echo "2. AI Чат с агентами: http://localhost:8004/ai-agents-chat"
echo "3. Мониторинг системы: http://localhost:8004/monitoring-dashboard"
echo "4. Мониторинг агентов: http://localhost:8004/agent-monitoring-dashboard"
curl -s http://localhost:8004/api/ai/providers/status | python3 -m json.tool
curl -X POST "http://localhost:8004/api/agents/chat" -H "Content-Type: application/json" -d '{"message": "Привет! Расскажи о себе как Supreme Commander"}' | python3 -m json.tool
curl -X POST "http://localhost:11434/api/generate" -H "Content-Type: application/json" -d '{"model": "llama3.1:8b", "prompt": "Hello", "stream": false}' --max-time 60
cd /home/mentor/mentor/app && python3 cloud_ollama_setup.py
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python3 cloud_ollama_setup.py
curl -X POST "http://localhost:8004/api/agents/chat" -H "Content-Type: application/json" -d '{"message": "Привет! Тест гибридной системы"}' | python3 -m json.tool
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python3 setup_cloud_servers.py
ls -la *.yml *.sh *.py | grep -E "(docker-compose|setup_cloud|cloud_config)"
chmod +x start_local_ollama_servers.sh
curl -X POST "http://localhost:8004/api/agents/chat" -H "Content-Type: application/json" -d '{"message": "Привет! Расскажи о себе"}' --max-time 30
python3 test_agents.py
python3 free_cloud_setup.py
ls -la *.json *.ipynb *.yml *.sh | head -10
echo "🌐 Откройте Google Colab: https://colab.research.google.com"
chmod +x update_cloud_config.py
echo "📁 Созданные файлы для облачной настройки:" && ls -la *.ipynb *.py *.md | grep -E "(quick_ollama|update_cloud|STEP_BY_STEP|CLOUD_SETUP)"
echo "🧪 Тестируем текущую конфигурацию..." && curl -s http://localhost:8004/api/ai/providers/status | python3 -c "import sys, json; data=json.load(sys.stdin); print('✅ Статус провайдеров:'); [print(f'   {k}: {v}') for k,v in data['agent_assignments'].items()]"
python3 cloud_infrastructure_agent.py
curl -s http://localhost:8004/api/cloud-infrastructure/status | python3 -m json.tool
curl -X POST http://localhost:8004/api/cloud-infrastructure/auto-setup | python3 -m json.tool
ls -la auto_cloud_setup.ipynb auto_setup_script.py
cd /home/mentor/mentor/app && python3 test_super_system.py
chmod +x /home/mentor/mentor/app/install_autonomous_server.sh
mkdir -p /home/mentor/mentor/app/grafana/dashboards /home/mentor/mentor/app/grafana/datasources
chmod +x /home/mentor/mentor/app/test_autonomous_server.py
sleep 5 && curl -s http://localhost:8000/health
ps aux | grep python | grep main.py
cd /home/mentor/mentor/app && python3 main.py
sleep 10 && curl -s http://localhost:8000/health
curl -s http://localhost:8000/api/super-system/status | python3 -m json.tool
curl -s http://localhost:8000/docs
curl -s http://localhost:8000/ | head -20
curl -s http://localhost:8000/org-dashboard | head -10
ps aux | grep python
curl -s http://localhost:8004/health
curl -s http://localhost:8000/health
curl -s http://localhost:8000/super-system-dashboard | head -10
curl -s http://localhost:8000/openapi.json | python3 -c "import sys, json; data=json.load(sys.stdin); print('Available paths:'); [print(f'  {path}') for path in data['paths'].keys()]"
pkill -f "python3 main.py"
cd /home/mentor/mentor/app && python3 main.py
sleep 10 && curl -s http://localhost:8000/health
ps aux | grep "python3 main.py"
cd /home/mentor/mentor/app && python3 main.py
sleep 15 && curl -s http://localhost:8000/health
ps aux | grep "python3 main.py" | grep -v grep
cd /home/mentor/mentor/app && timeout 10 python3 main.py
sleep 10 && curl -s http://localhost:8000/health
curl -s http://localhost:8000/openapi.json | python3 -c "import sys, json; data=json.load(sys.stdin); print('Available paths:'); [print(f'  {path}') for path in sorted(data['paths'].keys())]"
ps aux | grep uvicorn
curl -s http://localhost:8004/health
pkill -f uvicorn
pkill -f "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
cd /home/mentor/mentor/app && uvicorn main:app --host 0.0.0.0 --port 8000 --reload
sleep 10 && curl -s http://localhost:8001/health
ps aux | grep "uvicorn main:app" | grep -v grep
curl -s http://localhost:8001/health
sleep 5 && curl -s http://localhost:8001/health
sleep 5 && curl -s http://localhost:8002/health
netstat -tlnp | grep :800
ss -tlnp | grep :800
curl -s http://localhost:8004/health
sleep 5 && curl -s http://localhost:8003/health
which python3
python3 -c "import fastapi; print('FastAPI version:', fastapi.__version__)"
sleep 5 && curl -s http://localhost:8005/test
ps aux | grep python | grep -v grep
curl -s http://localhost:8004/health
cd /home/mentor/mentor/app && python3 -c "
try:
    from super_system_coordinator import super_system_coordinator
    print('✅ super_system_coordinator импортирован')
except Exception as e:
    print('❌ Ошибка импорта super_system_coordinator:', e)

try:
    from super_autonomous_system import super_autonomous_system
    print('✅ super_autonomous_system импортирован')
except Exception as e:
    print('❌ Ошибка импорта super_autonomous_system:', e)

try:
    from super_agent_manager import super_agent_manager
    print('✅ super_agent_manager импортирован')
except Exception as e:
    print('❌ Ошибка импорта super_agent_manager:', e)
"
curl -v http://localhost:8004/health
curl -s http://localhost:8000/health
curl -s http://localhost:8000/openapi.json | python3 -c "import sys, json; data=json.load(sys.stdin); print('Available paths:'); [print(f'  {path}') for path in sorted(data['paths'].keys())]"
curl -s http://localhost:8000/ | head -5
pkill -f "uvicorn main:app"
kill 1249511 1316637
sleep 10 && curl -s http://localhost:8006/health
sleep 5 && curl -s http://localhost:8007/health
ps aux | grep python | grep -v grep
curl -s http://localhost:8006/health
cd /home/mentor/mentor/app && uvicorn main:app --host 0.0.0.0 --port 8000 --reload
cd /home/mentor/mentor/app && python3 main.py
cd /home/mentor/mentor/app && uvicorn main:app --host 0.0.0.0 --port 8001 --reload
cd /home/mentor/mentor/app && python3 working_main.py
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
cd /home/mentor/mentor/app && python3 simple_test.py
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
deactivate && cd /home/mentor/mentor/app && python3 working_main.py
cd /home/mentor/mentor/app && python3 minimal_main.py
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
cd /home/mentor/mentor/app && python3 http_server.py
cd /home/mentor/mentor/app && python3 complete_system.py
cd /home/mentor/mentor/app && python3 simple_server.py
cd /home/mentor/mentor/app && python3 -c "
import uvicorn
from simple_server import app
print('🚀 Запуск на порту 8001...')
uvicorn.run(app, host='0.0.0.0', port=8001)
"
cd /home/mentor/mentor/app && python3 robust_server.py
pkill -f "uvicorn main:app" && pkill -f "working_main.py"
kill 1249511 1319335 2>/dev/null || true
sleep 5 && curl -s http://localhost:8000/health
sleep 5 && curl -s http://localhost:8001/health
sleep 5 && curl -s http://localhost:8000/health
ps aux | grep python | grep -v grep
curl -s http://localhost:8004/health
sleep 3 && curl -s http://localhost:8002/health
ps aux | grep python | grep -v grep
curl -s http://localhost:8002/health
netstat -tlnp 2>/dev/null | grep :800 || ss -tlnp | grep :800
curl -s http://localhost:8002/health
curl -v http://localhost:8002/health
kill 1325892 2>/dev/null || true
sleep 3 && curl -s http://localhost:8003/health
ps aux | grep python | grep robust_server
curl -s http://localhost:8003/health
curl -s http://localhost:8003/ | python3 -m json.tool
curl -s http://localhost:8003/org-dashboard | head -5
chmod +x /home/mentor/mentor/app/start_super_system.sh
curl -s http://localhost:8003/org-dashboard | grep -i "chat\|agent" | head -5
curl -s http://localhost:8003/org-dashboard | grep -A 5 -B 5 "chat"
pkill -f robust_server.py
sleep 5 && curl -s http://localhost:8004/health | python3 -m json.tool
ps aux | grep complete_system
cd /home/mentor/mentor/app && python3 complete_system.py
sleep 5 && curl -s http://localhost:8004/health
ps aux | grep complete_system
source /home/mentor/venv/bin/activate && cd /home/mentor/mentor/app && timeout 10 python3 complete_system.py
sleep 5 && curl -s http://localhost:8005/health
ps aux | grep complete_system
curl -s http://localhost:8005/health
curl -s http://localhost:8005/api/org/agents | python3 -m json.tool
curl -X POST http://localhost:8005/api/agents/chat   -H "Content-Type: application/json"   -d '{"message": "Привет! Как дела?", "agent_id": "supreme_commander"}' | python3 -m json.tool
curl -s -X POST http://localhost:8005/api/agents/chat -H "Content-Type: application/json" -d '{"message": "Привет!", "agent_id": "supreme_commander"}'
chmod +x /home/mentor/mentor/app/launch_complete_system.sh
pkill -f complete_system.py
./launch_complete_system.sh
sleep 5 && curl -s http://localhost:8006/health
curl -s -X POST http://localhost:8006/api/agents/chat -H "Content-Type: application/json" -d '{"message": "Привет! Как дела?", "agent_id": "supreme_commander"}'
source /home/mentor/venv/bin/activate && cd /home/mentor/mentor/app && python3 complete_system.py
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
curl -s http://localhost:8007/api/agents | python3 -m json.tool
curl -s http://localhost:8007/api/systems | python3 -m json.tool
pkill -f ULTIMATE_SYSTEM.py
cd /home/mentor/mentor/app && ./launch_ultimate_system.sh
curl -s -X POST http://localhost:8007/api/agents/chat -H "Content-Type: application/json" -d '{"message": "Supreme Commander! Создай план завершения проекта!", "agent_id": "supreme_commander"}'
curl -s http://localhost:8007/api/cloud-deployment | python3 -m json.tool
curl -s http://localhost:8007/health | python3 -m json.tool
curl -s -X POST http://localhost:8007/api/agents/chat -H "Content-Type: application/json" -d '{"message": "Тест", "agent_id": "supreme_commander"}' | python3 -m json.tool
ps aux | grep ULTIMATE_SYSTEM
chmod +x /home/mentor/mentor/app/launch_simple_system.sh
pkill -f ULTIMATE_SYSTEM.py
cd /home/mentor/mentor/app && ./launch_simple_system.sh
curl -s -X POST http://localhost:8008/api/agents/chat -H "Content-Type: application/json" -d '{"message": "Привет! Как дела?", "agent_id": "supreme_commander"}' | python3 -m json.tool
curl -s http://localhost:8008/health
ps aux | grep SIMPLE_ULTIMATE_SYSTEM
cd /home/mentor/mentor/app && python3 SIMPLE_ULTIMATE_SYSTEM.py
ps aux | grep python3 | grep -v grep
lsof -i :8008
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python3 SIMPLE_ULTIMATE_SYSTEM.py &
ps aux | grep python3
cd /home/mentor/mentor/app && python3 -c "import requests; print('requests OK')"
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && pip install requests
curl -s http://localhost:8008/health
ps aux | grep SIMPLE_ULTIMATE_SYSTEM
cd /home/mentor/mentor/app && ps aux | grep python3
cd /home/mentor/mentor/app && lsof -i :8008
cd /home/mentor/mentor/app && python3 -c "print('Python работает')"
cd /home/mentor/mentor/app && ls -la SIMPLE_ULTIMATE_SYSTEM.py
cd /home/mentor/mentor/app && python3 SIMPLE_ULTIMATE_SYSTEM.py 2>&1
cd /home/mentor/mentor/app && python3 -c "import sys; print(sys.version)"
cd /home/mentor/mentor/app && python3 -c "print('test')"
cd /home/mentor/mentor/app && python3 -c "print('test')" 2>&1
cd /home/mentor/mentor/app && python3 -c "print('test')" 2>&1 | cat
cd /home/mentor/mentor/app && python3 -c "print('test')" 2>&1 | head -1
cd /home/mentor/mentor/app && ls -la
cd /home/mentor/mentor/app && pwd
cd /home/mentor/mentor/app && ls
cd /home/mentor/mentor/app && ls -la | head -10
cd /home/mentor/mentor/app && ls -la | head -20
cd /home/mentor/mentor/app && ls -la
cd /home/mentor/mentor/app && ls
cd /home/mentor/mentor/app && ls -la | cat
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python3 SIMPLE_ULTIMATE_SYSTEM.py
cd /home/mentor/mentor && docker-compose up -d
cd /home/mentor/mentor && ls -la && which docker
cd /home/mentor/mentor && sudo apt update && sudo apt install -y docker-compose
cd /home/mentor/mentor && python3 -m venv venv && source venv/bin/activate && pip install -r app/requirements.txt
cd /home/mentor/mentor && source venv/bin/activate && python -c "import fastapi; print('FastAPI OK')"
cd /home/mentor/mentor && docker --version
cd /home/mentor/mentor && docker compose --version
cd /home/mentor/mentor && docker compose up -d
cd /home/mentor/mentor && docker compose ps
cd /home/mentor/mentor && netstat -tlnp | grep :8000
cd /home/mentor/mentor && ss -tlnp | grep :8000
cd /home/mentor/mentor && docker compose up -d
cd /home/mentor/mentor && docker compose ps
cd /home/mentor/mentor && docker compose logs api
cd /home/mentor/mentor && docker compose down && docker compose up -d --build
cd /home/mentor/mentor && docker compose ps
cd /home/mentor/mentor && docker compose logs api
cd /home/mentor/mentor && docker compose up -d --build api
cd /home/mentor/mentor && docker compose ps
cd /home/mentor/mentor && docker compose logs api --tail=20
cd /home/mentor/mentor && docker compose up -d --build api
cd /home/mentor/mentor && docker compose ps
cd /home/mentor/mentor && curl http://localhost:8001/health
cd /home/mentor/mentor && curl -v http://localhost:8001/health
cd /home/mentor/mentor && curl http://localhost:8001/health | jq .
cd /home/mentor/mentor && curl http://localhost:8001/api/status | jq .
cd /home/mentor/mentor && curl -I http://localhost:3000
cd /home/mentor/mentor && curl http://localhost:11434/api/tags
cd /home/mentor/mentor && curl http://localhost:11434/api/tags | jq .
cd /home/mentor/mentor && docker exec mentor-ollama-1 ollama pull llama3.1:8b
cd /home/mentor/mentor && curl http://localhost:11434/api/tags | jq .
find /home/mentor -type f -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.tsx" -o -name "*.json" -o -name "*.yml" -o -name "*.yaml" -o -name "*.md" -o -name "*.html" -o -name "*.css" -o -name "*.txt" -o -name "*.env" -o -name "*.sh" -o -name "*.sql" -o -name "*.dockerfile" -o -name "Dockerfile" | head -100
find /home/mentor/mentor -type f | wc -l
find /home/mentor/mentor -type f | head -50
find /home/mentor -type f | grep -E '\.(py|js|ts|tsx|json|yml|yaml|md|html|css|txt|env|sh|sql|dockerfile|Dockerfile)$' | head -200
ls -la /home/mentor/
find /home/mentor -type f -name "*.py" | head -100
docker ps -a
ls -la
pwd && whoami
pwd && ls -la
cd /home/mentor/mentor && docker ps -a
docker --version
cd /home/mentor/mentor && ls -la app/
cd /home/mentor/mentor && docker ps -a
docker --version && docker-compose --version
echo "test"
cd /home/mentor/mentor && docker compose up -d --build
docker --version
docker compose --version
cd /home/mentor/mentor && docker compose up -d --build
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
curl -s -X POST http://localhost:8006/api/agents/chat -H "Content-Type: application/json" -d '{"message": "Supreme Commander! Нужно создать ЕДИНУЮ САМОДОСТАТОЧНУЮ СИСТЕМУ! Проект должен быть завершен через час! Повысь мотивацию команды!", "agent_id": "supreme_commander"}'
curl -s -X POST http://localhost:8006/api/agents/chat -H "Content-Type: application/json" -d '{"message": "Strategic Advisor! Создай стратегию завершения проекта! Все системы должны работать как единый организм!", "agent_id": "strategic_advisor"}'
curl -s -X POST http://localhost:8006/api/agents/chat -H "Content-Type: application/json" -d '{"message": "Code Assistant! Исправь все дыры в коде! Создай надежную архитектуру!", "agent_id": "code_assistant"}'
curl -s -X POST http://localhost:8006/api/agents/chat -H "Content-Type: application/json" -d '{"message": "Business Intelligence! Проанализируй все упущения и создай план их устранения!", "agent_id": "business_intelligence"}'
chmod +x /home/mentor/mentor/app/launch_ultimate_system.sh
cd /home/mentor/mentor/app && ./launch_ultimate_system.sh
curl -s -X POST http://localhost:8007/api/agents/chat -H "Content-Type: application/json" -d '{"message": "Supreme Commander! Проект должен быть завершен через час! Повысь мотивацию команды!", "agent_id": "supreme_commander"}'
curl -s -X POST http://localhost:8007/api/agents/chat -H "Content-Type: application/json" -d '{"message": "Strategic Advisor! Создай стратегию завершения проекта!", "agent_id": "strategic_advisor"}'
curl -s -X POST http://localhost:8007/api/boost-motivation -H "Content-Type: application/json"
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8004 --reload
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "import main; print('✅ Импорты работают')"
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && curl -s http://localhost:8003/api/ai/providers/status | python -m json.tool
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && curl -s http://localhost:8003/api/ai/providers/status
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && ps aux | grep uvicorn
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && curl -s http://localhost:8000/api/ai/providers/status
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && curl -s http://localhost:8000/docs
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && pkill -f uvicorn
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && sudo pkill -f uvicorn
sleep 3 && curl -s http://localhost:8004/api/ai/providers/status
curl -s -X POST http://localhost:8004/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "Привет! Как дела?", "context": "Тестирование системы"}'
curl -s -X POST http://localhost:8004/api/ai/agent/code_assistant/chat -H "Content-Type: application/json" -d '{"message": "Создай простую функцию на Python", "context": "Тестирование"}'
curl -s http://localhost:8004/api/monitoring/status
cd /home/mentor/mentor/app && ls -la | grep env
cd /home/mentor/mentor/app && cat .env
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('HF_API_KEY:', os.getenv('HF_API_KEY', 'НЕ НАЙДЕН')[:20] + '...')"
curl -s -X POST http://localhost:8004/api/notifications/configure/telegram -H "Content-Type: application/json" -d '{"bot_token": "8325306099:AAG6hk3tG2-XmiJPgegzYFzQcY6WJaEbRxw", "chat_id": "458589236"}'
curl -s http://localhost:8004/openapi.json | python -c "import json, sys; data=json.load(sys.stdin); [print(f'{method.upper()} {path}') for path, methods in data['paths'].items() for method in methods.keys()]"
curl -s -X POST http://localhost:8004/api/notifications/configure-telegram -H "Content-Type: application/json" -d '{"bot_token": "8325306099:AAG6hk3tG2-XmiJPgegzYFzQcY6WJaEbRxw", "chat_id": "458589236"}'
curl -s -X POST http://localhost:8004/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "Привет! Как дела?", "context": "Тестирование реального API"}'
curl -s -X POST http://localhost:8004/api/ai/agent/business_intelligence/chat -H "Content-Type: application/json" -d '{"message": "Привет! Как дела?", "context": "Тестирование Cohere API"}'
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('HF_API_KEY:', os.getenv('HF_API_KEY', 'НЕ НАЙДЕН')[:10] + '...')
print('COHERE_API_KEY:', os.getenv('COHERE_API_KEY', 'НЕ НАЙДЕН')[:10] + '...')
print('REPLICATE_API_TOKEN:', os.getenv('REPLICATE_API_TOKEN', 'НЕ НАЙДЕН')[:10] + '...')
"
curl -s -X POST http://localhost:8004/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "Привет! Тест Hugging Face", "context": "Тестирование исправленного API"}'
curl -s -X POST http://localhost:8004/api/ai/agent/business_intelligence/chat -H "Content-Type: application/json" -d '{"message": "Привет! Тест Cohere", "context": "Тестирование исправленного API"}'
curl -s -X POST http://localhost:8004/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "Привет! Как дела?", "context": "Тестирование Replicate API"}'
curl -s -X POST http://localhost:8004/api/ai/agent/code_assistant/chat -H "Content-Type: application/json" -d '{"message": "Создай простую функцию на Python", "context": "Тестирование Code Assistant"}'
curl -s -X POST http://localhost:8004/api/ai/agent/business_intelligence/chat -H "Content-Type: application/json" -d '{"message": "Проанализируй метрики системы", "context": "Тестирование Business Intelligence"}'
cd /home/mentor/mentor/app && sed -i 's/COHERE_API_KEY=oeVLFxUG337suC7TcfjMiEkN2ffIMe2EQ6Z6pGC1/COHERE_API_KEY=ymOCG3esFisxQIPR0TwbYg5XWQ47BQNRnbRVZUI2/' .env
curl -s -X POST http://localhost:8004/api/ai/agent/business_intelligence/chat -H "Content-Type: application/json" -d '{"message": "Привет! Тест нового Cohere API", "context": "Тестирование обновленного API ключа"}'
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('COHERE_API_KEY:', os.getenv('COHERE_API_KEY', 'НЕ НАЙДЕН')[:10] + '...')
"
curl -s http://localhost:8004/api/ai/providers/status | python -m json.tool
curl -s http://localhost:8004/api/ai/providers/status
cd /home/mentor/mentor/app && sed -i 's/HF_API_KEY=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/HF_API_KEY=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/' .env
curl -s -X POST http://localhost:8004/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "Привет! Тест нового Hugging Face API", "context": "Тестирование обновленного API ключа"}'
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('HF_API_KEY:', os.getenv('HF_API_KEY', 'НЕ НАЙДЕН')[:10] + '...')
"
curl -s -X POST http://localhost:8004/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "Привет! Тест с моделью GPT-2", "context": "Тестирование"}'
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('HF_API_KEY')

async def test_hf():
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'inputs': 'Hello world',
        'parameters': {
            'max_length': 50,
            'temperature': 0.7
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://api-inference.huggingface.co/models/gpt2',
            headers=headers,
            json=payload,
            timeout=30
        ) as response:
            print(f'Status: {response.status}')
            text = await response.text()
            print(f'Response: {text[:200]}...')

asyncio.run(test_hf())
"
curl -s -X POST http://localhost:8004/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "Привет! Тест с DialoGPT", "context": "Тестирование"}'
curl -s -X POST http://localhost:8004/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "Привет! Тест с distilgpt2", "context": "Тестирование"}'
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && python -c "
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('HF_API_KEY')

async def test_hf_direct():
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'inputs': 'Hello world',
        'parameters': {
            'max_length': 50,
            'temperature': 0.7
        }
    }
    
    print(f'Testing with API key: {api_key[:10]}...')
    print(f'Model: distilgpt2')
    print(f'URL: https://api-inference.huggingface.co/models/distilgpt2')
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://api-inference.huggingface.co/models/distilgpt2',
            headers=headers,
            json=payload,
            timeout=30
        ) as response:
            print(f'Status: {response.status}')
            text = await response.text()
            print(f'Response: {text}')

asyncio.run(test_hf_direct())
"
curl -s -X POST http://localhost:8004/api/ai/agent/supreme_commander/chat -H "Content-Type: application/json" -d '{"message": "Привет! Тест Hugging Face", "context": "Проверка API"}'
curl -s -X POST http://localhost:8004/api/ai/agent/business_intelligence/chat -H "Content-Type: application/json" -d '{"message": "Привет! Тест Cohere", "context": "Проверка API"}'
curl -s -X POST http://localhost:8004/api/ai/agent/strategic_advisor/chat -H "Content-Type: application/json" -d '{"message": "Привет! Тест Replicate", "context": "Проверка API"}'
curl -s http://localhost:8004/api/ai/providers/status
curl -s http://localhost:8004/api/ai/providers/status | python -m json.tool
curl -s http://localhost:8004/api/ai/providers/status
curl -s http://localhost:8004/health
curl -s -v http://localhost:8004/api/ai/providers/status
ps aux | grep uvicorn
. "\home\mentor\.cursor-server\bin\2f2737de9aa376933d975ae30290447c910fdf40/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
. "\home\mentor\.cursor-server\bin\9b5f3f4f2368631e3455d37672ca61b6dce85430/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
cd /home/mentor/mentor/app && printf 'LLM_PROVIDER=ollama\nLOG_LEVEL=INFO\n' > .env && ls -la .env
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && pip install --upgrade pip setuptools wheel | cat
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && pip install -r requirements.txt | cat
cd /home/mentor/mentor/app && source /home/mentor/venv/bin/activate && nohup uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.out 2>&1 & echo $!
cd /home/mentor/mentor/app && curl -s http://localhost:8000/health | jq . | cat
. "\home\mentor\.cursor-server\bin\9b5f3f4f2368631e3455d37672ca61b6dce85430/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
. "\home\mentor\.cursor-server\bin\6af2d906e8ca91654dd7c4224a73ef17900ad730/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
ch/contrib/terminal/common/scripts/shellIntegration-bash.sh"

sudo apt install scrot imagemagick x11-utils

sudo apt install scrot imagemagick x11-utils
cd /home/mentor
./start_system.sh
. "\home\mentor\.cursor-server\bin\d750e54bba5cffada6d7b3d18e5688ba5e944ad0/out/vs/workbench/contrib/terminal/common/scripts/shellIntegration-bash.sh"
