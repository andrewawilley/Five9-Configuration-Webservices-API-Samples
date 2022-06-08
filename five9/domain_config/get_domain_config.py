import os

import git
import zeep

from ..five9 import five9_session


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
    repo = None
    vccConfig = None
    
    def __init__(self, client=None):
        self.client = client
        if self.client is not None:
            self.get_domain_objects()
    
    def getVCCConfiguration(self):
        self.vccConfig = self.client.service.getVCCConfiguration()
        print(f'Domain {self.vccConfig.domainName}')
    
    def get_or_create_repo(self):
        os.makedirs(os.path.dirname(REPO_PATH), exist_ok=True)
        repo_path = os.path.dirname(REPO_PATH)
        try:
            self.repo = git.Repo(repo_path)
        except git.exc.InvalidGitRepositoryError as e:
            print(f'Initializing bare repository in {repo_path}')
            git.Repo.init(REPO_PATH, bare=False)
            self.repo = git.Repo(repo_path)
    
    def get_domain_objects(self):
        if self.client is not None:
            try:
                self.getVCCConfiguration()
                self.get_or_create_repo()
                branch = self.repo.create_head(self.vccConfig.domainName)
                self.repo.checkout(branch)
                print("Obtaining Domain Objects")
                for method in dir(client.service):
                    if method in METHODS:
                        print(f'\t{method}')
                        vcc_method = getattr(client.service, method)
                        if method in METHOD_DEFAULT_ARGS.keys():
                            r = vcc_method(METHOD_DEFAULT_ARGS[method])
                        else:
                            try:
                                r = vcc_method()
                            except zeep.exceptions.Fault as e:
                                print(e)
                        self.domain_objects[method[3:]] = zeep.helpers.serialize_object(r, dict)
                        
            except zeep.exceptions.Fault as e:
                print(e)
        else:
            print('No active client object available to connect with Five9 VCC')

d = Five9Domain(client)
