from flask import Flask, render_template, request, Response
from Coordinator.main import call_coordinator
from Frontend.vmmanager import SECRET, vm_list_all, vm_shutdown, vm_startup
from Frontend.functions import *
from Frontend.monitor import *
from Frontend.costmanager import *

# other global vars from functions
app = Flask(__name__)
RES403 = Response("Forbidden", 403)
RES400 = Response("Error", 400)


@app.route("/")
def main():
    return render_template("welcome.html", header1="YYYaaannn App Engine", text1="There is nothing here.")
    

# cron job only
@app.route("/checkin")
def checkin():
    if not request.headers.get('X-Appengine-Cron'):
        return RES403

    if done_for_today():
        print("Check-in: completion noted from file object")
        return "Success", 200

    all_servers = list(BATCH_REF.keys())

    # only start VM when itself has more tasks remaining
    status, message, n_done = [True], "", 0
    for the_vm in all_servers:
        urls = call_coordinator(batch=BATCH_REF[the_vm], total_batches=len(BATCH_REF))
        the_n = len([x for x in urls.split("\n") if x != ""])
        if the_n < META['retry-threshold']:
            message += f" {the_vm}/{the_n}"
            n_done +=1
        else: 
            status.append(vm_startup(the_vm))

    if len(message):
        print("VM Manager: no action" + message)

    # all completed may not be catched by notify done due to async
    if n_done == len(all_servers) or determine_all_completed(caller=None, servers_required=all_servers):
        on_all_completed()
        return "Success", 200

    return ("Success" if min(status) else "Error"), (200 if min(status) else 400)


# pass-controlled interactions
@app.route("/vmaction", methods=['POST'])
def vmaction():
    try:
        if request.form['PASS'] != SECRET['PASS']:
            return RES403
        vmid, action = request.form['VMID'], request.form['ACTION']
        vm_startup(vmid) if action == "START" else vm_shutdown(vmid)
        return render_template( 
            "welcome.html", 
            header1="VM Action Success", 
            text1=f"Acknowledged and request forwareded {action} {vmid}",
            meta_redirect='<meta http-equiv="refresh" content="1;url=/sub-vmstatus" />')
    except Exception as e:
        print(f"VM control violation due to {str(e)}")
        return RES400


# serve completion
@app.route("/notifydone", methods=['POST'])
def notifydone(): 
    if not verify_cloud_auth(request.json): 
        return RES403

    if (get_secret("ycrawl-keep-alive") == TODAY_0):
        print("Completion noted and keep alive")
        return "Success", 200

    status = True
    try:
        vmid = request.json['VMID']
        status = vm_shutdown(vmid)
        all_done = determine_all_completed(caller=vmid, servers_required=list(BATCH_REF.keys()))
        if all_done:
            on_all_completed()
        return ("Success" if status else "Error"), (200 if status else 400)

    except Exception as e:
        print(f"Error in serving completion notification due to {str(e)}")
        return RES400



@app.route("/coordinator", methods=['POST', 'GET'])
def coordinator():
    if request.method == 'GET':
        res = call_coordinator()
        the_len = len([x for x in res.split("\n") if x != ""])
        print(f'Coordinator requested {the_len} to GET-client')
        return res

    if not verify_cloud_auth(request.json): 
        return RES403

    try:
        vmid = request.json['VMID'].lower()
        if vmid not in BATCH_REF.keys():
            return RES403
        res = call_coordinator(batch=BATCH_REF[vmid], total_batches=len(BATCH_REF))
        the_len = len([x for x in res.split("\n") if x != ""])
        print(f'Coordinator requested {the_len} {vmid}')
        return res
    except Exception as e:
        print(f"Error in serving coordinator due to {str(e)}")
        return Response({'success': False, 'reason': str(e)}, 400,  mimetype='application/json')


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


@app.route('/files')
def files():
    links = [rule.rule for rule in app.url_map.iter_rules()]
    all_files, info_str = storage_file_viewer(META['scope'])
    return render_template(
        "files.html", 
        gs_link = f"https://console.cloud.google.com/storage/browser/{GSBUCKET}/{RUN_MODE}/{datetime.now().strftime('%Y%m/%d')}",
        info_str = info_str,
        all_files = all_files,
        count=len(links),
        items=sorted(links))



@app.route("/sub-logviewer")
def sub_logviewer():
    return render_template( "sub-logviewer.html", costs=aws_cost(days=5), logs_by_vm=get_simple_log())


@app.route("/sub-vmstatus")
def sub_vmstatus():
    n_running, vm_list = vm_list_all()
    return render_template("sub-vmstatus.html", vm_status_list=vm_list)


@app.route("/overview")
def overview():
    info, n_all, n_todo, n_done, n_forfeit, n_error, nu_error =  call_coordinator(info_only=True)
    all_files, info_str = storage_file_viewer(META['scope'])
    return render_template(
        "overview.html",
        completed_percent = f"{(1-n_todo/n_all):.2%}",
        n_jobs = f"{n_all-n_todo}/{n_all}",
        jobs_detail = f"{n_done} completed<br/>{nu_error}({n_error})+{n_forfeit} issues",
        jobs_str = info,
        info_str = info_str,
        all_files = all_files,
        gs_link = f"https://console.cloud.google.com/storage/browser/{GSBUCKET}/{RUN_MODE}/{datetime.now().strftime('%Y%m/%d')}",
        )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)

 