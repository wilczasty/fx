import notify_run as nr
ENDPOINT = "https://notify.run/vWCzV1WWabtiW3nNXrp6"

def send_notification(msg):
    notify = nr.Notify(endpoint=ENDPOINT)
    notify.send(msg)