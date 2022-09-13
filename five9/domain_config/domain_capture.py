import json
import os
import time
import shutil

import git
import zeep

import five9_session

API_SLEEP_INTERVAL  = .3

REPO_PATH = "domain_config\\domain_snapshots\\"

METHOD_DEFAULT_ARGS = {
    "getAgentGroups": ".*",
}

# Order of aquisition matters for purpose of syncing
METHODS = [
    'getAvailableLocales',
    'getDialingRules',
    'getSkills',
    'getPrompts',
    'getDispositions',
    'getWebConnectors',
    'getCallVariableGroups',
    'getCallVariables',
    'getContactFields',

    'getAgentGroups',
    'getCampaignProfiles',
    'getCampaigns',
    
    'getIVRScripts',
    'getSpeedDialNumbers',
    'getUserProfiles',
]


class Five9DomainConfig:


    def __init__(self, client=None, username=None, password=None, account=None, sync_target_domain=None):
        self.client = None
        self.domain_objects = {}
        self.domain_path = f'{REPO_PATH}'
        self.repo = None
        self.repo_path = None
        self.vccConfig = None

        self.sync_target_domain = sync_target_domain

        if client is None:
            self.client = five9_session.get_client(five9username=username, five9password=password, account=account)
        else:
            self.client = client

        if self.client is not None:
            self.get_domain_objects()
    
    def sync_to_target_domain(self, sync_objects=[]):
        '''Method to run the domain object sync methods that are implemented.  If no sync_objects are provided, will run all sync methods'''


        self.sync_methods = {
            "campaignProfiles": self.sync_campaignProfiles,

        }

        if self.sync_target_domain is not None:
            if len(sync_objects) == 0:
                sync_objects = self.sync_methods.keys()
            for sync_object in sync_objects:
                sync_method = self.sync_methods[sync_object]
                print(f'SYNC - {sync_object}')
                sync_method()

    def getVCCConfiguration(self):
        self.vccConfig = self.client.service.getVCCConfiguration()
        self.domain_path = f'{REPO_PATH}\\{self.vccConfig.domainName}\\'
        print(f'\nAcquiring configuration for domain:\n{self.vccConfig.domainName}\n')
        try:
            shutil.rmtree(os.path.dirname(f'{self.domain_path}'), )
        except:
            pass
        os.makedirs(os.path.dirname(f'{self.domain_path}'), exist_ok=True)
    
    def get_or_create_repo(self):
        os.makedirs(os.path.dirname(REPO_PATH), exist_ok=True)
        self.repo_path = os.path.dirname(REPO_PATH)
        # try:
        #     self.repo = git.Repo(self.repo_path)
        # except git.exc.InvalidGitRepositoryError as e:
        #     print(f'Initializing bare repository in {self.repo_path}')
        #     git.Repo.init(REPO_PATH, bare=False)
        #     self.repo = git.Repo(self.repo_path)
    
    def write_json_to_target_path(self, target_path, domain_object, sort_keys=True, indent=4):
        jsonString = json.dumps(domain_object, sort_keys=sort_keys, indent=indent)
        # try:
        jsonFile = open(f'{target_path}.json', 'w')
        jsonFile.write(jsonString)
        jsonFile.close()
        return True
        # except: 
        #     return False

    def get_config_object_detail(self, parent_method_name, subfolder_name, method_response=None, vcc_method=None):
        subfolder_path = f'{self.domain_path}\\{subfolder_name}\\'
        os.makedirs(os.path.dirname(subfolder_path), exist_ok=True)
        print(f'\n\t{parent_method_name} - {subfolder_name}')
        self.domain_objects[f'{parent_method_name}_{subfolder_name}'] = {}
        
        for domain_object in method_response:
            object_name = domain_object.name
            print(f'\t\t{object_name}')
            if vcc_method is not None:
                sub_method = getattr(self.client.service, vcc_method)
                domain_object = sub_method(object_name)
                # print(domain_object)
            self.domain_objects[f'{parent_method_name}_{subfolder_name}'][object_name] = zeep.helpers.serialize_object(domain_object, dict)
            target_path = f'{subfolder_path}\\{object_name}'
            self.write_json_to_target_path(target_path, self.domain_objects[f'{parent_method_name}_{subfolder_name}'][object_name])

    def get_domain_objects(self, methods=METHODS):
        if self.client is not None:
            try:
                self.getVCCConfiguration()
                self.get_or_create_repo()
                # branch = self.repo.create_head(self.vccConfig.domainName)
                # self.repo.checkout(branch)
                print("Processing Domain Object Methods")
                for method in dir(self.client.service):
                    if method in methods:
                        print(f'\t{method}')
                        vcc_method = getattr(self.client.service, method)
                        
                        try:
                            if method in METHOD_DEFAULT_ARGS.keys():
                                    method_response = vcc_method(METHOD_DEFAULT_ARGS[method])
                            else:
                                method_response = vcc_method()
                            
                            if method == 'getIVRScripts':
                                self.get_config_object_detail(method, 'ivrs', method_response)

                            elif method == 'getCampaigns':
                                self.domain_objects[method] = zeep.helpers.serialize_object(method_response, dict)
                                self.write_json_to_target_path(f'{self.domain_path}{method}', self.domain_objects[method])
                                method_response = vcc_method(campaignType='OUTBOUND')
                                self.get_config_object_detail(method, 'campaigns_outbound', method_response, 'getOutboundCampaign')
                                method_response = vcc_method(campaignType='INBOUND')
                                self.get_config_object_detail(method, 'campaigns_inbound', method_response, 'getInboundCampaign')
                            
                            elif method == 'getCampaignProfiles':
                                self.domain_objects[method] = zeep.helpers.serialize_object(method_response, dict)
                                self.write_json_to_target_path(f'{self.domain_path}{method}', self.domain_objects[method])
                                self.get_config_object_detail(method, 'campaign_profile_filters', method_response, 'getCampaignProfileFilter')
                                self.get_config_object_detail(method, 'campaign_profile_dispositions', method_response, 'getCampaignProfileDispositions')

                            elif method == 'getSkills':
                                self.domain_objects[method] = zeep.helpers.serialize_object(method_response, dict)
                                self.write_json_to_target_path(f'{self.domain_path}{method}', self.domain_objects[method])
                                self.get_config_object_detail(method, 'skills_info', method_response, 'getSkillsInfo')

                            else:
                                self.domain_objects[method] = zeep.helpers.serialize_object(method_response, dict)
                                self.write_json_to_target_path(f'{self.domain_path}{method}', self.domain_objects[method])

                        except zeep.exceptions.Fault as e:
                            print(e)

            except zeep.exceptions.Fault as e:
                print(e)
        else:
            print('No active client object available to connect with Five9 VCC')
    
    def sync_campaignProfiles(self):
        for profile in self.domain_objects['getCampaignProfiles']:
            description = profile['description'] or ''
            if description.find('sync') > -1:
                try:
                    self.sync_target_domain.client.service.createCampaignProfile(profile)
                    print(f'\t\t\tSYNC (create): {profile["name"]}')
                except:
                    self.sync_target_domain.client.service.modifyCampaignProfile(profile)
                    print(f'\t\t\tSYNC (update): {profile["name"]}')

                    # Remove filters/grouping from the target domain before adding in conditions and grouping from this domain
                    self.sync_target_domain.client.service.modifyCampaignProfileCrmCriteria(
                        profileName=profile["name"],
                        grouping={
                            "expression": None,
                            "type": "All"
                        },
                        removeCriteria=self.sync_target_domain.domain_objects['getCampaignProfiles_campaign_profile_filters'][profile["name"]]["crmCriteria"]
                    )
                    if len(self.sync_target_domain.domain_objects['getCampaignProfiles_campaign_profile_filters'][profile["name"]]["orderByFields"]) > 0:
                        remove_fields = self.sync_target_domain.domain_objects['getCampaignProfiles_campaign_profile_filters'][profile["name"]]["orderByFields"]
                        
                        self.sync_target_domain.client.service.modifyCampaignProfileFilterOrder(
                            campaignProfile=profile["name"],
                            removeOrderByField=[field['fieldName'] for field in remove_fields]
                        )
                    
                self.sync_target_domain.client.service.modifyCampaignProfileCrmCriteria(
                    profileName=profile["name"],
                    grouping=self.domain_objects['getCampaignProfiles_campaign_profile_filters'][profile["name"]]["grouping"],
                    addCriteria=self.domain_objects['getCampaignProfiles_campaign_profile_filters'][profile["name"]]["crmCriteria"]
                )
                if len(self.domain_objects['getCampaignProfiles_campaign_profile_filters'][profile["name"]]["orderByFields"]) > 0:
                    self.sync_target_domain.client.service.modifyCampaignProfileFilterOrder(
                        campaignProfile=profile["name"],
                        addOrderByField=self.domain_objects['getCampaignProfiles_campaign_profile_filters'][profile["name"]]["orderByFields"]
                    )

    def sync_ivrScripts(self):
        pass
        # for profile in self.domain_objects['getCampaignProfiles']:
