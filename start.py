import uvicorn
from config import API_HOST, API_PORT, AUTO_START_DEMO
from main import build_system

app, state, repository, engine, feed = build_system()

if AUTO_START_DEMO:
    feed.start()

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT, reload=False)