#!/usr/bin/env python3
"Mastodon Streaming Client."
from typing import (Optional, Set)
import argparse
import logging
import os
import shutil
import sys


from mod import (parser, readconf)
from mod.deftypes import (TOOT, NOTIFICATION)
from mod.filtering import (MatchFilter, Highlight, ignore, gen_word_set)
from mod.stdfunc import exc_msg
from mod.streaming import (MstdnStreamListener, MstdnStream)


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
STYLE_NAME = "{display} ({account})"
STYLE_CW = "＃＃＃＃ {spoiler} ＃＃＃＃"
STYLE_BODY = """{content}
{tootcount} / {following} / {followers}
via {application}"""
CONFIG_FILE = os.path.join("config", "config.ini")


def main() -> None:
    """Main.

    """
    args = parse_arguments()
    if args.verbose:
        LOGGER.setLevel(logging.DEBUG)

    conf = readconf.read_conf(CONFIG_FILE)
    contentmute = conf["FILE"]["ContentFilter"]
    accountmute = conf["FILE"]["AccountFilter"]
    clientmute = conf["FILE"]["ClientFilter"]
    highlightwords = conf["FILE"]["HighlightWords"]

    if args.use_filter:
        LOGGER.debug("Use filter")
        contentfilter = MatchFilter(gen_word_set(contentmute))
        clientfilter = MatchFilter(gen_word_set(clientmute))
        try:
            with open(accountmute, "r") as fopen:
                accountfilter = {ln.strip() for ln in fopen if not ignore(ln)}
        except FileNotFoundError:
            LOGGER.error(exc_msg(accountmute))
            accountfilter = set()
        except IOError:
            LOGGER.error(exc_msg(accountmute))
            accountfilter = set()
    else:
        contentfilter = None
        accountfilter = None
        clientfilter = None

    listener = FilterListener(
        contentfilter=contentfilter,
        accountfilter=accountfilter,
        clientfilter=clientfilter)

    if args.highlight:
        LOGGER.debug("Use highlight")
        highlight = Highlight(gen_word_set(highlightwords))
        listener.set_highlight(highlight)

    stream = MstdnStream(
        conf["NETWORK"]["MstdnHost"],
        conf["AUTHENTICATION"]["BearerToken"],
        listener)

    timeline = args.timeline[0]
    if timeline == "home":
        stream.home()
    elif timeline == "local":
        stream.local()
    elif timeline == "public":
        stream.public()
    else:
        LOGGER.error("[ERR] %s", timeline)
        return


def parse_arguments() -> argparse.Namespace:
    """
    ArgumentParser.
    """
    argparser = argparse.ArgumentParser(
        description=__doc__,
        add_help=True)

    argparser.add_argument(
        "timeline",
        help="timeline to stream",
        type=str.lower,
        nargs=1,
        default="local",
        metavar="home/local/public")
    argparser.add_argument(
        "-f", "--use-filter",
        help="use mute filter",
        action="store_true")
    argparser.add_argument(
        "-v", "--verbose",
        help="show debugging messages",
        action="store_true")
    argparser.add_argument(
        "--highlight",
        help="highlight words",
        action="store_true")
    return argparser.parse_args()


def color_text(text: str, color: str) -> str:
    """Decolate texr.
    """
    color = color.lower()
    colordict = {
        "red": "31",
        "darkgreen": "32",
        "darkpurple": "35",
        "orange": "91",
        "green": "92",
        "yellow": "93",
        "blue": "94",
        "purple": "95",
        "sky": "96"
    }
    if color not in colordict.keys():
        return text

    return "\033[{0}m{1}\033[0m".format(
        colordict[color],
        text)


class FilterListener(MstdnStreamListener):
    """
    Mute filtering class.
    """
    def __init__(self, *,
                 contentfilter: MatchFilter=None,
                 accountfilter: Set[str]=None,
                 clientfilter: MatchFilter=None) -> None:
        super(FilterListener, self).__init__()
        self.clientfilter = clientfilter
        self.accountfilter = accountfilter
        self.contentfilter = contentfilter
        self.highlight = None  # type: Optional[Highlight]

    def on_update(self, toot: TOOT) -> None:
        showdata = ""

        account = toot["account"]
        namedict = parser.parse_name(toot)
        content = self.parser.parse_content(toot)
        if toot["application"]:
            application = toot["application"]["name"]
        else:
            application = ""
        if toot["spoiler_text"]:
            spoiler = toot["spoiler_text"]
        else:
            spoiler = None

        if self.should_mute(application,
                            namedict["account"],
                            content,
                            spoiler):
            return

        showdata += STYLE_NAME.format(
            display=color_text(namedict["display"], "sky"),
            account=namedict["account"])
        showdata += os.linesep

        # Warnings
        if toot["sensitive"]:
            showdata += "＊＊＊＊＊＊ NSFW ＊＊＊＊＊＊"
            showdata += os.linesep
        if spoiler:
            showdata += STYLE_CW.format(
                spoiler=color_text(toot["spoiler_text"],
                                   "darkpurple"))
            showdata += os.linesep

        if self.highlight:
            content = self.highlight.highlight_word(content)
            if spoiler:
                spoiler = self.highlight.highlight_word(spoiler)

        showdata += STYLE_BODY.format(
            content=content,
            tootcount=str(account["statuses_count"]),
            following=str(account["following_count"]),
            followers=str(account["followers_count"]),
            application=application)

        for media in toot["media_attachments"]:
            if media["description"]:
                pass
            if media["text_url"]:
                pass
            showdata += os.linesep
            showdata += "media: {} ".format(media["url"])

        print(showdata)
        print("\033[{0}m{1}\033[0m".format(
            "2",
            "=" * shutil.get_terminal_size()[0]))

    def on_notification(self, notification: NOTIFICATION) -> None:
        print(notification)

    def on_delete(self, data: str) -> None:
        LOGGER.debug("Deleted: %s", data)

    def set_highlight(self, highlight: Optional[Highlight]) -> None:
        """
        Set highlightword filter.
        """
        self.highlight = highlight

    def should_mute(self,
                    application: str,
                    account: str,
                    content: str,
                    spoiler: str=None) -> bool:
        """If should mute.
        """
        # Client mute
        if self.clientfilter:
            if self.clientfilter.is_match(application):
                LOGGER.debug("Muted: %s", application)
                return True
        # Account mute
        if self.accountfilter:
            if account in self.accountfilter:
                LOGGER.debug("Muted: %s", account)
                return True
        # Content mute
        if self.contentfilter:
            if self.contentfilter.is_match(content):
                LOGGER.debug("Muted: %s", "by content")
                return True
            # If has spoiler text, check matching.
            if not spoiler:
                pass
            elif self.contentfilter.is_match(spoiler):
                LOGGER.debug("Muted: %s", "by spoiler")
                return True
        return False


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Quit")
