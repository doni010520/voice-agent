from fastapi import FastAPI, Request, Response
import uvicorn
import httpx
import os

app = FastAPI(title="Voice Agent")

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Cache simples pro áudio
audio_cache = {}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/incoming-call")
async def incoming_call(request: Request):
    """Webhook que o Twilio chama quando recebe uma ligação"""
    
    host = request.headers.get("host", "")
    audio_url = f"https://{host}/audio/welcome.mp3"
    
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
</Response>"""
    
    return Response(content=twiml, media_type="application/xml")

@app.get("/audio/welcome.mp3")
async def audio_welcome():
    """Gera áudio com Deepgram TTS"""
    
    global audio_cache
    
    # Usa cache se existir
    if "welcome" in audio_cache:
        return Response(content=audio_cache["welcome"], media_type="audio/mpeg")
    
    text = "Olá! Você ligou para o agente de voz com inteligência artificial. Como posso ajudar você hoje?"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepgram.com/v1/speak?model=aura-asteria-en",
                headers={
                    "Authorization": f"Token {DEEPGRAM_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={"text": text},
                timeout=15.0
            )
            
            if response.status_code == 200:
                audio_cache["welcome"] = response.content
                return Response(content=response.content, media_type="audio/mpeg")
    
    except Exception as e:
        print(f"Erro Deepgram: {e}")
    
    # Retorna áudio vazio se falhar
    return Response(content=b"", media_type="audio/mpeg")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
