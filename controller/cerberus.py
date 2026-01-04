import copy
import re
import string
import uuid

import cerberus
from cerberus import errors as cerberus_errors

from config.non_env import FILTER_DATE_FORMAT, URL_REGEX
from utils.util import sanitize_string_input


class CustomErrorHandler(cerberus_errors.BasicErrorHandler):
    messages = cerberus_errors.BasicErrorHandler.messages.copy()
    # Override existing error messages here
    messages.update(
        {
            cerberus_errors.REQUIRED_FIELD.code: "{field} is a mandatory field",
        }
    )

    def __init__(self, tree=None, custom_messages=None):
        super().__init__(tree)
        self.custom_messages = custom_messages or {}

    def __iter__(self):
        pass

    def _format_message(self, field, error):
        tmp = self.custom_messages
        for i, j in enumerate(error.schema_path):
            try:
                tmp = tmp[j]
            except KeyError:
                if i == len(error.schema_path) - 1 and "any" in tmp:
                    return tmp["any"]
                return super()._format_message(field, error)
        if isinstance(tmp, dict):
            return super()._format_message(field, error)
        return tmp


class CustomValidator(cerberus.Validator):
    """
    A custom validator extending Cerberus where specific errors messages can be specified per field
    AND/OR
    Existing error messages can be overridden in class CustomErrorHandler
    Usage:
        schema = {"name": {"minlength": 2, "error_messages": {"minlength": "Length is too few"}}}
        v = CustomValidator(schema)
        v.validate({"name": "0"})   # => False
        v.errors                    # => {'name': ['Length is too few']}
    """

    def __init__(self, *args, **kwargs):
        if args:
            if "schema" in kwargs:
                raise TypeError("got multiple values for argument 'schema'")
            schema = args[0]
        else:
            schema = kwargs.pop("schema")
        if isinstance(schema, dict):
            schema = copy.deepcopy(schema)
            self.populate_custom_messages(schema)
            args = [schema] + list(args[1:])
        kwargs["error_handler"] = CustomErrorHandler(custom_messages=self.custom_messages)
        super().__init__(*args, **kwargs)
        self.custom_messages = {}
        self._allowed_func_caches = {}

    def populate_custom_messages(self, schema):
        self.custom_messages = {}
        queue = [(schema, self.custom_messages)]
        while queue:
            item, msgs = queue.pop()
            if "error_messages" in item:
                assert isinstance(item["error_messages"], dict)
                msgs.update(item.pop("error_messages"))
            for k, v in item.items():
                if isinstance(v, dict):
                    msgs[k] = {}
                    queue.append((v, msgs[k]))

    def _validate_maxlength_sanitized(self, max_length, field, value):
        if value is None:
            return
        sanitized_value = sanitize_string_input(value)
        if len(sanitized_value) > max_length:
            self._error(field, "Max length can be: {}".format(max_length))

    def _validate_minlength_sanitized(self, min_length, field, value):
        if value is None:
            return
        sanitized_value = sanitize_string_input(value)
        if len(sanitized_value) < min_length:
            self._error(field, "Min length can be: {}".format(min_length))

    def _validate_type_strict_integer(self, value):
        if isinstance(value, type(2)):
            return True
        return False


class CustomRules:
    @staticmethod
    def validate_password(field, value, error):
        length_check = len(value) >= 8
        lowercase_check = len(set(string.ascii_lowercase).intersection(set(value))) > 0
        uppercase_check = len(set(string.ascii_uppercase).intersection(set(value))) > 0
        digits_check = len(set(string.digits).intersection(set(value))) > 0
        punctuation_check = len(set(string.punctuation).intersection(set(value))) > 0
        if not (length_check and lowercase_check and uppercase_check and digits_check and punctuation_check):
            error(field, "Invalid password")

    @staticmethod
    def validate_uuid(field, value, error):
        try:
            uuid.UUID(value, version=4)
        except BaseException:
            error(field, "Invalid uuid")

    @staticmethod
    def validate_uuids_list(field, values, error):
        for value in values:
            try:
                uuid.UUID(value, version=4)
            except BaseException:
                error(field, "Invalid uuid")
                break

    @staticmethod
    def check_stripped_voicemail_name(field, value, error):
        if not value:
            pass
        elif not value.strip():
            error(
                field,
                "This voicemail greeting name is invalid. Please enter a valid name and try again",
            )

    @staticmethod
    def validate_url_if_not_empty(field, value, error):
        if not value:
            pass
        elif not re.search(URL_REGEX, value):
            error(
                field,
                "The value provided for {} is not an URL. Please provide a valid URL".format(field),
            )

    @staticmethod
    def validate_date_format(field, value, error):
        from datetime import datetime

        try:
            datetime.strptime(value, FILTER_DATE_FORMAT)
        except ValueError:
            error(field, "Invalid date string")
