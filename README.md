# Quickstart

The purpose of this repository is to provide individually functional scripts to demonstrate how to use Five9 Configuration Webservices API methods in Python.

# Breakfix Note
On July 11, 2023 a schema validation resource located at ws-i.org was no longer available which caused schema validations for API calls to fail.  This has been temporarily mitigated by using a local copy of the WSDL file which no longer references ws-i.org

This is likely a temporary fix and will be replaced with a more permanent solution in the near future.  Please check back for updates.

### Obtain the repository

It is highly recommended that you install [git](https://git-scm.com/download/win) so that you can update to the latest version of this repository as needed.  Once installed, from the command line you can clone this repository with

    git clone https://github.com/andrewawilley/Five9-Configuration-Webservices-API-Samples.git

You can also just download a [zip archive](https://github.com/andrewawilley/Five9-Configuration-Webservices-API-Samples/archive/refs/heads/main.zip) of the repository and extract

from the shell, navigate to the local copy (change to the directory that the repository is located) and then ...

#### Windows Users
    mkdir venvs
    cd venvs
    py.exe -m venv five9
    cd ..
    .\venvs\five9\Scripts\activate

#### Mac/Linux Users
    mkdir venvs
    cd venvs
    python3 -m venv five9
    cd ..
    source venvs/five9/bin/activate

### finishing up
    pip install -r requirements.txt
    py.exe bootstrap.py

The bootstrap.py script will create a private folder that can contain a credentials.py file where you can keep reusable Five9 admin API user credentials in a slightly more secure way than right in the script.  The private folder is excluded from Git.  

The credentials object in private.credentials looks like this:

    ACCOUNTS = {
        'default_account': {
            'username': 'apiUserName',
            'password': 'superSecretPassword'
        }
    }

If you run a script without this accounts object, you'll be prompted to enter username and password in the console. 

# Creating and using a shell session
After activating the virtual evnironment and starting a python shell, an authenticated client can be obtained using the included five9_session.py

import five9_session
client = five9_session.Five9Client()

This creates an authenticated client object that can invoke any of the API endpoints.  For example:

    call_variables = client.service.getCallVariables()

The most recent SOAP envelope content can be viewed with 

    print(client.latest_envelopes)

To print all of the client methods available from the service definition file
    
    client.print_available_service_methods()

The available methods as of v12 are:

    addDNISToCampaign
    addDispositionsToCampaign
    addListsToCampaign
    addNumbersToDnc
    addPromptTTS
    addPromptWav
    addPromptWavInline
    addRecordToList
    addRecordToListSimple
    addSkillAudioFile
    addSkillsToCampaign
    addToList
    addToListCsv
    addToListFtp
    asyncAddRecordsToList
    asyncDeleteRecordsFromList
    asyncUpdateCampaignDispositions
    asyncUpdateCrmRecords
    checkDncForNumbers
    closeSession
    createAgentGroup
    createAutodialCampaign
    createCallVariable
    createCallVariablesGroup
    createCampaignProfile
    createContactField
    createDisposition
    createIVRScript
    createInboundCampaign
    createList
    createOutboundCampaign
    createReasonCode
    createSkill
    createSpeedDialNumber
    createUser
    createUserProfile
    createWebConnector
    deleteAgentGroup
    deleteAllFromList
    deleteCallVariable
    deleteCallVariablesGroup
    deleteCampaign
    deleteCampaignProfile
    deleteContactField
    deleteFromContacts
    deleteFromContactsCsv
    deleteFromContactsFtp
    deleteFromList
    deleteFromListCsv
    deleteFromListFtp
    deleteIVRScript
    deleteLanguagePrompt
    deleteList
    deletePrompt
    deleteReasonCode
    deleteReasonCodeByType
    deleteRecordFromList
    deleteSkill
    deleteUser
    deleteUserProfile
    deleteWebConnector
    forceStopCampaign
    getAgentGroup
    getAgentGroups
    getApiVersions
    getAutodialCampaign
    getAvailableLocales
    getCallCountersState
    getCallVariableGroups
    getCallVariables
    getCampaignDNISList
    getCampaignProfileDispositions
    getCampaignProfileFilter
    getCampaignProfiles
    getCampaignState
    getCampaignStrategies
    getCampaigns
    getConfigurationTranslations
    getContactFields
    getContactRecords
    getCrmImportResult
    getDNISList
    getDialingRules
    getDisposition
    getDispositions
    getDispositionsImportResult
    getIVRScripts
    getInboundCampaign
    getIvrIcons
    getIvrScriptOwnership
    getListImportResult
    getListsForCampaign
    getListsInfo
    getLocale
    getOutboundCampaign
    getPrompt
    getPrompts
    getReasonCode
    getReasonCodeByType
    getReportResult
    getReportResultCsv
    getSkill
    getSkillAudioFiles
    getSkillInfo
    getSkillVoicemailGreeting
    getSkills
    getSkillsInfo
    getSpeedDialNumbers
    getUserGeneralInfo
    getUserInfo
    getUserProfile
    getUserProfiles
    getUserVoicemailGreeting
    getUsersGeneralInfo
    getUsersInfo
    getVCCConfiguration
    getWebConnectors
    isImportRunning
    isReportRunning
    modifyAgentGroup
    modifyAutodialCampaign
    modifyCallVariable
    modifyCallVariablesGroup
    modifyCampaignLists
    modifyCampaignProfile
    modifyCampaignProfileCrmCriteria
    modifyCampaignProfileDispositions
    modifyCampaignProfileFilterOrder
    modifyContactField
    modifyDisposition
    modifyIVRScript
    modifyInboundCampaign
    modifyOutboundCampaign
    modifyPromptTTS
    modifyPromptWav
    modifyPromptWavInline
    modifyReasonCode
    modifySkill
    modifyUser
    modifyUserCannedReports
    modifyUserProfile
    modifyUserProfileSkills
    modifyUserProfileUserList
    modifyVCCConfiguration
    modifyWebConnector
    removeDNISFromCampaign
    removeDisposition
    removeDispositionsFromCampaign
    removeIvrIcons
    removeIvrScriptOwnership
    removeListsFromCampaign
    removeNumbersFromDnc
    removeSkillAudioFile
    removeSkillsFromCampaign
    removeSpeedDialNumber
    renameCampaign
    renameDisposition
    resetCampaign
    resetCampaignDispositions
    resetListPosition
    runReport
    setCampaignStrategies
    setDefaultIVRSchedule
    setDialingRules
    setIvrIcons
    setIvrScriptOwnership
    setLocale
    setSkillVoicemailGreeting
    setUserVoicemailGreeting
    startCampaign
    stopCampaign
    updateConfigurationTranslations
    updateContacts
    updateContactsCsv
    updateContactsFtp
    updateCrmRecord
    updateDispositions
    updateDispositionsCsv
    updateDispositionsFtp
    userSkillAdd
    userSkillModify
    userSkillRemove

 # DISCLAIMER:
 This sample code is provided for illustrative purposes and should not be treated as officially supported software by Five9. By using this code, you understand that any customization, modification, or deployment is solely your responsibility if you  choose not to engage with Five9's professional services team.
 
 While these examples demonstrate how ADT+ customizations can be built, it is recommended that you consult with Five9 professional  services team for a fully supported and tailored solution to meet your specific needs.
