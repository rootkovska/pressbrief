import logging
import os
from datetime import datetime
from exceptions import PressBriefError
from pathlib import Path
from typing import Any

import yaml
from aws_lambda_context import LambdaContext
from dropbox import Dropbox
from dropbox.exceptions import AuthError, BadInputError

from exporter.pdf_exporter import PDFExporter
from newspaper.newspaper import Newspaper
from utils.parser import str2bool

logger = logging.getLogger()
if logger.hasHandlers():
    logger.setLevel(logging.INFO)
else:
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)


def lambda_handler(event: Any, context: LambdaContext) -> None:
    main()


def main() -> None:
    logger.info("Loading parameters ...")

    if not any(storage in os.environ for storage in ["BRIEF_OUTPUT", "DROPBOX_ACCESS_TOKEN"]):
        raise PressBriefError("No storage provided!")

    # bot parameters
    limit_per_rss = os.getenv("LIMIT_PER_RSS", 10)
    url2qrcode = str2bool(os.getenv("URL2QR", "False"))

    # storage pamaeters
    brief_output = os.getenv("BRIEF_OUTPUT", None)
    dropbox_access_token = os.getenv("DROPBOX_ACCESS_TOKEN", None)

    try:
        limit_per_rss = int(limit_per_rss)

        if limit_per_rss > 50:
            logger.warning("LIMIT_PER_RSS is greater than 50! Reducing to maximum (50) ...")
            limit_per_rss = 50
    except ValueError:
        logger.warning("LIMIT_PER_RSS must be an integer! Setting to default (10) ...")
        limit_per_rss = 10

    if brief_output is not None:
        try:
            brief_output = Path(brief_output)
            if not brief_output.is_dir():
                brief_output.mkdir(parents=True)
            if not os.access(brief_output, os.W_OK):
                raise PermissionError(f"No write permissions on `{brief_output}`!")
        except (FileExistsError, PermissionError):
            logger.error(f"The path `{brief_output}` is broken!")
            raise

    if dropbox_access_token is not None:
        try:
            dbx = Dropbox(dropbox_access_token)
            dbx.users_get_current_account()
        except (AuthError, BadInputError):
            logger.error("`DROPBOX_ACCESS_TOKEN` is invalid!")
            raise

    logger.info("Parameters loaded")
    logger.info("Extracting news ...")

    config_path = Path(os.getcwd()) / "config.yaml"
    if not config_path.is_file():
        raise PressBriefError("`config.yaml` file not found!")

    try:
        with open(config_path) as f:
            config = yaml.full_load(f.read())

        newspapers = map(
            lambda newspaper: Newspaper(
                config["newspapers"][newspaper]["name"], config["newspapers"][newspaper]["rss"], limit_per_rss,
            ),
            config["newspapers"],
        )
    except KeyError:
        logger.error("Corrupted `config.yaml` file!")
        raise

    logger.info("Exporting brief ...")

    exporter = PDFExporter(url2qrcode)
    date_str = datetime.now().strftime("%Y-%m-%d")

    title = f"Daily Press Brief ({date_str})"
    subtitle = f"{limit_per_rss} news/RSS feeds, {datetime.now().strftime('%H:%M:%S UTC')}"
    pdf = exporter.export(newspapers, title, subtitle)

    filename = f"pressbrief-{date_str}.pdf"
    if brief_output is not None:
        logger.info("Saving locally...")

        brief_path = brief_output / filename
        with open(brief_path, "wb") as f:
            f.write(pdf.getbuffer())

        logger.info("Brief saved")
    if dropbox_access_token is not None:
        logger.info("Uploading to Dropbox...")

        brief_path = Path("/") / filename
        dbx.files_upload(pdf.getvalue(), brief_path.as_posix())

        logger.info("Brief uploaded")


if __name__ == "__main__":
    main()
