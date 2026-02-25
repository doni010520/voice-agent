from fastapi import FastAPI, Request, Response
import uvicorn
import httpx
import os

app = FastAPI(title="Voice Agent")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
    """Gera áudio com OpenAI TTS"""
    
    text = "Olá! Você ligou para o agente de voz com inteligência artificial. Como posso ajudar você hoje?"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "tts-1",
                    "input": text,
                    "voice": "nova",
                    "response_format": "mp3"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return Response(content=response.content, media_type="audio/mpeg")
    
    except Exception as e:
        print(f"Erro OpenAI TTS: {e}")
    
    return Response(content=b"", media_type="audio/mpeg")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
