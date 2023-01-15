from flask import jsonify
from core import app
from core.apis.assignments import student_assignments_resources
from core.apis.assignments.teacher import teacher_assignments_resources
from core.errors import ERROR_HANDLERS
from core.libs import helpers

app.register_blueprint(student_assignments_resources, url_prefix='/student')
app.register_blueprint(teacher_assignments_resources, url_prefix='/teacher')


@app.route('/')
def ready():
    response = jsonify({
        'status': 'ready',
        'time': helpers.get_utc_now()
    })

    return response


@app.errorhandler(Exception)
def handle_error(exception):
    return ERROR_HANDLERS.get(exception.__class__, Exception).get_error_response(exception)
