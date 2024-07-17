import sys

from screens.screenAbout import ScreenAbout
from screens.screenBrowseResults import ScreenBrowseResults
from screens.screenExit import ScreenExit
from screens.screenMain import ScreenMain
from screens.screenPeek import ScreenPeek
from screens.screenResults import ScreenResults
from screens.screenVT import ScreenVT
from screens.screenWelcome import ScreenWelcome
from screens.screenStartScan import ScreenStartScan
from screens.screenMgmt import ScreenMgmt

from dotenv import load_dotenv

import configLogger
import logging

configLogger.config()
logger = logging.getLogger(__name__)

def main():
    logger.info("MED was launched")
    try:
        load_dotenv()

        ScreenWelcome()
        ScreenStartScan()
        ScreenMain()
        ScreenExit()
        ScreenResults()
        ScreenPeek()
        ScreenAbout()
        ScreenBrowseResults()
        ScreenVT()

        ScreenMgmt.get_screen("welcome")
    except KeyboardInterrupt:
        logger.info("Ctrl+C caught. We can't believe you are leaving :(")
        sys.exit(0)


if __name__ == '__main__':
    main()
