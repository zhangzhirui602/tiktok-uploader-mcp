"""Handles authentication for TikTokUploader"""

from http import cookiejar
from time import sleep, time
from typing import Any, cast

from playwright.sync_api import Page, expect

from tiktok_uploader import config, logger
from tiktok_uploader.browsers import browser_t, get_browser, get_persistent_browser
from tiktok_uploader.types import Cookie, ProxyDict, cookie_from_dict
from tiktok_uploader.utils import green


class AuthBackend:
    """
    Handles authentication for TikTokUploader
    """

    username: str
    password: str
    cookies: list[Cookie]
    cookies_path: str | None
    cookies_str: str | None
    cookies_list: list[Cookie]
    sessionid: str | None

    def __init__(
        self,
        username: str = "",
        password: str = "",
        cookies_list: list[Cookie] | None = None,
        cookies: str | None = None,
        cookies_str: str | None = None,
        sessionid: str | None = None,
    ):
        """
        Creates the authentication backend

        Keyword arguments:
        - username -> the accounts's username or email
        - password -> the account's password

        - cookies -> a list of cookie dictionaries of cookies which is Playwright-compatible
        """
        if (username and not password) or (password and not username):
            raise InsufficientAuth()

        self.cookies_path = cookies
        self.cookies_str = cookies_str
        self.cookies_list = list(cookies_list) if cookies_list else []
        self.sessionid = sessionid
        self.cookies = []

        has_cookie_input = bool(
            self.cookies_path or self.cookies_str or self.cookies_list or self.sessionid
        )
        if not (has_cookie_input or (username and password)):
            raise InsufficientAuth()

        self.username = username
        self.password = password

        if cookies:
            logger.debug(green("Authenticating browser with cookies"))
        elif username and password:
            logger.debug(green("Authenticating browser with username and password"))
        elif sessionid:
            logger.debug(green("Authenticating browser with sessionid"))
        elif self.cookies_list:
            logger.debug(green("Authenticating browser with cookies_list"))

    def authenticate_agent(self, page: Page) -> Page:
        """
        Authenticates the agent using the browser backend
        """
        if not self.cookies:
            self.cookies = self._resolve_cookies()

        if not self.cookies and self.username and self.password:
            self.cookies = login(page, username=self.username, password=self.password)

        if not self.cookies:
            raise InsufficientAuth(
                "No valid authentication source found. Provide a valid cookies file, cookies list/string, sessionid, or username/password."
            )

        logger.debug(green("Authenticating browser with cookies"))

        # Fix cookie keys for Playwright
        playwright_cookies = []
        for cookie in self.cookies:
            c = cookie.copy()
            if "expiry" in c:
                c["expires"] = c.pop("expiry")
            # Playwright requires strict types for sameSite
            if "sameSite" in c:
                if c["sameSite"] not in ["Strict", "Lax", "None"]:
                    c.pop("sameSite")

            # Playwright might fail if domain starts with a dot
            # if c.get("domain", "").startswith("."):
            #     c["domain"] = c["domain"][1:]

            # logger.debug(f"Adding cookie: {c}")
            print(f"DEBUG: Adding cookie: {c}")
            playwright_cookies.append(c)

        try:
            for pc in playwright_cookies:
                try:
                    page.context.add_cookies([cast(Any, pc)])
                except Exception as e:
                    print(f"DEBUG: Failed to add individual cookie {pc['name']}: {e}")
        except Exception as e:
            logger.error(f"Failed to add cookies: {e}")

        page.goto(str(config.paths.main))

        # Check if we are redirected to a login or explore page
        current_url = page.url
        if "login" in current_url or "explore" in current_url:
            # Check if we have the sessionid cookie
            cookies = page.context.cookies()
            has_sessionid = any(c["name"] == "sessionid" for c in cookies)
            if not has_sessionid:
                logger.error(
                    f"Redirected to {current_url} and sessionid cookie is missing"
                )
                raise InsufficientAuth(
                    f"Authentication failed: Redirected to {current_url}. Please ensure your cookies are valid and include a sessionid."
                )

        # WaitForTitle is not directly available, but we can wait for load or selector
        # Using expect(page).to_have_title(...) is better but authenticate_agent expects to return page.
        # We can just wait for network idle or a specific element.
        # However, for title check:
        import re

        expect(page).to_have_title(
            re.compile(r"TikTok"), timeout=config.explicit_wait * 1000
        )

        return page

    def _resolve_cookies(self) -> list[Cookie]:
        resolved_cookies: list[Cookie] = []

        if self.cookies_path:
            try:
                resolved_cookies.extend(self.get_cookies(path=self.cookies_path))
            except OSError as error:
                logger.warning(
                    "Could not read cookies file '%s': %s",
                    self.cookies_path,
                    error,
                )

        if self.cookies_str:
            resolved_cookies.extend(self.get_cookies(cookies_str=self.cookies_str))

        if self.cookies_list:
            resolved_cookies.extend(self.cookies_list)

        if self.sessionid:
            resolved_cookies.append({"name": "sessionid", "value": self.sessionid})

        return resolved_cookies

    def get_cookies(
        self, path: str | None = None, cookies_str: str | None = None
    ) -> list[Cookie]:
        """
        Gets cookies from the passed file using the netscape standard
        """
        if path:
            with open(path, encoding="utf-8") as file:
                lines = file.read().split("\n")
        elif cookies_str is not None:
            lines = cookies_str.split("\n")
        else:
            raise ValueError("Must have either a path or a cookies_str")

        return_cookies: list[Cookie] = []
        for line in lines:
            split = line.split("\t")
            if len(split) < 6:
                continue

            split = [x.strip() for x in split]

            name = split[5]
            value = split[6]
            domain = split[0]
            path = split[2]

            cookie: Cookie = {
                "name": name,
                "value": value,
                "domain": domain,
                "path": path,
            }

            try:
                cookie["expiry"] = int(split[4])
            except ValueError:
                pass

            return_cookies.append(cookie)  # type: ignore
        return return_cookies


def login_accounts(
    page: Page | None = None, accounts=[(None, None)], *args, **kwargs
) -> dict[str, list[Cookie]]:
    """
    Authenticates the accounts using the browser backend and saves the required credentials

    Keyword arguments:
    - page -> the playwright page to use
    - accounts -> a list of tuples of the form (username, password)
    """
    page = page or get_browser(*args, **kwargs)

    cookies = {}
    for account in accounts:
        username, password = get_username_and_password(account)

        cookies[username] = login(page, username, password)

    return cookies


def login(page: Page, username: str, password: str) -> list[Cookie]:
    """
    Logs in the user using the email and password
    """
    assert username and password, "Username and password are required"

    # checks if the browser is on TikTok
    if str(config.paths.main) not in page.url:
        page.goto(str(config.paths.main))

    # checks if the user is already logged in
    # We check cookies in context
    cookies = page.context.cookies()
    session_cookie = next(
        (c for c in cookies if c["name"] == config.selectors.login.cookie_of_interest),
        None,
    )

    if session_cookie:
        # clears the existing cookies
        page.context.clear_cookies()

    # goes to the login site
    page.goto(str(config.paths.login))

    # selects and fills the login and the password
    username_field = page.locator(f"xpath={config.selectors.login.username_field}")
    username_field.wait_for(state="visible", timeout=config.explicit_wait * 1000)
    username_field.clear()
    username_field.fill(username)

    password_field = page.locator(f"xpath={config.selectors.login.password_field}")
    password_field.clear()
    password_field.fill(password)

    # submits the form
    submit = page.locator(f"xpath={config.selectors.login.login_button}")
    submit.click()

    print(f"Complete the captcha for {username}")

    # Wait until the session id cookie is set
    # Playwright doesn't have a direct "wait for cookie" so we poll or wait for navigation
    start_time = time()
    while True:
        cookies = page.context.cookies()
        if any(c["name"] == config.selectors.login.cookie_of_interest for c in cookies):
            break
        sleep(0.5)
        if time() - start_time > config.explicit_wait:
            raise InsufficientAuth()

    # wait until the url changes
    # page.wait_for_url(lambda url: str(config.paths.login) not in url) # simplified
    # or just wait for it to not be login
    try:
        page.wait_for_function(
            f"window.location.href !== '{config.paths.login}'",
            timeout=config.explicit_wait * 1000,
        )
    except Exception:
        pass  # might have already changed

    return page.context.cookies()  # type: ignore[return-value]


def get_username_and_password(login_info: tuple | dict):
    """
    Parses the input into a username and password
    """
    if not isinstance(login_info, dict):
        return login_info[0], login_info[1]

    # checks if they used email or username
    if "email" in login_info:
        return login_info["email"], login_info["password"]
    elif "username" in login_info:
        return login_info["username"], login_info["password"]

    raise InsufficientAuth()


def save_cookies(path: str, cookies: list[Cookie]) -> None:
    """
    Saves the cookies to a netscape file
    """
    # saves the cookies to a file
    cookie_jar = cookiejar.MozillaCookieJar(path)
    # No need to load for new file or we can if we want to append
    # cookie_jar.load()

    for cookie in cookies:
        cookie_jar.set_cookie(cookie_from_dict(cookie))

    cookie_jar.save()


def setup_profile(
    profile_dir: str,
    browser: browser_t = "chrome",
    proxy: ProxyDict | None = None,
    timeout: int = 300,
) -> None:
    """
    Opens a visible browser with the given persistent profile directory and
    waits for the user to manually log in to TikTok.

    Once a ``sessionid`` cookie is detected the browser is closed and the
    profile is saved to *profile_dir* automatically by Playwright.

    Parameters
    ----------
    profile_dir:
        Path to the directory where the browser profile will be stored.
        The directory is created if it does not exist.
    browser:
        Browser to use (default: ``"chrome"``).
    proxy:
        Optional proxy settings.
    timeout:
        How many seconds to wait for the user to log in (default: 300 = 5 min).
    """
    import os

    os.makedirs(profile_dir, exist_ok=True)

    logger.info("Opening browser — please log in to TikTok within %d seconds.", timeout)

    context, page = get_persistent_browser(
        profile_dir=profile_dir,
        name=browser,
        headless=False,
        proxy=proxy,
    )

    try:
        page.goto("https://www.tiktok.com/login")

        _LOGIN_SESSION_COOKIES = {"sessionid", "sessionid_ss", "sid_tt"}

        start = time()
        while True:
            cookies = context.cookies()
            cookie_names = {c["name"] for c in cookies}
            if cookie_names & _LOGIN_SESSION_COOKIES:
                logger.info(green("Login detected — saving profile to %s"), profile_dir)
                break
            # Also detect login by URL leaving the login pages
            if "tiktok.com/login" not in page.url and "tiktok.com" in page.url:
                logger.info(
                    green("Login detected via redirect — saving profile to %s"),
                    profile_dir,
                )
                break
            if time() - start > timeout:
                logger.error(
                    "Timed out. Current URL: %s | Cookies present: %s",
                    page.url,
                    cookie_names,
                )
                raise TimeoutError(
                    f"Login not completed within {timeout} seconds. "
                    "Please re-run the setup command and log in faster."
                )
            sleep(1)
    finally:
        context.close()


def setup_profile_from_cookies(
    profile_dir: str,
    cookies_path: str,
    browser: browser_t = "chrome",
    proxy: ProxyDict | None = None,
) -> None:
    """
    Initialises a persistent browser profile from an existing cookies file.

    This is the recommended first-time setup when manual login is blocked by
    TikTok's anti-bot detection.  The cookies are injected into the profile
    once; afterwards uploads can use ``--profile`` instead of ``--cookies``.

    Parameters
    ----------
    profile_dir:
        Directory where the persistent profile will be stored.
    cookies_path:
        Path to a Netscape-format cookies file (e.g. ``cookies.txt``).
    browser:
        Browser to use (default: ``"chrome"``).
    proxy:
        Optional proxy settings.
    """
    import os

    os.makedirs(profile_dir, exist_ok=True)

    auth = AuthBackend(cookies=cookies_path)
    cookies = auth._resolve_cookies()
    if not cookies:
        raise ValueError(f"Could not load any cookies from '{cookies_path}'")

    context, page = get_persistent_browser(
        profile_dir=profile_dir,
        name=browser,
        headless=True,
        proxy=proxy,
    )

    try:
        # Inject cookies into the persistent context
        playwright_cookies = []
        for cookie in cookies:
            c = dict(cookie)
            if "expiry" in c:
                c["expires"] = c.pop("expiry")
            if "sameSite" in c and c["sameSite"] not in ("Strict", "Lax", "None"):
                c.pop("sameSite")
            playwright_cookies.append(c)

        context.add_cookies(playwright_cookies)  # type: ignore[arg-type]

        # Navigate to TikTok to let the session activate and persist
        page.goto(str(config.paths.main))

        final_cookies = {c["name"] for c in context.cookies()}
        if not (final_cookies & {"sessionid", "sessionid_ss", "sid_tt"}):
            raise ValueError(
                "Cookies were injected but no session cookie found. "
                "Your cookies file may be expired or invalid."
            )

        logger.info(green("Session verified — profile saved to %s"), profile_dir)
    finally:
        context.close()


class InsufficientAuth(Exception):
    """
    Insufficient authentication:

    > TikTok uses cookies to keep track of the user's authentication or session.

    Either:
        - Use a cookies file passed as the `cookies` argument
            - easily obtained using https://github.com/kairi003/Get-cookies.txt-LOCALLY
        - Use a cookies list passed as the `cookies_list` argument
            - can be obtained from your browser's developer tools under storage -> cookies
            - only the `sessionid` cookie is required
    """

    def __init__(self, message: str | None = None):
        super().__init__(message or self.__doc__)
