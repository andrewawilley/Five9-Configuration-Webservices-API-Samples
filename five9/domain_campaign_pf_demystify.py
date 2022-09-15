import argparse

from domain_config import domain_capture

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="demystifies campaign profile filter expressions"
    )

    parser.add_argument(
        '--username',
        metavar='Five9 Username',
        type=str,
        required=False,
        help='Username for Five9 account with the admin/api role')
    
    parser.add_argument(
        '--password',
        metavar='Five9 Password',
        type=str,
        required=False,
        help='Password for the Five9 account')

    parser.add_argument(
        '--account_alias',
        metavar='Stored credential alias',
        type=str,
        required=False,
        help='Alias for a stored credential object in private/credentials.py')

    args = parser.parse_args()

    domain = domain_capture.Five9DomainConfig(username=args.username, password=args.password, account=args.account_alias, methods=["getCampaignProfiles"])
    domain.demystify_campaign_profile_filters(
        # verbose=True
    )
