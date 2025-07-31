TikTokAPI Quick Start
View the above tree for detailed documentation on the package.

Unofficial TikTok API in Python
This is an unofficial api wrapper for TikTok.com in python. With this api you are able to call most trending and fetch specific user information as well as much more.

DOI LinkedIn Sponsor Me GitHub release (latest by date) GitHub Downloads  Support Server

This api is designed to retrieve data TikTok. It can not be used post or upload content to TikTok on the behalf of a user. It has no support for any user-authenticated routes, if you can’t access it while being logged out on their website you can’t access it here.

Sponsors
These sponsors have paid to be placed here or are my own affiliate links which I may earn a commission from, and beyond that I do not have any affiliation with them. The TikTokAPI package will always be free and open-source. If you wish to be a sponsor of this project check out my GitHub sponsors page.

TikApi
TikAPI is a paid TikTok API service providing a full out-of-the-box solution, making life easier for developers — trusted by 500+ companies.

Ensemble Data
EnsembleData is the leading API provider for scraping Tiktok, Instagram, Youtube, and more.
Trusted by the major influencer marketing and social media listening platforms.

TikTok Captcha Solver
TikTok Captcha Solver: Bypass any TikTok captcha in just two lines of code.
Scale your TikTok automation and get unblocked with SadCaptcha.

TikTok Captcha Solver
Cheap, Reliable Proxies: Supercharge your web scraping with fast, reliable proxies. Try 10 free datacenter proxies today!
Table of Contents
Documentation

Getting Started

How to Support The Project

Installing

Common Issues

Quick Start Guide

Examples

Upgrading from V5 to V6

Documentation
You can find the full documentation here

Getting Started
To get started using this API follow the instructions below.

Note: If you want to learn how to web scrape websites check my free and open-source course for learning everything web scraping

How to Support The Project
Star the repo 😎

Consider sponsoring me on GitHub

Send me an email or a LinkedIn message telling me what you’re using the API for, I really like hearing what people are using it for.

Submit PRs for issues :)

Installing
Note: Installation requires python3.9+

If you run into an issue please check the closed issues on the github, although feel free to re-open a new issue if you find an issue that’s been closed for a few months. The codebase can and does run into similar issues as it has before, because TikTok changes things up.

pip install TikTokApi
python -m playwright install
If you would prefer a video walk through of setting up this package YouTube video just for that. (is a version out of date, installation is the same though)

If you want a quick video to listen for TikTok Live events in python.

Docker Installation
Clone this repository onto a local machine (or just the Dockerfile since it installs TikTokApi from pip) then run the following commands.

docker pull mcr.microsoft.com/playwright:focal
docker build . -t tiktokapi:latest
docker run -v TikTokApi --rm tiktokapi:latest python3 your_script.py
Note this assumes your script is named your_script.py and lives in the root of this directory.

Common Issues
EmptyResponseException - this means TikTok is blocking the request and detects you’re a bot. This can be a problem with your setup or the library itself

you may need a proxy to successfuly scrape TikTok, I’ve made a web scraping lesson explaining the differences of “tiers” of proxies, I’ve personally had success with webshare’s residential proxies (affiliate link), but you might have success on their free data center IPs or a cheaper competitor.

Browser Has no Attribute - make sure you ran python3 -m playwright install, if your error persists try the playwright-python quickstart guide and diagnose issues from there.

API methods returning Coroutine - many of the API’s methods are async so make sure your program awaits them for proper functionality

Quick Start Guide
Here’s a quick bit of code to get the most recent trending videos on TikTok. There’s more examples in the examples directory.

Note: If you want to learn how to web scrape websites check my free and open-source course for web scraping

from TikTokApi import TikTokApi
import asyncio
import os

ms_token = os.environ.get("ms_token", None) # get your own ms_token from your cookies on tiktok.com

async def trending_videos():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        async for video in api.trending.videos(count=30):
            print(video)
            print(video.as_dict)

if __name__ == "__main__":
    asyncio.run(trending_videos())
To directly run the example scripts from the repository root, use the -m option on python.

python -m examples.trending_example
You can access the full data dictionary the object was created from with .as_dict. On a video this may look like this. TikTok changes their structure from time to time so it’s worth investigating the structure of the dictionary when you use this package.



TikTokApi package
Subpackages
TikTokApi.api package
Comment
User
Trending
Search
Hashtags
Sound
Video
TikTokApi Main Class
This is the main TikTokApi module. It contains the TikTokApi class which is the main class of the package.

classTikTokApi.tiktok.TikTokApi(logging_level: int = 30, logger_name: str = None)[source]
Bases: object

The main TikTokApi class that contains all the endpoints.

Import With:
from TikTokApi import TikTokApi
api = TikTokApi()
asyncclose_sessions()[source]
Close all the sessions. Should be called when you’re done with the TikTokApi object

comment
alias of Comment

asynccreate_sessions(num_sessions=5, headless=True, ms_tokens: list[str] = None, proxies: list = None, sleep_after=1, starting_url='https://www.tiktok.com', context_options: dict = {}, override_browser_args: list[dict] = None, cookies: list[dict] = None, suppress_resource_load_types: list[str] = None, browser: str = 'chromium', executable_path: str = None, timeout: int = 30000)[source]
Create sessions for use within the TikTokApi class.

These sessions are what will carry out requesting your data from TikTok.

Parameters
:
num_sessions (int) – The amount of sessions you want to create.

headless (bool) – Whether or not you want the browser to be headless.

ms_tokens (list[str]) – A list of msTokens to use for the sessions, you can get these from your cookies after visiting TikTok. If you don’t provide any, the sessions will try to get them themselves, but this is not guaranteed to work.

proxies (list) – A list of proxies to use for the sessions

sleep_after (int) – The amount of time to sleep after creating a session, this is to allow the msToken to be generated.

starting_url (str) – The url to start the sessions on, this is usually https://www.tiktok.com.

context_options (dict) – Options to pass to the playwright context.

override_browser_args (list[dict]) – A list of dictionaries containing arguments to pass to the browser.

cookies (list[dict]) – A list of cookies to use for the sessions, you can get these from your cookies after visiting TikTok.

suppress_resource_load_types (list[str]) – Types of resources to suppress playwright from loading, excluding more types will make playwright faster.. Types: document, stylesheet, image, media, font, script, textrack, xhr, fetch, eventsource, websocket, manifest, other.

browser (str) – firefox, chromium, or webkit; default is chromium

executable_path (str) – Path to the browser executable

timeout (int) – The timeout in milliseconds for page navigation

Example Usage:
from TikTokApi import TikTokApi
with TikTokApi() as api:
    await api.create_sessions(num_sessions=5, ms_tokens=['msToken1', 'msToken2'])
generate_js_fetch(method: str, url: str, headers: dict)→ str[source]
Generate a javascript fetch function for use in playwright

asyncgenerate_x_bogus(url: str, **kwargs)[source]
Generate the X-Bogus header for a url

asyncget_session_content(url: str, **kwargs)[source]
Get the content of a url

asyncget_session_cookies(session)[source]
Get the cookies for a session

Parameters
:
session (TikTokPlaywrightSession) – The session to get the cookies for.

Returns
:
The cookies for the session.

Return type
:
dict

hashtag
alias of Hashtag

asyncmake_request(url: str, headers: dict = None, params: dict = None, retries: int = 3, exponential_backoff: bool = True, **kwargs)[source]
Makes a request to TikTok through a session.

Parameters
:
url (str) – The url to make the request to.

headers (dict) – The headers to use for the request.

params (dict) – The params to use for the request.

retries (int) – The amount of times to retry the request if it fails.

exponential_backoff (bool) – Whether or not to use exponential backoff when retrying the request.

session_index (int) – The index of the session you want to use, if not provided a random session will be used.

Returns
:
The json response from TikTok.

Return type
:
dict

Raises
:
Exception – If the request fails.

playlist
alias of Playlist

asyncrun_fetch_script(url: str, headers: dict, **kwargs)[source]
Execute a javascript fetch function in a session

Parameters
:
url (str) – The url to fetch.

headers (dict) – The headers to use for the fetch.

Returns
:
The result of the fetch. Seems to be a string or dict

Return type
:
any

search
alias of Search

asyncset_session_cookies(session, cookies)[source]
Set the cookies for a session

Parameters
:
session (TikTokPlaywrightSession) – The session to set the cookies for.

cookies (dict) – The cookies to set for the session.

asyncsign_url(url: str, **kwargs)[source]
Sign a url

sound
alias of Sound

asyncstop_playwright()[source]
Stop the playwright browser

trending
alias of Trending

user
alias of User

video
alias of Video

classTikTokApi.tiktok.TikTokPlaywrightSession(context: Any, page: Any, proxy: str = None, params: dict = None, headers: dict = None, ms_token: str = None, base_url: str = 'https://www.tiktok.com')[source]
Bases: object

A TikTok session using Playwright

base_url: str= 'https://www.tiktok.com'
context: Any
headers: dict= None
ms_token: str= None
page: Any
params: dict= None
proxy: str= None
TikTokApi.exceptions module
exceptionTikTokApi.exceptions.CaptchaException(raw_response, message, error_code=None)[source]
Bases: TikTokException

TikTok is showing captcha

exceptionTikTokApi.exceptions.EmptyResponseException(raw_response, message, error_code=None)[source]
Bases: TikTokException

TikTok sent back an empty response.

exceptionTikTokApi.exceptions.InvalidJSONException(raw_response, message, error_code=None)[source]
Bases: TikTokException

TikTok returned invalid JSON.

exceptionTikTokApi.exceptions.InvalidResponseException(raw_response, message, error_code=None)[source]
Bases: TikTokException

The response from TikTok was invalid.

exceptionTikTokApi.exceptions.NotFoundException(raw_response, message, error_code=None)[source]
Bases: TikTokException

TikTok indicated that this object does not exist.

exceptionTikTokApi.exceptions.SoundRemovedException(raw_response, message, error_code=None)[source]
Bases: TikTokException

This TikTok sound has no id from being removed by TikTok.

exceptionTikTokApi.exceptions.TikTokException(raw_response, message, error_code=None)[source]
Bases: Exception

Generic exception that all other TikTok errors are children of.

TikTokApi.helpers module
TikTokApi.helpers.extract_video_id_from_url(url, headers={}, proxy=None)[source]
TikTokApi.helpers.random_choice(choices: list)[source]
Return a random choice from a list, or None if the list is empty

TikTokApi.helpers.requests_cookie_to_playwright_cookie(req_c)[source]

TikTokApi.api package
This package wraps each entity from TikTok into a class with high-level methods to interact with the TikTok object.

Comment
TikTokApi.api.comment module
classTikTokApi.api.comment.Comment(data: dict | None = None)[source]
Bases: object

A TikTok Comment.

Example Usage
for comment in video.comments:
    print(comment.text)
    print(comment.as_dict)
as_dict: dict
The raw data associated with this comment

author: ClassVar[User]
The author of the comment

id: str
The id of the comment

likes_count: int
The amount of likes of the comment

parent: ClassVar[TikTokApi]
asyncreplies(count=20, cursor=0, **kwargs)→ AsyncIterator[Comment][source]
text: str
The contents of the comment

User
TikTokApi.api.user module
classTikTokApi.api.user.User(username: str | None = None, user_id: str | None = None, sec_uid: str | None = None, data: dict | None = None)[source]
Bases: object

A TikTok User.

Example Usage:
user = api.user(username='therock')
as_dict: dict
The raw data associated with this user.

asyncinfo(**kwargs)→ dict[source]
Returns a dictionary of information associated with this User.

Returns
:
A dictionary of information associated with this User.

Return type
:
dict

Raises
:
InvalidResponseException – If TikTok returns an invalid response, or one we don’t understand.

Example Usage:
user_data = await api.user(username='therock').info()
asyncliked(count: int = 30, cursor: int = 0, **kwargs)→ AsyncIterator[Video][source]
Returns a user’s liked posts if public.

Parameters
:
count (int) – The amount of recent likes you want returned.

cursor (int) – The the offset of likes from 0 you want to get.

Returns
:
Yields TikTokApi.video objects.

Return type
:
async iterator/generator

Raises
:
InvalidResponseException – If TikTok returns an invalid response, the user’s likes are private, or one we don’t understand.

Example Usage:
async for like in api.user(username="davidteathercodes").liked():
    # do something
parent: ClassVar[TikTokApi]
asyncplaylists(count=20, cursor=0, **kwargs)→ AsyncIterator[Playlist][source]
Returns a user’s playlists.

Returns
:
Yields TikTokApi.playlist objects.

Return type
:
async iterator/generator

Raises
:
InvalidResponseException – If TikTok returns an invalid response, or one we don’t understand.

Example Usage:
async for playlist in await api.user(username='therock').playlists():
    # do something
sec_uid: str
The sec UID of the user.

user_id: str
The ID of the user.

username: str
The username of the user.

asyncvideos(count=30, cursor=0, **kwargs)→ AsyncIterator[Video][source]
Returns a user’s videos.

Parameters
:
count (int) – The amount of videos you want returned.

cursor (int) – The the offset of videos from 0 you want to get.

Returns
:
Yields TikTokApi.video objects.

Return type
:
async iterator/generator

Raises
:
InvalidResponseException – If TikTok returns an invalid response, or one we don’t understand.

Example Usage:
async for video in api.user(username="davidteathercodes").videos():
    # do something
Trending
TikTokApi.api.trending module
classTikTokApi.api.trending.Trending[source]
Bases: object

Contains static methods related to trending objects on TikTok.

parent: TikTokApi
staticvideos(count=30, **kwargs)→ AsyncIterator[Video][source]
Returns Videos that are trending on TikTok.

Parameters
:
count (int) – The amount of videos you want returned.

Returns
:
Yields TikTokApi.video objects.

Return type
:
async iterator/generator

Raises
:
InvalidResponseException – If TikTok returns an invalid response, or one we don’t understand.

Example Usage:
async for video in api.trending.videos():
    # do something
Search
TikTokApi.api.search module
classTikTokApi.api.search.Search[source]
Bases: object

Contains static methods about searching TikTok for a phrase.

parent: TikTokApi
staticsearch_type(search_term, obj_type, count=10, cursor=0, **kwargs)→ AsyncIterator[source]
Searches for a specific type of object. But you shouldn’t use this directly, use the other methods.

Note: Your ms_token needs to have done a search before for this to work. Note: Currently only supports searching for users, other endpoints require auth.

Parameters
:
search_term (str) – The phrase you want to search for.

obj_type (str) – The type of object you want to search for (user)

count (int) – The amount of users you want returned.

cursor (int) – The the offset of users from 0 you want to get.

Returns
:
Yields TikTokApi.video objects.

Return type
:
async iterator/generator

Raises
:
InvalidResponseException – If TikTok returns an invalid response, or one we don’t understand.

Example Usage:
async for user in api.search.search_type('david teather', 'user'):
    # do something
staticusers(search_term, count=10, cursor=0, **kwargs)→ AsyncIterator[User][source]
Searches for users.

Note: Your ms_token needs to have done a search before for this to work.

Parameters
:
search_term (str) – The phrase you want to search for.

count (int) – The amount of users you want returned.

Returns
:
Yields TikTokApi.user objects.

Return type
:
async iterator/generator

Raises
:
InvalidResponseException – If TikTok returns an invalid response, or one we don’t understand.

Example Usage:
async for user in api.search.users('david teather'):
    # do something
Hashtags
TikTokApi.api.hashtag module
classTikTokApi.api.hashtag.Hashtag(name: str | None = None, id: str | None = None, data: dict | None = None)[source]
Bases: object

A TikTok Hashtag/Challenge.

Example Usage
hashtag = api.hashtag(name='funny')
async for video in hashtag.videos():
    print(video.id)
as_dict: dict
The raw data associated with this hashtag.

id: str | None
The ID of the hashtag

asyncinfo(**kwargs)→ dict[source]
Returns all information sent by TikTok related to this hashtag.

Example Usage
hashtag = api.hashtag(name='funny')
hashtag_data = await hashtag.info()
name: str | None
The name of the hashtag (omiting the #)

parent: ClassVar[TikTokApi]
asyncvideos(count=30, cursor=0, **kwargs)→ AsyncIterator[Video][source]
Returns TikTok videos that have this hashtag in the caption.

Parameters
:
count (int) – The amount of videos you want returned.

cursor (int) – The the offset of videos from 0 you want to get.

Returns
:
Yields TikTokApi.video objects.

Return type
:
async iterator/generator

Raises
:
InvalidResponseException – If TikTok returns an invalid response, or one we don’t understand.

Example Usage:
async for video in api.hashtag(name='funny').videos():
    # do something
Sound
TikTokApi.api.sound module
classTikTokApi.api.sound.Sound(id: str | None = None, data: str | None = None)[source]
Bases: object

A TikTok Sound/Music/Song.

Example Usage
song = api.song(id='7016547803243022337')
author: User | None
The author of the song (if it exists)

duration: int | None
The duration of the song in seconds.

id: str
TikTok’s ID for the sound

asyncinfo(**kwargs)→ dict[source]
Returns all information sent by TikTok related to this sound.

Returns
:
The raw data returned by TikTok.

Return type
:
dict

Raises
:
InvalidResponseException – If TikTok returns an invalid response, or one we don’t understand.

Example Usage:
sound_info = await api.sound(id='7016547803243022337').info()
original: bool | None
Whether the song is original or not.

parent: ClassVar[TikTokApi]
title: str | None
The title of the song.

asyncvideos(count=30, cursor=0, **kwargs)→ AsyncIterator[Video][source]
Returns Video objects of videos created with this sound.

Parameters
:
count (int) – The amount of videos you want returned.

cursor (int) – The the offset of videos from 0 you want to get.

Returns
:
Yields TikTokApi.video objects.

Return type
:
async iterator/generator

Raises
:
InvalidResponseException – If TikTok returns an invalid response, or one we don’t understand.

Example Usage:
async for video in api.sound(id='7016547803243022337').videos():
    # do something
Video
TikTokApi.api.video module
classTikTokApi.api.video.Video(id: str | None = None, url: str | None = None, data: dict | None = None, **kwargs)[source]
Bases: object

A TikTok Video class

Example Usage `py video = api.video(id='7041997751718137094') `

as_dict: dict
The raw data associated with this Video.

author: User | None
The User who created the Video

asyncbytes(stream: bool = False, **kwargs)→ bytes | AsyncIterator[bytes][source]
Returns the bytes of a TikTok Video.

Example Usage:
video_bytes = await api.video(id='7041997751718137094').bytes()

# Saving The Video
with open('saved_video.mp4', 'wb') as output:
    output.write(video_bytes)

# Streaming (if stream=True)
async for chunk in api.video(id='7041997751718137094').bytes(stream=True):
    # Process or upload chunk
asynccomments(count=20, cursor=0, **kwargs)→ AsyncIterator[Comment][source]
Returns the comments of a TikTok Video.

Parameters
:
count (int) – The amount of comments you want returned.

cursor (int) – The the offset of comments from 0 you want to get.

Returns
:
Yields TikTokApi.comment objects.

Return type
:
async iterator/generator

Example Usage .. code-block:: python

async for comment in api.video(id=’7041997751718137094’).comments():
# do something

```

create_time: datetime | None
The creation time of the Video

hashtags: list[Hashtag] | None
A List of Hashtags on the Video

id: str | None
TikTok’s ID of the Video

asyncinfo(**kwargs)→ dict[source]
Returns a dictionary of all data associated with a TikTok Video.

Note: This is slow since it requires an HTTP request, avoid using this if possible.

Returns
:
A dictionary of all data associated with a TikTok Video.

Return type
:
dict

Raises
:
InvalidResponseException – If TikTok returns an invalid response, or one we don’t understand.

Example Usage:
url = "https://www.tiktok.com/@davidteathercodes/video/7106686413101468970"
video_info = await api.video(url=url).info()
parent: ClassVar[TikTokApi]
asyncrelated_videos(count: int = 30, cursor: int = 0, **kwargs)→ AsyncIterator[Video][source]
Returns related videos of a TikTok Video.

Parameters
:
count (int) – The amount of comments you want returned.

cursor (int) – The the offset of comments from 0 you want to get.

Returns
:
Yields TikTokApi.video objects.

Return type
:
async iterator/generator

Example Usage .. code-block:: python

async for related_videos in api.video(id=’7041997751718137094’).related_videos():
# do something

```

sound: Sound | None
The Sound that is associated with the Video

stats: dict | None
TikTok’s stats of the Video

url: str | None
The URL of the Video


Python Module Index




-	TikTokApi	
    TikTokApi.api.comment	
    TikTokApi.api.hashtag	
    TikTokApi.api.search	
    TikTokApi.api.sound	
    TikTokApi.api.trending	
    TikTokApi.api.user	
    TikTokApi.api.video	
    TikTokApi.exceptions	
    TikTokApi.helpers	
    TikTokApi.stealth.stealth	
    TikTokApi.tiktok	
https://davidteather.github.io/TikTok-Api/genindex.html