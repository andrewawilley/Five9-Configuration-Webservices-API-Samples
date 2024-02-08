# unittests for the domain_capture module

import unittest
# from unittest.mock import patch

from five9.utils.domain_capture import *
from five9_session import Five9Client

from private.credentials import ACCOUNTS


# run with coverage
# coverage run -m unittest discover -s tests -p "test*.py" -v
# coverage html

# instructions for how to run coverage for just this test
# coverage run -m unittest tests.testDomainCapture


class TestDomainCapture(unittest.TestCase):
    username = None
    password = None
    account = None

    def input(self, prompt):
        if prompt == "Enter Username: ":
            return self.username
        if prompt == "Enter Password: ":
            return self.password

    # initialize test variables from credentials.ACCOUNTS
    def setUp(self):
        self.username = ACCOUNTS["default_test_account"]["username"]
        self.password = ACCOUNTS["default_test_account"]["password"]
        self.account = "default_test_account"
        self.client = Five9Client(account=self.account)

    def initialize_domain_configuration(self, get_objects=False):
        # if no self.domain_configuration object exists, create one
        if not hasattr(self, "domain_configuration"):
            self.domain_configuration = Five9DomainConfig(
                client=self.client,
                # methods=["getCampaignProfiles"]
            )
            get_objects = True

        if get_objects:
            self.domain_configuration.get_domain_objects()

    def test_domain_config_capture(self):
        self.domain_configuration = Five9DomainConfig(
            client=self.client,
            # methods=["getCampaignProfiles"]
        )

        # self.assertEqual(self.domain_configuration.client, self.client)

        # assert that a folder was created matching the domain name in the
        # domain_config/domain_snapshots folder
        self.assertTrue(os.path.exists(self.domain_configuration.domain_path))

        # assert that there is a git repo in the domain_config/domain_snapshots folder
        self.assertTrue(
            os.path.exists(os.path.join(self.domain_configuration.domain_path, ".git"))
        )

    def test_domain_config_capture_campaign_profiles(self):
        # assert that a a demystified campaign profile was created for each
        # campaign in the domain with type "OUTBOUND" that also has a campaignProfile
        # with one or more crmCriteria
        self.initialize_domain_configuration()

        for campaign in self.domain_configuration.domain_objects["getCampaigns"]:
            if (
                campaign["type"] == "OUTBOUND"
                and campaign["mode"] == "ADVANCED"
                and campaign["profileName"]
                and self.domain_configuration.domain_objects[
                    "getCampaignProfiles_campaign_profile_filters"
                ][campaign["profileName"]]["grouping"]["type"]
                == "Custom"
                and len(
                    self.domain_configuration.domain_objects[
                        "getCampaignProfiles_campaign_profile_filters"
                    ][campaign["profileName"]]["crmCriteria"]
                )
                > 0
            ):
                # build path variable for the demystified campaign profile
                # and assert that it exists
                demystified_campaign_profile_path = os.path.join(
                    "domain_config",
                    "domain_snapshots",
                    f"{self.domain_configuration.domain_path}",
                    "campaign_profile_filters_demystified",
                    campaign["profileName"] + ".txt",
                )
                print(demystified_campaign_profile_path)
                self.assertTrue(os.path.exists(demystified_campaign_profile_path))
