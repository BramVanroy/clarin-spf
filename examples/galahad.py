from clarin_spf import ClarinRequester


def main():
    """Retrieve the user and corpora information from the Galahad portal."""
    base_url = "https://portal.clarin.ivdnt.org/galahad"

    clarin = ClarinRequester(trigger_url=base_url, logging_level="INFO")
    user_resp = clarin.get(f"{base_url}/api/user").json()
    corpora_resp = clarin.get(f"{base_url}/api/corpora").json()

    print(f"Available corpora for user account: {user_resp['id']}")
    for corpus in corpora_resp:
        print(f"Corpus: {corpus['name']} - Public: {corpus['public']} - sourceName: {corpus['sourceName']}")


if __name__ == "__main__":
    main()
