import requests

from clarin_spf import clarin_login


def main():
    cookies = clarin_login("https://portal.clarin.ivdnt.org/galahad/home")
    response = requests.get("https://portal.clarin.ivdnt.org/galahad/api/corpora", cookies=cookies)
    print(response.json())


if __name__ == "__main__":
    main()
