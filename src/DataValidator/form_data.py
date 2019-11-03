import re
from collections import OrderedDict


class _Null:
    def __bool__(self):
        return False


class _ValueBag:
    def __init__(self, key, value, error_msg=None):
        self._key = key
        self._value = value
        self._validator = _Null()
        self._error_msg = error_msg

    def get_key(self):
        return self._key

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def get_validator(self):
        return self._validator

    def set_validator(self, validator):
        self._validator = validator

    def set_error_msg(self, msg):
        self._error_msg = msg

    def get_error_msg(self):
        return '' if self._error_msg is None else self._error_msg


class ValidationError:
    def __init__(self, key, value, error=''):
        self._value = value
        self._key = key
        self._error = error

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    @property
    def error(self):
        return self._error

    def __str__(self):
        return f'Validation error for key {self.key} with value {self.value} and message {self.error}'

    def __repr__(self):
        return self.__str__()


class AttrsValidation:
    def __init__(self):
        self._errors = {}

    def has_error_for(self, key):
        return key in self._errors

    def get_error_for(self, key):
        return self._errors[key]

    def has_errors(self):
        return len(self._errors) > 0

    def __bool__(self):
        return self.has_errors()

    @property
    def errors(self):
        return tuple(self._errors.values())

    def add_error(self, key, error: ValidationError):
        self._errors[key] = error


class AttrsObject:
    ident_regex = re.compile('^[A-Za-z_][A-Za-z0-9_]*')

    def __init__(self, *attrs):
        object.__setattr__(self, '_dict', OrderedDict())
        for attr in attrs:
            if not self.ident_regex.match(attr):
                self._dict.clear()
                raise Exception(f'Cannot use this as identifier {attr}')
            self._dict[attr] = _ValueBag(attr, _Null())

    def __getattr__(self, key):
        if key not in self._dict:
            raise AttributeError(f'Key {key} is not present.')
        value_bag = self._dict.get(key)
        return value_bag.get_value()

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __setattr__(self, key, value):
        if key not in self._dict:
            raise AttributeError(f'Key {key} is not present.')
        value_bag = self._dict.get(key)
        value_bag.set_value(value)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def set_validator(self, key, validator, error_msg=None):
        if key not in self._dict:
            raise AttributeError(f'Key {key} is not present.')
        value_bag = self._dict.get(key)
        value_bag.set_validator(validator)
        value_bag.set_error_msg(error_msg)

    def set_regex_validator(self, key, regex, error_msg=None):
        if not isinstance(regex, type(self.ident_regex)):
            regex = re.compile(regex)

        def regex_validator(data):
            return regex.match(data)
        self.set_validator(key, regex_validator, error_msg=error_msg)

    def validate(self):
        attrs_validation = AttrsValidation()

        for key, value_bag in self._dict.items():
            value = value_bag.get_value()
            if isinstance(value, _Null):
                attrs_validation.add_error(key, ValidationError(key, value, 'Value was never added'))
            else:
                validator = value_bag.get_validator()
                if callable(validator):
                    if not validator(value):
                        attrs_validation.add_error(key, ValidationError(key, value, value_bag.get_error_msg()))

        return attrs_validation


class FormAttrs(AttrsObject):
    pass
