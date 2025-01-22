from marshmallow import Schema, fields, validate


class RegistrationSchema(Schema):
    email = fields.Email(required=True)
    username = fields.Str(required=True,
                          validate=validate.Length(min=3,
                                                   max=80))
    password = fields.Str(required=True, validate=validate.Length(min=8))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


def validate_registration(data):
    schema = RegistrationSchema()
    return schema.load(data)


def validate_login(data):
    schema = LoginSchema()
    return schema.load(data)
