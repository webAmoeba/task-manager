import os

import rollbar
from django.apps import AppConfig
from dotenv import load_dotenv


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "task_manager.apps.core"

    def ready(self):
        load_dotenv()
        is_debug = os.getenv("DEBUG") == "True"
        rollbar.init(
            access_token=os.getenv("rollbar_token"),
            environment="development" if is_debug else "production",
            code_version="1.0",
            root=os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../..")
            ),
        )
