import os
import json

from zeep import helpers

from five9 import five9_session


client = five9_session.get_client()

REPO_PATH = "domain_config\\domain_git\\"

METHOD_DEFAULT_ARGS = {
    "getAgentGroups": ".*",
}

METHODS = [
    'getAgentGroups',
    'getAvailableLocales',
    'getCallVariableGroups',
    'getCallVariables',
    'getCampaigns',
    'getContactFields',
    'getDialingRules',
    'getDispositions',
    'getIVRScripts',
    'getPrompts',
    'getSkills',
    'getSpeedDialNumbers',
    'getUserProfiles',
    'getWebConnectors',
]


class Five9Domain:
    client = None
    domain_objects = {}
    
    
    def __init__(self, client=None):
        self.client = client

        if self.client is not None:
            self.get_domain_objects()
    
    def get_domain_objects(self):
        if self.client is not None:
            vccConfig = self.client.service.getVCCConfiguration

            os.makedirs(os.path.dirname(REPO_PATH), exist_ok=True)
                        
            
            print("Obtaining Domain Objects")
            for method in dir(client.service):
                if method in METHODS:
                    print(method)
                    vcc_method = getattr(client.service, method)
                    if method in METHOD_DEFAULT_ARGS.keys():
                        r = vcc_method(METHOD_DEFAULT_ARGS[method])
                    else:
                        r = vcc_method()
                    self.domain_objects[method[3:]] = helpers.serialize_object(r, dict)

d = Five9Domain(client)
