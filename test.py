from flask import Flask
from flask import render_template, request, redirect
import data_handler
from datetime import datetime 


app = Flask(__name__)


@app.route('/')
@app.route('/users')
def route_list():
    users = data_handler.get_all_users()
    return render_template("index.html", users = users)


if __name__ == '__main__':
    app.run()

# for run the python's flask server
# use> python -m flask run
# for automatic changes and debugger use> "python -m flask --debug run"