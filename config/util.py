import os

from config.non_env import CONFIG_ERROR_LOG_MESSAGE, ALERT_MESSAGE_PREPEND
from logger.logging import LoggerUtil


class Environment:
    @classmethod
    def get_string(cls, config_name, default=""):
        return str(os.getenv(config_name, default))

    @classmethod
    def get_int(cls, config_name, default=0):
        value = cls.get_string(config_name, default)
        try:
            value = int(eval(value))  # pylint: disable=eval-used
        except Exception:
            LoggerUtil.create_error_log(
                "{}:{}::Invalid int value:{} for {}".format(
                    ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE, value, config_name
                )
            )
            return default
        return value

    @classmethod
    def get_bool(cls, config_name, default=False):
        value = cls.get_string(config_name, default)
        try:
            value = bool(eval(value))  # pylint: disable=eval-used
        except Exception:
            LoggerUtil.create_error_log(
                "{}:{}::Invalid bool value:{} for {}".format(
                    ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE, value, config_name
                )
            )
            return default
        return value

    @classmethod
    def get_float(cls, config_name, default=0.0):
        value = cls.get_string(config_name, default)
        try:
            value = float(eval(value))  # pylint: disable=eval-used
        except Exception:
            LoggerUtil.create_error_log(
                "{}:{}::Invalid float value:{} for {}".format(
                    ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE, value, config_name
                )
            )
            return default
        return value

    @classmethod
    def get_list(cls, config_name, default=""):
        return cls.get_string(config_name, default).split(",")

    @classmethod
    def get_dict(cls, config_name, default="{}"):
        value = cls.get_string(config_name, default)
        try:
            value = eval(value)  # pylint: disable=eval-used
            assert isinstance(value, dict)
        except Exception:
            LoggerUtil.create_error_log(
                "{}:{}::Invalid dict value:{} for {}".format(
                    ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE, value, config_name
                )
            )
            return eval(default)  # pylint: disable=eval-used
        return value
