from fastapi import FastAPI
from API.routes import router

app = FastAPI()

print('INFO:     Serviço em funcionamento [OK]')

app.include_router(router)

