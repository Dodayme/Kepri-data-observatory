from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(title='Observatorium Pembangunan Kepri', version='1.0.0', description='Analisis eksploratif K-Means dan regresi temporal; penyimpanan dataset dalam memori sesi.')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'], allow_methods=['GET', 'POST', 'DELETE'], allow_headers=['Content-Type'])
app.include_router(router)
