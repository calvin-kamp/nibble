import re


def link_token(message):
    return re.search(r"token=(\S+)", message.body).group(1)
