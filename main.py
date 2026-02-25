from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="Voice Agent")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/incoming-call")
async def incoming_call(request: Request):
    """Webhook que o Twilio chama quando recebe uma ligação"""
    
    # Por enquanto, só atende e fala uma mensagem de teste
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="pt-BR">Olá! Você ligou para o agente de voz. Em breve estarei funcionando completamente.</Say>
    <Pause length="1"/>
    <Say language="pt-BR">Obrigado por ligar. Até logo!</Say>
</Response>"""
    
    return Response(content=twiml, media_type="application/xml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
