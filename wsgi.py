from main2 import app

if __name__ == "__main__":
    app.run()

# apt install gunicorn python3-gunicorn python3-pastedeploy python3-setproctitle python3-tornado
# gunicorn --bind 0.0.0.0:7999 wsgi:app
