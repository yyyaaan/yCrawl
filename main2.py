from os import getcwd
from subprocess import Popen
from Messenger.Line import send_line
from Frontend.functions import verify_cloud_auth
from main import *


#######################################################################
#   _____      _                 _          _   _                    _ 
#  | ____|_  _| |_ ___ _ __   __| | ___  __| | | |    ___   ___ __ _| |
#  |  _| \ \/ / __/ _ \ '_ \ / _` |/ _ \/ _` | | |   / _ \ / __/ _` | |
#  | |___ >  <| ||  __/ | | | (_| |  __/ (_| | | |__| (_) | (_| (_| | |
#  |_____/_/\_\\__\___|_| |_|\__,_|\___|\__,_| |_____\___/ \___\__,_|_|
#######################################################################

@app.route("/rundata", methods=["POST", "GET"])
def rundata():
    if request.method == 'GET':
        return render_template("welcome.html", header1=f"Data Processor Endpoint", text1=data_process_monitor())

    if (not verify_cloud_auth(request.json)) or ("VMID" not in request.json.keys()): 
        return RES403

    vmid = request.json["VMID"]
    try:
        if vmid == "local":
            data_dir = str(getcwd()) + "/DataProcessor"
            send_line(text="Recieved pipeline initiation, pulling cloud storage data in LOCAL")
            with open("log.log", "ab") as logfile:
                Popen(["python3", "main.py"], cwd= data_dir, stdin=None, stdout=logfile, stderr=logfile)
            return "OK", 200
        elif "STOP" in request.json:
            vm_shutdown(vmid)
        else:
            vm_startup(vmid)
        return "OK", 200
    except Exception as e:
        return f"Data processor failed {str(e)}", 400
        


@app.route("/sendline", methods=["POST"])
def sendline():
    info = "AUTH OK" if verify_cloud_auth(request.json) else "AUTH error"
    # if not verify_cloud_auth(request.json): 
    #     return RES403
    try:
        flex_json = request.json["FLEX"] if "FLEX" in request.json else None
        send_line(target=request.json["TO"], text=request.json["TEXT"], flex=flex_json)
        return f"Success {info}", 200
    except Exception as e:
        print(f"fail to send line due to {str(e)}")
        return f"{str(e)}", 400
    


# NOT served from Appengine, only from VM/local
@app.route("/xyz")
def xyz():
    return render_template("welcome.html", header1="Extended-Service", text1="Activated local extended service mode")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7999, debug=True)

