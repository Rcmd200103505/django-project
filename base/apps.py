from django.apps import AppConfig


class BaseConfig(AppConfig):
    name = 'sample'


class UsersConfig(AppConfig):
    name = 'base'

    def ready(self):
       import base.signals
