import json


class BasePythonSchemaException(Exception):
    pass


class PythonSchemaException(BasePythonSchemaException):
    pass


class InvalidValueError(BasePythonSchemaException):
    pass


class ValidationError(BasePythonSchemaException):
    pass


class NotSetError(BasePythonSchemaException):
    pass


# class MultipleValidationError(BaseValidationError):
#     """Aggregated errors from validatin, used to make a proper response in
#     human readable form.
#     """
#     def __init__(self, schema, errors, *args, **kwargs):
#         self.errors = errors
#         self.schema = schema
#
#         super().__init__(*args, **kwargs)
#
#     def get_errors(self):
#         """Method returns errors in a format that could be easily consumed by
#         other parts of the system.
#
#         Ie.
#         {
#             'username': {
#                 'error_code': '40-20',
#                 'errors': [
#                     'Username cannot be empty',
#                 ],
#             },
#             'address': {
#                 'error_code': '12-20',
#                 'errors': {
#                     'city': {
#                         'error_code': '25-13',
#                         'errors': [
#                             'City is not recognised',
#                         ]
#                     },
#                     'post_code': {
#                         'error_code': '25-16',
#                         'errors': [
#                             'Post code cannot be empty',
#                         ],
#                     },
#                 },
#             },
#         }
#         """
#         # this import is on purpose to avoid cyclic-imports
#         from magicarp import tools
#
#         tmp = {}
#
#         for key, errors in self.errors.items():
#             tmp[key] = {
#                 'error_code': tools.helpers.make_error_code(key, self.schema),
#                 'errors': errors,
#             }
#
#         return tmp
#
#     def __str__(self):
#         return json.dumps(self.get_errors())
