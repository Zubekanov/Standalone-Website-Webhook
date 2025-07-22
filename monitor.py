import os
import time
import requests

_ENV = {}

# Garbage .env access method as this is a light standalone script.
with open(os.path.join(os.path.dirname(__file__), '.env')) as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            value = value.strip('"').strip("'")
            _ENV[key] = value

def try_ping_url():
    ping_url = _ENV.get('PING_URL')
    if not ping_url:
        raise ValueError("PING_URL is not set in the environment variables.")
    try:
        response = requests.get(ping_url, timeout=5)
        
        response.raise_for_status()
        return response.status_code == 200
    except requests.RequestException as e:
        return False
    
def send_webhook_message(contents: str):
    time_str = f"<t:{int(time.time())}:t>"
    if "WEBHOOK" not in _ENV.keys():
        raise ValueError("WEBHOOK url is not set in the environment variables.")
    if "WEBHOOK_USERNAME" not in _ENV.keys() or "WEBHOOK_AVATAR" not in _ENV.keys():
        raise ValueError("WEBHOOK_USERNAME or WEBHOOK_AVATAR is not set in the environment variables.")
    payload = {
        "content": f"[{time_str}] {contents}",
        "username": _ENV.get('WEBHOOK_USERNAME'),
        "avatar_url": _ENV.get('WEBHOOK_AVATAR'),
    }
    try:
        response = requests.post(_ENV['WEBHOOK'], json=payload, timeout=5)
        response.raise_for_status()
        if response.status_code == 204:
            print("Webhook message sent successfully.")
            return True
        else:
            print(f"Webhook message sent with status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to send webhook message: {e}")
    return False

def run():
	ping_interval   = int(_ENV.get('PING_INTERVAL', 5))
	alert_threshold = int(_ENV.get('ALERT_THRESHOLD', 12))
	dropped = 0
	waiting = False

	while True:
		if try_ping_url():
			if waiting:
				send_webhook_message("Website is back up.")
				waiting = False
			dropped = 0
		else:
			dropped += 1
			if not waiting and dropped >= alert_threshold:
				send_webhook_message("Website is down.")
				waiting = True

		time.sleep(ping_interval)
          
if __name__ == "__main__":
    run()