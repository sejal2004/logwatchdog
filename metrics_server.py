from fastapi import FastAPI
from prometheus_client import make_asgi_app
import uvicorn

app = FastAPI()

# Mount the Prometheus metrics app at `/metrics`
app.mount("/metrics", make_asgi_app())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
