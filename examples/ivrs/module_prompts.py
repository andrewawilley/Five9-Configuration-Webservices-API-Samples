from five9 import five9_session

import os
import pickle

import csv
import base64
import gzip
import io
import xmltodict
import json

import logging
logging.basicConfig(level=logging.INFO)

def is_base64_encoded(data):
    if not isinstance(data, str):
        return False
    try:
        if base64.b64encode(base64.b64decode(data)).decode('utf-8') == data:
            return True
    except Exception:
        return False
    return False

def decompress_data(encoded_value):
    try:
        decoded_bytes = base64.b64decode(encoded_value)
        with gzip.GzipFile(fileobj=io.BytesIO(decoded_bytes)) as f:
            decompressed_data = f.read()
        return decompressed_data.decode('utf-8')
    except Exception as e:
        # print(f"Decompression failed: {e}")
        return None


def recursively_decompress(data):
    if isinstance(data, dict):
        return {k: recursively_decompress(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [recursively_decompress(item) for item in data]
    elif isinstance(data, str) and is_base64_encoded(data):
        decompressed = decompress_data(data)
        if decompressed:
            try:
                # Try to parse as JSON or XML if it's decompressed text
                return json.loads(decompressed)
            except json.JSONDecodeError:
                try:
                    return xmltodict.parse(decompressed)
                except:
                    return decompressed
        else:
            return data
    else:
        return data

def process_ivr_script(data):
    if "xmlDefinition" in data:
        xml_definition = data["xmlDefinition"].replace("\n", "").replace("\r", "")  
        ivr_script_dict = xmltodict.parse(xml_definition)
        data["jsonDefinition"] = recursively_decompress(ivr_script_dict)
        del data["xmlDefinition"]
    return data

def process_multilingual_prompts(prompt):
    return

def process_module_type(module_type, module):

    prompt_data = module.get("data", {})
    if prompt_data:
        
        return_prompts = []
        return_recoEvents = []


        if module_type in ["input", "menu"]:
            prompts = prompt_data.get("prompts", {}).get("prompt", {})
        else:
            prompts = prompt_data.get("prompt", {})

        filePrompts = prompts.get("filePrompt", [])
        if isinstance(filePrompts, dict):
            filePrompts = [filePrompts]
        for filePrompt in filePrompts:
            prompt_name = filePrompt["promptData"]["prompt"]["name"]
            prompt_id = filePrompt["promptData"]["prompt"]["id"]

            return_prompts.append({
                "prompt_name": prompt_name,
                "prompt_id": prompt_id
            })

        # check if ttsPrompt is a dict or a list
        ttsPrompts = prompts.get("ttsPrompt", [])
        if isinstance(ttsPrompts, dict):
            ttsPrompts = [ttsPrompts]
        for ttsPrompt in ttsPrompts:
            prompt_tts_complete = ""
            try:
                prompt_tts_language = ttsPrompt["xml"]["speakElement"]["attributes"]["langAttr"].get("attributeValueBase", {}).get("@value", {})
            except Exception as e:
                logging.error(e)
                logging.error(f"Error getting prompt_tts_language: {ttsPrompt}")
                # prettyprint the ttsPrompt for debugging
                logging.error(json.dumps(ttsPrompt, indent=4))
            
            # check if prompt_tts_items is a dict or a list
            prompt_tts_items = ttsPrompt["xml"]["speakElement"]["items"].get("sayAsElement", {})
            if isinstance(prompt_tts_items, dict):
                prompt_tts_items = [prompt_tts_items]

            for prompt_tts_item in prompt_tts_items:
                prompt_tts = prompt_tts_item.get("items", None)
                if not prompt_tts:
                    continue
                # check if prompt_tts is a dict or a list
                if isinstance(prompt_tts, dict):
                    prompt_tts = [prompt_tts]
                for prompt_tts_item in prompt_tts:
                    prompt_tts_item_body = prompt_tts_item["textElement"]["body"]
                    # ["textElement"]["body"]
                    prompt_tts_complete += prompt_tts_item_body
            return_prompts.append({
                "prompt_tts": prompt_tts_complete,
                "prompt_tts_languageCode": prompt_tts_language
            })

        announcements = prompt_data.get("announcements", [])        
        for announcement in announcements:
            if announcement["prompt"]:
                return_prompts.append({
                    "prompt_name": announcement["prompt"]["name"],
                    "prompt_id": announcement["prompt"]["id"]
                })    
        
        # additional processing for menu modules
        # if module_type == "menu":
        #     prompt_locations = ["recoEvents", "confirmData", ""]
        #     recoEvents = prompt_data.get("recoEvents", [])
        #     for recoEvent in recoEvents:
        #         prompts = recoEvent.get("prompts", [])
        #         if recoEvent["prompt"]:
        #             return_prompts.append({
        #                 "prompt_name": recoEvent["prompt"]["name"],
        #                 "prompt_id": recoEvent["prompt"]["id"]
        #             })
        
        return return_prompts

    return []



client = five9_session.Five9Client()


# Fetch IVR scripts data from the API
ivr_scripts = client.service.getIVRScripts()


summary = []
for ivr_script in ivr_scripts:
    # Process the IVR script
    processed_data = process_ivr_script(ivr_script)
    logging.info(f"Processing IVR script: {processed_data["name"]}")
    
    i = 0
    for module_type_name, module_type_instance in processed_data["jsonDefinition"]["ivrScript"]["modules"].items():
        # get the key name for the module type at this point of the iteration
        
        # check if the module type value is a dict or a list
        if isinstance(processed_data["jsonDefinition"]["ivrScript"]["modules"][module_type_name], dict):
            module_type_instance = [module_type_instance]

        for module in module_type_instance:
            module_prompts = process_module_type(module_type_name, module)
            # if len(module_prompts) == 0:
            #     continue
            module_prompt_summary = {
                "domainID": processed_data["jsonDefinition"]["ivrScript"]["domainId"],
                "ivr_script_name": processed_data["name"],
                "module_type": module_type_name,
                "module_name": module["moduleName"],
                "prompts": module_prompts
            }
            summary.append(module_prompt_summary)

# logging.info(summary)
for item in summary:
    print(item)

subfolder = f'private/{client.domain_name}/prompt_module_exports'
if not os.path.exists(subfolder):
    os.makedirs(subfolder)

with open(f'{subfolder}/output.txt', 'w', newline='') as file:
    writer = csv.writer(file, delimiter='|')
    # Write the header
    writer.writerow(['domainID', 'ivr_script_name', 'module_type', 'module_name', 'prompt_name', 'prompt_id', 'prompt_tts', 'prompt_tts_languageCode'])
    
    for entry in summary:
        for prompt in entry.get('prompts', [{}]):
            row = [
                entry['domainID'],
                entry['ivr_script_name'],
                entry['module_type'],
                entry['module_name'],
                prompt.get('prompt_name', ''),
                prompt.get('prompt_id', ''),
                prompt.get('prompt_tts', ''),
                prompt.get('prompt_tts_languageCode', '')
            ]
            writer.writerow(row)