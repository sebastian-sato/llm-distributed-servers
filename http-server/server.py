from fastapi import FastAPI, HTTPException, Request
import uvicorn
from verify import verify_password
import asyncio
import json
import requests
import itertools
import time

app = FastAPI()

# In a real production environment you'd most likely want to use a database for keeping track of this
verified_hosts = []
blocked_hosts = []
attempted_auth = {}
MAX_FAILED_AUTHENTICATION_ATTEMPTS = 3


# Get list of instances
with open("INSTANCES.json", "r") as f:
    instances = json.load(f)["INSTANCES"]
num_instances = len(instances)
instance_index = 0

MAX_ATTEMPTS = 5
def sendAndRecieve(payload, attempt=1):
    global instances, num_instances, instance_index
    server_payload = {"payload":payload}
    if num_instances <= 0 or attempt > MAX_ATTEMPTS:
        raise HTTPException(
            status_code=500,
            detail={"error": "Server Outage", "msg": "Unable to process request at this time."}
        )
    selected_instance = instances[instance_index]
    URL = f"http://{selected_instance["IP"]}:{selected_instance["PORT"]}/llminstance"
    server_payload["token"] = selected_instance["SHARED-TOKEN"]
    try:
        instance_index += 1
        if instance_index >= num_instances:
            instance_index = 0
        response = requests.post(URL, json=server_payload, timeout=60)
        return response.json()
    except Exception as e:
        print(e)
        print("UNRESPONSIVE LLM INSTANCE!")
        #del(instances[instance_index]) # Remove unresponsive instance from list
        #num_instances -= 1             #
        return sendAndRecieve(payload, attempt=attempt+1) # Try again

@app.post("/llmaccess")
async def lmm_access_server(data: dict, request: Request):
    print("HOST:",request.client.host)
    
    client_ip = request.client.host
    # Reject blocked hosts
    if client_ip in blocked_hosts:
        raise HTTPException(
            status_code=403,
            detail={"error": "Unauthorized", "msg": "You do not have access to this service."}
        )

    if client_ip not in verified_hosts:
        # Request verification
        if "pass" not in data:
            raise HTTPException(
                status_code=401,
                detail={"error": "Passphrase Error", "msg": "Passphrase not supplied."}
            )
        elif verify_password(data["pass"]) == False: # Vulnerable to a DoS attack, which is why blocking is needed.
            if client_ip not in attempted_auth:
                attempted_auth[client_ip] = 1
            else:
                attempted_auth[client_ip] += 1

            if attempted_auth[client_ip] > MAX_FAILED_AUTHENTICATION_ATTEMPTS:
                blocked_hosts.append(client_ip)
            
            raise HTTPException(
                status_code=401,
                detail={"error": "Passphrase Error", "msg": "Invalid passphrase."}
            )
        verified_hosts.append(client_ip)

    if "payload" not in data:
        raise HTTPException(
            status_code=400,
            detail={"error": "Missing Required Field", "msg": "The 'payload' key must be provided."}
        )

    payload = data["payload"]

    # Handle optional fields with manual defaults
    max_tokens = data.get("max_tokens", 250)

    if not isinstance(max_tokens, int):
        raise HTTPException(status_code=400, detail="max_tokens must be an integer")

    response_text = sendAndRecieve(payload)

    return {"message": response_text} # Error happens here

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
