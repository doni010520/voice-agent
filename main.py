from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import uvicorn
import httpx
import os

app = FastAPI(title="Voice Agent")

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/incoming-call")
async def incoming_call(request: Request):
    """Webhook que o Twilio chama quando recebe uma ligação"""
    
    # Usa TTS do Twilio mas aponta pra gerar áudio via Deepgram
    host = request.headers.get("host", "")
    audio_url = f"https://{host}/audio/welcome"
    
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
    <Pause length="1"/>
    <Say language="pt-BR">Até logo!</Say>
</Response>"""
    
    return Response(content=twiml, media_type="application/xml")

@app.get("/audio/welcome")
async def audio_welcome():
    """Gera áudio com Deepgram TTS"""
    
    text = "Olá! Você ligou para o agente de voz com inteligência artificial. Em breve estarei funcionando completamente. Como posso ajudar você hoje?"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.deepgram.com/v1/speak?model=aura-asteria-pt-br",
            headers={
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={"text": text},
            timeout=30.0
        )
        
        return Response(
            content=response.content,
            media_type="audio/mpeg"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
