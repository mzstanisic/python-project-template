"""
The running script.
"""

import config


def run_pipeline():
    """
    Runs the main project pipeline.
    """
    # get the processed user config
    user_config = config.get_config()


if __name__ == "__main__":
    run_pipeline()
