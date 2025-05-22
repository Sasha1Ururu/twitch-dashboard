==> ./__init__.py <==
VERSION = (4, 4, 0, '')

__version__ = '4.4.0'

==> ./helper.py <==
#  Copyright (c) 2020. Lena "Teekeks" During <info@teawork.de>
"""
Helper functions
----------------"""
import asyncio
import datetime
import logging
import time
import urllib.parse
import uuid
from logging import Logger
from typing import AsyncGenerator, TypeVar
from enum import Enum

from .type import AuthScope

from typing import Union, List, Type, Optional

__all__ = ['first', 'limit', 'TWITCH_API_BASE_URL', 'TWITCH_AUTH_BASE_URL', 'TWITCH_PUB_SUB_URL', 'TWITCH_CHAT_URL', 'TWITCH_EVENT_SUB_WEBSOCKET_URL',
           'build_url', 'get_uuid', 'build_scope', 'fields_to_enum', 'make_enum',
           'enum_value_or_none', 'datetime_to_str', 'remove_none_values', 'ResultType', 'RateLimitBucket', 'RATE_LIMIT_SIZES', 'done_task_callback']

T = TypeVar('T')

TWITCH_API_BASE_URL: str = "https://api.twitch.tv/helix/"
"""The base url to the Twitch API endpoints"""
TWITCH_AUTH_BASE_URL: str = "https://id.twitch.tv/oauth2/"
"""The base url to the twitch authentication endpoints"""
TWITCH_PUB_SUB_URL: str = "wss://pubsub-edge.twitch.tv"
"""The url to the Twitch PubSub websocket"""
TWITCH_CHAT_URL: str = "wss://irc-ws.chat.twitch.tv:443"
"""The url to the Twitch Chat websocket"""
TWITCH_EVENT_SUB_WEBSOCKET_URL: str = 'wss://eventsub.wss.twitch.tv/ws'
"""The url to the Twitch EventSub websocket"""


class ResultType(Enum):
    RETURN_TYPE = 0
    STATUS_CODE = 1
    TEXT = 2


def build_url(url: str, params: dict, remove_none: bool = False, split_lists: bool = False, enum_value: bool = True) -> str:
    """Build a valid url string

    :param url: base URL
    :param params: dictionary of URL parameter
    :param remove_none: if set all params that have a None value get removed |default| :code:`False`
    :param split_lists: if set all params that are a list will be split over multiple url parameter with the same name |default| :code:`False`
    :param enum_value: if true, automatically get value string from Enum values |default| :code:`True`
    :return: URL
    """

    def get_val(val):
        if not enum_value:
            return str(val)
        if isinstance(val, Enum):
            return str(val.value)
        return str(val)

    def add_param(res, k, v):
        if len(res) > 0:
            res += "&"
        res += str(k)
        if v is not None:
            res += "=" + urllib.parse.quote(get_val(v))
        return res

    result = ""
    for key, value in params.items():
        if value is None and remove_none:
            continue
        if split_lists and isinstance(value, list):
            for va in value:
                result = add_param(result, key, va)
        else:
            result = add_param(result, key, value)
    return url + (("?" + result) if len(result) > 0 else "")


def get_uuid() -> uuid.UUID:
    """Returns a random UUID"""
    return uuid.uuid4()


def build_scope(scopes: List[AuthScope]) -> str:
    """Builds a valid scope string from list

    :param scopes: list of :class:`~twitchAPI.type.AuthScope`
    :returns: the valid auth scope string
    """
    return ' '.join([s.value for s in scopes])


def fields_to_enum(data: Union[dict, list],
                   fields: List[str],
                   _enum: Type[Enum],
                   default: Optional[Enum]) -> Union[dict, list]:
    """Iterates a dict or list and tries to replace every dict entry with key in fields with the correct Enum value

    :param data: dict or list
    :param fields: list of keys to be replaced
    :param _enum: Type of Enum to be replaced
    :param default: The default value if _enum does not contain the field value
    """
    _enum_vals = [e.value for e in _enum.__members__.values()]

    def make_dict_field_enum(_data: dict,
                             _fields: List[str],
                             _enum: Type[Enum],
                             _default: Optional[Enum]) -> Union[dict, Enum, None]:
        fd = _data
        if isinstance(_data, str):
            if _data not in _enum_vals:
                return _default
            else:
                return _enum(_data)
        for key, value in _data.items():
            if isinstance(value, str):
                if key in fields:
                    if value not in _enum_vals:
                        fd[key] = _default
                    else:
                        fd[key] = _enum(value)
            elif isinstance(value, dict):
                fd[key] = make_dict_field_enum(value, _fields, _enum, _default)
            elif isinstance(value, list):
                fd[key] = fields_to_enum(value, _fields, _enum, _default)
        return fd

    if isinstance(data, list):
        return [make_dict_field_enum(d, fields, _enum, default) for d in data]
    else:
        return make_dict_field_enum(data, fields, _enum, default)


def make_enum(data: Union[str, int], _enum: Type[Enum], default: Enum) -> Enum:
    """Takes in a value and maps it to the given Enum. If the value is not valid it will take the default.

    :param data: the value to map from
    :param _enum: the Enum type to map to
    :param default: the default value"""
    _enum_vals = [e.value for e in _enum.__members__.values()]
    if data in _enum_vals:
        return _enum(data)
    else:
        return default


def enum_value_or_none(enum: Optional[Enum]) -> Union[None, str, int]:
    """Returns the value of the given Enum member or None

    :param enum: the Enum member"""
    return enum.value if enum is not None else None


def datetime_to_str(dt: Optional[datetime.datetime]) -> Optional[str]:
    """ISO-8601 formats the given datetime, returns None if datetime is None

    :param dt: the datetime to format"""
    return dt.astimezone().isoformat() if dt is not None else None


def remove_none_values(d: dict) -> dict:
    """Removes items where the value is None from the dict.
    This returns a new dict and does not manipulate the one given.

    :param d: the dict from which the None values should be removed"""
    return {k: v for k, v in d.items() if v is not None}


async def first(gen: AsyncGenerator[T, None]) -> Optional[T]:
    """Returns the first value of the given AsyncGenerator

    Example:

    .. code-block:: python

        user = await first(twitch.get_users())

    :param gen: The generator from which you want the first value"""
    try:
        return await gen.__anext__()
    except StopAsyncIteration:
        return None


async def limit(gen: AsyncGenerator[T, None], num: int) -> AsyncGenerator[T, None]:
    """Limits the number of entries from the given AsyncGenerator to up to num.

    This example will give you the currently 5 most watched streams:

    .. code-block:: python

        async for stream in limit(twitch.get_streams(), 5):
            print(stream.title)

    :param gen: The generator from which you want the first n values
    :param num: the number of entries you want
    :raises ValueError: if num is less than 1
    """
    if num < 1:
        raise ValueError('num has to be a int > 1')
    c = 0
    async for y in gen:
        c += 1
        if c > num:
            break
        yield y


class RateLimitBucket:
    """Handler used for chat rate limiting"""

    def __init__(self,
                 bucket_length: int,
                 bucket_size: int,
                 scope: str,
                 logger: Optional[logging.Logger] = None):
        """

        :param bucket_length: time in seconds the bucket is valid for
        :param bucket_size: the number of entries that can be put into the bucket
        :param scope: the scope of this bucket (used for logging)
        :param logger: the logger to be used. If None the default logger is used
        """
        self.scope = scope
        self.bucket_length = float(bucket_length)
        self.bucket_size = bucket_size
        self.reset = None
        self.content = 0
        self.logger = logger
        self.lock: asyncio.Lock = asyncio.Lock()

    def get_delta(self, num: int) -> Optional[float]:
        current = time.time()
        if self.reset is None:
            self.reset = current + self.bucket_length
        if current >= self.reset:
            self.reset = current + self.bucket_length
            self.content = num
        else:
            self.content += num
        if self.content >= self.bucket_size:
            return self.reset - current
        return None

    def left(self) -> int:
        """Returns the space left in the current bucket"""
        return self.bucket_size - self.content

    def _warn(self, msg):
        if self.logger is not None:
            self.logger.warning(msg)
        else:
            logging.warning(msg)

    async def put(self, num: int = 1):
        """Puts :code:`num` uses into the current bucket and waits if rate limit is hit

        :param num: the number of uses put into the current bucket"""
        async with self.lock:
            delta = self.get_delta(num)
            if delta is not None:
                self._warn(f'Bucket {self.scope} got rate limited. waiting {delta:.2f}s...')
                await asyncio.sleep(delta + 0.05)


RATE_LIMIT_SIZES = {
    'user': 20,
    'mod': 100
}


def done_task_callback(logger: Logger, task: asyncio.Task):
    """helper function used as a asyncio task done callback"""
    e = task.exception()
    if e is not None:
        logger.exception("Error while running callback", exc_info=e)

==> ./oauth.py <==
#  Copyright (c) 2020. Lena "Teekeks" During <info@teawork.de>
"""
User OAuth Authenticator and helper functions
=============================================

User Authenticator
------------------

:const:`~twitchAPI.oauth.UserAuthenticator` is an alternative to various online services that give you a user auth token.
It provides non-server and server options.

Requirements for non-server environment
***************************************

Since this tool opens a browser tab for the Twitch authentication, you can only use this tool on environments that can
open a browser window and render the `<twitch.tv>`__ website.

For my authenticator you have to add the following URL as a "OAuth Redirect URL": :code:`http://localhost:17563`
You can set that `here in your twitch dev dashboard <https://dev.twitch.tv/console>`__.

Requirements for server environment
***********************************

You need the user code provided by Twitch when the user logs-in at the url returned by :const:`~twitchAPI.oauth.UserAuthenticator.return_auth_url()`.

Create the UserAuthenticator with the URL of your webserver that will handle the redirect, and add it as a "OAuth Redirect URL"
You can set that `here in your twitch dev dashboard <https://dev.twitch.tv/console>`__.

.. seealso:: This tutorial has a more detailed example how to use UserAuthenticator on a headless server: :doc:`/tutorial/user-auth-headless`

.. seealso:: You may also use the CodeFlow to generate your access token headless :const:`~twitchAPI.oauth.CodeFlow`

Code example
************

.. code-block:: python

    from twitchAPI.twitch import Twitch
    from twitchAPI.oauth import UserAuthenticator
    from twitchAPI.type import AuthScope

    twitch = await Twitch('my_app_id', 'my_app_secret')

    target_scope = [AuthScope.BITS_READ]
    auth = UserAuthenticator(twitch, target_scope, force_verify=False)
    # this will open your default browser and prompt you with the twitch verification website
    token, refresh_token = await auth.authenticate()
    # add User authentication
    await twitch.set_user_authentication(token, target_scope, refresh_token)

User Authentication Storage Helper
----------------------------------

:const:`~twitchAPI.oauth.UserAuthenticationStorageHelper` provides a simplified way to store & reuse user tokens.

Code example
************

.. code-block:: python

      twitch = await Twitch(APP_ID, APP_SECRET)
      helper = UserAuthenticationStorageHelper(twitch, TARGET_SCOPES)
      await helper.bind()"

.. seealso:: See :doc:`/tutorial/reuse-user-token` for more information.


Class Documentation
-------------------
"""
import datetime
import json
import os.path
from pathlib import PurePath

import aiohttp

from .twitch import Twitch
from .helper import build_url, build_scope, get_uuid, TWITCH_AUTH_BASE_URL, fields_to_enum
from .type import AuthScope, InvalidRefreshTokenException, UnauthorizedException, TwitchAPIException
from typing import Optional, Callable, Awaitable, Tuple
import webbrowser
from aiohttp import web
import asyncio
from threading import Thread
from concurrent.futures import CancelledError
from logging import getLogger, Logger

from typing import List, Union

__all__ = ['refresh_access_token', 'validate_token', 'get_user_info', 'revoke_token', 'CodeFlow', 'UserAuthenticator', 'UserAuthenticationStorageHelper']


async def refresh_access_token(refresh_token: str,
                               app_id: str,
                               app_secret: str,
                               session: Optional[aiohttp.ClientSession] = None,
                               auth_base_url: str = TWITCH_AUTH_BASE_URL):
    """Simple helper function for refreshing a user access token.

    :param str refresh_token: the current refresh_token
    :param str app_id: the id of your app
    :param str app_secret: the secret key of your app
    :param ~aiohttp.ClientSession session: optionally a active client session to be used for the web request to avoid having to open a new one
    :param auth_base_url: The URL to the Twitch API auth server |default| :const:`~twitchAPI.helper.TWITCH_AUTH_BASE_URL`
    :return: access_token, refresh_token
    :raises ~twitchAPI.type.InvalidRefreshTokenException: if refresh token is invalid
    :raises ~twitchAPI.type.UnauthorizedException: if both refresh and access token are invalid (eg if the user changes
                their password of the app gets disconnected)
    :rtype: (str, str)
    """
    param = {
        'refresh_token': refresh_token,
        'client_id': app_id,
        'grant_type': 'refresh_token',
        'client_secret': app_secret
    }
    url = build_url(auth_base_url + 'token', {})
    ses = session if session is not None else aiohttp.ClientSession()
    async with ses.post(url, data=param) as result:
        data = await result.json()
    if session is None:
        await ses.close()
    if data.get('status', 200) == 400:
        raise InvalidRefreshTokenException(data.get('message', ''))
    if data.get('status', 200) == 401:
        raise UnauthorizedException(data.get('message', ''))
    return data['access_token'], data['refresh_token']


async def validate_token(access_token: str,
                         session: Optional[aiohttp.ClientSession] = None,
                         auth_base_url: str = TWITCH_AUTH_BASE_URL) -> dict:
    """Helper function for validating a user or app access token.

    https://dev.twitch.tv/docs/authentication/validate-tokens

    :param access_token: either a user or app OAuth access token
    :param session: optionally a active client session to be used for the web request to avoid having to open a new one
    :param auth_base_url: The URL to the Twitch API auth server |default| :const:`~twitchAPI.helper.TWITCH_AUTH_BASE_URL`
    :return: response from the api
    """
    header = {'Authorization': f'OAuth {access_token}'}
    url = build_url(auth_base_url + 'validate', {})
    ses = session if session is not None else aiohttp.ClientSession()
    async with ses.get(url, headers=header) as result:
        data = await result.json()
    if session is None:
        await ses.close()
    return fields_to_enum(data, ['scopes'], AuthScope, None)


async def get_user_info(access_token: str,
                        session: Optional[aiohttp.ClientSession] = None,
                        auth_base_url: str = TWITCH_AUTH_BASE_URL) -> dict:
    """Helper function to get claims information from an OAuth2 access token.

    https://dev.twitch.tv/docs/authentication/getting-tokens-oidc/#getting-claims-information-from-an-access-token

    :param access_token: a OAuth2 access token
    :param session: optionally a active client session to be used for the web request to avoid having to open a new one
    :param auth_base_url: The URL to the Twitch API auth server |default| :const:`~twitchAPI.helper.TWITCH_AUTH_BASE_URL`
    :return: response from the API
    """
    header = {'Authorization': f'Bearer {access_token}',
              'Content-Type': 'application/json'}
    url = build_url(auth_base_url + 'userinfo', {})
    ses = session if session is not None else aiohttp.ClientSession()
    async with ses.get(url, headers=header) as result:
        data = await result.json()
    if session is None:
        await ses.close()
    return data


async def revoke_token(client_id: str,
                       access_token: str,
                       session: Optional[aiohttp.ClientSession] = None,
                       auth_base_url: str = TWITCH_AUTH_BASE_URL) -> bool:
    """Helper function for revoking a user or app OAuth access token.

    https://dev.twitch.tv/docs/authentication/revoke-tokens

    :param str client_id: client id belonging to the access token
    :param str access_token: user or app OAuth access token
    :param ~aiohttp.ClientSession session: optionally a active client session to be used for the web request to avoid having to open a new one
    :param auth_base_url: The URL to the Twitch API auth server |default| :const:`~twitchAPI.helper.TWITCH_AUTH_BASE_URL`
    :rtype: bool
    :return: :code:`True` if revoking succeeded, otherwise :code:`False`
    """
    url = build_url(auth_base_url + 'revoke', {
        'client_id': client_id,
        'token': access_token
    })
    ses = session if session is not None else aiohttp.ClientSession()
    async with ses.post(url) as result:
        ret = result.status == 200
    if session is None:
        await ses.close()
    return ret


class CodeFlow:
    """Basic implementation of the CodeFlow User Authentication.

    Example use:

    .. code-block:: python

        APP_ID = "my_app_id"
        APP_SECRET = "my_app_secret"
        USER_SCOPES = [AuthScope.BITS_READ, AuthScope.BITS_WRITE]

        twitch = await Twitch(APP_ID, APP_SECRET)
        code_flow = CodeFlow(twitch, USER_SCOPES)
        code, url = await code_flow.get_code()
        print(url)  # visit this url and complete the flow
        token, refresh = await code_flow.wait_for_auth_complete()
        await twitch.set_user_authentication(token, USER_SCOPES, refresh)
    """
    def __init__(self,
                 twitch: 'Twitch',
                 scopes: List[AuthScope],
                 auth_base_url: str = TWITCH_AUTH_BASE_URL):
        """

        :param twitch: A twitch instance
        :param scopes: List of the desired Auth scopes
        :param auth_base_url: The URL to the Twitch API auth server |default| :const:`~twitchAPI.helper.TWITCH_AUTH_BASE_URL`
        """
        self._twitch: 'Twitch' = twitch
        self._client_id: str = twitch.app_id
        self._scopes: List[AuthScope] = scopes
        self.logger: Logger = getLogger('twitchAPI.oauth.code_flow')
        """The logger used for OAuth related log messages"""
        self.auth_base_url: str = auth_base_url
        self._device_code: Optional[str] = None
        self._expires_in: Optional[datetime.datetime] = None

    async def get_code(self) -> (str, str):
        """Requests a Code and URL from teh API to start the flow

        :return: The Code and URL used to further the flow
        """
        async with aiohttp.ClientSession(timeout=self._twitch.session_timeout) as session:
            data = {
                'client_id': self._client_id,
                'scopes': build_scope(self._scopes)
            }
            async with session.post(self.auth_base_url + 'device', data=data) as result:
                data = await result.json()
                self._device_code = data['device_code']
                self._expires_in = datetime.datetime.now() + datetime.timedelta(seconds=data['expires_in'])
                return data['user_code'], data['verification_uri']

    async def wait_for_auth_complete(self) -> (str, str):
        """Waits till the user completed the flow on teh website and then generates the tokens.

        :return: the generated access_token and refresh_token
        """
        if self._device_code is None:
            raise ValueError('Please start the code flow first using CodeFlow.get_code()')
        request_data = {
            'client_id': self._client_id,
            'scopes': build_scope(self._scopes),
            'device_code': self._device_code,
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
        }
        async with aiohttp.ClientSession(timeout=self._twitch.session_timeout) as session:
            while True:
                if datetime.datetime.now() > self._expires_in:
                    raise TimeoutError('Timed out waiting for auth complete')
                async with session.post(self.auth_base_url + 'token', data=request_data) as result:
                    result_data = await result.json()
                    if result_data.get('access_token') is not None:
                        # reset state for reuse before exit
                        self._device_code = None
                        self._expires_in = None
                        return result_data['access_token'], result_data['refresh_token']
                await asyncio.sleep(1)


class UserAuthenticator:
    """Simple to use client for the Twitch User authentication flow.
       """

    def __init__(self,
                 twitch: 'Twitch',
                 scopes: List[AuthScope],
                 force_verify: bool = False,
                 url: str = 'http://localhost:17563',
                 host: str = '0.0.0.0',
                 port: int = 17563,
                 auth_base_url: str = TWITCH_AUTH_BASE_URL):
        """

        :param twitch: A twitch instance
        :param scopes: List of the desired Auth scopes
        :param force_verify: If this is true, the user will always be prompted for authorization by twitch |default| :code:`False`
        :param url: The reachable URL that will be opened in the browser. |default| :code:`http://localhost:17563`
        :param host: The host the webserver will bind to. |default| :code:`0.0.0.0`
        :param port: The port that will be used for the webserver. |default| :code:`17653`
        :param auth_base_url: The URL to the Twitch API auth server |default| :const:`~twitchAPI.helper.TWITCH_AUTH_BASE_URL`
        """
        self._twitch: 'Twitch' = twitch
        self._client_id: str = twitch.app_id
        self.scopes: List[AuthScope] = scopes
        self.force_verify: bool = force_verify
        self.logger: Logger = getLogger('twitchAPI.oauth')
        """The logger used for OAuth related log messages"""
        self.url = url
        self.auth_base_url: str = auth_base_url
        self.document: str = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>pyTwitchAPI OAuth</title>
        </head>
        <body>
            <h1>Thanks for Authenticating with pyTwitchAPI!</h1>
        You may now close this page.
        </body>
        </html>"""
        """The document that will be rendered at the end of the flow"""
        self.port: int = port
        """The port that will be used for the webserver. |default| :code:`17653`"""
        self.host: str = host
        """The host the webserver will bind to. |default| :code:`0.0.0.0`"""
        self.state: str = str(get_uuid())
        """The state to be used for identification, |default| a random UUID"""
        self._callback_func = None
        self._server_running: bool = False
        self._loop: Union[asyncio.AbstractEventLoop, None] = None
        self._runner: Union[web.AppRunner, None] = None
        self._thread: Union[Thread, None] = None
        self._user_token: Union[str, None] = None
        self._can_close: bool = False
        self._is_closed = False

    def _build_auth_url(self):
        params = {
            'client_id': self._twitch.app_id,
            'redirect_uri': self.url,
            'response_type': 'code',
            'scope': build_scope(self.scopes),
            'force_verify': str(self.force_verify).lower(),
            'state': self.state
        }
        return build_url(self.auth_base_url + 'authorize', params)

    def _build_runner(self):
        app = web.Application()
        app.add_routes([web.get('/', self._handle_callback)])
        return web.AppRunner(app)

    async def _run_check(self):
        while not self._can_close:
            await asyncio.sleep(0.1)
        await self._runner.shutdown()
        await self._runner.cleanup()
        self.logger.info('shutting down oauth Webserver')
        self._is_closed = True

    def _run(self, runner: web.AppRunner):
        self._runner = runner
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, self.host, self.port)
        self._loop.run_until_complete(site.start())
        self._server_running = True
        self.logger.info('running oauth Webserver')
        try:
            self._loop.run_until_complete(self._run_check())
        except (CancelledError, asyncio.CancelledError):
            pass

    def _start(self):
        self._thread = Thread(target=self._run, args=(self._build_runner(),))
        self._thread.start()

    def stop(self):
        """Manually stop the flow

        :rtype: None
        """
        self._can_close = True

    async def _handle_callback(self, request: web.Request):
        val = request.rel_url.query.get('state')
        self.logger.debug(f'got callback with state {val}')
        # invalid state!
        if val != self.state:
            return web.Response(status=401)
        self._user_token = request.rel_url.query.get('code')
        if self._user_token is None:
            # must provide code
            return web.Response(status=400)
        if self._callback_func is not None:
            self._callback_func(self._user_token)
        return web.Response(text=self.document, content_type='text/html')

    def return_auth_url(self):
        """Returns the URL that will authenticate the app, used for headless server environments."""
        return self._build_auth_url()

    async def mock_authenticate(self, user_id: str) -> str:
        """Authenticate with a mocked auth flow via ``twitch-cli``

        For more info see :doc:`/tutorial/mocking`

        :param user_id: the id of the user to generate a auth token for
        :return: the user auth token
        """
        param = {
            'client_id': self._client_id,
            'client_secret': self._twitch.app_secret,
            'code': self._user_token,
            'user_id': user_id,
            'scope': build_scope(self.scopes),
            'grant_type': 'user_token'
        }
        url = build_url(self.auth_base_url + 'authorize', param)
        async with aiohttp.ClientSession(timeout=self._twitch.session_timeout) as session:
            async with session.post(url) as response:
                data: dict = await response.json()
        if data is None or data.get('access_token') is None:
            raise TwitchAPIException(f'Authentication failed:\n{str(data)}')
        return data['access_token']

    async def authenticate(self,
                           callback_func: Optional[Callable[[str, str], None]] = None,
                           user_token: Optional[str] = None,
                           browser_name: Optional[str] = None,
                           browser_new: int = 2,
                           use_browser: bool = True,
                           auth_url_callback: Optional[Callable[[str], Awaitable[None]]] = None):
        """Start the user authentication flow\n
        If callback_func is not set, authenticate will wait till the authentication process finished and then return
        the access_token and the refresh_token
        If user_token is set, it will be used instead of launching the webserver and opening the browser

        :param callback_func: Function to call once the authentication finished.
        :param user_token: Code obtained from twitch to request the access and refresh token.
        :param browser_name: The browser that should be used, None means that the system default is used.
                            See `the webbrowser documentation <https://docs.python.org/3/library/webbrowser.html#webbrowser.register>`__ for more info
                            |default|:code:`None`
        :param browser_new: controls in which way the link will be opened in the browser.
                            See `the webbrowser documentation <https://docs.python.org/3/library/webbrowser.html#webbrowser.open>`__ for more info
                            |default|:code:`2`
        :param use_browser: controls if a browser should be opened.
                            If set to :const:`False`, the browser will not be opened and the URL to be opened will either be printed to the info log or
                            send to the specified callback function (controlled by :const:`~twitchAPI.oauth.UserAuthenticator.authenticate.params.auth_url_callback`)
                            |default|:code:`True`
        :param auth_url_callback: a async callback that will be called with the url to be used for the authentication flow should
                            :const:`~twitchAPI.oauth.UserAuthenticator.authenticate.params.use_browser` be :const:`False`.
                            If left as None, the URL will instead be printed to the info log
                            |default|:code:`None`
        :return: None if callback_func is set, otherwise access_token and refresh_token
        :raises ~twitchAPI.type.TwitchAPIException: if authentication fails
        :rtype: None or (str, str)
        """
        self._callback_func = callback_func
        self._can_close = False
        self._user_token = None
        self._is_closed = False

        if user_token is None:
            self._start()
            # wait for the server to start up
            while not self._server_running:
                await asyncio.sleep(0.01)
            if use_browser:
                # open in browser
                browser = webbrowser.get(browser_name)
                browser.open(self._build_auth_url(), new=browser_new)
            else:
                if auth_url_callback is not None:
                    await auth_url_callback(self._build_auth_url())
                else:
                    self.logger.info(f"To authenticate open: {self._build_auth_url()}")
            while self._user_token is None:
                await asyncio.sleep(0.01)
            # now we need to actually get the correct token
        else:
            self._user_token = user_token
            self._is_closed = True

        param = {
            'client_id': self._client_id,
            'client_secret': self._twitch.app_secret,
            'code': self._user_token,
            'grant_type': 'authorization_code',
            'redirect_uri': self.url
        }
        url = build_url(self.auth_base_url + 'token', param)
        async with aiohttp.ClientSession(timeout=self._twitch.session_timeout) as session:
            async with session.post(url) as response:
                data: dict = await response.json()
        if callback_func is None:
            self.stop()
            while not self._is_closed:
                await asyncio.sleep(0.1)
            if data.get('access_token') is None:
                raise TwitchAPIException(f'Authentication failed:\n{str(data)}')
            return data['access_token'], data['refresh_token']
        elif user_token is not None:
            self._callback_func(data['access_token'], data['refresh_token'])


class UserAuthenticationStorageHelper:
    """Helper for automating the generation and storage of a user auth token.\n
    See :doc:`/tutorial/reuse-user-token` for more detailed examples and use cases.

    Basic example use:

    .. code-block:: python

      twitch = await Twitch(APP_ID, APP_SECRET)
      helper = UserAuthenticationStorageHelper(twitch, TARGET_SCOPES)
      await helper.bind()"""

    def __init__(self,
                 twitch: 'Twitch',
                 scopes: List[AuthScope],
                 storage_path: Optional[PurePath] = None,
                 auth_generator_func: Optional[Callable[['Twitch', List[AuthScope]], Awaitable[Tuple[str, str]]]] = None,
                 auth_base_url: str = TWITCH_AUTH_BASE_URL):
        self.twitch = twitch
        self.logger: Logger = getLogger('twitchAPI.oauth.storage_helper')
        """The logger used for OAuth Storage Helper related log messages"""
        self._target_scopes = scopes
        self.storage_path = storage_path if storage_path is not None else PurePath('user_token.json')
        self.auth_generator = auth_generator_func if auth_generator_func is not None else self._default_auth_gen
        self.auth_base_url: str = auth_base_url

    async def _default_auth_gen(self, twitch: 'Twitch', scopes: List[AuthScope]) -> (str, str):
        auth = UserAuthenticator(twitch, scopes, force_verify=True, auth_base_url=self.auth_base_url)
        return await auth.authenticate()

    async def _update_stored_tokens(self, token: str, refresh_token: str):
        self.logger.info('user token got refreshed and stored')
        with open(self.storage_path, 'w') as _f:
            json.dump({'token': token, 'refresh': refresh_token}, _f)

    async def bind(self):
        """Bind the helper to the provided instance of twitch and sets the user authentication."""
        self.twitch.user_auth_refresh_callback = self._update_stored_tokens
        needs_auth = True
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as _f:
                    creds = json.load(_f)
                await self.twitch.set_user_authentication(creds['token'], self._target_scopes, creds['refresh'])
            except:
                self.logger.info('stored token invalid, refreshing...')
            else:
                needs_auth = False
        if needs_auth:
            token, refresh_token = await self.auth_generator(self.twitch, self._target_scopes)
            with open(self.storage_path, 'w') as _f:
                json.dump({'token': token, 'refresh': refresh_token}, _f)
            await self.twitch.set_user_authentication(token, self._target_scopes, refresh_token)

==> ./pubsub.py <==
#  Copyright (c) 2020. Lena "Teekeks" During <info@teawork.de>
"""
PubSub
------

This is a full implementation of the PubSub API of twitch.
PubSub enables you to subscribe to a topic, for updates (e.g., when a user cheers in a channel).

Read more about it on `the Twitch API Documentation <https://dev.twitch.tv/docs/pubsub>`__.

.. note:: You **always** need User Authentication while using this!

************
Code Example
************

.. code-block:: python

    from twitchAPI.pubsub import PubSub
    from twitchAPI.twitch import Twitch
    from twitchAPI.helper import first
    from twitchAPI.type import AuthScope
    from twitchAPI.oauth import UserAuthenticator
    import asyncio
    from pprint import pprint
    from uuid import UUID

    APP_ID = 'my_app_id'
    APP_SECRET = 'my_app_secret'
    USER_SCOPE = [AuthScope.WHISPERS_READ]
    TARGET_CHANNEL = 'teekeks42'

    async def callback_whisper(uuid: UUID, data: dict) -> None:
        print('got callback for UUID ' + str(uuid))
        pprint(data)


    async def run_example():
        # setting up Authentication and getting your user id
        twitch = await Twitch(APP_ID, APP_SECRET)
        auth = UserAuthenticator(twitch, [AuthScope.WHISPERS_READ], force_verify=False)
        token, refresh_token = await auth.authenticate()
        # you can get your user auth token and user auth refresh token following the example in twitchAPI.oauth
        await twitch.set_user_authentication(token, [AuthScope.WHISPERS_READ], refresh_token)
        user = await first(twitch.get_users(logins=[TARGET_CHANNEL]))

        # starting up PubSub
        pubsub = PubSub(twitch)
        pubsub.start()
        # you can either start listening before or after you started pubsub.
        uuid = await pubsub.listen_whispers(user.id, callback_whisper)
        input('press ENTER to close...')
        # you do not need to unlisten to topics before stopping but you can listen and unlisten at any moment you want
        await pubsub.unlisten(uuid)
        pubsub.stop()
        await twitch.close()

    asyncio.run(run_example())


*******************
Class Documentation
*******************
"""
from asyncio import CancelledError
from functools import partial

import aiohttp
from aiohttp import ClientSession

from .twitch import Twitch
from .type import *
from .helper import get_uuid, make_enum, TWITCH_PUB_SUB_URL, done_task_callback
import asyncio
import threading
import json
from random import randrange
import datetime
from logging import getLogger, Logger
from uuid import UUID
from time import sleep

from typing import Callable, List, Dict, Awaitable, Optional

__all__ = ['PubSub']


CALLBACK_FUNC = Callable[[UUID, dict], Awaitable[None]]


class PubSub:
    """The PubSub client
    """

    def __init__(self, twitch: Twitch, callback_loop: Optional[asyncio.AbstractEventLoop] = None):
        """

        :param twitch:  A authenticated Twitch instance
        :param callback_loop: The asyncio eventloop to be used for callbacks. \n
            Set this if you or a library you use cares about which asyncio event loop is running the callbacks.
            Defaults to the one used by PubSub.
        """
        self.__twitch: Twitch = twitch
        self.logger: Logger = getLogger('twitchAPI.pubsub')
        """The logger used for PubSub related log messages"""
        self.ping_frequency: int = 120
        """With which frequency in seconds a ping command is sent. You probably don't want to change this. 
           This should never be shorter than 12 + `ping_jitter` seconds to avoid problems with the pong timeout. |default| :code:`120`"""
        self.ping_jitter: int = 4
        """time in seconds added or subtracted from `ping_frequency`. You probably don't want to change this. |default| :code:`4`"""
        self.listen_confirm_timeout: int = 30
        """maximum time in seconds waited for a listen confirm. |default| :code:`30`"""
        self.reconnect_delay_steps: List[int] = [1, 2, 4, 8, 16, 32, 64, 128]
        self.__connection = None
        self._callback_loop = callback_loop
        self.__socket_thread: Optional[threading.Thread] = None
        self.__running: bool = False
        self.__socket_loop = None
        self.__topics: dict = {}
        self._session = None
        self.__startup_complete: bool = False
        self.__tasks = None
        self.__waiting_for_pong: bool = False
        self.__nonce_waiting_confirm: dict = {}
        self._closing = False
        self._task_callback = partial(done_task_callback, self.logger)

    def start(self) -> None:
        """
        Start the PubSub Client

        :raises RuntimeError: if already started
        """
        self.logger.debug('starting pubsub...')
        if self.__running:
            raise RuntimeError('already started')
        self.__startup_complete = False
        self.__socket_thread = threading.Thread(target=self.__run_socket)
        self.__running = True
        self.__socket_thread.start()
        while not self.__startup_complete:
            sleep(0.01)
        self.logger.debug('pubsub started up!')

    async def _stop(self):
        for t in self.__tasks:
            t.cancel()
        await self.__connection.close()
        await self._session.close()
        await asyncio.sleep(0.25)
        self._closing = True

    def stop(self) -> None:
        """
        Stop the PubSub Client

        :raises RuntimeError: if the client is not running
        """

        if not self.__running:
            raise RuntimeError('not running')
        self.logger.debug('stopping pubsub...')
        self.__startup_complete = False
        self.__running = False
        f = asyncio.run_coroutine_threadsafe(self._stop(), self.__socket_loop)
        f.result()
        self.logger.debug('pubsub stopped!')
        self.__socket_thread.join()

    def is_connected(self) -> bool:
        """Returns your current connection status."""
        if self.__connection is None:
            return False
        return not self.__connection.closed

###########################################################################################
# Internal
###########################################################################################

    async def __connect(self, is_startup=False):
        self.logger.debug('connecting...')
        self._closing = False
        if self.__connection is not None and not self.__connection.closed:
            await self.__connection.close()
        retry = 0
        need_retry = True
        if self._session is None:
            self._session = ClientSession(timeout=self.__twitch.session_timeout)
        while need_retry and retry < len(self.reconnect_delay_steps):
            need_retry = False
            try:
                self.__connection = await self._session.ws_connect(TWITCH_PUB_SUB_URL)
            except Exception:
                self.logger.warning(f'connection attempt failed, retry in {self.reconnect_delay_steps[retry]}s...')
                await asyncio.sleep(self.reconnect_delay_steps[retry])
                retry += 1
                need_retry = True
        if retry >= len(self.reconnect_delay_steps):
            raise TwitchBackendException('can\'t connect')

        if not self.__connection.closed and not is_startup:
            uuid = str(get_uuid())
            await self.__send_listen(uuid, list(self.__topics.keys()))

    async def __send_listen(self, nonce: str, topics: List[str], subscribe: bool = True):
        listen_msg = {
            'type': 'LISTEN' if subscribe else 'UNLISTEN',
            'nonce': nonce,
            'data': {
                'topics': topics,
                'auth_token': self.__twitch.get_user_auth_token()
            }
        }
        self.__nonce_waiting_confirm[nonce] = {'received': False,
                                               'error': PubSubResponseError.NONE}
        timeout = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.listen_confirm_timeout)
        confirmed = False
        self.logger.debug(f'sending {"" if subscribe else "un"}listen for topics {str(topics)} with nonce {nonce}')
        await self.__send_message(listen_msg)
        # wait for confirm
        while not confirmed and datetime.datetime.utcnow() < timeout:
            await asyncio.sleep(0.01)
            confirmed = self.__nonce_waiting_confirm[nonce]['received']
        if not confirmed:
            raise PubSubListenTimeoutException()
        else:
            error = self.__nonce_waiting_confirm[nonce]['error']
            if error is not PubSubResponseError.NONE:
                if error is PubSubResponseError.BAD_AUTH:
                    raise TwitchAuthorizationException()
                if error is PubSubResponseError.SERVER:
                    raise TwitchBackendException()
                raise TwitchAPIException(error)

    async def __send_message(self, msg_data):
        self.logger.debug(f'sending message {json.dumps(msg_data)}')
        await self.__connection.send_str(json.dumps(msg_data))

    async def _keep_loop_alive(self):
        while not self._closing:
            await asyncio.sleep(0.1)

    def __run_socket(self):
        self.__socket_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.__socket_loop)
        if self._callback_loop is None:
            self._callback_loop = self.__socket_loop

        # startup
        self.__socket_loop.run_until_complete(self.__connect(is_startup=True))

        self.__tasks = [
            asyncio.ensure_future(self.__task_heartbeat(), loop=self.__socket_loop),
            asyncio.ensure_future(self.__task_receive(), loop=self.__socket_loop),
            asyncio.ensure_future(self.__task_initial_listen(), loop=self.__socket_loop)
        ]

        self.__socket_loop.run_until_complete(self._keep_loop_alive())

    async def __generic_listen(self, key, callback_func, required_scopes: List[AuthScope]) -> UUID:
        if not asyncio.iscoroutinefunction(callback_func):
            raise ValueError('callback_func needs to be a async function which takes 2 arguments')
        for scope in required_scopes:
            if scope not in self.__twitch.get_user_auth_scope():
                raise MissingScopeException(str(scope))
        uuid = get_uuid()
        if key not in self.__topics.keys():
            self.__topics[key] = {'subs': {}}
        self.__topics[key]['subs'][uuid] = callback_func
        if self.__startup_complete:
            await self.__send_listen(str(uuid), [key])
        return uuid

###########################################################################################
# Asyncio Tasks
###########################################################################################

    async def __task_initial_listen(self):
        self.__startup_complete = True
        if len(list(self.__topics.keys())) > 0:
            uuid = str(get_uuid())
            await self.__send_listen(uuid, list(self.__topics.keys()))

    async def __task_heartbeat(self):
        while not self._closing:
            next_heartbeat = datetime.datetime.utcnow() + \
                             datetime.timedelta(seconds=randrange(self.ping_frequency - self.ping_jitter,
                                                                  self.ping_frequency + self.ping_jitter,
                                                                  1))

            while datetime.datetime.utcnow() < next_heartbeat:
                await asyncio.sleep(1)
            self.logger.debug('send ping...')
            pong_timeout = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
            self.__waiting_for_pong = True
            await self.__send_message({'type': 'PING'})
            while self.__waiting_for_pong:
                if datetime.datetime.utcnow() > pong_timeout:
                    self.logger.info('did not receive pong in time, reconnecting...')
                    await self.__connect()
                    self.__waiting_for_pong = False
                await asyncio.sleep(1)

    async def __task_receive(self):
        try:
            while not self.__connection.closed:
                message = await self.__connection.receive()
                if message.type == aiohttp.WSMsgType.TEXT:
                    messages = message.data.split('\r\n')
                    for m in messages:
                        if len(m) == 0:
                            continue
                        self.logger.debug(f'received message {m}')
                        data = json.loads(m)
                        switcher: Dict[str, Callable] = {
                            'pong': self.__handle_pong,
                            'reconnect': self.__handle_reconnect,
                            'response': self.__handle_response,
                            'message': self.__handle_message,
                            'auth_revoked': self.__handle_auth_revoked
                        }
                        handler = switcher.get(data.get('type', '').lower(),
                                               self.__handle_unknown)
                        self.__socket_loop.create_task(handler(data))
                elif message.type == aiohttp.WSMsgType.CLOSED:
                    self.logger.debug('websocket is closing... trying to reestablish connection')
                    try:
                        await self._handle_base_reconnect()
                    except TwitchBackendException:
                        self.logger.exception('Connection to websocket lost and unable to reestablish connection!')
                        break
                    break
                elif message.type == aiohttp.WSMsgType.ERROR:
                    self.logger.warning('error in websocket')
                    break
        except CancelledError:
            return

###########################################################################################
# Handler
###########################################################################################

    async def _handle_base_reconnect(self):
        await self.__connect(is_startup=False)

    # noinspection PyUnusedLocal
    async def __handle_pong(self, data):
        self.__waiting_for_pong = False
        self.logger.debug('received pong')

    # noinspection PyUnusedLocal
    async def __handle_reconnect(self, data):
        self.logger.info('received reconnect command, reconnecting now...')
        await self.__connect()

    async def __handle_response(self, data):
        error = make_enum(data.get('error'),
                          PubSubResponseError,
                          PubSubResponseError.UNKNOWN)
        self.logger.debug(f'got response for nonce {data.get("nonce")}: {str(error)}')
        self.__nonce_waiting_confirm[data.get('nonce')]['error'] = error
        self.__nonce_waiting_confirm[data.get('nonce')]['received'] = True

    async def __handle_message(self, data):
        topic_data = self.__topics.get(data.get('data', {}).get('topic', ''), None)
        msg_data = json.loads(data.get('data', {}).get('message', '{}'))
        if topic_data is not None:
            for uuid, sub in topic_data.get('subs', {}).items():
                t = self._callback_loop.create_task(sub(uuid, msg_data))
                t.add_done_callback(self._task_callback)

    async def __handle_auth_revoked(self, data):
        revoked_topics = data.get('data', {}).get('topics', [])
        for topic in revoked_topics:
            self.__topics.pop(topic, None)
        self.logger.warning("received auth revoked. no longer listening on topics: " + str(revoked_topics))

    async def __handle_unknown(self, data):
        self.logger.warning('got message of unknown type: ' + str(data))

###########################################################################################
# Listener
###########################################################################################

    async def unlisten(self, uuid: UUID) -> None:
        """
        Stop listening to a specific Topic subscription.

        :param ~uuid.UUID uuid: The UUID of the subscription you want to stop listening to
        :raises ~twitchAPI.type.TwitchAuthorizationException: if Token is not valid
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch Server has a problem
        :raises ~twitchAPI.type.TwitchAPIException: if the server response is something else than suspected
        :raises ~twitchAPI.type.PubSubListenTimeoutException: if the unsubscription is not confirmed in the time set by
                `listen_confirm_timeout`
        """
        clear_topics = []
        for topic, topic_data in self.__topics.items():
            if uuid in topic_data['subs'].keys():
                topic_data['subs'].pop(uuid)
                if len(topic_data['subs'].keys()) == 0:
                    clear_topics.append(topic)
        if self.__startup_complete and len(clear_topics) > 0:
            await self.__send_listen(str(uuid), clear_topics, subscribe=False)
        if len(clear_topics) > 0:
            for topic in clear_topics:
                self.__topics.pop(topic)

    async def listen_whispers(self,
                              user_id: str,
                              callback_func: CALLBACK_FUNC) -> UUID:
        """
        You are notified when anyone whispers the specified user or the specified user whispers to anyone.\n
        Requires the :const:`~twitchAPI.type.AuthScope.WHISPERS_READ` AuthScope.\n

        :param user_id: ID of the User
        :param callback_func: Function called on event
        :return: UUID of this subscription
        :raises ~twitchAPI.type.TwitchAuthorizationException: if Token is not valid
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch Server has a problem
        :raises ~twitchAPI.type.TwitchAPIException: if the subscription response is something else than suspected
        :raises ~twitchAPI.type.PubSubListenTimeoutException: if the subscription is not confirmed in the time set by `listen_confirm_timeout`
        :raises ~twitchAPI.type.MissingScopeException: if required AuthScope is missing from Token
        """
        return await self.__generic_listen(f'whispers.{user_id}', callback_func, [AuthScope.WHISPERS_READ])

    async def listen_bits_v1(self,
                             channel_id: str,
                             callback_func: CALLBACK_FUNC) -> UUID:
        """
        You are notified when anyone cheers in the specified channel.\n
        Requires the :const:`~twitchAPI.type.AuthScope.BITS_READ` AuthScope.\n

        :param channel_id: ID of the Channel
        :param callback_func: Function called on event
        :return: UUID of this subscription
        :raises ~twitchAPI.type.TwitchAuthorizationException: if Token is not valid
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch Server has a problem
        :raises ~twitchAPI.type.TwitchAPIException: if the subscription response is something else than suspected
        :raises ~twitchAPI.type.PubSubListenTimeoutException: if the subscription is not confirmed in the time set by `listen_confirm_timeout`
        :raises ~twitchAPI.type.MissingScopeException: if required AuthScope is missing from Token
        """
        return await self.__generic_listen(f'channel-bits-events-v1.{channel_id}', callback_func, [AuthScope.BITS_READ])

    async def listen_bits(self,
                          channel_id: str,
                          callback_func: CALLBACK_FUNC) -> UUID:
        """
        You are notified when anyone cheers in the specified channel.\n
        Requires the :const:`~twitchAPI.type.AuthScope.BITS_READ` AuthScope.\n

        :param channel_id: ID of the Channel
        :param callback_func: Function called on event
        :return: UUID of this subscription
        :raises ~twitchAPI.type.TwitchAuthorizationException: if Token is not valid
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch Server has a problem
        :raises ~twitchAPI.type.TwitchAPIException: if the subscription response is something else than suspected
        :raises ~twitchAPI.type.PubSubListenTimeoutException: if the subscription is not confirmed in the time set by `listen_confirm_timeout`
        :raises ~twitchAPI.type.MissingScopeException: if required AuthScope is missing from Token
        """
        return await self.__generic_listen(f'channel-bits-events-v2.{channel_id}', callback_func, [AuthScope.BITS_READ])

    async def listen_bits_badge_notification(self,
                                             channel_id: str,
                                             callback_func: CALLBACK_FUNC) -> UUID:
        """
        You are notified when a user earns a new Bits badge in the given channel,
        and chooses to share the notification with chat.\n
        Requires the :const:`~twitchAPI.type.AuthScope.BITS_READ` AuthScope.\n

        :param channel_id: ID of the Channel
        :param callback_func: Function called on event
        :return: UUID of this subscription
        :raises ~twitchAPI.type.TwitchAuthorizationException: if Token is not valid
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch Server has a problem
        :raises ~twitchAPI.type.TwitchAPIException: if the subscription response is something else than suspected
        :raises ~twitchAPI.type.PubSubListenTimeoutException: if the subscription is not confirmed in the time set by `listen_confirm_timeout`
        :raises ~twitchAPI.type.MissingScopeException: if required AuthScope is missing from Token
        """
        return await self.__generic_listen(f'channel-bits-badge-unlocks.{channel_id}', callback_func, [AuthScope.BITS_READ])

    async def listen_channel_points(self,
                                    channel_id: str,
                                    callback_func: CALLBACK_FUNC) -> UUID:
        """
        You are notified when a custom reward is redeemed in the channel.\n
        Requires the :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS` AuthScope.\n

        :param channel_id: ID of the Channel
        :param callback_func: Function called on event
        :return: UUID of this subscription
        :raises ~twitchAPI.type.TwitchAuthorizationException: if Token is not valid
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch Server has a problem
        :raises ~twitchAPI.type.TwitchAPIException: if the subscription response is something else than suspected
        :raises ~twitchAPI.type.PubSubListenTimeoutException: if the subscription is not confirmed in the time set by `listen_confirm_timeout`
        :raises ~twitchAPI.type.MissingScopeException: if required AuthScope is missing from Token
        """
        return await self.__generic_listen(f'channel-points-channel-v1.{channel_id}',
                                           callback_func,
                                           [AuthScope.CHANNEL_READ_REDEMPTIONS])

    async def listen_channel_subscriptions(self,
                                           channel_id: str,
                                           callback_func: CALLBACK_FUNC) -> UUID:
        """
        You are notified when anyone subscribes (first month), resubscribes (subsequent months),
        or gifts a subscription to a channel. Subgift subscription messages contain recipient information.\n
        Requires the :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_SUBSCRIPTIONS` AuthScope.\n

        :param channel_id: ID of the Channel
        :param callback_func: Function called on event
        :return: UUID of this subscription
        :raises ~twitchAPI.type.TwitchAuthorizationException: if Token is not valid
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch Server has a problem
        :raises ~twitchAPI.type.TwitchAPIException: if the subscription response is something else than suspected
        :raises ~twitchAPI.type.PubSubListenTimeoutException: if the subscription is not confirmed in the time set by `listen_confirm_timeout`
        :raises ~twitchAPI.type.MissingScopeException: if required AuthScope is missing from Token
        """
        return await self.__generic_listen(f'channel-subscribe-events-v1.{channel_id}',
                                           callback_func,
                                           [AuthScope.CHANNEL_READ_SUBSCRIPTIONS])

    async def listen_chat_moderator_actions(self,
                                            user_id: str,
                                            channel_id: str,
                                            callback_func: CALLBACK_FUNC) -> UUID:
        """
        Supports moderators listening to the topic, as well as users listening to the topic to receive their own events.
        Examples of moderator actions are bans, unbans, timeouts, deleting messages,
        changing chat mode (followers-only, subs-only), changing AutoMod levels, and adding a mod.\n
        Requires the :const:`~twitchAPI.type.AuthScope.CHANNEL_MODERATE` AuthScope.\n

        :param user_id: ID of the User
        :param channel_id: ID of the Channel
        :param callback_func: Function called on event
        :return: UUID of this subscription
        :raises ~twitchAPI.type.TwitchAuthorizationException: if Token is not valid
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch Server has a problem
        :raises ~twitchAPI.type.TwitchAPIException: if the subscription response is something else than suspected
        :raises ~twitchAPI.type.PubSubListenTimeoutException: if the subscription is not confirmed in the time set by `listen_confirm_timeout`
        :raises ~twitchAPI.type.MissingScopeException: if required AuthScope is missing from Token
        """
        return await self.__generic_listen(f'chat_moderator_actions.{user_id}.{channel_id}',
                                           callback_func,
                                           [AuthScope.CHANNEL_MODERATE])

    async def listen_automod_queue(self,
                                   moderator_id: str,
                                   channel_id: str,
                                   callback_func: CALLBACK_FUNC) -> UUID:
        """
        AutoMod flags a message as potentially inappropriate, and when a moderator takes action on a message.\n
        Requires the :const:`~twitchAPI.type.AuthScope.CHANNEL_MODERATE` AuthScope.\n

        :param moderator_id: ID of the Moderator
        :param channel_id: ID of the Channel
        :param callback_func: Function called on event
        :return: UUID of this subscription
        :raises ~twitchAPI.type.TwitchAuthorizationException: if Token is not valid
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch Server has a problem
        :raises ~twitchAPI.type.TwitchAPIException: if the subscription response is something else than suspected
        :raises ~twitchAPI.type.PubSubListenTimeoutException: if the subscription is not confirmed in the time set by `listen_confirm_timeout`
        :raises ~twitchAPI.type.MissingScopeException: if required AuthScope is missing from Token
        """
        return await self.__generic_listen(f'automod-queue.{moderator_id}.{channel_id}',
                                           callback_func,
                                           [AuthScope.CHANNEL_MODERATE])

    async def listen_user_moderation_notifications(self,
                                                   user_id: str,
                                                   channel_id: str,
                                                   callback_func: CALLBACK_FUNC) -> UUID:
        """
        A user’s message held by AutoMod has been approved or denied.\n
        Requires the :const:`~twitchAPI.type.AuthScope.CHAT_READ` AuthScope.\n

        :param user_id: ID of the User
        :param channel_id: ID of the Channel
        :param callback_func: Function called on event
        :return: UUID of this subscription
        :raises ~twitchAPI.type.TwitchAuthorizationException: if Token is not valid
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch Server has a problem
        :raises ~twitchAPI.type.TwitchAPIException: if the subscription response is something else than suspected
        :raises ~twitchAPI.type.PubSubListenTimeoutException: if the subscription is not confirmed in the time set by `listen_confirm_timeout`
        :raises ~twitchAPI.type.MissingScopeException: if required AuthScope is missing from Token
        """
        return await self.__generic_listen(f'user-moderation-notifications.{user_id}.{channel_id}',
                                           callback_func,
                                           [AuthScope.CHAT_READ])

    async def listen_low_trust_users(self,
                                     moderator_id: str,
                                     channel_id: str,
                                     callback_func: CALLBACK_FUNC) -> UUID:
        """The broadcaster or a moderator updates the low trust status of a user,
        or a new message has been sent in chat by a potential ban evader or a bans shared user.

        Requires the :const:`~twitchAPI.type.AuthScope.CHANNEL_MODERATE` AuthScope.\n

        :param moderator_id: ID of the moderator
        :param channel_id: ID of the Channel
        :param callback_func: Function called on event
        :return: UUID of this subscription
        :raises ~twitchAPI.type.TwitchAuthorizationException: if Token is not valid
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch Server has a problem
        :raises ~twitchAPI.type.TwitchAPIException: if the subscription response is something else than suspected
        :raises ~twitchAPI.type.PubSubListenTimeoutException: if the subscription is not confirmed in the time set by `listen_confirm_timeout`
        :raises ~twitchAPI.type.MissingScopeException: if required AuthScope is missing from Token
        """
        return await self.__generic_listen(f'low-trust-users.{moderator_id}.{channel_id}',
                                           callback_func,
                                           [AuthScope.CHANNEL_MODERATE])

    async def listen_undocumented_topic(self,
                                        topic: str,
                                        callback_func: CALLBACK_FUNC) -> UUID:
        """
        Listen to one of the many undocumented PubSub topics.

        Make sure that you have the required AuthScope for your topic set, since this lib can not check it for you!

        .. warning:: Using a undocumented topic can break at any time, use at your own risk!

        :param topic: the topic string
        :param callback_func: Function called on event
        :raises ~twitchAPI.type.TwitchAuthorizationException: if Token is not valid or does not have the required AuthScope
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch Server has a problem
        :raises ~twitchAPI.type.TwitchAPIException: if the subscription response is something else than suspected
        :raises ~twitchAPI.type.PubSubListenTimeoutException: if the subscription is not confirmed in the time set by `listen_confirm_timeout`
        """
        self.logger.warning(f"using undocumented topic {topic}")
        return await self.__generic_listen(topic, callback_func, [])

==> ./twitch.py <==
#  Copyright (c) 2020. Lena "Teekeks" During <info@teawork.de>
"""
Twitch API
----------

This is the base of this library, it handles authentication renewal, error handling and permission management.

Look at the `Twitch API reference <https://dev.twitch.tv/docs/api/reference>`__ for a more detailed documentation on
what each endpoint does.

*************
Example Usage
*************

.. code-block:: python

    from twitchAPI.twitch import Twitch
    from twitchAPI.helper import first
    import asyncio

    async def twitch_example():
        # initialize the twitch instance, this will by default also create a app authentication for you
        twitch = await Twitch('app_id', 'app_secret')
        # call the API for the data of your twitch user
        # this returns a async generator that can be used to iterate over all results
        # but we are just interested in the first result
        # using the first helper makes this easy.
        user = await first(twitch.get_users(logins='your_twitch_user'))
        # print the ID of your user or do whatever else you want with it
        print(user.id)
        await twitch.close()

    # run this example
    asyncio.run(twitch_example())


****************************
Working with the API results
****************************

The API returns a few different types of results.


TwitchObject
============

A lot of API calls return a child of :py:const:`~twitchAPI.object.TwitchObject` in some way (either directly or via generator).
You can always use the :py:const:`~twitchAPI.object.TwitchObject.to_dict()` method to turn that object to a dictionary.

Example:

.. code-block:: python

    blocked_term = await twitch.add_blocked_term('broadcaster_id', 'moderator_id', 'bad_word')
    print(blocked_term.id)


IterTwitchObject
================

Some API calls return a special type of TwitchObject.
These usually have some list inside that you may want to directly iterate over in your API usage but that also contain other useful data
outside of that List.


Example:

.. code-block:: python

    lb = await twitch.get_bits_leaderboard()
    print(lb.total)
    for e in lb:
        print(f'#{e.rank:02d} - {e.user_name}: {e.score}')


AsyncIterTwitchObject
=====================

A few API calls will have useful data outside of the list the pagination iterates over.
For those cases, this object exist.

Example:

.. code-block:: python

    schedule = await twitch.get_channel_stream_schedule('user_id')
    print(schedule.broadcaster_name)
    async for segment in schedule:
        print(segment.title)


AsyncGenerator
==============

AsyncGenerators are used to automatically iterate over all possible results of your API call, this will also automatically handle pagination for you.
In some cases (for example stream schedules with repeating entries), this may result in a endless stream of entries returned so make sure to add your
own exit conditions in such cases.
The generated objects will always be children of :py:const:`~twitchAPI.object.TwitchObject`, see the docs of the API call to see the exact
object type.

Example:

.. code-block:: python

    async for tag in twitch.get_all_stream_tags():
        print(tag.tag_id)

**************
Authentication
**************

The Twitch API knows 2 different authentications. App and User Authentication.
Which one you need (or if one at all) depends on what calls you want to use.

Its always good to get at least App authentication even for calls where you don't need it since the rate limits are way
better for authenticated calls.


App Authentication
==================

By default, The lib will try to attempt to create a App Authentication on Initialization:

.. code-block:: python

    from twitchAPI.twitch import Twitch
    twitch = await Twitch('my_app_id', 'my_app_secret')

You can set a Auth Scope like this:

.. code-block:: python

    from twitchAPI.twitch import Twitch, AuthScope
    twitch = await Twitch('my_app_id', 'my_app_secret', target_app_auth_scope=[AuthScope.USER_EDIT])

If you want to change the AuthScope later use this:

.. code-block:: python

    await twitch.authenticate_app(my_new_scope)


If you don't want to use App Authentication, Initialize like this:

.. code-block:: python

    from twitchAPI.twitch import Twitch
    twitch = await Twitch('my_app_id', authenticate_app=False)


User Authentication
===================

Only use a user auth token, use this:

.. code-block:: python

    from twitchAPI.twitch import Twitch
    twitch = await Twitch('my_app_id', authenticate_app=False)
    # make sure to set the second parameter as the scope used to generate the token
    await twitch.set_user_authentication('token', [], 'refresh_token')


Use both App and user Authentication:

.. code-block:: python

    from twitchAPI.twitch import Twitch
    twitch = await Twitch('my_app_id', 'my_app_secret')
    # make sure to set the second parameter as the scope used to generate the token
    await twitch.set_user_authentication('token', [], 'refresh_token')


To get a user auth token, the user has to explicitly click "Authorize" on the twitch website. You can use various online
services to generate a token or use my build in authenticator.

See :obj:`twitchAPI.oauth` for more info on my build in authenticator.

Authentication refresh callback
===============================

Optionally you can set a callback for both user access token refresh and app access token refresh.

.. code-block:: python

    from twitchAPI.twitch import Twitch

    async def user_refresh(token: str, refresh_token: str):
        print(f'my new user token is: {token}')

    async def app_refresh(token: str):
        print(f'my new app token is: {token}')

    twitch = await Twitch('my_app_id', 'my_app_secret')
    twitch.app_auth_refresh_callback = app_refresh
    twitch.user_auth_refresh_callback = user_refresh

*******************
Class Documentation
*******************
"""
import asyncio
import aiohttp.helpers
from datetime import datetime
from aiohttp import ClientSession, ClientResponse
from aiohttp.client import ClientTimeout
from .helper import TWITCH_API_BASE_URL, TWITCH_AUTH_BASE_URL, build_scope, enum_value_or_none, datetime_to_str, remove_none_values, ResultType, \
    build_url
from logging import getLogger, Logger
from .object.api import *
from .type import *
from typing import Union, List, Optional, Callable, AsyncGenerator, TypeVar, Dict, Awaitable

__all__ = ['Twitch']
T = TypeVar('T')


class Twitch:
    """
    Twitch API client
    """

    def __init__(self,
                 app_id: str,
                 app_secret: Optional[str] = None,
                 authenticate_app: bool = True,
                 target_app_auth_scope: Optional[List[AuthScope]] = None,
                 base_url: str = TWITCH_API_BASE_URL,
                 auth_base_url: str = TWITCH_AUTH_BASE_URL,
                 session_timeout: Union[object, ClientTimeout] = aiohttp.helpers.sentinel):
        """
        :param app_id: Your app id
        :param app_secret: Your app secret, leave as None if you only want to use User Authentication |default| :code:`None`
        :param authenticate_app: If true, auto generate a app token on startup |default| :code:`True`
        :param target_app_auth_scope: AuthScope to use if :code:`authenticate_app` is True |default| :code:`None`
        :param base_url: The URL to the Twitch API |default| :const:`~twitchAPI.helper.TWITCH_API_BASE_URL`
        :param auth_base_url: The URL to the Twitch API auth server |default| :const:`~twitchAPI.helper.TWITCH_AUTH_BASE_URL`
        :param session_timeout: Override the time in seconds before any request times out. Defaults to aiohttp default (300 seconds)
        """
        self.app_id: Optional[str] = app_id
        self.app_secret: Optional[str] = app_secret
        self.logger: Logger = getLogger('twitchAPI.twitch')
        """The logger used for Twitch API call related log messages"""
        self.user_auth_refresh_callback: Optional[Callable[[str, str], Awaitable[None]]] = None
        """If set, gets called whenever a user auth token gets refreshed. Parameter: Auth Token, Refresh Token |default| :code:`None`"""
        self.app_auth_refresh_callback: Optional[Callable[[str], Awaitable[None]]] = None
        """If set, gets called whenever a app auth token gets refreshed. Parameter: Auth Token |default| :code:`None`"""
        self.session_timeout: Union[object, ClientTimeout] = session_timeout
        """Override the time in seconds before any request times out. Defaults to aiohttp default (300 seconds)"""
        self._app_auth_token: Optional[str] = None
        self._app_auth_scope: List[AuthScope] = []
        self._has_app_auth: bool = False
        self._user_auth_token: Optional[str] = None
        self._user_auth_refresh_token: Optional[str] = None
        self._user_auth_scope: List[AuthScope] = []
        self._has_user_auth: bool = False
        self.auto_refresh_auth: bool = True
        """If set to true, auto refresh the auth token once it expires. |default| :code:`True`"""
        self._authenticate_app = authenticate_app
        self._target_app_scope = target_app_auth_scope
        self.base_url: str = base_url
        """The URL to the Twitch API used"""
        self.auth_base_url: str = auth_base_url
        self._user_token_refresh_lock: bool = False
        self._app_token_refresh_lock: bool = False

    def __await__(self):
        if self._authenticate_app:
            t = asyncio.create_task(self.authenticate_app(self._target_app_scope if self._target_app_scope is not None else []))
            yield from t
        return self

    @staticmethod
    async def close():
        """Gracefully close the connection to the Twitch API"""
        # ensure that asyncio actually gracefully shut down
        await asyncio.sleep(0.25)

    def _generate_header(self, auth_type: 'AuthType', required_scope: List[Union[AuthScope, List[AuthScope]]]) -> dict:
        header = {"Client-ID": self.app_id}
        if auth_type == AuthType.EITHER:
            has_auth, target, token, scope = self._get_used_either_auth(required_scope)
            if not has_auth:
                raise UnauthorizedException('No authorization with correct scope set!')
            header['Authorization'] = f'Bearer {token}'
        elif auth_type == AuthType.APP:
            if not self._has_app_auth:
                raise UnauthorizedException('Require app authentication!')
            for s in required_scope:
                if isinstance(s, list):
                    if not any([x in self._app_auth_scope for x in s]):
                        raise MissingScopeException(f'Require at least one of the following app auth scopes: {", ".join([x.name for x in s])}')
                else:
                    if s not in self._app_auth_scope:
                        raise MissingScopeException('Require app auth scope ' + s.name)
            header['Authorization'] = f'Bearer {self._app_auth_token}'
        elif auth_type == AuthType.USER:
            if not self._has_user_auth:
                raise UnauthorizedException('require user authentication!')
            for s in required_scope:
                if isinstance(s, list):
                    if not any([x in self._user_auth_scope for x in s]):
                        raise MissingScopeException(f'Require at least one of the following user auth scopes: {", ".join([x.name for x in s])}')
                else:
                    if s not in self._user_auth_scope:
                        raise MissingScopeException('Require user auth scope ' + s.name)
            header['Authorization'] = f'Bearer {self._user_auth_token}'
        elif auth_type == AuthType.NONE:
            # set one anyway for better performance if possible but don't error if none found
            has_auth, target, token, scope = self._get_used_either_auth(required_scope)
            if has_auth:
                header['Authorization'] = f'Bearer {token}'
        return header

    def _get_used_either_auth(self, required_scope: List[AuthScope]) -> (bool, AuthType, Union[None, str], List[AuthScope]):
        if self.has_required_auth(AuthType.USER, required_scope):
            return True, AuthType.USER, self._user_auth_token, self._user_auth_scope
        if self.has_required_auth(AuthType.APP, required_scope):
            return True, AuthType.APP, self._app_auth_token, self._app_auth_scope
        return False, AuthType.NONE, None, []

    def get_user_auth_scope(self) -> List[AuthScope]:
        """Returns the set User auth Scope"""
        return self._user_auth_scope

    def has_required_auth(self, required_type: AuthType, required_scope: List[AuthScope]) -> bool:
        if required_type == AuthType.NONE:
            return True
        if required_type == AuthType.EITHER:
            return self.has_required_auth(AuthType.USER, required_scope) or \
                   self.has_required_auth(AuthType.APP, required_scope)
        if required_type == AuthType.USER:
            if not self._has_user_auth:
                return False
            for s in required_scope:
                if s not in self._user_auth_scope:
                    return False
            return True
        if required_type == AuthType.APP:
            if not self._has_app_auth:
                return False
            for s in required_scope:
                if s not in self._app_auth_scope:
                    return False
            return True
        # default to false
        return False

    # FIXME rewrite refresh_used_token
    async def refresh_used_token(self):
        """Refreshes the currently used token"""
        if self._has_user_auth:
            from .oauth import refresh_access_token
            if self._user_token_refresh_lock:
                while self._user_token_refresh_lock:
                    await asyncio.sleep(0.1)
            else:
                self.logger.debug('refreshing user token')
                self._user_token_refresh_lock = True
                self._user_auth_token, self._user_auth_refresh_token = await refresh_access_token(self._user_auth_refresh_token,
                                                                                                  self.app_id,
                                                                                                  self.app_secret,
                                                                                                  auth_base_url=self.auth_base_url)
                self._user_token_refresh_lock = False
                if self.user_auth_refresh_callback is not None:
                    await self.user_auth_refresh_callback(self._user_auth_token, self._user_auth_refresh_token)
        else:
            await self._refresh_app_token()

    async def _refresh_app_token(self):
        if self._app_token_refresh_lock:
            while self._app_token_refresh_lock:
                await asyncio.sleep(0.1)
        else:
            self._app_token_refresh_lock = True
            self.logger.debug('refreshing app token')
            await self._generate_app_token()
            self._app_token_refresh_lock = False
            if self.app_auth_refresh_callback is not None:
                await self.app_auth_refresh_callback(self._app_auth_token)

    async def _check_request_return(self,
                                    session: ClientSession,
                                    response: ClientResponse,
                                    method: str,
                                    url: str,
                                    auth_type: 'AuthType',
                                    required_scope: List[AuthScope],
                                    data: Optional[dict] = None,
                                    retries: int = 1
                                    ) -> ClientResponse:
        if retries > 0:
            if response.status == 503:
                # service unavailable, retry exactly once as recommended by twitch documentation
                self.logger.debug('got 503 response -> retry once')
                return await self._api_request(method, session, url, auth_type, required_scope, data=data, retries=retries - 1)
            elif response.status == 401:
                if self.auto_refresh_auth:
                    # unauthorized, lets try to refresh the token once
                    self.logger.debug('got 401 response -> try to refresh token')
                    await self.refresh_used_token()
                    return await self._api_request(method, session, url, auth_type, required_scope, data=data, retries=retries - 1)
                else:
                    msg = (await response.json()).get('message', '')
                    self.logger.debug(f'got 401 response and can\'t refresh. Message: "{msg}"')
                    raise UnauthorizedException(msg)
        else:
            if response.status == 503:
                raise TwitchBackendException('The Twitch API returns a server error')
            elif response.status == 401:
                msg = (await response.json()).get('message', '')
                self.logger.debug(f'got 401 response and can\'t refresh. Message: "{msg}"')
                raise UnauthorizedException(msg)

        if response.status == 500:
            raise TwitchBackendException('Internal Server Error')
        if response.status == 400:
            msg = None
            try:
                msg = (await response.json()).get('message')
            except:
                pass
            raise TwitchAPIException('Bad Request' + ('' if msg is None else f' - {str(msg)}'))
        if response.status == 404:
            msg = None
            try:
                msg = (await response.json()).get('message')
            except:
                pass
            raise TwitchResourceNotFound(msg)
        if response.status == 429 or str(response.headers.get('Ratelimit-Remaining', '')) == '0':
            self.logger.warning('reached rate limit, waiting for reset')
            import time
            reset = int(response.headers['Ratelimit-Reset'])
            # wait a tiny bit longer to ensure that we are definitely beyond the rate limit
            await asyncio.sleep((reset - time.time()) + 0.1)
        return response

    async def _api_request(self,
                           method: str,
                           session: ClientSession,
                           url: str,
                           auth_type: 'AuthType',
                           required_scope: List[Union[AuthScope, List[AuthScope]]],
                           data: Optional[dict] = None,
                           retries: int = 1) -> ClientResponse:
        """Make API request"""
        headers = self._generate_header(auth_type, required_scope)
        self.logger.debug(f'making {method} request to {url}')
        req = await session.request(method, url, headers=headers, json=data)
        return await self._check_request_return(session, req, method, url, auth_type, required_scope, data, retries)

    async def _build_generator(self,
                               method: str,
                               url: str,
                               url_params: dict,
                               auth_type: AuthType,
                               auth_scope: List[Union[AuthScope, List[AuthScope]]],
                               return_type: T,
                               body_data: Optional[dict] = None,
                               split_lists: bool = False,
                               error_handler: Optional[Dict[int, BaseException]] = None) -> AsyncGenerator[T, None]:
        _after = url_params.get('after')
        _first = True
        async with ClientSession(timeout=self.session_timeout) as session:
            while _first or _after is not None:
                url_params['after'] = _after
                _url = build_url(self.base_url + url, url_params, remove_none=True, split_lists=split_lists)
                response = await self._api_request(method, session, _url, auth_type, auth_scope, data=body_data)
                if error_handler is not None:
                    if response.status in error_handler.keys():
                        raise error_handler[response.status]
                data = await response.json()
                for entry in data.get('data', []):
                    yield return_type(**entry)
                _after = data.get('pagination', {}).get('cursor')
                _first = False

    async def _build_iter_result(self,
                                 method: str,
                                 url: str,
                                 url_params: dict,
                                 auth_type: AuthType,
                                 auth_scope: List[Union[AuthScope, List[AuthScope]]],
                                 return_type: T,
                                 body_data: Optional[dict] = None,
                                 split_lists: bool = False,
                                 iter_field: str = 'data',
                                 in_data: bool = False):
        _url = build_url(self.base_url + url, url_params, remove_none=True, split_lists=split_lists)
        async with ClientSession(timeout=self.session_timeout) as session:
            response = await self._api_request(method, session, _url, auth_type, auth_scope, data=body_data)
            data = await response.json()
        url_params['after'] = data.get('pagination', {}).get('cursor')
        if in_data:
            data = data['data']
        cont_data = {
            'req': self._api_request,
            'method': method,
            'url': self.base_url + url,
            'param': url_params,
            'split': split_lists,
            'auth_t': auth_type,
            'auth_s': auth_scope,
            'body': body_data,
            'iter_field': iter_field,
            'in_data': in_data
        }
        return return_type(cont_data, **data)

    async def _build_result(self,
                            method: str,
                            url: str,
                            url_params: dict,
                            auth_type: AuthType,
                            auth_scope: List[Union[AuthScope, List[AuthScope]]],
                            return_type: T,
                            body_data: Optional[dict] = None,
                            split_lists: bool = False,
                            get_from_data: bool = True,
                            result_type: ResultType = ResultType.RETURN_TYPE,
                            error_handler: Optional[Dict[int, BaseException]] = None):
        async with ClientSession(timeout=self.session_timeout) as session:
            _url = build_url(self.base_url + url, url_params, remove_none=True, split_lists=split_lists)
            response = await self._api_request(method, session, _url, auth_type, auth_scope, data=body_data)
            if error_handler is not None:
                if response.status in error_handler.keys():
                    raise error_handler[response.status]
            if result_type == ResultType.STATUS_CODE:
                return response.status
            if result_type == ResultType.TEXT:
                return await response.text()
            if return_type is not None:
                data = await response.json()
                if isinstance(return_type, dict):
                    return data
                origin = return_type.__origin__ if hasattr(return_type, '__origin__') else None
                if origin == list:
                    c = return_type.__args__[0]
                    return [x if isinstance(x, c) else c(**x) for x in data['data']]
                if get_from_data:
                    d = data['data']
                    if isinstance(d, list):
                        if len(d) == 0:
                            return None
                        return return_type(**d[0])
                    else:
                        return return_type(**d)
                else:
                    return return_type(**data)

    async def _generate_app_token(self) -> None:
        if self.app_secret is None:
            raise MissingAppSecretException()
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'grant_type': 'client_credentials',
            'scope': build_scope(self._app_auth_scope)
        }
        self.logger.debug('generating fresh app token')
        url = build_url(self.auth_base_url + 'token', params)
        async with ClientSession(timeout=self.session_timeout) as session:
            result = await session.post(url)
        if result.status != 200:
            raise TwitchAuthorizationException(f'Authentication failed with code {result.status} ({result.text})')
        try:
            data = await result.json()
            self._app_auth_token = data['access_token']
        except ValueError:
            raise TwitchAuthorizationException('Authentication response did not have a valid json body')
        except KeyError:
            raise TwitchAuthorizationException('Authentication response did not contain access_token')

    async def authenticate_app(self, scope: List[AuthScope]) -> None:
        """Authenticate with a fresh generated app token

        :param scope: List of Authorization scopes to use
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the authentication fails
        :return: None
        """
        self._app_auth_scope = scope
        await self._generate_app_token()
        self._has_app_auth = True

    async def set_app_authentication(self, token: str, scope: List[AuthScope]):
        """Set a app token, most likely only used for testing purposes

        :param token: the app token
        :param scope: List of Authorization scopes that the given app token has
        """
        self._app_auth_token = token
        self._app_auth_scope = scope
        self._has_app_auth = True

    async def set_user_authentication(self,
                                      token: str,
                                      scope: List[AuthScope],
                                      refresh_token: Optional[str] = None,
                                      validate: bool = True):
        """Set a user token to be used.

        :param token: the generated user token
        :param scope: List of Authorization Scopes that the given user token has
        :param refresh_token: The generated refresh token, has to be provided if :attr:`auto_refresh_auth` is True |default| :code:`None`
        :param validate: if true, validate the set token for being a user auth token and having the required scope |default| :code:`True`
        :raises ValueError: if :attr:`auto_refresh_auth` is True but refresh_token is not set
        :raises ~twitchAPI.type.MissingScopeException: if given token is missing one of the required scopes
        :raises ~twitchAPI.type.InvalidTokenException: if the given token is invalid or for a different client id
        """
        if refresh_token is None and self.auto_refresh_auth:
            raise ValueError('refresh_token has to be provided when auto_refresh_auth is True')
        if scope is None:
            raise MissingScopeException('scope was not provided')
        if validate:
            from .oauth import validate_token, refresh_access_token
            val_result = await validate_token(token, auth_base_url=self.auth_base_url)
            if val_result.get('status', 200) == 401 and refresh_token is not None:
                # try to refresh once and revalidate
                token, refresh_token = await refresh_access_token(refresh_token, self.app_id, self.app_secret, auth_base_url=self.auth_base_url)
                if self.user_auth_refresh_callback is not None:
                    await self.user_auth_refresh_callback(token, refresh_token)
                val_result = await validate_token(token, auth_base_url=self.auth_base_url)
            if val_result.get('status', 200) == 401:
                raise InvalidTokenException(val_result.get('message', ''))
            if 'login' not in val_result or 'user_id' not in val_result:
                # this is a app token or not valid
                raise InvalidTokenException('not a user oauth token')
            if val_result.get('client_id') != self.app_id:
                raise InvalidTokenException('client id does not match')
            scopes = val_result.get('scopes', [])
            for s in scope:
                if s not in scopes:
                    raise MissingScopeException(f'given token is missing scope {s.value}')

        self._user_auth_token = token
        self._user_auth_refresh_token = refresh_token
        self._user_auth_scope = scope
        self._has_user_auth = True

    def get_app_token(self) -> Union[str, None]:
        """Returns the app token that the api uses or None when not authenticated.

        :return: app token
        """
        return self._app_auth_token

    def get_user_auth_token(self) -> Union[str, None]:
        """Returns the current user auth token, None if no user Authentication is set

        :return: current user auth token
        """
        return self._user_auth_token

    async def get_refreshed_user_auth_token(self) -> Union[str, None]:
        """Validates the current set user auth token and returns it

        Will reauth if token is invalid
        """
        if self._user_auth_token is None:
            return None
        from .oauth import validate_token
        val_result = await validate_token(self._user_auth_token, auth_base_url=self.auth_base_url)
        if val_result.get('status', 200) != 200:
            # refresh token
            await self.refresh_used_token()
        return self._user_auth_token

    async def get_refreshed_app_token(self) -> Optional[str]:
        if self._app_auth_token is None:
            return None
        from .oauth import validate_token
        val_result = await validate_token(self._app_auth_token, auth_base_url=self.auth_base_url)
        if val_result.get('status', 200) != 200:
            await self._refresh_app_token()
        return self._app_auth_token

    def get_used_token(self) -> Union[str, None]:
        """Returns the currently used token, can be either the app or user auth Token or None if no auth is set

        :return: the currently used auth token or None if no Authentication is set
        """
        # if no auth is set, self.__app_auth_token will be None
        return self._user_auth_token if self._has_user_auth else self._app_auth_token

    # ======================================================================================================================
    # API calls
    # ======================================================================================================================

    async def get_extension_analytics(self,
                                      after: Optional[str] = None,
                                      extension_id: Optional[str] = None,
                                      first: int = 20,
                                      ended_at: Optional[datetime] = None,
                                      started_at: Optional[datetime] = None,
                                      report_type: Optional[AnalyticsReportType] = None) -> AsyncGenerator[ExtensionAnalytic, None]:
        """Gets a URL that extension developers can use to download analytics reports (CSV files) for their extensions.
        The URL is valid for 5 minutes.\n\n

        Requires User authentication with scope :py:const:`~twitchAPI.type.AuthScope.ANALYTICS_READ_EXTENSION`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-extension-analytics

        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param extension_id: If this is specified, the returned URL points to an analytics report for just the
                    specified extension. |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :param ended_at: Ending date/time for returned reports, if this is provided, `started_at` must also be specified. |default| :code:`None`
        :param started_at: Starting date/time for returned reports, if this is provided, `ended_at` must also be specified. |default| :code:`None`
        :param report_type: Type of analytics report that is returned |default| :code:`None`
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the extension specified in extension_id was not found
        :raises ValueError: When you only supply `started_at` or `ended_at` without the other or when first is not in range 1 to 100
        """
        if ended_at is not None or started_at is not None:
            # you have to put in both:
            if ended_at is None or started_at is None:
                raise ValueError('you must specify both ended_at and started_at')
            if started_at > ended_at:
                raise ValueError('started_at must be before ended_at')
        if first > 100 or first < 1:
            raise ValueError('first must be between 1 and 100')

        url_params = {
            'after': after,
            'ended_at': datetime_to_str(ended_at),
            'extension_id': extension_id,
            'first': first,
            'started_at': datetime_to_str(started_at),
            'type': enum_value_or_none(report_type)
        }
        async for y in self._build_generator('GET', 'analytics/extensions', url_params, AuthType.USER,
                                             [AuthScope.ANALYTICS_READ_EXTENSION], ExtensionAnalytic):
            yield y

    async def get_game_analytics(self,
                                 after: Optional[str] = None,
                                 first: int = 20,
                                 game_id: Optional[str] = None,
                                 ended_at: Optional[datetime] = None,
                                 started_at: Optional[datetime] = None,
                                 report_type: Optional[AnalyticsReportType] = None) -> AsyncGenerator[GameAnalytics, None]:
        """Gets a URL that game developers can use to download analytics reports (CSV files) for their games.
        The URL is valid for 5 minutes.\n\n

        Requires User authentication with scope :py:const:`~twitchAPI.type.AuthScope.ANALYTICS_READ_GAMES`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-game-analytics

        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :param game_id: Game ID |default| :code:`None`
        :param ended_at: Ending date/time for returned reports, if this is provided, `started_at` must also be specified. |default| :code:`None`
        :param started_at: Starting date/time for returned reports, if this is provided, `ended_at` must also be specified. |default| :code:`None`
        :param report_type: Type of analytics report that is returned. |default| :code:`None`
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the game specified in game_id was not found
        :raises ValueError: When you only supply `started_at` or `ended_at` without the other or when first is not in range 1 to 100
        """
        if ended_at is not None or started_at is not None:
            if ended_at is None or started_at is None:
                raise ValueError('you must specify both ended_at and started_at')
            if ended_at < started_at:
                raise ValueError('ended_at must be after started_at')
        if first > 100 or first < 1:
            raise ValueError('first must be between 1 and 100')
        url_params = {
            'after': after,
            'ended_at': datetime_to_str(ended_at),
            'first': first,
            'game_id': game_id,
            'started_at': datetime_to_str(started_at),
            'type': report_type
        }
        async for y in self._build_generator('GET', 'analytics/game', url_params, AuthType.USER, [AuthScope.ANALYTICS_READ_GAMES], GameAnalytics):
            yield y

    async def get_creator_goals(self, broadcaster_id: str) -> AsyncGenerator[CreatorGoal, None]:
        """Gets Creator Goal Details for the specified channel.

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_GOALS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-creator-goals

        :param broadcaster_id: The ID of the broadcaster that created the goals.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        async for y in self._build_generator('GET', 'goals', {'broadcaster_id': broadcaster_id}, AuthType.USER,
                                             [AuthScope.CHANNEL_READ_GOALS], CreatorGoal):
            yield y

    async def get_bits_leaderboard(self,
                                   count: Optional[int] = 10,
                                   period: Optional[TimePeriod] = TimePeriod.ALL,
                                   started_at: Optional[datetime] = None,
                                   user_id: Optional[str] = None) -> BitsLeaderboard:
        """Gets a ranked list of Bits leaderboard information for an authorized broadcaster.\n\n

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.BITS_READ`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-bits-leaderboard

        :param count: Number of results to be returned. In range 1 to 100, |default| :code:`10`
        :param period: Time period over which data is aggregated, |default| :const:`twitchAPI.types.TimePeriod.ALL`
        :param started_at: Timestamp for the period over which the returned data is aggregated. |default| :code:`None`
        :param user_id: ID of the user whose results are returned; i.e., the person who paid for the Bits. |default| :code:`None`
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if first is not in range 1 to 100
        """
        if count > 100 or count < 1:
            raise ValueError('count must be between 1 and 100')
        url_params = {
            'count': count,
            'period': period.value,
            'started_at': datetime_to_str(started_at),
            'user_id': user_id
        }
        return await self._build_result('GET', 'bits/leaderboard', url_params, AuthType.USER, [AuthScope.BITS_READ], BitsLeaderboard,
                                        get_from_data=False)

    async def get_extension_transactions(self,
                                         extension_id: str,
                                         transaction_id: Optional[Union[str, List[str]]] = None,
                                         after: Optional[str] = None,
                                         first: int = 20) -> AsyncGenerator[ExtensionTransaction, None]:
        """Get Extension Transactions allows extension back end servers to fetch a list of transactions that have
        occurred for their extension across all of Twitch.
        A transaction is a record of a user exchanging Bits for an in-Extension digital good.\n\n

        Requires App authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-extension-transactions

        :param extension_id: ID of the extension to list transactions for.
        :param transaction_id: Transaction IDs to look up. Can either be a list of str or str |default| :code:`None`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :raises ~twitchAPI.type.UnauthorizedException: if app authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid
                        and a re authentication failed
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchResourceNotFound: if one or more transaction IDs specified in transaction_id where not found
        :raises ValueError: if first is not in range 1 to 100
        :raises ValueError: if transaction_ids is longer than 100 entries
        """
        if first > 100 or first < 1:
            raise ValueError("first must be between 1 and 100")
        if transaction_id is not None and isinstance(transaction_id, list) and len(transaction_id) > 100:
            raise ValueError("transaction_ids can't be longer than 100 entries")
        url_param = {
            'extension_id': extension_id,
            'id': transaction_id,
            'after': after,
            'first': first
        }
        async for y in self._build_generator('GET', 'extensions/transactions', url_param, AuthType.EITHER, [], ExtensionTransaction):
            yield y

    async def get_chat_settings(self,
                                broadcaster_id: str,
                                moderator_id: Optional[str] = None) -> ChatSettings:
        """Gets the broadcaster’s chat settings.

        Requires App authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-chat-settings

        :param broadcaster_id: The ID of the broadcaster whose chat settings you want to get
        :param moderator_id: Required only to access the non_moderator_chat_delay or non_moderator_chat_delay_duration settings |default| :code:`None`
        :raises ~twitchAPI.type.UnauthorizedException: if app authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        """
        url_param = {
            'broadcaster_id': broadcaster_id,
            'moderator_id': moderator_id
        }
        return await self._build_result('GET', 'chat/settings', url_param, AuthType.EITHER, [], ChatSettings)

    async def update_chat_settings(self,
                                   broadcaster_id: str,
                                   moderator_id: str,
                                   emote_mode: Optional[bool] = None,
                                   follower_mode: Optional[bool] = None,
                                   follower_mode_duration: Optional[int] = None,
                                   non_moderator_chat_delay: Optional[bool] = None,
                                   non_moderator_chat_delay_duration: Optional[int] = None,
                                   slow_mode: Optional[bool] = None,
                                   slow_mode_wait_time: Optional[int] = None,
                                   subscriber_mode: Optional[bool] = None,
                                   unique_chat_mode: Optional[bool] = None) -> ChatSettings:
        """Updates the broadcaster’s chat settings.

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_CHAT_SETTINGS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#update-chat-settings

        :param broadcaster_id: The ID of the broadcaster whose chat settings you want to update.
        :param moderator_id: The ID of a user that has permission to moderate the broadcaster’s chat room.
        :param emote_mode: A Boolean value that determines whether chat messages must contain only emotes. |default| :code:`None`
        :param follower_mode: A Boolean value that determines whether the broadcaster restricts the chat room to
                    followers only, based on how long they’ve followed. |default| :code:`None`
        :param follower_mode_duration: The length of time, in minutes, that the followers must have followed the
                    broadcaster to participate in the chat room |default| :code:`None`
        :param non_moderator_chat_delay: A Boolean value that determines whether the broadcaster adds a short delay
                    before chat messages appear in the chat room. |default| :code:`None`
        :param non_moderator_chat_delay_duration: he amount of time, in seconds, that messages are delayed
                    from appearing in chat. Possible Values: 2, 4 and 6 |default| :code:`None`
        :param slow_mode: A Boolean value that determines whether the broadcaster limits how often users in the
                    chat room are allowed to send messages. |default| :code:`None`
        :param slow_mode_wait_time: The amount of time, in seconds, that users need to wait between sending messages |default| :code:`None`
        :param subscriber_mode: A Boolean value that determines whether only users that subscribe to the
                    broadcaster’s channel can talk in the chat room. |default| :code:`None`
        :param unique_chat_mode: A Boolean value that determines whether the broadcaster requires users to post
                    only unique messages in the chat room. |default| :code:`None`
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if non_moderator_chat_delay_duration is not one of 2, 4 or 6
        """
        if non_moderator_chat_delay_duration is not None:
            if non_moderator_chat_delay_duration not in (2, 4, 6):
                raise ValueError('non_moderator_chat_delay_duration has to be one of 2, 4 or 6')
        url_param = {
            'broadcaster_id': broadcaster_id,
            'moderator_id': moderator_id
        }
        body = remove_none_values({
            'emote_mode': emote_mode,
            'follower_mode': follower_mode,
            'follower_mode_duration': follower_mode_duration,
            'non_moderator_chat_delay': non_moderator_chat_delay,
            'non_moderator_chat_delay_duration': non_moderator_chat_delay_duration,
            'slow_mode': slow_mode,
            'slow_mode_wait_time': slow_mode_wait_time,
            'subscriber_mode': subscriber_mode,
            'unique_chat_mode': unique_chat_mode
        })
        return await self._build_result('PATCH', 'chat/settings', url_param, AuthType.USER, [AuthScope.MODERATOR_MANAGE_CHAT_SETTINGS],
                                        ChatSettings, body_data=body)

    async def create_clip(self,
                          broadcaster_id: str,
                          has_delay: bool = False) -> CreatedClip:
        """Creates a clip programmatically. This returns both an ID and an edit URL for the new clip.\n\n

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.CLIPS_EDIT`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#create-clip

        :param broadcaster_id: Broadcaster ID of the stream from which the clip will be made.
        :param has_delay: If False, the clip is captured from the live stream when the API is called; otherwise,
                a delay is added before the clip is captured (to account for the brief delay between the broadcaster’s
                stream and the viewer’s experience of that stream). |default| :code:`False`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the broadcaster is not live
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'has_delay': has_delay
        }
        errors = {403: TwitchAPIException('The broadcaster has restricted the ability to capture clips to followers and/or subscribers only or the'
                                          'specified broadcaster has not enabled clips on their channel.')}
        return await self._build_result('POST', 'clips', param, AuthType.USER, [AuthScope.CLIPS_EDIT], CreatedClip, error_handler=errors)

    async def get_clips(self,
                        broadcaster_id: Optional[str] = None,
                        game_id: Optional[str] = None,
                        clip_id: Optional[List[str]] = None,
                        is_featured: Optional[bool] = None,
                        after: Optional[str] = None,
                        before: Optional[str] = None,
                        ended_at: Optional[datetime] = None,
                        started_at: Optional[datetime] = None,
                        first: int = 20) -> AsyncGenerator[Clip, None]:
        """Gets clip information by clip ID (one or more), broadcaster ID (one only), or game ID (one only).
        Clips are returned sorted by view count, in descending order.\n\n

        Requires App or User authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-clips

        :param broadcaster_id: ID of the broadcaster for whom clips are returned. |default| :code:`None`
        :param game_id: ID of the game for which clips are returned. |default| :code:`None`
        :param clip_id: ID of the clip being queried. Limit: 100. |default| :code:`None`
        :param is_featured: A Boolean value that determines whether the response includes featured clips. |br|
                     If :code:`True`, returns only clips that are featured. |br|
                     If :code:`False`, returns only clips that aren’t featured. |br|
                     If :code:`None`, all clips are returned. |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param before: Cursor for backward pagination |default| :code:`None`
        :param ended_at: Ending date/time for returned clips |default| :code:`None`
        :param started_at: Starting date/time for returned clips |default| :code:`None`
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if you try to query more than 100 clips in one call
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ValueError: if not exactly one of clip_id, broadcaster_id or game_id is given
        :raises ValueError: if first is not in range 1 to 100
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the game specified in game_id was not found
        """
        if clip_id is not None and len(clip_id) > 100:
            raise ValueError('A maximum of 100 clips can be queried in one call')
        if not (sum([clip_id is not None, broadcaster_id is not None, game_id is not None]) == 1):
            raise ValueError('You need to specify exactly one of clip_id, broadcaster_id or game_id')
        if first < 1 or first > 100:
            raise ValueError('first must be in range 1 to 100')
        param = {
            'broadcaster_id': broadcaster_id,
            'game_id': game_id,
            'id': clip_id,
            'after': after,
            'before': before,
            'first': first,
            'ended_at': datetime_to_str(ended_at),
            'started_at': datetime_to_str(started_at),
            'is_featured': is_featured
        }
        async for y in self._build_generator('GET', 'clips', param, AuthType.EITHER, [], Clip, split_lists=True):
            yield y

    async def get_top_games(self,
                            after: Optional[str] = None,
                            before: Optional[str] = None,
                            first: int = 20) -> AsyncGenerator[Game, None]:
        """Gets games sorted by number of current viewers on Twitch, most popular first.\n\n

        Requires App or User authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-top-games

        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param before: Cursor for backward pagination |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if app authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if first is not in range 1 to 100
        """
        if first < 1 or first > 100:
            raise ValueError('first must be between 1 and 100')
        param = {
            'after': after,
            'before': before,
            'first': first
        }
        async for y in self._build_generator('GET', 'games/top', param, AuthType.EITHER, [], Game):
            yield y

    async def get_games(self,
                        game_ids: Optional[List[str]] = None,
                        names: Optional[List[str]] = None,
                        igdb_ids: Optional[List[str]] = None) -> AsyncGenerator[Game, None]:
        """Gets game information by game ID or name.\n\n

        Requires User or App authentication.
        In total, only 100 game ids and names can be fetched at once.

        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-games

        :param game_ids: Game ID |default| :code:`None`
        :param names: Game Name |default| :code:`None`
        :param igdb_ids: IGDB ID |default| :code:`None`
        :raises ~twitchAPI.type.UnauthorizedException: if app authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if none of game_ids, names or igdb_ids are given or if game_ids, names and igdb_ids are more than 100 entries combined.
        """
        if game_ids is None and names is None and igdb_ids is None:
            raise ValueError('at least one of game_ids, names or igdb_ids has to be set')
        if (len(game_ids) if game_ids is not None else 0) + \
                (len(names) if names is not None else 0) + \
                (len(igdb_ids) if igdb_ids is not None else 0) > 100:
            raise ValueError('in total, only 100 game_ids, names and igdb_ids can be passed')
        param = {
            'id': game_ids,
            'name': names,
            'igdb_id': igdb_ids
        }
        async for y in self._build_generator('GET', 'games', param, AuthType.EITHER, [], Game, split_lists=True):
            yield y

    async def check_automod_status(self,
                                   broadcaster_id: str,
                                   automod_check_entries: List[AutoModCheckEntry]) -> AsyncGenerator[AutoModStatus, None]:
        """Determines whether a string message meets the channel’s AutoMod requirements.\n\n

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.MODERATION_READ`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#check-automod-status

        :param broadcaster_id: Provided broadcaster ID must match the user ID in the user auth token.
        :param automod_check_entries: The Automod Check Entries
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        """
        body = {'data': automod_check_entries}
        async for y in self._build_generator('POST', 'moderation/enforcements/status', {'broadcaster_id': broadcaster_id},
                                             AuthType.USER, [AuthScope.MODERATION_READ], AutoModStatus, body_data=body):
            yield y

    async def get_automod_settings(self,
                                   broadcaster_id: str,
                                   moderator_id: str) -> AutoModSettings:
        """Gets the broadcaster’s AutoMod settings.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_AUTOMOD_SETTINGS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-automod-settings

        :param broadcaster_id: The ID of the broadcaster whose AutoMod settings you want to get.
        :param moderator_id: The ID of the broadcaster or a user that has permission to moderate the broadcaster’s chat room.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        param = {
            "broadcaster_id": broadcaster_id,
            "moderator_id": moderator_id
        }
        error_handler = {403: TwitchAPIException('Forbidden: The user in moderator_id is not one of the broadcaster\'s moderators.')}
        return await self._build_result('GET',
                                        'moderation/automod/settings',
                                        param,
                                        AuthType.USER,
                                        [AuthScope.MODERATOR_READ_AUTOMOD_SETTINGS],
                                        AutoModSettings,
                                        error_handler=error_handler)

    async def update_automod_settings(self,
                                      broadcaster_id: str,
                                      moderator_id: str,
                                      settings: Optional[AutoModSettings] = None,
                                      overall_level: Optional[int] = None) -> AutoModSettings:
        """Updates the broadcaster’s AutoMod settings.

        You can either set the individual level or the overall level, but not both at the same time.
        Setting the overall_level parameter in settings will be ignored.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_AUTOMOD_SETTINGS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#update-automod-settings

        :param broadcaster_id: The ID of the broadcaster whose AutoMod settings you want to update.
        :param moderator_id: The ID of the broadcaster or a user that has permission to moderate the broadcaster’s chat room.
        :param settings: If you want to change individual settings, set this. |default|:code:`None`
        :param overall_level: If you want to change the overall level, set this. |default|:code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if both settings and overall_level are given or none of them are given
        """
        if (settings is not None and overall_level is not None) or (settings is None and overall_level is None):
            raise ValueError('You have to specify exactly one of settings or oevrall_level')
        param = {
            "broadcaster_id": broadcaster_id,
            "moderator_id": moderator_id
        }
        body = settings.to_dict() if settings is not None else {}
        body['overall_level'] = overall_level
        return await self._build_result('PUT',
                                        'moderation/automod/settings',
                                        param,
                                        AuthType.USER,
                                        [AuthScope.MODERATOR_MANAGE_AUTOMOD_SETTINGS],
                                        AutoModSettings,
                                        body_data=remove_none_values(body))

    async def get_banned_users(self,
                               broadcaster_id: str,
                               user_id: Optional[str] = None,
                               after: Optional[str] = None,
                               first: Optional[int] = 20,
                               before: Optional[str] = None) -> AsyncGenerator[BannedUser, None]:
        """Returns all banned and timed-out users in a channel.\n\n

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.MODERATION_READ`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-banned-users

        :param broadcaster_id: Provided broadcaster ID must match the user ID in the user auth token.
        :param user_id: Filters the results and only returns a status object for users who are banned in this
                        channel and have a matching user_id. |default| :code:`None`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param before: Cursor for backward pagination |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if first is not in range 1 to 100
        """
        if first < 1 or first > 100:
            raise ValueError('first must be in range 1 to 100')
        param = {
            'broadcaster_id': broadcaster_id,
            'user_id': user_id,
            'after': after,
            'first': first,
            'before': before
        }
        async for y in self._build_generator('GET', 'moderation/banned', param, AuthType.USER, [AuthScope.MODERATION_READ], BannedUser):
            yield y

    async def ban_user(self,
                       broadcaster_id: str,
                       moderator_id: str,
                       user_id: str,
                       reason: str,
                       duration: Optional[int] = None) -> BanUserResponse:
        """Bans a user from participating in a broadcaster’s chat room, or puts them in a timeout.

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_BANNED_USERS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#ban-user

        :param broadcaster_id: The ID of the broadcaster whose chat room the user is being banned from.
        :param moderator_id: The ID of a user that has permission to moderate the broadcaster’s chat room. This ID must match the user ID
                    associated with the user OAuth token.
        :param user_id: The ID of the user to ban or put in a timeout.
        :param reason: The reason the user is being banned or put in a timeout. The text is user defined and limited to a maximum of 500 characters.
        :param duration: To ban a user indefinitely, don't set this. Put a user in timeout for the number of seconds specified.
                    Maximum 1_209_600 (2 weeks) |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if duration is set and not between 1 and 1_209_600
        :raises ValueError: if reason is not between 1 and 500 characters in length
        """
        if duration is not None and (duration < 1 or duration > 1_209_600):
            raise ValueError('duration must be either omitted or between 1 and 1209600')
        if len(reason) < 1 or len(reason) > 500:
            raise ValueError('reason must be between 1 and 500 characters in length')
        param = {
            'broadcaster_id': broadcaster_id,
            'moderator_id': moderator_id
        }
        body = {
            'data': remove_none_values({
                'duration': duration,
                'reason': reason,
                'user_id': user_id
            })
        }
        return await self._build_result('POST', 'moderation/bans', param, AuthType.USER, [AuthScope.MODERATOR_MANAGE_BANNED_USERS], BanUserResponse,
                                        body_data=body, get_from_data=True)

    async def unban_user(self,
                         broadcaster_id: str,
                         moderator_id: str,
                         user_id: str) -> bool:
        """Removes the ban or timeout that was placed on the specified user

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_BANNED_USERS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#unban-user

        :param broadcaster_id: The ID of the broadcaster whose chat room the user is banned from chatting in.
        :param moderator_id: The ID of a user that has permission to moderate the broadcaster’s chat room.
                    This ID must match the user ID associated with the user OAuth token.
        :param user_id: The ID of the user to remove the ban or timeout from.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'moderator_id': moderator_id,
            'user_id': user_id
        }
        return await self._build_result('DELETE', 'moderation/bans', param, AuthType.USER, [AuthScope.MODERATOR_MANAGE_BANNED_USERS], None,
                                        result_type=ResultType.STATUS_CODE) == 204

    async def get_blocked_terms(self,
                                broadcaster_id: str,
                                moderator_id: str,
                                after: Optional[str] = None,
                                first: Optional[int] = None) -> AsyncGenerator[BlockedTerm, None]:
        """Gets the broadcaster’s list of non-private, blocked words or phrases.
        These are the terms that the broadcaster or moderator added manually, or that were denied by AutoMod.

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_BLOCKED_TERMS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-blocked-terms

        :param broadcaster_id: The ID of the broadcaster whose blocked terms you’re getting.
        :param moderator_id: The ID of a user that has permission to moderate the broadcaster’s chat room.
                    This ID must match the user ID associated with the user OAuth token.
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if first is set and not between 1 and 100
        """
        if first is not None and (first < 1 or first > 100):
            raise ValueError('first must be between 1 and 100')
        param = {
            'broadcaster_id': broadcaster_id,
            'moderator_id': moderator_id,
            'first': first,
            'after': after
        }
        async for y in self._build_generator('GET', 'moderation/blocked_terms', param, AuthType.USER, [AuthScope.MODERATOR_READ_BLOCKED_TERMS],
                                             BlockedTerm):
            yield y

    async def add_blocked_term(self,
                               broadcaster_id: str,
                               moderator_id: str,
                               text: str) -> BlockedTerm:
        """Adds a word or phrase to the broadcaster’s list of blocked terms. These are the terms that broadcasters don’t want used in their chat room.

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_BLOCKED_TERMS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#add-blocked-term

        :param broadcaster_id: The ID of the broadcaster that owns the list of blocked terms.
        :param moderator_id: The ID of a user that has permission to moderate the broadcaster’s chat room.
                    This ID must match the user ID associated with the user OAuth token.
        :param text: The word or phrase to block from being used in the broadcaster’s chat room. Between 2 and 500 characters long
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if text is not between 2 and 500 characters long
        """
        if len(text) < 2 or len(text) > 500:
            raise ValueError('text must have a length between 2 and 500 characters')
        param = {
            'broadcaster_id': broadcaster_id,
            'moderator_id': moderator_id
        }
        body = {'text': text}
        return await self._build_result('POST', 'moderation/blocked_terms', param, AuthType.USER, [AuthScope.MODERATOR_MANAGE_BLOCKED_TERMS],
                                        BlockedTerm, body_data=body)

    async def remove_blocked_term(self,
                                  broadcaster_id: str,
                                  moderator_id: str,
                                  term_id: str) -> bool:
        """Removes the word or phrase that the broadcaster is blocking users from using in their chat room.

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_BLOCKED_TERMS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#remove-blocked-term

        :param broadcaster_id: The ID of the broadcaster that owns the list of blocked terms.
        :param moderator_id: The ID of a user that has permission to moderate the broadcaster’s chat room.
                        This ID must match the user ID associated with the user OAuth token.
        :param term_id: The ID of the blocked term you want to delete.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'moderator_id': moderator_id,
            'id': term_id
        }
        return await self._build_result('DELETE', 'moderation/blocked_terms', param, AuthType.USER, [AuthScope.MODERATOR_MANAGE_BLOCKED_TERMS],
                                        None, result_type=ResultType.STATUS_CODE) == 204

    async def get_moderators(self,
                             broadcaster_id: str,
                             user_ids: Optional[List[str]] = None,
                             first: Optional[int] = 20,
                             after: Optional[str] = None) -> AsyncGenerator[Moderator, None]:
        """Returns all moderators in a channel.\n\n

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.MODERATION_READ`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-moderators

        :param broadcaster_id: Provided broadcaster ID must match the user ID in the user auth token.
        :param user_ids: Filters the results and only returns a status object for users who are moderator in
                        this channel and have a matching user_id. Maximum 100 |default| :code:`None`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if user_ids has more than 100 entries
        :raises ValueError: if first is not in range 1 to 100
        """
        if first < 1 or first > 100:
            raise ValueError('first must be in range 1 to 100')
        if user_ids is not None and len(user_ids) > 100:
            raise ValueError('user_ids can only be 100 entries long')
        param = {
            'broadcaster_id': broadcaster_id,
            'user_id': user_ids,
            'first': first,
            'after': after
        }
        async for y in self._build_generator('GET', 'moderation/moderators', param, AuthType.USER, [AuthScope.MODERATION_READ], Moderator,
                                             split_lists=True):
            yield y

    async def create_stream_marker(self,
                                   user_id: str,
                                   description: Optional[str] = None) -> CreateStreamMarkerResponse:
        """Creates a marker in the stream of a user specified by user ID.\n\n

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_BROADCAST`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#create-stream-marker

        :param user_id: ID of the broadcaster in whose live stream the marker is created.
        :param description: Description of or comments on the marker. Max length is 140 characters. |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if description has more than 140 characters
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the user in user_id is not live, the ID is not valid or has not enabled VODs
        """
        if description is not None and len(description) > 140:
            raise ValueError('max length for description is 140')
        body = {'user_id': user_id}
        if description is not None:
            body['description'] = description
        return await self._build_result('POST', 'streams/markers', {}, AuthType.USER, [AuthScope.CHANNEL_MANAGE_BROADCAST],
                                        CreateStreamMarkerResponse, body_data=body)

    async def get_streams(self,
                          after: Optional[str] = None,
                          before: Optional[str] = None,
                          first: int = 20,
                          game_id: Optional[List[str]] = None,
                          language: Optional[List[str]] = None,
                          user_id: Optional[List[str]] = None,
                          user_login: Optional[List[str]] = None,
                          stream_type: Optional[str] = None) -> AsyncGenerator[Stream, None]:
        """Gets information about active streams. Streams are returned sorted by number of current viewers, in
        descending order. Across multiple pages of results, there may be duplicate or missing streams, as viewers join
        and leave streams.\n\n

        Requires App or User authentication.\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-streams

        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param before: Cursor for backward pagination |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :param game_id: Returns streams broadcasting a specified game ID. You can specify up to 100 IDs. |default| :code:`None`
        :param language: Stream language. You can specify up to 100 languages. |default| :code:`None`
        :param user_id: Returns streams broadcast by one or more specified user IDs. You can specify up to 100 IDs. |default| :code:`None`
        :param user_login: Returns streams broadcast by one or more specified user login names.
                        You can specify up to 100 names. |default| :code:`None`
        :param stream_type: The type of stream to filter the list of streams by. Possible values are :code:`all` and :code:`live`
                        |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if app authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if first is not in range 1 to 100 or one of the following fields have more than 100 entries:
                        `user_id, game_id, language, user_login`
        """
        if user_id is not None and len(user_id) > 100:
            raise ValueError('a maximum of 100 user_id entries are allowed')
        if user_login is not None and len(user_login) > 100:
            raise ValueError('a maximum of 100 user_login entries are allowed')
        if language is not None and len(language) > 100:
            raise ValueError('a maximum of 100 languages are allowed')
        if game_id is not None and len(game_id) > 100:
            raise ValueError('a maximum of 100 game_id entries are allowed')
        if first > 100 or first < 1:
            raise ValueError('first must be between 1 and 100')
        param = {
            'after': after,
            'before': before,
            'first': first,
            'game_id': game_id,
            'language': language,
            'user_id': user_id,
            'user_login': user_login,
            'type': stream_type
        }
        async for y in self._build_generator('GET', 'streams', param, AuthType.EITHER, [], Stream, split_lists=True):
            yield y

    async def get_stream_markers(self,
                                 user_id: str,
                                 video_id: str,
                                 after: Optional[str] = None,
                                 before: Optional[str] = None,
                                 first: int = 20) -> AsyncGenerator[GetStreamMarkerResponse, None]:
        """Gets a list of markers for either a specified user’s most recent stream or a specified VOD/video (stream),
        ordered by recency.\n\n

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.USER_READ_BROADCAST`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-stream-markers

        Only one of user_id and video_id must be specified.

        :param user_id: ID of the broadcaster from whose stream markers are returned.
        :param video_id: ID of the VOD/video whose stream markers are returned.
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param before: Cursor for backward pagination |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if first is not in range 1 to 100 or neither user_id nor video_id is provided
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the user specified in user_id does not have videos
        """
        if first > 100 or first < 1:
            raise ValueError('first must be between 1 and 100')
        if user_id is None and video_id is None:
            raise ValueError('you must specify either user_id and/or video_id')
        param = {
            'user_id': user_id,
            'video_id': video_id,
            'after': after,
            'before': before,
            'first': first
        }
        async for y in self._build_generator('GET', 'streams/markers', param, AuthType.USER, [AuthScope.USER_READ_BROADCAST],
                                             GetStreamMarkerResponse):
            yield y

    async def get_broadcaster_subscriptions(self,
                                            broadcaster_id: str,
                                            user_ids: Optional[List[str]] = None,
                                            after: Optional[str] = None,
                                            first: Optional[int] = 20) -> BroadcasterSubscriptions:
        """Get all of a broadcaster’s subscriptions.\n\n

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_SUBSCRIPTIONS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-broadcaster-subscriptions

        :param broadcaster_id: User ID of the broadcaster. Must match the User ID in the Bearer token.
        :param user_ids: Unique identifier of account to get subscription status of. Maximum 100 entries |default| :code:`None`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if user_ids has more than 100 entries
        :raises ValueError: if first is not in range 1 to 100
        """
        if first < 1 or first > 100:
            raise ValueError('first must be in range 1 to 100')
        if user_ids is not None and len(user_ids) > 100:
            raise ValueError('user_ids can have a maximum of 100 entries')
        param = {
            'broadcaster_id': broadcaster_id,
            'user_id': user_ids,
            'first': first,
            'after': after
        }
        return await self._build_iter_result('GET', 'subscriptions', param, AuthType.USER, [AuthScope.CHANNEL_READ_SUBSCRIPTIONS],
                                             BroadcasterSubscriptions, split_lists=True)

    async def check_user_subscription(self,
                                      broadcaster_id: str,
                                      user_id: str) -> UserSubscription:
        """Checks if a specific user (user_id) is subscribed to a specific channel (broadcaster_id).

        Requires User or App Authorization with scope :const:`~twitchAPI.type.AuthScope.USER_READ_SUBSCRIPTIONS`

        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#check-user-subscription

        :param broadcaster_id: User ID of an Affiliate or Partner broadcaster.
        :param user_id: User ID of a Twitch viewer.
        :raises ~twitchAPI.type.UnauthorizedException: if app or user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the app or user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchResourceNotFound: if user is not subscribed to the given broadcaster
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'user_id': user_id
        }
        return await self._build_result('GET', 'subscriptions/user', param, AuthType.EITHER, [AuthScope.USER_READ_SUBSCRIPTIONS], UserSubscription)

    async def get_channel_teams(self,
                                broadcaster_id: str) -> List[ChannelTeam]:
        """Retrieves a list of Twitch Teams of which the specified channel/broadcaster is a member.\n\n

        Requires User or App authentication.

        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference/#get-channel-teams

        :param broadcaster_id: User ID for a Twitch user.
        :raises ~twitchAPI.type.UnauthorizedException: if app or user authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the broadcaster was not found or is not member of a team
        """
        return await self._build_result('GET', 'teams/channel', {'broadcaster_id': broadcaster_id}, AuthType.EITHER, [], List[ChannelTeam])

    async def get_teams(self,
                        team_id: Optional[str] = None,
                        name: Optional[str] = None) -> ChannelTeam:
        """Gets information for a specific Twitch Team.\n\n

        Requires User or App authentication.
        One of the two optional query parameters must be specified.

        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference/#get-teams

        :param team_id: Team ID |default| :code:`None`
        :param name: Team Name |default| :code:`None`
        :raises ~twitchAPI.type.UnauthorizedException: if app or user authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if neither team_id nor name are given or if both team_id and names are given.
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the specified team was not found
        """
        if team_id is None and name is None:
            raise ValueError('You need to specify one of the two optional parameter.')
        if team_id is not None and name is not None:
            raise ValueError('Only one optional parameter must be specified.')
        param = {
            'id': team_id,
            'name': name
        }
        return await self._build_result('GET', 'teams', param, AuthType.EITHER, [], ChannelTeam)

    async def get_users(self,
                        user_ids: Optional[List[str]] = None,
                        logins: Optional[List[str]] = None) -> AsyncGenerator[TwitchUser, None]:
        """Gets information about one or more specified Twitch users.
        Users are identified by optional user IDs and/or login name.
        If neither a user ID nor a login name is specified, the user is the one authenticated.\n\n

        Requires App authentication if either user_ids or logins is provided, otherwise requires a User authentication.
        If you have user Authentication and want to get your email info, you also need the authentication scope
        :const:`~twitchAPI.type.AuthScope.USER_READ_EMAIL`\n
        If you provide user_ids and/or logins, the maximum combined entries should not exceed 100.

        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-users

        :param user_ids: User ID. Multiple user IDs can be specified. Limit: 100. |default| :code:`None`
        :param logins: User login name. Multiple login names can be specified. Limit: 100. |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if more than 100 combined user_ids and logins where provided
        """
        if (len(user_ids) if user_ids is not None else 0) + (len(logins) if logins is not None else 0) > 100:
            raise ValueError('the total number of entries in user_ids and logins can not be more than 100')
        url_params = {
            'id': user_ids,
            'login': logins
        }
        at = AuthType.USER if (user_ids is None or len(user_ids) == 0) and (logins is None or len(logins) == 0) else AuthType.EITHER
        async for f in self._build_generator('GET', 'users', url_params, at, [], TwitchUser, split_lists=True):
            yield f

    async def get_channel_followers(self,
                                    broadcaster_id: str,
                                    user_id: Optional[str] = None,
                                    first: Optional[int] = None,
                                    after: Optional[str] = None) -> ChannelFollowersResult:
        """ Gets a list of users that follow the specified broadcaster.
        You can also use this endpoint to see whether a specific user follows the broadcaster.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_FOLLOWERS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-channel-followers

        .. note:: This can also be used without the required scope or just with App Authentication, but the result will only include the total number
                  of followers in these cases.

        :param broadcaster_id: The broadcaster’s ID. Returns the list of users that follow this broadcaster.
        :param user_id: A user’s ID. Use this parameter to see whether the user follows this broadcaster.
            If specified, the response contains this user if they follow the broadcaster.
            If not specified, the response contains all users that follow the broadcaster. |default|:code:`None`
        :param first: The maximum number of items to return per API call.
                    You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                    fetch the amount of results you desire.\n
                    Minimum 1, Maximum 100 |default| :code:`20`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if first is not in range 1 to 100
        """
        if first is not None and (first < 1 or first > 100):
            raise ValueError('first must be in range 1 to 100')
        param = {
            'broadcaster_id': broadcaster_id,
            'user_id': user_id,
            'first': first,
            'after': after
        }
        return await self._build_iter_result('GET', 'channels/followers', param, AuthType.EITHER, [], ChannelFollowersResult)

    async def get_followed_channels(self,
                                    user_id: str,
                                    broadcaster_id: Optional[str] = None,
                                    first: Optional[int] = None,
                                    after: Optional[str] = None) -> FollowedChannelsResult:
        """Gets a list of broadcasters that the specified user follows.
        You can also use this endpoint to see whether a user follows a specific broadcaster.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.USER_READ_FOLLOWS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-followed-channels

        :param user_id: A user’s ID. Returns the list of broadcasters that this user follows. This ID must match the user ID in the user OAuth token.
        :param broadcaster_id: A broadcaster’s ID. Use this parameter to see whether the user follows this broadcaster.
            If specified, the response contains this broadcaster if the user follows them.
            If not specified, the response contains all broadcasters that the user follows. |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if first is not in range 1 to 100
        """
        if first is not None and (first < 1 or first > 100):
            raise ValueError('first must be in range 1 to 100')
        param = {
            'user_id': user_id,
            'broadcaster_id': broadcaster_id,
            'first': first,
            'after': after
        }
        return await self._build_iter_result('GET', 'channels/followed', param, AuthType.USER, [AuthScope.USER_READ_FOLLOWS], FollowedChannelsResult)

    async def update_user(self,
                          description: str) -> TwitchUser:
        """Updates the description of the Authenticated user.\n\n

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.USER_EDIT`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#update-user

        :param description: User’s account description
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        """
        return await self._build_result('PUT', 'users', {'description': description}, AuthType.USER, [AuthScope.USER_EDIT], TwitchUser)

    async def get_user_extensions(self) -> List[UserExtension]:
        """Gets a list of all extensions (both active and inactive) for the authenticated user\n\n

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.USER_READ_BROADCAST`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-user-extensions

        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        """
        return await self._build_result('GET', 'users/extensions/list', {}, AuthType.USER, [AuthScope.USER_READ_BROADCAST], List[UserExtension])

    async def get_user_active_extensions(self,
                                         user_id: Optional[str] = None) -> UserActiveExtensions:
        """Gets information about active extensions installed by a specified user, identified by a user ID or the
        authenticated user.\n\n

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.USER_READ_BROADCAST`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-user-active-extensions

        :param user_id: ID of the user whose installed extensions will be returned. |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        """
        return await self._build_result('GET', 'users/extensions', {'user_id': user_id}, AuthType.USER, [AuthScope.USER_READ_BROADCAST],
                                        UserActiveExtensions)

    async def update_user_extensions(self,
                                     data: UserActiveExtensions) -> UserActiveExtensions:
        """"Updates the activation state, extension ID, and/or version number of installed extensions
        for the authenticated user.\n\n

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.USER_EDIT_BROADCAST`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#update-user-extensions

        :param data: The user extension data to be written
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the extension specified in id and version was not found
        """
        dat = {'data': data.to_dict(False)}
        return await self._build_result('PUT', 'users/extensions', {}, AuthType.USER, [AuthScope.USER_EDIT_BROADCAST], UserActiveExtensions,
                                        body_data=dat)

    async def get_videos(self,
                         ids: Optional[List[str]] = None,
                         user_id: Optional[str] = None,
                         game_id: Optional[str] = None,
                         after: Optional[str] = None,
                         before: Optional[str] = None,
                         first: Optional[int] = 20,
                         language: Optional[str] = None,
                         period: TimePeriod = TimePeriod.ALL,
                         sort: SortMethod = SortMethod.TIME,
                         video_type: VideoType = VideoType.ALL) -> AsyncGenerator[Video, None]:
        """Gets video information by video ID (one or more), user ID (one only), or game ID (one only).\n\n

        Requires App authentication.\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-videos

        :param ids: ID of the video being queried. Limit: 100. |default| :code:`None`
        :param user_id: ID of the user who owns the video. |default| :code:`None`
        :param game_id: ID of the game the video is of. |default| :code:`None`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param before: Cursor for backward pagination |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :param language: Language of the video being queried. |default| :code:`None`
        :param period: Period during which the video was created. |default| :code:`TimePeriod.ALL`
        :param sort: Sort order of the videos. |default| :code:`SortMethod.TIME`
        :param video_type: Type of video. |default| :code:`VideoType.ALL`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if app authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if first is not in range 1 to 100, ids has more than 100 entries or none of ids, user_id nor game_id is provided.
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the game_id was not found or all IDs in video_id where not found
        """
        if ids is None and user_id is None and game_id is None:
            raise ValueError('you must use either ids, user_id or game_id')
        if first < 1 or first > 100:
            raise ValueError('first must be between 1 and 100')
        if ids is not None and len(ids) > 100:
            raise ValueError('ids can only have a maximum of 100 entries')
        param = {
            'id': ids,
            'user_id': user_id,
            'game_id': game_id,
            'after': after,
            'before': before,
            'first': first,
            'language': language,
            'period': period.value,
            'sort': sort.value,
            'type': video_type.value
        }
        async for y in self._build_generator('GET', 'videos', param, AuthType.EITHER, [], Video, split_lists=True):
            yield y

    async def get_channel_information(self,
                                      broadcaster_id: Union[str, List[str]]) -> List[ChannelInformation]:
        """Gets channel information for users.\n\n

        Requires App or user authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-channel-information

        :param broadcaster_id: ID of the channel to be returned, can either be a string or a list of strings with up to 100 entries
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if app authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if broadcaster_id is a list and does not have between 1 and 100 entries
        """
        if isinstance(broadcaster_id, list):
            if len(broadcaster_id) < 1 or len(broadcaster_id) > 100:
                raise ValueError('broadcaster_id has to have between 1 and 100 entries')
        return await self._build_result('GET', 'channels', {'broadcaster_id': broadcaster_id}, AuthType.EITHER, [], List[ChannelInformation],
                                        split_lists=True)

    async def modify_channel_information(self,
                                         broadcaster_id: str,
                                         game_id: Optional[str] = None,
                                         broadcaster_language: Optional[str] = None,
                                         title: Optional[str] = None,
                                         delay: Optional[int] = None,
                                         tags: Optional[List[str]] = None,
                                         content_classification_labels: Optional[List[str]] = None,
                                         is_branded_content: Optional[bool] = None) -> bool:
        """Modifies channel information for users.\n\n

        Requires User authentication with scope :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_BROADCAST`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#modify-channel-information

        :param broadcaster_id: ID of the channel to be updated
        :param game_id: The current game ID being played on the channel |default| :code:`None`
        :param broadcaster_language: The language of the channel |default| :code:`None`
        :param title: The title of the stream |default| :code:`None`
        :param delay: Stream delay in seconds. Trying to set this while not being a Twitch Partner will fail! |default| :code:`None`
        :param tags: A list of channel-defined tags to apply to the channel. To remove all tags from the channel, set tags to an empty array.
                |default|:code:`None`
        :param content_classification_labels: List of labels that should be set as the Channel’s CCLs.
        :param is_branded_content: Boolean flag indicating if the channel has branded content.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if none of the following fields are specified: `game_id, broadcaster_language, title`
        :raises ValueError: if title is a empty string
        :raises ValueError: if tags has more than 10 entries
        :raises ValueError: if requested a gaming CCL to channel or used Unallowed CCLs declared for underaged authorized user in a restricted country
        :raises ValueError: if the is_branded_content flag was set too frequently
        """
        if game_id is None and broadcaster_language is None and title is None and tags is None:
            raise ValueError('You need to specify at least one of the optional parameter')
        if title is not None and len(title) == 0:
            raise ValueError("title can't be a empty string")
        if tags is not None and len(tags) > 10:
            raise ValueError('tags can only contain up to 10 items')
        body = {k: v for k, v in {'game_id': game_id,
                                  'broadcaster_language': broadcaster_language,
                                  'title': title,
                                  'delay': delay,
                                  'tags': tags,
                                  'content_classification_labels': content_classification_labels,
                                  'is_branded_content': is_branded_content}.items() if v is not None}
        error_handler = {403: ValueError('Either requested to add gaming CCL to channel or used Unallowed CCLs declared for underaged authorized '
                                         'user in a restricted country'),
                         409: ValueError('tried to set is_branded_content flag too frequently')}
        return await self._build_result('PATCH', 'channels', {'broadcaster_id': broadcaster_id}, AuthType.USER,
                                        [AuthScope.CHANNEL_MANAGE_BROADCAST], None, body_data=body, result_type=ResultType.STATUS_CODE,
                                        error_handler=error_handler) == 204

    async def search_channels(self,
                              query: str,
                              first: Optional[int] = 20,
                              after: Optional[str] = None,
                              live_only: Optional[bool] = False) -> AsyncGenerator[SearchChannelResult, None]:
        """Returns a list of channels (users who have streamed within the past 6 months) that match the query via
        channel name or description either entirely or partially.\n\n

        Requires App authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#search-channels

        :param query: search query
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param live_only: Filter results for live streams only. |default| :code:`False`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if app authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if first is not in range 1 to 100
        """
        if first < 1 or first > 100:
            raise ValueError('first must be between 1 and 100')
        param = {'query': query,
                 'first': first,
                 'after': after,
                 'live_only': live_only}
        async for y in self._build_generator('GET', 'search/channels', param, AuthType.EITHER, [], SearchChannelResult):
            yield y

    async def search_categories(self,
                                query: str,
                                first: Optional[int] = 20,
                                after: Optional[str] = None) -> AsyncGenerator[SearchCategoryResult, None]:
        """Returns a list of games or categories that match the query via name either entirely or partially.\n\n

        Requires App authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#search-categories

        :param query: search query
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if app authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if first is not in range 1 to 100
        """
        if first < 1 or first > 100:
            raise ValueError('first must be between 1 and 100')
        param = {'query': query,
                 'first': first,
                 'after': after}
        async for y in self._build_generator('GET', 'search/categories', param, AuthType.EITHER, [], SearchCategoryResult):
            yield y

    async def get_stream_key(self,
                             broadcaster_id: str) -> str:
        """Gets the channel stream key for a user.\n\n

        Requires User authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_STREAM_KEY`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-stream-key

        :param broadcaster_id: User ID of the broadcaster
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        """
        data = await self._build_result('GET', 'streams/key', {'broadcaster_id': broadcaster_id}, AuthType.USER, [AuthScope.CHANNEL_READ_STREAM_KEY],
                                        dict)
        return data['stream_key']

    async def start_commercial(self,
                               broadcaster_id: str,
                               length: int) -> StartCommercialResult:
        """Starts a commercial on a specified channel.\n\n

        Requires User authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_EDIT_COMMERCIAL`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#start-commercial

        :param broadcaster_id: ID of the channel requesting a commercial
        :param length: Desired length of the commercial in seconds. , one of these: [30, 60, 90, 120, 150, 180]
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the broadcaster_id was not found
        :raises ValueError: if length is not one of these: :code:`30, 60, 90, 120, 150, 180`
        """
        if length not in [30, 60, 90, 120, 150, 180]:
            raise ValueError('length needs to be one of these: [30, 60, 90, 120, 150, 180]')
        param = {
            'broadcaster_id': broadcaster_id,
            'length': length
        }
        return await self._build_result('POST', 'channels/commercial', param, AuthType.USER, [AuthScope.CHANNEL_EDIT_COMMERCIAL],
                                        StartCommercialResult)

    async def get_cheermotes(self,
                             broadcaster_id: str) -> GetCheermotesResponse:
        """Retrieves the list of available Cheermotes, animated emotes to which viewers can assign Bits,
        to cheer in chat.\n\n

        Requires App authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-cheermotes

        :param broadcaster_id: ID for the broadcaster who might own specialized Cheermotes.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if app authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        """
        return await self._build_result('GET', 'bits/cheermotes', {'broadcaster_id': broadcaster_id}, AuthType.EITHER, [], GetCheermotesResponse)

    async def get_hype_train_events(self,
                                    broadcaster_id: str,
                                    first: Optional[int] = 1,
                                    cursor: Optional[str] = None) -> AsyncGenerator[HypeTrainEvent, None]:
        """Gets the information of the most recent Hype Train of the given channel ID.
        When there is currently an active Hype Train, it returns information about that Hype Train.
        When there is currently no active Hype Train, it returns information about the most recent Hype Train.
        After 5 days, if no Hype Train has been active, the endpoint will return an empty response.\n\n

        Requires App or User authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_HYPE_TRAIN`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-hype-train-events

        :param broadcaster_id: User ID of the broadcaster.
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`1`
        :param cursor: Cursor for forward pagination |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if app authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user or app authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if first is not in range 1 to 100
        """
        if first < 1 or first > 100:
            raise ValueError('first must be between 1 and 100')
        param = {'broadcaster_id': broadcaster_id,
                 'first': first,
                 'cursor': cursor}
        async for y in self._build_generator('GET', 'hypetrain/events', param, AuthType.EITHER, [AuthScope.CHANNEL_READ_HYPE_TRAIN], HypeTrainEvent):
            yield y

    async def get_drops_entitlements(self,
                                     entitlement_id: Optional[str] = None,
                                     user_id: Optional[str] = None,
                                     game_id: Optional[str] = None,
                                     after: Optional[str] = None,
                                     first: Optional[int] = 20) -> AsyncGenerator[DropsEntitlement, None]:
        """Gets a list of entitlements for a given organization that have been granted to a game, user, or both.

        OAuth Token Client ID must have ownership of Game\n\n

        Requires App or User authentication\n
        See Twitch documentation for valid parameter combinations!\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-drops-entitlements

        :param entitlement_id: Unique Identifier of the entitlement |default| :code:`None`
        :param user_id: A Twitch User ID |default| :code:`None`
        :param game_id: A Twitch Game ID |default| :code:`None`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if app authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ValueError: if first is not in range 1 to 1000
        """
        if first < 1 or first > 1000:
            raise ValueError('first must be between 1 and 1000')
        can_use, auth_type, token, scope = self._get_used_either_auth([])
        if auth_type == AuthType.USER:
            if user_id is not None:
                raise ValueError('cant use user_id when using User Authentication')
        param = {
            'id': entitlement_id,
            'user_id': user_id,
            'game_id': game_id,
            'after': after,
            'first': first
        }
        async for y in self._build_generator('GET', 'entitlements/drops', param, AuthType.EITHER, [], DropsEntitlement):
            yield y

    async def create_custom_reward(self,
                                   broadcaster_id: str,
                                   title: str,
                                   cost: int,
                                   prompt: Optional[str] = None,
                                   is_enabled: Optional[bool] = True,
                                   background_color: Optional[str] = None,
                                   is_user_input_required: Optional[bool] = False,
                                   is_max_per_stream_enabled: Optional[bool] = False,
                                   max_per_stream: Optional[int] = None,
                                   is_max_per_user_per_stream_enabled: Optional[bool] = False,
                                   max_per_user_per_stream: Optional[int] = None,
                                   is_global_cooldown_enabled: Optional[bool] = False,
                                   global_cooldown_seconds: Optional[int] = None,
                                   should_redemptions_skip_request_queue: Optional[bool] = False) -> CustomReward:
        """Creates a Custom Reward on a channel.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#create-custom-rewards

        :param broadcaster_id: ID of the broadcaster, must be same as user_id of auth token
        :param title: The title of the reward
        :param cost: The cost of the reward
        :param prompt: The prompt for the viewer when they are redeeming the reward |default| :code:`None`
        :param is_enabled: Is the reward currently enabled, if false the reward won’t show up to viewers. |default| :code:`True`
        :param background_color: Custom background color for the reward. Format: Hex with # prefix. Example: :code:`#00E5CB`. |default| :code:`None`
        :param is_user_input_required: Does the user need to enter information when redeeming the reward. |default| :code:`False`
        :param is_max_per_stream_enabled: Whether a maximum per stream is enabled. |default| :code:`False`
        :param max_per_stream: The maximum number per stream if enabled |default| :code:`None`
        :param is_max_per_user_per_stream_enabled: Whether a maximum per user per stream is enabled. |default| :code:`False`
        :param max_per_user_per_stream: The maximum number per user per stream if enabled |default| :code:`None`
        :param is_global_cooldown_enabled: Whether a cooldown is enabled. |default| :code:`False`
        :param global_cooldown_seconds: The cooldown in seconds if enabled |default| :code:`None`
        :param should_redemptions_skip_request_queue: Should redemptions be set to FULFILLED status immediately
                    when redeemed and skip the request queue instead of the normal UNFULFILLED status. |default| :code:`False`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ValueError: if is_global_cooldown_enabled is True but global_cooldown_seconds is not specified
        :raises ValueError: if is_max_per_stream_enabled is True but max_per_stream is not specified
        :raises ValueError: if is_max_per_user_per_stream_enabled is True but max_per_user_per_stream is not specified
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchAPIException: if Channel Points are not available for the broadcaster
        """

        if is_global_cooldown_enabled and global_cooldown_seconds is None:
            raise ValueError('please specify global_cooldown_seconds')
        if is_max_per_stream_enabled and max_per_stream is None:
            raise ValueError('please specify max_per_stream')
        if is_max_per_user_per_stream_enabled and max_per_user_per_stream is None:
            raise ValueError('please specify max_per_user_per_stream')

        param = {'broadcaster_id': broadcaster_id}
        body = {x: y for x, y in {
            'title': title,
            'prompt': prompt,
            'cost': cost,
            'is_enabled': is_enabled,
            'background_color': background_color,
            'is_user_input_required': is_user_input_required,
            'is_max_per_stream_enabled': is_max_per_stream_enabled,
            'max_per_stream': max_per_stream,
            'is_max_per_user_per_stream_enabled': is_max_per_user_per_stream_enabled,
            'max_per_user_per_stream': max_per_user_per_stream,
            'is_global_cooldown_enabled': is_global_cooldown_enabled,
            'global_cooldown_seconds': global_cooldown_seconds,
            'should_redemptions_skip_request_queue': should_redemptions_skip_request_queue
        }.items() if y is not None}
        error_handler = {403: TwitchAPIException('Forbidden: Channel Points are not available for the broadcaster')}
        return await self._build_result('POST', 'channel_points/custom_rewards', param, AuthType.USER, [AuthScope.CHANNEL_MANAGE_REDEMPTIONS],
                                        CustomReward, body_data=body, error_handler=error_handler)

    async def delete_custom_reward(self,
                                   broadcaster_id: str,
                                   reward_id: str):
        """Deletes a Custom Reward on a channel.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#delete-custom-rewards

        :param broadcaster_id: Provided broadcaster_id must match the user_id in the auth token
        :param reward_id: ID of the Custom Reward to delete, must match a Custom Reward on broadcaster_id’s channel.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the broadcaster has no custom reward with the given id
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the custom reward specified in reward_id was not found
        """

        await self._build_result('DELETE', 'channel_points/custom_rewards', {'broadcaster_id': broadcaster_id, 'id': reward_id}, AuthType.USER,
                                 [AuthScope.CHANNEL_MANAGE_REDEMPTIONS], None)

    async def get_custom_reward(self,
                                broadcaster_id: str,
                                reward_id: Optional[Union[str, List[str]]] = None,
                                only_manageable_rewards: Optional[bool] = False) -> List[CustomReward]:
        """Returns a list of Custom Reward objects for the Custom Rewards on a channel.
        Developers only have access to update and delete rewards that the same/calling client_id created.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-custom-reward

        :param broadcaster_id: Provided broadcaster_id must match the user_id in the auth token
        :param reward_id: When used, this parameter filters the results and only returns reward objects for the Custom Rewards with matching ID.
                Maximum: 50 |default| :code:`None`
        :param only_manageable_rewards: When set to true, only returns custom rewards that the calling client_id can manage. |default| :code:`False`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if app authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user or app authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchResourceNotFound: if all custom rewards specified in reward_id where not found
        :raises ValueError: if reward_id is longer than 50 entries
        """

        if reward_id is not None and isinstance(reward_id, list) and len(reward_id) > 50:
            raise ValueError('reward_id can not contain more than 50 entries')
        param = {
            'broadcaster_id': broadcaster_id,
            'id': reward_id,
            'only_manageable_rewards': only_manageable_rewards
        }
        return await self._build_result('GET', 'channel_points/custom_rewards', param, AuthType.USER, [AuthScope.CHANNEL_READ_REDEMPTIONS],
                                        List[CustomReward], split_lists=True)

    async def get_custom_reward_redemption(self,
                                           broadcaster_id: str,
                                           reward_id: str,
                                           redemption_id: Optional[List[str]] = None,
                                           status: Optional[CustomRewardRedemptionStatus] = None,
                                           sort: Optional[SortOrder] = SortOrder.OLDEST,
                                           after: Optional[str] = None,
                                           first: Optional[int] = 20) -> AsyncGenerator[CustomRewardRedemption, None]:
        """Returns Custom Reward Redemption objects for a Custom Reward on a channel that was created by the
        same client_id.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-custom-reward-redemption

        :param broadcaster_id: Provided broadcaster_id must match the user_id in the auth token
        :param reward_id: When ID is not provided, this parameter returns paginated Custom
                Reward Redemption objects for redemptions of the Custom Reward with ID reward_id
        :param redemption_id: When used, this param filters the results and only returns Custom Reward Redemption objects for the
                redemptions with matching ID. Maximum: 50 ids |default| :code:`None`
        :param status: When id is not provided, this param is required and filters the paginated Custom Reward Redemption objects
                for redemptions with the matching status. |default| :code:`None`
        :param sort: Sort order of redemptions returned when getting the paginated Custom Reward Redemption objects for a reward.
                |default| :code:`SortOrder.OLDEST`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 50 |default| :code:`20`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if app authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user or app authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchResourceNotFound: if all redemptions specified in redemption_id where not found
        :raises ValueError: if id has more than 50 entries
        :raises ValueError: if first is not in range 1 to 50
        :raises ValueError: if status and id are both :code:`None`
        """

        if first is not None and (first < 1 or first > 50):
            raise ValueError('first must be in range 1 to 50')
        if redemption_id is not None and len(redemption_id) > 50:
            raise ValueError('id can not have more than 50 entries')
        if status is None and redemption_id is None:
            raise ValueError('you have to set at least one of status or id')

        param = {
            'broadcaster_id': broadcaster_id,
            'reward_id': reward_id,
            'id': redemption_id,
            'status': status,
            'sort': sort,
            'after': after,
            'first': first
        }
        error_handler = {
            403: TwitchAPIException('The ID in the Client-Id header must match the client ID used to create the custom reward or '
                                    'the broadcaster is not a partner or affiliate')
        }
        async for y in self._build_generator('GET', 'channel_points/custom_rewards/redemptions', param, AuthType.USER,
                                             [AuthScope.CHANNEL_READ_REDEMPTIONS], CustomRewardRedemption, split_lists=True,
                                             error_handler=error_handler):
            yield y

    async def update_custom_reward(self,
                                   broadcaster_id: str,
                                   reward_id: str,
                                   title: Optional[str] = None,
                                   prompt: Optional[str] = None,
                                   cost: Optional[int] = None,
                                   is_enabled: Optional[bool] = True,
                                   background_color: Optional[str] = None,
                                   is_user_input_required: Optional[bool] = False,
                                   is_max_per_stream_enabled: Optional[bool] = False,
                                   max_per_stream: Optional[int] = None,
                                   is_max_per_user_per_stream_enabled: Optional[bool] = False,
                                   max_per_user_per_stream: Optional[int] = None,
                                   is_global_cooldown_enabled: Optional[bool] = False,
                                   global_cooldown_seconds: Optional[int] = None,
                                   is_paused: Optional[bool] = False,
                                   should_redemptions_skip_request_queue: Optional[bool] = False) -> CustomReward:
        """Updates a Custom Reward created on a channel.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#update-custom-reward

        :param broadcaster_id: ID of the broadcaster, must be same as user_id of auth token
        :param reward_id: ID of the reward that you want to update
        :param title: The title of the reward |default| :code:`None`
        :param prompt: The prompt for the viewer when they are redeeming the reward |default| :code:`None`
        :param cost: The cost of the reward |default| :code:`None`
        :param is_enabled: Is the reward currently enabled, if false the reward won’t show up to viewers. |default| :code:`True`
        :param background_color: Custom background color for the reward. |default| :code:`None` Format: Hex with # prefix. Example: :code:`#00E5CB`.
        :param is_user_input_required: Does the user need to enter information when redeeming the reward. |default| :code:`False`
        :param is_max_per_stream_enabled: Whether a maximum per stream is enabled. |default| :code:`False`
        :param max_per_stream: The maximum number per stream if enabled |default| :code:`None`
        :param is_max_per_user_per_stream_enabled: Whether a maximum per user per stream is enabled. |default| :code:`False`
        :param max_per_user_per_stream: The maximum number per user per stream if enabled |default| :code:`None`
        :param is_global_cooldown_enabled: Whether a cooldown is enabled. |default| :code:`False`
        :param global_cooldown_seconds: The cooldown in seconds if enabled |default| :code:`None`
        :param is_paused: Whether to pause the reward, if true viewers cannot redeem the reward. |default| :code:`False`
        :param should_redemptions_skip_request_queue: Should redemptions be set to FULFILLED status immediately
                    when redeemed and skip the request queue instead of the normal UNFULFILLED status. |default| :code:`False`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ValueError: if is_global_cooldown_enabled is True but global_cooldown_seconds is not specified
        :raises ValueError: if is_max_per_stream_enabled is True but max_per_stream is not specified
        :raises ValueError: if is_max_per_user_per_stream_enabled is True but max_per_user_per_stream is not specified
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchAPIException: if Channel Points are not available for the broadcaster or
                        the custom reward belongs to a different broadcaster
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the custom reward specified in reward_id was not found
        :raises ValueError: if the given reward_id does not match a custom reward by the given broadcaster
        """

        if is_global_cooldown_enabled and global_cooldown_seconds is None:
            raise ValueError('please specify global_cooldown_seconds')
        elif not is_global_cooldown_enabled and global_cooldown_seconds is None:
            is_global_cooldown_enabled = None
        if is_max_per_stream_enabled and max_per_stream is None:
            raise ValueError('please specify max_per_stream')
        elif not is_max_per_stream_enabled and max_per_stream is None:
            is_max_per_stream_enabled = None
        if is_max_per_user_per_stream_enabled and max_per_user_per_stream is None:
            raise ValueError('please specify max_per_user_per_stream')
        elif not is_max_per_user_per_stream_enabled and max_per_user_per_stream is None:
            is_max_per_user_per_stream_enabled = None

        param = {
            'broadcaster_id': broadcaster_id,
            'id': reward_id
        }
        body = {x: y for x, y in {
            'title': title,
            'prompt': prompt,
            'cost': cost,
            'is_enabled': is_enabled,
            'background_color': background_color,
            'is_user_input_required': is_user_input_required,
            'is_max_per_stream_enabled': is_max_per_stream_enabled,
            'max_per_stream': max_per_stream,
            'is_max_per_user_per_stream_enabled': is_max_per_user_per_stream_enabled,
            'max_per_user_per_stream': max_per_user_per_stream,
            'is_global_cooldown_enabled': is_global_cooldown_enabled,
            'global_cooldown_seconds': global_cooldown_seconds,
            'is_paused': is_paused,
            'should_redemptions_skip_request_queue': should_redemptions_skip_request_queue
        }.items() if y is not None}
        error_handler = {
            403: TwitchAPIException('This custom reward was created by a different broadcaster or channel points are'
                                    'not available for the broadcaster')
        }

        return await self._build_result('PATCH', 'channel_points/custom_rewards', param, AuthType.USER, [AuthScope.CHANNEL_MANAGE_REDEMPTIONS],
                                        CustomReward, body_data=body, error_handler=error_handler)

    async def update_redemption_status(self,
                                       broadcaster_id: str,
                                       reward_id: str,
                                       redemption_ids: Union[List[str], str],
                                       status: CustomRewardRedemptionStatus) -> CustomRewardRedemption:
        """Updates the status of Custom Reward Redemption objects on a channel that are in the :code:`UNFULFILLED` status.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#update-redemption-status

        :param broadcaster_id: Provided broadcaster_id must match the user_id in the auth token.
        :param reward_id: ID of the Custom Reward the redemptions to be updated are for.
        :param redemption_ids: IDs of the Custom Reward Redemption to update, must match a
                    Custom Reward Redemption on broadcaster_id’s channel Max: 50
        :param status: The new status to set redemptions to.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchAPIException: if Channel Points are not available for the broadcaster or
                        the custom reward belongs to a different broadcaster
        :raises ValueError: if redemption_ids is longer than 50 entries
        :raises ~twitchAPI.type.TwitchResourceNotFound: if no custom reward redemptions with status UNFULFILLED where found for the given ids
        :raises ~twitchAPI.type.TwitchAPIException: if Channel Points are not available for the broadcaster or
                        the custom reward belongs to a different broadcaster
        """
        if isinstance(redemption_ids, list) and len(redemption_ids) > 50:
            raise ValueError("redemption_ids can't have more than 50 entries")

        param = {
            'id': redemption_ids,
            'broadcaster_id': broadcaster_id,
            'reward_id': reward_id
        }
        body = {'status': status.value}
        error_handler = {
            403: TwitchAPIException('This custom reward was created by a different broadcaster or channel points are '
                                    'not available for the broadcaster')
        }
        return await self._build_result('PATCH', 'channel_points/custom_rewards/redemptions', param, AuthType.USER,
                                        [AuthScope.CHANNEL_MANAGE_REDEMPTIONS], CustomRewardRedemption, body_data=body, split_lists=True,
                                        error_handler=error_handler)

    async def get_channel_editors(self,
                                  broadcaster_id: str) -> List[ChannelEditor]:
        """Gets a list of users who have editor permissions for a specific channel.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_EDITORS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-channel-editors

        :param broadcaster_id: Broadcaster’s user ID associated with the channel
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        return await self._build_result('GET', 'channel/editors', {'broadcaster_id': broadcaster_id}, AuthType.USER, [AuthScope.CHANNEL_READ_EDITORS],
                                        List[ChannelEditor])

    async def delete_videos(self,
                            video_ids: List[str]) -> List[str]:
        """Deletes one or more videos. Videos are past broadcasts, Highlights, or uploads.
        Returns False if the User was not Authorized to delete at least one of the given videos.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_VIDEOS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#delete-videos

        :param video_ids: ids of the videos, Limit: 5 ids
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if video_ids contains more than 5 entries or is a empty list
        """
        if video_ids is None or len(video_ids) == 0 or len(video_ids) > 5:
            raise ValueError('video_ids must contain between 1 and 5 entries')
        return await self._build_result('DELETE', 'videos', {'id': video_ids}, AuthType.USER, [AuthScope.CHANNEL_MANAGE_VIDEOS], List[str],
                                        split_lists=True)

    async def get_user_block_list(self,
                                  broadcaster_id: str,
                                  first: Optional[int] = 20,
                                  after: Optional[str] = None) -> AsyncGenerator[BlockListEntry, None]:
        """Gets a specified user’s block list. The list is sorted by when the block occurred in descending order
        (i.e. most recent block first).

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.USER_READ_BLOCKED_USERS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-user-block-list

        :param broadcaster_id: User ID for a twitch user
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`20`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if first is not in range 1 to 100
        """

        if first < 1 or first > 100:
            raise ValueError('first must be in range 1 to 100')
        param = {
            'broadcaster_id': broadcaster_id,
            'first': first,
            'after': after}
        async for y in self._build_generator('GET', 'users/blocks', param, AuthType.USER, [AuthScope.USER_READ_BLOCKED_USERS], BlockListEntry):
            yield y

    async def block_user(self,
                         target_user_id: str,
                         source_context: Optional[BlockSourceContext] = None,
                         reason: Optional[BlockReason] = None) -> bool:
        """Blocks the specified user on behalf of the authenticated user.

         Requires User Authentication with :const:`~twitchAPI.type.AuthScope.USER_MANAGE_BLOCKED_USERS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#block-user

        :param target_user_id: User ID of the user to be blocked.
        :param source_context: Source context for blocking the user. |default| :code:`None`
        :param reason: Reason for blocking the user. |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid
                        and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        param = {
            'target_user_id': target_user_id,
            'source_context': enum_value_or_none(source_context),
            'reason': enum_value_or_none(reason)}
        return await self._build_result('PUT', 'users/blocks', param, AuthType.USER, [AuthScope.USER_MANAGE_BLOCKED_USERS], None,
                                        result_type=ResultType.STATUS_CODE) == 204

    async def unblock_user(self,
                           target_user_id: str) -> bool:
        """Unblocks the specified user on behalf of the authenticated user.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.USER_MANAGE_BLOCKED_USERS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#unblock-user

        :param target_user_id: User ID of the user to be unblocked.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        return await self._build_result('DELETE', 'users/blocks', {'target_user_id': target_user_id}, AuthType.USER,
                                        [AuthScope.USER_MANAGE_BLOCKED_USERS], None, result_type=ResultType.STATUS_CODE) == 204

    async def get_followed_streams(self,
                                   user_id: str,
                                   after: Optional[str] = None,
                                   first: Optional[int] = 100) -> AsyncGenerator[Stream, None]:
        """Gets information about active streams belonging to channels that the authenticated user follows.
        Streams are returned sorted by number of current viewers, in descending order.
        Across multiple pages of results, there may be duplicate or missing streams, as viewers join and leave streams.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.USER_READ_FOLLOWS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-followed-streams

        :param user_id: Results will only include active streams from the channels that this Twitch user follows.
                user_id must match the User ID in the bearer token.
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default| :code:`100`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if first is not in range 1 to 100
        """
        if first < 1 or first > 100:
            raise ValueError('first must be in range 1 to 100')
        param = {
            'user_id': user_id,
            'after': after,
            'first': first
        }
        async for y in self._build_generator('GET', 'streams/followed', param, AuthType.USER, [AuthScope.USER_READ_FOLLOWS], Stream):
            yield y

    async def get_polls(self,
                        broadcaster_id: str,
                        poll_id: Union[None, str, List[str]] = None,
                        after: Optional[str] = None,
                        first: Optional[int] = 20) -> AsyncGenerator[Poll, None]:
        """Get information about all polls or specific polls for a Twitch channel. Poll information is available for 90 days.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_POLLS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-polls

        :param broadcaster_id: The broadcaster running polls.
                Provided broadcaster_id must match the user_id in the user OAuth token.
        :param poll_id: ID(s) of a poll. You can specify up to 20 poll ids |default| :code:`None`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 20 |default| :code:`20`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchResourceNotFound: if none of the IDs in poll_id where found
        :raises ValueError: if first is not in range 1 to 20
        :raises ValueError: if poll_id has more than 20 entries
        """
        if poll_id is not None and isinstance(poll_id, List) and len(poll_id) > 20:
            raise ValueError('You may only specify up to 20 poll IDs')
        if first is not None and (first < 1 or first > 20):
            raise ValueError('first must be in range 1 to 20')
        param = {
            'broadcaster_id': broadcaster_id,
            'id': poll_id,
            'after': after,
            'first': first
        }
        async for y in self._build_generator('GET', 'polls', param, AuthType.USER, [AuthScope.CHANNEL_READ_POLLS], Poll, split_lists=True):
            yield y

    async def create_poll(self,
                          broadcaster_id: str,
                          title: str,
                          choices: List[str],
                          duration: int,
                          channel_points_voting_enabled: bool = False,
                          channel_points_per_vote: Optional[int] = None) -> Poll:
        """Create a poll for a specific Twitch channel.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_POLLS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#create-poll

        :param broadcaster_id: The broadcaster running the poll
        :param title: Question displayed for the poll
        :param choices: List of poll choices.
        :param duration: Total duration for the poll (in seconds). Minimum 15, Maximum 1800
        :param channel_points_voting_enabled: Indicates if Channel Points can be used for voting. |default| :code:`False`
        :param channel_points_per_vote: Number of Channel Points required to vote once with Channel Points.
            Minimum: 0. Maximum: 1000000. |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if duration is not in range 15 to 1800
        :raises ValueError: if channel_points_per_vote is not in range 0 to 1000000
        """
        if duration < 15 or duration > 1800:
            raise ValueError('duration must be between 15 and 1800')
        if channel_points_per_vote is not None:
            if channel_points_per_vote < 0 or channel_points_per_vote > 1_000_000:
                raise ValueError('channel_points_per_vote must be in range 0 to 1000000')
        if len(choices) < 0 or len(choices) > 5:
            raise ValueError('require between 2 and 5 choices')
        body = {k: v for k, v in {
            'broadcaster_id': broadcaster_id,
            'title': title,
            'choices': [{'title': x} for x in choices],
            'duration': duration,
            'channel_points_voting_enabled': channel_points_voting_enabled,
            'channel_points_per_vote': channel_points_per_vote
        }.items() if v is not None}
        return await self._build_result('POST', 'polls', {}, AuthType.USER, [AuthScope.CHANNEL_MANAGE_POLLS], Poll, body_data=body)

    async def end_poll(self,
                       broadcaster_id: str,
                       poll_id: str,
                       status: PollStatus) -> Poll:
        """End a poll that is currently active.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_POLLS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#end-poll

        :param broadcaster_id: id of the broadcaster running the poll
        :param poll_id: id of the poll
        :param status: The poll status to be set
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if status is not TERMINATED or ARCHIVED
        """
        if status not in (PollStatus.TERMINATED, PollStatus.ARCHIVED):
            raise ValueError('status must be either TERMINATED or ARCHIVED')
        body = {
            'broadcaster_id': broadcaster_id,
            'id': poll_id,
            'status': status.value
        }
        return await self._build_result('PATCH', 'polls', {}, AuthType.USER, [AuthScope.CHANNEL_MANAGE_POLLS], Poll, body_data=body)

    async def get_predictions(self,
                              broadcaster_id: str,
                              prediction_ids: Optional[List[str]] = None,
                              after: Optional[str] = None,
                              first: Optional[int] = 20) -> AsyncGenerator[Prediction, None]:
        """Get information about all Channel Points Predictions or specific Channel Points Predictions for a Twitch channel.
        Results are ordered by most recent, so it can be assumed that the currently active or locked Prediction will be the first item.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_PREDICTIONS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-predictions

        :param broadcaster_id: The broadcaster running the prediction
        :param prediction_ids: List of prediction ids. |default| :code:`None`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 20 |default| :code:`20`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if first is not in range 1 to 20
        :raises ValueError: if prediction_ids contains more than 100 entries
        """
        if first is not None and (first < 1 or first > 20):
            raise ValueError('first must be in range 1 to 20')
        if prediction_ids is not None and len(prediction_ids) > 100:
            raise ValueError('maximum of 100 prediction ids allowed')

        param = {
            'broadcaster_id': broadcaster_id,
            'id': prediction_ids,
            'after': after,
            'first': first
        }
        async for y in self._build_generator('GET', 'predictions', param, AuthType.USER, [AuthScope.CHANNEL_READ_PREDICTIONS], Prediction,
                                             split_lists=True):
            yield y

    async def create_prediction(self,
                                broadcaster_id: str,
                                title: str,
                                outcomes: List[str],
                                prediction_window: int) -> Prediction:
        """Create a Channel Points Prediction for a specific Twitch channel.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_PREDICTIONS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#create-prediction

        :param broadcaster_id: The broadcaster running the prediction
        :param title: Title of the Prediction
        :param outcomes: List of possible Outcomes, must contain between 2 and 10 entries
        :param prediction_window: Total duration for the Prediction (in seconds). Minimum 1, Maximum 1800
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if prediction_window is not in range 1 to 1800
        :raises ValueError: if outcomes does not contain exactly 2 entries
        """
        if prediction_window < 1 or prediction_window > 1800:
            raise ValueError('prediction_window must be in range 1 to 1800')
        if len(outcomes) < 2 or len(outcomes) > 10:
            raise ValueError('outcomes must have between 2 entries and 10 entries')
        body = {
            'broadcaster_id': broadcaster_id,
            'title': title,
            'outcomes': [{'title': x} for x in outcomes],
            'prediction_window': prediction_window
        }
        return await self._build_result('POST', 'predictions', {}, AuthType.USER, [AuthScope.CHANNEL_MANAGE_PREDICTIONS], Prediction, body_data=body)

    async def end_prediction(self,
                             broadcaster_id: str,
                             prediction_id: str,
                             status: PredictionStatus,
                             winning_outcome_id: Optional[str] = None) -> Prediction:
        """Lock, resolve, or cancel a Channel Points Prediction.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_PREDICTIONS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#end-prediction

        :param broadcaster_id: ID of the broadcaster
        :param prediction_id: ID of the Prediction
        :param status: The Prediction status to be set.
        :param winning_outcome_id: ID of the winning outcome for the Prediction. |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if winning_outcome_id is None and status is RESOLVED
        :raises ValueError: if status is not one of RESOLVED, CANCELED or LOCKED
        :raises ~twitchAPI.type.TwitchResourceNotFound: if prediction_id or winning_outcome_id where not found
        """
        if status not in (PredictionStatus.RESOLVED, PredictionStatus.CANCELED, PredictionStatus.LOCKED):
            raise ValueError('status has to be one of RESOLVED, CANCELED or LOCKED')
        if status == PredictionStatus.RESOLVED and winning_outcome_id is None:
            raise ValueError('need to specify winning_outcome_id for status RESOLVED')
        body = {
            'broadcaster_id': broadcaster_id,
            'id': prediction_id,
            'status': status.value
        }
        if winning_outcome_id is not None:
            body['winning_outcome_id'] = winning_outcome_id
        return await self._build_result('PATCH', 'predictions', {}, AuthType.USER, [AuthScope.CHANNEL_MANAGE_PREDICTIONS], Prediction, body_data=body)

    async def start_raid(self,
                         from_broadcaster_id: str,
                         to_broadcaster_id: str) -> RaidStartResult:
        """ Raid another channel by sending the broadcaster’s viewers to the targeted channel.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_RAIDS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#start-a-raid

        :param from_broadcaster_id: The ID of the broadcaster that's sending the raiding party.
        :param to_broadcaster_id: The ID of the broadcaster to raid.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the target channel was not found
        """
        param = {
            'from_broadcaster_id': from_broadcaster_id,
            'to_broadcaster_id': to_broadcaster_id
        }
        return await self._build_result('POST', 'raids', param, AuthType.USER, [AuthScope.CHANNEL_MANAGE_RAIDS], RaidStartResult)

    async def cancel_raid(self,
                          broadcaster_id: str):
        """Cancel a pending raid.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_RAIDS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#cancel-a-raid

        :param broadcaster_id: The ID of the broadcaster that sent the raiding party.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the broadcaster does not have a pending raid to cancel
        """
        await self._build_result('DELETE', 'raids', {'broadcaster_id': broadcaster_id}, AuthType.USER, [AuthScope.CHANNEL_MANAGE_RAIDS], None)

    async def manage_held_automod_message(self,
                                          user_id: str,
                                          msg_id: str,
                                          action: AutoModAction):
        """Allow or deny a message that was held for review by AutoMod.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_AUTOMOD`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#manage-held-automod-messages

        :param user_id: The moderator who is approving or rejecting the held message.
        :param msg_id: ID of the targeted message
        :param action: The action to take for the message.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the message specified in msg_id was not found
        """
        body = {
            'user_id': user_id,
            'msg_id': msg_id,
            'action': action.value
        }
        await self._build_result('POST', 'moderation/automod/message', {}, AuthType.USER, [AuthScope.MODERATOR_MANAGE_AUTOMOD], None, body_data=body)

    async def get_chat_badges(self, broadcaster_id: str) -> List[ChatBadge]:
        """Gets a list of custom chat badges that can be used in chat for the specified channel.

        Requires User or App Authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-channel-chat-badges

        :param broadcaster_id: The ID of the broadcaster whose chat badges you want to get.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        return await self._build_result('GET', 'chat/badges', {'broadcaster_id': broadcaster_id}, AuthType.EITHER, [], List[ChatBadge])

    async def get_global_chat_badges(self) -> List[ChatBadge]:
        """Gets a list of chat badges that can be used in chat for any channel.

        Requires User or App Authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-global-chat-badges

        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        return await self._build_result('GET', 'chat/badges/global', {}, AuthType.EITHER, [], List[ChatBadge])

    async def get_channel_emotes(self, broadcaster_id: str) -> GetEmotesResponse:
        """Gets all emotes that the specified Twitch channel created.

        Requires User or App Authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-channel-emotes

        :param broadcaster_id: ID of the broadcaster
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        return await self._build_result('GET', 'chat/emotes', {'broadcaster_id': broadcaster_id}, AuthType.EITHER, [], GetEmotesResponse,
                                        get_from_data=False)

    async def get_global_emotes(self) -> GetEmotesResponse:
        """Gets all global emotes.

        Requires User or App Authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-global-emotes

        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        return await self._build_result('GET', 'chat/emotes/global', {}, AuthType.EITHER, [], GetEmotesResponse, get_from_data=False)

    async def get_emote_sets(self, emote_set_id: List[str]) -> GetEmotesResponse:
        """Gets emotes for one or more specified emote sets.

        Requires User or App Authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-emote-sets

        :param emote_set_id: A list of IDs that identify the emote sets.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        if len(emote_set_id) == 0 or len(emote_set_id) > 25:
            raise ValueError('you need to specify between 1 and 25 emote_set_ids')
        return await self._build_result('GET', 'chat/emotes/set', {'emote_set_id': emote_set_id}, AuthType.EITHER, [], GetEmotesResponse,
                                        split_lists=True)

    async def create_eventsub_subscription(self,
                                           subscription_type: str,
                                           version: str,
                                           condition: dict,
                                           transport: dict):
        """Creates an EventSub subscription.

        Requires Authentication and Scopes depending on Subscription & Transport used.\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#create-eventsub-subscription

        :param subscription_type: The type of subscription to create. For a list of subscriptions that you can create, see [!Subscription Types](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#subscription-types).
                Set this field to the value in the Name column of the Subscription Types table.
        :param version: The version number that identifies the definition of the subscription type that you want the response to use.
        :param condition: A dict that contains the parameter values that are specific to the specified subscription type.
                For the object’s required and optional fields, see the subscription type’s documentation.
        :param transport: The transport details that you want Twitch to use when sending you notifications.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the subscription was not found
        """
        data = {
            'type': subscription_type,
            'version': version,
            'condition': condition,
            'transport': transport
        }
        await self._build_iter_result('POST',
                                      'eventsub/subscriptions', {},
                                      AuthType.USER if transport['method'] == 'websocket' else AuthType.APP, [],
                                      GetEventSubSubscriptionResult, body_data=data)

    async def delete_eventsub_subscription(self, subscription_id: str):
        """Deletes an EventSub subscription.

        Requires App Authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#delete-eventsub-subscription

        :param subscription_id: The ID of the subscription
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the subscription was not found
        """
        await self._build_result('DELETE', 'eventsub/subscriptions', {'id': subscription_id}, AuthType.APP, [], None)

    async def get_eventsub_subscriptions(self,
                                         status: Optional[str] = None,
                                         sub_type: Optional[str] = None,
                                         user_id: Optional[str] = None,
                                         after: Optional[str] = None) -> GetEventSubSubscriptionResult:
        """Gets a list of your EventSub subscriptions.
        The list is paginated and ordered by the oldest subscription first.

        Requires App Authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-eventsub-subscriptions

        :param status: Filter subscriptions by its status. |default| :code:`None`
        :param sub_type: Filter subscriptions by subscription type. |default| :code:`None`
        :param user_id: Filter subscriptions by user ID. |default| :code:`None`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        param = {
            'status': status,
            'type': sub_type,
            'user_id': user_id,
            'after': after
        }
        return await self._build_iter_result('GET', 'eventsub/subscriptions', param, AuthType.APP, [], GetEventSubSubscriptionResult)

    async def get_channel_stream_schedule(self,
                                          broadcaster_id: str,
                                          stream_segment_ids: Optional[List[str]] = None,
                                          start_time: Optional[datetime] = None,
                                          utc_offset: Optional[str] = None,
                                          first: Optional[int] = 20,
                                          after: Optional[str] = None) -> ChannelStreamSchedule:
        """Gets all scheduled broadcasts or specific scheduled broadcasts from a channel’s stream schedule.

        Requires App or User Authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-channel-stream-schedule

        :param broadcaster_id: user id of the broadcaster
        :param stream_segment_ids: optional list of stream segment ids. Maximum 100 entries. |default| :code:`None`
        :param start_time: optional timestamp to start returning stream segments from. |default| :code:`None`
        :param utc_offset: A timezone offset to be used. |default| :code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 25 |default| :code:`20`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the broadcaster has not created a streaming schedule
        :raises ValueError: if stream_segment_ids has more than 100 entries
        :raises ValueError: if first is not in range 1 to 25
        """
        if stream_segment_ids is not None and len(stream_segment_ids) > 100:
            raise ValueError('stream_segment_ids can only have 100 entries')
        if first is not None and (first > 25 or first < 1):
            raise ValueError('first has to be in range 1 to 25')
        param = {
            'broadcaster_id': broadcaster_id,
            'id': stream_segment_ids,
            'start_time': datetime_to_str(start_time),
            'utc_offset': utc_offset,
            'first': first,
            'after': after
        }
        return await self._build_iter_result('GET', 'schedule', param, AuthType.EITHER, [], ChannelStreamSchedule, split_lists=True,
                                             in_data=True, iter_field='segments')

    async def get_channel_icalendar(self, broadcaster_id: str) -> str:
        """Gets all scheduled broadcasts from a channel’s stream schedule as an iCalendar.

        Does not require Authorization\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-channel-icalendar

        :param broadcaster_id: id of the broadcaster
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        return await self._build_result('GET', 'schedule/icalendar', {'broadcaster_id': broadcaster_id}, AuthType.NONE, [], None,
                                        result_type=ResultType.TEXT)

    async def update_channel_stream_schedule(self,
                                             broadcaster_id: str,
                                             is_vacation_enabled: Optional[bool] = None,
                                             vacation_start_time: Optional[datetime] = None,
                                             vacation_end_time: Optional[datetime] = None,
                                             timezone: Optional[str] = None):
        """Update the settings for a channel’s stream schedule. This can be used for setting vacation details.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_SCHEDULE`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#update-channel-stream-schedule

        :param broadcaster_id: id of the broadcaster
        :param is_vacation_enabled: indicates if Vacation Mode is enabled. |default| :code:`None`
        :param vacation_start_time: Start time for vacation |default| :code:`None`
        :param vacation_end_time: End time for vacation specified |default| :code:`None`
        :param timezone: The timezone for when the vacation is being scheduled using the IANA time zone database format.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the broadcasters schedule was not found
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'is_vacation_enabled': is_vacation_enabled,
            'vacation_start_time': datetime_to_str(vacation_start_time),
            'vacation_end_time': datetime_to_str(vacation_end_time),
            'timezone': timezone
        }
        await self._build_result('PATCH', 'schedule/settings', param, AuthType.USER, [AuthScope.CHANNEL_MANAGE_SCHEDULE], None)

    async def create_channel_stream_schedule_segment(self,
                                                     broadcaster_id: str,
                                                     start_time: datetime,
                                                     timezone: str,
                                                     is_recurring: bool,
                                                     duration: Optional[str] = None,
                                                     category_id: Optional[str] = None,
                                                     title: Optional[str] = None) -> ChannelStreamSchedule:
        """Create a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_SCHEDULE`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#create-channel-stream-schedule-segment

        :param broadcaster_id: id of the broadcaster
        :param start_time: Start time for the scheduled broadcast
        :param timezone: The timezone of the application creating the scheduled broadcast using the IANA time zone database format.
        :param is_recurring: Indicates if the scheduled broadcast is recurring weekly.
        :param duration: Duration of the scheduled broadcast in minutes from the start_time. |default| :code:`240`
        :param category_id: Game/Category ID for the scheduled broadcast. |default| :code:`None`
        :param title: Title for the scheduled broadcast. |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        param = {'broadcaster_id': broadcaster_id}
        body = remove_none_values({
            'start_time': datetime_to_str(start_time),
            'timezone': timezone,
            'is_recurring': is_recurring,
            'duration': duration,
            'category_id': category_id,
            'title': title
        })
        return await self._build_iter_result('POST', 'schedule/segment', param, AuthType.USER, [AuthScope.CHANNEL_MANAGE_SCHEDULE],
                                             ChannelStreamSchedule, body_data=body, in_data=True, iter_field='segments')

    async def update_channel_stream_schedule_segment(self,
                                                     broadcaster_id: str,
                                                     stream_segment_id: str,
                                                     start_time: Optional[datetime] = None,
                                                     duration: Optional[str] = None,
                                                     category_id: Optional[str] = None,
                                                     title: Optional[str] = None,
                                                     is_canceled: Optional[bool] = None,
                                                     timezone: Optional[str] = None) -> ChannelStreamSchedule:
        """Update a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_SCHEDULE`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#update-channel-stream-schedule-segment

        :param broadcaster_id: id of the broadcaster
        :param stream_segment_id: The ID of the streaming segment to update.
        :param start_time: Start time for the scheduled broadcast |default| :code:`None`
        :param duration: Duration of the scheduled broadcast in minutes from the start_time. |default| :code:`240`
        :param category_id: Game/Category ID for the scheduled broadcast. |default| :code:`None`
        :param title: Title for the scheduled broadcast. |default| :code:`None`
        :param is_canceled: Indicated if the scheduled broadcast is canceled. |default| :code:`None`
        :param timezone: The timezone of the application creating the scheduled broadcast using the IANA time zone database format.
                    |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the specified broadcast segment was not found
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'id': stream_segment_id
        }
        body = remove_none_values({
            'start_time': datetime_to_str(start_time),
            'duration': duration,
            'category_id': category_id,
            'title': title,
            'is_canceled': is_canceled,
            'timezone': timezone
        })
        return await self._build_iter_result('PATCH', 'schedule/segment', param, AuthType.USER, [AuthScope.CHANNEL_MANAGE_SCHEDULE],
                                             ChannelStreamSchedule, body_data=body, in_data=True, iter_field='segments')

    async def delete_channel_stream_schedule_segment(self,
                                                     broadcaster_id: str,
                                                     stream_segment_id: str):
        """Delete a single scheduled broadcast or a recurring scheduled broadcast for a channel’s stream schedule.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_SCHEDULE`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#delete-channel-stream-schedule-segment

        :param broadcaster_id: id of the broadcaster
        :param stream_segment_id: The ID of the streaming segment to delete.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'id': stream_segment_id
        }
        await self._build_result('DELETE', 'schedule/segment', param, AuthType.USER, [AuthScope.CHANNEL_MANAGE_SCHEDULE],
                                 None)

    async def update_drops_entitlements(self,
                                        entitlement_ids: List[str],
                                        fulfillment_status: EntitlementFulfillmentStatus) -> List[DropsEntitlement]:
        """Updates the fulfillment status on a set of Drops entitlements, specified by their entitlement IDs.

        Requires User or App Authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#update-drops-entitlements

        :param entitlement_ids: An array of unique identifiers of the entitlements to update.
        :param fulfillment_status: A fulfillment status.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if entitlement_ids has more than 100 entries
        """
        if len(entitlement_ids) > 100:
            raise ValueError('entitlement_ids can only have a maximum of 100 entries')
        body = remove_none_values({
            'entitlement_ids': entitlement_ids,
            'fulfillment_status': fulfillment_status.value
        })
        return await self._build_result('PATCH', 'entitlements/drops', {}, AuthType.EITHER, [], List[DropsEntitlement], body_data=body)

    async def send_whisper(self,
                           from_user_id: str,
                           to_user_id: str,
                           message: str):
        """Sends a whisper message to the specified user.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.USER_MANAGE_WHISPERS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#send-whisper

        :param from_user_id: The ID of the user sending the whisper.
        :param to_user_id: The ID of the user to receive the whisper.
        :param message: The whisper message to send.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the user specified in to_user_id was not found
        :raises ValueError: if message is empty
        """
        if len(message) == 0:
            raise ValueError('message can\'t be empty')
        param = {
            'from_user_id': from_user_id,
            'to_user_id': to_user_id
        }
        body = {'message': message}
        await self._build_result('POST', 'whispers', param, AuthType.USER, [AuthScope.USER_MANAGE_WHISPERS], None, body_data=body)

    async def remove_channel_vip(self,
                                 broadcaster_id: str,
                                 user_id: str) -> bool:
        """Removes a VIP from the broadcaster’s chat room.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_VIPS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#remove-channel-vip

        :param broadcaster_id: The ID of the broadcaster that’s removing VIP status from the user.
        :param user_id: The ID of the user to remove as a VIP from the broadcaster’s chat room.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the moderator_id or user_id where not found
        :returns: True if channel vip was removed, False if user was not a channel vip
        """
        param = {
            'user_id': user_id,
            'broadcaster_id': broadcaster_id
        }
        return await self._build_result('DELETE', 'channels/vips', param, AuthType.USER, [AuthScope.CHANNEL_MANAGE_VIPS], None,
                                        result_type=ResultType.STATUS_CODE) == 204

    async def add_channel_vip(self,
                              broadcaster_id: str,
                              user_id: str) -> bool:
        """Adds a VIP to the broadcaster’s chat room.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_VIPS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#add-channel-vip

        :param broadcaster_id: The ID of the broadcaster that’s granting VIP status to the user.
        :param user_id: The ID of the user to add as a VIP in the broadcaster’s chat room.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if broadcaster does not have available VIP slots or has not completed the "Build a Community" requirements
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the broadcaster_id or user_id where not found
        :returns: True if user was added as vip, False when user was already vip or is moderator
        """
        param = {
            'user_id': user_id,
            'broadcaster_id': broadcaster_id
        }
        error_handler = {
            409: ValueError('Broadcaster does not have available VIP slots'),
            425: ValueError('The broadcaster did not complete the "Build a Community" requirements')
        }
        return await self._build_result('POST', 'channels/vips', param, AuthType.USER, [AuthScope.CHANNEL_MANAGE_VIPS], None,
                                        result_type=ResultType.STATUS_CODE, error_handler=error_handler) == 204

    async def get_vips(self,
                       broadcaster_id: str,
                       user_ids: Optional[Union[str, List[str]]] = None,
                       first: Optional[int] = None,
                       after: Optional[str] = None) -> AsyncGenerator[ChannelVIP, None]:
        """Gets a list of the channel’s VIPs.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_VIPS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-vips

        :param broadcaster_id: The ID of the broadcaster whose list of VIPs you want to get.
        :param user_ids: Filters the list for specific VIPs. Maximum 100 |default|:code:`None`
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default|:code:`None`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if you specify more than 100 user ids
        """
        if user_ids is not None and isinstance(user_ids, list) and len(user_ids) > 100:
            raise ValueError('you can only specify up to 100 user ids')
        param = {
            'broadcaster_id': broadcaster_id,
            'user_id': user_ids,
            'first': first,
            'after': after
        }
        async for y in self._build_generator('GET', 'channels/vips', param, AuthType.USER, [AuthScope.CHANNEL_READ_VIPS], ChannelVIP,
                                             split_lists=True):
            yield y

    async def add_channel_moderator(self,
                                    broadcaster_id: str,
                                    user_id: str):
        """Adds a moderator to the broadcaster’s chat room.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_MODERATORS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#add-channel-moderator

        :param broadcaster_id: The ID of the broadcaster that owns the chat room.
        :param user_id: The ID of the user to add as a moderator in the broadcaster’s chat room.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: If user is a vip
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'user_id': user_id
        }
        error_handler = {422: ValueError('User is a vip')}
        await self._build_result('POST', 'moderation/moderators', param, AuthType.USER, [AuthScope.CHANNEL_MANAGE_MODERATORS], None,
                                 error_handler=error_handler)

    async def remove_channel_moderator(self,
                                       broadcaster_id: str,
                                       user_id: str):
        """Removes a moderator from the broadcaster’s chat room.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_MODERATORS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#remove-channel-moderator

        :param broadcaster_id: The ID of the broadcaster that owns the chat room.
        :param user_id: The ID of the user to remove as a moderator from the broadcaster’s chat room.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'user_id': user_id
        }
        await self._build_result('DELETE', 'moderation/moderators', param, AuthType.USER, [AuthScope.CHANNEL_MANAGE_MODERATORS], None)

    async def get_user_chat_color(self,
                                  user_ids: Union[str, List[str]]) -> List[UserChatColor]:
        """Gets the color used for the user’s name in chat.

        Requires User or App Authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-user-chat-color

        :param user_ids: The ID of the user whose color you want to get.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if you specify more than 100 user ids
        :return: A list of user chat Colors
        """
        if isinstance(user_ids, list) and len(user_ids) > 100:
            raise ValueError('you can only request up to 100 users at the same time')
        return await self._build_result('GET', 'chat/color', {'user_id': user_ids}, AuthType.EITHER, [], List[UserChatColor], split_lists=True)

    async def update_user_chat_color(self,
                                     user_id: str,
                                     color: str):
        """Updates the color used for the user’s name in chat.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.USER_MANAGE_CHAT_COLOR`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#update-user-chat-color

        :param user_id: The ID of the user whose chat color you want to update.
        :param color: The color to use for the user’s name in chat. See twitch Docs for valid values.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        param = {
            'user_id': user_id,
            'color': color
        }
        await self._build_result('PUT', 'chat/color', param, AuthType.USER, [AuthScope.USER_MANAGE_CHAT_COLOR], None)

    async def delete_chat_message(self,
                                  broadcaster_id: str,
                                  moderator_id: str,
                                  message_id: Optional[str] = None):
        """Removes a single chat message or all chat messages from the broadcaster’s chat room.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_CHAT_MESSAGES`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#delete-chat-messages

        :param broadcaster_id: The ID of the broadcaster that owns the chat room to remove messages from.
        :param moderator_id: The ID of a user that has permission to moderate the broadcaster’s chat room.
        :param message_id: The ID of the message to remove. If None, removes all messages from the broadcasters chat. |default|:code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.ForbiddenError: if moderator_id is not a moderator of broadcaster_id
        :raises ~twitchAPI.type.TwitchResourceNotFound: if the message_id was not found or the message was created more than 6 hours ago
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'moderator_id': moderator_id,
            'message_id': message_id
        }
        error = {403: ForbiddenError('moderator_id is not a moderator of broadcaster_id')}
        await self._build_result('DELETE', 'moderation/chat', param, AuthType.USER, [AuthScope.MODERATOR_MANAGE_CHAT_MESSAGES], None,
                                 error_handler=error)

    async def send_chat_announcement(self,
                                     broadcaster_id: str,
                                     moderator_id: str,
                                     message: str,
                                     color: Optional[str] = None):
        """Sends an announcement to the broadcaster’s chat room.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_ANNOUNCEMENTS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#send-chat-announcement

        :param broadcaster_id: The ID of the broadcaster that owns the chat room to send the announcement to.
        :param moderator_id: The ID of a user who has permission to moderate the broadcaster’s chat room.
        :param message: The announcement to make in the broadcaster’s chat room.
        :param color: The color used to highlight the announcement. See twitch Docs for valid values. |default|:code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.ForbiddenError: if moderator_id is not a moderator of broadcaster_id
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'moderator_id': moderator_id
        }
        body = remove_none_values({
            'message': message,
            'color': color
        })
        error = {403: ForbiddenError('moderator_id is not a moderator of broadcaster_id')}
        await self._build_result('POST', 'chat/announcements', param, AuthType.USER, [AuthScope.MODERATOR_MANAGE_ANNOUNCEMENTS], None,
                                 body_data=body, error_handler=error)

    async def send_a_shoutout(self,
                              from_broadcaster_id: str,
                              to_broadcaster_id: str,
                              moderator_id: str) -> None:
        """Sends a Shoutout to the specified broadcaster.\n
        Typically, you send Shoutouts when you or one of your moderators notice another broadcaster in your chat, the other broadcaster is coming up
        in conversation, or after they raid your broadcast.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHOUTOUTS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#send-a-shoutout

        :param from_broadcaster_id: The ID of the broadcaster that’s sending the Shoutout.
        :param to_broadcaster_id: The ID of the broadcaster that’s receiving the Shoutout.
        :param moderator_id: The ID of the broadcaster or a user that is one of the broadcaster’s moderators.
            This ID must match the user ID in the access token.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ~twitchAPI.type.TwitchAPIException: if the user in moderator_id is not one of the broadcasters moderators or the broadcaster
            can't send to_broadcaster_id a shoutout
        """
        param = {
            'from_broadcaster_id': from_broadcaster_id,
            'to_broadcaster_id': to_broadcaster_id,
            'moderator_id': moderator_id
        }
        err = {403: TwitchAPIException(f'Forbidden: the user with ID {moderator_id} is not one of the moderators broadcasters or '
                                       f"the broadcaster can't send {to_broadcaster_id} a shoutout")}
        await self._build_result('POST', 'chat/shoutouts', param, AuthType.USER, [AuthScope.MODERATOR_MANAGE_SHOUTOUTS], None, error_handler=err)

    async def get_chatters(self,
                           broadcaster_id: str,
                           moderator_id: str,
                           first: Optional[int] = None,
                           after: Optional[str] = None) -> GetChattersResponse:
        """Gets the list of users that are connected to the broadcaster’s chat session.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_CHATTERS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-chatters

        :param broadcaster_id: The ID of the broadcaster whose list of chatters you want to get.
        :param moderator_id: The ID of the broadcaster or one of the broadcaster’s moderators.
                    This ID must match the user ID in the user access token.
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 1000 |default| :code:`100`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if first is not between 1 and 1000
        """
        if first is not None and (first < 1 or first > 1000):
            raise ValueError('first must be between 1 and 1000')

        param = {
            'broadcaster_id': broadcaster_id,
            'moderator_id': moderator_id,
            'first': first,
            'after': after
        }
        return await self._build_iter_result('GET', 'chat/chatters', param, AuthType.USER, [AuthScope.MODERATOR_READ_CHATTERS], GetChattersResponse)

    async def get_shield_mode_status(self,
                                     broadcaster_id: str,
                                     moderator_id: str) -> ShieldModeStatus:
        """Gets the broadcaster’s Shield Mode activation status.

        Requires User Authentication with either :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_SHIELD_MODE` or
        :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHIELD_MODE`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-shield-mode-status

        :param broadcaster_id: The ID of the broadcaster whose Shield Mode activation status you want to get.
        :param moderator_id: The ID of the broadcaster or a user that is one of the broadcaster’s moderators.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'moderator_id': moderator_id
        }
        return await self._build_result('GET', 'moderation/shield_mode', param, AuthType.USER,
                                        [[AuthScope.MODERATOR_READ_SHIELD_MODE, AuthScope.MODERATOR_MANAGE_SHIELD_MODE]], ShieldModeStatus)

    async def update_shield_mode_status(self,
                                        broadcaster_id: str,
                                        moderator_id: str,
                                        is_active: bool) -> ShieldModeStatus:
        """Activates or deactivates the broadcaster’s Shield Mode.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHIELD_MODE`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#update-shield-mode-status

        :param broadcaster_id: The ID of the broadcaster whose Shield Mode you want to activate or deactivate.
        :param moderator_id: The ID of the broadcaster or a user that is one of the broadcaster’s moderators.
        :param is_active: A Boolean value that determines whether to activate Shield Mode.
                Set to true to activate Shield Mode; otherwise, false to deactivate Shield Mode.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'moderator_id': moderator_id
        }
        return await self._build_result('PUT', 'moderation/shield_mode', param, AuthType.USER, [AuthScope.MODERATOR_MANAGE_SHIELD_MODE],
                                        ShieldModeStatus, body_data={'is_active': is_active})

    async def get_charity_campaign(self,
                                   broadcaster_id: str) -> Optional[CharityCampaign]:
        """Gets information about the charity campaign that a broadcaster is running.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_CHARITY`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-charity-campaign

        :param broadcaster_id: The ID of the broadcaster that’s currently running a charity campaign.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        return await self._build_result('GET', 'charity/campaigns', {'broadcaster_id': broadcaster_id}, AuthType.USER,
                                        [AuthScope.CHANNEL_READ_CHARITY], CharityCampaign)

    async def get_charity_donations(self,
                                    broadcaster_id: str,
                                    first: Optional[int] = None,
                                    after: Optional[str] = None) -> AsyncGenerator[CharityCampaignDonation, None]:
        """Gets the list of donations that users have made to the broadcaster’s active charity campaign.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_CHARITY`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-charity-campaign-donations

        :param broadcaster_id: The ID of the broadcaster that’s currently running a charity campaign.
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default|:code:`20`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'first': first,
            'after': after
        }
        async for y in self._build_generator('GET', 'charity/donations', param, AuthType.USER, [AuthScope.CHANNEL_READ_CHARITY],
                                             CharityCampaignDonation):
            yield y

    async def get_content_classification_labels(self, locale: Optional[str] = None) -> List[ContentClassificationLabel]:
        """Gets information about Twitch content classification labels.

        Requires User or App Authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-content-classification-labels

        :param locale: Locale for the Content Classification Labels. |default|:code:`en-US`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        return await self._build_result('GET',
                                        'content_classification_labels',
                                        {'locale': locale},
                                        AuthType.EITHER, [],
                                        List[ContentClassificationLabel])

    async def get_ad_schedule(self,
                              broadcaster_id: str) -> AdSchedule:
        """This endpoint returns ad schedule related information, including snooze, when the last ad was run,
        when the next ad is scheduled, and if the channel is currently in pre-roll free time. Note that a new ad cannot
        be run until 8 minutes after running a previous ad.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_ADS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-ad-schedule

        :param broadcaster_id: Provided broadcaster_id must match the user_id in the auth token.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        return await self._build_result('GET',
                                        'channels/ads',
                                        {'broadcaster_id': broadcaster_id},
                                        AuthType.USER, [AuthScope.CHANNEL_READ_ADS],
                                        AdSchedule)

    async def snooze_next_ad(self,
                             broadcaster_id: str) -> AdSnoozeResponse:
        """If available, pushes back the timestamp of the upcoming automatic mid-roll ad by 5 minutes.
        This endpoint duplicates the snooze functionality in the creator dashboard’s Ads Manager.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_ADS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#snooze-next-ad

        :param broadcaster_id: Provided broadcaster_id must match the user_id in the auth token.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        return await self._build_result('POST',
                                        'channels/ads/schedule/snooze',
                                        {'broadcaster_id': broadcaster_id},
                                        AuthType.USER, [AuthScope.CHANNEL_MANAGE_ADS],
                                        AdSnoozeResponse)

    async def send_chat_message(self,
                                broadcaster_id: str,
                                sender_id: str,
                                message: str,
                                reply_parent_message_id: Optional[str] = None) -> SendMessageResponse:
        """Sends a message to the broadcaster’s chat room.

        Requires User or App Authentication with :const:`~twitchAPI.type.AuthScope.USER_WRITE_CHAT` \n
        If App Authorization is used, then additionally requires :const:`~twitchAPI.type.AuthScope.USER_BOT` scope from the
        chatting user and either :const:`~twitchAPI.type.AuthScope.CHANNEL_BOT` from the broadcaster or moderator status.\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#send-chat-message

        :param broadcaster_id: The ID of the broadcaster whose chat room the message will be sent to.
        :param sender_id: The ID of the user sending the message. This ID must match the user ID in the user access token.
        :param message: The message to send. The message is limited to a maximum of 500 characters.
            Chat messages can also include emoticons. To include emoticons, use the name of the emote.
            The names are case sensitive. Don’t include colons around the name (e.g., :bleedPurple:).
            If Twitch recognizes the name, Twitch converts the name to the emote before writing the chat message to the chat room
        :param reply_parent_message_id: The ID of the chat message being replied to.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        param = {
            'broadcaster_id': broadcaster_id,
            'sender_id': sender_id,
            'message': message,
            'reply_parent_message_id': reply_parent_message_id
        }
        return await self._build_result('POST',
                                        'chat/messages',
                                        param,
                                        AuthType.EITHER, [AuthScope.USER_WRITE_CHAT],
                                        SendMessageResponse)

    async def get_moderated_channels(self,
                                     user_id: str,
                                     after: Optional[str] = None,
                                     first: Optional[int] = None) -> AsyncGenerator[ChannelModerator, None]:
        """Gets a list of channels that the specified user has moderator privileges in.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.USER_READ_MODERATED_CHANNELS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-moderated-channels

        :param user_id: A user’s ID. Returns the list of channels that this user has moderator privileges in.
                     This ID must match the user ID in the user OAuth token
        :param first: The maximum number of items to return per API call.
                     You can use this in combination with :const:`~twitchAPI.helper.limit()` to optimize the bandwidth and number of API calls used to
                     fetch the amount of results you desire.\n
                     Minimum 1, Maximum 100 |default|:code:`20`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if first is set and not in range 1 to 100
        """
        if first is not None and (first < 1 or first > 100):
            raise ValueError('first has to be between 1 and 100')
        param = {
            'user_id': user_id,
            'after': after,
            'first': first
        }
        async for y in self._build_generator('GET', 'moderation/channels', param,
                                             AuthType.USER, [AuthScope.USER_READ_MODERATED_CHANNELS],
                                             ChannelModerator):
            yield y

    async def get_user_emotes(self,
                              user_id: str,
                              broadcaster_id: Optional[str] = None,
                              after: Optional[str] = None) -> UserEmotesResponse:
        """Retrieves emotes available to the user across all channels.

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.USER_READ_EMOTES`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-user-emotes

        :param user_id: The ID of the user. This ID must match the user ID in the user access token.
        :param broadcaster_id: The User ID of a broadcaster you wish to get follower emotes of. Using this query parameter will guarantee inclusion
                    of the broadcaster’s follower emotes in the response body.\n
                    Note: If the user specified in user_id is subscribed to the broadcaster specified, their follower emotes will appear in the
                    response body regardless if this query parameter is used.
                    |default| :code:`None`
        :param after: Cursor for forward pagination.\n
                    Note: The library handles pagination on its own, only use this parameter if you get a pagination cursor via other means.
                    |default| :code:`None`
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        """
        param = {
            'user_id': user_id,
            'after': after,
            'broadcaster_id': broadcaster_id
        }
        return await self._build_iter_result('GET', 'chat/emotes/user', param,
                                             AuthType.USER, [AuthScope.USER_READ_EMOTES],
                                             UserEmotesResponse)

    async def warn_chat_user(self,
                             broadcaster_id: str,
                             moderator_id: str,
                             user_id: str,
                             reason: str) -> WarnResponse:
        """Warns a user in the specified broadcaster’s chat room, preventing them from chat interaction until the warning is acknowledged.
        New warnings can be issued to a user when they already have a warning in the channel (new warning will replace old warning).

        Requires User Authentication with :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_WARNINGS`\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#warn-chat-user

        :param broadcaster_id: The ID of the channel in which the warning will take effect.
        :param moderator_id: The ID of the twitch user who requested the warning.
        :param user_id: The ID of the twitch user to be warned.
        :param reason: A custom reason for the warning. Max 500 chars.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.MissingScopeException: if the user authentication is missing the required scope
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :raises ValueError: if :const:`~twitchAPI.twitch.Twitch.warn_chat_user.params.reason` is longer than 500 characters
        """
        if len(reason) > 500:
            raise ValueError('reason has to be les than 500 characters long')
        param = {
            'broadcaster_id': broadcaster_id,
            'moderator_id': moderator_id
        }
        data = {
            'data': [{
                'user_id': user_id,
                'reason': reason
            }]
        }
        return await self._build_result('POST', 'moderation/warnings', param, AuthType.USER, [AuthScope.MODERATOR_MANAGE_WARNINGS],
                                        WarnResponse, body_data=data)

    async def get_shared_chat_session(self, broadcaster_id: str) -> Optional[SharedChatSession]:
        """Retrieves the active shared chat session for a channel.

        Requires User or App Authentication\n
        For detailed documentation, see here: https://dev.twitch.tv/docs/api/reference#get-shared-chat-session

        :param broadcaster_id: The User ID of the channel broadcaster.
        :raises ~twitchAPI.type.TwitchAPIException: if the request was malformed
        :raises ~twitchAPI.type.UnauthorizedException: if user authentication is not set or invalid
        :raises ~twitchAPI.type.TwitchAuthorizationException: if the used authentication token became invalid and a re authentication failed
        :raises ~twitchAPI.type.TwitchBackendException: if the Twitch API itself runs into problems
        :raises ~twitchAPI.type.TwitchAPIException: if a Query Parameter is missing or invalid
        :returns: None if there is no active shared chat session
        """
        param = {
            'broadcaster_id': broadcaster_id
        }
        return await self._build_result('GET', 'shared_chat/session', param, AuthType.EITHER, [], SharedChatSession)

==> ./type.py <==
#  Copyright (c) 2020. Lena "Teekeks" During <info@teawork.de>
"""
Type Definitions
----------------"""
from dataclasses import dataclass
from enum import Enum
from typing_extensions import TypedDict
from enum_tools.documentation import document_enum

__all__ = ['AnalyticsReportType', 'AuthScope', 'ModerationEventType', 'TimePeriod', 'SortMethod', 'HypeTrainContributionMethod',
           'VideoType', 'AuthType', 'StatusCode', 'PubSubResponseError', 'CustomRewardRedemptionStatus', 'SortOrder',
           'BlockSourceContext', 'BlockReason', 'EntitlementFulfillmentStatus', 'PollStatus', 'PredictionStatus', 'AutoModAction',
           'AutoModCheckEntry', 'DropsEntitlementFulfillmentStatus', 'ChatEvent', 'ChatRoom',
           'TwitchAPIException', 'InvalidRefreshTokenException', 'InvalidTokenException', 'NotFoundException', 'TwitchAuthorizationException',
           'UnauthorizedException', 'MissingScopeException', 'TwitchBackendException', 'PubSubListenTimeoutException', 'MissingAppSecretException',
           'EventSubSubscriptionTimeout', 'EventSubSubscriptionConflict', 'EventSubSubscriptionError', 'DeprecatedError', 'TwitchResourceNotFound',
           'ForbiddenError']


class AnalyticsReportType(Enum):
    """Enum of all Analytics report types
    """
    V1 = 'overview_v1'
    V2 = 'overview_v2'

@document_enum
class AuthScope(Enum):
    """Enum of Authentication scopes"""
    ANALYTICS_READ_EXTENSION = 'analytics:read:extensions'
    """View analytics data for the Twitch Extensions owned by the authenticated account.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_game_analytics()`
    """
    ANALYTICS_READ_GAMES = 'analytics:read:games'
    """View analytics data for the games owned by the authenticated account.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_game_analytics()`
    """
    BITS_READ = 'bits:read'
    """View Bits information for a channel.
             
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_bits_leaderboard()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_cheer()`
    """
    CHANNEL_READ_SUBSCRIPTIONS = 'channel:read:subscriptions'
    """View a list of all subscribers to a channel and check if a user is subscribed to a channel.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_broadcaster_subscriptions()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_subscribe()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_end()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_gift()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_message()` |br|
    """
    CHANNEL_READ_STREAM_KEY = 'channel:read:stream_key'
    """View an authorized user’s stream key.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_stream_key()` |br|
    """
    CHANNEL_EDIT_COMMERCIAL = 'channel:edit:commercial'
    """Run commercials on a channel.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.start_commercial()`
    """
    CHANNEL_READ_HYPE_TRAIN = 'channel:read:hype_train'
    """View Hype Train information for a channel.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_hype_train_events()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_hype_train_begin()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_hype_train_progress()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_hype_train_end()` |br|
    """
    CHANNEL_MANAGE_BROADCAST = 'channel:manage:broadcast'
    """Manage a channel’s broadcast configuration, including updating channel configuration and managing stream markers and stream tags.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.modify_channel_information()` |br|
    :const:`~twitchAPI.twitch.Twitch.create_stream_marker()`
    """
    CHANNEL_READ_REDEMPTIONS = 'channel:read:redemptions'
    """View Channel Points custom rewards and their redemptions on a channel.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_custom_reward()` |br|
    :const:`~twitchAPI.twitch.Twitch.get_custom_reward_redemption()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_automatic_reward_redemption_add()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_add()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_update()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_remove()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_add()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_update()` |br|
    """
    CHANNEL_MANAGE_REDEMPTIONS = 'channel:manage:redemptions'
    """Manage Channel Points custom rewards and their redemptions on a channel.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_custom_reward()` |br|
    :const:`~twitchAPI.twitch.Twitch.get_custom_reward_redemption()` |br|
    :const:`~twitchAPI.twitch.Twitch.create_custom_reward()` |br|
    :const:`~twitchAPI.twitch.Twitch.delete_custom_reward()` |br|
    :const:`~twitchAPI.twitch.Twitch.update_custom_reward()` |br|
    :const:`~twitchAPI.twitch.Twitch.update_redemption_status()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_automatic_reward_redemption_add()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_add()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_update()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_remove()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_add()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_update()` |br|
    """
    CHANNEL_READ_CHARITY = 'channel:read:charity'
    """Read charity campaign details and user donations on your channel.
           
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_charity_campaign()` |br|
    :const:`~twitchAPI.twitch.Twitch.get_charity_donations()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_donate()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_start()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_progress()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_stop()` |br|
    """
    CLIPS_EDIT = 'clips:edit'
    """Manage Clips for a channel.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.create_clip()` |br|
    """
    USER_EDIT = 'user:edit'
    """Manage a user object.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.update_user()` |br|
    """
    USER_EDIT_BROADCAST = 'user:edit:broadcast'
    """View and edit a user’s broadcasting configuration, including Extension configurations.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_user_extensions()` |br|
    :const:`~twitchAPI.twitch.Twitch.get_user_active_extensions()` |br|
    :const:`~twitchAPI.twitch.Twitch.update_user_extensions()` |br|
    """
    USER_READ_BROADCAST = 'user:read:broadcast'
    """View a user’s broadcasting configuration, including Extension configurations.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_stream_markers()` |br|
    :const:`~twitchAPI.twitch.Twitch.get_user_extensions()` |br|
    :const:`~twitchAPI.twitch.Twitch.get_user_active_extensions()` |br|
    """
    USER_READ_EMAIL = 'user:read:email'
    """View a user’s email address.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_users()` (optional) |br|
    :const:`~twitchAPI.twitch.Twitch.update_user()` (optional) |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_user_update()` (optional) |br|
    """
    USER_EDIT_FOLLOWS = 'user:edit:follows'
    CHANNEL_MODERATE = 'channel:moderate'
    CHAT_EDIT = 'chat:edit'
    """Send chat messages to a chatroom using an IRC connection."""
    CHAT_READ = 'chat:read'
    """View chat messages sent in a chatroom using an IRC connection."""
    WHISPERS_READ = 'whispers:read'
    """Receive whisper messages for your user using PubSub."""
    WHISPERS_EDIT = 'whispers:edit'
    MODERATION_READ = 'moderation:read'
    """
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.check_automod_status()` |br|
    :const:`~twitchAPI.twitch.Twitch.get_banned_users()` |br|
    :const:`~twitchAPI.twitch.Twitch.get_moderators()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderator_add()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderator_remove()` |br|
    """
    CHANNEL_SUBSCRIPTIONS = 'channel_subscriptions'
    CHANNEL_READ_EDITORS = 'channel:read:editors'
    """View a list of users with the editor role for a channel.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_channel_editors()`
    """
    CHANNEL_MANAGE_VIDEOS = 'channel:manage:videos'
    """Manage a channel’s videos, including deleting videos.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.delete_videos()` |br|
    """
    USER_READ_BLOCKED_USERS = 'user:read:blocked_users'
    """View the block list of a user.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_user_block_list()` |br|
    """
    USER_MANAGE_BLOCKED_USERS = 'user:manage:blocked_users'
    """Manage the block list of a user.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.block_user()` |br|
    :const:`~twitchAPI.twitch.Twitch.unblock_user()` |br|
    """
    USER_READ_SUBSCRIPTIONS = 'user:read:subscriptions'
    """View if an authorized user is subscribed to specific channels.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.check_user_subscription()` |br|
    """
    USER_READ_FOLLOWS = 'user:read:follows'
    """View the list of channels a user follows.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_followed_channels()` |br|
    :const:`~twitchAPI.twitch.Twitch.get_followed_streams()` |br|
    """
    CHANNEL_READ_GOALS = 'channel:read:goals'
    """View Creator Goals for a channel.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_creator_goals()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_goal_begin()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_goal_progress()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_goal_end()` |br|
    """
    CHANNEL_READ_POLLS = 'channel:read:polls'
    """View a channel’s polls.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_polls()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_begin()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_progress()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_end()` |br|
    """
    CHANNEL_MANAGE_POLLS = 'channel:manage:polls'
    """Manage a channel’s polls.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_polls()` |br|
    :const:`~twitchAPI.twitch.Twitch.create_poll()` |br|
    :const:`~twitchAPI.twitch.Twitch.end_poll()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_begin()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_progress()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_end()` |br|
    """
    CHANNEL_READ_PREDICTIONS = 'channel:read:predictions'
    """View a channel’s Channel Points Predictions.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_predictions()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_begin()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_progress()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_lock()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_end()` |br|
    """
    CHANNEL_MANAGE_PREDICTIONS = 'channel:manage:predictions'
    """Manage of channel’s Channel Points Predictions
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_predictions()` |br|
    :const:`~twitchAPI.twitch.Twitch.create_prediction()` |br|
    :const:`~twitchAPI.twitch.Twitch.end_prediction()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_begin()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_progress()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_lock()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_end()` |br|
    """
    MODERATOR_MANAGE_AUTOMOD = 'moderator:manage:automod'
    """Manage messages held for review by AutoMod in channels where you are a moderator.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.manage_held_automod_message()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_automod_message_hold()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_automod_message_update()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_automod_terms_update()` |br|
    """
    CHANNEL_MANAGE_SCHEDULE = 'channel:manage:schedule'
    """Manage a channel’s stream schedule.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.update_channel_stream_schedule()` |br|
    :const:`~twitchAPI.twitch.Twitch.create_channel_stream_schedule_segment()` |br|
    :const:`~twitchAPI.twitch.Twitch.update_channel_stream_schedule_segment()` |br|
    :const:`~twitchAPI.twitch.Twitch.delete_channel_stream_schedule_segment()` |br|
    """
    MODERATOR_MANAGE_CHAT_SETTINGS = 'moderator:manage:chat_settings'
    """Manage a broadcaster’s chat room settings.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.update_chat_settings()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate()` |br|
    """
    MODERATOR_READ_CHAT_SETTINGS = 'moderator:read:chat_settings'
    """View a broadcaster’s chat room settings.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_chat_settings()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate()` |br|"""
    MODERATOR_MANAGE_BANNED_USERS = 'moderator:manage:banned_users'
    """Ban and unban users.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_banned_users()` |br|
    :const:`~twitchAPI.twitch.Twitch.ban_user()` |br|
    :const:`~twitchAPI.twitch.Twitch.unban_user()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate()` |br|
    """
    MODERATOR_READ_BANNED_USERS = 'moderator:read:banned_users'
    """Read banned users.
    
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate()` |br|
    """
    MODERATOR_READ_BLOCKED_TERMS = 'moderator:read:blocked_terms'
    """View a broadcaster’s list of blocked terms.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_blocked_terms()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate()` |br|
    """
    MODERATOR_MANAGE_BLOCKED_TERMS = 'moderator:manage:blocked_terms'
    """Manage a broadcaster’s list of blocked terms.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_blocked_terms()` |br|
    :const:`~twitchAPI.twitch.Twitch.add_blocked_term()` |br|
    :const:`~twitchAPI.twitch.Twitch.remove_blocked_term()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate()` |br|
    """
    CHANNEL_MANAGE_RAIDS = 'channel:manage:raids'
    """Manage a channel raiding another channel.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.start_raid()` |br|
    :const:`~twitchAPI.twitch.Twitch.cancel_raid()` |br|
    """
    MODERATOR_MANAGE_ANNOUNCEMENTS = 'moderator:manage:announcements'
    """Send announcements in channels where you have the moderator role.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.send_chat_announcement()` |br|
    """
    MODERATOR_MANAGE_CHAT_MESSAGES = 'moderator:manage:chat_messages'
    """Delete chat messages in channels where you have the moderator role.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.delete_chat_message()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate()` |br|
    """
    MODERATOR_READ_CHAT_MESSAGES = 'moderator:read:chat_messages'
    """Read deleted chat messages in channels where you have the moderator role.
    
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate()` |br|
    """
    MODERATOR_READ_WARNINGS = 'moderator:read:warnings'
    """Read warnings in channels where you have the moderator role.
    
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_acknowledge()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_send()` |br|
    """
    MODERATOR_MANAGE_WARNINGS = 'moderator:manage:warnings'
    """Warn users in channels where you have the moderator role.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.warn_chat_user()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_acknowledge()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_send()` |br|
    """
    USER_MANAGE_CHAT_COLOR = 'user:manage:chat_color'
    """Update the color used for the user’s name in chat.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.update_user_chat_color()` |br|
    """
    CHANNEL_MANAGE_MODERATORS = 'channel:manage:moderators'
    """Add or remove the moderator role from users in your channel.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.add_channel_moderator()` |br|
    :const:`~twitchAPI.twitch.Twitch.remove_channel_moderator()` |br|
    :const:`~twitchAPI.twitch.Twitch.get_moderators()` |br|
    """
    CHANNEL_READ_VIPS = 'channel:read:vips'
    """Read the list of VIPs in your channel.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_vips()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_add()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_remove()` |br|
    """
    MODERATOR_READ_MODERATORS = 'moderator:read:moderators'
    """Read the list of channels you are moderator in.
    
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate()` |br|
    """
    MODERATOR_READ_VIPS = 'moderator:read:vips'
    CHANNEL_MANAGE_VIPS = 'channel:manage:vips'
    """Add or remove the VIP role from users in your channel.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_vips()` |br|
    :const:`~twitchAPI.twitch.Twitch.add_channel_vip()` |br|
    :const:`~twitchAPI.twitch.Twitch.remove_channel_vip()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_add()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_remove()` |br|
    """
    USER_READ_WHISPERS = 'user:read:whispers'
    """Receive whispers sent to your user.
    
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_user_whisper_message()` |br|
    """
    USER_MANAGE_WHISPERS = 'user:manage:whispers'
    """Receive whispers sent to your user, and send whispers on your user’s behalf.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.send_whisper()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_user_whisper_message()` |br|
    """
    MODERATOR_READ_CHATTERS = 'moderator:read:chatters'
    """View the chatters in a broadcaster’s chat room.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_chatters()` |br|
    """
    MODERATOR_READ_SHIELD_MODE = 'moderator:read:shield_mode'
    """View a broadcaster’s Shield Mode status.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_shield_mode_status()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_begin()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_end()` |br|
    """
    MODERATOR_MANAGE_SHIELD_MODE = 'moderator:manage:shield_mode'
    """Manage a broadcaster’s Shield Mode status.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.update_shield_mode_status()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_begin()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_end()` |br|
    """
    MODERATOR_READ_AUTOMOD_SETTINGS = 'moderator:read:automod_settings'
    """View a broadcaster’s AutoMod settings.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_automod_settings()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_automod_settings_update()` |br|
    """
    MODERATOR_MANAGE_AUTOMOD_SETTINGS = 'moderator:manage:automod_settings'
    """Manage a broadcaster’s AutoMod settings.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.update_automod_settings()` |br|
    """
    MODERATOR_READ_FOLLOWERS = 'moderator:read:followers'
    """Read the followers of a broadcaster.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_channel_followers()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_follow_v2()` |br|
    """
    MODERATOR_MANAGE_SHOUTOUTS = 'moderator:manage:shoutouts'
    """Manage a broadcaster’s shoutouts.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.send_a_shoutout()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_create()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_receive()` |br|
    """
    MODERATOR_READ_SHOUTOUTS = 'moderator:read:shoutouts'
    """View a broadcaster’s shoutouts.
    
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_create()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_receive()` |br|
    """
    CHANNEL_BOT = 'channel:bot'
    """Joins your channel’s chatroom as a bot user, and perform chat-related actions as that user.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.send_chat_message()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear_user_messages()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message_delete()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_notification()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_settings_update()` 
    """
    USER_BOT = 'user:bot'
    """Join a specified chat channel as your user and appear as a bot, and perform chat-related actions as your user.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.send_chat_message()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear_user_messages()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message_delete()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_notification()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_settings_update()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_hold()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_update()` |br|
    """
    USER_READ_CHAT = 'user:read:chat'
    """Receive chatroom messages and informational notifications relating to a channel’s chatroom.
    
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear_user_messages()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message_delete()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_notification()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_settings_update()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_hold()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_update()` |br|
    """
    CHANNEL_READ_ADS = 'channel:read:ads'
    """Read the ads schedule and details on your channel.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_ad_schedule()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_ad_break_begin()`
    """
    CHANNEL_MANAGE_ADS = 'channel:manage:ads'
    """Manage ads schedule on a channel.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_ad_schedule()`
    """
    USER_WRITE_CHAT = 'user:write:chat'
    """Send chat messages to a chatroom.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.send_chat_message()` |br|
    """
    USER_READ_MODERATED_CHANNELS = 'user:read:moderated_channels'
    """Read the list of channels you have moderator privileges in.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_moderated_channels()` |br|
    """
    USER_READ_EMOTES = 'user:read:emotes'
    """View emotes available to a user.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_user_emotes()` |br|
    """
    MODERATOR_READ_UNBAN_REQUESTS = 'moderator:read:unban_requests'
    """View a broadcaster’s unban requests.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.get_unban_requests()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_create()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_resolve()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate()` |br|
    """
    MODERATOR_MANAGE_UNBAN_REQUESTS = 'moderator:manage:unban_requests'
    """Manage a broadcaster’s unban requests.
    
    **API** |br|
    :const:`~twitchAPI.twitch.Twitch.resolve_unban_requests()` |br|
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_create()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_resolve()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate()` |br|
    """
    MODERATOR_READ_SUSPICIOUS_USERS = 'moderator:read:suspicious_users'
    """Read chat messages from suspicious users and see users flagged as suspicious in channels where you have the moderator role.
    
    **EventSub** |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_message()` |br|
    :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_update()` |br|
    """

class ModerationEventType(Enum):
    """Enum of moderation event types
    """
    BAN = 'moderation.user.ban'
    UNBAN = 'moderation.user.unban'
    UNKNOWN = ''


class TimePeriod(Enum):
    """Enum of valid Time periods
    """
    ALL = 'all'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'


class SortMethod(Enum):
    """Enum of valid sort methods
    """
    TIME = 'time'
    TRENDING = 'trending'
    VIEWS = 'views'


class HypeTrainContributionMethod(Enum):
    """Enum of valid Hype Train contribution types
    """

    BITS = 'BITS'
    SUBS = 'SUBS'
    OTHER = 'OTHER'
    UNKNOWN = ''


class VideoType(Enum):
    """Enum of valid video types
    """
    ALL = 'all'
    UPLOAD = 'upload'
    ARCHIVE = 'archive'
    HIGHLIGHT = 'highlight'
    UNKNOWN = ''


class AuthType(Enum):
    """Type of authentication required. Only internal use
    """
    NONE = 0
    USER = 1
    APP = 2
    EITHER = 3


class StatusCode(Enum):
    """Enum Code Status, see https://dev.twitch.tv/docs/api/reference#get-code-status for more documentation
    """
    SUCCESSFULLY_REDEEMED = 'SUCCESSFULLY_REDEEMED'
    ALREADY_CLAIMED = 'ALREADY_CLAIMED'
    EXPIRED = 'EXPIRED'
    USER_NOT_ELIGIBLE = 'USER_NOT_ELIGIBLE'
    NOT_FOUND = 'NOT_FOUND'
    INACTIVE = 'INACTIVE'
    UNUSED = 'UNUSED'
    INCORRECT_FORMAT = 'INCORRECT_FORMAT'
    INTERNAL_ERROR = 'INTERNAL_ERROR'
    UNKNOWN_VALUE = ''


class PubSubResponseError(Enum):
    """
    """
    BAD_MESSAGE = 'ERR_BADMESSAGE'
    BAD_AUTH = 'ERR_BADAUTH'
    SERVER = 'ERR_SERVER'
    BAD_TOPIC = 'ERR_BADTOPIC'
    NONE = ''
    UNKNOWN = 'unknown error'


class CustomRewardRedemptionStatus(Enum):
    """
    """
    UNFULFILLED = 'UNFULFILLED'
    FULFILLED = 'FULFILLED'
    CANCELED = 'CANCELED'


class SortOrder(Enum):
    """
    """
    OLDEST = 'OLDEST'
    NEWEST = 'NEWEST'


class BlockSourceContext(Enum):
    """
    """
    CHAT = 'chat'
    WHISPER = 'whisper'


class BlockReason(Enum):
    """
    """
    SPAM = 'spam'
    HARASSMENT = 'harassment'
    OTHER = 'other'


class EntitlementFulfillmentStatus(Enum):
    """
    """
    CLAIMED = 'CLAIMED'
    FULFILLED = 'FULFILLED'


class PollStatus(Enum):
    """
    """
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'
    MODERATED = 'MODERATED'
    INVALID = 'INVALID'
    TERMINATED = 'TERMINATED'
    ARCHIVED = 'ARCHIVED'


class PredictionStatus(Enum):
    """
    """
    ACTIVE = 'ACTIVE'
    RESOLVED = 'RESOLVED'
    CANCELED = 'CANCELED'
    LOCKED = 'LOCKED'


class AutoModAction(Enum):
    """
    """
    ALLOW = 'ALLOW'
    DENY = 'DENY'


class DropsEntitlementFulfillmentStatus(Enum):
    """
    """
    CLAIMED = 'CLAIMED'
    FULFILLED = 'FULFILLED'


class AutoModCheckEntry(TypedDict):
    msg_id: str
    """Developer-generated identifier for mapping messages to results."""
    msg_text: str
    """Message text"""

# CHAT

@document_enum
class ChatEvent(Enum):
    """Represents the possible events to listen for using :const:`~twitchAPI.chat.Chat.register_event()`"""
    READY = 'ready'
    """Triggered when the bot is started up and ready"""
    MESSAGE = 'message'
    """Triggered when someone wrote a message in a chat channel"""
    SUB = 'sub'
    """Triggered when someone subscribed to a channel"""
    RAID = 'raid'
    """Triggered when a channel gets raided"""
    ROOM_STATE_CHANGE = 'room_state_change'
    """Triggered when a chat channel is changed (e.g. sub only mode was enabled)"""
    JOIN = 'join'
    """Triggered when someone other than the bot joins a chat channel"""
    JOINED = 'joined'
    """Triggered when the bot joins a chat channel"""
    LEFT = 'left'
    """Triggered when the bot leaves a chat channel"""
    USER_LEFT = 'user_left'
    """Triggered when a user leaves a chat channel"""
    MESSAGE_DELETE = 'message_delete'
    """Triggered when a message gets deleted from a channel"""
    CHAT_CLEARED = 'chat_cleared'
    """Triggered when a user was banned, timed out or all messaged from a user where deleted"""
    WHISPER = 'whisper'
    """Triggered when someone whispers to your bot. NOTE: You need the :const:`~twitchAPI.type.AuthScope.WHISPERS_READ` Auth Scope
    to get this Event."""
    NOTICE = 'notice'
    """Triggered on server notice"""


@dataclass
class ChatRoom:
    name: str
    is_emote_only: bool
    is_subs_only: bool
    is_followers_only: bool
    is_unique_only: bool
    follower_only_delay: int
    room_id: str
    slow: int


# EXCEPTIONS


class TwitchAPIException(Exception):
    """Base Twitch API Exception"""
    pass


class InvalidRefreshTokenException(TwitchAPIException):
    """used User Refresh Token is invalid"""
    pass


class InvalidTokenException(TwitchAPIException):
    """Used if a invalid token is set for the client"""
    pass


class NotFoundException(TwitchAPIException):
    """Resource was not found with the given parameter"""
    pass


class TwitchAuthorizationException(TwitchAPIException):
    """Exception in the Twitch Authorization"""
    pass


class UnauthorizedException(TwitchAuthorizationException):
    """Not authorized to use this"""
    pass


class MissingScopeException(TwitchAuthorizationException):
    """authorization is missing scope"""
    pass


class TwitchBackendException(TwitchAPIException):
    """when the Twitch API itself is down"""
    pass


class PubSubListenTimeoutException(TwitchAPIException):
    """when a PubSub listen command times out"""
    pass


class MissingAppSecretException(TwitchAPIException):
    """When the app secret is not set but app authorization is attempted"""
    pass


class EventSubSubscriptionTimeout(TwitchAPIException):
    """When the waiting for a confirmed EventSub subscription timed out"""
    pass


class EventSubSubscriptionConflict(TwitchAPIException):
    """When you try to subscribe to a EventSub subscription that already exists"""
    pass


class EventSubSubscriptionError(TwitchAPIException):
    """if the subscription request was invalid"""
    pass


class DeprecatedError(TwitchAPIException):
    """If something has been marked as deprecated by the Twitch API"""
    pass


class TwitchResourceNotFound(TwitchAPIException):
    """If a requested resource was not found"""
    pass


class ForbiddenError(TwitchAPIException):
    """If you are not allowed to do that"""
    pass

==> ./chat/__init__.py <==
#  Copyright (c) 2022. Lena "Teekeks" During <info@teawork.de>
"""
Twitch Chat Bot
---------------

A simple twitch chat bot.\n
Chat bots can join channels, listen to chat and reply to messages, commands, subscriptions and many more.


********
Commands
********

Chat commands are specific messages user can send in chat in order to trigger some action of your bot.

Example:

.. code-block::

    <User123>: !say Hello world
    <MyBot>: User123 asked me to say "Hello world"


You can register listeners to chat commands using :const:`~twitchAPI.chat.Chat.register_command()`.

The bot prefix can be set by using :const:`~twitchAPI.chat.Chat.set_prefix()`, the default is :code:`!`

Your command listener function needs to be async and take in one parameter of type :const:`~twitchAPI.chat.ChatCommand`.

Example:

.. code-block:: python

    async def say_command_handler(cmd: ChatCommand):
        await cmd.reply(f'{cmd.user.name} asked me to say "{cmd.parameter}")

    chat.register_command('say', say_command_handler)

******************
Command Middleware
******************

Command Middleware is a way to control when a command should be executed.

See :doc:`/modules/twitchAPI.chat.middleware` and :doc:`/tutorial/chat-use-middleware` for more information.

******
Events
******

You can listen to different events happening in the chat rooms you joined.

Generally you register a event listener using :const:`~twitchAPI.chat.Chat.register_event()`.
The first parameter has to be of type :const:`~twitchAPI.type.ChatEvent` and the second one is your listener function.

Those Listeners always have to be async functions taking in one parameter (the payload). The Payload type is described below.

Example:

.. code-block:: python

    async def on_ready(cmd: EventData):
        await cmd.chat.join_room('teekeks42')

    chat.register_event(ChatEvent.READY, on_ready)

Available Events
================

.. list-table::
   :header-rows: 1

   * - Event Name
     - Event Data
     - Description
   * - Bot Ready
     - ChatEvent: :obj:`~twitchAPI.type.ChatEvent.READY` |br|
       Payload: :const:`~twitchAPI.chat.EventData`
     - This Event is triggered when the bot is started up and ready to join channels.
   * - Message Send
     - ChatEvent: :const:`~twitchAPI.type.ChatEvent.MESSAGE` |br|
       Payload: :const:`~twitchAPI.chat.ChatMessage`
     - This Event is triggered when someone wrote a message in a channel we joined
   * - Channel Subscription
     - ChatEvent: :const:`~twitchAPI.type.ChatEvent.SUB` |br|
       Payload: :const:`~twitchAPI.chat.ChatSub`
     - This Event is triggered when someone subscribed to a channel we joined.
   * - Raid
     - ChatEvent: :const:`~twitchAPI.type.ChatEvent.RAID` |br|
       Payload: :const:`dict`
     - Triggered when a channel gets raided
   * - Channel Config Changed
     - ChatEvent: :const:`~twitchAPI.type.ChatEvent.ROOM_STATE_CHANGE` |br|
       Payload: :const:`~twitchAPI.chat.RoomStateChangeEvent`
     - Triggered when a channel is changed (e.g. sub only mode was enabled)
   * - User Channel Join
     - ChatEvent: :const:`~twitchAPI.type.ChatEvent.JOIN` |br|
       Payload: :const:`~twitchAPI.chat.JoinEvent`
     - Triggered when someone other than the bot joins a channel. |br| **This will not always trigger, depending on channel size**
   * - User Channel Leave
     - ChatEvent: :const:`~twitchAPI.type.ChatEvent.USER_LEFT` |br|
       Payload: :const:`~twitchAPI.chat.LeftEvent`
     - Triggered when someone other than the bot leaves a channel. |br| **This will not always trigger, depending on channel size**
   * - Bot Channel Join
     - ChatEvent: :const:`~twitchAPI.type.ChatEvent.JOINED` |br|
       Payload: :const:`~twitchAPI.chat.JoinedEvent`
     - Triggered when the bot joins a channel
   * - Bot Channel Leave
     - ChatEvent: :const:`~twitchAPI.type.ChatEvent.LEFT` |br|
       Payload: :const:`~twitchAPI.chat.LeftEvent`
     - Triggered when the bot left a channel
   * - Message Delete
     - ChatEvent: :const:`~twitchAPI.type.ChatEvent.MESSAGE_DELETE` |br|
       Payload: :const:`~twitchAPI.chat.MessageDeletedEvent`
     - Triggered when a single message in a channel got deleted
   * - User Messages Cleared
     - ChatEvent: :const:`~twitchAPI.type.ChatEvent.CHAT_CLEARED` |br|
       Payload: :const:`~twitchAPI.chat.ClearChatEvent`
     - Triggered when a user was banned, timed out and/or all messaged from a user where deleted
   * - Bot Receives Whisper Message
     - ChatEvent: :const:`~twitchAPI.type.ChatEvent.WHISPER` |br|
       Payload: :const:`~twitchAPI.chat.WhisperEvent`
     - Triggered when someone whispers to your bot. |br| **You need the** :const:`~twitchAPI.type.AuthScope.WHISPERS_READ` **Auth Scope to receive this Event.**
   * - Server Notice
     - ChatEvent: :const:`~twitchAPI.type.ChatEvent.NOTICE` |br|
       Payload: :const:`~twitchAPI.chat.NoticeEvent`
     - Triggered when server sends a notice message.


************
Code example
************

.. code-block:: python

    from twitchAPI.twitch import Twitch
    from twitchAPI.oauth import UserAuthenticator
    from twitchAPI.type import AuthScope, ChatEvent
    from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
    import asyncio

    APP_ID = 'my_app_id'
    APP_SECRET = 'my_app_secret'
    USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
    TARGET_CHANNEL = 'teekeks42'


    # this will be called when the event READY is triggered, which will be on bot start
    async def on_ready(ready_event: EventData):
        print('Bot is ready for work, joining channels')
        # join our target channel, if you want to join multiple, either call join for each individually
        # or even better pass a list of channels as the argument
        await ready_event.chat.join_room(TARGET_CHANNEL)
        # you can do other bot initialization things in here


    # this will be called whenever a message in a channel was send by either the bot OR another user
    async def on_message(msg: ChatMessage):
        print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')


    # this will be called whenever someone subscribes to a channel
    async def on_sub(sub: ChatSub):
        print(f'New subscription in {sub.room.name}:\\n'
              f'  Type: {sub.sub_plan}\\n'
              f'  Message: {sub.sub_message}')


    # this will be called whenever the !reply command is issued
    async def test_command(cmd: ChatCommand):
        if len(cmd.parameter) == 0:
            await cmd.reply('you did not tell me what to reply with')
        else:
            await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')


    # this is where we set up the bot
    async def run():
        # set up twitch api instance and add user authentication with some scopes
        twitch = await Twitch(APP_ID, APP_SECRET)
        auth = UserAuthenticator(twitch, USER_SCOPE)
        token, refresh_token = await auth.authenticate()
        await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

        # create chat instance
        chat = await Chat(twitch)

        # register the handlers for the events you want

        # listen to when the bot is done starting up and ready to join channels
        chat.register_event(ChatEvent.READY, on_ready)
        # listen to chat messages
        chat.register_event(ChatEvent.MESSAGE, on_message)
        # listen to channel subscriptions
        chat.register_event(ChatEvent.SUB, on_sub)
        # there are more events, you can view them all in this documentation

        # you can directly register commands and their handlers, this will register the !reply command
        chat.register_command('reply', test_command)


        # we are done with our setup, lets start this bot up!
        chat.start()

        # lets run till we press enter in the console
        try:
            input('press ENTER to stop\\n')
        finally:
            # now we can close the chat bot and the twitch api client
            chat.stop()
            await twitch.close()


    # lets run our setup
    asyncio.run(run())

*******************
Class Documentation
*******************
"""
import asyncio
import dataclasses
import datetime
import re
import threading
from asyncio import CancelledError
from functools import partial
from logging import getLogger, Logger
from time import sleep
import aiohttp


from twitchAPI.twitch import Twitch
from twitchAPI.object.api import TwitchUser
from twitchAPI.helper import TWITCH_CHAT_URL, first, RateLimitBucket, RATE_LIMIT_SIZES, done_task_callback
from twitchAPI.type import ChatRoom, TwitchBackendException, AuthType, AuthScope, ChatEvent, UnauthorizedException

from typing import List, Optional, Union, Callable, Dict, Awaitable, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from twitchAPI.chat.middleware import BaseCommandMiddleware


__all__ = ['Chat', 'ChatUser', 'EventData', 'ChatMessage', 'ChatCommand', 'ChatSub', 'ChatRoom', 'ChatEvent', 'RoomStateChangeEvent',
           'JoinEvent', 'JoinedEvent', 'LeftEvent', 'ClearChatEvent', 'WhisperEvent', 'MessageDeletedEvent', 'NoticeEvent', 'HypeChat']


class ChatUser:
    """Represents a user in a chat channel
    """

    def __init__(self, chat, parsed, name_override=None):
        self.chat: 'Chat' = chat
        """The :const:`twitchAPI.chat.Chat` instance"""
        self.name: str = parsed['source']['nick'] if parsed['source']['nick'] is not None else f'{chat.username}'
        """The name of the user"""
        if self.name[0] == ':':
            self.name = self.name[1:]
        if name_override is not None:
            self.name = name_override
        self.badge_info = parsed['tags'].get('badge-info')
        """All infos related to the badges of the user"""
        self.badges = parsed['tags'].get('badges')
        """The badges of the user"""
        self.source_badges = parsed['tags'].get('source-badges')
        """The badges for the chatter in the room the message was sent from. This uses the same format as the badges tag."""
        self.source_badge_info = parsed['tags'].get('source-badge-info')
        """Contains metadata related to the chat badges in the source-badges tag."""
        self.color: str = parsed['tags'].get('color')
        """The color of the chat user if set"""
        self.display_name: str = parsed['tags'].get('display-name')
        """The display name, should usually be the same as name"""
        self.mod: bool = parsed['tags'].get('mod', '0') == '1'
        """if the user is a mod in chat channel"""
        self.subscriber: bool = parsed['tags'].get('subscriber') == '1'
        """if the user is a subscriber to the channel"""
        self.turbo: bool = parsed['tags'].get('turbo') == '1'
        """Indicates whether the user has site-wide commercial free mode enabled"""
        self.id: str = parsed['tags'].get('user-id')
        """The ID of the user"""
        self.user_type: str = parsed['tags'].get('user-type')
        """The type of user"""
        self.vip: bool = parsed['tags'].get('vip') == '1'
        """if the chatter is a channel VIP"""


class EventData:
    """Represents a basic chat event"""

    def __init__(self, chat):
        self.chat: 'Chat' = chat
        """The :const:`twitchAPI.chat.Chat` instance"""


class MessageDeletedEvent(EventData):

    def __init__(self, chat, parsed):
        super(MessageDeletedEvent, self).__init__(chat)
        self._room_name = parsed['command']['channel'][1:]
        self.message: str = parsed['parameters']
        """The content of the message that got deleted"""
        self.user_name: str = parsed['tags'].get('login')
        """Username of the message author"""
        self.message_id: str = parsed['tags'].get('target-msg-id')
        """ID of the message that got deleted"""
        self.sent_timestamp: int = int(parsed['tags'].get('tmi-sent-ts'))
        """The timestamp the deleted message was send"""

    @property
    def room(self) -> Optional[ChatRoom]:
        """The room the message was deleted in"""
        return self.chat.room_cache.get(self._room_name)


class RoomStateChangeEvent(EventData):
    """Triggered when a room state changed"""

    def __init__(self, chat, prev, new):
        super(RoomStateChangeEvent, self).__init__(chat)
        self.old: Optional[ChatRoom] = prev
        """The State of the room from before the change, might be Null if not in cache"""
        self.new: ChatRoom = new
        """The new room state"""

    @property
    def room(self) -> Optional[ChatRoom]:
        """Returns the Room from cache"""
        return self.chat.room_cache.get(self.new.name)


class JoinEvent(EventData):
    """"""

    def __init__(self, chat, channel_name, user_name):
        super(JoinEvent, self).__init__(chat)
        self._name = channel_name
        self.user_name: str = user_name
        """The name of the user that joined"""

    @property
    def room(self) -> Optional[ChatRoom]:
        """The room the user joined to"""
        return self.chat.room_cache.get(self._name)


class JoinedEvent(EventData):
    """"""

    def __init__(self, chat, channel_name, user_name):
        super(JoinedEvent, self).__init__(chat)
        self.room_name: str = channel_name
        """the name of the room the bot joined to"""
        self.user_name: str = user_name
        """the name of the bot"""


class LeftEvent(EventData):
    """When the bot or a user left a room"""

    def __init__(self, chat, channel_name, room, user):
        super(LeftEvent, self).__init__(chat)
        self.room_name: str = channel_name
        """the name of the channel the bot left"""
        self.user_name: str = user
        """The name of the user that left the chat"""
        self.cached_room: Optional[ChatRoom] = room
        """the cached room state, might bo Null"""


class HypeChat:

    def __init__(self, parsed):
        self.amount: int = int(parsed['tags'].get('pinned-chat-paid-amount'))
        """The value of the Hype Chat sent by the user."""
        self.currency: str = parsed['tags'].get('pinned-chat-paid-currency')
        """The ISO 4217 alphabetic currency code the user has sent the Hype Chat in."""
        self.exponent: int = int(parsed['tags'].get('pinned-chat-paid-exponent'))
        """Indicates how many decimal points this currency represents partial amounts in. 
        Decimal points start from the right side of the value defined in :const:`~twitchAPI.chat.HypeChat.amount`"""
        self.level: str = parsed['tags'].get('pinned-chat-paid-level')
        """The level of the Hype Chat, in English.\n
        Possible Values are:
        :code:`ONE`, :code:`TWO`, :code:`THREE`, :code:`FOUR`, :code:`FIVE`, :code:`SIX`, :code:`SEVEN`, :code:`EIGHT`, :code:`NINE`, :code:`TEN`"""
        self.is_system_message: bool = parsed['tags'].get('pinned-chat-paid-is-system-message') == '1'
        """A Boolean value that determines if the message sent with the Hype Chat was filled in by the system.\n
           If True, the user entered no message and the body message was automatically filled in by the system.\n
           If False, the user provided their own message to send with the Hype Chat."""


class ChatMessage(EventData):
    """Represents a chat message"""

    def __init__(self, chat, parsed):
        super(ChatMessage, self).__init__(chat)
        self._parsed = parsed
        self.text: str = parsed['parameters']
        """The message"""
        self.is_me: bool = False
        """Flag indicating if the message used the /me command"""
        result = _ME_REGEX.match(self.text)
        if result is not None:
            self.text = result.group('msg')
            self.is_me = True
        self.bits: int = int(parsed['tags'].get('bits', '0'))
        """The amount of Bits the user cheered"""
        self.first: bool = parsed['tags'].get('first-msg', '0') != '0'
        """Flag if message is user's first ever in room"""
        self.sent_timestamp: int = int(parsed['tags'].get('tmi-sent-ts'))
        """the unix timestamp of when the message was sent"""
        self.reply_parent_msg_id: Optional[str] = parsed['tags'].get('reply-parent-msg-id')
        """An ID that uniquely identifies the parent message that this message is replying to."""
        self.reply_parent_user_id: Optional[str] = parsed['tags'].get('reply-parent-user-id')
        """An ID that identifies the sender of the parent message."""
        self.reply_parent_user_login: Optional[str] = parsed['tags'].get('reply-parent-user-login')
        """The login name of the sender of the parent message. """
        self.reply_parent_display_name: Optional[str] = parsed['tags'].get('reply-parent-display-name')
        """The display name of the sender of the parent message."""
        self.reply_parent_msg_body: Optional[str] = parsed['tags'].get('reply-parent-msg-body')
        """The text of the parent message"""
        self.reply_thread_parent_msg_id: Optional[str] = parsed['tags'].get('reply-thread-parent-msg-id')
        """An ID that uniquely identifies the top-level parent message of the reply thread that this message is replying to.
           Is :code:`None` if this message is not a reply."""
        self.reply_thread_parent_user_login: Optional[str] = parsed['tags'].get('reply-thread-parent-user-login')
        """The login name of the sender of the top-level parent message. Is :code:`None` if this message is not a reply."""
        self.emotes = parsed['tags'].get('emotes')
        """The emotes used in the message"""
        self.id: str = parsed['tags'].get('id')
        """the ID of the message"""
        self.hype_chat: Optional[HypeChat] = HypeChat(parsed) if parsed['tags'].get('pinned-chat-paid-level') is not None else None
        """Hype Chat related data, is None if the message was not a hype chat"""
        self.source_id: Optional[str] = parsed['tags'].get('source-id')
        """A UUID that identifies the source message from the channel the message was sent from."""
        self.source_room_id: Optional[str] = parsed['tags'].get('source-room-id')
        """An ID that identifies the chat room (channel) the message was sent from."""



    @property
    def room(self) -> Optional[ChatRoom]:
        """The channel the message was issued in"""
        return self.chat.room_cache.get(self._parsed['command']['channel'][1:])

    @property
    def user(self) -> ChatUser:
        """The user that issued the message"""
        return ChatUser(self.chat, self._parsed)

    async def reply(self, text: str):
        """Reply to this message"""
        bucket = self.chat._get_message_bucket(self._parsed['command']['channel'][1:])
        await bucket.put()
        await self.chat.send_raw_irc_message(f'@reply-parent-msg-id={self.id} PRIVMSG #{self.room.name} :{text}')


class ChatCommand(ChatMessage):
    """Represents a command"""

    def __init__(self, chat, parsed):
        super(ChatCommand, self).__init__(chat, parsed)
        self.name: str = parsed['command'].get('bot_command')
        """the name of the command"""
        self.parameter: str = parsed['command'].get('bot_command_params', '')
        """the parameter given to the command"""

    async def send(self, message: str):
        """Sends a message to the channel the command was issued in

        :param message: the message you want to send
        """
        await self.chat.send_message(self.room.name, message)


class ChatSub:
    """Represents a sub to a channel"""

    def __init__(self, chat, parsed):
        self.chat: 'Chat' = chat
        """The :const:`twitchAPI.chat.Chat` instance"""
        self._parsed = parsed
        self.sub_type: str = parsed['tags'].get('msg-id')
        """The type of sub given"""
        self.sub_message: str = parsed['parameters'] if parsed['parameters'] is not None else ''
        """The message that was sent together with the sub"""
        self.sub_plan: str = parsed['tags'].get('msg-param-sub-plan')
        """the ID of the subscription plan that was used"""
        self.sub_plan_name: str = parsed['tags'].get('msg-param-sub-plan-name')
        """the name of the subscription plan that was used"""
        self.system_message: str = parsed['tags'].get('system-msg', '').replace('\\\\s', ' ')
        """the system message that was generated for this sub"""

    @property
    def room(self) -> Optional[ChatRoom]:
        """The room this sub was issued in"""
        return self.chat.room_cache.get(self._parsed['command']['channel'][1:])


class ClearChatEvent(EventData):

    def __init__(self, chat, parsed):
        super(ClearChatEvent, self).__init__(chat)
        self.room_name: str = parsed['command']['channel'][1:]
        """The name of the chat room the event happened in"""
        self.room_id: str = parsed['tags'].get('room-id')
        """The ID of the chat room the event happened in"""
        self.user_name: str = parsed['parameters']
        """The name of the user who's messages got cleared"""
        self.duration: Optional[int] = int(parsed['tags']['ban-duration']) if parsed['tags'].get('ban-duration') not in (None, '') else None
        """duration of the timeout in seconds. None if user was not timed out"""
        self.banned_user_id: Optional[str] = parsed['tags'].get('target-user-id')
        """The ID of the user who got banned or timed out. if :const:`~twitchAPI.chat.ClearChatEvent.duration` is None, the user was banned.
        Will be None when the user was not banned nor timed out."""
        self.sent_timestamp: int = int(parsed['tags'].get('tmi-sent-ts'))
        """The timestamp the event happened at"""

    @property
    def room(self) -> Optional[ChatRoom]:
        """The room this event was issued in. None on cache miss."""
        return self.chat.room_cache.get(self.room_name)


class WhisperEvent(EventData):

    def __init__(self, chat, parsed):
        super(WhisperEvent, self).__init__(chat)
        self._parsed = parsed
        self.message: str = parsed['parameters']
        """The message that was send"""

    @property
    def user(self) -> ChatUser:
        """The user that DMed your bot"""
        return ChatUser(self.chat, self._parsed)


class NoticeEvent(EventData):
    """Represents a server notice"""

    def __init__(self, chat, parsed):
        super(NoticeEvent, self).__init__(chat)
        self._room_name = parsed['command']['channel'][1:]
        """The name of the chat room the notice is from"""
        self.msg_id: str = parsed['tags'].get('msg-id')
        """Message ID of the notice, `Msg-id reference <https://dev.twitch.tv/docs/irc/msg-id/>`__"""
        self.message: str = parsed['parameters']
        """Description for the msg_id"""

    @property
    def room(self) -> Optional[ChatRoom]:
        """The room this notice is from"""
        return self.chat.room_cache.get(self._room_name)


COMMAND_CALLBACK_TYPE = Callable[[ChatCommand], Awaitable[None]]
EVENT_CALLBACK_TYPE = Callable[[Any], Awaitable[None]]
CHATROOM_TYPE = Union[str, ChatRoom]

_ME_REGEX = re.compile(r'^\x01ACTION (?P<msg>.+)\x01$')


class Chat:
    """The chat bot instance"""

    def __init__(self,
                 twitch: Twitch,
                 connection_url: Optional[str] = None,
                 is_verified_bot: bool = False,
                 initial_channel: Optional[List[str]] = None,
                 callback_loop: Optional[asyncio.AbstractEventLoop] = None,
                 no_message_reset_time: Optional[float] = 10,
                 no_shared_chat_messages: bool = True):
        """
        :param twitch: A Authenticated twitch instance
        :param connection_url: alternative connection url |default|:code:`None`
        :param is_verified_bot: set to true if your bot is verified by twitch |default|:code:`False`
        :param initial_channel: List of channel which should be automatically joined on startup |default| :code:`None`
        :param callback_loop: The asyncio eventloop to be used for callbacks. \n
            Set this if you or a library you use cares about which asyncio event loop is running the callbacks.
            Defaults to the one used by Chat.
        :param no_message_reset_time: How many minutes of mo messages from Twitch before the connection is considered
            dead. Twitch sends a PING just under every 5 minutes and the bot must respond to them for Twitch to keep
            the connection active. At 10 minutes we've definitely missed at least one PING |default|:code:`10`
        :param no_shared_chat_messages: Filter out Twitch shared chat messages from other channels. This will only
            listen for messages that were sent in the chat room that the bot is listening in.
        """
        self.logger: Logger = getLogger('twitchAPI.chat')
        """The logger used for Chat related log messages"""
        self._prefix: str = "!"
        self.twitch: Twitch = twitch
        """The twitch instance being used"""
        if not self.twitch.has_required_auth(AuthType.USER, [AuthScope.CHAT_READ]):
            raise ValueError('passed twitch instance is missing User Auth.')
        self.connection_url: str = connection_url if connection_url is not None else TWITCH_CHAT_URL
        """Alternative connection url |default|:code:`None`"""
        self.ping_frequency: int = 120
        """Frequency in seconds for sending ping messages. This should usually not be changed."""
        self.ping_jitter: int = 4
        """Jitter in seconds for ping messages. This should usually not be changed."""
        self._callback_loop = callback_loop
        self.no_message_reset_time: Optional[float] = no_message_reset_time
        self.no_shared_chat_messages: bool = no_shared_chat_messages
        self.listen_confirm_timeout: int = 30
        """Time in second that any :code:`listen_` should wait for its subscription to be completed."""
        self.reconnect_delay_steps: List[int] = [0, 1, 2, 4, 8, 16, 32, 64, 128]
        """Time in seconds between reconnect attempts"""
        self.log_no_registered_command_handler: bool = True
        """Controls if instances of commands being issued in chat where no handler exists should be logged. |default|:code:`True`"""
        self.__connection = None
        self._session = None
        self.__socket_thread: Optional[threading.Thread] = None
        self.__running: bool = False
        self.__socket_loop = None
        self.__startup_complete: bool = False
        self.__tasks = None
        self._ready = False
        self._send_buckets = {}
        self._join_target = [c[1:].lower() if c[0] == '#' else c.lower() for c in initial_channel] if initial_channel is not None else []
        self._join_bucket = RateLimitBucket(10, 2000 if is_verified_bot else 20, 'channel_join', self.logger)
        self.__waiting_for_pong: bool = False
        self._event_handler = {}
        self._command_handler = {}
        self.room_cache: Dict[str, ChatRoom] = {}
        """internal cache of all chat rooms the bot is currently in"""
        self._room_join_locks = []
        self._room_leave_locks = []
        self._closing: bool = False
        self.join_timeout: int = 10
        """Time in seconds till a channel join attempt times out"""
        self._mod_status_cache = {}
        self._subscriber_status_cache = {}
        self._channel_command_prefix = {}
        self._command_middleware: List['BaseCommandMiddleware'] = []
        self._command_specific_middleware: Dict[str, List['BaseCommandMiddleware']] = {}
        self._task_callback = partial(done_task_callback, self.logger)
        self.default_command_execution_blocked_handler: Optional[Callable[[ChatCommand], Awaitable[None]]] = None
        """The default handler to be called should a command execution be blocked by a middleware that has no specific handler set."""
        self.username: Optional[str] = None

    def __await__(self):
        t = asyncio.create_task(self._get_username())
        yield from t
        return self

    async def _get_username(self):
        user: TwitchUser = await first(self.twitch.get_users())
        self.username = user.login.lower()

    ##################################################################################################################################################
    # command parsing
    ##################################################################################################################################################

    def _parse_irc_message(self, message: str):
        parsed_message = {
            'tags': {},
            'source': None,
            'command': None,
            'parameters': None
        }
        idx = 0
        raw_tags_component = None
        raw_source_component = None
        raw_parameters_component = None

        if message[idx] == '@':
            end_idx = message.index(' ')
            raw_tags_component = message[1:end_idx]
            idx = end_idx + 1

        if message[idx] == ':':
            end_idx = message.index(' ', idx)
            raw_source_component = message[idx:end_idx]
            idx = end_idx + 1

        try:
            end_idx = message.index(':', idx)
        except ValueError:
            end_idx = len(message)

        raw_command_component = message[idx:end_idx].strip()

        if end_idx != len(message):
            idx = end_idx + 1
            raw_parameters_component = message[idx::]

        parsed_message['command'] = self._parse_irc_command(raw_command_component)

        if parsed_message['command'] is None:
            return None

        if raw_tags_component is not None:
            parsed_message['tags'] = self._parse_irc_tags(raw_tags_component)

        parsed_message['source'] = self._parse_irc_source(raw_source_component)
        parsed_message['parameters'] = raw_parameters_component
        if parsed_message['command']['command'] == 'PRIVMSG':
            ch = parsed_message['command'].get('channel', '#')[1::]
            used_prefix = self._channel_command_prefix.get(ch, self._prefix)
            if raw_parameters_component is not None and raw_parameters_component.startswith(used_prefix):
                parsed_message['command'] = self._parse_irc_parameters(raw_parameters_component, parsed_message['command'], used_prefix)

        return parsed_message

    @staticmethod
    def _parse_irc_parameters(raw_parameters_component: str, command, prefix):
        command_parts = raw_parameters_component[len(prefix)::].strip()
        try:
            params_idx = command_parts.index(' ')
        except ValueError:
            command['bot_command'] = command_parts
            return command
        command['bot_command'] = command_parts[:params_idx]
        command['bot_command_params'] = command_parts[params_idx:].strip()
        return command

    @staticmethod
    def _parse_irc_source(raw_source_component: str):
        if raw_source_component is None:
            return None
        source_parts = raw_source_component.split('!')
        return {
            'nick': source_parts[0] if len(source_parts) == 2 else None,
            'host': source_parts[1] if len(source_parts) == 2 else source_parts[0]
        }

    @staticmethod
    def _parse_irc_tags(raw_tags_component: str):
        tags_to_ignore = ('client-nonce', 'flags')
        parsed_tags = {}

        tags = raw_tags_component.split(';')

        for tag in tags:
            parsed_tag = tag.split('=')
            tag_value = None if parsed_tag[1] == '' else parsed_tag[1]
            if parsed_tag[0] in ('badges', 'badge-info', 'source-badges', 'source-badge-info'):
                if tag_value is not None:
                    d = {}
                    badges = tag_value.split(',')
                    for pair in badges:
                        badge_parts = pair.split('/', 1)
                        d[badge_parts[0]] = badge_parts[1]
                    parsed_tags[parsed_tag[0]] = d
                else:
                    parsed_tags[parsed_tag[0]] = None
            elif parsed_tag[0] == 'emotes':
                if tag_value is not None:
                    d = {}
                    emotes = tag_value.split('/')
                    for emote in emotes:
                        emote_parts = emote.split(':')
                        text_positions = []
                        positions = emote_parts[1].split(',')
                        for position in positions:
                            pos_parts = position.split('-')
                            text_positions.append({
                                'start_position': pos_parts[0],
                                'end_position': pos_parts[1]
                            })
                        d[emote_parts[0]] = text_positions
                    parsed_tags[parsed_tag[0]] = d
                else:
                    parsed_tags[parsed_tag[0]] = None
            elif parsed_tag[0] == 'emote-sets':
                parsed_tags[parsed_tag[0]] = tag_value.split(',')
            else:
                if parsed_tag[0] not in tags_to_ignore:
                    parsed_tags[parsed_tag[0]] = tag_value
        return parsed_tags

    def _parse_irc_command(self, raw_command_component: str):
        command_parts = raw_command_component.split(' ')

        if command_parts[0] in ('JOIN', 'PART', 'NOTICE', 'CLEARCHAT', 'HOSTTARGET', 'PRIVMSG',
                                'USERSTATE', 'ROOMSTATE', '001', 'USERNOTICE', 'CLEARMSG', 'WHISPER'):
            parsed_command = {
                'command': command_parts[0],
                'channel': command_parts[1]
            }
        elif command_parts[0] in ('PING', 'GLOBALUSERSTATE', 'RECONNECT'):
            parsed_command = {
                'command': command_parts[0]
            }
        elif command_parts[0] == 'CAP':
            parsed_command = {
                'command': command_parts[0],
                'is_cap_request_enabled': command_parts[2] == 'ACK'
            }
        elif command_parts[0] == '421':
            # unsupported command in parts 2
            self.logger.warning(f'Unsupported IRC command: {command_parts[0]}')
            return None
        elif command_parts[0] == '353':
            parsed_command = {
                'command': command_parts[0]
            }
        elif command_parts[0] in ('002', '003', '004', '366', '372', '375', '376'):
            self.logger.debug(f'numeric message: {command_parts[0]}\n{raw_command_component}')
            return None
        else:
            # unexpected command
            self.logger.warning(f'Unexpected command: {command_parts[0]}')
            return None

        return parsed_command

    ##################################################################################################################################################
    # general web socket tools
    ##################################################################################################################################################

    def start(self) -> None:
        """
        Start the Chat Client

        :raises RuntimeError: if already started
        """
        self.logger.debug('starting chat...')
        if self.__running:
            raise RuntimeError('already started')
        if self.username is None:
            raise RuntimeError('Chat() was not awaited')
        if not self.twitch.has_required_auth(AuthType.USER, [AuthScope.CHAT_READ]):
            raise UnauthorizedException('CHAT_READ authscope is required to run a chat bot')
        self.__startup_complete = False
        self._closing = False
        self._ready = False
        self.__socket_thread = threading.Thread(target=self.__run_socket)
        self.__running = True
        self.__socket_thread.start()
        while not self.__startup_complete:
            sleep(0.01)
        self.logger.debug('chat started up!')

    def stop(self) -> None:
        """
        Stop the Chat Client

        :raises RuntimeError: if the client is not running
        """

        if not self.__running:
            raise RuntimeError('not running')
        self.logger.debug('stopping chat...')
        self.__startup_complete = False
        self.__running = False
        self._ready = False
        f = asyncio.run_coroutine_threadsafe(self._stop(), self.__socket_loop)
        f.result()

    async def _stop(self):
        await self.__connection.close()
        await self._session.close()
        # wait for ssl to close as per aiohttp docs...
        await asyncio.sleep(0.25)
        # clean up bot state
        self.__connection = None
        self._session = None
        self.room_cache = {}
        self._room_join_locks = []
        self._room_leave_locks = []
        self._closing = True

    async def __connect(self, is_startup=False):
        if is_startup:
            self.logger.debug('connecting...')
        else:
            self.logger.debug('reconnecting...')
        if self.__connection is not None and not self.__connection.closed:
            await self.__connection.close()
        retry = 0
        need_retry = True
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.twitch.session_timeout)
        while need_retry and retry < len(self.reconnect_delay_steps):
            need_retry = False
            try:
                self.__connection = await self._session.ws_connect(self.connection_url)
            except Exception:
                self.logger.warning(f'connection attempt failed, retry in {self.reconnect_delay_steps[retry]}s...')
                await asyncio.sleep(self.reconnect_delay_steps[retry])
                retry += 1
                need_retry = True
        if retry >= len(self.reconnect_delay_steps):
            raise TwitchBackendException('can\'t connect')

    async def _keep_loop_alive(self):
        while not self._closing:
            await asyncio.sleep(0.1)

    def __run_socket(self):
        self.__socket_loop = asyncio.new_event_loop()
        if self._callback_loop is None:
            self._callback_loop = self.__socket_loop
        asyncio.set_event_loop(self.__socket_loop)

        # startup
        self.__socket_loop.run_until_complete(self.__connect(is_startup=True))

        self.__tasks = [
            asyncio.ensure_future(self.__task_receive(), loop=self.__socket_loop),
            asyncio.ensure_future(self.__task_startup(), loop=self.__socket_loop)
        ]
        # keep loop alive
        self.__socket_loop.run_until_complete(self._keep_loop_alive())

    async def _send_message(self, message: str):
        self.logger.debug(f'> "{message}"')
        await self.__connection.send_str(message)

    async def __task_receive(self):
        receive_timeout = None if self.no_message_reset_time is None else self.no_message_reset_time * 60
        try:
            handlers: Dict[str, Callable] = {
                'PING': self._handle_ping,
                'PRIVMSG': self._handle_msg,
                '001': self._handle_ready,
                'ROOMSTATE': self._handle_room_state,
                'JOIN': self._handle_join,
                'USERNOTICE': self._handle_user_notice,
                'CLEARMSG': self._handle_clear_msg,
                'CAP': self._handle_cap_reply,
                'PART': self._handle_part,
                'NOTICE': self._handle_notice,
                'CLEARCHAT': self._handle_clear_chat,
                'WHISPER': self._handle_whisper,
                'RECONNECT': self._handle_reconnect,
                'USERSTATE': self._handle_user_state
            }
            while not self.__connection.closed:
                try:  # At minimum we should receive a PING request just under every 5 minutes
                    message = await self.__connection.receive(timeout=receive_timeout)
                except asyncio.TimeoutError:
                    self.logger.warning(f"Reached timeout for websocket receive, will attempt a reconnect")
                    if self.__running:
                        try:
                            await self._handle_base_reconnect()
                        except TwitchBackendException:
                            self.logger.exception('Connection to chat websocket lost and unable to reestablish connection!')
                            break
                    else:
                        break
                if message.type == aiohttp.WSMsgType.TEXT:
                    messages = message.data.split('\r\n')
                    for m in messages:
                        if len(m) == 0:
                            continue
                        self.logger.debug(f'< {m}')
                        parsed = self._parse_irc_message(m)
                        # a message we don't know or don't care about
                        if parsed is None:
                            continue
                        handler = handlers.get(parsed['command']['command'])
                        if handler is not None:
                            asyncio.ensure_future(handler(parsed))
                elif message.type == aiohttp.WSMsgType.CLOSED:
                    self.logger.debug('websocket is closing')
                    if self.__running:
                        try:
                            await self._handle_base_reconnect()
                        except TwitchBackendException:
                            self.logger.exception('Connection to chat websocket lost and unable to reestablish connection!')
                            break
                    else:
                        break
                elif message.type == aiohttp.WSMsgType.ERROR:
                    self.logger.warning('error in websocket: ' + str(self.__connection.exception()))
                    break
        except CancelledError:
            # we are closing down!
            # print('we are closing down!')
            return

    async def _handle_base_reconnect(self):
        await self.__connect(is_startup=False)
        await self.__task_startup()

    # noinspection PyUnusedLocal
    async def _handle_reconnect(self, parsed: dict):
        self.logger.info('got reconnect request...')
        await self._handle_base_reconnect()
        self.logger.info('reconnect completed')

    async def _handle_whisper(self, parsed: dict):
        e = WhisperEvent(self, parsed)
        for handler in self._event_handler.get(ChatEvent.WHISPER, []):
            t = asyncio.ensure_future(handler(e), loop=self._callback_loop)
            t.add_done_callback(self._task_callback)

    async def _handle_clear_chat(self, parsed: dict):
        e = ClearChatEvent(self, parsed)
        for handler in self._event_handler.get(ChatEvent.CHAT_CLEARED, []):
            t = asyncio.ensure_future(handler(e), loop=self._callback_loop)
            t.add_done_callback(self._task_callback)

    async def _handle_notice(self, parsed: dict):
        e = NoticeEvent(self, parsed)
        for handler in self._event_handler.get(ChatEvent.NOTICE, []):
            t = asyncio.ensure_future(handler(e), loop=self._callback_loop)
            t.add_done_callback(self._task_callback)
        self.logger.debug(f'got NOTICE for channel {parsed["command"]["channel"]}: {parsed["tags"].get("msg-id")}')

    async def _handle_clear_msg(self, parsed: dict):
        ev = MessageDeletedEvent(self, parsed)
        for handler in self._event_handler.get(ChatEvent.MESSAGE_DELETE, []):
            t = asyncio.ensure_future(handler(ev), loop=self._callback_loop)
            t.add_done_callback(self._task_callback)

    async def _handle_cap_reply(self, parsed: dict):
        self.logger.debug(f'got CAP reply, granted caps: {parsed["parameters"]}')
        caps = parsed['parameters'].split()
        if not all([x in caps for x in ['twitch.tv/membership', 'twitch.tv/tags', 'twitch.tv/commands']]):
            self.logger.warning(f'chat bot did not get all requested capabilities granted, this might result in weird bot behavior!')

    async def _handle_join(self, parsed: dict):
        ch = parsed['command']['channel'][1:]
        nick = parsed['source']['nick'][1:]
        if ch in self._room_join_locks and nick == self.username:
            self._room_join_locks.remove(ch)
        if nick == self.username:
            e = JoinedEvent(self, ch, nick)
            for handler in self._event_handler.get(ChatEvent.JOINED, []):
                t = asyncio.ensure_future(handler(e), loop=self._callback_loop)
                t.add_done_callback(self._task_callback)
        else:
            e = JoinEvent(self, ch, nick)
            for handler in self._event_handler.get(ChatEvent.JOIN, []):
                t = asyncio.ensure_future(handler(e), loop=self._callback_loop)
                t.add_done_callback(self._task_callback)

    async def _handle_part(self, parsed: dict):
        ch = parsed['command']['channel'][1:]
        usr = parsed['source']['nick'][1:]
        if usr == self.username:
            if ch in self._room_leave_locks:
                self._room_leave_locks.remove(ch)
            room = self.room_cache.pop(ch, None)
            e = LeftEvent(self, ch, room, usr)
            for handler in self._event_handler.get(ChatEvent.LEFT, []):
                t = asyncio.ensure_future(handler(e), loop=self._callback_loop)
                t.add_done_callback(self._task_callback)
        else:
            room = self.room_cache.get(ch)
            e = LeftEvent(self, ch, room, usr)
            for handler in self._event_handler.get(ChatEvent.USER_LEFT, []):
                t = asyncio.ensure_future(handler(e), loop=self._callback_loop)
                t.add_done_callback(self._task_callback)

    async def _handle_user_notice(self, parsed: dict):
        if parsed['tags'].get('msg-id') == 'raid':
            handlers = self._event_handler.get(ChatEvent.RAID, [])
            for handler in handlers:
                asyncio.ensure_future(handler(parsed))
        elif parsed['tags'].get('msg-id') in ('sub', 'resub', 'subgift'):
            sub = ChatSub(self, parsed)
            for handler in self._event_handler.get(ChatEvent.SUB, []):
                t = asyncio.ensure_future(handler(sub), loop=self._callback_loop)
                t.add_done_callback(self._task_callback)

    async def _handle_room_state(self, parsed: dict):
        self.logger.debug('got room state event')
        state = ChatRoom(
            name=parsed['command']['channel'][1:],
            is_emote_only=parsed['tags'].get('emote-only') == '1',
            is_subs_only=parsed['tags'].get('subs-only') == '1',
            is_followers_only=parsed['tags'].get('followers-only') != '-1',
            is_unique_only=parsed['tags'].get('r9k') == '1',
            follower_only_delay=int(parsed['tags'].get('followers-only', '-1')),
            room_id=parsed['tags'].get('room-id'),
            slow=int(parsed['tags'].get('slow', '0')))
        prev = self.room_cache.get(state.name)
        # create copy
        if prev is not None:
            prev = dataclasses.replace(prev)
        self.room_cache[state.name] = state
        dat = RoomStateChangeEvent(self, prev, state)
        for handler in self._event_handler.get(ChatEvent.ROOM_STATE_CHANGE, []):
            t = asyncio.ensure_future(handler(dat), loop=self._callback_loop)
            t.add_done_callback(self._task_callback)

    async def _handle_user_state(self, parsed: dict):
        self.logger.debug('got user state event')
        is_broadcaster = False
        if parsed['tags'].get('badges') is not None:
            is_broadcaster = parsed['tags']['badges'].get('broadcaster') is not None
        self._mod_status_cache[parsed['command']['channel'][1:]] = 'mod' if parsed['tags']['mod'] == '1' or is_broadcaster else 'user'
        self._subscriber_status_cache[parsed['command']['channel'][1:]] = 'sub' if parsed['tags']['subscriber'] == '1' else 'non-sub'

    async def _handle_ping(self, parsed: dict):
        self.logger.debug('got PING')
        await self._send_message('PONG ' + parsed['parameters'])

    # noinspection PyUnusedLocal
    async def _handle_ready(self, parsed: dict):
        self.logger.debug('got ready event')
        dat = EventData(self)
        was_ready = self._ready
        self._ready = True
        if self._join_target is not None and len(self._join_target) > 0:
            _failed = await self.join_room(self._join_target)
            if len(_failed) > 0:
                self.logger.warning(f'failed to join the following channel of the initial following list: {", ".join(_failed)}')
            else:
                self.logger.info('done joining initial channels')
        if not was_ready:
            for h in self._event_handler.get(ChatEvent.READY, []):
                t = asyncio.ensure_future(h(dat), loop=self._callback_loop)
                t.add_done_callback(self._task_callback)

    async def _handle_msg(self, parsed: dict):
        if self.no_shared_chat_messages and "source-room-id" in parsed["tags"]:
            if parsed["tags"]["source-room-id"] != parsed["tags"].get("room-id"):
                return

        async def _can_execute_command(_com: ChatCommand, _name: str) -> bool:
            for mid in self._command_middleware + self._command_specific_middleware.get(_name, []):
                if not await mid.can_execute(command):
                    if mid.execute_blocked_handler is not None:
                        await mid.execute_blocked_handler(_com)
                    elif self.default_command_execution_blocked_handler is not None:
                        await self.default_command_execution_blocked_handler(_com)
                    return False
            return True

        self.logger.debug('got new message, call handler')
        if parsed['command'].get('bot_command') is not None:
            command_name = parsed['command'].get('bot_command').lower()
            handler = self._command_handler.get(command_name)
            if handler is not None:
                command = ChatCommand(self, parsed)
                # check middleware
                if await _can_execute_command(command, command_name):
                    t = asyncio.ensure_future(handler(command), loop=self._callback_loop)
                    t.add_done_callback(self._task_callback)
                    for _mid in self._command_middleware + self._command_specific_middleware.get(command_name, []):
                        await _mid.was_executed(command)
            else:
                if self.log_no_registered_command_handler:
                    self.logger.info(f'no handler registered for command "{command_name}"')
        handler = self._event_handler.get(ChatEvent.MESSAGE, [])
        message = ChatMessage(self, parsed)
        for h in handler:
            t = asyncio.ensure_future(h(message), loop=self._callback_loop)
            t.add_done_callback(self._task_callback)

    async def __task_startup(self):
        await self._send_message('CAP REQ :twitch.tv/membership twitch.tv/tags twitch.tv/commands')
        await self._send_message(f'PASS oauth:{await self.twitch.get_refreshed_user_auth_token()}')
        await self._send_message(f'NICK {self.username}')
        self.__startup_complete = True

    def _get_message_bucket(self, channel) -> RateLimitBucket:
        bucket = self._send_buckets.get(channel)
        if bucket is None:
            bucket = RateLimitBucket(30, 20, channel, self.logger)
            self._send_buckets[channel] = bucket
        target_size = RATE_LIMIT_SIZES[self._mod_status_cache.get(channel, 'user')]
        if bucket.bucket_size != target_size:
            bucket.bucket_size = target_size
        return bucket

    ##################################################################################################################################################
    # user functions
    ##################################################################################################################################################

    def set_prefix(self, prefix: str):
        """Sets a command prefix.

        The default prefix is !, the prefix can not start with / or .

        :param prefix: the new prefix to use for command parsing
        :raises ValueError: when the given prefix is None or starts with / or .
        """
        if prefix is None or prefix[0] in ('/', '.'):
            raise ValueError('Prefix starting with / or . are reserved for twitch internal use')
        self._prefix = prefix

    def set_channel_prefix(self, prefix: str, channel: Union[CHATROOM_TYPE, List[CHATROOM_TYPE]]):
        """Sets a command prefix for the given channel or channels

        The default channel prefix is either ! or the one set by :const:`~twitchAPI.chat.Chat.set_prefix()`, the prefix can not start with / or .

        :param prefix: the new prefix to use for commands in the given channels
        :param channel: the channel or channels you want the given command prefix to be used in
        :raises ValueError: when the given prefix is None or starts with / or .
        """
        if prefix is None or prefix[0] in ('/', '.'):
            raise ValueError('Prefix starting with / or . are reserved for twitch internal use')
        if not isinstance(channel, List):
            channel = [channel]
        for ch in channel:
            if isinstance(ch, ChatRoom):
                ch = ch.name
            self._channel_command_prefix[ch] = prefix

    def reset_channel_prefix(self, channel: Union[CHATROOM_TYPE, List[CHATROOM_TYPE]]):
        """Resets the custom command prefix set by :const:`~twitchAPI.chat.Chat.set_channel_prefix()` back to the global one.

        :param channel: The channel or channels you want to reset the channel command prefix for
        """
        if not isinstance(channel, List):
            channel = [channel]
        for ch in channel:
            if isinstance(ch, ChatRoom):
                ch = ch.name
            self._channel_command_prefix.pop(ch, None)

    def register_command(self, name: str, handler: COMMAND_CALLBACK_TYPE, command_middleware: Optional[List['BaseCommandMiddleware']] = None) -> bool:
        """Register a command

        :param name: the name of the command
        :param handler: The event handler
        :param command_middleware: a optional list of middleware to use just for this command
        :raises ValueError: if handler is not a coroutine"""
        if not asyncio.iscoroutinefunction(handler):
            raise ValueError('handler needs to be a async function which takes one parameter')
        name = name.lower()
        if self._command_handler.get(name) is not None:
            return False
        self._command_handler[name] = handler
        if command_middleware is not None:
            self._command_specific_middleware[name] = command_middleware
        return True

    def unregister_command(self, name: str) -> bool:
        """Unregister a already registered command.

        :param name: the name of the command to unregister
        :return: True if the command was unregistered, otherwise false
        """
        name = name.lower()
        if self._command_handler.get(name) is None:
            return False
        self._command_handler.pop(name, None)
        return True

    def register_event(self, event: ChatEvent, handler: EVENT_CALLBACK_TYPE):
        """Register a event handler

        :param event: The Event you want to register the handler to
        :param handler: The handler you want to register.
        :raises ValueError: if handler is not a coroutine"""
        if not asyncio.iscoroutinefunction(handler):
            raise ValueError('handler needs to be a async function which takes one parameter')
        if self._event_handler.get(event) is None:
            self._event_handler[event] = [handler]
        else:
            self._event_handler[event].append(handler)

    def unregister_event(self, event: ChatEvent, handler: EVENT_CALLBACK_TYPE) -> bool:
        """Unregister a handler from a event

        :param event: The Event you want to unregister your handler from
        :param handler: The handler you want to unregister
        :return: Returns true when the handler was removed from the event, otherwise false
        """
        if self._event_handler.get(event) is None or handler not in self._event_handler.get(event):
            return False
        self._event_handler[event].remove(handler)
        return True

    def is_connected(self) -> bool:
        """Returns your current connection status."""
        if self.__connection is None:
            return False
        return not self.__connection.closed

    def is_ready(self) -> bool:
        """Returns True if the chat bot is ready to join channels and/or receive events"""
        return self._ready

    def is_mod(self, room: CHATROOM_TYPE) -> bool:
        """Check if chat bot is a mod in a channel

        :param room: The chat room you want to check if bot is a mod in.
            This can either be a instance of :const:`~twitchAPI.type.ChatRoom` or a string with the room name (either with leading # or without)
        :return: Returns True if chat bot is a mod """
        if isinstance(room, ChatRoom):
            room = room.name
        if room is None or len(room) == 0:
            raise ValueError('please specify a room')
        if room[0] == '#':
            room = room[1:]
        return self._mod_status_cache.get(room.lower(), 'user') == 'mod'

    def is_subscriber(self, room: CHATROOM_TYPE) -> bool:
        """Check if chat bot is a subscriber in a channel

        :param room: The chat room you want to check if bot is a subscriber in.
            This can either be a instance of :const:`~twitchAPI.type.ChatRoom` or a string with the room name (either with leading # or without)
        :return: Returns True if chat bot is a subscriber """
        if isinstance(room, ChatRoom):
            room = room.name
        if room is None or len(room) == 0:
            raise ValueError('please specify a room')
        if room[0] == '#':
            room = room[1:]
        return self._subscriber_status_cache.get(room.lower(), 'user') == 'sub'

    def is_in_room(self, room: CHATROOM_TYPE) -> bool:
        """Check if the bot is currently in the given chat room

        :param room: The chat room you want to check
            This can either be a instance of :const:`~twitchAPI.type.ChatRoom` or a string with the room name (either with leading # or without)
        """
        if isinstance(room, ChatRoom):
            room = room.name
        if room is None or len(room) == 0:
            raise ValueError('please specify a room')
        if room[0] == '#':
            room = room[1:]
        return self.room_cache.get(room.lower()) is not None

    async def join_room(self, chat_rooms: Union[List[str], str]):
        """ join one or more chat rooms\n
        Will only exit once all given chat rooms where successfully joined or :const:`twitchAPI.chat.Chat.join_timeout` run out.

        :param chat_rooms: the Room or rooms you want to join
        :returns: list of channels that could not be joined
        """
        if isinstance(chat_rooms, str):
            chat_rooms = [chat_rooms]
        target = [c[1:].lower() if c[0] == '#' else c.lower() for c in chat_rooms]
        for r in target:
            self._room_join_locks.append(r)
        if len(target) > self._join_bucket.left():
            # we want to join more than the current bucket has left, join slowly one after another
            # TODO we could join the current remaining bucket size in blocks
            for r in target:
                await self._join_bucket.put()
                await self._send_message(f'JOIN #{r}')
        else:
            # enough space in the current bucket left, join all at once
            await self._join_bucket.put(len(target))
            await self._send_message(f'JOIN {",".join([f"#{x}" for x in target])}')
        # wait for us to join all rooms
        timeout = datetime.datetime.now() + datetime.timedelta(seconds=self.join_timeout)
        while any([r in self._room_join_locks for r in target]) and timeout > datetime.datetime.now():
            await asyncio.sleep(0.01)
        failed_to_join = [r for r in self._room_join_locks if r in target]
        self._join_target.extend([x for x in target if x not in failed_to_join])
        # deduplicate join target
        self._join_target = list(set(self._join_target))
        for r in failed_to_join:
            self._room_join_locks.remove(r)
        return failed_to_join

    async def send_raw_irc_message(self, message: str):
        """Send a raw IRC message

        :param message: the message to send
        :raises ValueError: if bot is not ready
        """
        if not self.is_ready():
            raise ValueError('can\'t send message: bot not ready')
        while not self.is_connected():
            await asyncio.sleep(0.1)
        if message is None or len(message) == 0:
            raise ValueError('message must be a non empty string')
        await self._send_message(message)

    async def send_message(self, room: CHATROOM_TYPE, text: str):
        """Send a message to the given channel

        Please note that you first need to join a channel before you can send a message to it.

        :param room: The chat room you want to send the message to.
            This can either be a instance of :const:`~twitchAPI.type.ChatRoom` or a string with the room name (either with leading # or without)
        :param text: The text you want to send
        :raises ValueError: if message is empty or room is not given
        :raises ValueError: if bot is not ready
        """
        if not self.is_ready():
            raise ValueError('can\'t send message: bot not ready')
        while not self.is_connected():
            await asyncio.sleep(0.1)
        if isinstance(room, ChatRoom):
            room = room.name
        if room is None or len(room) == 0:
            raise ValueError('please specify a room to post to')
        if text is None or len(text) == 0:
            raise ValueError('you can\'t send a empty message')
        if room[0] != '#':
            room = f'#{room}'.lower()
        bucket = self._get_message_bucket(room[1:])
        await bucket.put()
        await self._send_message(f'PRIVMSG {room} :{text}')

    async def leave_room(self, chat_rooms: Union[List[str], str]):
        """leave one or more chat rooms\n
        Will only exit once all given chat rooms where successfully left

        :param chat_rooms: The room or rooms you want to leave"""
        if isinstance(chat_rooms, str):
            chat_rooms = [chat_rooms]
        room_str = ','.join([f'#{c}'.lower() if c[0] != '#' else c.lower() for c in chat_rooms])
        target = [c[1:].lower() if c[0] == '#' else c.lower() for c in chat_rooms]
        for r in target:
            self._room_leave_locks.append(r)
        await self._send_message(f'PART {room_str}')
        for x in target:
            if x in self._join_target:
                self._join_target.remove(x)
        # wait to leave all rooms
        while any([r in self._room_leave_locks for r in target]):
            await asyncio.sleep(0.01)

    def register_command_middleware(self, mid: 'BaseCommandMiddleware'):
        """Adds the given command middleware as a general middleware"""
        if mid not in self._command_middleware:
            self._command_middleware.append(mid)

    def unregister_command_middleware(self, mid: 'BaseCommandMiddleware'):
        """Removes the given command middleware from the general list"""
        if mid in self._command_middleware:
            self._command_middleware.remove(mid)

==> ./chat/middleware.py <==
#  Copyright (c) 2023. Lena "Teekeks" During <info@teawork.de>
"""
Chat Command Middleware
-----------------------

A selection of preimplemented chat command middleware.

.. note:: See :doc:`/tutorial/chat-use-middleware` for a more detailed walkthough on how to use these.

Available Middleware
====================

.. list-table::
   :header-rows: 1

   * - Middleware
     - Description
   * - :const:`~twitchAPI.chat.middleware.ChannelRestriction`
     - Filters in which channels a command can be executed in.
   * - :const:`~twitchAPI.chat.middleware.UserRestriction`
     - Filters which users can execute a command.
   * - :const:`~twitchAPI.chat.middleware.StreamerOnly`
     - Restricts the use of commands to only the streamer in their channel.
   * - :const:`~twitchAPI.chat.middleware.ChannelCommandCooldown`
     - Restricts a command to only be executed once every :const:`cooldown_seconds` in a channel regardless of user.
   * - :const:`~twitchAPI.chat.middleware.ChannelUserCommandCooldown`
     - Restricts a command to be only executed once every :const:`cooldown_seconds` in a channel by a user.
   * - :const:`~twitchAPI.chat.middleware.GlobalCommandCooldown`
     - Restricts a command to be only executed once every :const:`cooldown_seconds` in any channel.


Class Documentation
===================

"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING, Callable, Awaitable, Dict

if TYPE_CHECKING:
    from twitchAPI.chat import ChatCommand


__all__ = ['BaseCommandMiddleware', 'ChannelRestriction', 'UserRestriction', 'StreamerOnly',
           'ChannelCommandCooldown', 'ChannelUserCommandCooldown', 'GlobalCommandCooldown', 'SharedChatOnlyCurrent']


class BaseCommandMiddleware(ABC):
    """The base for chat command middleware, extend from this when implementing your own"""

    execute_blocked_handler: Optional[Callable[['ChatCommand'], Awaitable[None]]] = None
    """If set, this handler will be called should :const:`~twitchAPI.chat.middleware.BaseCommandMiddleware.can_execute()` fail."""

    @abstractmethod
    async def can_execute(self, command: 'ChatCommand') -> bool:
        """
        return :code:`True` if the given command should execute, otherwise :code:`False`

        :param command: The command to check if it should be executed"""
        pass

    @abstractmethod
    async def was_executed(self, command: 'ChatCommand'):
        """Will be called when a command was executed, use to update internal state"""
        pass


class ChannelRestriction(BaseCommandMiddleware):
    """Filters in which channels a command can be executed in"""

    def __init__(self,
                 allowed_channel: Optional[List[str]] = None,
                 denied_channel: Optional[List[str]] = None,
                 execute_blocked_handler: Optional[Callable[['ChatCommand'], Awaitable[None]]] = None):
        """
        :param allowed_channel: if provided, the command can only be used in channels on this list
        :param denied_channel:  if provided, the command can't be used in channels on this list
        :param execute_blocked_handler: optional specific handler for when the execution is blocked
        """
        self.execute_blocked_handler = execute_blocked_handler
        self.allowed = allowed_channel if allowed_channel is not None else []
        self.denied = denied_channel if denied_channel is not None else []

    async def can_execute(self, command: 'ChatCommand') -> bool:
        if len(self.allowed) > 0:
            if command.room.name not in self.allowed:
                return False
        return command.room.name not in self.denied

    async def was_executed(self, command: 'ChatCommand'):
        pass


class UserRestriction(BaseCommandMiddleware):
    """Filters which users can execute a command"""

    def __init__(self,
                 allowed_users: Optional[List[str]] = None,
                 denied_users: Optional[List[str]] = None,
                 execute_blocked_handler: Optional[Callable[['ChatCommand'], Awaitable[None]]] = None):
        """
        :param allowed_users: if provided, the command can only be used by one of the provided users
        :param denied_users: if provided, the command can not be used by any of the provided users
        :param execute_blocked_handler: optional specific handler for when the execution is blocked
        """
        self.execute_blocked_handler = execute_blocked_handler
        self.allowed = allowed_users if allowed_users is not None else []
        self.denied = denied_users if denied_users is not None else []

    async def can_execute(self, command: 'ChatCommand') -> bool:
        if len(self.allowed) > 0:
            if command.user.name not in self.allowed:
                return False
        return command.user.name not in self.denied

    async def was_executed(self, command: 'ChatCommand'):
        pass


class StreamerOnly(BaseCommandMiddleware):
    """Restricts the use of commands to only the streamer in their channel"""

    def __init__(self, execute_blocked_handler: Optional[Callable[['ChatCommand'], Awaitable[None]]] = None):
        """
        :param execute_blocked_handler: optional specific handler for when the execution is blocked
        """
        self.execute_blocked_handler = execute_blocked_handler

    async def can_execute(self, command: 'ChatCommand') -> bool:
        return command.room.name == command.user.name

    async def was_executed(self, command: 'ChatCommand'):
        pass


class ChannelCommandCooldown(BaseCommandMiddleware):
    """Restricts a command to only be executed once every :const:`cooldown_seconds` in a channel regardless of user."""

    # command -> channel -> datetime
    _last_executed: Dict[str, Dict[str, datetime]] = {}

    def __init__(self,
                 cooldown_seconds: int,
                 execute_blocked_handler: Optional[Callable[['ChatCommand'], Awaitable[None]]] = None):
        """
        :param cooldown_seconds: time in seconds a command should not be used again
        :param execute_blocked_handler: optional specific handler for when the execution is blocked
        """
        self.execute_blocked_handler = execute_blocked_handler
        self.cooldown = cooldown_seconds

    async def can_execute(self, command: 'ChatCommand') -> bool:
        if self._last_executed.get(command.name) is None:
            return True
        last_executed = self._last_executed[command.name].get(command.room.name)
        if last_executed is None:
            return True
        since = (datetime.now() - last_executed).total_seconds()
        return since >= self.cooldown

    async def was_executed(self, command: 'ChatCommand'):
        if self._last_executed.get(command.name) is None:
            self._last_executed[command.name] = {}
            self._last_executed[command.name][command.room.name] = datetime.now()
            return
        self._last_executed[command.name][command.room.name] = datetime.now()


class ChannelUserCommandCooldown(BaseCommandMiddleware):
    """Restricts a command to be only executed once every :const:`cooldown_seconds` in a channel by a user."""

    # command -> channel -> user -> datetime
    _last_executed: Dict[str, Dict[str, Dict[str, datetime]]] = {}

    def __init__(self,
                 cooldown_seconds: int,
                 execute_blocked_handler: Optional[Callable[['ChatCommand'], Awaitable[None]]] = None):
        """
        :param cooldown_seconds: time in seconds a command should not be used again
        :param execute_blocked_handler: optional specific handler for when the execution is blocked
        """
        self.execute_blocked_handler = execute_blocked_handler
        self.cooldown = cooldown_seconds

    async def can_execute(self, command: 'ChatCommand') -> bool:
        if self._last_executed.get(command.name) is None:
            return True
        if self._last_executed[command.name].get(command.room.name) is None:
            return True
        last_executed = self._last_executed[command.name][command.room.name].get(command.user.name)
        if last_executed is None:
            return True
        since = (datetime.now() - last_executed).total_seconds()
        return since >= self.cooldown

    async def was_executed(self, command: 'ChatCommand'):
        if self._last_executed.get(command.name) is None:
            self._last_executed[command.name] = {}
            self._last_executed[command.name][command.room.name] = {}
            self._last_executed[command.name][command.room.name][command.user.name] = datetime.now()
            return
        if self._last_executed[command.name].get(command.room.name) is None:
            self._last_executed[command.name][command.room.name] = {}
            self._last_executed[command.name][command.room.name][command.user.name] = datetime.now()
            return
        self._last_executed[command.name][command.room.name][command.user.name] = datetime.now()


class GlobalCommandCooldown(BaseCommandMiddleware):
    """Restricts a command to be only executed once every :const:`cooldown_seconds` in any channel"""

    # command -> datetime
    _last_executed: Dict[str, datetime] = {}

    def __init__(self,
                 cooldown_seconds: int,
                 execute_blocked_handler: Optional[Callable[['ChatCommand'], Awaitable[None]]] = None):
        """
        :param cooldown_seconds: time in seconds a command should not be used again
        :param execute_blocked_handler: optional specific handler for when the execution is blocked
        """
        self.execute_blocked_handler = execute_blocked_handler
        self.cooldown = cooldown_seconds

    async def can_execute(self, command: 'ChatCommand') -> bool:
        if self._last_executed.get(command.name) is None:
            return True
        since = (datetime.now() - self._last_executed[command.name]).total_seconds()
        return since >= self.cooldown

    async def was_executed(self, command: 'ChatCommand'):
        self._last_executed[command.name] = datetime.now()


class SharedChatOnlyCurrent(BaseCommandMiddleware):
    """Restricts commands to only current chat room in Shared Chat streams"""

    async def can_execute(self, command: 'ChatCommand') -> bool:
        if command.source_room_id != command.room.room_id:
            return False
        return True

    async def was_executed(self, command: 'ChatCommand'):
        pass

==> ./eventsub/__init__.py <==
#  Copyright (c) 2023. Lena "Teekeks" During <info@teawork.de>
"""
EventSub
--------

EventSub lets you listen for events that happen on Twitch.

All available EventSub clients runs in their own thread, calling the given callback function whenever an event happens.

Look at :ref:`eventsub-available-topics` to find the topics you are interested in.

Available Transports
====================

EventSub is available with different types of transports, used for different applications.

.. list-table::
   :header-rows: 1

   * - Transport Method
     - Use Case
     - Auth Type
   * - :doc:`twitchAPI.eventsub.webhook`
     - Server / Multi User
     - App Authentication
   * - :doc:`twitchAPI.eventsub.websocket`
     - Client / Single User
     - User Authentication


.. _eventsub-available-topics:

Available Topics and Callback Payloads
======================================

List of available EventSub Topics.

The Callback Payload is the type of the parameter passed to the callback function you specified in :const:`listen_`.

.. list-table::
   :header-rows: 1

   * - Topic
     - Subscription Function & Callback Payload
     - Description
   * - **Channel Update** v1
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_update()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelUpdateEvent`
     - A broadcaster updates their channel properties e.g., category, title, mature flag, broadcast, or language.
   * - **Channel Update** v2
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_update_v2()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelUpdateEvent`
     - A broadcaster updates their channel properties e.g., category, title, content classification labels, broadcast, or language.
   * - **Channel Follow** v2
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_follow_v2()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelFollowEvent`
     - A specified channel receives a follow.
   * - **Channel Subscribe**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_subscribe()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelSubscribeEvent`
     - A notification when a specified channel receives a subscriber. This does not include resubscribes.
   * - **Channel Subscription End**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_end()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelSubscriptionEndEvent`
     - A notification when a subscription to the specified channel ends.
   * - **Channel Subscription Gift**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_gift()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelSubscriptionGiftEvent`
     - A notification when a viewer gives a gift subscription to one or more users in the specified channel.
   * - **Channel Subscription Message**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_subscription_message()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelSubscriptionMessageEvent`
     - A notification when a user sends a resubscription chat message in a specific channel.
   * - **Channel Cheer**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_cheer()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelCheerEvent`
     - A user cheers on the specified channel.
   * - **Channel Raid**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_raid()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelRaidEvent`
     - A broadcaster raids another broadcaster’s channel.
   * - **Channel Ban**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_ban()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelBanEvent`
     - A viewer is banned from the specified channel.
   * - **Channel Unban**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_unban()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelUnbanEvent`
     - A viewer is unbanned from the specified channel.
   * - **Channel Moderator Add**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderator_add()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelModeratorAddEvent`
     - Moderator privileges were added to a user on a specified channel.
   * - **Channel Moderator Remove**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderator_remove()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelModeratorRemoveEvent`
     - Moderator privileges were removed from a user on a specified channel.
   * - **Channel Points Custom Reward Add**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_add()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelPointsCustomRewardAddEvent`
     - A custom channel points reward has been created for the specified channel.
   * - **Channel Points Custom Reward Update**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_update()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelPointsCustomRewardUpdateEvent`
     - A custom channel points reward has been updated for the specified channel.
   * - **Channel Points Custom Reward Remove**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_remove()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelPointsCustomRewardRemoveEvent`
     - A custom channel points reward has been removed from the specified channel.
   * - **Channel Points Custom Reward Redemption Add**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_add()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelPointsCustomRewardRedemptionAddEvent`
     - A viewer has redeemed a custom channel points reward on the specified channel.
   * - **Channel Points Custom Reward Redemption Update**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_custom_reward_redemption_update()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelPointsCustomRewardRedemptionUpdateEvent`
     - A redemption of a channel points custom reward has been updated for the specified channel.
   * - **Channel Poll Begin**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_begin()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelPollBeginEvent`
     - A poll started on a specified channel.
   * - **Channel Poll Progress**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_progress()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelPollProgressEvent`
     - Users respond to a poll on a specified channel.
   * - **Channel Poll End**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_poll_end()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelPollEndEvent`
     - A poll ended on a specified channel.
   * - **Channel Prediction Begin**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_begin()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelPredictionEvent`
     - A Prediction started on a specified channel.
   * - **Channel Prediction Progress**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_progress()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelPredictionEvent`
     - Users participated in a Prediction on a specified channel.
   * - **Channel Prediction Lock**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_lock()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelPredictionEvent`
     - A Prediction was locked on a specified channel.
   * - **Channel Prediction End**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_prediction_end()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelPredictionEndEvent`
     - A Prediction ended on a specified channel.
   * - **Drop Entitlement Grant**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_drop_entitlement_grant()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.DropEntitlementGrantEvent`
     - An entitlement for a Drop is granted to a user.
   * - **Extension Bits Transaction Create**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_extension_bits_transaction_create()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ExtensionBitsTransactionCreateEvent`
     - A Bits transaction occurred for a specified Twitch Extension.
   * - **Goal Begin**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_goal_begin()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.GoalEvent`
     - A goal begins on the specified channel.
   * - **Goal Progress**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_goal_progress()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.GoalEvent`
     - A goal makes progress on the specified channel.
   * - **Goal End**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_goal_end()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.GoalEvent`
     - A goal ends on the specified channel.
   * - **Hype Train Begin**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_hype_train_begin()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.HypeTrainEvent`
     - A Hype Train begins on the specified channel.
   * - **Hype Train Progress**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_hype_train_progress()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.HypeTrainEvent`
     - A Hype Train makes progress on the specified channel.
   * - **Hype Train End**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_hype_train_end()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.HypeTrainEvent`
     - A Hype Train ends on the specified channel.
   * - **Stream Online**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_stream_online()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.StreamOnlineEvent`
     - The specified broadcaster starts a stream.
   * - **Stream Offline**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_stream_offline()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.StreamOfflineEvent`
     - The specified broadcaster stops a stream.
   * - **User Authorization Grant**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_user_authorization_grant()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.UserAuthorizationGrantEvent`
     - A user’s authorization has been granted to your client id.
   * - **User Authorization Revoke**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_user_authorization_revoke()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.UserAuthorizationRevokeEvent`
     - A user’s authorization has been revoked for your client id.
   * - **User Update**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_user_update()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.UserUpdateEvent`
     - A user has updated their account.
   * - **Channel Shield Mode Begin**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_begin()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ShieldModeEvent`
     - Sends a notification when the broadcaster activates Shield Mode.
   * - **Channel Shield Mode End**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shield_mode_end()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ShieldModeEvent`
     - Sends a notification when the broadcaster deactivates Shield Mode.
   * - **Channel Charity Campaign Start**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_start()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.CharityCampaignStartEvent`
     - Sends a notification when the broadcaster starts a charity campaign.
   * - **Channel Charity Campaign Progress**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_progress()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.CharityCampaignProgressEvent`
     - Sends notifications when progress is made towards the campaign’s goal or when the broadcaster changes the fundraising goal.
   * - **Channel Charity Campaign Stop**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_stop()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.CharityCampaignStopEvent`
     - Sends a notification when the broadcaster stops a charity campaign.
   * - **Channel Charity Campaign Donate**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_charity_campaign_donate()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.CharityDonationEvent`
     - Sends a notification when a user donates to the broadcaster’s charity campaign.
   * - **Channel Shoutout Create**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_create()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelShoutoutCreateEvent`
     - Sends a notification when the specified broadcaster sends a Shoutout.
   * - **Channel Shoutout Receive**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shoutout_receive()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelShoutoutReceiveEvent`
     - Sends a notification when the specified broadcaster receives a Shoutout.
   * - **Channel Chat Clear**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelChatClearEvent`
     - A moderator or bot has cleared all messages from the chat room.
   * - **Channel Chat Clear User Messages**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_clear_user_messages()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelChatClearUserMessagesEvent`
     - A moderator or bot has cleared all messages from a specific user.
   * - **Channel Chat Message Delete**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message_delete()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelChatMessageDeleteEvent`
     - A moderator has removed a specific message.
   * - **Channel Chat Notification**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_notification()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelChatNotificationEvent`
     - A notification for when an event that appears in chat has occurred.
   * - **Channel Chat Message**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_message()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelChatMessageEvent`
     - Any user sends a message to a specific chat room.
   * - **Channel Ad Break Begin**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_ad_break_begin()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelAdBreakBeginEvent`
     - A midroll commercial break has started running.
   * - **Channel Chat Settings Update**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_settings_update()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelChatSettingsUpdateEvent`
     - A notification for when a broadcaster’s chat settings are updated.
   * - **Whisper Received**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_user_whisper_message()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.UserWhisperMessageEvent`
     - A user receives a whisper.
   * - **Channel Points Automatic Reward Redemption**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_points_automatic_reward_redemption_add()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelPointsAutomaticRewardRedemptionAddEvent`
     - A viewer has redeemed an automatic channel points reward on the specified channel.
   * - **Channel VIP Add**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_add()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelVIPAddEvent`
     - A VIP is added to the channel.
   * - **Channel VIP Remove**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_vip_remove()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelVIPRemoveEvent`
     - A VIP is removed from the channel.
   * - **Channel Unban Request Create**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_create()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelUnbanRequestCreateEvent`
     - A user creates an unban request.
   * - **Channel Unban Request Resolve**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_unban_request_resolve()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelUnbanRequestResolveEvent`
     - An unban request has been resolved.
   * - **Channel Suspicious User Message**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_message()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelSuspiciousUserMessageEvent`
     - A chat message has been sent by a suspicious user.
   * - **Channel Suspicious User Update**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_suspicious_user_update()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelSuspiciousUserUpdateEvent`
     - A suspicious user has been updated.
   * - **Channel Moderate** v2
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_moderate()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelModerateEvent`
     - A moderator performs a moderation action in a channel. Includes warnings.
   * - **Channel Warning Acknowledgement**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_acknowledge()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelWarningAcknowledgeEvent`
     - A user awknowledges a warning. Broadcasters and moderators can see the warning’s details.
   * - **Channel Warning Send**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_warning_send()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelWarningSendEvent`
     - A user is sent a warning. Broadcasters and moderators can see the warning’s details.
   * - **Automod Message Hold**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_automod_message_hold()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.AutomodMessageHoldEvent`
     - A user is notified if a message is caught by automod for review.
   * - **Automod Message Update**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_automod_message_update()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.AutomodMessageUpdateEvent`
     - A message in the automod queue had its status changed.
   * - **Automod Settings Update**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_automod_settings_update()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.AutomodSettingsUpdateEvent`
     - A notification is sent when a broadcaster’s automod settings are updated.
   * - **Automod Terms Update**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_automod_terms_update()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.AutomodTermsUpdateEvent`
     - A notification is sent when a broadcaster’s automod terms are updated. Changes to private terms are not sent.
   * - **Channel Chat User Message Hold**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_hold()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelChatUserMessageHoldEvent`
     - A user is notified if their message is caught by automod.
   * - **Channel Chat User Message Update**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_chat_user_message_update()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelChatUserMessageUpdateEvent`
     - A user is notified if their message’s automod status is updated.
   * - **Channel Shared Chat Session Begin**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_begin()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelSharedChatBeginEvent`
     - A notification when a channel becomes active in an active shared chat session.
   * - **Channel Shared Chat Session Update**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_update()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelSharedChatUpdateEvent`
     - A notification when the active shared chat session the channel is in changes.
   * - **Channel Shared Chat Session End**
     - Function: :const:`~twitchAPI.eventsub.base.EventSubBase.listen_channel_shared_chat_end()` |br|
       Payload: :const:`~twitchAPI.object.eventsub.ChannelSharedChatEndEvent`
     - A notification when a channel leaves a shared chat session or the session ends.
"""

==> ./eventsub/base.py <==
#  Copyright (c) 2021. Lena "Teekeks" During <info@teawork.de>
"""
Base EventSub Client
--------------------

.. note:: This is the base class used for all EventSub Transport implementations.

  See :doc:`twitchAPI.eventsub` for a list of all available Transports.

*******************
Class Documentation
*******************
"""
from twitchAPI.object.eventsub import (ChannelPollBeginEvent, ChannelUpdateEvent, ChannelFollowEvent, ChannelSubscribeEvent,
                                       ChannelSubscriptionEndEvent, ChannelSubscriptionGiftEvent, ChannelSubscriptionMessageEvent,
                                       ChannelCheerEvent, ChannelRaidEvent, ChannelBanEvent, ChannelUnbanEvent,
                                       ChannelModeratorAddEvent, ChannelModeratorRemoveEvent, ChannelPointsCustomRewardAddEvent,
                                       ChannelPointsCustomRewardUpdateEvent, ChannelPointsCustomRewardRemoveEvent,
                                       ChannelPointsCustomRewardRedemptionAddEvent, ChannelPointsCustomRewardRedemptionUpdateEvent,
                                       ChannelPollProgressEvent, ChannelPollEndEvent, ChannelPredictionEvent, ChannelPredictionEndEvent,
                                       DropEntitlementGrantEvent, ExtensionBitsTransactionCreateEvent, GoalEvent, HypeTrainEvent, HypeTrainEndEvent,
                                       StreamOnlineEvent, StreamOfflineEvent, UserAuthorizationGrantEvent, UserAuthorizationRevokeEvent,
                                       UserUpdateEvent, ShieldModeEvent, CharityCampaignStartEvent, CharityCampaignProgressEvent,
                                       CharityCampaignStopEvent, CharityDonationEvent, ChannelShoutoutCreateEvent, ChannelShoutoutReceiveEvent,
                                       ChannelChatClearEvent, ChannelChatClearUserMessagesEvent, ChannelChatMessageDeleteEvent,
                                       ChannelChatNotificationEvent, ChannelAdBreakBeginEvent, ChannelChatMessageEvent, ChannelChatSettingsUpdateEvent,
                                       UserWhisperMessageEvent, ChannelPointsAutomaticRewardRedemptionAddEvent, ChannelVIPAddEvent,
                                       ChannelVIPRemoveEvent, ChannelUnbanRequestCreateEvent, ChannelUnbanRequestResolveEvent,
                                       ChannelSuspiciousUserMessageEvent, ChannelSuspiciousUserUpdateEvent, ChannelModerateEvent,
                                       ChannelWarningAcknowledgeEvent, ChannelWarningSendEvent, AutomodMessageHoldEvent, AutomodMessageUpdateEvent,
                                       AutomodSettingsUpdateEvent, AutomodTermsUpdateEvent, ChannelChatUserMessageHoldEvent, ChannelChatUserMessageUpdateEvent,
                                       ChannelSharedChatBeginEvent, ChannelSharedChatUpdateEvent, ChannelSharedChatEndEvent)
from twitchAPI.helper import remove_none_values
from twitchAPI.type import TwitchAPIException
import asyncio
from logging import getLogger, Logger
from twitchAPI.twitch import Twitch
from abc import ABC, abstractmethod

from typing import Union, Callable, Optional, Awaitable

__all__ = ['EventSubBase']


class EventSubBase(ABC):
    """EventSub integration for the Twitch Helix API."""

    def __init__(self,
                 twitch: Twitch,
                 logger_name: str):
        """
        :param twitch: a app authenticated instance of :const:`~twitchAPI.twitch.Twitch`
        :param logger_name: the name of the logger to be used
        """
        self._twitch: Twitch = twitch
        self.logger: Logger = getLogger(logger_name)
        """The logger used for EventSub related log messages"""
        self._callbacks = {}

    @abstractmethod
    def start(self):
        """Starts the EventSub client

        :rtype: None
        :raises RuntimeError: if EventSub is already running
        """

    @abstractmethod
    async def stop(self):
        """Stops the EventSub client

        This also unsubscribes from all known subscriptions if unsubscribe_on_stop is True

        :rtype: None
        """

    @abstractmethod
    def _get_transport(self):
        pass

    # ==================================================================================================================
    # HELPER
    # ==================================================================================================================

    @abstractmethod
    async def _build_request_header(self):
        pass

    async def _api_post_request(self, session, url: str, data: Union[dict, None] = None):
        headers = await self._build_request_header()
        return await session.post(url, headers=headers, json=data)

    def _add_callback(self, c_id: str, callback, event):
        self._callbacks[c_id] = {'id': c_id, 'callback': callback, 'active': False, 'event': event}

    async def _activate_callback(self, c_id: str):
        if c_id not in self._callbacks:
            self.logger.debug(f'callback for {c_id} arrived before confirmation, waiting...')
        while c_id not in self._callbacks:
            await asyncio.sleep(0.1)
        self._callbacks[c_id]['active'] = True

    @abstractmethod
    async def _subscribe(self, sub_type: str, sub_version: str, condition: dict, callback, event, is_batching_enabled: Optional[bool] = None) -> str:
        pass

    # ==================================================================================================================
    # HANDLERS
    # ==================================================================================================================

    async def unsubscribe_all(self):
        """Unsubscribe from all subscriptions"""
        ret = await self._twitch.get_eventsub_subscriptions()
        async for d in ret:
            try:
                await self._twitch.delete_eventsub_subscription(d.id)
            except TwitchAPIException as e:
                self.logger.warning(f'failed to unsubscribe from event {d.id}: {str(e)}')
        self._callbacks.clear()

    async def unsubscribe_all_known(self):
        """Unsubscribe from all subscriptions known to this client."""
        for key, value in self._callbacks.items():
            self.logger.debug(f'unsubscribe from event {key}')
            try:
                await self._twitch.delete_eventsub_subscription(key)
            except TwitchAPIException as e:
                self.logger.warning(f'failed to unsubscribe from event {key}: {str(e)}')
        self._callbacks.clear()

    @abstractmethod
    async def _unsubscribe_hook(self, topic_id: str) -> bool:
        pass

    async def unsubscribe_topic(self, topic_id: str) -> bool:
        """Unsubscribe from a specific topic."""
        try:
            await self._twitch.delete_eventsub_subscription(topic_id)
            self._callbacks.pop(topic_id, None)
            return await self._unsubscribe_hook(topic_id)
        except TwitchAPIException as e:
            self.logger.warning(f'failed to unsubscribe from {topic_id}: {str(e)}')
        return False

    async def listen_channel_update(self, broadcaster_user_id: str, callback: Callable[[ChannelUpdateEvent], Awaitable[None]]) -> str:
        """A broadcaster updates their channel properties e.g., category, title, mature flag, broadcast, or language.

        No Authentication required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelupdate

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.update', '1', {'broadcaster_user_id': broadcaster_user_id}, callback,
                                     ChannelUpdateEvent)

    async def listen_channel_update_v2(self, broadcaster_user_id: str, callback: Callable[[ChannelUpdateEvent], Awaitable[None]]) -> str:
        """A broadcaster updates their channel properties e.g., category, title, content classification labels or language.

        No Authentication required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelupdate

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.update', '2', {'broadcaster_user_id': broadcaster_user_id}, callback,
                                     ChannelUpdateEvent)

    async def listen_channel_follow_v2(self,
                                       broadcaster_user_id: str,
                                       moderator_user_id: str,
                                       callback: Callable[[ChannelFollowEvent], Awaitable[None]]) -> str:
        """A specified channel receives a follow.

        User Authentication with :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_FOLLOWERS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelfollow

        :param broadcaster_user_id: the id of the user you want to listen to
        :param moderator_user_id: The ID of the moderator of the channel you want to get follow notifications for.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.follow',
                                     '2',
                                     {'broadcaster_user_id': broadcaster_user_id, 'moderator_user_id': moderator_user_id},
                                     callback,
                                     ChannelFollowEvent)

    async def listen_channel_subscribe(self, broadcaster_user_id: str, callback: Callable[[ChannelSubscribeEvent], Awaitable[None]]) -> str:
        """A notification when a specified channel receives a subscriber. This does not include resubscribes.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_SUBSCRIPTIONS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelsubscribe

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.subscribe', '1', {'broadcaster_user_id': broadcaster_user_id}, callback,
                                     ChannelSubscribeEvent)

    async def listen_channel_subscription_end(self,
                                              broadcaster_user_id: str,
                                              callback: Callable[[ChannelSubscriptionEndEvent], Awaitable[None]]) -> str:
        """A notification when a subscription to the specified channel ends.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_SUBSCRIPTIONS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelsubscriptionend

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.subscription.end', '1', {'broadcaster_user_id': broadcaster_user_id},
                                     callback, ChannelSubscriptionEndEvent)

    async def listen_channel_subscription_gift(self,
                                               broadcaster_user_id: str,
                                               callback: Callable[[ChannelSubscriptionGiftEvent], Awaitable[None]]) -> str:
        """A notification when a viewer gives a gift subscription to one or more users in the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_SUBSCRIPTIONS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelsubscriptiongift

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.subscription.gift', '1', {'broadcaster_user_id': broadcaster_user_id},
                                     callback, ChannelSubscriptionGiftEvent)

    async def listen_channel_subscription_message(self,
                                                  broadcaster_user_id: str,
                                                  callback: Callable[[ChannelSubscriptionMessageEvent], Awaitable[None]]) -> str:
        """A notification when a user sends a resubscription chat message in a specific channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_SUBSCRIPTIONS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelsubscriptionmessage

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.subscription.message',
                                     '1',
                                     {'broadcaster_user_id': broadcaster_user_id},
                                     callback,
                                     ChannelSubscriptionMessageEvent)

    async def listen_channel_cheer(self, broadcaster_user_id: str, callback: Callable[[ChannelCheerEvent], Awaitable[None]]) -> str:
        """A user cheers on the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.BITS_READ` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelcheer

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.cheer',
                                     '1',
                                     {'broadcaster_user_id': broadcaster_user_id},
                                     callback,
                                     ChannelCheerEvent)

    async def listen_channel_raid(self,
                                  callback: Callable[[ChannelRaidEvent], Awaitable[None]],
                                  to_broadcaster_user_id: Optional[str] = None,
                                  from_broadcaster_user_id: Optional[str] = None) -> str:
        """A broadcaster raids another broadcaster’s channel.

        No authorization required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelraid

        :param from_broadcaster_user_id: The broadcaster user ID that created the channel raid you want to get notifications for.
        :param to_broadcaster_user_id: The broadcaster user ID that received the channel raid you want to get notifications for.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.raid',
                                     '1',
                                     remove_none_values({
                                         'from_broadcaster_user_id': from_broadcaster_user_id,
                                         'to_broadcaster_user_id': to_broadcaster_user_id}),
                                     callback,
                                     ChannelRaidEvent)

    async def listen_channel_ban(self, broadcaster_user_id: str, callback: Callable[[ChannelBanEvent], Awaitable[None]]) -> str:
        """A viewer is banned from the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MODERATE` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelban

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.ban',
                                     '1',
                                     {'broadcaster_user_id': broadcaster_user_id},
                                     callback,
                                     ChannelBanEvent)

    async def listen_channel_unban(self, broadcaster_user_id: str, callback: Callable[[ChannelUnbanEvent], Awaitable[None]]) -> str:
        """A viewer is unbanned from the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_MODERATE` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelunban

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.unban',
                                     '1',
                                     {'broadcaster_user_id': broadcaster_user_id},
                                     callback,
                                     ChannelUnbanEvent)

    async def listen_channel_moderator_add(self, broadcaster_user_id: str, callback: Callable[[ChannelModeratorAddEvent], Awaitable[None]]) -> str:
        """Moderator privileges were added to a user on a specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.MODERATION_READ` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelmoderatoradd

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.moderator.add',
                                     '1',
                                     {'broadcaster_user_id': broadcaster_user_id},
                                     callback,
                                     ChannelModeratorAddEvent)

    async def listen_channel_moderator_remove(self,
                                              broadcaster_user_id: str,
                                              callback: Callable[[ChannelModeratorRemoveEvent], Awaitable[None]]) -> str:
        """Moderator privileges were removed from a user on a specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.MODERATION_READ` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelmoderatorremove

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.moderator.remove',
                                     '1',
                                     {'broadcaster_user_id': broadcaster_user_id},
                                     callback,
                                     ChannelModeratorRemoveEvent)

    async def listen_channel_points_custom_reward_add(self,
                                                      broadcaster_user_id: str,
                                                      callback: Callable[[ChannelPointsCustomRewardAddEvent], Awaitable[None]]) -> str:
        """A custom channel points reward has been created for the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS` or
        :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel_points_custom_rewardadd

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.channel_points_custom_reward.add',
                                     '1',
                                     {'broadcaster_user_id': broadcaster_user_id},
                                     callback,
                                     ChannelPointsCustomRewardAddEvent)

    async def listen_channel_points_custom_reward_update(self,
                                                         broadcaster_user_id: str,
                                                         callback: Callable[[ChannelPointsCustomRewardUpdateEvent], Awaitable[None]],
                                                         reward_id: Optional[str] = None) -> str:
        """A custom channel points reward has been updated for the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS` or
        :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel_points_custom_rewardupdate

        :param broadcaster_user_id: the id of the user you want to listen to
        :param reward_id: the id of the reward you want to get updates from. |default| :code:`None`
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.channel_points_custom_reward.update',
                                     '1',
                                     remove_none_values({
                                         'broadcaster_user_id': broadcaster_user_id,
                                         'reward_id': reward_id}),
                                     callback,
                                     ChannelPointsCustomRewardUpdateEvent)

    async def listen_channel_points_custom_reward_remove(self,
                                                         broadcaster_user_id: str,
                                                         callback: Callable[[ChannelPointsCustomRewardRemoveEvent], Awaitable[None]],
                                                         reward_id: Optional[str] = None) -> str:
        """A custom channel points reward has been removed from the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS` or
        :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel_points_custom_rewardremove

        :param broadcaster_user_id: the id of the user you want to listen to
        :param reward_id: the id of the reward you want to get updates from. |default| :code:`None`
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.channel_points_custom_reward.remove',
                                     '1',
                                     remove_none_values({
                                         'broadcaster_user_id': broadcaster_user_id,
                                         'reward_id': reward_id}),
                                     callback,
                                     ChannelPointsCustomRewardRemoveEvent)

    async def listen_channel_points_custom_reward_redemption_add(self,
                                                                 broadcaster_user_id: str,
                                                                 callback: Callable[[ChannelPointsCustomRewardRedemptionAddEvent], Awaitable[None]],
                                                                 reward_id: Optional[str] = None) -> str:
        """A viewer has redeemed a custom channel points reward on the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS` or
        :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS` is required.

        For more information see here:
        https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel_points_custom_reward_redemptionadd

        :param broadcaster_user_id: the id of the user you want to listen to
        :param reward_id: the id of the reward you want to get updates from. |default| :code:`None`
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.channel_points_custom_reward_redemption.add',
                                     '1',
                                     remove_none_values({
                                         'broadcaster_user_id': broadcaster_user_id,
                                         'reward_id': reward_id}),
                                     callback,
                                     ChannelPointsCustomRewardRedemptionAddEvent)

    async def listen_channel_points_custom_reward_redemption_update(self,
                                                                    broadcaster_user_id: str,
                                                                    callback: Callable[[ChannelPointsCustomRewardRedemptionUpdateEvent], Awaitable[None]],
                                                                    reward_id: Optional[str] = None) -> str:
        """A redemption of a channel points custom reward has been updated for the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS` or
        :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS` is required.

        For more information see here:
        https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelchannel_points_custom_reward_redemptionupdate

        :param broadcaster_user_id: the id of the user you want to listen to
        :param reward_id: the id of the reward you want to get updates from. |default| :code:`None`
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.channel_points_custom_reward_redemption.update',
                                     '1',
                                     remove_none_values({
                                         'broadcaster_user_id': broadcaster_user_id,
                                         'reward_id': reward_id}),
                                     callback,
                                     ChannelPointsCustomRewardRedemptionUpdateEvent)

    async def listen_channel_poll_begin(self, broadcaster_user_id: str, callback: Callable[[ChannelPollBeginEvent], Awaitable[None]]) -> str:
        """A poll started on a specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_POLLS` or
        :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_POLLS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpollbegin

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.poll.begin', '1', {'broadcaster_user_id': broadcaster_user_id}, callback,
                                     ChannelPollBeginEvent)

    async def listen_channel_poll_progress(self, broadcaster_user_id: str, callback: Callable[[ChannelPollProgressEvent], Awaitable[None]]) -> str:
        """Users respond to a poll on a specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_POLLS` or
        :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_POLLS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpollprogress

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.poll.progress', '1', {'broadcaster_user_id': broadcaster_user_id}, callback,
                                     ChannelPollProgressEvent)

    async def listen_channel_poll_end(self, broadcaster_user_id: str, callback: Callable[[ChannelPollEndEvent], Awaitable[None]]) -> str:
        """A poll ended on a specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_POLLS` or
        :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_POLLS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpollend

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.poll.end', '1', {'broadcaster_user_id': broadcaster_user_id}, callback,
                                     ChannelPollEndEvent)

    async def listen_channel_prediction_begin(self, broadcaster_user_id: str, callback: Callable[[ChannelPredictionEvent], Awaitable[None]]) -> str:
        """A Prediction started on a specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_PREDICTIONS` or
        :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_PREDICTIONS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpredictionbegin

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.prediction.begin', '1', {'broadcaster_user_id': broadcaster_user_id},
                                     callback, ChannelPredictionEvent)

    async def listen_channel_prediction_progress(self, broadcaster_user_id: str, callback: Callable[[ChannelPredictionEvent], Awaitable[None]]) -> str:
        """Users participated in a Prediction on a specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_PREDICTIONS` or
        :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_PREDICTIONS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpredictionprogress

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.prediction.progress', '1', {'broadcaster_user_id': broadcaster_user_id},
                                     callback, ChannelPredictionEvent)

    async def listen_channel_prediction_lock(self, broadcaster_user_id: str, callback: Callable[[ChannelPredictionEvent], Awaitable[None]]) -> str:
        """A Prediction was locked on a specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_PREDICTIONS` or
        :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_PREDICTIONS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpredictionlock

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.prediction.lock', '1', {'broadcaster_user_id': broadcaster_user_id},
                                     callback, ChannelPredictionEvent)

    async def listen_channel_prediction_end(self, broadcaster_user_id: str, callback: Callable[[ChannelPredictionEndEvent], Awaitable[None]]) -> str:
        """A Prediction ended on a specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_PREDICTIONS` or
        :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_PREDICTIONS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelpredictionend

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.prediction.end', '1', {'broadcaster_user_id': broadcaster_user_id},
                                     callback, ChannelPredictionEndEvent)

    async def listen_drop_entitlement_grant(self,
                                            organisation_id: str,
                                            callback: Callable[[DropEntitlementGrantEvent], Awaitable[None]],
                                            category_id: Optional[str] = None,
                                            campaign_id: Optional[str] = None) -> str:
        """An entitlement for a Drop is granted to a user.

        App access token required. The client ID associated with the access token must be owned by a user who is part of the specified organization.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#dropentitlementgrant

        :param organisation_id: The organization ID of the organization that owns the game on the developer portal.
        :param category_id: The category (or game) ID of the game for which entitlement notifications will be received. |default| :code:`None`
        :param campaign_id: The campaign ID for a specific campaign for which entitlement notifications will be received. |default| :code:`None`
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('drop.entitlement.grant',
                                     '1',
                                     remove_none_values({
                                         'organization_id': organisation_id,
                                         'category_id': category_id,
                                         'campaign_id': campaign_id
                                     }),
                                     callback, DropEntitlementGrantEvent, is_batching_enabled=True)

    async def listen_extension_bits_transaction_create(self,
                                                       extension_client_id: str,
                                                       callback: Callable[[ExtensionBitsTransactionCreateEvent], Awaitable[None]]) -> str:
        """A Bits transaction occurred for a specified Twitch Extension.

        The OAuth token client ID must match the Extension client ID.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#extensionbits_transactioncreate

        :param extension_client_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('extension.bits_transaction.create', '1', {'extension_client_id': extension_client_id}, callback,
                                     ExtensionBitsTransactionCreateEvent)

    async def listen_goal_begin(self, broadcaster_user_id: str, callback: Callable[[GoalEvent], Awaitable[None]]) -> str:
        """A goal begins on the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_GOALS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelgoalbegin

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.goal.begin', '1', {'broadcaster_user_id': broadcaster_user_id}, callback,
                                     GoalEvent)

    async def listen_goal_progress(self, broadcaster_user_id: str, callback: Callable[[GoalEvent], Awaitable[None]]) -> str:
        """A goal makes progress on the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_GOALS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelgoalprogress

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.goal.progress', '1', {'broadcaster_user_id': broadcaster_user_id}, callback,
                                     GoalEvent)

    async def listen_goal_end(self, broadcaster_user_id: str, callback: Callable[[GoalEvent], Awaitable[None]]) -> str:
        """A goal ends on the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_GOALS` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelgoalend

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.goal.end', '1', {'broadcaster_user_id': broadcaster_user_id}, callback,
                                     GoalEvent)

    async def listen_hype_train_begin(self, broadcaster_user_id: str, callback: Callable[[HypeTrainEvent], Awaitable[None]]) -> str:
        """A Hype Train begins on the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_HYPE_TRAIN` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelhype_trainbegin

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.hype_train.begin', '1', {'broadcaster_user_id': broadcaster_user_id}, callback,
                                     HypeTrainEvent)

    async def listen_hype_train_progress(self, broadcaster_user_id: str, callback: Callable[[HypeTrainEvent], Awaitable[None]]) -> str:
        """A Hype Train makes progress on the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_HYPE_TRAIN` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelhype_trainprogress

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.hype_train.progress', '1', {'broadcaster_user_id': broadcaster_user_id}, callback,
                                     HypeTrainEvent)

    async def listen_hype_train_end(self, broadcaster_user_id: str, callback: Callable[[HypeTrainEndEvent], Awaitable[None]]) -> str:
        """A Hype Train ends on the specified channel.

        User Authentication with :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_HYPE_TRAIN` is required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#channelhype_trainend

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.hype_train.end', '1', {'broadcaster_user_id': broadcaster_user_id}, callback,
                                     HypeTrainEndEvent)

    async def listen_stream_online(self, broadcaster_user_id: str, callback: Callable[[StreamOnlineEvent], Awaitable[None]]) -> str:
        """The specified broadcaster starts a stream.

        No authorization required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#streamonline

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('stream.online', '1', {'broadcaster_user_id': broadcaster_user_id}, callback, StreamOnlineEvent)

    async def listen_stream_offline(self, broadcaster_user_id: str, callback: Callable[[StreamOfflineEvent], Awaitable[None]]) -> str:
        """The specified broadcaster stops a stream.

        No authorization required.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#streamoffline

        :param broadcaster_user_id: the id of the user you want to listen to
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('stream.offline', '1', {'broadcaster_user_id': broadcaster_user_id}, callback, StreamOfflineEvent)

    async def listen_user_authorization_grant(self, client_id: str, callback: Callable[[UserAuthorizationGrantEvent], Awaitable[None]]) -> str:
        """A user’s authorization has been granted to your client id.

        Provided client_id must match the client id in the application access token.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#userauthorizationgrant

        :param client_id: Your application’s client id.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('user.authorization.grant', '1', {'client_id': client_id}, callback,
                                     UserAuthorizationGrantEvent)

    async def listen_user_authorization_revoke(self, client_id: str, callback: Callable[[UserAuthorizationRevokeEvent], Awaitable[None]]) -> str:
        """A user’s authorization has been revoked for your client id.

        Provided client_id must match the client id in the application access token.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#userauthorizationrevoke

        :param client_id: Your application’s client id.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('user.authorization.revoke', '1', {'client_id': client_id}, callback,
                                     UserAuthorizationRevokeEvent)

    async def listen_user_update(self, user_id: str, callback: Callable[[UserUpdateEvent], Awaitable[None]]) -> str:
        """A user has updated their account.

        No authorization required. If you have the :const:`~twitchAPI.type.AuthScope.USER_READ_EMAIL` scope,
        the notification will include email field.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#userupdate

        :param user_id: The user ID for the user you want update notifications for.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('user.update', '1', {'user_id': user_id}, callback, UserUpdateEvent)

    async def listen_channel_shield_mode_begin(self,
                                               broadcaster_user_id: str,
                                               moderator_user_id: str,
                                               callback: Callable[[ShieldModeEvent], Awaitable[None]]) -> str:
        """Sends a notification when the broadcaster activates Shield Mode.

        Requires the :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_SHIELD_MODE` or
        :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHIELD_MODE` auth scope.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshield_modebegin

        :param broadcaster_user_id: The ID of the broadcaster that you want to receive notifications about when they activate Shield Mode.
        :param moderator_user_id: The ID of the broadcaster or one of the broadcaster’s moderators.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id
        }
        return await self._subscribe('channel.shield_mode.begin', '1', param, callback, ShieldModeEvent)

    async def listen_channel_shield_mode_end(self,
                                             broadcaster_user_id: str,
                                             moderator_user_id: str,
                                             callback: Callable[[ShieldModeEvent], Awaitable[None]]) -> str:
        """Sends a notification when the broadcaster deactivates Shield Mode.

        Requires the :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_SHIELD_MODE` or
        :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHIELD_MODE` auth scope.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshield_modeend

        :param broadcaster_user_id: The ID of the broadcaster that you want to receive notifications about when they deactivate Shield Mode.
        :param moderator_user_id: The ID of the broadcaster or one of the broadcaster’s moderators.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id
        }
        return await self._subscribe('channel.shield_mode.end', '1', param, callback, ShieldModeEvent)

    async def listen_channel_charity_campaign_start(self,
                                                    broadcaster_user_id: str,
                                                    callback: Callable[[CharityCampaignStartEvent], Awaitable[None]]) -> str:
        """Sends a notification when the broadcaster starts a charity campaign.

        Requires the :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_CHARITY` auth scope.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelcharity_campaignstart

        :param broadcaster_user_id: The ID of the broadcaster that you want to receive notifications about when they start a charity campaign.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {'broadcaster_user_id': broadcaster_user_id}
        return await self._subscribe('channel.charity_campaign.start', '1', param, callback, CharityCampaignStartEvent)

    async def listen_channel_charity_campaign_progress(self,
                                                       broadcaster_user_id: str,
                                                       callback: Callable[[CharityCampaignProgressEvent], Awaitable[None]]) -> str:
        """Sends notifications when progress is made towards the campaign’s goal or when the broadcaster changes the fundraising goal.

        Requires the :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_CHARITY` auth scope.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelcharity_campaignprogress

        :param broadcaster_user_id: The ID of the broadcaster that you want to receive notifications about when their campaign makes progress or is updated.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {'broadcaster_user_id': broadcaster_user_id}
        return await self._subscribe('channel.charity_campaign.progress', '1', param, callback, CharityCampaignProgressEvent)

    async def listen_channel_charity_campaign_stop(self,
                                                   broadcaster_user_id: str,
                                                   callback: Callable[[CharityCampaignStopEvent], Awaitable[None]]) -> str:
        """Sends a notification when the broadcaster stops a charity campaign.

        Requires the :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_CHARITY` auth scope.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelcharity_campaignstop

        :param broadcaster_user_id: The ID of the broadcaster that you want to receive notifications about when they stop a charity campaign.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {'broadcaster_user_id': broadcaster_user_id}
        return await self._subscribe('channel.charity_campaign.stop', '1', param, callback, CharityCampaignStopEvent)

    async def listen_channel_charity_campaign_donate(self,
                                                     broadcaster_user_id: str,
                                                     callback: Callable[[CharityDonationEvent], Awaitable[None]]) -> str:
        """Sends a notification when a user donates to the broadcaster’s charity campaign.

        Requires the :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_CHARITY` auth scope.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelcharity_campaigndonate

        :param broadcaster_user_id: The ID of the broadcaster that you want to receive notifications about when users donate to their campaign.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {'broadcaster_user_id': broadcaster_user_id}
        return await self._subscribe('channel.charity_campaign.donate', '1', param, callback, CharityDonationEvent)

    async def listen_channel_shoutout_create(self,
                                             broadcaster_user_id: str,
                                             moderator_user_id: str,
                                             callback: Callable[[ChannelShoutoutCreateEvent], Awaitable[None]]) -> str:
        """Sends a notification when the specified broadcaster sends a Shoutout.

        Requires the :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_SHOUTOUTS` or :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHOUTOUTS`
        auth scope.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshoutoutcreate

        :param broadcaster_user_id: The ID of the broadcaster that you want to receive notifications about when they send a Shoutout.
        :param moderator_user_id: The ID of the broadcaster that gave the Shoutout or one of the broadcaster’s moderators.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id
        }
        return await self._subscribe('channel.shoutout.create', '1', param, callback, ChannelShoutoutCreateEvent)

    async def listen_channel_shoutout_receive(self,
                                              broadcaster_user_id: str,
                                              moderator_user_id: str,
                                              callback: Callable[[ChannelShoutoutReceiveEvent], Awaitable[None]]) -> str:
        """Sends a notification when the specified broadcaster receives a Shoutout.

        Requires the :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_SHOUTOUTS` or :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_SHOUTOUTS`
        auth scope.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshoutoutreceive

        :param broadcaster_user_id: The ID of the broadcaster that you want to receive notifications about when they receive a Shoutout.
        :param moderator_user_id: The ID of the broadcaster that received the Shoutout or one of the broadcaster’s moderators.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id
        }
        return await self._subscribe('channel.shoutout.receive', '1', param, callback, ChannelShoutoutReceiveEvent)

    async def listen_channel_chat_clear(self,
                                        broadcaster_user_id: str,
                                        user_id: str,
                                        callback: Callable[[ChannelChatClearEvent], Awaitable[None]]) -> str:
        """A moderator or bot has cleared all messages from the chat room.

        Requires :const:`~twitchAPI.type.AuthScope.USER_READ_CHAT` scope from chatting user. If app access token used, then additionally requires
        :const:`~twitchAPI.type.AuthScope.USER_BOT` scope from chatting user, and either :const:`~twitchAPI.type.AuthScope.CHANNEL_BOT` scope from
        broadcaster or moderator status.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatclear

        :param broadcaster_user_id: User ID of the channel to receive chat clear events for.
        :param user_id: The user ID to read chat as.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._subscribe('channel.chat.clear', '1', param, callback, ChannelChatClearEvent)

    async def listen_channel_chat_clear_user_messages(self,
                                                      broadcaster_user_id: str,
                                                      user_id: str,
                                                      callback: Callable[[ChannelChatClearUserMessagesEvent], Awaitable[None]]) -> str:
        """A moderator or bot has cleared all messages from a specific user.

        Requires :const:`~twitchAPI.type.AuthScope.USER_READ_CHAT` scope from chatting user. If app access token used, then additionally requires
        :const:`~twitchAPI.type.AuthScope.USER_BOT` scope from chatting user, and either :const:`~twitchAPI.type.AuthScope.CHANNEL_BOT` scope from
        broadcaster or moderator status.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatclear_user_messages

        :param broadcaster_user_id: User ID of the channel to receive chat clear user messages events for.
        :param user_id: The user ID to read chat as.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._subscribe('channel.chat.clear_user_messages', '1', param, callback, ChannelChatClearUserMessagesEvent)

    async def listen_channel_chat_message_delete(self,
                                                 broadcaster_user_id: str,
                                                 user_id: str,
                                                 callback: Callable[[ChannelChatMessageDeleteEvent], Awaitable[None]]) -> str:
        """A moderator has removed a specific message.

        Requires :const:`~twitchAPI.type.AuthScope.USER_READ_CHAT` scope from chatting user. If app access token used, then additionally requires
        :const:`~twitchAPI.type.AuthScope.USER_BOT` scope from chatting user, and either :const:`~twitchAPI.type.AuthScope.CHANNEL_BOT` scope from
        broadcaster or moderator status.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatmessage_delete

        :param broadcaster_user_id: User ID of the channel to receive chat message delete events for.
        :param user_id: The user ID to read chat as.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._subscribe('channel.chat.message_delete', '1', param, callback, ChannelChatMessageDeleteEvent)

    async def listen_channel_chat_notification(self,
                                               broadcaster_user_id: str,
                                               user_id: str,
                                               callback: Callable[[ChannelChatNotificationEvent], Awaitable[None]]) -> str:
        """A notification for when an event that appears in chat has occurred.

        Requires :const:`~twitchAPI.type.AuthScope.USER_READ_CHAT` scope from chatting user. If app access token used, then additionally requires
        :const:`~twitchAPI.type.AuthScope.USER_BOT` scope from chatting user, and either :const:`~twitchAPI.type.AuthScope.CHANNEL_BOT` scope from
        broadcaster or moderator status.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatnotification

        :param broadcaster_user_id: User ID of the channel to receive chat notification events for.
        :param user_id: The user ID to read chat as.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._subscribe('channel.chat.notification', '1', param, callback, ChannelChatNotificationEvent)

    async def listen_channel_ad_break_begin(self,
                                            broadcaster_user_id: str,
                                            callback: Callable[[ChannelAdBreakBeginEvent], Awaitable[None]]) -> str:
        """A midroll commercial break has started running.

        Requires the :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_ADS` scope.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelad_breakbegin

        :param broadcaster_user_id: The ID of the broadcaster that you want to get Channel Ad Break begin notifications for.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        return await self._subscribe('channel.ad_break.begin', '1',
                                     {'broadcaster_user_id': broadcaster_user_id},
                                     callback,
                                     ChannelAdBreakBeginEvent)

    async def listen_channel_chat_message(self,
                                          broadcaster_user_id: str,
                                          user_id: str,
                                          callback: Callable[[ChannelChatMessageEvent], Awaitable[None]]) -> str:
        """Any user sends a message to a specific chat room.

        Requires :const:`~twitchAPI.type.AuthScope.USER_READ_CHAT` scope from chatting user.
        If app access token used, then additionally requires :const:`~twitchAPI.type.AuthScope.USER_BOT` scope from chatting user, and either
        :const:`~twitchAPI.type.AuthScope.CHANNEL_BOT` scope from broadcaster or moderator status.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatmessage

        :param broadcaster_user_id: User ID of the channel to receive chat message events for.
        :param user_id: The user ID to read chat as.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._subscribe('channel.chat.message', '1', param, callback, ChannelChatMessageEvent)

    async def listen_channel_chat_settings_update(self,
                                                  broadcaster_user_id: str,
                                                  user_id: str,
                                                  callback: Callable[[ChannelChatSettingsUpdateEvent], Awaitable[None]]) -> str:
        """This event sends a notification when a broadcaster’s chat settings are updated.

        Requires :const:`~twitchAPI.type.AuthScope.USER_READ_CHAT` scope from chatting user.
        If app access token used, then additionally requires :const:`~twitchAPI.type.AuthScope.USER_BOT` scope from chatting user, and either
        :const:`~twitchAPI.type.AuthScope.CHANNEL_BOT` scope from broadcaster or moderator status.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchat_settingsupdate

        :param broadcaster_user_id: User ID of the channel to receive chat settings update events for.
        :param user_id: The user ID to read chat as.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._subscribe('channel.chat_settings.update', '1', param, callback, ChannelChatSettingsUpdateEvent)

    async def listen_user_whisper_message(self,
                                          user_id: str,
                                          callback: Callable[[UserWhisperMessageEvent], Awaitable[None]]) -> str:
        """ Sends a notification when a user receives a whisper. Event Triggers - Anyone whispers the specified user.

        Requires :const:`~twitchAPI.type.AuthScope.USER_READ_WHISPERS` or :const:`~twitchAPI.type.AuthScope.USER_MANAGE_WHISPERS` scope.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#userwhispermessage

        :param user_id: The user_id of the person receiving whispers.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {'user_id': user_id}
        return await self._subscribe('user.whisper.message', '1', param, callback, UserWhisperMessageEvent)

    async def listen_channel_points_automatic_reward_redemption_add(self,
                                                                    broadcaster_user_id: str,
                                                                    callback: Callable[[ChannelPointsAutomaticRewardRedemptionAddEvent], Awaitable[None]]) -> str:
        """A viewer has redeemed an automatic channel points reward on the specified channel.

        Requires :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_REDEMPTIONS` or :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_REDEMPTIONS` scope.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchannel_points_automatic_reward_redemptionadd

        :param broadcaster_user_id: The broadcaster user ID for the channel you want to receive channel points reward add notifications for.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {'broadcaster_user_id': broadcaster_user_id}
        return await self._subscribe('channel.channel_points_automatic_reward_redemption.add', '1', param, callback,
                                     ChannelPointsAutomaticRewardRedemptionAddEvent)

    async def listen_channel_vip_add(self,
                                     broadcaster_user_id: str,
                                     callback: Callable[[ChannelVIPAddEvent], Awaitable[None]]) -> str:
        """A VIP is added to the channel.

        Requires :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_VIPS` or :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_VIPS` scope.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelvipadd

        :param broadcaster_user_id: The User ID of the broadcaster
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {'broadcaster_user_id': broadcaster_user_id}
        return await self._subscribe('channel.vip.add', '1', param, callback, ChannelVIPAddEvent)

    async def listen_channel_vip_remove(self,
                                        broadcaster_user_id: str,
                                        callback: Callable[[ChannelVIPRemoveEvent], Awaitable[None]]) -> str:
        """A VIP is removed from the channel.

        Requires :const:`~twitchAPI.type.AuthScope.CHANNEL_READ_VIPS` or :const:`~twitchAPI.type.AuthScope.CHANNEL_MANAGE_VIPS` scope.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelvipremove

        :param broadcaster_user_id: The User ID of the broadcaster
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {'broadcaster_user_id': broadcaster_user_id}
        return await self._subscribe('channel.vip.remove', '1', param, callback, ChannelVIPRemoveEvent)

    async def listen_channel_unban_request_create(self,
                                                  broadcaster_user_id: str,
                                                  moderator_user_id: str,
                                                  callback: Callable[[ChannelUnbanRequestCreateEvent], Awaitable[None]]) -> str:
        """A user creates an unban request.

        Requires :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_UNBAN_REQUESTS` or :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_UNBAN_REQUESTS` scope.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelunban_requestcreate

        :param broadcaster_user_id: The ID of the broadcaster you want to get chat unban request notifications for.
        :param moderator_user_id: The ID of the user that has permission to moderate the broadcaster’s channel and has granted your app permission to subscribe to this subscription type.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {'broadcaster_user_id': broadcaster_user_id,
                 'moderator_user_id': moderator_user_id}
        return await self._subscribe('channel.unban_request.create', '1', param, callback, ChannelUnbanRequestCreateEvent)

    async def listen_channel_unban_request_resolve(self,
                                                   broadcaster_user_id: str,
                                                   moderator_user_id: str,
                                                   callback: Callable[[ChannelUnbanRequestResolveEvent], Awaitable[None]]) -> str:
        """An unban request has been resolved.

        Requires :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_UNBAN_REQUESTS` or :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_UNBAN_REQUESTS` scope.

        .. note:: If you use webhooks, the user in moderator_user_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

                  If you use WebSockets, the ID in moderator_user_id must match the user ID in the user access token.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelunban_requestresolve

        :param broadcaster_user_id: The ID of the broadcaster you want to get unban request resolution notifications for.
        :param moderator_user_id: The ID of the user that has permission to moderate the broadcaster’s channel and has granted your app permission to subscribe to this subscription type.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {'broadcaster_user_id': broadcaster_user_id,
                 'moderator_user_id': moderator_user_id}
        return await self._subscribe('channel.unban_request.resolve', '1', param, callback, ChannelUnbanRequestResolveEvent)

    async def listen_channel_suspicious_user_message(self,
                                                     broadcaster_user_id: str,
                                                     moderator_user_id: str,
                                                     callback: Callable[[ChannelSuspiciousUserMessageEvent], Awaitable[None]]) -> str:
        """A chat message has been sent by a suspicious user.

        Requires :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_SUSPICIOUS_USERS` scope.

        .. note:: If you use webhooks, the user in moderator_user_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

                  If you use WebSockets, the ID in moderator_user_id must match the user ID in the user access token.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelsuspicious_usermessage

        :param broadcaster_user_id: User ID of the channel to receive chat message events for.
        :param moderator_user_id: The ID of a user that has permission to moderate the broadcaster’s channel and has granted your app permission
            to subscribe to this subscription type.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {'broadcaster_user_id': broadcaster_user_id,
                 'moderator_user_id': moderator_user_id}
        return await self._subscribe('channel.suspicious_user.message', '1', param, callback, ChannelSuspiciousUserMessageEvent)

    async def listen_channel_suspicious_user_update(self,
                                                    broadcaster_user_id: str,
                                                    moderator_user_id: str,
                                                    callback: Callable[[ChannelSuspiciousUserUpdateEvent], Awaitable[None]]) -> str:
        """A suspicious user has been updated.

        Requires :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_SUSPICIOUS_USERS` scope.

        .. note:: If you use webhooks, the user in moderator_user_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

                  If you use WebSockets, the ID in moderator_user_id must match the user ID in the user access token.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelsuspicious_userupdate

        :param broadcaster_user_id: The broadcaster you want to get chat unban request notifications for.
        :param moderator_user_id: The ID of a user that has permission to moderate the broadcaster’s channel and has granted your app permission
            to subscribe to this subscription type.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {'broadcaster_user_id': broadcaster_user_id,
                 'moderator_user_id': moderator_user_id}
        return await self._subscribe('channel.suspicious_user.update', '1', param, callback, ChannelSuspiciousUserUpdateEvent)

    async def listen_channel_moderate(self,
                                      broadcaster_user_id: str,
                                      moderator_user_id: str,
                                      callback: Callable[[ChannelModerateEvent], Awaitable[None]]) -> str:
        """A moderator performs a moderation action in a channel. Includes warnings.

        Requires all of the following scopes:

        - :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_BLOCKED_TERMS` or :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_BLOCKED_TERMS`
        - :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_CHAT_SETTINGS` or :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_CHAT_SETTINGS`
        - :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_UNBAN_REQUESTS` or :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_UNBAN_REQUESTS`
        - :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_BANNED_USERS` or :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_BANNED_USERS`
        - :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_CHAT_MESSAGES` or :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_CHAT_MESSAGES`
        - :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_WARNINGS` or :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_WARNINGS`
        - :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_MODERATORS`
        - :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_VIPS`

        .. note:: If you use webhooks, the user in moderator_user_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

                  If you use WebSockets, the ID in moderator_user_id must match the user ID in the user access token.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelmoderate-v2

        :param broadcaster_user_id: The user ID of the broadcaster.
        :param moderator_user_id: The user ID of the moderator.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id
        }
        return await self._subscribe('channel.moderate', '2', param, callback, ChannelModerateEvent)

    async def listen_channel_warning_acknowledge(self,
                                                 broadcaster_user_id: str,
                                                 moderator_user_id: str,
                                                 callback: Callable[[ChannelWarningAcknowledgeEvent], Awaitable[None]]) -> str:
        """Sends a notification when a warning is acknowledged by a user.

        Requires :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_WARNINGS` or :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_WARNINGS` scope.

        .. note:: If you use webhooks, the user in moderator_user_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

                  If you use WebSockets, the ID in moderator_user_id must match the user ID in the user access token.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelwarningacknowledge

        :param broadcaster_user_id: The User ID of the broadcaster.
        :param moderator_user_id: The User ID of the moderator.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id
        }
        return await self._subscribe('channel.warning.acknowledge', '1', param, callback, ChannelWarningAcknowledgeEvent)

    async def listen_channel_warning_send(self,
                                          broadcaster_user_id: str,
                                          moderator_user_id: str,
                                          callback: Callable[[ChannelWarningSendEvent], Awaitable[None]]) -> str:
        """Sends a notification when a warning is send to a user. Broadcasters and moderators can see the warning’s details.

        Requires :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_WARNINGS` or :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_WARNINGS` scope.

        .. note:: If you use webhooks, the user in moderator_user_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

                  If you use WebSockets, the ID in moderator_user_id must match the user ID in the user access token.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelwarningsend

        :param broadcaster_user_id: The User ID of the broadcaster.
        :param moderator_user_id: The User ID of the moderator.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id
        }
        return await self._subscribe('channel.warning.send', '1', param, callback, ChannelWarningSendEvent)

    async def listen_automod_message_hold(self,
                                          broadcaster_user_id: str,
                                          moderator_user_id: str,
                                          callback: Callable[[AutomodMessageHoldEvent], Awaitable[None]]) -> str:
        """Sends a notification if a message was caught by automod for review.

        Requires :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_AUTOMOD` scope.

        .. note:: If you use webhooks, the user in moderator_user_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

                  If you use WebSockets, the ID in moderator_user_id must match the user ID in the user access token.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#automodmessagehold

        :param broadcaster_user_id: User ID of the broadcaster (channel).
        :param moderator_user_id: User ID of the moderator.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id
        }
        return await self._subscribe('automod.message.hold', '1', param , callback, AutomodMessageHoldEvent)

    async def listen_automod_message_update(self,
                                            broadcaster_user_id: str,
                                            moderator_user_id: str,
                                            callback: Callable[[AutomodMessageUpdateEvent], Awaitable[None]]) -> str:
        """Sends a notification when a message in the automod queue has its status changed.

        Requires :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_AUTOMOD` scope.

        .. note:: If you use webhooks, the user in moderator_user_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

                  If you use WebSockets, the ID in moderator_user_id must match the user ID in the user access token.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#automodmessageupdate

        :param broadcaster_user_id: User ID of the broadcaster (channel)
        :param moderator_user_id: User ID of the moderator.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id
        }
        return await self._subscribe('automod.message.update', '1', param, callback, AutomodMessageUpdateEvent)

    async def listen_automod_settings_update(self,
                                             broadcaster_user_id: str,
                                             moderator_user_id: str,
                                             callback: Callable[[AutomodSettingsUpdateEvent], Awaitable[None]]) -> str:
        """Sends a notification when the broadcaster's automod settings are updated.

        Requires :const:`~twitchAPI.type.AuthScope.MODERATOR_READ_AUTOMOD_SETTINGS` scope.

        .. note:: If you use webhooks, the user in moderator_user_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

                  If you use WebSockets, the ID in moderator_user_id must match the user ID in the user access token.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#automodsettingsupdate

        :param broadcaster_user_id: User ID of the broadcaster (channel).
        :param moderator_user_id: User ID of the moderator.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id
        }
        return await self._subscribe('automod.settings.update', '1', param, callback, AutomodSettingsUpdateEvent)

    async def listen_automod_terms_update(self,
                                          broadcaster_user_id: str,
                                          moderator_user_id: str,
                                          callback: Callable[[AutomodTermsUpdateEvent], Awaitable[None]]) -> str:
        """Sends a notification when a broadcaster's automod terms are updated.

        Requires :const:`~twitchAPI.type.AuthScope.MODERATOR_MANAGE_AUTOMOD` scope.

        .. note:: If you use webhooks, the user in moderator_user_id must have granted your app (client ID) one of the above permissions prior to your app subscribing to this subscription type.

                  If you use WebSockets, the ID in moderator_user_id must match the user ID in the user access token.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#automodtermsupdate

        :param broadcaster_user_id: User ID of the broadcaster (channel).
        :param moderator_user_id: User ID of the moderator creating the subscription.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id
        }
        return await self._subscribe('automod.terms.update', '1', param, callback, AutomodTermsUpdateEvent)

    async def listen_channel_chat_user_message_hold(self,
                                                    broadcaster_user_id: str,
                                                    user_id: str,
                                                    callback: Callable[[ChannelChatUserMessageHoldEvent], Awaitable[None]]) -> str:
        """A user is notified if their message is caught by automod.

        .. note:: Requires :const:`~twitchAPI.type.AuthScope.USER_READ_CHAT` scope from the chatting user.

                  If WebSockets is used, additionally requires :const:`~twitchAPI.type.AuthScope.USER_BOT` from chatting user.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatuser_message_hold

        :param broadcaster_user_id: User ID of the channel to receive chat message events for.
        :param user_id: The user ID to read chat as.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._subscribe('channel.chat.user_message_hold', '1', param, callback, ChannelChatUserMessageHoldEvent)

    async def listen_channel_chat_user_message_update(self,
                                                      broadcaster_user_id: str,
                                                      user_id: str,
                                                      callback: Callable[[ChannelChatUserMessageUpdateEvent], Awaitable[None]]) -> str:
        """A user is notified if their message’s automod status is updated.

        .. note:: Requires :const:`~twitchAPI.type.AuthScope.USER_READ_CHAT` scope from the chatting user.

                  If WebSockets is used, additionally requires :const:`~twitchAPI.type.AuthScope.USER_BOT` from chatting user.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatuser_message_update

        :param broadcaster_user_id: User ID of the channel to receive chat message events for.
        :param user_id: The user ID to read chat as.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._subscribe('channel.chat.user_message_update', '1', param, callback, ChannelChatUserMessageUpdateEvent)

    async def listen_channel_shared_chat_begin(self,
                                               broadcaster_user_id: str,
                                               callback: Callable[[ChannelSharedChatBeginEvent], Awaitable[None]]) -> str:
        """A notification when a channel becomes active in an active shared chat session.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshared_chatbegin

        :param broadcaster_user_id: The User ID of the channel to receive shared chat session begin events for.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
        }
        return await self._subscribe('channel.shared_chat.begin', '1', param, callback, ChannelSharedChatBeginEvent)

    async def listen_channel_shared_chat_update(self,
                                                broadcaster_user_id: str,
                                                callback: Callable[[ChannelSharedChatUpdateEvent], Awaitable[None]]) -> str:
        """A notification when the active shared chat session the channel is in changes.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshared_chatupdate

        :param broadcaster_user_id: The User ID of the channel to receive shared chat session update events for.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
        }
        return await self._subscribe('channel.shared_chat.update', '1', param, callback, ChannelSharedChatUpdateEvent)

    async def listen_channel_shared_chat_end(self,
                                             broadcaster_user_id: str,
                                             callback: Callable[[ChannelSharedChatEndEvent], Awaitable[None]]) -> str:
        """A notification when a channel leaves a shared chat session or the session ends.

        For more information see here: https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelshared_chatend

        :param broadcaster_user_id: The User ID of the channel to receive shared chat session end events for.
        :param callback: function for callback
        :raises ~twitchAPI.type.EventSubSubscriptionConflict: if a conflict was found with this subscription
            (e.g. already subscribed to this exact topic)
        :raises ~twitchAPI.type.EventSubSubscriptionTimeout: if :const:`~twitchAPI.eventsub.webhook.EventSubWebhook.wait_for_subscription_confirm`
            is true and the subscription was not fully confirmed in time
        :raises ~twitchAPI.type.EventSubSubscriptionError: if the subscription failed (see error message for details)
        :raises ~twitchAPI.type.TwitchBackendException: if the subscription failed due to a twitch backend error
        :returns: The id of the topic subscription
        """
        param = {
            'broadcaster_user_id': broadcaster_user_id,
        }
        return await self._subscribe('channel.shared_chat.end', '1', param, callback, ChannelSharedChatEndEvent)

==> ./eventsub/webhook.py <==
#  Copyright (c) 2023. Lena "Teekeks" During <info@teawork.de>
"""
EventSub Webhook
----------------

.. note:: EventSub Webhook is targeted at programs which have to subscribe to topics for multiple broadcasters.\n
    Should you only need to target a single broadcaster or are building a client side project, look at :doc:`/modules/twitchAPI.eventsub.websocket`

EventSub lets you listen for events that happen on Twitch.

The EventSub client runs in its own thread, calling the given callback function whenever an event happens.

************
Requirements
************

.. note:: Please note that Your Endpoint URL has to be HTTPS, has to run on Port 443 and requires a valid, non self signed certificate
            This most likely means, that you need a reverse proxy like nginx. You can also hand in a valid ssl context to be used in the constructor.

In the case that you don't hand in a valid ssl context to the constructor, you can specify any port you want in the constructor and handle the
bridge between this program and your public URL on port 443 via reverse proxy.\n
You can check on whether or not your webhook is publicly reachable by navigating to the URL set in `callback_url`.
You should get a 200 response with the text :code:`pyTwitchAPI eventsub`.

*******************
Listening to topics
*******************

After you started your EventSub client, you can use the :code:`listen_` prefixed functions to listen to the topics you are interested in.

Look at :ref:`eventsub-available-topics` to find the topics you are interested in.

The function you hand in as callback will be called whenever that event happens with the event data as a parameter,
the type of that parameter is also listed in the link above.

************
Code Example
************

.. code-block:: python

    from twitchAPI.twitch import Twitch
    from twitchAPI.helper import first
    from twitchAPI.eventsub.webhook import EventSubWebhook
    from twitchAPI.object.eventsub import ChannelFollowEvent
    from twitchAPI.oauth import UserAuthenticator
    from twitchAPI.type import AuthScope
    import asyncio

    TARGET_USERNAME = 'target_username_here'
    EVENTSUB_URL = 'https://url.to.your.webhook.com'
    APP_ID = 'your_app_id'
    APP_SECRET = 'your_app_secret'
    TARGET_SCOPES = [AuthScope.MODERATOR_READ_FOLLOWERS]


    async def on_follow(data: ChannelFollowEvent):
        # our event happened, lets do things with the data we got!
        print(f'{data.event.user_name} now follows {data.event.broadcaster_user_name}!')


    async def eventsub_webhook_example():
        # create the api instance and get the ID of the target user
        twitch = await Twitch(APP_ID, APP_SECRET)
        user = await first(twitch.get_users(logins=TARGET_USERNAME))

        # the user has to authenticate once using the bot with our intended scope.
        # since we do not need the resulting token after this authentication, we just discard the result we get from authenticate()
        # Please read up the UserAuthenticator documentation to get a full view of how this process works
        auth = UserAuthenticator(twitch, TARGET_SCOPES)
        await auth.authenticate()

        # basic setup, will run on port 8080 and a reverse proxy takes care of the https and certificate
        eventsub = EventSubWebhook(EVENTSUB_URL, 8080, twitch)

        # unsubscribe from all old events that might still be there
        # this will ensure we have a clean slate
        await eventsub.unsubscribe_all()
        # start the eventsub client
        eventsub.start()
        # subscribing to the desired eventsub hook for our user
        # the given function (in this example on_follow) will be called every time this event is triggered
        # the broadcaster is a moderator in their own channel by default so specifying both as the same works in this example
        await eventsub.listen_channel_follow_v2(user.id, user.id, on_follow)

        # eventsub will run in its own process
        # so lets just wait for user input before shutting it all down again
        try:
            input('press Enter to shut down...')
        finally:
            # stopping both eventsub as well as gracefully closing the connection to the API
            await eventsub.stop()
            await twitch.close()
        print('done')


    # lets run our example
    asyncio.run(eventsub_webhook_example())"""
import asyncio
import hashlib
import hmac
import threading
from functools import partial
from json import JSONDecodeError
from random import choice
from string import ascii_lowercase
from ssl import SSLContext
from time import sleep
from typing import Optional, Union, Callable, Awaitable
import datetime
from collections import deque

from aiohttp import web, ClientSession

from twitchAPI.eventsub.base import EventSubBase
from ..twitch import Twitch
from ..helper import done_task_callback
from ..type import TwitchBackendException, EventSubSubscriptionConflict, EventSubSubscriptionError, EventSubSubscriptionTimeout, \
    TwitchAuthorizationException

__all__ = ['EventSubWebhook']


class EventSubWebhook(EventSubBase):

    def __init__(self,
                 callback_url: str,
                 port: int,
                 twitch: Twitch,
                 ssl_context: Optional[SSLContext] = None,
                 host_binding: str = '0.0.0.0',
                 subscription_url: Optional[str] = None,
                 callback_loop: Optional[asyncio.AbstractEventLoop] = None,
                 revocation_handler: Optional[Callable[[dict], Awaitable[None]]] = None,
                 message_deduplication_history_length: int = 50):
        """
        :param callback_url: The full URL of the webhook.
        :param port: the port on which this webhook should run
        :param twitch: a app authenticated instance of :const:`~twitchAPI.twitch.Twitch`
        :param ssl_context: optional ssl context to be used |default| :code:`None`
        :param host_binding: the host to bind the internal server to |default| :code:`0.0.0.0`
        :param subscription_url: Alternative subscription URL, useful for development with the twitch-cli
        :param callback_loop: The asyncio eventloop to be used for callbacks. \n
            Set this if you or a library you use cares about which asyncio event loop is running the callbacks.
            Defaults to the one used by EventSub Webhook.
        :param revocation_handler: Optional handler for when subscriptions get revoked. |default| :code:`None`
        :param message_deduplication_history_length: The amount of messages being considered for the duplicate message deduplication. |default| :code:`50`
        """
        super().__init__(twitch, 'twitchAPI.eventsub.webhook')
        self.callback_url: str = callback_url
        """The full URL of the webhook."""
        if self.callback_url[-1] == '/':
            self.callback_url = self.callback_url[:-1]
        self.secret: str = ''.join(choice(ascii_lowercase) for _ in range(20))
        """A random secret string. Set this for added security. |default| :code:`A random 20 character long string`"""
        self.wait_for_subscription_confirm: bool = True
        """Set this to false if you don't want to wait for a subscription confirm. |default| :code:`True`"""
        self.wait_for_subscription_confirm_timeout: int = 30
        """Max time in seconds to wait for a subscription confirmation. Only used if ``wait_for_subscription_confirm`` is set to True. 
            |default| :code:`30`"""

        self._port: int = port
        self.subscription_url: Optional[str] = subscription_url
        """Alternative subscription URL, useful for development with the twitch-cli"""
        if self.subscription_url is not None and self.subscription_url[-1] != '/':
            self.subscription_url += '/'
        self._callback_loop = callback_loop
        self._host: str = host_binding
        self.__running = False
        self.revokation_handler: Optional[Callable[[dict], Awaitable[None]]] = revocation_handler
        """Optional handler for when subscriptions get revoked."""
        self._startup_complete = False
        self.unsubscribe_on_stop: bool = True
        """Unsubscribe all currently active Webhooks on calling :const:`~twitchAPI.eventsub.EventSub.stop()` |default| :code:`True`"""

        self._closing = False
        self.__ssl_context: Optional[SSLContext] = ssl_context
        self.__active_webhooks = {}
        self.__hook_thread: Union['threading.Thread', None] = None
        self.__hook_loop: Union['asyncio.AbstractEventLoop', None] = None
        self.__hook_runner: Union['web.AppRunner', None] = None
        self._task_callback = partial(done_task_callback, self.logger)
        if not self.callback_url.startswith('https'):
            raise RuntimeError('HTTPS is required for authenticated webhook.\n'
                               + 'Either use non authenticated webhook or use a HTTPS proxy!')
        self._msg_id_history: deque = deque(maxlen=message_deduplication_history_length)

    async def _unsubscribe_hook(self, topic_id: str) -> bool:
        return True

    def __build_runner(self):
        hook_app = web.Application()
        hook_app.add_routes([web.post('/callback', self.__handle_callback),
                             web.get('/', self.__handle_default)])
        return web.AppRunner(hook_app)

    def __run_hook(self, runner: 'web.AppRunner'):
        self.__hook_runner = runner
        self.__hook_loop = asyncio.new_event_loop()
        if self._callback_loop is None:
            self._callback_loop = self.__hook_loop
        asyncio.set_event_loop(self.__hook_loop)
        self.__hook_loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, str(self._host), self._port, ssl_context=self.__ssl_context)
        self.__hook_loop.run_until_complete(site.start())
        self.logger.info('started twitch API event sub on port ' + str(self._port))
        self._startup_complete = True
        self.__hook_loop.run_until_complete(self._keep_loop_alive())

    async def _keep_loop_alive(self):
        while not self._closing:
            await asyncio.sleep(0.1)

    def start(self):
        """Starts the EventSub client

        :rtype: None
        :raises RuntimeError: if EventSub is already running
        """
        if self.__running:
            raise RuntimeError('already started')
        self.__hook_thread = threading.Thread(target=self.__run_hook, args=(self.__build_runner(),))
        self.__running = True
        self._startup_complete = False
        self._closing = False
        self.__hook_thread.start()
        while not self._startup_complete:
            sleep(0.1)

    async def stop(self):
        """Stops the EventSub client

        This also unsubscribes from all known subscriptions if unsubscribe_on_stop is True

        :rtype: None
        :raises RuntimeError: if EventSub is not running
        """
        if not self.__running:
            raise RuntimeError('EventSubWebhook is not running')
        self.logger.debug('shutting down eventsub')
        if self.__hook_runner is not None and self.unsubscribe_on_stop:
            await self.unsubscribe_all_known()
        # ensure all client sessions are closed
        await asyncio.sleep(0.25)
        self._closing = True
        # cleanly shut down the runner
        await self.__hook_runner.shutdown()
        await self.__hook_runner.cleanup()
        self.__hook_runner = None
        self.__running = False
        self.logger.debug('eventsub shut down')

    def _get_transport(self):
        return {
            'method': 'webhook',
            'callback': f'{self.callback_url}/callback',
            'secret': self.secret
        }

    async def _build_request_header(self):
        token = await self._twitch.get_refreshed_app_token()
        if token is None:
            raise TwitchAuthorizationException('no Authorization set!')
        return {
            'Client-ID': self._twitch.app_id,
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

    async def _subscribe(self, sub_type: str, sub_version: str, condition: dict, callback, event, is_batching_enabled: Optional[bool] = None) -> str:
        """"Subscribe to Twitch Topic"""
        if not asyncio.iscoroutinefunction(callback):
            raise ValueError('callback needs to be a async function which takes one parameter')
        self.logger.debug(f'subscribe to {sub_type} version {sub_version} with condition {condition}')
        data = {
            'type': sub_type,
            'version': sub_version,
            'condition': condition,
            'transport': self._get_transport()
        }
        if is_batching_enabled is not None:
            data['is_batching_enabled'] = is_batching_enabled

        async with ClientSession(timeout=self._twitch.session_timeout) as session:
            sub_base = self.subscription_url if self.subscription_url is not None else self._twitch.base_url
            r_data = await self._api_post_request(session, sub_base + 'eventsub/subscriptions', data=data)
            result = await r_data.json()
        error = result.get('error')
        if r_data.status == 500:
            raise TwitchBackendException(error)
        if error is not None:
            if error.lower() == 'conflict':
                raise EventSubSubscriptionConflict(result.get('message', ''))
            raise EventSubSubscriptionError(result.get('message'))
        sub_id = result['data'][0]['id']
        self.logger.debug(f'subscription for {sub_type} version {sub_version} with condition {condition} has id {sub_id}')
        self._add_callback(sub_id, callback, event)
        if self.wait_for_subscription_confirm:
            timeout = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=self.wait_for_subscription_confirm_timeout)
            while timeout >= datetime.datetime.utcnow():
                if self._callbacks[sub_id]['active']:
                    return sub_id
                await asyncio.sleep(0.01)
            self._callbacks.pop(sub_id, None)
            raise EventSubSubscriptionTimeout()
        return sub_id

    async def _verify_signature(self, request: 'web.Request') -> bool:
        expected = request.headers['Twitch-Eventsub-Message-Signature']
        hmac_message = request.headers['Twitch-Eventsub-Message-Id'] + \
            request.headers['Twitch-Eventsub-Message-Timestamp'] + await request.text()
        sig = 'sha256=' + hmac.new(bytes(self.secret, 'utf-8'),
                                   msg=bytes(hmac_message, 'utf-8'),
                                   digestmod=hashlib.sha256).hexdigest().lower()
        return sig == expected

    # noinspection PyUnusedLocal
    @staticmethod
    async def __handle_default(request: 'web.Request'):
        return web.Response(text="pyTwitchAPI EventSub")

    async def __handle_challenge(self, request: 'web.Request', data: dict):
        self.logger.debug(f'received challenge for subscription {data.get("subscription").get("id")}')
        if not await self._verify_signature(request):
            self.logger.warning(f'message signature is not matching! Discarding message')
            return web.Response(status=403)
        await self._activate_callback(data.get('subscription').get('id'))
        return web.Response(text=data.get('challenge'))

    async def _handle_revokation(self, data):
        sub_id: str = data.get('subscription', {}).get('id')
        self.logger.debug(f'got revocation of subscription {sub_id} for reason {data.get("subscription").get("status")}')
        if sub_id not in self._callbacks.keys():
            self.logger.warning(f'unknown subscription {sub_id} got revoked. ignore')
            return
        self._callbacks.pop(sub_id)
        if self.revokation_handler is not None:
            t = self._callback_loop.create_task(self.revokation_handler(data))
            t.add_done_callback(self._task_callback)

    async def __handle_callback(self, request: 'web.Request'):
        try:
            data: dict = await request.json()
        except JSONDecodeError:
            self.logger.error('got request with malformed body! Discarding message')
            return web.Response(status=400)
        if data.get('challenge') is not None:
            return await self.__handle_challenge(request, data)
        sub_id = data.get('subscription', {}).get('id')
        callback = self._callbacks.get(sub_id)
        if callback is None:
            self.logger.error(f'received event for unknown subscription with ID {sub_id}')
        else:
            if not await self._verify_signature(request):
                self.logger.warning(f'message signature is not matching! Discarding message')
                return web.Response(status=403)
            msg_type = request.headers['Twitch-Eventsub-Message-Type']
            if msg_type.lower() == 'revocation':
                await self._handle_revokation(data)
            else:
                msg_id = request.headers.get('Twitch-Eventsub-Message-Id')
                if msg_id is not None and msg_id in self._msg_id_history:
                    self.logger.warning(f'got message with duplicate id {msg_id}! Discarding message')
                else:
                    self._msg_id_history.append(msg_id)
                    dat = callback['event'](**data)
                    t = self._callback_loop.create_task(callback['callback'](dat))
                    t.add_done_callback(self._task_callback)
        return web.Response(status=200)

==> ./eventsub/websocket.py <==
#  Copyright (c) 2023. Lena "Teekeks" During <info@teawork.de>
"""
EventSub Websocket
------------------

.. note:: EventSub Websocket is targeted at programs which have to subscribe to topics for just a single broadcaster.\n
    Should you need to target multiple broadcasters or are building a server side project, look at :doc:`/modules/twitchAPI.eventsub.webhook`

EventSub lets you listen for events that happen on Twitch.

The EventSub client runs in its own thread, calling the given callback function whenever an event happens.

*******************
Listening to topics
*******************

After you started your EventSub client, you can use the :code:`listen_` prefixed functions to listen to the topics you are interested in.

Look at :ref:`eventsub-available-topics` to find the topics you are interested in.

The function you hand in as callback will be called whenever that event happens with the event data as a parameter,
the type of that parameter is also listed in the link above.

************
Code Example
************

.. code-block:: python

    from twitchAPI.helper import first
    from twitchAPI.twitch import Twitch
    from twitchAPI.oauth import UserAuthenticationStorageHelper
    from twitchAPI.object.eventsub import ChannelFollowEvent
    from twitchAPI.eventsub.websocket import EventSubWebsocket
    from twitchAPI.type import AuthScope
    import asyncio

    APP_ID = 'your_app_id'
    APP_SECRET = 'your_app_secret'
    TARGET_SCOPES = [AuthScope.MODERATOR_READ_FOLLOWERS]


    async def on_follow(data: ChannelFollowEvent):
        # our event happened, lets do things with the data we got!
        print(f'{data.event.user_name} now follows {data.event.broadcaster_user_name}!')


    async def run():
        # create the api instance and get user auth either from storage or website
        twitch = await Twitch(APP_ID, APP_SECRET)
        helper = UserAuthenticationStorageHelper(twitch, TARGET_SCOPES)
        await helper.bind()

        # get the currently logged in user
        user = await first(twitch.get_users())

        # create eventsub websocket instance and start the client.
        eventsub = EventSubWebsocket(twitch)
        eventsub.start()
        # subscribing to the desired eventsub hook for our user
        # the given function (in this example on_follow) will be called every time this event is triggered
        # the broadcaster is a moderator in their own channel by default so specifying both as the same works in this example
        # We have to subscribe to the first topic within 10 seconds of eventsub.start() to not be disconnected.
        await eventsub.listen_channel_follow_v2(user.id, user.id, on_follow)

        # eventsub will run in its own process
        # so lets just wait for user input before shutting it all down again
        try:
            input('press Enter to shut down...')
        except KeyboardInterrupt:
            pass
        finally:
            # stopping both eventsub as well as gracefully closing the connection to the API
            await eventsub.stop()
            await twitch.close()


    asyncio.run(run())
"""
import asyncio
import datetime
import json
import threading
from asyncio import CancelledError
from dataclasses import dataclass
from functools import partial
from time import sleep
from typing import Optional, List, Dict, Callable, Awaitable

import aiohttp
from aiohttp import ClientSession, WSMessage, ClientWebSocketResponse

from .base import EventSubBase


__all__ = ['EventSubWebsocket']

from twitchAPI.twitch import Twitch
from ..helper import TWITCH_EVENT_SUB_WEBSOCKET_URL, done_task_callback
from ..type import AuthType, UnauthorizedException, TwitchBackendException, EventSubSubscriptionConflict, EventSubSubscriptionError, \
    TwitchAuthorizationException


@dataclass
class Session:
    id: str
    keepalive_timeout_seconds: int
    status: str
    reconnect_url: str

    @classmethod
    def from_twitch(cls, data: dict):
        return cls(
            id=data.get('id'),
            keepalive_timeout_seconds=data.get('keepalive_timeout_seconds'),
            status=data.get('status'),
            reconnect_url=data.get('reconnect_url'),
        )


@dataclass
class Reconnect:
    session: Session
    connection: ClientWebSocketResponse


class EventSubWebsocket(EventSubBase):
    _reconnect: Optional[Reconnect] = None
    
    def __init__(self,
                 twitch: Twitch,
                 connection_url: Optional[str] = None,
                 subscription_url: Optional[str] = None,
                 callback_loop: Optional[asyncio.AbstractEventLoop] = None,
                 revocation_handler: Optional[Callable[[dict], Awaitable[None]]] = None):
        """
        :param twitch: The Twitch instance to be used
        :param connection_url: Alternative connection URL, useful for development with the twitch-cli
        :param subscription_url: Alternative subscription URL, useful for development with the twitch-cli
        :param callback_loop: The asyncio eventloop to be used for callbacks. \n
            Set this if you or a library you use cares about which asyncio event loop is running the callbacks.
            Defaults to the one used by EventSub Websocket.
        :param revocation_handler: Optional handler for when subscriptions get revoked. |default| :code:`None`
        """
        super().__init__(twitch, 'twitchAPI.eventsub.websocket')
        self.subscription_url: Optional[str] = subscription_url
        """The URL where subscriptions are being sent to. Defaults to :const:`~twitchAPI.helper.TWITCH_API_BASE_URL`"""
        if self.subscription_url is not None and self.subscription_url[-1] != '/':
            self.subscription_url += '/'
        self.connection_url: str = connection_url if connection_url is not None else TWITCH_EVENT_SUB_WEBSOCKET_URL
        """The URL where the websocket connects to. Defaults to :const:`~twitchAPI.helper.TWITCH_EVENT_SUB_WEBSOCKET_URL`"""
        self.active_session: Optional[Session] = None
        """The currently used session"""
        self._running: bool = False
        self._socket_thread = None
        self._startup_complete: bool = False
        self._socket_loop = None
        self._ready: bool = False
        self._closing: bool = False
        self._connection = None
        self._session = None
        self._callback_loop = callback_loop
        self._is_reconnecting: bool = False
        self._active_subscriptions = {}
        self.revokation_handler: Optional[Callable[[dict], Awaitable[None]]] = revocation_handler
        """Optional handler for when subscriptions get revoked."""
        self._task_callback = partial(done_task_callback, self.logger)
        self._reconnect_timeout: Optional[datetime.datetime] = None
        self.reconnect_delay_steps: List[int] = [0, 1, 2, 4, 8, 16, 32, 64, 128]
        """Time in seconds between reconnect attempts"""

    def start(self):
        """Starts the EventSub client

        :raises RuntimeError: If EventSub is already running
        :raises ~twitchAPI.type.UnauthorizedException: If Twitch instance is missing user authentication
        """
        self.logger.debug('starting websocket EventSub...')
        if self._running:
            raise RuntimeError('EventSubWebsocket is already started!')
        if not self._twitch.has_required_auth(AuthType.USER, []):
            raise UnauthorizedException('Twitch needs user authentication')
        self._startup_complete = False
        self._ready = False
        self._closing = False
        self._socket_thread = threading.Thread(target=self._run_socket)
        self._running = True
        self._active_subscriptions = {}
        self._socket_thread.start()
        while not self._startup_complete:
            sleep(0.01)
        self.logger.debug('EventSubWebsocket started up!')

    async def stop(self):
        """Stops the EventSub client

        :raises RuntimeError: If EventSub is not running
        """
        if not self._running:
            raise RuntimeError('EventSubWebsocket is not running')
        self.logger.debug('stopping websocket EventSub...')
        self._startup_complete = False
        self._running = False
        self._ready = False
        f = asyncio.run_coroutine_threadsafe(self._stop(), self._socket_loop)
        f.result()

    def _get_transport(self):
        return {
            'method': 'websocket',
            'session_id': self.active_session.id
        }

    async def _subscribe(self, sub_type: str, sub_version: str, condition: dict, callback, event, is_batching_enabled: Optional[bool] = None) -> str:
        if not asyncio.iscoroutinefunction(callback):
            raise ValueError('callback needs to be a async function which takes one parameter')
        self.logger.debug(f'subscribe to {sub_type} version {sub_version} with condition {condition}')
        data = {
            'type': sub_type,
            'version': sub_version,
            'condition': condition,
            'transport': self._get_transport()
        }
        if is_batching_enabled is not None:
            data['is_batching_enabled'] = is_batching_enabled
        async with ClientSession(timeout=self._twitch.session_timeout) as session:
            sub_base = self.subscription_url if self.subscription_url is not None else self._twitch.base_url
            r_data = await self._api_post_request(session, sub_base + 'eventsub/subscriptions', data=data)
            result = await r_data.json()
        error = result.get('error')
        if r_data.status == 500:
            raise TwitchBackendException(error)
        if error is not None:
            if error.lower() == 'conflict':
                raise EventSubSubscriptionConflict(result.get('message', ''))
            raise EventSubSubscriptionError(result.get('message'))
        sub_id = result['data'][0]['id']
        self.logger.debug(f'subscription for {sub_type} version {sub_version} with condition {condition} has id {sub_id}')
        self._add_callback(sub_id, callback, event)
        self._callbacks[sub_id]['active'] = True
        self._active_subscriptions[sub_id] = {
            'sub_type': sub_type,
            'sub_version': sub_version,
            'condition': condition,
            'callback': callback,
            'event': event
        }
        return sub_id

    async def _connect(self, is_startup: bool = False):
        if is_startup:
            self.logger.debug(f'connecting to {self.connection_url}...')
        else:
            self._is_reconnecting = True
            self.logger.debug(f'reconnecting using {self.connection_url}...')
        self._reconnect_timeout = None
        if self._connection is not None and not self._connection.closed:
            await self._connection.close()
            while not self._connection.closed:
                await asyncio.sleep(0.1)
        retry = 0
        need_retry = True
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self._twitch.session_timeout)
        while need_retry and retry < len(self.reconnect_delay_steps):
            need_retry = False
            try:
                self._connection = await self._session.ws_connect(self.connection_url)
            except Exception:
                self.logger.warning(f'connection attempt failed, retry in {self.reconnect_delay_steps[retry]} seconds...')
                await asyncio.sleep(self.reconnect_delay_steps[retry])
                retry += 1
                need_retry = True
        if retry >= len(self.reconnect_delay_steps):
            raise TwitchBackendException(f'can\'t connect to EventSub websocket {self.connection_url}')

    def _run_socket(self):
        self._socket_loop = asyncio.new_event_loop()
        if self._callback_loop is None:
            self._callback_loop = self._socket_loop
        asyncio.set_event_loop(self._socket_loop)

        self._socket_loop.run_until_complete(self._connect(is_startup=True))

        self._tasks = [
            asyncio.ensure_future(self._task_receive(), loop=self._socket_loop),
            asyncio.ensure_future(self._task_reconnect_handler(), loop=self._socket_loop)
        ]
        self._socket_loop.run_until_complete(self._keep_loop_alive())

    async def _stop(self):
        await self._connection.close()
        await self._session.close()
        await asyncio.sleep(0.25)
        self._connection = None
        self._session = None
        self._closing = True

    async def _keep_loop_alive(self):
        while not self._closing:
            await asyncio.sleep(0.1)

    async def _task_reconnect_handler(self):
        try:
            while not self._closing:
                await asyncio.sleep(0.1)
                if self._reconnect_timeout is None:
                    continue
                if self._reconnect_timeout <= datetime.datetime.now():
                    self.logger.warning('keepalive missed, connection lost. reconnecting...')
                    self._reconnect_timeout = None
                    await self._connect(is_startup=False)
        except CancelledError:
            return

    async def _task_receive(self):
        handler: Dict[str, Callable] = {
            'session_welcome': self._handle_welcome,
            'session_keepalive': self._handle_keepalive,
            'notification': self._handle_notification,
            'session_reconnect': self._handle_reconnect,
            'revocation': self._handle_revocation
        }
        try:
            while not self._closing:
                if self._connection.closed:
                    await asyncio.sleep(0.01)
                    continue
                message: WSMessage = await self._connection.receive()
                if message.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(message.data)
                    _type = data.get('metadata', {}).get('message_type')
                    _handler = handler.get(_type)
                    if _handler is not None:
                        asyncio.ensure_future(_handler(data))
                    # debug
                    else:
                        self.logger.warning(f'got message for unknown message_type: {_type}, ignoring...')
                elif message.type == aiohttp.WSMsgType.CLOSE:
                    msg_lookup = {
                        4000: "4000 - Internal server error",
                        4001: "4001 - Client sent inbound traffic",
                        4002: "4002 - Client failed ping-pong",
                        4003: "4003 - Connection unused, you have to create a subscription within 10 seconds",
                        4004: "4004 - Reconnect grace time expired",
                        4005: "4005 - Network timeout",
                        4006: "4006 - Network error",
                        4007: "4007 - Invalid reconnect"
                    }
                    self.logger.info(f'Websocket closing: {msg_lookup.get(message.data, f" {message.data} - Unknown")}')
                elif message.type == aiohttp.WSMsgType.CLOSING:
                    if self._reconnect and self._reconnect.session.status == "connected":
                        self._connection = self._reconnect.connection
                        self.active_session = self._reconnect.session
                        self._reconnect = None
                        self.logger.debug("websocket session_reconnect completed")
                        continue
                elif message.type == aiohttp.WSMsgType.CLOSED:
                    self.logger.debug('websocket is closing')
                    if self._running:
                        if self._is_reconnecting:
                            continue
                        try:
                            await self._connect(is_startup=False)
                        except TwitchBackendException:
                            self.logger.exception('Connection to EventSub websocket lost and unable to reestablish connection!')
                            break
                    else:
                        break
                elif message.type == aiohttp.WSMsgType.ERROR:
                    self.logger.warning('error in websocket: ' + str(self._connection.exception()))
                    break
        except CancelledError:
            return

    async def _build_request_header(self):
        token = await self._twitch.get_refreshed_user_auth_token()
        if token is None:
            raise TwitchAuthorizationException('no Authorization set!')
        return {
            'Client-ID': self._twitch.app_id,
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

    async def _unsubscribe_hook(self, topic_id: str) -> bool:
        self._active_subscriptions.pop(topic_id, None)
        return True

    async def _resubscribe(self):
        self.logger.debug('resubscribe to all active subscriptions of this websocket...')
        subs = self._active_subscriptions.copy()
        self._active_subscriptions = {}
        try:
            for sub in subs.values():
                await self._subscribe(**sub)
        except:
            self.logger.exception('exception while resubscribing')
            if not self._active_subscriptions:  # Restore old subscriptions for next reconnect
                self._active_subscriptions = subs
            return
        self.logger.debug('done resubscribing!')

    def _reset_timeout(self):
        self._reconnect_timeout = datetime.datetime.now() + datetime.timedelta(seconds=self.active_session.keepalive_timeout_seconds*2)

    async def _handle_revocation(self, data: dict):
        _payload = data.get('payload', {})
        sub_id: str = _payload.get('subscription', {}).get('id')
        self.logger.debug(f'got revocation of subscription {sub_id} for reason {_payload.get("subscription").get("status")}')
        if sub_id not in self._active_subscriptions.keys():
            self.logger.warning(f'unknown subscription {sub_id} got revoked. ignore')
            return
        self._active_subscriptions.pop(sub_id)
        self._callbacks.pop(sub_id)
        if self.revokation_handler is not None:
            t = self._callback_loop.create_task(self.revokation_handler(_payload))
            t.add_done_callback(self._task_callback)

    async def _handle_reconnect(self, data: dict):
        session = data.get('payload', {}).get('session', {})
        new_session = Session.from_twitch(session)
        self.logger.debug(f"got request from websocket to reconnect, reconnect url: {new_session.reconnect_url}")
        self._reset_timeout()
        new_connection = None
        retry = 0
        need_retry = True
        while need_retry and retry <= 5:  # We only have up to 30 seconds to move to new connection
            need_retry = False
            try:
                new_connection = await self._session.ws_connect(new_session.reconnect_url)
            except Exception as err:
                self.logger.warning(f"reconnection attempt failed because {err}, retry in {self.reconnect_delay_steps[retry]} seconds...")
                await asyncio.sleep(self.reconnect_delay_steps[retry])
                retry += 1
                need_retry = True
        if new_connection is None:  # We failed to establish new connection, do nothing and force a full refresh
            self.logger.warning(f"Failed to establish connection to {new_session.reconnect_url}, Twitch will close and we'll reconnect")
            return
        reconnect = Reconnect(session=new_session, connection=new_connection)
        try:
            message: WSMessage = await reconnect.connection.receive(timeout=30)
        except asyncio.TimeoutError:
            await reconnect.connection.close()
            self.logger.warning(f"Reconnect socket got a timeout waiting for first message {reconnect.session}")
            return
        self._reset_timeout()
        if message.type != aiohttp.WSMsgType.TEXT:
            self.logger.warning(f"Reconnect socket got an unknown message {message}")
            await reconnect.connection.close()
            return
        data = message.json()
        message_type = data.get('metadata', {}).get('message_type')
        if message_type != "session_welcome":
            self.logger.warning(f"Reconnect socket got a non session_welcome first message {data}")
            await reconnect.connection.close()
            return
        session_dict = data.get('payload', {}).get('session', {})
        reconnect.session = Session.from_twitch(session_dict)
        self._reconnect = reconnect
        await self._connection.close()  # This will wake up _task_receive with a CLOSING message

    async def _handle_welcome(self, data: dict):
        session = data.get('payload', {}).get('session', {})
        self.active_session = Session.from_twitch(session)
        self.logger.debug(f'new session id: {self.active_session.id}')
        self._reset_timeout()
        if self._is_reconnecting:
            await self._resubscribe()
        self._is_reconnecting = False
        self._startup_complete = True

    async def _handle_keepalive(self, data: dict):
        self.logger.debug('got session keep alive')
        self._reset_timeout()

    async def _handle_notification(self, data: dict):
        self._reset_timeout()
        _payload = data.get('payload', {})
        sub_id = _payload.get('subscription', {}).get('id')
        callback = self._callbacks.get(sub_id)
        if callback is None:
            self.logger.error(f'received event for unknown subscription with ID {sub_id}')
        else:
            t = self._callback_loop.create_task(callback['callback'](callback['event'](**_payload)))
            t.add_done_callback(self._task_callback)


==> ./object/__init__.py <==
#  Copyright (c) 2023. Lena "Teekeks" During <info@teawork.de>
"""
Objects used by this Library
----------------------------

.. toctree::
   :hidden:
   :maxdepth: 1

   twitchAPI.object.base
   twitchAPI.object.api
   twitchAPI.object.eventsub

.. autosummary::

   base
   api
   eventsub

"""

__all__ = []


==> ./object/api.py <==
#  Copyright (c) 2022. Lena "Teekeks" During <info@teawork.de>
"""
Objects used by the Twitch API
------------------------------
"""

from datetime import datetime
from typing import Optional, List, Dict

from twitchAPI.object.base import TwitchObject, IterTwitchObject, AsyncIterTwitchObject
from twitchAPI.type import StatusCode, VideoType, HypeTrainContributionMethod, DropsEntitlementFulfillmentStatus, CustomRewardRedemptionStatus, \
    PollStatus, PredictionStatus


__all__ = ['TwitchUser', 'TwitchUserFollow', 'TwitchUserFollowResult', 'DateRange',
           'ExtensionAnalytic', 'GameAnalytics', 'CreatorGoal', 'BitsLeaderboardEntry', 'BitsLeaderboard', 'ProductCost', 'ProductData',
           'ExtensionTransaction', 'ChatSettings', 'CreatedClip', 'Clip', 'CodeStatus', 'Game', 'AutoModStatus', 'BannedUser', 'BanUserResponse',
           'BlockedTerm', 'Moderator', 'CreateStreamMarkerResponse', 'Stream', 'StreamMarker', 'StreamMarkers', 'GetStreamMarkerResponse',
           'BroadcasterSubscription', 'BroadcasterSubscriptions', 'UserSubscription', 'StreamTag', 'TeamUser', 'ChannelTeam', 'UserExtension',
           'ActiveUserExtension', 'UserActiveExtensions', 'VideoMutedSegments', 'Video', 'ChannelInformation', 'SearchChannelResult',
           'SearchCategoryResult', 'StartCommercialResult', 'Cheermote', 'GetCheermotesResponse', 'HypeTrainContribution', 'HypeTrainEventData',
           'HypeTrainEvent', 'DropsEntitlement', 'MaxPerStreamSetting', 'MaxPerUserPerStreamSetting', 'GlobalCooldownSetting', 'CustomReward',
           'PartialCustomReward', 'CustomRewardRedemption', 'ChannelEditor', 'BlockListEntry', 'PollChoice', 'Poll', 'Predictor', 'PredictionOutcome',
           'Prediction', 'RaidStartResult', 'ChatBadgeVersion', 'ChatBadge', 'Emote', 'UserEmote', 'GetEmotesResponse', 'EventSubSubscription',
           'GetEventSubSubscriptionResult', 'StreamCategory', 'ChannelStreamScheduleSegment', 'StreamVacation', 'ChannelStreamSchedule',
           'ChannelVIP', 'UserChatColor', 'Chatter', 'GetChattersResponse', 'ShieldModeStatus', 'CharityAmount', 'CharityCampaign',
           'CharityCampaignDonation', 'AutoModSettings', 'ChannelFollower', 'ChannelFollowersResult', 'FollowedChannel', 'FollowedChannelsResult',
           'ContentClassificationLabel', 'AdSchedule', 'AdSnoozeResponse', 'SendMessageResponse', 'ChannelModerator', 'UserEmotesResponse',
           'WarnResponse', 'SharedChatParticipant', 'SharedChatSession']


class TwitchUser(TwitchObject):
    id: str
    login: str
    display_name: str
    type: str
    broadcaster_type: str
    description: str
    profile_image_url: str
    offline_image_url: str
    view_count: int
    email: str = None
    created_at: datetime


class TwitchUserFollow(TwitchObject):
    from_id: str
    from_login: str
    from_name: str
    to_id: str
    to_login: str
    to_name: str
    followed_at: datetime


class TwitchUserFollowResult(AsyncIterTwitchObject[TwitchUserFollow]):
    total: int
    data: List[TwitchUserFollow]


class ChannelFollower(TwitchObject):
    followed_at: datetime
    user_id: str
    user_name: str
    user_login: str


class ChannelFollowersResult(AsyncIterTwitchObject[ChannelFollower]):
    total: int
    data: List[ChannelFollower]


class FollowedChannel(TwitchObject):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    followed_at: datetime


class FollowedChannelsResult(AsyncIterTwitchObject[FollowedChannel]):
    total: int
    data: List[FollowedChannel]


class DateRange(TwitchObject):
    ended_at: datetime
    started_at: datetime


class ExtensionAnalytic(TwitchObject):
    extension_id: str
    URL: str
    type: str
    date_range: DateRange


class GameAnalytics(TwitchObject):
    game_id: str
    URL: str
    type: str
    date_range: DateRange


class CreatorGoal(TwitchObject):
    id: str
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    type: str
    description: str
    current_amount: int
    target_amount: int
    created_at: datetime


class BitsLeaderboardEntry(TwitchObject):
    user_id: str
    user_login: str
    user_name: str
    rank: int
    score: int


class BitsLeaderboard(IterTwitchObject):
    data: List[BitsLeaderboardEntry]
    date_range: DateRange
    total: int


class ProductCost(TwitchObject):
    amount: int
    type: str


class ProductData(TwitchObject):
    domain: str
    sku: str
    cost: ProductCost


class ExtensionTransaction(TwitchObject):
    id: str
    timestamp: datetime
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    user_id: str
    user_login: str
    user_name: str
    product_type: str
    product_data: ProductData
    inDevelopment: bool
    displayName: str
    expiration: str
    broadcast: str


class ChatSettings(TwitchObject):
    broadcaster_id: str
    moderator_id: str
    emote_mode: bool
    slow_mode: bool
    slow_mode_wait_time: int
    follower_mode: bool
    follower_mode_duration: int
    subscriber_mode: bool
    unique_chat_mode: bool
    non_moderator_chat_delay: bool
    non_moderator_chat_delay_duration: int


class CreatedClip(TwitchObject):
    id: str
    edit_url: str


class Clip(TwitchObject):
    id: str
    url: str
    embed_url: str
    broadcaster_id: str
    broadcaster_name: str
    creator_id: str
    creator_name: str
    video_id: str
    game_id: str
    language: str
    title: str
    view_count: int
    created_at: datetime
    thumbnail_url: str
    duration: float
    vod_offset: int
    is_featured: bool


class CodeStatus(TwitchObject):
    code: str
    status: StatusCode


class Game(TwitchObject):
    box_art_url: str
    id: str
    name: str
    igdb_id: str


class AutoModStatus(TwitchObject):
    msg_id: str
    is_permitted: bool


class BannedUser(TwitchObject):
    user_id: str
    user_login: str
    user_name: str
    expires_at: datetime
    created_at: datetime
    reason: str
    moderator_id: str
    moderator_login: str
    moderator_name: str


class BanUserResponse(TwitchObject):
    broadcaster_id: str
    moderator_id: str
    user_id: str
    created_at: datetime
    end_time: datetime


class BlockedTerm(TwitchObject):
    broadcaster_id: str
    moderator_id: str
    id: str
    text: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime


class Moderator(TwitchObject):
    user_id: str
    user_login: str
    user_name: str


class CreateStreamMarkerResponse(TwitchObject):
    id: str
    created_at: datetime
    description: str
    position_seconds: int


class Stream(TwitchObject):
    id: str
    user_id: str
    user_login: str
    user_name: str
    game_id: str
    game_name: str
    type: str
    title: str
    viewer_count: int
    started_at: datetime
    language: str
    thumbnail_url: str
    tag_ids: List[str]
    is_mature: bool
    tags: List[str]


class StreamMarker(TwitchObject):
    id: str
    created_at: datetime
    description: str
    position_seconds: int
    URL: str


class StreamMarkers(TwitchObject):
    video_id: str
    markers: List[StreamMarker]


class GetStreamMarkerResponse(TwitchObject):
    user_id: str
    user_name: str
    user_login: str
    videos: List[StreamMarkers]


class BroadcasterSubscription(TwitchObject):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    gifter_id: str
    gifter_login: str
    gifter_name: str
    is_gift: bool
    tier: str
    plan_name: str
    user_id: str
    user_name: str
    user_login: str


class BroadcasterSubscriptions(AsyncIterTwitchObject[BroadcasterSubscription]):
    total: int
    points: int
    data: List[BroadcasterSubscription]


class UserSubscription(TwitchObject):
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    is_gift: bool
    tier: str


class StreamTag(TwitchObject):
    tag_id: str
    is_auto: bool
    localization_names: Dict[str, str]
    localization_descriptions: Dict[str, str]


class TeamUser(TwitchObject):
    user_id: str
    user_name: str
    user_login: str


class ChannelTeam(TwitchObject):
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    background_image_url: str
    banner: str
    users: Optional[List[TeamUser]]
    created_at: datetime
    updated_at: datetime
    info: str
    thumbnail_url: str
    team_name: str
    team_display_name: str
    id: str


class UserExtension(TwitchObject):
    id: str
    version: str
    can_activate: bool
    type: List[str]
    name: str


class ActiveUserExtension(UserExtension):
    x: int
    y: int
    active: bool


class UserActiveExtensions(TwitchObject):
    panel: Dict[str, ActiveUserExtension]
    overlay: Dict[str, ActiveUserExtension]
    component: Dict[str, ActiveUserExtension]


class VideoMutedSegments(TwitchObject):
    duration: int
    offset: int


class Video(TwitchObject):
    id: str
    stream_id: str
    user_id: str
    user_login: str
    user_name: str
    title: str
    description: str
    created_at: datetime
    published_at: datetime
    url: str
    thumbnail_url: str
    viewable: str
    view_count: int
    language: str
    type: VideoType
    duration: str
    muted_segments: List[VideoMutedSegments]


class ChannelInformation(TwitchObject):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    game_name: str
    game_id: str
    broadcaster_language: str
    title: str
    delay: int
    tags: List[str]
    content_classification_labels: List[str]
    is_branded_content: bool


class SearchChannelResult(TwitchObject):
    broadcaster_language: str
    """The ISO 639-1 two-letter language code of the language used by the broadcaster. For example, en for English. 
    If the broadcaster uses a language not in the list of supported stream languages, the value is other."""
    broadcaster_login: str
    """The broadcaster’s login name."""
    display_name: str
    """The broadcaster’s display name."""
    game_id: str
    """The ID of the game that the broadcaster is playing or last played."""
    game_name: str
    """The name of the game that the broadcaster is playing or last played."""
    id: str
    """An ID that uniquely identifies the channel (this is the broadcaster’s ID)."""
    is_live: bool
    """A Boolean value that determines whether the broadcaster is streaming live. Is True if the broadcaster is streaming live; otherwise, False."""
    tags: List[str]
    """The tags applied to the channel."""
    thumbnail_url: str
    """A URL to a thumbnail of the broadcaster’s profile image."""
    title: str
    """The stream’s title. Is an empty string if the broadcaster didn’t set it."""
    started_at: Optional[datetime]
    """The datetime of when the broadcaster started streaming. None if the broadcaster is not streaming live."""


class SearchCategoryResult(TwitchObject):
    id: str
    name: str
    box_art_url: str


class StartCommercialResult(TwitchObject):
    length: int
    message: str
    retry_after: int


class Cheermote(TwitchObject):
    min_bits: int
    id: str
    color: str
    images: Dict[str, Dict[str, Dict[str, str]]]
    can_cheer: bool
    show_in_bits_card: bool


class GetCheermotesResponse(TwitchObject):
    prefix: str
    tiers: List[Cheermote]
    type: str
    order: int
    last_updated: datetime
    is_charitable: bool


class HypeTrainContribution(TwitchObject):
    total: int
    type: HypeTrainContributionMethod
    user: str


class HypeTrainEventData(TwitchObject):
    broadcaster_id: str
    cooldown_end_time: datetime
    expires_at: datetime
    goal: int
    id: str
    last_contribution: HypeTrainContribution
    level: int
    started_at: datetime
    top_contributions: List[HypeTrainContribution]
    total: int


class HypeTrainEvent(TwitchObject):
    id: str
    event_type: str
    event_timestamp: datetime
    version: str
    event_data: HypeTrainEventData


class DropsEntitlement(TwitchObject):
    id: str
    benefit_id: str
    timestamp: datetime
    user_id: str
    game_id: str
    fulfillment_status: DropsEntitlementFulfillmentStatus
    updated_at: datetime


class MaxPerStreamSetting(TwitchObject):
    is_enabled: bool
    max_per_stream: int


class MaxPerUserPerStreamSetting(TwitchObject):
    is_enabled: bool
    max_per_user_per_stream: int


class GlobalCooldownSetting(TwitchObject):
    is_enabled: bool
    global_cooldown_seconds: int


class CustomReward(TwitchObject):
    broadcaster_name: str
    broadcaster_login: str
    broadcaster_id: str
    id: str
    image: Dict[str, str]
    background_color: str
    is_enabled: bool
    cost: int
    title: str
    prompt: str
    is_user_input_required: bool
    max_per_stream_setting: MaxPerStreamSetting
    max_per_user_per_stream_setting: MaxPerUserPerStreamSetting
    global_cooldown_setting: GlobalCooldownSetting
    is_paused: bool
    is_in_stock: bool
    default_image: Dict[str, str]
    should_redemptions_skip_request_queue: bool
    redemptions_redeemed_current_stream: int
    cooldown_expires_at: datetime


class PartialCustomReward(TwitchObject):
    id: str
    title: str
    prompt: str
    cost: int


class CustomRewardRedemption(TwitchObject):
    broadcaster_name: str
    broadcaster_login: str
    broadcaster_id: str
    id: str
    user_id: str
    user_name: str
    user_input: str
    status: CustomRewardRedemptionStatus
    redeemed_at: datetime
    reward: PartialCustomReward


class ChannelEditor(TwitchObject):
    user_id: str
    user_name: str
    created_at: datetime


class BlockListEntry(TwitchObject):
    user_id: str
    user_login: str
    user_name: str


class PollChoice(TwitchObject):
    id: str
    title: str
    votes: int
    channel_point_votes: int


class Poll(TwitchObject):
    id: str
    broadcaster_name: str
    broadcaster_id: str
    broadcaster_login: str
    title: str
    choices: List[PollChoice]
    channel_point_voting_enabled: bool
    channel_points_per_vote: int
    status: PollStatus
    duration: int
    started_at: datetime


class Predictor(TwitchObject):
    user_id: str
    user_name: str
    user_login: str
    channel_points_used: int
    channel_points_won: int


class PredictionOutcome(TwitchObject):
    id: str
    title: str
    users: int
    channel_points: int
    top_predictors: Optional[List[Predictor]]
    color: str


class Prediction(TwitchObject):
    id: str
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    title: str
    winning_outcome_id: Optional[str]
    outcomes: List[PredictionOutcome]
    prediction_window: int
    status: PredictionStatus
    created_at: datetime
    ended_at: Optional[datetime]
    locked_at: Optional[datetime]


class RaidStartResult(TwitchObject):
    created_at: datetime
    is_mature: bool


class ChatBadgeVersion(TwitchObject):
    id: str
    image_url_1x: str
    image_url_2x: str
    image_url_4x: str
    title: str
    description: str
    click_action: Optional[str]
    click_url: Optional[str]


class ChatBadge(TwitchObject):
    set_id: str
    versions: List[ChatBadgeVersion]


class Emote(TwitchObject):
    id: str
    name: str
    images: Dict[str, str]
    tier: str
    emote_type: str
    emote_set_id: str
    format: List[str]
    scale: List[str]
    theme_mode: List[str]


class UserEmote(Emote):
    owner_id: str


class GetEmotesResponse(IterTwitchObject):
    data: List[Emote]
    template: str


class EventSubSubscription(TwitchObject):
    id: str
    status: str
    type: str
    version: str
    condition: Dict[str, str]
    created_at: datetime
    transport: Dict[str, str]
    cost: int


class GetEventSubSubscriptionResult(AsyncIterTwitchObject[EventSubSubscription]):
    total: int
    total_cost: int
    max_total_cost: int
    data: List[EventSubSubscription]


class StreamCategory(TwitchObject):
    id: str
    name: str


class ChannelStreamScheduleSegment(TwitchObject):
    id: str
    start_time: datetime
    end_time: datetime
    title: str
    canceled_until: Optional[datetime]
    category: StreamCategory
    is_recurring: bool


class StreamVacation(TwitchObject):
    start_time: datetime
    end_time: datetime


class ChannelStreamSchedule(AsyncIterTwitchObject[ChannelStreamScheduleSegment]):
    segments: List[ChannelStreamScheduleSegment]
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    vacation: Optional[StreamVacation]


class ChannelVIP(TwitchObject):
    user_id: str
    user_name: str
    user_login: str


class UserChatColor(TwitchObject):
    user_id: str
    user_name: str
    user_login: str
    color: str


class Chatter(TwitchObject):
    user_id: str
    user_login: str
    user_name: str


class GetChattersResponse(AsyncIterTwitchObject[Chatter]):
    data: List[Chatter]
    total: int


class ShieldModeStatus(TwitchObject):
    is_active: bool
    moderator_id: str
    moderator_login: str
    moderator_name: str
    last_activated_at: Optional[datetime]


class CharityAmount(TwitchObject):
    value: int
    decimal_places: int
    currency: str


class CharityCampaign(TwitchObject):
    id: str
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    current_amount: CharityAmount
    target_amount: CharityAmount


class CharityCampaignDonation(TwitchObject):
    id: str
    campaign_id: str
    user_id: str
    user_name: str
    user_login: str
    amount: CharityAmount


class AutoModSettings(TwitchObject):
    broadcaster_id: str
    moderator_id: str
    overall_level: Optional[int]
    disability: int
    aggression: int
    sexuality_sex_or_gender: int
    misogyny: int
    bullying: int
    swearing: int
    race_ethnicity_or_religion: int
    sex_based_terms: int


class ContentClassificationLabel(TwitchObject):
    id: str
    description: str
    name: str


class AdSchedule(TwitchObject):
    snooze_count: int
    """The number of snoozes available for the broadcaster."""
    snooze_refresh_at: Optional[datetime]
    """The UTC timestamp when the broadcaster will gain an additional snooze."""
    next_ad_at: Optional[datetime]
    """The UTC timestamp of the broadcaster’s next scheduled ad. Empty if the channel has no ad scheduled or is not live."""
    duration: int
    """The length in seconds of the scheduled upcoming ad break."""
    last_ad_at: Optional[datetime]
    """The UTC timestamp of the broadcaster’s last ad-break. Empty if the channel has not run an ad or is not live."""
    preroll_free_time: int
    """The amount of pre-roll free time remaining for the channel in seconds. Returns 0 if they are currently not pre-roll free."""


class AdSnoozeResponse(TwitchObject):
    snooze_count: int
    """The number of snoozes available for the broadcaster."""
    snooze_refresh_at: Optional[datetime]
    """The UTC timestamp when the broadcaster will gain an additional snooze"""
    next_ad_at: Optional[datetime]
    """The UTC timestamp of the broadcaster’s next scheduled ad"""


class SendMessageDropReason(TwitchObject):
    code: str
    """Code for why the message was dropped."""
    message: str
    """Message for why the message was dropped."""


class SendMessageResponse(TwitchObject):
    message_id: str
    """The message id for the message that was sent."""
    is_sent: bool
    """If the message passed all checks and was sent."""
    drop_reason: Optional[SendMessageDropReason]
    """The reason the message was dropped, if any."""


class ChannelModerator(TwitchObject):
    broadcaster_id: str
    """An ID that uniquely identifies the channel this user can moderate."""
    broadcaster_login: str
    """The channel’s login name."""
    broadcaster_name: str
    """The channels’ display name."""


class UserEmotesResponse(AsyncIterTwitchObject):
    template: str
    """A templated URL. Uses the values from the id, format, scale, and theme_mode fields to replace the like-named placeholder strings in the 
    templated URL to create a CDN (content delivery network) URL that you use to fetch the emote."""
    data: List[UserEmote]


class WarnResponse(TwitchObject):
    broadcaster_id: str
    """The ID of the channel in which the warning will take effect."""
    user_id: str
    """The ID of the warned user."""
    moderator_id: str
    """The ID of the user who applied the warning."""
    reason: str
    """The reason provided for warning."""


class SharedChatParticipant(TwitchObject):
    broadcaster_id: str
    """The User ID of the participant channel."""


class SharedChatSession(TwitchObject):
    session_id: str
    """The unique identifier for the shared chat session."""
    host_broadcaster_id: str
    """The User ID of the host channel."""
    participants: List[SharedChatParticipant]
    """The list of participants in the session."""
    created_at: datetime
    """The UTC timestamp when the session was created."""
    updated_at: datetime
    """The UTC timestamp when the session was last updated."""

==> ./object/base.py <==
#  Copyright (c) 2023. Lena "Teekeks" During <info@teawork.de>
"""
Base Objects used by the Library
--------------------------------
"""
from datetime import datetime
from enum import Enum
from typing import TypeVar, Union, Generic, Optional

from aiohttp import ClientSession
from dateutil import parser as du_parser

from twitchAPI.helper import build_url

T = TypeVar('T')

__all__ = ['TwitchObject', 'IterTwitchObject', 'AsyncIterTwitchObject']


class TwitchObject:
    """
    A lot of API calls return a child of this in some way (either directly or via generator).
    You can always use the :const:`~twitchAPI.object.TwitchObject.to_dict()` method to turn that object to a dictionary.

    Example:

    .. code-block:: python

        blocked_term = await twitch.add_blocked_term('broadcaster_id', 'moderator_id', 'bad_word')
        print(blocked_term.id)"""
    @staticmethod
    def _val_by_instance(instance, val):
        if val is None:
            return None
        origin = instance.__origin__ if hasattr(instance, '__origin__') else None
        if instance == datetime:
            if isinstance(val, int):
                # assume unix timestamp
                return None if val == 0 else datetime.fromtimestamp(val)
            # assume ISO8601 string
            return du_parser.isoparse(val) if len(val) > 0 else None
        elif origin == list:
            c = instance.__args__[0]
            return [TwitchObject._val_by_instance(c, x) for x in val]
        elif origin == dict:
            c1 = instance.__args__[0]
            c2 = instance.__args__[1]
            return {TwitchObject._val_by_instance(c1, x1): TwitchObject._val_by_instance(c2, x2) for x1, x2 in val.items()}
        elif origin == Union:
            # TODO: only works for optional pattern, fix to try out all possible patterns?
            c1 = instance.__args__[0]
            return TwitchObject._val_by_instance(c1, val)
        elif issubclass(instance, TwitchObject):
            return instance(**val)
        else:
            return instance(val)

    @staticmethod
    def _dict_val_by_instance(instance, val, include_none_values):
        if val is None:
            return None
        if instance is None:
            return val
        origin = instance.__origin__ if hasattr(instance, '__origin__') else None
        if instance == datetime:
            return val.isoformat() if val is not None else None
        elif origin == list:
            c = instance.__args__[0]
            return [TwitchObject._dict_val_by_instance(c, x, include_none_values) for x in val]
        elif origin == dict:
            c1 = instance.__args__[0]
            c2 = instance.__args__[1]
            return {TwitchObject._dict_val_by_instance(c1, x1, include_none_values):
                    TwitchObject._dict_val_by_instance(c2, x2, include_none_values) for x1, x2 in val.items()}
        elif origin == Union:
            # TODO: only works for optional pattern, fix to try out all possible patterns?
            c1 = instance.__args__[0]
            return TwitchObject._dict_val_by_instance(c1, val, include_none_values)
        elif issubclass(instance, TwitchObject):
            return val.to_dict(include_none_values)
        elif isinstance(val, Enum):
            return val.value
        return instance(val)

    @classmethod
    def _get_annotations(cls):
        d = {}
        for c in cls.mro():
            try:
                d.update(**c.__annotations__)
            except AttributeError:
                pass
        return d

    def to_dict(self, include_none_values: bool = False) -> dict:
        """build dict based on annotation types

        :param include_none_values: if fields that have None values should be included in the dictionary
        """
        d = {}
        annotations = self._get_annotations()
        for name, val in self.__dict__.items():
            val = None
            cls = annotations.get(name)
            try:
                val = getattr(self, name)
            except AttributeError:
                pass
            if val is None and not include_none_values:
                continue
            if name[0] == '_':
                continue
            d[name] = TwitchObject._dict_val_by_instance(cls, val, include_none_values)
        return d

    def __init__(self, **kwargs):
        merged_annotations = self._get_annotations()
        for name, cls in merged_annotations.items():
            if name not in kwargs.keys():
                continue
            self.__setattr__(name, TwitchObject._val_by_instance(cls, kwargs.get(name)))

    def __repr__(self):
        merged_annotations = self._get_annotations()
        args = ', '.join(['='.join([name, str(self.__getattribute__(name))]) for name in merged_annotations.keys()])
        return f'{type(self).__name__}({args})'


class IterTwitchObject(TwitchObject):
    """Special type of :const:`~twitchAPI.object.TwitchObject`.
       These usually have some list inside that you may want to directly iterate over in your API usage but that also contain other useful data
       outside of that List.

       Example:

       .. code-block:: python

          lb = await twitch.get_bits_leaderboard()
          print(lb.total)
          for e in lb:
              print(f'#{e.rank:02d} - {e.user_name}: {e.score}')"""

    def __iter__(self):
        if not hasattr(self, 'data') or not isinstance(self.__getattribute__('data'), list):
            raise ValueError('Object is missing data attribute of type list')
        for i in self.__getattribute__('data'):
            yield i


class AsyncIterTwitchObject(TwitchObject, Generic[T]):
    """A few API calls will have useful data outside the list the pagination iterates over.
       For those cases, this object exist.

       Example:

       .. code-block:: python

           schedule = await twitch.get_channel_stream_schedule('user_id')
           print(schedule.broadcaster_name)
           async for segment in schedule:
               print(segment.title)"""

    def __init__(self, _data, **kwargs):
        super(AsyncIterTwitchObject, self).__init__(**kwargs)
        self.__idx = 0
        self._data = _data

    def __aiter__(self):
        return self

    def current_cursor(self) -> Optional[str]:
        """Provides the currently used forward pagination cursor"""
        return self._data['param'].get('after')

    async def __anext__(self) -> T:
        if not hasattr(self, self._data['iter_field']) or not isinstance(self.__getattribute__(self._data['iter_field']), list):
            raise ValueError(f'Object is missing {self._data["iter_field"]} attribute of type list')
        data = self.__getattribute__(self._data['iter_field'])
        if len(data) > self.__idx:
            self.__idx += 1
            return data[self.__idx - 1]
        # make request
        if self._data['param']['after'] is None:
            raise StopAsyncIteration()
        _url = build_url(self._data['url'], self._data['param'], remove_none=True, split_lists=self._data['split'])
        async with ClientSession() as session:
            response = await self._data['req'](self._data['method'], session, _url, self._data['auth_t'], self._data['auth_s'], self._data['body'])
            _data = await response.json()
        _after = _data.get('pagination', {}).get('cursor')
        self._data['param']['after'] = _after
        if self._data['in_data']:
            _data = _data['data']
        # refill data
        merged_annotations = self._get_annotations()
        for name, cls in merged_annotations.items():
            if name not in _data.keys():
                continue
            self.__setattr__(name, TwitchObject._val_by_instance(cls, _data.get(name)))
        data = self.__getattribute__(self._data['iter_field'])
        self.__idx = 1
        if len(data) == 0:
            raise StopAsyncIteration()
        return data[self.__idx - 1]

==> ./object/eventsub.py <==
#  Copyright (c) 2023. Lena "Teekeks" During <info@teawork.de>
"""
Objects used by EventSub
------------------------
"""


from twitchAPI.object.base import TwitchObject
from datetime import datetime
from typing import List, Optional

__all__ = ['ChannelPollBeginEvent', 'ChannelUpdateEvent', 'ChannelFollowEvent', 'ChannelSubscribeEvent', 'ChannelSubscriptionEndEvent',
           'ChannelSubscriptionGiftEvent', 'ChannelSubscriptionMessageEvent', 'ChannelCheerEvent', 'ChannelRaidEvent', 'ChannelBanEvent',
           'ChannelUnbanEvent', 'ChannelModeratorAddEvent', 'ChannelModeratorRemoveEvent', 'ChannelPointsCustomRewardAddEvent',
           'ChannelPointsCustomRewardUpdateEvent', 'ChannelPointsCustomRewardRemoveEvent', 'ChannelPointsCustomRewardRedemptionAddEvent',
           'ChannelPointsCustomRewardRedemptionUpdateEvent', 'ChannelPollProgressEvent', 'ChannelPollEndEvent', 'ChannelPredictionEvent',
           'ChannelPredictionEndEvent', 'DropEntitlementGrantEvent', 'ExtensionBitsTransactionCreateEvent', 'GoalEvent', 'HypeTrainEvent',
           'HypeTrainEndEvent', 'StreamOnlineEvent', 'StreamOfflineEvent', 'UserAuthorizationGrantEvent', 'UserAuthorizationRevokeEvent',
           'UserUpdateEvent', 'ShieldModeEvent', 'CharityCampaignStartEvent', 'CharityCampaignProgressEvent', 'CharityCampaignStopEvent',
           'CharityDonationEvent', 'ChannelShoutoutCreateEvent', 'ChannelShoutoutReceiveEvent', 'ChannelChatClearEvent',
           'ChannelChatClearUserMessagesEvent', 'ChannelChatMessageDeleteEvent', 'ChannelChatNotificationEvent', 'ChannelAdBreakBeginEvent',
           'ChannelChatMessageEvent', 'ChannelChatSettingsUpdateEvent', 'UserWhisperMessageEvent', 'ChannelPointsAutomaticRewardRedemptionAddEvent',
           'ChannelVIPAddEvent', 'ChannelVIPRemoveEvent', 'ChannelUnbanRequestCreateEvent', 'ChannelUnbanRequestResolveEvent',
           'ChannelSuspiciousUserMessageEvent', 'ChannelSuspiciousUserUpdateEvent', 'ChannelModerateEvent', 'ChannelWarningAcknowledgeEvent',
           'ChannelWarningSendEvent', 'AutomodMessageHoldEvent', 'AutomodMessageUpdateEvent', 'AutomodSettingsUpdateEvent',
           'AutomodTermsUpdateEvent', 'ChannelChatUserMessageHoldEvent', 'ChannelChatUserMessageUpdateEvent', 'ChannelSharedChatBeginEvent',
           'ChannelSharedChatUpdateEvent', 'ChannelSharedChatEndEvent',
           'Subscription', 'ChannelPollBeginData', 'PollChoice', 'BitsVoting', 'ChannelPointsVoting', 'ChannelUpdateData', 'ChannelFollowData',
           'ChannelSubscribeData', 'ChannelSubscriptionEndData', 'ChannelSubscriptionGiftData', 'ChannelSubscriptionMessageData',
           'SubscriptionMessage', 'Emote', 'ChannelCheerData', 'ChannelRaidData', 'ChannelBanData', 'ChannelUnbanData', 'ChannelModeratorAddData',
           'ChannelModeratorRemoveData', 'ChannelPointsCustomRewardData', 'GlobalCooldown', 'Image', 'MaxPerStream', 'MaxPerUserPerStream',
           'ChannelPointsCustomRewardRedemptionData', 'Reward', 'ChannelPollProgressData', 'ChannelPollEndData', 'ChannelPredictionData', 'Outcome',
           'TopPredictors', 'ChannelPredictionEndData', 'DropEntitlementGrantData', 'Entitlement', 'Product', 'ExtensionBitsTransactionCreateData',
           'GoalData', 'TopContribution', 'LastContribution', 'HypeTrainData', 'HypeTrainEndData', 'StreamOnlineData', 'StreamOfflineData',
           'UserAuthorizationGrantData', 'UserAuthorizationRevokeData', 'UserUpdateData', 'ShieldModeData', 'Amount', 'CharityCampaignStartData',
           'CharityCampaignStopData', 'CharityCampaignProgressData', 'CharityDonationData', 'ChannelShoutoutCreateData', 'ChannelShoutoutReceiveData',
           'ChannelChatClearData', 'ChannelChatClearUserMessagesData', 'ChannelChatMessageDeleteData', 'Badge', 'MessageFragmentCheermote',
           'MessageFragmentEmote', 'MessageFragmentMention', 'MessageFragment', 'Message', 'AnnouncementNoticeMetadata',
           'CharityDonationNoticeMetadata', 'BitsBadgeTierNoticeMetadata', 'SubNoticeMetadata', 'RaidNoticeMetadata', 'ResubNoticeMetadata',
           'UnraidNoticeMetadata', 'SubGiftNoticeMetadata', 'CommunitySubGiftNoticeMetadata', 'GiftPaidUpgradeNoticeMetadata',
           'PrimePaidUpgradeNoticeMetadata', 'PayItForwardNoticeMetadata', 'ChannelChatNotificationData', 'ChannelAdBreakBeginData',
           'ChannelChatMessageData', 'ChatMessage', 'ChatMessageBadge', 'ChatMessageFragment', 'ChatMessageFragmentCheermoteMetadata',
           'ChatMessageFragmentMentionMetadata', 'ChatMessageReplyMetadata', 'ChatMessageCheerMetadata', 'ChatMessageFragmentEmoteMetadata',
           'ChannelChatSettingsUpdateData', 'WhisperInformation', 'UserWhisperMessageData', 'AutomaticReward', 'RewardMessage', 'RewardEmote',
           'ChannelPointsAutomaticRewardRedemptionAddData', 'ChannelVIPAddData', 'ChannelVIPRemoveData', 'ChannelUnbanRequestCreateData',
           'ChannelUnbanRequestResolveData', 'MessageWithID', 'ChannelSuspiciousUserMessageData', 'ChannelSuspiciousUserUpdateData',
           'ModerateMetadataSlow', 'ModerateMetadataWarn', 'ModerateMetadataDelete', 'ModerateMetadataTimeout', 'ModerateMetadataUnmod',
           'ModerateMetadataUnvip', 'ModerateMetadataUntimeout', 'ModerateMetadataUnraid', 'ModerateMetadataUnban', 'ModerateMetadataUnbanRequest',
           'ModerateMetadataAutomodTerms', 'ModerateMetadataBan', 'ModerateMetadataMod', 'ModerateMetadataVip', 'ModerateMetadataRaid',
           'ModerateMetadataFollowers', 'ChannelModerateData', 'ChannelWarningAcknowledgeData', 'ChannelWarningSendData', 'AutomodMessageHoldData',
           'AutomodMessageUpdateData', 'AutomodSettingsUpdateData', 'AutomodTermsUpdateData', 'ChannelChatUserMessageHoldData', 'ChannelChatUserMessageUpdateData',
           'SharedChatParticipant', 'ChannelSharedChatBeginData', 'ChannelSharedChatUpdateData', 'ChannelSharedChatEndData']


# Event Data

class Subscription(TwitchObject):
    condition: dict
    cost: int
    created_at: datetime
    id: str
    status: str
    transport: dict
    type: str
    version: str


class PollChoice(TwitchObject):
    id: str
    """ID for the choice"""
    title: str
    """Text displayed for the choice"""
    bits_votes: int
    """Not used; will be stet to 0"""
    channel_points_votes: int
    """Number of votes received via Channel Points"""
    votes: int
    """Total number of votes received for the choice across all methods of voting"""


class BitsVoting(TwitchObject):
    is_enabled: bool
    """Not used; will be set to False"""
    amount_per_vote: int
    """Not used; will be set to 0"""


class ChannelPointsVoting(TwitchObject):
    is_enabled: bool
    """Indicates if Channel Points can be used for Voting"""
    amount_per_vote: int
    """Number of Channel Points required to vote once with Channel Points"""


class ChannelPollBeginData(TwitchObject):
    id: str
    """ID of the poll"""
    broadcaster_user_id: str
    """The requested broadcaster ID"""
    broadcaster_user_login: str
    """The requested broadcaster login"""
    broadcaster_user_name: str
    """The requested broadcaster display name"""
    title: str
    """Question displayed for the poll"""
    choices: List[PollChoice]
    """Array of choices for the poll"""
    bits_voting: BitsVoting
    """Not supported"""
    channel_points_voting: ChannelPointsVoting
    """The Channel Points voting settings for the Poll"""
    started_at: datetime
    """The time the poll started"""
    ends_at: datetime
    """The time the poll will end"""


class ChannelUpdateData(TwitchObject):
    broadcaster_user_id: str
    """The broadcaster’s user ID"""
    broadcaster_user_login: str
    """The broadcaster’s user login"""
    broadcaster_user_name: str
    """The broadcaster’s user display name"""
    title: str
    """The channel’s stream title"""
    language: str
    """The channel’s broadcast language"""
    category_id: str
    """The channel´s category ID"""
    category_name: str
    """The category name"""
    content_classification_labels: List[str]
    """Array of classification label IDs currently applied to the Channel"""


class ChannelFollowData(TwitchObject):
    user_id: str
    """The user ID for the user now following the specified channel"""
    user_login: str
    """The user login for the user now following the specified channel"""
    user_name: str
    """The user display name for the user now following the specified channel"""
    broadcaster_user_id: str
    """The requested broadcaster’s user ID"""
    broadcaster_user_login: str
    """The requested broadcaster’s user login"""
    broadcaster_user_name: str
    """The requested broadcaster’s user display name"""
    followed_at: datetime
    """when the follow occurred"""


class ChannelSubscribeData(TwitchObject):
    user_id: str
    """The user ID for the user who subscribed to the specified channel"""
    user_login: str
    """The user login for the user who subscribed to the specified channel"""
    user_name: str
    """The user display name for the user who subscribed to the specified channel"""
    broadcaster_user_id: str
    """The requested broadcaster’s user ID"""
    broadcaster_user_login: str
    """The requested broadcaster’s user login"""
    broadcaster_user_name: str
    """The requested broadcaster’s user display name"""
    tier: str
    """The tier of the subscription. Valid values are 1000, 2000, and 3000"""
    is_gift: bool
    """Whether the subscription is a gift"""


class ChannelSubscriptionEndData(TwitchObject):
    user_id: str
    """The user ID for the user whose subscription ended"""
    user_login: str
    """The user login for the user whose subscription ended"""
    user_name: str
    """The user display name for the user whose subscription ended"""
    broadcaster_user_id: str
    """The requested broadcaster’s user ID"""
    broadcaster_user_login: str
    """The requested broadcaster’s user login"""
    broadcaster_user_name: str
    """The requested broadcaster’s user display name"""
    tier: str
    """The tier of the subscription that ended. Valid values are 1000, 2000, and 3000"""
    is_gift: bool
    """Whether the subscription was a gift"""


class ChannelSubscriptionGiftData(TwitchObject):
    user_id: Optional[str]
    """The user ID for the user who sent the subscription gift. None if it was an anonymous subscription gift."""
    user_login: Optional[str]
    """The user login for the user who sent the subscription gift. None if it was an anonymous subscription gift."""
    user_name: Optional[str]
    """The user display name for the user who sent the subscription gift. None if it was an anonymous subscription gift."""
    broadcaster_user_id: str
    """The requested broadcaster’s user ID"""
    broadcaster_user_login: str
    """The requested broadcaster’s user login"""
    broadcaster_user_name: str
    """The requested broadcaster’s user display name"""
    total: int
    """The number of subscriptions in the subscription gift"""
    tier: str
    """The tier of the subscription that ended. Valid values are 1000, 2000, and 3000"""
    cumulative_total: Optional[int]
    """The number of subscriptions gifted by this user in the channel. 
    None for anonymous gifts or if the gifter has opted out of sharing this information"""
    is_anonymous: bool
    """Whether the subscription gift was anonymous"""


class Emote(TwitchObject):
    begin: int
    """The index of where the Emote starts in the text"""
    end: int
    """The index of where the Emote ends in the text"""
    id: str
    """The emote ID"""


class SubscriptionMessage(TwitchObject):
    text: str
    """the text of the resubscription chat message"""
    emotes: List[Emote]
    """An array that includes the emote ID and start and end positions for where the emote appears in the text"""


class ChannelSubscriptionMessageData(TwitchObject):
    user_id: str
    """The user ID for the user who sent a resubscription chat message"""
    user_login: str
    """The user login for the user who sent a resubscription chat message"""
    user_name: str
    """The user display name for the user who sent a resubscription chat message"""
    broadcaster_user_id: str
    """The requested broadcaster’s user ID"""
    broadcaster_user_login: str
    """The requested broadcaster’s user login"""
    broadcaster_user_name: str
    """The requested broadcaster’s user display name"""
    tier: str
    """The tier of the user´s subscription"""
    message: SubscriptionMessage
    """An object that contains the resubscription message and emote information needed to recreate the message."""
    cumulative_months: Optional[int]
    """The number of consecutive months the user’s current subscription has been active. 
    None if the user has opted out of sharing this information."""
    duration_months: int
    """The month duration of the subscription"""


class ChannelCheerData(TwitchObject):
    is_anonymous: bool
    """Whether the user cheered anonymously or not"""
    user_id: Optional[str]
    """The user ID for the user who cheered on the specified channel. None if is_anonymous is True."""
    user_login: Optional[str]
    """The user login for the user who cheered on the specified channel. None if is_anonymous is True."""
    user_name: Optional[str]
    """The user display name for the user who cheered on the specified channel. None if is_anonymous is True."""
    broadcaster_user_id: str
    """The requested broadcaster’s user ID"""
    broadcaster_user_login: str
    """The requested broadcaster’s user login"""
    broadcaster_user_name: str
    """The requested broadcaster’s user display name"""
    message: str
    """The message sent with the cheer"""
    bits: int
    """The number of bits cheered"""


class ChannelRaidData(TwitchObject):
    from_broadcaster_user_id: str
    """The broadcaster id that created the raid"""
    from_broadcaster_user_login: str
    """The broadcaster login that created the raid"""
    from_broadcaster_user_name: str
    """The broadcaster display name that created the raid"""
    to_broadcaster_user_id: str
    """The broadcaster id that received the raid"""
    to_broadcaster_user_login: str
    """The broadcaster login that received the raid"""
    to_broadcaster_user_name: str
    """The broadcaster display name that received the raid"""
    viewers: int
    """The number of viewers in the raid"""


class ChannelBanData(TwitchObject):
    user_id: str
    """The user ID for the user who was banned on the specified channel"""
    user_login: str
    """The user login for the user who was banned on the specified channel"""
    user_name: str
    """The user display name for the user who was banned on the specified channel"""
    broadcaster_user_id: str
    """The requested broadcaster ID"""
    broadcaster_user_login: str
    """The requested broadcaster login"""
    broadcaster_user_name: str
    """The requested broadcaster display name"""
    moderator_user_id: str
    """The user ID of the issuer of the ban"""
    moderator_user_login: str
    """The user login of the issuer of the ban"""
    moderator_user_name: str
    """The user display name of the issuer of the ban"""
    reason: str
    """The reason behind the ban"""
    banned_at: datetime
    """The timestamp of when the user was banned or put in a timeout"""
    ends_at: Optional[datetime]
    """The timestamp of when the timeout ends. None if the user was banned instead of put in a timeout."""
    is_permanent: bool
    """Indicates whether the ban is permanent (True) or a timeout (False). If True, ends_at will be None."""


class ChannelUnbanData(TwitchObject):
    user_id: str
    """The user ID for the user who was unbanned on the specified channel"""
    user_login: str
    """The user login for the user who was unbanned on the specified channel"""
    user_name: str
    """The user display name for the user who was unbanned on the specified channel"""
    broadcaster_user_id: str
    """The requested broadcaster ID"""
    broadcaster_user_login: str
    """The requested broadcaster login"""
    broadcaster_user_name: str
    """The requested broadcaster display name"""
    moderator_user_id: str
    """The user ID of the issuer of the unban"""
    moderator_user_login: str
    """The user login of the issuer of the unban"""
    moderator_user_name: str
    """The user display name of the issuer of the unban"""


class ChannelModeratorAddData(TwitchObject):
    broadcaster_user_id: str
    """The requested broadcaster ID"""
    broadcaster_user_login: str
    """The requested broadcaster login"""
    broadcaster_user_name: str
    """The requested broadcaster display name"""
    user_id: str
    """The user ID of the new moderator"""
    user_login: str
    """The user login of the new moderator"""
    user_name: str
    """The user display name of the new moderator"""


class ChannelModeratorRemoveData(TwitchObject):
    broadcaster_user_id: str
    """The requested broadcaster ID"""
    broadcaster_user_login: str
    """The requested broadcaster login"""
    broadcaster_user_name: str
    """The requested broadcaster display name"""
    user_id: str
    """The user ID of the removed moderator"""
    user_login: str
    """The user login of the removed moderator"""
    user_name: str
    """The user display name of the removed moderator"""


class MaxPerStream(TwitchObject):
    is_enabled: bool
    """Is the setting enabled"""
    value: int
    """The max per stream limit"""


class MaxPerUserPerStream(TwitchObject):
    is_enabled: bool
    """Is the setting enabled"""
    value: int
    """The max per user per stream limit"""


class Image(TwitchObject):
    url_1x: str
    """URL for the image at 1x size"""
    url_2x: str
    """URL for the image at 2x size"""
    url_4x: str
    """URL for the image at 4x size"""


class GlobalCooldown(TwitchObject):
    is_enabled: bool
    """Is the setting enabled"""
    seconds: int
    """The cooldown in seconds"""


class ChannelPointsCustomRewardData(TwitchObject):
    id: str
    """The reward identifier"""
    broadcaster_user_id: str
    """The requested broadcaster ID"""
    broadcaster_user_login: str
    """The requested broadcaster login"""
    broadcaster_user_name: str
    """The requested broadcaster display name"""
    is_enabled: bool
    """Is the reward currently enabled. If False, the reward won't show up to viewers."""
    is_paused: bool
    """Is the reward currently paused. If True, viewers can't redeem."""
    is_in_stock: bool
    """Is the reward currently in stock. If False, viewers can't redeem."""
    title: str
    """The reward title"""
    cost: int
    """The reward cost"""
    prompt: str
    """The reward description"""
    is_user_input_required: bool
    """Does the viewer need to enter information when redeeming the reward"""
    should_redemptions_skip_request_queue: bool
    """Should redemptions be set to :code:`fulfilled` status immediately when redeemed and skip the request queue instead of the normal 
    :code:`unfulfilled` status."""
    max_per_stream: MaxPerStream
    """Whether a maximum per stream is enabled and what the maximum is"""
    max_per_user_per_stream: MaxPerUserPerStream
    """Whether a maximum per user per stream is enabled and what the maximum is"""
    background_color: str
    """Custom background color for the reward. Format: Hex with # prefix."""
    image: Optional[Image]
    """Set of custom images for the reward. None if no images have been uploaded"""
    default_image: Image
    """Set of default images for the reward"""
    global_cooldown: GlobalCooldown
    """Whether a cooldown is enabled and what the cooldown is in seconds"""
    cooldown_expires_at: Optional[datetime]
    """Timestamp of the cooldown expiration. None if the reward is not on cooldown."""
    redemptions_redeemed_current_stream: Optional[int]
    """The number of redemptions redeemed during the current live stream. Counts against the max_per_stream limit. 
    None if the broadcasters stream is not live or max_per_stream is not enabled."""


class Reward(TwitchObject):
    id: str
    """The reward identifier"""
    title: str
    """The reward name"""
    cost: int
    """The reward cost"""
    prompt: str
    """The reward description"""


class ChannelPointsCustomRewardRedemptionData(TwitchObject):
    id: str
    """The redemption identifier"""
    broadcaster_user_id: str
    """The requested broadcaster ID"""
    broadcaster_user_login: str
    """The requested broadcaster login"""
    broadcaster_user_name: str
    """The requested broadcaster display name"""
    user_id: str
    """User ID of the user the redeemed the reward"""
    user_login: str
    """Login of the user the redeemed the reward"""
    user_name: str
    """Display name of the user the redeemed the reward"""
    user_input: str
    """The user input provided. Empty if not provided."""
    status: str
    """Defaults to :code:`unfulfilled`. Possible values are: :code:`unknown`, :code:`unfulfilled`, :code:`fulfilled` and :code:`canceled`"""
    reward: Reward
    """Basic information about the reward that was redeemed, at the time it was redeemed"""
    redeemed_at: datetime
    """Timestamp of when the reward was redeemed"""


class ChannelPollProgressData(TwitchObject):
    id: str
    """ID of the poll"""
    broadcaster_user_id: str
    """The requested broadcaster ID"""
    broadcaster_user_login: str
    """The requested broadcaster login"""
    broadcaster_user_name: str
    """The requested broadcaster display name"""
    title: str
    """Question displayed for the poll"""
    choices: List[PollChoice]
    """An array of choices for the poll. Includes vote counts."""
    bits_voting: BitsVoting
    """not supported"""
    channel_points_voting: ChannelPointsVoting
    """The Channel Points voting settings for the poll"""
    started_at: datetime
    """The time the poll started"""
    ends_at: datetime
    """The time the poll will end"""


class ChannelPollEndData(TwitchObject):
    id: str
    """ID of the poll"""
    broadcaster_user_id: str
    """The requested broadcaster ID"""
    broadcaster_user_login: str
    """The requested broadcaster login"""
    broadcaster_user_name: str
    """The requested broadcaster display name"""
    title: str
    """Question displayed for the poll"""
    choices: List[PollChoice]
    """An array of choices for the poll. Includes vote counts."""
    bits_voting: BitsVoting
    """not supported"""
    channel_points_voting: ChannelPointsVoting
    """The Channel Points voting settings for the poll"""
    status: str
    """The status of the poll. Valid values are completed, archived and terminated."""
    started_at: datetime
    """The time the poll started"""
    ended_at: datetime
    """The time the poll ended"""


class TopPredictors(TwitchObject):
    user_id: str
    """The ID of the user."""
    user_login: str
    """The login of the user."""
    user_name: str
    """The display name of the user."""
    channel_points_won: int
    """The number of Channel Points won. This value is always null in the event payload for Prediction progress and Prediction lock. This value is 0 
    if the outcome did not win or if the Prediction was canceled and Channel Points were refunded."""
    channel_points_used: int
    """The number of Channel Points used to participate in the Prediction."""


class Outcome(TwitchObject):
    id: str
    """The outcome ID."""
    title: str
    """The outcome title."""
    color: str
    """The color for the outcome. Valid values are pink and blue."""
    users: int
    """The number of users who used Channel Points on this outcome."""
    channel_points: int
    """The total number of Channel Points used on this outcome."""
    top_predictors: List[TopPredictors]
    """An array of users who used the most Channel Points on this outcome."""


class ChannelPredictionData(TwitchObject):
    id: str
    """Channel Points Prediction ID."""
    broadcaster_user_id: str
    """The requested broadcaster ID."""
    broadcaster_user_login: str
    """The requested broadcaster login."""
    broadcaster_user_name: str
    """The requested broadcaster display name."""
    title: str
    """Title for the Channel Points Prediction."""
    outcomes: List[Outcome]
    """An array of outcomes for the Channel Points Prediction."""
    started_at: datetime
    """The time the Channel Points Prediction started."""
    locks_at: datetime
    """The time the Channel Points Prediction will automatically lock."""


class ChannelPredictionEndData(TwitchObject):
    id: str
    """Channel Points Prediction ID."""
    broadcaster_user_id: str
    """The requested broadcaster ID."""
    broadcaster_user_login: str
    """The requested broadcaster login."""
    broadcaster_user_name: str
    """The requested broadcaster display name."""
    title: str
    """Title for the Channel Points Prediction."""
    winning_outcome_id: str
    """ID of the winning outcome."""
    outcomes: List[Outcome]
    """An array of outcomes for the Channel Points Prediction. Includes top_predictors."""
    status: str
    """The status of the Channel Points Prediction. Valid values are resolved and canceled."""
    started_at: datetime
    """The time the Channel Points Prediction started."""
    ended_at: datetime
    """The time the Channel Points Prediction ended."""


class Entitlement(TwitchObject):
    organization_id: str
    """The ID of the organization that owns the game that has Drops enabled."""
    category_id: str
    """Twitch category ID of the game that was being played when this benefit was entitled."""
    category_name: str
    """The category name."""
    campaign_id: str
    """The campaign this entitlement is associated with."""
    user_id: str
    """Twitch user ID of the user who was granted the entitlement."""
    user_name: str
    """The user display name of the user who was granted the entitlement."""
    user_login: str
    """The user login of the user who was granted the entitlement."""
    entitlement_id: str
    """Unique identifier of the entitlement. Use this to de-duplicate entitlements."""
    benefit_id: str
    """Identifier of the Benefit."""
    created_at: datetime
    """UTC timestamp in ISO format when this entitlement was granted on Twitch."""


class DropEntitlementGrantData(TwitchObject):
    id: str
    """Individual event ID, as assigned by EventSub. Use this for de-duplicating messages."""
    data: Entitlement
    """Entitlement object"""


class Product(TwitchObject):
    name: str
    """Product name."""
    bits: int
    """Bits involved in the transaction."""
    sku: str
    """Unique identifier for the product acquired."""
    in_development: bool
    """Flag indicating if the product is in development. If in_development is true, bits will be 0."""


class ExtensionBitsTransactionCreateData(TwitchObject):
    extension_client_id: str
    """Client ID of the extension."""
    id: str
    """Transaction ID."""
    broadcaster_user_id: str
    """The transaction’s broadcaster ID."""
    broadcaster_user_login: str
    """The transaction’s broadcaster login."""
    broadcaster_user_name: str
    """The transaction’s broadcaster display name."""
    user_id: str
    """The transaction’s user ID."""
    user_login: str
    """The transaction’s user login."""
    user_name: str
    """The transaction’s user display name."""
    product: Product
    """Additional extension product information."""


class GoalData(TwitchObject):
    id: str
    """An ID that identifies this event."""
    broadcaster_user_id: str
    """An ID that uniquely identifies the broadcaster."""
    broadcaster_user_name: str
    """The broadcaster’s display name."""
    broadcaster_user_login: str
    """The broadcaster’s user handle."""
    type: str
    """The type of goal. Possible values are:
    
    - follow — The goal is to increase followers.
    - subscription — The goal is to increase subscriptions. This type shows the net increase or decrease in tier points associated with the 
      subscriptions.
    - subscription_count — The goal is to increase subscriptions. This type shows the net increase or decrease in the number of subscriptions.
    - new_subscription — The goal is to increase subscriptions. This type shows only the net increase in tier points associated with the subscriptions
      (it does not account for users that unsubscribed since the goal started).
    - new_subscription_count — The goal is to increase subscriptions. This type shows only the net increase in the number of subscriptions 
      (it does not account for users that unsubscribed since the goal started).
    """
    description: str
    """A description of the goal, if specified. The description may contain a maximum of 40 characters."""
    is_achieved: Optional[bool]
    """A Boolean value that indicates whether the broadcaster achieved their goal. Is true if the goal was achieved; otherwise, false.
    Only the channel.goal.end event includes this field."""
    current_amount: int
    """The goals current value. The goals type determines how this value is increased or decreased
    
    - If type is follow, this field is set to the broadcaster's current number of followers. This number increases with new followers and decreases 
      when users unfollow the broadcaster.
    - If type is subscription, this field is increased and decreased by the points value associated with the subscription tier. For example, if a 
      tier-two subscription is worth 2 points, this field is increased or decreased by 2, not 1.
    - If type is subscription_count, this field is increased by 1 for each new subscription and decreased by 1 for each user that unsubscribes.
    - If type is new_subscription, this field is increased by the points value associated with the subscription tier. For example, if a tier-two 
      subscription is worth 2 points, this field is increased by 2, not 1.
    - If type is new_subscription_count, this field is increased by 1 for each new subscription.
    """
    target_amount: int
    """The goal’s target value. For example, if the broadcaster has 200 followers before creating the goal, and their goal is to double that number, 
    this field is set to 400."""
    started_at: datetime
    """The timestamp which indicates when the broadcaster created the goal."""
    ended_at: Optional[datetime]
    """The timestamp which indicates when the broadcaster ended the goal. Only the channel.goal.end event includes this field."""


class TopContribution(TwitchObject):
    user_id: str
    """The ID of the user that made the contribution."""
    user_login: str
    """The user’s login name."""
    user_name: str
    """The user’s display name."""
    type: str
    """The contribution method used. Possible values are:
    
    - bits — Cheering with Bits.
    - subscription — Subscription activity like subscribing or gifting subscriptions.
    - other — Covers other contribution methods not listed.
    """
    total: int
    """The total amount contributed. If type is bits, total represents the amount of Bits used. If type is subscription, total is 500, 1000, or 2500 
    to represent tier 1, 2, or 3 subscriptions, respectively."""


class LastContribution(TwitchObject):
    user_id: str
    """The ID of the user that made the contribution."""
    user_login: str
    """The user’s login name."""
    user_name: str
    """The user’s display name."""
    type: str
    """The contribution method used. Possible values are:
    
    - bits — Cheering with Bits.
    - subscription — Subscription activity like subscribing or gifting subscriptions.
    - other — Covers other contribution methods not listed.
    """
    total: int
    """The total amount contributed. If type is bits, total represents the amount of Bits used. If type is subscription, total is 500, 1000, or 2500 
    to represent tier 1, 2, or 3 subscriptions, respectively."""


class HypeTrainData(TwitchObject):
    id: str
    """The Hype Train ID."""
    broadcaster_user_id: str
    """The requested broadcaster ID."""
    broadcaster_user_login: str
    """The requested broadcaster login."""
    broadcaster_user_name: str
    """The requested broadcaster display name."""
    total: int
    """Total points contributed to the Hype Train."""
    progress: int
    """The number of points contributed to the Hype Train at the current level."""
    goal: int
    """The number of points required to reach the next level."""
    top_contributions: List[TopContribution]
    """The contributors with the most points contributed."""
    last_contribution: LastContribution
    """The most recent contribution."""
    level: int
    """The starting level of the Hype Train."""
    started_at: datetime
    """The time when the Hype Train started."""
    expires_at: datetime
    """The time when the Hype Train expires. The expiration is extended when the Hype Train reaches a new level."""
    is_golden_kappa_train: bool
    """Indicates if the Hype Train is a Golden Kappa Train."""


class HypeTrainEndData(TwitchObject):
    id: str
    """The Hype Train ID."""
    broadcaster_user_id: str
    """The requested broadcaster ID."""
    broadcaster_user_login: str
    """The requested broadcaster login."""
    broadcaster_user_name: str
    """The requested broadcaster display name."""
    level: int
    """The final level of the Hype Train."""
    total: int
    """Total points contributed to the Hype Train."""
    top_contributions: List[TopContribution]
    """The contributors with the most points contributed."""
    started_at: datetime
    """The time when the Hype Train started."""
    ended_at: datetime
    """The time when the Hype Train ended."""
    cooldown_ends_at: datetime
    """The time when the Hype Train cooldown ends so that the next Hype Train can start."""
    is_golden_kappa_train: bool
    """Indicates if the Hype Train is a Golden Kappa Train."""


class StreamOnlineData(TwitchObject):
    id: str
    """The id of the stream."""
    broadcaster_user_id: str
    """The broadcaster’s user id."""
    broadcaster_user_login: str
    """The broadcaster’s user login."""
    broadcaster_user_name: str
    """The broadcaster’s user display name."""
    type: str
    """The stream type. Valid values are: live, playlist, watch_party, premiere, rerun."""
    started_at: datetime
    """The timestamp at which the stream went online at."""


class StreamOfflineData(TwitchObject):
    broadcaster_user_id: str
    """The broadcaster’s user id."""
    broadcaster_user_login: str
    """The broadcaster’s user login."""
    broadcaster_user_name: str
    """The broadcaster’s user display name."""


class UserAuthorizationGrantData(TwitchObject):
    client_id: str
    """The client_id of the application that was granted user access."""
    user_id: str
    """The user id for the user who has granted authorization for your client id."""
    user_login: str
    """The user login for the user who has granted authorization for your client id."""
    user_name: str
    """The user display name for the user who has granted authorization for your client id."""


class UserAuthorizationRevokeData(TwitchObject):
    client_id: str
    """The client_id of the application with revoked user access."""
    user_id: str
    """The user id for the user who has revoked authorization for your client id."""
    user_login: str
    """The user login for the user who has revoked authorization for your client id. This is null if the user no longer exists."""
    user_name: str
    """The user display name for the user who has revoked authorization for your client id. This is null if the user no longer exists."""


class UserUpdateData(TwitchObject):
    user_id: str
    """The user’s user id."""
    user_login: str
    """The user’s user login."""
    user_name: str
    """The user’s user display name."""
    email: str
    """The user’s email address. The event includes the user’s email address only if the app used to request this event type includes the 
    user:read:email scope for the user; otherwise, the field is set to an empty string. See Create EventSub Subscription."""
    email_verified: bool
    """A Boolean value that determines whether Twitch has verified the user’s email address. Is true if Twitch has verified the email address; 
    otherwise, false.

    NOTE: Ignore this field if the email field contains an empty string."""


class ShieldModeData(TwitchObject):
    broadcaster_user_id: str
    """An ID that identifies the broadcaster whose Shield Mode status was updated."""
    broadcaster_user_login: str
    """The broadcaster’s login name."""
    broadcaster_user_name: str
    """The broadcaster’s display name."""
    moderator_user_id: str
    """An ID that identifies the moderator that updated the Shield Mode’s status. If the broadcaster updated the status, this ID will be the same 
    as broadcaster_user_id."""
    moderator_user_login: str
    """The moderator’s login name."""
    moderator_user_name: str
    """The moderator’s display name."""
    started_at: datetime
    """The timestamp of when the moderator activated Shield Mode. The object includes this field only for channel.shield_mode.begin events."""
    ended_at: datetime
    """The timestamp of when the moderator deactivated Shield Mode. The object includes this field only for channel.shield_mode.end events."""


class Amount(TwitchObject):
    value: int
    """The monetary amount. The amount is specified in the currency’s minor unit. For example, the minor units for USD is cents, so if the amount 
    is $5.50 USD, value is set to 550."""
    decimal_places: int
    """The number of decimal places used by the currency. For example, USD uses two decimal places. Use this number to translate value from minor 
    units to major units by using the formula: value / 10^decimal_places"""
    currency: str
    """The ISO-4217 three-letter currency code that identifies the type of currency in value."""


class CharityCampaignStartData(TwitchObject):
    id: str
    """An ID that identifies the charity campaign."""
    broadcaster_id: str
    """An ID that identifies the broadcaster that’s running the campaign."""
    broadcaster_login: str
    """The broadcaster’s login name."""
    broadcaster_name: str
    """The broadcaster’s display name."""
    charity_name: str
    """The charity’s name."""
    charity_description: str
    """A description of the charity."""
    charity_logo: str
    """A URL to an image of the charity’s logo. The image’s type is PNG and its size is 100px X 100px."""
    charity_website: str
    """A URL to the charity’s website."""
    current_amount: Amount
    """Contains the current amount of donations that the campaign has received."""
    target_amount: Amount
    """Contains the campaign’s target fundraising goal."""
    started_at: datetime
    """The timestamp of when the broadcaster started the campaign."""


class CharityCampaignProgressData(TwitchObject):
    id: str
    """An ID that identifies the charity campaign."""
    broadcaster_id: str
    """An ID that identifies the broadcaster that’s running the campaign."""
    broadcaster_login: str
    """The broadcaster’s login name."""
    broadcaster_name: str
    """The broadcaster’s display name."""
    charity_name: str
    """The charity’s name."""
    charity_description: str
    """A description of the charity."""
    charity_logo: str
    """A URL to an image of the charity’s logo. The image’s type is PNG and its size is 100px X 100px."""
    charity_website: str
    """A URL to the charity’s website."""
    current_amount: Amount
    """Contains the current amount of donations that the campaign has received."""
    target_amount: Amount
    """Contains the campaign’s target fundraising goal."""


class CharityCampaignStopData(TwitchObject):
    id: str
    """An ID that identifies the charity campaign."""
    broadcaster_id: str
    """An ID that identifies the broadcaster that ran the campaign."""
    broadcaster_login: str
    """The broadcaster’s login name."""
    broadcaster_name: str
    """The broadcaster’s display name."""
    charity_name: str
    """The charity’s name."""
    charity_description: str
    """A description of the charity."""
    charity_logo: str
    """A URL to an image of the charity’s logo. The image’s type is PNG and its size is 100px X 100px."""
    charity_website: str
    """A URL to the charity’s website."""
    current_amount: Amount
    """Contains the final amount of donations that the campaign received."""
    target_amount: Amount
    """Contains the campaign’s target fundraising goal."""
    stopped_at: datetime
    """The timestamp of when the broadcaster stopped the campaign."""


class CharityDonationData(TwitchObject):
    id: str
    """An ID that identifies the donation. The ID is unique across campaigns."""
    campaign_id: str
    """An ID that identifies the charity campaign."""
    broadcaster_id: str
    """An ID that identifies the broadcaster that’s running the campaign."""
    broadcaster_login: str
    """The broadcaster’s login name."""
    broadcaster_name: str
    """The broadcaster’s display name."""
    user_id: str
    """An ID that identifies the user that donated to the campaign."""
    user_login: str
    """The user’s login name."""
    user_name: str
    """The user’s display name."""
    charity_name: str
    """The charity’s name."""
    charity_description: str
    """A description of the charity."""
    charity_logo: str
    """A URL to an image of the charity’s logo. The image’s type is PNG and its size is 100px X 100px."""
    charity_website: str
    """A URL to the charity’s website."""
    amount: Amount
    """Contains the amount of money that the user donated."""


class ChannelShoutoutCreateData(TwitchObject):
    broadcaster_user_id: str
    """An ID that identifies the broadcaster that sent the Shoutout."""
    broadcaster_user_login: str
    """The broadcaster’s login name."""
    broadcaster_user_name: str
    """The broadcaster’s display name."""
    to_broadcaster_user_id: str
    """An ID that identifies the broadcaster that received the Shoutout."""
    to_broadcaster_user_login: str
    """The broadcaster’s login name."""
    to_broadcaster_user_name: str
    """The broadcaster’s display name."""
    moderator_user_id: str
    """An ID that identifies the moderator that sent the Shoutout. If the broadcaster sent the Shoutout, this ID is the same as the ID in 
    broadcaster_user_id."""
    moderator_user_login: str
    """The moderator’s login name."""
    moderator_user_name: str
    """The moderator’s display name."""
    viewer_count: int
    """The number of users that were watching the broadcaster’s stream at the time of the Shoutout."""
    started_at: datetime
    """The timestamp of when the moderator sent the Shoutout."""
    cooldown_ends_at: datetime
    """The timestamp of when the broadcaster may send a Shoutout to a different broadcaster."""
    target_cooldown_ends_at: datetime
    """The timestamp of when the broadcaster may send another Shoutout to the broadcaster in to_broadcaster_user_id."""


class ChannelShoutoutReceiveData(TwitchObject):
    broadcaster_user_id: str
    """An ID that identifies the broadcaster that received the Shoutout."""
    broadcaster_user_login: str
    """The broadcaster’s login name."""
    broadcaster_user_name: str
    """The broadcaster’s display name."""
    from_broadcaster_user_id: str
    """An ID that identifies the broadcaster that sent the Shoutout."""
    from_broadcaster_user_login: str
    """The broadcaster’s login name."""
    from_broadcaster_user_name: str
    """The broadcaster’s display name."""
    viewer_count: int
    """The number of users that were watching the from-broadcaster’s stream at the time of the Shoutout."""
    started_at: datetime
    """The timestamp of when the moderator sent the Shoutout."""


class ChannelChatClearData(TwitchObject):
    broadcaster_user_id: str
    """The broadcaster user ID."""
    broadcaster_user_name: str
    """The broadcaster display name."""
    broadcaster_user_login: str
    """The broadcaster login."""


class ChannelChatClearUserMessagesData(TwitchObject):
    broadcaster_user_id: str
    """The broadcaster user ID."""
    broadcaster_user_name: str
    """The broadcaster display name."""
    broadcaster_user_login: str
    """The broadcaster login."""
    target_user_id: str
    """The ID of the user that was banned or put in a timeout. All of their messages are deleted."""
    target_user_name: str
    """The user name of the user that was banned or put in a timeout."""
    target_user_login: str
    """The user login of the user that was banned or put in a timeout."""


class ChannelChatMessageDeleteData(TwitchObject):
    broadcaster_user_id: str
    """The broadcaster user ID."""
    broadcaster_user_name: str
    """The broadcaster display name."""
    broadcaster_user_login: str
    """The broadcaster login."""
    target_user_id: str
    """The ID of the user whose message was deleted."""
    target_user_name: str
    """The user name of the user whose message was deleted."""
    target_user_login: str
    """The user login of the user whose message was deleted."""
    message_id: str
    """A UUID that identifies the message that was removed."""


class Badge(TwitchObject):
    set_id: str
    """An ID that identifies this set of chat badges. For example, Bits or Subscriber."""
    id: str
    """An ID that identifies this version of the badge. The ID can be any value. For example, for Bits, the ID is the Bits tier level, but for 
    World of Warcraft, it could be Alliance or Horde."""
    info: str
    """Contains metadata related to the chat badges in the badges tag. Currently, this tag contains metadata only for subscriber badges, 
    to indicate the number of months the user has been a subscriber."""


class MessageFragmentCheermote(TwitchObject):
    prefix: str
    """The name portion of the Cheermote string that you use in chat to cheer Bits. The full Cheermote string is the concatenation of 
    {prefix} + {number of Bits}. For example, if the prefix is “Cheer” and you want to cheer 100 Bits, the full Cheermote string is Cheer100. 
    When the Cheermote string is entered in chat, Twitch converts it to the image associated with the Bits tier that was cheered."""
    bits: int
    """The amount of bits cheered."""
    tier: int
    """The tier level of the cheermote."""


class MessageFragmentEmote(TwitchObject):
    id: str
    """An ID that uniquely identifies this emote."""
    emote_set_id: str
    """An ID that identifies the emote set that the emote belongs to."""
    owner_id: str
    """The ID of the broadcaster who owns the emote."""
    format: List[str]
    """The formats that the emote is available in. For example, if the emote is available only as a static PNG, the array contains only static. But if the emote is available as a static PNG and an animated GIF, the array contains static and animated. The possible formats are:
        
    - animated — An animated GIF is available for this emote.
    - static — A static PNG file is available for this emote.
    """


class MessageFragmentMention(TwitchObject):
    user_id: str
    """The user ID of the mentioned user."""
    user_name: str
    """The user name of the mentioned user."""
    user_login: str
    """The user login of the mentioned user."""


class MessageFragment(TwitchObject):
    type: str
    """The type of message fragment. Possible values:
    
    - text
    - cheermote
    - emote
    - mention
    """
    text: str
    """Message text in fragment"""
    cheermote: Optional[MessageFragmentCheermote]
    """Metadata pertaining to the cheermote."""
    emote: Optional[MessageFragmentEmote]
    """Metadata pertaining to the emote."""
    mention: Optional[MessageFragmentMention]
    """Metadata pertaining to the mention."""


class Message(TwitchObject):
    text: str
    """The chat message in plain text."""
    fragments: List[MessageFragment]
    """Ordered list of chat message fragments."""


class SubNoticeMetadata(TwitchObject):
    sub_tier: str
    """The type of subscription plan being used. Possible values are:
    
    - 1000 — First level of paid or Prime subscription
    - 2000 — Second level of paid subscription
    - 3000 — Third level of paid subscription
    """
    is_prime: bool
    """Indicates if the subscription was obtained through Amazon Prime."""
    duration_months: int
    """The number of months the subscription is for."""


class ResubNoticeMetadata(TwitchObject):
    cumulative_months: int
    """The total number of months the user has subscribed."""
    duration_months: int
    """The number of months the subscription is for."""
    streak_months: int
    """Optional. The number of consecutive months the user has subscribed."""
    sub_tier: str
    """The type of subscription plan being used. Possible values are:
    
    - 1000 — First level of paid or Prime subscription
    - 2000 — Second level of paid subscription
    - 3000 — Third level of paid subscription
    """
    is_prime: bool
    """Indicates if the resub was obtained through Amazon Prime."""
    is_gift: bool
    """Whether or not the resub was a result of a gift."""
    gifter_is_anonymous: Optional[bool]
    """Optional. Whether or not the gift was anonymous."""
    gifter_user_id: Optional[str]
    """Optional. The user ID of the subscription gifter. None if anonymous."""
    gifter_user_name: Optional[str]
    """Optional. The user name of the subscription gifter. None if anonymous."""
    gifter_user_login: Optional[str]
    """Optional. The user login of the subscription gifter. None if anonymous."""


class SubGiftNoticeMetadata(TwitchObject):
    duration_months: int
    """The number of months the subscription is for."""
    cumulative_total: Optional[int]
    """Optional. The amount of gifts the gifter has given in this channel. None if anonymous."""
    recipient_user_id: str
    """The user ID of the subscription gift recipient."""
    recipient_user_name: str
    """The user name of the subscription gift recipient."""
    recipient_user_login: str
    """The user login of the subscription gift recipient."""
    sub_tier: str
    """The type of subscription plan being used. Possible values are:
    
    - 1000 — First level of paid subscription
    - 2000 — Second level of paid subscription
    - 3000 — Third level of paid subscription
    """
    community_gift_id: Optional[str]
    """Optional. The ID of the associated community gift. None if not associated with a community gift."""


class CommunitySubGiftNoticeMetadata(TwitchObject):
    id: str
    """The ID of the associated community gift."""
    total: int
    """Number of subscriptions being gifted."""
    sub_tier: str
    """The type of subscription plan being used. Possible values are:
    
    - 1000 — First level of paid subscription
    - 2000 — Second level of paid subscription
    - 3000 — Third level of paid subscription
    """
    cumulative_total: Optional[int]
    """Optional. The amount of gifts the gifter has given in this channel. None if anonymous."""


class GiftPaidUpgradeNoticeMetadata(TwitchObject):
    gifter_is_anonymous: bool
    """Whether the gift was given anonymously."""
    gifter_user_id: Optional[str]
    """Optional. The user ID of the user who gifted the subscription. None if anonymous."""
    gifter_user_name: Optional[str]
    """Optional. The user name of the user who gifted the subscription. None if anonymous."""
    gifter_user_login: Optional[str]
    """Optional. The user login of the user who gifted the subscription. None if anonymous."""


class PrimePaidUpgradeNoticeMetadata(TwitchObject):
    sub_tier: str
    """The type of subscription plan being used. Possible values are:
    
    - 1000 — First level of paid subscription
    - 2000 — Second level of paid subscription
    - 3000 — Third level of paid subscription
    """


class RaidNoticeMetadata(TwitchObject):
    user_id: str
    """The user ID of the broadcaster raiding this channel."""
    user_name: str
    """The user name of the broadcaster raiding this channel."""
    user_login: str
    """The login name of the broadcaster raiding this channel."""
    viewer_count: int
    """The number of viewers raiding this channel from the broadcaster’s channel."""
    profile_image_url: str
    """Profile image URL of the broadcaster raiding this channel."""


class UnraidNoticeMetadata(TwitchObject):
    pass


class PayItForwardNoticeMetadata(TwitchObject):
    gifter_is_anonymous: bool
    """Whether the gift was given anonymously."""
    gifter_user_id: Optional[str]
    """Optional. The user ID of the user who gifted the subscription. None if anonymous."""
    gifter_user_name: Optional[str]
    """Optional. The user name of the user who gifted the subscription. None if anonymous."""
    gifter_user_login: Optional[str]
    """Optional. The user login of the user who gifted the subscription. None if anonymous."""


class AnnouncementNoticeMetadata(TwitchObject):
    color: str
    """Color of the announcement."""


class CharityDonationNoticeMetadata(TwitchObject):
    charity_name: str
    """Name of the charity."""
    amount: Amount
    """An object that contains the amount of money that the user paid."""


class BitsBadgeTierNoticeMetadata(TwitchObject):
    tier: int
    """The tier of the Bits badge the user just earned. For example, 100, 1000, or 10000."""


class ChannelChatNotificationData(TwitchObject):
    broadcaster_user_id: str
    """The broadcaster user ID."""
    broadcaster_user_name: str
    """The broadcaster display name."""
    broadcaster_user_login: str
    """The broadcaster login."""
    chatter_user_id: str
    """The user ID of the user that sent the message."""
    chatter_user_name: str
    """The user name of the user that sent the message."""
    chatter_user_login: str
    """The user login of the user that sent the message."""
    chatter_is_anonymous: bool
    """Whether or not the chatter is anonymous."""
    color: str
    """The color of the user’s name in the chat room."""
    badges: List[Badge]
    """List of chat badges."""
    system_message: str
    """The message Twitch shows in the chat room for this notice."""
    message_id: str
    """A UUID that identifies the message."""
    message: Message
    """The structured chat message"""
    notice_type: str
    """The type of notice. Possible values are:

    - sub
    - resub
    - sub_gift
    - community_sub_gift
    - gift_paid_upgrade
    - prime_paid_upgrade
    - raid
    - unraid
    - pay_it_forward
    - announcement
    - bits_badge_tier
    - charity_donation
    """
    sub: Optional[SubNoticeMetadata]
    """Information about the sub event. None if notice_type is not sub."""
    resub: Optional[ResubNoticeMetadata]
    """Information about the resub event. None if notice_type is not resub."""
    sub_gift: Optional[SubGiftNoticeMetadata]
    """Information about the gift sub event. None if notice_type is not sub_gift."""
    community_sub_gift: Optional[CommunitySubGiftNoticeMetadata]
    """Information about the community gift sub event. None if notice_type is not community_sub_gift."""
    gift_paid_upgrade: Optional[GiftPaidUpgradeNoticeMetadata]
    """Information about the community gift paid upgrade event. None if notice_type is not gift_paid_upgrade."""
    prime_paid_upgrade: Optional[PrimePaidUpgradeNoticeMetadata]
    """Information about the Prime gift paid upgrade event. None if notice_type is not prime_paid_upgrade."""
    raid: Optional[RaidNoticeMetadata]
    """Information about the raid event. None if notice_type is not raid."""
    unraid: Optional[UnraidNoticeMetadata]
    """Returns an empty payload if notice_type is unraid, otherwise returns None."""
    pay_it_forward: Optional[PayItForwardNoticeMetadata]
    """Information about the pay it forward event. None if notice_type is not pay_it_forward."""
    announcement: Optional[AnnouncementNoticeMetadata]
    """Information about the announcement event. None if notice_type is not announcement"""
    charity_donation: Optional[CharityDonationNoticeMetadata]
    """Information about the charity donation event. None if notice_type is not charity_donation."""
    bits_badge_tier: Optional[BitsBadgeTierNoticeMetadata]
    """Information about the bits badge tier event. None if notice_type is not bits_badge_tier."""


class ChannelAdBreakBeginData(TwitchObject):
    duration_seconds: int
    """Length in seconds of the mid-roll ad break requested"""
    started_at: datetime
    """The UTC timestamp of when the ad break began, in RFC3339 format. Note that there is potential delay between this 
    event, when the streamer requested the ad break, and when the viewers will see ads."""
    is_automatic: bool
    """Indicates if the ad was automatically scheduled via Ads Manager"""
    broadcaster_user_id: str
    """The broadcaster’s user ID for the channel the ad was run on."""
    broadcaster_user_login: str
    """The broadcaster’s user login for the channel the ad was run on."""
    broadcaster_user_name: str
    """The broadcaster’s user display name for the channel the ad was run on."""
    requester_user_id: str
    """The ID of the user that requested the ad. For automatic ads, this will be the ID of the broadcaster."""
    requester_user_login: str
    """The login of the user that requested the ad."""
    requester_user_name: str
    """The display name of the user that requested the ad."""


class ChatMessageFragmentCheermoteMetadata(TwitchObject):
    prefix: str
    """The name portion of the Cheermote string that you use in chat to cheer Bits. 
    The full Cheermote string is the concatenation of {prefix} + {number of Bits}. 
    For example, if the prefix is “Cheer” and you want to cheer 100 Bits, the full Cheermote string is Cheer100. 
    When the Cheermote string is entered in chat, Twitch converts it to the image associated with the Bits tier that was cheered."""
    bits: int
    """The amount of bits cheered."""
    tier: int
    """The tier level of the cheermote."""


class ChatMessageFragmentEmoteMetadata(TwitchObject):
    id: str
    """An ID that uniquely identifies this emote."""
    emote_set_id: str
    """An ID that identifies the emote set that the emote belongs to."""
    owner_id: str
    """The ID of the broadcaster who owns the emote."""
    format: str
    """The formats that the emote is available in. For example, if the emote is available only as a static PNG, the array contains only static. 
    But if the emote is available as a static PNG and an animated GIF, the array contains static and animated. The possible formats are:

    - animated — An animated GIF is available for this emote.
    - static — A static PNG file is available for this emote.
    """


class ChatMessageFragmentMentionMetadata(TwitchObject):
    user_id: str
    """The user ID of the mentioned user."""
    user_name: str
    """The user name of the mentioned user."""
    user_login: str
    """The user login of the mentioned user."""


class ChatMessageFragment(TwitchObject):
    type: str
    """The type of message fragment. Possible values:

    - text
    - cheermote
    - emote
    - mention
    """
    text: str
    """Message text in fragment."""
    cheermote: Optional[ChatMessageFragmentCheermoteMetadata]
    """Optional. Metadata pertaining to the cheermote."""
    emote: Optional[ChatMessageFragmentEmoteMetadata]
    """Optional. Metadata pertaining to the emote."""
    mention: Optional[ChatMessageFragmentMentionMetadata]
    """Optional. Metadata pertaining to the mention."""


class ChatMessageBadge(TwitchObject):
    set_id: str
    """An ID that identifies this set of chat badges. For example, Bits or Subscriber."""
    id: str
    """An ID that identifies this version of the badge. The ID can be any value. For example, for Bits, 
    the ID is the Bits tier level, but for World of Warcraft, it could be Alliance or Horde."""
    info: str
    """Contains metadata related to the chat badges in the badges tag. Currently, this tag contains metadata only for 
    subscriber badges, to indicate the number of months the user has been a subscriber."""


class ChatMessageCheerMetadata(TwitchObject):
    bits: int
    """The amount of Bits the user cheered."""


class ChatMessageReplyMetadata(TwitchObject):
    parent_message_id: str
    """An ID that uniquely identifies the parent message that this message is replying to."""
    parent_message_body: str
    """The message body of the parent message."""
    parent_user_id: str
    """User ID of the sender of the parent message."""
    parent_user_name: str
    """User name of the sender of the parent message."""
    parent_user_login: str
    """User login of the sender of the parent message."""
    thread_message_id: str
    """An ID that identifies the parent message of the reply thread."""
    thread_user_id: str
    """User ID of the sender of the thread’s parent message."""
    thread_user_name: str
    """User name of the sender of the thread’s parent message."""
    thread_user_login: str
    """User login of the sender of the thread’s parent message."""


class ChatMessage(TwitchObject):
    text: str
    """The chat message in plain text."""
    fragments: List[ChatMessageFragment]
    """Ordered list of chat message fragments."""


class ChannelChatMessageData(TwitchObject):
    broadcaster_user_id: str
    """The broadcaster user ID."""
    broadcaster_user_name: str
    """The broadcaster display name."""
    broadcaster_user_login: str
    """The broadcaster login."""
    chatter_user_id: str
    """The user ID of the user that sent the message."""
    chatter_user_name: str
    """The user name of the user that sent the message."""
    chatter_user_login: str
    """The user login of the user that sent the message."""
    message_id: str
    """A UUID that identifies the message."""
    message: ChatMessage
    """The structured chat message."""
    message_type: str
    """The type of message. Possible values:

    - text
    - channel_points_highlighted
    - channel_points_sub_only
    - user_intro
    """
    badges: List[ChatMessageBadge]
    """List of chat badges."""
    cheer: Optional[ChatMessageCheerMetadata]
    """Optional. Metadata if this message is a cheer."""
    color: str
    """The color of the user’s name in the chat room. This is a hexadecimal RGB color code in the form, #<RGB>. 
    This tag may be empty if it is never set."""
    reply: Optional[ChatMessageReplyMetadata]
    """Optional. Metadata if this message is a reply."""
    channel_points_custom_reward_id: str
    """Optional. The ID of a channel points custom reward that was redeemed."""


class ChannelChatSettingsUpdateData(TwitchObject):
    broadcaster_user_id: str
    """The ID of the broadcaster specified in the request."""
    broadcaster_user_login: str
    """The login of the broadcaster specified in the request."""
    broadcaster_user_name: str
    """The user name of the broadcaster specified in the request."""
    emote_mode: bool
    """A Boolean value that determines whether chat messages must contain only emotes. True if only messages that are 100% emotes are allowed; otherwise false."""
    follower_mode: bool
    """A Boolean value that determines whether the broadcaster restricts the chat room to followers only, based on how long they’ve followed.

    True if the broadcaster restricts the chat room to followers only; otherwise false.

    See follower_mode_duration_minutes for how long the followers must have followed the broadcaster to participate in the chat room."""
    follower_mode_duration_minutes: Optional[int]
    """The length of time, in minutes, that the followers must have followed the broadcaster to participate in the chat room. See follower_mode.

    None if follower_mode is false."""
    slow_mode: bool
    """A Boolean value that determines whether the broadcaster limits how often users in the chat room are allowed to send messages.

    Is true, if the broadcaster applies a delay; otherwise, false.

    See slow_mode_wait_time_seconds for the delay."""
    slow_mode_wait_time_seconds: Optional[int]
    """The amount of time, in seconds, that users need to wait between sending messages. See slow_mode.

    None if slow_mode is false."""
    subscriber_mode: bool
    """A Boolean value that determines whether only users that subscribe to the broadcaster’s channel can talk in the chat room.

    True if the broadcaster restricts the chat room to subscribers only; otherwise false."""
    unique_chat_mode: bool
    """A Boolean value that determines whether the broadcaster requires users to post only unique messages in the chat room.

    True if the broadcaster requires unique messages only; otherwise false."""


class WhisperInformation(TwitchObject):
    text: str
    """The body of the whisper message."""

class UserWhisperMessageData(TwitchObject):
    from_user_id: str
    """The ID of the user sending the message."""
    from_user_name: str
    """The name of the user sending the message."""
    from_user_login: str
    """The login of the user sending the message."""
    to_user_id: str
    """The ID of the user receiving the message."""
    to_user_name: str
    """The name of the user receiving the message."""
    to_user_login: str
    """The login of the user receiving the message."""
    whisper_id: str
    """The whisper ID."""
    whisper: WhisperInformation
    """Object containing whisper information."""


class RewardEmote(TwitchObject):
    id: str
    """The emote ID."""
    name: str
    """The human readable emote token."""

class AutomaticReward(TwitchObject):
    type: str
    """The type of reward. One of:
    
    - ssingle_message_bypass_sub_mode
    - send_highlighted_message
    - random_sub_emote_unlock
    - chosen_sub_emote_unlock
    - chosen_modified_sub_emote_unlock
    """
    cost: int
    """The reward cost."""
    unlocked_emote: Optional[MessageFragmentEmote]
    """Emote that was unlocked."""


class RewardMessage(TwitchObject):
    text: str
    """The text of the chat message."""
    emotes: List[Emote]
    """An array that includes the emote ID and start and end positions for where the emote appears in the text."""


class ChannelPointsAutomaticRewardRedemptionAddData(TwitchObject):
    broadcaster_user_id: str
    """The ID of the channel where the reward was redeemed."""
    broadcaster_user_login: str
    """The login of the channel where the reward was redeemed."""
    broadcaster_user_name: str
    """The display name of the channel where the reward was redeemed."""
    user_id: str
    """The ID of the redeeming user."""
    user_login: str
    """The login of the redeeming user."""
    user_name: str
    """The display name of the redeeming user."""
    id: str
    """The ID of the Redemption."""
    reward: AutomaticReward
    """An object that contains the reward information."""
    message: RewardMessage
    """An object that contains the user message and emote information needed to recreate the message."""
    user_input: Optional[str]
    """A string that the user entered if the reward requires input."""
    redeemed_at: datetime
    """The time of when the reward was redeemed."""


class ChannelVIPAddData(TwitchObject):
    user_id: str
    """The ID of the user who was added as a VIP."""
    user_login: str
    """The login of the user who was added as a VIP."""
    user_name: str
    """The display name of the user who was added as a VIP."""
    broadcaster_user_id: str
    """The ID of the broadcaster."""
    broadcaster_user_login: str
    """The login of the broadcaster."""
    broadcaster_user_name: str
    """The display name of the broadcaster."""


class ChannelVIPRemoveData(TwitchObject):
    user_id: str
    """The ID of the user who was removed as a VIP."""
    user_login: str
    """The login of the user who was removed as a VIP."""
    user_name: str
    """The display name of the user who was removed as a VIP."""
    broadcaster_user_id: str
    """The ID of the broadcaster."""
    broadcaster_user_login: str
    """The login of the broadcaster."""
    broadcaster_user_name: str
    """The display name of the broadcaster."""


class ChannelUnbanRequestCreateData(TwitchObject):
    id: str
    """The ID of the unban request."""
    broadcaster_user_id: str
    """The broadcaster’s user ID for the channel the unban request was created for."""
    broadcaster_user_login: str
    """The broadcaster’s login name."""
    broadcaster_user_name: str
    """The broadcaster’s display name."""
    user_id: str
    """User ID of user that is requesting to be unbanned."""
    user_login: str
    """The user’s login name."""
    user_name: str
    """The user’s display name."""
    text: str
    """Message sent in the unban request."""
    created_at: datetime
    """The datetime of when the unban request was created."""


class ChannelUnbanRequestResolveData(TwitchObject):
    id: str
    """The ID of the unban request."""
    broadcaster_user_id: str
    """The broadcaster’s user ID for the channel the unban request was updated for."""
    broadcaster_user_login: str
    """The broadcaster’s login name."""
    broadcaster_user_name: str
    """The broadcaster’s display name."""
    moderator_id: str
    """Optional. User ID of moderator who approved/denied the request."""
    moderator_login: str
    """Optional. The moderator’s login name"""
    moderator_name: str
    """Optional. The moderator’s display name"""
    user_id: str
    """User ID of user that requested to be unbanned."""
    user_login: str
    """The user’s login name."""
    user_name: str
    """The user’s display name."""
    resolution_text: str
    """Optional. Resolution text supplied by the mod/broadcaster upon approval/denial of the request."""
    status: str
    """Dictates whether the unban request was approved or denied. Can be the following:
    
    - approved
    - canceled
    - denied
    """


class MessageWithID(Message):
    message_id: str
    """The UUID that identifies the message."""


class ChannelSuspiciousUserMessageData(TwitchObject):
    broadcaster_user_id: str
    """The ID of the channel where the treatment for a suspicious user was updated."""
    broadcaster_user_name: str
    """The display name of the channel where the treatment for a suspicious user was updated."""
    broadcaster_user_login: str
    """The login of the channel where the treatment for a suspicious user was updated."""
    user_id: str
    """The user ID of the user that sent the message."""
    user_name: str
    """The user name of the user that sent the message."""
    user_login: str
    """The user login of the user that sent the message."""
    low_trust_status: str
    """The status set for the suspicious user. Can be the following: “none”, “active_monitoring”, or “restricted”"""
    shared_ban_channel_ids: List[str]
    """A list of channel IDs where the suspicious user is also banned."""
    types: List[str]
    """User types (if any) that apply to the suspicious user, can be “manual”, “ban_evader_detector”, or “shared_channel_ban”."""
    ban_evasion_evaluation: str
    """A ban evasion likelihood value (if any) that as been applied to the user automatically by Twitch, can be “unknown”, “possible”, or “likely”."""
    message: MessageWithID
    """The Chat Message"""


class ChannelSuspiciousUserUpdateData(TwitchObject):
    broadcaster_user_id: str
    """The ID of the channel where the treatment for a suspicious user was updated."""
    broadcaster_user_name: str
    """The display name of the channel where the treatment for a suspicious user was updated."""
    broadcaster_user_login: str
    """The Login of the channel where the treatment for a suspicious user was updated."""
    moderator_user_id: str
    """The ID of the moderator that updated the treatment for a suspicious user."""
    moderator_user_name: str
    """The display name of the moderator that updated the treatment for a suspicious user."""
    moderator_user_login: str
    """The login of the moderator that updated the treatment for a suspicious user."""
    user_id: str
    """The ID of the suspicious user whose treatment was updated."""
    user_name: str
    """The display name of the suspicious user whose treatment was updated."""
    user_login: str
    """The login of the suspicious user whose treatment was updated."""
    low_trust_status: str
    """The status set for the suspicious user. Can be the following: “none”, “active_monitoring”, or “restricted”."""


class ModerateMetadataFollowers(TwitchObject):
    follow_duration_minutes: int
    """The length of time, in minutes, that the followers must have followed the broadcaster to participate in the chat room."""


class ModerateMetadataSlow(TwitchObject):
    wait_time_seconds: int
    """The amount of time, in seconds, that users need to wait between sending messages."""


class ModerateMetadataVip(TwitchObject):
    user_id: str
    """The ID of the user gaining VIP status."""
    user_login: str
    """The login of the user gaining VIP status."""
    user_name: str
    """The user name of the user gaining VIP status."""


class ModerateMetadataUnvip(TwitchObject):
    user_id: str
    """The ID of the user losing VIP status."""
    user_login: str
    """The login of the user losing VIP status."""
    user_name: str
    """The user name of the user losing VIP status."""


class ModerateMetadataMod(TwitchObject):
    user_id: str
    """The ID of the user gaining mod status."""
    user_login: str
    """The login of the user gaining mod status."""
    user_name: str
    """The user name of the user gaining mod status."""


class ModerateMetadataUnmod(TwitchObject):
    user_id: str
    """The ID of the user losing mod status."""
    user_login: str
    """The login of the user losing mod status."""
    user_name: str
    """The user name of the user losing mod status."""


class ModerateMetadataBan(TwitchObject):
    user_id: str
    """The ID of the user being banned."""
    user_login: str
    """The login of the user being banned."""
    user_name: str
    """The user name of the user being banned."""
    reason: Optional[str]
    """Reason given for the ban."""


class ModerateMetadataUnban(TwitchObject):
    user_id: str
    """The ID of the user being unbanned."""
    user_login: str
    """The login of the user being unbanned."""
    user_name: str
    """The user name of the user being unbanned."""


class ModerateMetadataTimeout(TwitchObject):
    user_id: str
    """The ID of the user being timed out."""
    user_login: str
    """The login of the user being timed out."""
    user_name: str
    """The user name of the user being timed out."""
    reason: str
    """Optional. The reason given for the timeout."""
    expires_at: datetime
    """The time at which the timeout ends."""


class ModerateMetadataUntimeout(TwitchObject):
    user_id: str
    """The ID of the user being untimed out."""
    user_login: str
    """The login of the user being untimed out."""
    user_name: str
    """The user name of the user untimed out."""


class ModerateMetadataRaid(TwitchObject):
    user_id: str
    """The ID of the user being raided."""
    user_login: str
    """The login of the user being raided."""
    user_name: str
    """The user name of the user raided."""
    user_name: str
    """The user name of the user raided."""
    viewer_count: int
    """The viewer count."""


class ModerateMetadataUnraid(TwitchObject):
    user_id: str
    """The ID of the user no longer being raided."""
    user_login: str
    """The login of the user no longer being raided."""
    user_name: str
    """The user name of the no longer user raided."""


class ModerateMetadataDelete(TwitchObject):
    user_id: str
    """The ID of the user whose message is being deleted."""
    user_login: str
    """The login of the user."""
    user_name: str
    """The user name of the user."""
    message_id: str
    """The ID of the message being deleted."""
    message_body: str
    """The message body of the message being deleted."""


class ModerateMetadataAutomodTerms(TwitchObject):
    action: str
    """Either “add” or “remove”."""
    list: str
    """Either “blocked” or “permitted”."""
    terms: List[str]
    """Terms being added or removed."""
    from_automod: bool
    """Whether the terms were added due to an Automod message approve/deny action."""


class ModerateMetadataUnbanRequest(TwitchObject):
    is_approved: bool
    """Whether or not the unban request was approved or denied."""
    user_id: str
    """The ID of the banned user."""
    user_login: str
    """The login of the user."""
    user_name: str
    """The user name of the user."""
    moderator_message: str
    """The message included by the moderator explaining their approval or denial."""


class ModerateMetadataWarn(TwitchObject):
    user_id: str
    """The ID of the user being warned."""
    user_login: str
    """The login of the user being warned."""
    user_name: str
    """The user name of the user being warned."""
    reason: Optional[str]
    """Reason given for the warning."""
    chat_rules_cited: Optional[List[str]]
    """Chat rules cited for the warning."""


class ChannelModerateData(TwitchObject):
    broadcaster_user_id: str
    """The ID of the broadcaster."""
    broadcaster_user_login: str
    """The login of the broadcaster."""
    broadcaster_user_name: str
    """The user name of the broadcaster."""
    moderator_user_id: str
    """The ID of the moderator who performed the action."""
    moderator_user_login: str
    """The login of the moderator."""
    moderator_user_name: str
    """The user name of the moderator."""
    action: str
    """The action performed. Possible values are:
    
    - ban
    - timeout
    - unban
    - untimeout
    - clear
    - emoteonly
    - emoteonlyoff
    - followers
    - followersoff
    - uniquechat
    - uniquechatoff
    - slow
    - slowoff
    - subscribers
    - subscribersoff
    - unraid
    - delete
    - vip
    - unvip
    - raid
    - add_blocked_term
    - add_permitted_term
    - remove_blocked_term
    - remove_permitted_term
    - mod
    - unmod
    - approve_unban_request
    - deny_unban_request
    - warn
    """
    followers: Optional[ModerateMetadataFollowers]
    """Metadata associated with the followers command."""
    slow: Optional[ModerateMetadataSlow]
    """Metadata associated with the slow command."""
    vip: Optional[ModerateMetadataVip]
    """Metadata associated with the vip command."""
    unvip: Optional[ModerateMetadataUnvip]
    """Metadata associated with the unvip command."""
    mod: Optional[ModerateMetadataMod]
    """Metadata associated with the mod command."""
    unmod: Optional[ModerateMetadataUnmod]
    """Metadata associated with the unmod command."""
    ban: Optional[ModerateMetadataBan]
    """Metadata associated with the ban command."""
    unban: Optional[ModerateMetadataUnban]
    """Metadata associated with the unban command."""
    timeout: Optional[ModerateMetadataTimeout]
    """Metadata associated with the timeout command."""
    untimeout: Optional[ModerateMetadataUntimeout]
    """Metadata associated with the untimeout command."""
    raid: Optional[ModerateMetadataRaid]
    """Metadata associated with the raid command."""
    unraid: Optional[ModerateMetadataUnraid]
    """Metadata associated with the unraid command."""
    delete: Optional[ModerateMetadataDelete]
    """Metadata associated with the delete command."""
    automod_terms: Optional[ModerateMetadataAutomodTerms]
    """Metadata associated with the automod terms changes."""
    unban_request: Optional[ModerateMetadataUnbanRequest]
    """Metadata associated with an unban request."""
    warn: Optional[ModerateMetadataWarn]
    """Metadata associated with the warn command."""


class ChannelWarningAcknowledgeData(TwitchObject):
    broadcaster_user_id: str
    """The user ID of the broadcaster."""
    broadcaster_user_login: str
    """The login of the broadcaster."""
    broadcaster_user_name: str
    """The user name of the broadcaster."""
    user_id: str
    """The ID of the user that has acknowledged their warning."""
    user_login: str
    """The login of the user that has acknowledged their warning."""
    user_name: str
    """The user name of the user that has acknowledged their warning."""


class ChannelWarningSendData(TwitchObject):
    broadcaster_user_id: str
    """The user ID of the broadcaster."""
    broadcaster_user_login: str
    """The login of the broadcaster."""
    broadcaster_user_name: str
    """The user name of the broadcaster."""
    moderator_user_id: str
    """The user ID of the moderator who sent the warning."""
    moderator_user_login: str
    """The login of the moderator."""
    moderator_user_name: str
    """The user name of the moderator."""
    user_id: str
    """The ID of the user being warned."""
    user_login: str
    """The login of the user being warned."""
    user_name: str
    """The user name of the user being."""
    reason: Optional[str]
    """The reason given for the warning."""
    chat_rules_cited: Optional[List[str]]
    """The chat rules cited for the warning."""


class AutomodMessageHoldData(TwitchObject):
    broadcaster_user_id: str
    """The ID of the broadcaster specified in the request."""
    broadcaster_user_login: str
    """The login of the broadcaster specified in the request."""
    broadcaster_user_name: str
    """The user name of the broadcaster specified in the request."""
    user_id: str
    """The message sender’s user ID."""
    user_login: str
    """The message sender’s login name."""
    user_name: str
    """The message sender’s display name."""
    message_id: str
    """The ID of the message that was flagged by automod."""
    message: Message
    """The body of the message."""
    category: str
    """The category of the message."""
    level: int
    """The level of severity. Measured between 1 to 4."""
    held_at: datetime
    """The timestamp of when automod saved the message."""


class AutomodMessageUpdateData(TwitchObject):
    broadcaster_user_id: str
    """The ID of the broadcaster specified in the request."""
    broadcaster_user_login: str
    """The login of the broadcaster specified in the request."""
    broadcaster_user_name: str
    """The user name of the broadcaster specified in the request."""
    user_id: str
    """The message sender’s user ID."""
    user_login: str
    """The message sender’s login name."""
    user_name: str
    """The message sender’s display name."""
    moderator_user_id: str
    """The ID of the moderator."""
    moderator_user_name: str
    """TThe moderator’s user name."""
    moderator_user_login: str
    """The login of the moderator."""
    message_id: str
    """The ID of the message that was flagged by automod."""
    message: Message
    """The body of the message."""
    category: str
    """The category of the message."""
    level: int
    """The level of severity. Measured between 1 to 4."""
    status: str
    """The message’s status. Possible values are:
    
    - Approved
    - Denied
    - Expired"""
    held_at: datetime
    """The timestamp of when automod saved the message."""


class AutomodSettingsUpdateData(TwitchObject):
    broadcaster_user_id: str
    """The ID of the broadcaster specified in the request."""
    broadcaster_user_login: str
    """The login of the broadcaster specified in the request."""
    broadcaster_user_name: str
    """The user name of the broadcaster specified in the request."""
    moderator_user_id: str
    """The ID of the moderator who changed the channel settings."""
    moderator_user_login: str
    """The moderator’s login."""
    moderator_user_name: str
    """The moderator’s user name."""
    bullying: int
    """The Automod level for hostility involving name calling or insults."""
    overall_level: Optional[int]
    """The default AutoMod level for the broadcaster. This field is None if the broadcaster has set one or more of the individual settings."""
    disability: int
    """The Automod level for discrimination against disability."""
    race_ethnicity_or_religion: int
    """The Automod level for racial discrimination."""
    misogyny: int
    """The Automod level for discrimination against women."""
    sexuality_sex_or_gender: int
    """The AutoMod level for discrimination based on sexuality, sex, or gender."""
    aggression: int
    """The Automod level for hostility involving aggression."""
    sex_based_terms: int
    """The Automod level for sexual content."""
    swearing: int
    """The Automod level for profanity."""


class AutomodTermsUpdateData(TwitchObject):
    broadcaster_user_id: str
    """The ID of the broadcaster specified in the request."""
    broadcaster_user_login: str
    """The login of the broadcaster specified in the request."""
    broadcaster_user_name: str
    """The user name of the broadcaster specified in the request."""
    moderator_user_id: str
    """The ID of the moderator who changed the channel settings."""
    moderator_user_login: str
    """The moderator’s login."""
    moderator_user_name: str
    """The moderator’s user name."""
    action: str
    """The status change applied to the terms. Possible options are:
    
    - add_permitted
    - remove_permitted
    - add_blocked
    - remove_blocked"""
    from_automod: bool
    """Indicates whether this term was added due to an Automod message approve/deny action."""
    terms: List[str]
    """The list of terms that had a status change."""


class ChannelChatUserMessageHoldData(TwitchObject):
    broadcaster_user_id: str
    """The ID of the broadcaster specified in the request."""
    broadcaster_user_login: str
    """The login of the broadcaster specified in the request."""
    broadcaster_user_name: str
    """The user name of the broadcaster specified in the request."""
    user_id: str
    """The User ID of the message sender."""
    user_login: str
    """The message sender’s login."""
    user_name: str
    """The message sender’s display name."""
    message_id: str
    """The ID of the message that was flagged by automod."""
    message: Message
    """The body of the message."""


class ChannelChatUserMessageUpdateData(TwitchObject):
    broadcaster_user_id: str
    """The ID of the broadcaster specified in the request."""
    broadcaster_user_login: str
    """The login of the broadcaster specified in the request."""
    broadcaster_user_name: str
    """The user name of the broadcaster specified in the request."""
    user_id: str
    """The User ID of the message sender."""
    user_login: str
    """The message sender’s login."""
    user_name: str
    """The message sender’s user name."""
    status: str
    """The message’s status. Possible values are:
    
    - approved
    - denied
    - invalid"""
    message_id: str
    """The ID of the message that was flagged by automod."""
    message: Message
    """The body of the message."""


class SharedChatParticipant(TwitchObject):
    broadcaster_user_id: str
    """The User ID of the participant channel."""
    broadcaster_user_name: str
    """The display name of the participant channel."""
    broadcaster_user_login: str
    """The user login of the participant channel."""


class ChannelSharedChatBeginData(TwitchObject):
    session_id: str
    """The unique identifier for the shared chat session."""
    broadcaster_user_id: str
    """The User ID of the channel in the subscription condition which is now active in the shared chat session."""
    broadcaster_user_name: str
    """The display name of the channel in the subscription condition which is now active in the shared chat session."""
    broadcaster_user_login: str
    """The user login of the channel in the subscription condition which is now active in the shared chat session."""
    host_broadcaster_user_id: str
    """The User ID of the host channel."""
    host_broadcaster_user_name: str
    """The display name of the host channel."""
    host_broadcaster_user_login: str
    """The user login of the host channel."""
    participants: List[SharedChatParticipant]
    """The list of participants in the session."""


class ChannelSharedChatUpdateData(TwitchObject):
    session_id: str
    """The unique identifier for the shared chat session."""
    broadcaster_user_id: str
    """The User ID of the channel in the subscription condition."""
    broadcaster_user_name: str
    """The display name of the channel in the subscription condition."""
    broadcaster_user_login: str
    """The user login of the channel in the subscription condition."""
    host_broadcaster_user_id: str
    """The User ID of the host channel."""
    host_broadcaster_user_name: str
    """The display name of the host channel."""
    host_broadcaster_user_login: str
    """The user login of the host channel."""
    participants: List[SharedChatParticipant]
    """The list of participants in the session."""


class ChannelSharedChatEndData(TwitchObject):
    session_id: str
    """The unique identifier for the shared chat session."""
    broadcaster_user_id: str
    """The User ID of the channel in the subscription condition which is no longer active in the shared chat session."""
    broadcaster_user_name: str
    """The display name of the channel in the subscription condition which is no longer active in the shared chat session."""
    broadcaster_user_login: str
    """The user login of the channel in the subscription condition which is no longer active in the shared chat session."""
    host_broadcaster_user_id: str
    """The User ID of the host channel."""
    host_broadcaster_user_name: str
    """The display name of the host channel."""
    host_broadcaster_user_login: str
    """The user login of the host channel."""


# Events

class ChannelPollBeginEvent(TwitchObject):
    subscription: Subscription
    event: ChannelPollBeginData


class ChannelUpdateEvent(TwitchObject):
    subscription: Subscription
    event: ChannelUpdateData


class ChannelFollowEvent(TwitchObject):
    subscription: Subscription
    event: ChannelFollowData


class ChannelSubscribeEvent(TwitchObject):
    subscription: Subscription
    event: ChannelSubscribeData


class ChannelSubscriptionEndEvent(TwitchObject):
    subscription: Subscription
    event: ChannelSubscribeData


class ChannelSubscriptionGiftEvent(TwitchObject):
    subscription: Subscription
    event: ChannelSubscriptionGiftData


class ChannelSubscriptionMessageEvent(TwitchObject):
    subscription: Subscription
    event: ChannelSubscriptionMessageData


class ChannelCheerEvent(TwitchObject):
    subscription: Subscription
    event: ChannelCheerData


class ChannelRaidEvent(TwitchObject):
    subscription: Subscription
    event: ChannelRaidData


class ChannelBanEvent(TwitchObject):
    subscription: Subscription
    event: ChannelBanData


class ChannelUnbanEvent(TwitchObject):
    subscription: Subscription
    event: ChannelUnbanData


class ChannelModeratorAddEvent(TwitchObject):
    subscription: Subscription
    event: ChannelModeratorAddData


class ChannelModeratorRemoveEvent(TwitchObject):
    subscription: Subscription
    event: ChannelModeratorRemoveData


class ChannelPointsCustomRewardAddEvent(TwitchObject):
    subscription: Subscription
    event: ChannelPointsCustomRewardData


class ChannelPointsCustomRewardUpdateEvent(TwitchObject):
    subscription: Subscription
    event: ChannelPointsCustomRewardData


class ChannelPointsCustomRewardRemoveEvent(TwitchObject):
    subscription: Subscription
    event: ChannelPointsCustomRewardData


class ChannelPointsCustomRewardRedemptionAddEvent(TwitchObject):
    subscription: Subscription
    event: ChannelPointsCustomRewardRedemptionData


class ChannelPointsCustomRewardRedemptionUpdateEvent(TwitchObject):
    subscription: Subscription
    event: ChannelPointsCustomRewardRedemptionData


class ChannelPollProgressEvent(TwitchObject):
    subscription: Subscription
    event: ChannelPollProgressData


class ChannelPollEndEvent(TwitchObject):
    subscription: Subscription
    event: ChannelPollEndData


class ChannelPredictionEvent(TwitchObject):
    subscription: Subscription
    event: ChannelPredictionData


class ChannelPredictionEndEvent(TwitchObject):
    subscription: Subscription
    event: ChannelPredictionEndData


class DropEntitlementGrantEvent(TwitchObject):
    subscription: Subscription
    event: DropEntitlementGrantData


class ExtensionBitsTransactionCreateEvent(TwitchObject):
    subscription: Subscription
    event: ExtensionBitsTransactionCreateData


class GoalEvent(TwitchObject):
    subscription: Subscription
    event: GoalData


class HypeTrainEvent(TwitchObject):
    subscription: Subscription
    event: HypeTrainData


class HypeTrainEndEvent(TwitchObject):
    subscription: Subscription
    event: HypeTrainEndData


class StreamOnlineEvent(TwitchObject):
    subscription: Subscription
    event: StreamOnlineData


class StreamOfflineEvent(TwitchObject):
    subscription: Subscription
    event: StreamOfflineData


class UserAuthorizationGrantEvent(TwitchObject):
    subscription: Subscription
    event: UserAuthorizationGrantData


class UserAuthorizationRevokeEvent(TwitchObject):
    subscription: Subscription
    event: UserAuthorizationRevokeData


class UserUpdateEvent(TwitchObject):
    subscription: Subscription
    event: UserUpdateData


class ShieldModeEvent(TwitchObject):
    subscription: Subscription
    event: ShieldModeData


class CharityCampaignStartEvent(TwitchObject):
    subscription: Subscription
    event: CharityCampaignStartData


class CharityCampaignProgressEvent(TwitchObject):
    subscription: Subscription
    event: CharityCampaignProgressData


class CharityCampaignStopEvent(TwitchObject):
    subscription: Subscription
    event: CharityCampaignStopData


class CharityDonationEvent(TwitchObject):
    subscription: Subscription
    event: CharityDonationData


class ChannelShoutoutCreateEvent(TwitchObject):
    subscription: Subscription
    event: ChannelShoutoutCreateData


class ChannelShoutoutReceiveEvent(TwitchObject):
    subscription: Subscription
    event: ChannelShoutoutReceiveData


class ChannelChatClearEvent(TwitchObject):
    subscription: Subscription
    event: ChannelChatClearData


class ChannelChatClearUserMessagesEvent(TwitchObject):
    subscription: Subscription
    event: ChannelChatClearUserMessagesData


class ChannelChatMessageDeleteEvent(TwitchObject):
    subscription: Subscription
    event: ChannelChatMessageDeleteData


class ChannelChatNotificationEvent(TwitchObject):
    subscription: Subscription
    event: ChannelChatNotificationData


class ChannelAdBreakBeginEvent(TwitchObject):
    subscription: Subscription
    event: ChannelAdBreakBeginData


class ChannelChatMessageEvent(TwitchObject):
    subscription: Subscription
    event: ChannelChatMessageData


class ChannelChatSettingsUpdateEvent(TwitchObject):
    subscription: Subscription
    event: ChannelChatSettingsUpdateData


class UserWhisperMessageEvent(TwitchObject):
    subscription: Subscription
    event: UserWhisperMessageData


class ChannelPointsAutomaticRewardRedemptionAddEvent(TwitchObject):
    subscription: Subscription
    event: ChannelPointsAutomaticRewardRedemptionAddData


class ChannelVIPAddEvent(TwitchObject):
    subscription: Subscription
    event: ChannelVIPAddData


class ChannelVIPRemoveEvent(TwitchObject):
    subscription: Subscription
    event: ChannelVIPRemoveData


class ChannelUnbanRequestCreateEvent(TwitchObject):
    subscription: Subscription
    event: ChannelUnbanRequestCreateData


class ChannelUnbanRequestResolveEvent(TwitchObject):
    subscription: Subscription
    event: ChannelUnbanRequestResolveData


class ChannelSuspiciousUserMessageEvent(TwitchObject):
    subscription: Subscription
    event: ChannelSuspiciousUserMessageData


class ChannelSuspiciousUserUpdateEvent(TwitchObject):
    subscription: Subscription
    event: ChannelSuspiciousUserUpdateData


class ChannelModerateEvent(TwitchObject):
    subscription: Subscription
    event: ChannelModerateData


class ChannelWarningAcknowledgeEvent(TwitchObject):
    subscription: Subscription
    event: ChannelWarningAcknowledgeData


class ChannelWarningSendEvent(TwitchObject):
    subscription: Subscription
    event: ChannelWarningSendData


class AutomodMessageHoldEvent(TwitchObject):
    subscription: Subscription
    event: AutomodMessageHoldData


class AutomodMessageUpdateEvent(TwitchObject):
    subscription: Subscription
    event: AutomodMessageUpdateData


class AutomodSettingsUpdateEvent(TwitchObject):
    subscription: Subscription
    event: AutomodSettingsUpdateData


class AutomodTermsUpdateEvent(TwitchObject):
    subscription: Subscription
    event: AutomodTermsUpdateData


class ChannelChatUserMessageHoldEvent(TwitchObject):
    subscription: Subscription
    event: ChannelChatUserMessageHoldData


class ChannelChatUserMessageUpdateEvent(TwitchObject):
    subscription: Subscription
    event: ChannelChatUserMessageUpdateData


class ChannelSharedChatBeginEvent(TwitchObject):
    subscription: Subscription
    event: ChannelSharedChatBeginData


class ChannelSharedChatUpdateEvent(TwitchObject):
    subscription: Subscription
    event: ChannelSharedChatUpdateData


class ChannelSharedChatEndEvent(TwitchObject):
    subscription: Subscription
    event: ChannelSharedChatEndData
