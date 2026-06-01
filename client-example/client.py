import requests
import json

SERVER_IP = "192.168.50.88"
PORT = "8000"
URL = f"http://{SERVER_IP}:{PORT}/llmaccess"

INCLUDE_LLM_RESPONSE_CONTEXT = True

with open("./PASSWORD.txt", 'r') as f:
    PASSWORD = f.read().split('\n')[0].strip()
    print("USING PASSWORD:",PASSWORD)

def sendAndRecieve(payload):
    payload["pass"] = PASSWORD
    return requests.post(URL, json=payload, timeout=60)

# Maintain conversation history locally
local_chat_state = {
    "messages": [
    ],
}

# Simple chat loop example for talking with the chatbot over the terminal, you can replace this with your own
# application integration
done = False
while not done:
    # Get user prompt
    prompt = input("User: ")
    local_chat_state["messages"].append({"role":"user","content":prompt})

    # Send prompt to the LLM server
    server_payload = {"payload": local_chat_state, "max_tokens": 500}

    # Receive response
    response = sendAndRecieve(server_payload)
    
    try:
        if response.status_code == 200:
            # Success
            response_data = response.json()
            response = response_data["message"]["message"] # WHAT??

            print("\nAssistant response: \n\n" + response + "\n")

            # Update local conversation history
            if INCLUDE_LLM_RESPONSE_CONTEXT:
                local_chat_state["messages"].append({"role":"assistant","content":response})
            else:
                # Reduces memory usage but makes it so the LLM can't see its own responses to user prompts
                local_chat_state["messages"].append({"role":"assistant","content":""})
        else:
            # Report HTTPExceptions 
            print(f"Server Error (Status {response.status_code}):")
            try:
                # Show JSON response
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                # Fallback if the server returned raw text instead of JSON
                print(response.text)
    except requests.exceptions.ConnectionError:
        print(
            f"Could not connect to {URL}. If you are using Tailscale on the server side, check that Tailscale is also running on your device."
        )
    except requests.exceptions.Timeout:
        print("The request timed out. The LLM server is taking a while to respond.")
