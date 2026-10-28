"""Gunicorn access log without query strings.

Search terms of the food and recipe search travel in the query string, of the API
request itself and of the page in the Referer. Neither reaches the log: the request
line keeps only the path and the Referer loses everything after it. The remaining
fields (IP, time, status, size, user agent) are the ones the privacy policy lists.
"""

from urllib.parse import urlsplit, urlunsplit

from gunicorn.glogging import Logger


def without_query(url):
    if not url or url == "-":
        return url

    parts = urlsplit(url)

    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


class AccessLogger(Logger):
    def atoms(self, resp, req, environ, request_time):
        atoms = super().atoms(resp, req, environ, request_time)
        referer = without_query(atoms["f"])

        atoms["r"] = f"{atoms['m']} {atoms['U']} {atoms['H']}"
        atoms["q"] = ""
        atoms["f"] = referer
        atoms["{referer}i"] = referer

        return atoms
