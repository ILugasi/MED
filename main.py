from screens.screenAbout import ScreenAbout
from screens.screenBrowseResults import ScreenBrowseResults
from screens.screenExit import ScreenExit
from screens.screenMain import ScreenMain
from screens.screenPeek import ScreenPeek
from screens.screenResults import ScreenResults
from screens.screenWelcome import ScreenWelcome
from screens.screenStartScan import ScreenStartScan
from screens.screenMgmt import ScreenMgmt

from dotenv import load_dotenv
load_dotenv()

ScreenWelcome()
ScreenStartScan()
ScreenMain()
ScreenExit()
ScreenResults()
ScreenPeek()
ScreenAbout()
ScreenBrowseResults()

ScreenMgmt.get_screen("welcome")
