from marshmallow import Schema, fields


class TaskSchema(Schema):
    """ Task schema """
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    state = fields.Str(required=True)
    due = fields.DateTime()


class TaskFilterSchema(Schema):
    """ Schema to filter tasks by state and due date range """
    state = fields.Str()
    due_min = fields.DateTime()
    due_max = fields.DateTime()


class UserSchema(Schema):
    """ User schema """
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
