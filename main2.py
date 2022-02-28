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
    if request.method == 'POST':
        if not verify_cloud_auth(request.json): 
            return RES403

        data_dir = str(getcwd()) + "/DataProcessor"
        send_line(text="Recieved pipeline initiation, pulling cloud storage data")
        Popen(["python3", "main.py"], cwd= data_dir, stdin=None, stdout=None, stderr=None)
        return "Success", 200
    
    else:
        return render_template("welcome.html", header1="Data Processor Started", text1="ETA 5-30 mins")
        # return RES403


# NOT served from Appengine, only from VM/local
@app.route("/xyz")
def xyz():
    return render_template("welcome.html", header1="Extended-Service", text1="extended functions are available")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7999, debug=True)

