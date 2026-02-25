from fastapi import FastAPI, Request, Response
import uvicorn
import httpx
import os
import base64

app = FastAPI(title="Voice Agent")

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/incoming-call")
async def incoming_call(request: Request):
    """Webhook que o Twilio chama quando recebe uma ligação"""
    
    # Gera o áudio primeiro
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
                timeout=10.0
            )
            
            if response.status_code == 200:
                audio_base64 = base64.b64encode(response.content).decode('utf-8')
                
                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>data:audio/mpeg;base64,{audio_base64}</Play>
</Response>"""
            else:
                # Fallback pro TTS do Twilio
                twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="pt-BR">Olá! Você ligou para o agente de voz. Como posso ajudar?</Say>
</Response>"""
                
    except Exception as e:
        print(f"Erro Deepgram: {e}")
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="pt-BR">Olá! Você ligou para o agente de voz. Como posso ajudar?</Say>
</Response>"""
    
    return Response(content=twiml, media_type="application/xml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
