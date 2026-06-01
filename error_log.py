import os, sys, logging, traceback
from PyQt6 import QtCore

_LOG_FILE = None
_LOGGER = None


def setup(app_dir):
    global _LOG_FILE, _LOGGER
    _LOG_FILE = os.path.join(app_dir, "error.log")
    _LOGGER = logging.getLogger("SiteTools")
    _LOGGER.setLevel(logging.DEBUG)
    fh = logging.FileHandler(_LOG_FILE, mode="a", encoding="utf-8", delay=True)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    ))
    _LOGGER.addHandler(fh)

    def excepthook(exc_type, exc_value, exc_tb):
        lines = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        _LOGGER.critical("Unhandled exception:\n" + lines)
        if sys.stderr:
            sys.stderr.write(lines)

    sys.excepthook = excepthook

    def qt_message_handler(mode, context, message):
        level = {
            QtCore.QtMsgType.QtDebugMsg: logging.DEBUG,
            QtCore.QtMsgType.QtWarningMsg: logging.WARNING,
            QtCore.QtMsgType.QtCriticalMsg: logging.ERROR,
            QtCore.QtMsgType.QtFatalMsg: logging.CRITICAL,
            QtCore.QtMsgType.QtInfoMsg: logging.INFO,
        }.get(mode, logging.INFO)
        _LOGGER.log(level, "Qt: %s (line %d, %s)", message, context.line, context.file)

    QtCore.qInstallMessageHandler(qt_message_handler)

    _LOGGER.info("=== Site Tools started ===")


def log_exception(msg, exc_info=True):
    if _LOGGER:
        _LOGGER.exception(msg) if exc_info else _LOGGER.error(msg)


def debug(msg):
    if _LOGGER:
        _LOGGER.debug(msg)


def info(msg):
    if _LOGGER:
        _LOGGER.info(msg)


def warning(msg):
    if _LOGGER:
        _LOGGER.warning(msg)


def error(msg):
    if _LOGGER:
        _LOGGER.error(msg)


def critical(msg):
    if _LOGGER:
        _LOGGER.critical(msg)
