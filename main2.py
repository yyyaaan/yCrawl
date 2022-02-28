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
        return render_template("welcome.html", header1="Data Processor Endpoint", text1=data_process_monitor())



@app.route('/simplelogging', methods=['POST', 'GET'])
def simplelogging():
    # curl -i -H "Content-Type: application/json" -X POST -d '{"VMID":"y-crawl-x", "log": "new log service"}' http://127.0.0.1:8080/simplelogging
    if request.method == 'POST':
        try:
            print(request.json['log'])
            return "Success", 200
        except:
            print("Error im Simple Logging Service")
            return RES400

    else:
        try:
            log_content = request.args.get('log')
            print(log_content)
            output_text = f"Simple Logging OK [{request.method}] Content: {log_content}"
            return render_template("welcome.html", header1="Success", text1=output_text)
        except:
            return render_template("welcome.html", header1="Sorry!", text1=f"Request to Simple Logging Service Failed")



# NOT served from Appengine, only from VM/local
@app.route("/xyz")
def xyz():
    return render_template("welcome.html", header1="Extended-Service", text1="extended functions are available")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7999, debug=True)

