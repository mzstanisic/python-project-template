"""
Retrieve config values from the config.yml file in the base project directory,
and environment variables from either the system or an included .env file.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

import utils
import yaml
from dotenv import load_dotenv

# setup the logger
logger = logging.getLogger(__name__)
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


class Config:
    """
    Class for the user Config object. Contains information from the config.yaml
    and .env file if present.
    """

    def __init__(
        self,
        log_retention_period: int,
        email_port: int,
        email_smtp_server: str,
        email_sender_email: str,
        email_password: str,
        email_receiver_email: str,
    ):
        """
        Initializes the Config object with the given properties.

        :param log_retention_period: How many days to keeps logs for.
        """
        self.log_retention_period = log_retention_period or 30
        self.email_port = email_port
        self.email_smtp_server = email_smtp_server
        self.email_sender_email = email_sender_email
        self.email_password = email_password
        self.email_receiver_email = email_receiver_email

    def __repr__(self):
        """
        Provides a string representation of the Config object.
        """
        return (
            f"log_retention_period={self.log_retention_period}\n"
            f"email_port={self.email_port}\n"
            f"email_smtp_server={self.email_smtp_server}\n"
            f"email_sender_email={self.email_sender_email}\n"
            f"email_password={self.email_password}\n"
            f"email_receiver_email={self.email_receiver_email}\n"
        )


def validate_config(config_path: Path) -> dict:
    """
    Retrieve config settings from `config.yml` and validate them.

    :param1 config_path (Path): The path to the config file.
    :return (dict): A dictionary with values from the config file.
    """

    # check that the config path provided is a file
    if not config_path.is_file():
        logger.error(
            "The path %s is not a valid file. "
            "Add a config.yml file to the base directory.",
            config_path,
        )
        raise FileNotFoundError(
            f"The path {config_path} is not a valid file. "
            "Add a config.yml file to the base directory."
        )

    # load the config.yml file
    config = yaml.safe_load(open(config_path, encoding="utf-8"))

    # check each optional configuration option
    # and provide a default if it is empty
    if config.get("log_retention_period") is None:
        config["log_retention_period"] = 30
        logger.warning(
            "Configuration field 'log_retention_period' in config.yml is empty. "
            "Using default: %s",
            config["log_retention_period"],
        )

    return config


def validate_env(env_path: Path) -> dict:
    """
    Retrieve environment variables trying the system first, then a `.env` file.
    Finally, validate them.

    :param1 env_path (Path): The path to the environment file.
    :return (dict): A dictionary with values from the environment file.
    """
    env = {
        "email_port": None,
        "email_smtp_port": None,
        "email_sender_email": None,
        "email_password": None,
        "email_receiver_email": None,
    }

    env["email_port"] = os.environ.get("EMAIL_PORT")
    env["email_smtp_port"] = os.environ.get("EMAIL_SMTP_SERVER")
    env["email_sender_email"] = os.environ.get("EMAIL_SENDER_EMAIL")
    env["email_password"] = os.environ.get("EMAIL_PASSWORD")
    env["email_receiver_email"] = os.environ.get("EMAIL_RECEIVER_EMAIL")

    # if no system environment variables, check file
    if None in env.values():
        logger.info("No system environment variables found. Trying .env file...")

        if not env_path.is_file():
            logger.error(
                "The path %s is not a valid file."
                "Add system environment variables or a .env file to the resources directory.",
                env_path,
            )
            raise FileNotFoundError(
                f"The path {env_path} is not a valid file. "
                "Add system environment variables or a .env file to the resources directory."
            )

        load_dotenv(env_path)

        env["email_port"] = os.environ.get("EMAIL_PORT")
        env["email_smtp_port"] = os.environ.get("EMAIL_SMTP_SERVER")
        env["email_sender_email"] = os.environ.get("EMAIL_SENDER_EMAIL")
        env["email_password"] = os.environ.get("EMAIL_PASSWORD")
        env["email_receiver_email"] = os.environ.get("EMAIL_RECEIVER_EMAIL")

        if None in env.values():
            logger.error(
                "Some or all .env file variables are empty. "
                "Update %s to include all necessary environment variables.",
                env_path,
            )
            raise RuntimeError(
                "Some or all .env file variables are empty. "
                f"Update {env_path} to include all necessary environment variables."
            )

        logger.info("Retrieved environment variables from .env file.")
        return env

    logger.info("Obtained environment variables from system.")
    return env


def get_config() -> Config:
    """
    Looks for a valid config.yml file in the base project directory.
    If there is none, uses defaults.

    :returns: A Config object that includes a data format and paths.
    """
    config_path = Path(__file__).parent / "../config.yml"
    config = validate_config(config_path)

    # in production, can use system environment variables instead
    # assumes the .env file is required. If not, this can be removed
    env_path = Path(__file__).parent / "../.env"
    env = validate_env(env_path)

    config = Config(
        log_retention_period=config.get("log_retention_period"),
        email_port=env.get("email_port"),
        email_smtp_server=env.get("email_smtp_server"),
        email_sender_email=env.get("email_sender_email"),
        email_password=env.get("email_password"),
        email_receiver_email=env.get("email_receiver_email"),
    )

    # clean old logs
    utils.clean_old_logs(log_path, config.log_retention_period)

    return config


if __name__ == "__main__":
    user_config = get_config()
    print(f"\n-----config.py-----\n{repr(user_config)}")
