import argparse

from five9 import five9_session

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gets the current callCountersState for the target account.  IMPORTANT: ONLY COUNTS API USAGE FOR THE SPECIFIED ACCOUNT.  DOES NOT COUNT USAGE FOR OTHER ACCOUNTS IN THE SAME FIVE9 ORG."
    )

    parser.add_argument(
        "--username",
        metavar="Five9 Username",
        type=str,
        required=False,
        help="Username for Five9 account with the admin/api role",
    )

    parser.add_argument(
        "--password",
        metavar="Five9 Password",
        type=str,
        required=False,
        help="Password for the Five9 account",
    )

    parser.add_argument(
        "--account_alias",
        metavar="Stored credential alias",
        type=str,
        required=False,
        help="Alias for a stored credential object in private/credentials.py",
    )

    parser.add_argument(
        "--verbose",
        metavar="Stored credential alias",
        type=bool,
        required=False,
        help="verbose level set true to see all the output",
    )

    args = parser.parse_args()

    client = five9_session.Five9Client(
        five9username=args.username,
        five9password=args.password,
        account=args.account_alias,
    )

    print(client.current_api_useage_formatted)
