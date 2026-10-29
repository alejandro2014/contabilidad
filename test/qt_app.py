import atexit
import os
import shutil
import tempfile

# The widgets are tested without opening any window
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtCore import QCoreApplication, QSettings
from PySide6.QtWidgets import QApplication

# The settings of the tests go to a temporary folder, never to the ones of the app
SETTINGS_DIR = tempfile.mkdtemp(prefix='contabilidad-settings-')
atexit.register(shutil.rmtree, SETTINGS_DIR, ignore_errors=True)
QSettings.setDefaultFormat(QSettings.Format.IniFormat)
QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, SETTINGS_DIR)
QCoreApplication.setOrganizationName('contabilidad-tests')
QCoreApplication.setApplicationName('contabilidad-tests')

def get_app():
    # Qt allows a single application per process, shared by all the widget tests
    return QApplication.instance() or QApplication([])

def clear_settings():
    QSettings().clear()
