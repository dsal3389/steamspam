import sys
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By


# although it says `SteamClassName`
# it also include steam ID names
class SteamClassName:
    PROFILE_NAME = "actual_persona_name"
    COMMENT_BOX = "commentthread_Profile_{profileid}_textarea"
    COMMENT_BOX_ERROR = "commentthread_Profile_{profileid}_entry_error"



class SteamDriver:
    STEAM_DOMAIN = "steamcommunity.com"
    STEAM_PROFILE = f"https://{STEAM_DOMAIN}/profiles/" + "{profileid}"
    STEAM_LOGIN = f"https://{STEAM_DOMAIN}/login/home/?goto=profiles%2F" + "{profileid}"

    def __init__(self, profileid: str) -> None:
        self._profileid = profileid
        self._webdriver = webdriver.Chrome()
        self._element_cache = {}

    def login(self) -> None:
        self._wait_for_redirect(self.STEAM_LOGIN.format(profileid=self._profileid),)

    def comment(self, message: str) -> None:
        comment_error_info = self._find_element(By.ID, SteamClassName.COMMENT_BOX_ERROR.format(profileid=self._profileid))
        comment_box = self._find_element(
            By.ID, 
            SteamClassName.COMMENT_BOX.format(profileid=self._profileid)
        )

        comment_box.send_keys(message)
        comment_box.submit()

        # try to submit the message until
        # there are no error messages
        while comment_error_info.text:
            time.sleep(5)
            comment_box.submit()

    def get_username(self) -> str:
        assert self._webdriver.current_url == self.STEAM_PROFILE.format(profileid=self._profileid)
        return self._find_element(By.CLASS_NAME, SteamClassName.PROFILE_NAME).text

    def _find_element(self, by: str, value: str, *, cached=True) -> webdriver.remote.webelement.WebElement:
        """fetching information from webdriver and caching the results for next time"""
        key = f"{by}::{value}"

        if not cached or key not in self._element_cache:
            self._element_cache[key] = self._webdriver.find_element(by, value)
        return self._element_cache[key]

    def _wait_for_redirect(self, url: str) -> None:
        self._webdriver.get(url)

        # block the process until we are no longer in the current URL
        while self._webdriver.current_url == url:
            time.sleep(0.8)


class SteamProfile:

    def __init__(self, profile: str, message: str) -> None:
        self.message = message
        self.profile = self._parse_profile(profile)
        self._steamdriver = SteamDriver(profileid=self.profile)

    def spam(self) -> None:
        self._steamdriver.login()

        print(f"start spamming user {self._steamdriver.get_username()}")
        while True:
            self._steamdriver.comment(self.message)
            time.sleep(1)

    @staticmethod
    def _parse_profile(profile: str) -> str:
        if profile.startswith(('http', SteamDriver.STEAM_DOMAIN)):
            return profile.rsplit('/', maxsplit=1)[-1]
        return profile


def parse_argv() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--profile", help="steam profile full link or ID", required=True)
    parser.add_argument("-m", "--message", help="message to spam, or file path that contains the message", required=True)
    return parser.parse_args(sys.argv[1:])


def main() -> None:
    args = parse_argv()
    message = ""

    if args.message.startswith(('/', './')):
        with open(args.message, 'r') as f:
            message = f.read()
    else:
        message = args.message
    
    steamprofile = SteamProfile(args.profile, message)
    steamprofile.spam()


if __name__ == '__main__':
    main()

