# disable csrf protection
from webrecorder.basecontroller import BaseController
BaseController.validate_csrf = lambda *args, **kwargs: None

from webrecorder.main import application