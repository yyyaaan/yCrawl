
from os import getenv
from requests import post
from random import randint


def send_df_as_flex(df, cols=['title', 'content'], text="info", color="RANDOM", msg_endpoint="XXX", reciever="cloud"):

    msg_list = [{"title": x[0], "content": x[1]} for x in df[cols].values]

    titles = set([x["title"] for x in msg_list])
    bubbles = []
    for t in titles:
        title_color = f"#{randint(0,255):02X}{randint(0,255):02X}{randint(0,255):02X}" \
                if color == "RANDOM" else color


        bubbles.append({
            "type": "bubble",
            "size": "micro",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": title_color,
                "contents": [{
                    "type": "text",
                    "text": str(t),
                    "size": "xs",
                    "color": "#FFFFFF",
                    "wrap": True
                }]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                        "type": "text",
                        "text": x["content"],
                        "size": "xs",
                        "color": "#aaaaaa",
                        "wrap": True
                    } for x in msg_list if x["title"]==t]
            }
        })

    flex_json = {"type": "carousel", "contents": bubbles}
    if len(msg_endpoint)>10:
        try:
            res = post(msg_endpoint, json = {
                "AUTH": 'this is a key to authenticate ycrawl worker, coordinator and other communication. ', #getenv("AUTHKEY"), 
                "TO": reciever,
                "TEXT": text,
                "FLEX": flex_json
            })
            print(f"{res.status_code} {res.text}")                
        except Exception as e:
            print(flex_json)
            print(f"failed to post line message due to {str(e)}")

    return flex_json
