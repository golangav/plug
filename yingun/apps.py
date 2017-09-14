from django.apps import AppConfig


class YingunConfig(AppConfig):
    name = 'yingun'

    def ready(self):
        super(YingunConfig,self).ready()

        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('yg')