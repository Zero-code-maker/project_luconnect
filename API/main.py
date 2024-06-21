from fastapi import FastAPI
from API.routes import router

app = FastAPI()

print('INFO:     Serviço em funcionamento [OK]')

@app.get("/")
async def root():
    return {"message": "Bem-vindo Lu connect"}

app.include_router(router)

