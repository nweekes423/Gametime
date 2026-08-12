import sys
from http.client import responses

import requests
import validators


def usage():
    print(
        "\nUsage:\n"
        "Single URL: urlcheck <url>\n"
        "Multiple URLs: urlcheck <url1> <url2> ...... <urln>\n"
    )


def main():
    if len(sys.argv) < 2:
        print("You need to specify at least one URL")
        return

    if "help" in sys.argv:
        usage()
        return

    print("\n")

    for url in sys.argv[1:]:
        if validators.url(url):
            try:
                response = requests.head(url, timeout=10)
                status = response.status_code
            except requests.RequestException as exc:
                print(url, f"Request failed: {exc}\n")
                continue

            try:
                print(url, status, responses[status], "\n")
            except KeyError:
                print(url, status, "Not a Standard HTTP Response code\n")
        else:
            print(url, "Not a valid URL\n")


if __name__ == "__main__":
    main()
