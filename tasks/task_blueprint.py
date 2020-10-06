from flask import request, Blueprint, g
from loguru import logger
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import DataError

from tasks.models import Task
from tasks.schemas import TaskSchema, TaskFilterSchema
from tasks.auth import Auth
from tasks.custom_response import custom_response

tasks_api = Blueprint('tasks', __name__)
task_schema = TaskSchema()
task_filter_schema = TaskFilterSchema()


@tasks_api.route('/', methods=['GET'])
@Auth.auth_required
def all_tasks():
    tasks_list = Task.query.filter_by(owner=int(g.user['id'])).all()
    serialized_tasks = task_schema.dump(tasks_list, many=True)
    return custom_response(serialized_tasks, 200)


@tasks_api.route('/new', methods=['POST'])
@Auth.auth_required
def new_task():
    """ Create new task """
    req_data = request.get_json()
    try:
        data = task_schema.load(req_data)
    except ValidationError as validation_error:
        return custom_response(validation_error.messages, 400)

    task = Task(data)
    task.owner = int(g.user['id'])
    try:
        task_id = task.save()
    except DataError:
        return custom_response({
            "error": "Wrong state. State can be one of the following: 'Новая', 'в Работе', 'Запланированная', 'Завершённая' "
        }, 400)

    return custom_response({
        'created task ID': task_id
    },
        200)


@tasks_api.route('/<int:task_id>', methods=['PUT', 'GET'])
@Auth.auth_required
def task_get_edit(task_id):
    """ Gets one task by id or edits it """
    if request.method == "PUT":
        # Edit task
        req_data = request.get_json()
        try:
            data = task_schema.load(req_data, partial=True)
        except ValidationError as validation_error:
            return custom_response(validation_error.messages, 400)

        task = Task.query.filter_by(
            id=task_id, owner=int(g.user['id'])).first()
        if not task:
            return custom_response({
                "error": "You have no tasks with this id"
            }, 200)
        try:
            task.update(data)
        except DataError:
            return custom_response({
                "error": "Wrong state. State can be one of the following: 'Новая', 'в Работе', 'Запланированная', 'Завершённая' "
            }, 400)
        serialized_task = task_schema.dump(task)
        return custom_response(serialized_task, 200)

    # Get one task
    elif request.method == "GET":
        task = Task.query.filter_by(
            id=task_id, owner=int(g.user['id'])).first()
        if not task:
            return custom_response({
                "error": "You have no tasks with this id"
            }, 200)
        serialized_task = task_schema.dump(task)
        return custom_response(serialized_task, 200)


@tasks_api.route('/filter', methods=['GET'])
@Auth.auth_required
def filter_tasks():
    """ Filter tasks by state, range of due datetimes """
    req_data = request.get_json()
    try:
        data = task_filter_schema.load(req_data, partial=True)
    except ValidationError as validation_error:
        return custom_response(validation_error.messages, 400)

    tasks = Task.query.filter_by(owner=int(g.user['id']))
    if not tasks:
        return custom_response({}, 200)
    if data.get('state'):
        tasks = tasks.filter_by(state=data.get('state'))
    if data.get('due_min'):
        tasks = tasks.filter(Task.due.isnot(None))
        tasks = tasks.filter(Task.due >= data.get('due_min'))
    if data.get('due_max'):
        tasks = tasks.filter(Task.due.isnot(None))
        tasks = tasks.filter(Task.due <= data.get('due_max'))

    tasks = tasks.all()
    serialized_tasks = task_schema.dump(tasks, many=True)
    return custom_response(serialized_tasks, 200)
