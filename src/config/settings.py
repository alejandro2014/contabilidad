from PySide6.QtCore import QCoreApplication, QSettings

# Name of the app for the settings that are kept between sessions (window size, last screen, date range...)
ORGANIZATION_NAME = 'Contabilidad'
APPLICATION_NAME = 'Contabilidad'

def init_settings():
    QCoreApplication.setOrganizationName(ORGANIZATION_NAME)
    QCoreApplication.setApplicationName(APPLICATION_NAME)

def app_settings():
    # Where they are kept is up to Qt: the preferences of the user in macOS, the registry in Windows...
    return QSettings()
