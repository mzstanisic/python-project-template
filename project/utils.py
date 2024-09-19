"""
Provides utility functions to the rest of the modules in the package.
"""

import logging
import platform
import smtplib
import ssl
from datetime import datetime, timedelta
from pathlib import Path

import config

logger = logging.getLogger(__name__)


def logger_setup() -> None:
    """
    Sets up the logger.
    """
    # setup the logger
    log_path = Path(__file__).parent / "../logs/"
    log_path.mkdir(parents=True, exist_ok=True)

    # config the logger
    logging.basicConfig(
        filename=log_path / datetime.now().strftime("%Y-%m-%d.log"),
        encoding="utf-8",
        level=logging.DEBUG,    # can change to INFO when moving to production
        format="%(asctime)s :: %(levelname)-8s :: %(module)s.%(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def clean_old_logs(log_dir: Path, days: int = 30) -> None:
    """
    Remove old logs from the log folder to prevent buildup.

    :param1 log_dir (Path): The path to the log directory.
    :param2 days (int): The number of days to keep logs for.
    :return: None
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    for log_file in log_dir.glob("*.log"):
        file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
        if file_date < cutoff_date:
            log_file.unlink()
            logger.info("Deleted old log file: %s", log_file)


def send_email(c_config, message: str, exit_status: str = 'SUCCESS') -> None:
    """
    Sends an email upon program completion with a success
    or error message.

    :param1 c_config (Config): The config which contains email
    credential info pulled from the system environment variables or .env file.
    :param2 message (str): The success or error message to send.
    :param3 exit_status (str): The exit status of the application.
    """

    if not c_config.enable_email_notifications:
        logger.info("Email notifications are disabled. Update 'config.yml' to enable.")
        return

    cwd = Path.cwd()

    # if message is an error, exit_status = 'Error'

    message = (
        f"Subject: {cwd.stem} - {exit_status}"
        f"     Exit Status: {exit_status}\n"
        f"Application Name: {cwd.stem}\n"
        f"       Timestamp: {datetime.now()}\n"
        f"            Host: {platform.node()}\n"
        f"       Directory: {cwd}\n"
        f"    Last Run Log: {logger.root.handlers[0].baseFilename}\n"
        f"Operating System: {platform.system()} {platform.release()}\n"
        f"  Python Version: {platform.python_version()}\n\n"
        f"{message}"
    )

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            c_config.email_smtp_server, c_config.email_port, context=context
        ) as server:
            server.login(c_config.email_sender_email, c_config.email_password)
            server.sendmail(
                c_config.email_sender_email,
                c_config.email_receiver_email,
                message
            )
    except Exception as e:
        logger.error("Failed sending email: %s", e)

    logger.info("Email notification sent to: %s", c_config.email_receiver_email)


if __name__ == "__main__":
    user_config = config.get_config()
    print("\n-----utils.py-----\n")
