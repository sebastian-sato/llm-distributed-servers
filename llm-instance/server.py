from fastapi import FastAPI, HTTPException
import uvicorn
from llm import generate
from resource_profile import get_resource_profile
import asyncio

app = FastAPI()

max_characters = get_resource_profile()

with open("./SHARED-TOKEN.txt", 'r') as f:
    shared_token = f.read().split('\n')[0]
    print("SHARED TOKEN:",'"'+shared_token+'"')

inference_semaphore = asyncio.Semaphore(1)

async def run_llm(payload, max_tokens):
    response = generate(payload, max_tokens)
    return {"message": response}

def prevent_oom(payload):
    character_counts = []
    for msg in payload["messages"]:
        character_counts.append(len(msg))
    while sum(character_counts) > max_characters:
        # Remove old context until we've reached safe maximum character count.
        # Note that we must do it two at a time to keep the expected format.
        payload["messages"].pop(0)
        payload["messages"].pop(0)
        character_counts.pop(0)
        character_counts.pop(0)
    if len(payload["messages"]) == 0:
        raise HTTPException(
            status_code=413,
            detail={"error":"Prompt too big","msg":"Recieved prompt of a larger character length than is allowed"}
        )
    return payload


@app.post("/llminstance")
async def llm_instance_server(data: dict):
    if "token" not in data:
        raise HTTPException(
            status_code=401,
            detail={"error": "Failed to authenticate", "msg": "Token not supplied."}
        )
    elif data["token"] != shared_token:
        raise HTTPException(
            status_code=401,
            detail={"error": "Failed to authenticate", "msg": "Invalid token."}
        )

    if "payload" not in data:
        print("PAYLOAD MISSING")
        raise HTTPException(
            status_code=400,
            detail={"error": "Missing Required Field", "msg": "The 'payload' key must be provided."}
        )

    payload = data["payload"]

    # Do quick character count check
    if len(payload["messages"]) > max_characters: # Wait, isn't this still an issue?
        raise HTTPException(
            status_code=413,
            detail={"error":"Prompt too big","msg":"Recieved prompt of a larger character length than is allowed"}
        )
    
    # Ensure total conversation history size is not too big
    payload = prevent_oom(payload)

    # Handle optional fields with manual defaults
    max_tokens = data.get("max_tokens", 250)

    if not isinstance(max_tokens, int):
        print("INVALID VALUE FOR MAX TOKENS")
        raise HTTPException(status_code=400, detail="max_tokens must be an integer")

    try:
        async with inference_semaphore:
            return await run_llm(payload["messages"], max_tokens)
    except :
        return

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
