"""
CLI is a controller for the command line use of this library
"""

import datetime
from argparse import ArgumentParser, Namespace
from os.path import exists, join

import pytz

from tiktok_uploader.auth import login_accounts, save_cookies
from tiktok_uploader.types import ProxyDict
from tiktok_uploader.upload import TikTokUploader


def main() -> None:
    """
    Passes arguments into the program
    """
    args = get_uploader_args()
    validate_uploader_args(args)

    # parse args
    schedule = parse_schedule(args.schedule)
    proxy = parse_proxy(args.proxy)
    product_id = args.product_id
    visibility = args.visibility
    sound_name = args.sound_name
    sound_artist = args.sound_artist

    # runs the program using the arguments provided
    with TikTokUploader(
        username=args.username,
        password=args.password,
        cookies=args.cookies,
        proxy=proxy,
        sessionid=args.sessionid,
        headless=not args.attach,
    ) as uploader:
        result = uploader.upload_video(
            filename=args.video,
            description=args.description,
            schedule=schedule,
            product_id=product_id,
            cover=args.cover,
            visibility=visibility,
            sound_name=sound_name,
            sound_artist=sound_artist,
        )

    print("-------------------------")
    if not result:
        print("Error while uploading video")
    else:
        print("Video uploaded successfully")
    print("-------------------------")


def get_uploader_args() -> Namespace:
    """
    Generates a parser which is used to get all of the video's information
    """
    parser = ArgumentParser(
        description="TikTok uploader is a video uploader which can upload a"
        + "video from your computer to the TikTok using playwright automation"
    )

    # primary arguments
    parser.add_argument("-v", "--video", help="Video file", required=True)
    parser.add_argument("-d", "--description", help="Description", default="")

    # secondary arguments
    parser.add_argument(
        "-t",
        "--schedule",
        help="Schedule UTC time in %%Y-%%m-%%d %%H:%%M format ",
        default=None,
    )
    parser.add_argument(
        "--proxy", help="Proxy user:pass@host:port or host:port format", default=None
    )
    parser.add_argument(
        "--product-id",
        help="ID of the product to link in the video (if applicable)",
        default=None,
    )
    parser.add_argument(
        "--visibility",
        help="Video visibility: everyone (default), friends, or only_you",
        choices=["everyone", "friends", "only_you"],
        default="everyone",
    )
    parser.add_argument("--cover", help="Custom cover image file", default=None)
    parser.add_argument(
        "--sound-name",
        help="Name of the TikTok sound/music to add as background music",
        default=None,
    )
    parser.add_argument(
        "--sound-artist",
        help="Artist name to refine sound search (optional, used with --sound-name)",
        default=None,
    )

    # authentication arguments
    parser.add_argument("-c", "--cookies", help="The cookies you want to use")
    parser.add_argument("-s", "--sessionid", help="The session id you want to use")

    parser.add_argument("-u", "--username", help="Your TikTok email / username")
    parser.add_argument("-p", "--password", help="Your TikTok password")

    # playwright arguments
    parser.add_argument(
        "--attach",
        "-a",
        action="store_true",
        default=False,
        help="Runs the program in headful mode (shows browser window)",
    )

    return parser.parse_args()


def validate_uploader_args(args: Namespace) -> None:
    """
    Preforms validation on each input given
    """

    # Makes sure the video file exists
    if not exists(args.video):
        raise FileNotFoundError(f"Could not find the video file at {args.video}")

    # Makes sure the optional cover image file exists
    if args.cover and not exists(args.cover):
        raise FileNotFoundError(f"Could not find the cover image file at {args.cover}")

    # User can not pass in both cookies and username / password
    if args.cookies and (args.username or args.password):
        raise ValueError("You can not pass in both cookies and username / password")


def auth() -> None:
    """
    Authenticates the user
    """
    args = get_auth_args()
    validate_auth_args(args=args)

    # runs the program using the arguments provided
    if args.input:
        login_info = get_login_info(path=args.input, header=args.header)
    else:
        login_info = [(args.username, args.password)]

    username_and_cookies = login_accounts(accounts=login_info)

    for username, cookies in username_and_cookies.items():
        save_cookies(path=join(args.output, username + ".txt"), cookies=cookies)


def get_auth_args() -> Namespace:
    """
    Generates a parser which is used to get all of the authentication information
    """
    parser = ArgumentParser(
        description="TikTok Auth is a program which can log you into multiple accounts sequentially"
    )

    # authentication arguments
    parser.add_argument(
        "-o", "--output", default="tmp", help="The output folder to save the cookies to"
    )
    parser.add_argument("-i", "--input", help="A csv file with username and password")
    # parser.add_argument('-h', '--header', default=True,
    # help='The header of the csv file which contains the username and password')
    parser.add_argument("-u", "--username", help="Your TikTok email / username")
    parser.add_argument("-p", "--password", help="Your TikTok password")

    return parser.parse_args()


def validate_auth_args(args: Namespace) -> None:
    """
    Preforms validation on each input given
    """
    # username and password or input files are mutually exclusive
    if args.username and args.password and args.input:
        raise ValueError("You can not pass in both username / password and input file")


def get_login_info(path: str, header: bool = True) -> list[tuple[str, str]]:
    """
    Parses the input file into a list of usernames and passwords
    """

    def extract_username_and_pass(input_str: str) -> tuple[str, str]:
        split_string = input_str.strip().split(",")
        if len(split_string) != 2:
            raise ValueError(f"{input_str} not valid")

        user, password = split_string

        return user, password

    with open(path, encoding="utf-8") as file:
        parsed_file = file.readlines()
        if header:
            parsed_file = parsed_file[1:]

        return [extract_username_and_pass(line) for line in parsed_file]


def parse_schedule(schedule_raw: str | None) -> datetime.datetime | None:
    return (
        datetime.datetime.strptime(schedule_raw, "%Y-%m-%d %H:%M")
        if schedule_raw
        else None
    )


def generate_schedule_times(
    schedule_from: datetime.datetime,
    interval_minutes: int,
    count: int,
) -> list[datetime.datetime | None]:
    """Returns ``count`` UTC-naive datetimes spaced ``interval_minutes`` apart."""
    return [
        schedule_from + datetime.timedelta(minutes=i * interval_minutes)
        for i in range(count)
    ]


def get_batch_args() -> Namespace:
    """
    Argument parser for the batch-upload command.
    """
    parser = ArgumentParser(
        description="Batch-upload multiple TikTok videos with optional scheduled posting"
    )

    parser.add_argument(
        "-v",
        "--video",
        action="append",
        required=True,
        metavar="VIDEO",
        help="Video file to upload (repeat for each video: -v a.mp4 -v b.mp4)",
    )
    parser.add_argument(
        "-d",
        "--description",
        action="append",
        default=[],
        metavar="DESCRIPTION",
        help="Description for each video in order (repeat to match -v flags)",
    )
    parser.add_argument(
        "--schedule-from",
        help="UTC start time for scheduled posting in YYYY-MM-DD HH:MM format",
        default=None,
    )
    parser.add_argument(
        "--schedule-interval",
        type=int,
        default=1440,
        help="Minutes between each video's scheduled publish time (default: 1440 = 24 h)",
    )
    parser.add_argument(
        "--timezone",
        default="Europe/Copenhagen",
        help="Timezone for --schedule-from (default: Europe/Copenhagen). "
        "Accepts any tz database name, e.g. Asia/Shanghai, America/New_York.",
    )
    parser.add_argument(
        "--proxy",
        help="Proxy in user:pass@host:port or host:port format",
        default=None,
    )
    parser.add_argument(
        "--visibility",
        choices=["everyone", "friends", "only_you"],
        default="everyone",
        help="Video visibility (default: everyone)",
    )
    parser.add_argument("-c", "--cookies", help="Path to cookies file")
    parser.add_argument("-s", "--sessionid", help="TikTok session ID")
    parser.add_argument("-u", "--username", help="TikTok email / username")
    parser.add_argument("-p", "--password", help="TikTok password")
    parser.add_argument(
        "--attach",
        "-a",
        action="store_true",
        default=False,
        help="Run in headful mode (shows browser window)",
    )

    return parser.parse_args()


def validate_batch_args(args: Namespace) -> None:
    """
    Validates arguments for the batch-upload command.
    """
    for path in args.video:
        if not exists(path):
            raise FileNotFoundError(f"Could not find video file: {path}")

    if args.cookies and (args.username or args.password):
        raise ValueError("You cannot pass both cookies and username/password")

    if args.schedule_from is not None:
        schedule_from_naive = parse_schedule(args.schedule_from)
        if schedule_from_naive is None:
            raise ValueError("--schedule-from must be in YYYY-MM-DD HH:MM format")

        try:
            tz = pytz.timezone(args.timezone)
        except pytz.UnknownTimeZoneError:
            raise ValueError(f"Unknown timezone: {args.timezone!r}")

        schedule_from_utc = tz.localize(schedule_from_naive).astimezone(pytz.UTC)

        count = len(args.video)
        last_schedule_utc = schedule_from_utc + datetime.timedelta(
            minutes=(count - 1) * args.schedule_interval
        )
        max_allowed = pytz.UTC.localize(
            datetime.datetime.utcnow()
        ) + datetime.timedelta(days=10)
        if last_schedule_utc > max_allowed:
            raise ValueError(
                f"The last video would be scheduled at {last_schedule_utc:%Y-%m-%d %H:%M} UTC, "
                f"which exceeds TikTok's 10-day limit ({max_allowed:%Y-%m-%d %H:%M} UTC). "
                "Reduce --schedule-interval or the number of videos."
            )


def batch_upload() -> None:
    """
    Entry point for batch uploading multiple videos with optional scheduled posting.

    Usage example::

        tiktok-uploader-batch \\
            -v video1.mp4 -v video2.mp4 -v video3.mp4 \\
            --schedule-from "2026-03-20 10:00" \\
            --schedule-interval 240 \\
            -c cookies.txt
    """
    args = get_batch_args()
    validate_batch_args(args)

    videos = args.video
    descriptions: list[str] = args.description or []
    proxy = parse_proxy(args.proxy)
    visibility = args.visibility

    schedules: list[datetime.datetime | None] = [None] * len(videos)
    if args.schedule_from is not None:
        schedule_from_naive = parse_schedule(args.schedule_from)
        assert schedule_from_naive is not None  # already validated above
        tz = pytz.timezone(args.timezone)
        schedule_from_utc = tz.localize(schedule_from_naive).astimezone(pytz.UTC)
        schedules = generate_schedule_times(
            schedule_from_utc, args.schedule_interval, len(videos)
        )

    video_dicts = []
    for i, path in enumerate(videos):
        vd: dict = {
            "path": path,
            "description": descriptions[i] if i < len(descriptions) else "",
        }
        if schedules[i] is not None:
            vd["schedule"] = schedules[i]
        if visibility != "everyone":
            vd["visibility"] = visibility
        video_dicts.append(vd)

    with TikTokUploader(
        username=args.username or "",
        password=args.password or "",
        cookies=args.cookies or "",
        proxy=proxy,
        sessionid=args.sessionid,
        headless=not args.attach,
    ) as uploader:
        failed = uploader.upload_videos(video_dicts)

    total = len(videos)
    succeeded = total - len(failed)
    print("-------------------------")
    print(f"Uploaded {succeeded}/{total} videos successfully")
    if failed:
        print("Failed videos:")
        for v in failed:
            print(f"  - {v.get('path', 'unknown')}")
    print("-------------------------")


def parse_proxy(proxy_raw: str | None) -> ProxyDict:
    proxy: ProxyDict = {}
    if proxy_raw:
        if "@" in proxy_raw:
            proxy["user"] = proxy_raw.split("@")[0].split(":")[0]
            proxy["password"] = proxy_raw.split("@")[0].split(":")[1]
            proxy["host"] = proxy_raw.split("@")[1].split(":")[0]
            proxy["port"] = proxy_raw.split("@")[1].split(":")[1]
        else:
            proxy["host"] = proxy_raw.split(":")[0]
            proxy["port"] = proxy_raw.split(":")[1]
    return proxy
