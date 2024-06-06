import argparse
import xml.etree.ElementTree as ET
import json
import csv

from getpass import getpass

from five9 import five9_session
import os

# Function to extract skill transfer modules and their skills
def extract_skill_transfers(xml_root):
    skill_transfers = []
    
    for skill_transfer in xml_root.findall('.//skillTransfer'):
        module_name_elem = skill_transfer.find('moduleName')
        module_name = module_name_elem.text if module_name_elem is not None else "Unnamed Module"
        
        skills = []
        for extrnal_obj in skill_transfer.findall('.//extrnalObj'):
            skill_name_elem = extrnal_obj.find('name')
            if skill_name_elem is not None:
                skills.append({'name': skill_name_elem.text, 'type': 'skill'})
                
        # Handle variable-selected skills
        for skill_var in skill_transfer.findall('.//listOfSkillsEx'):
            var_selected_elem = skill_var.find('varSelected')
            if var_selected_elem is not None and var_selected_elem.text == 'true':
                variable_name_elem = skill_var.find('variableName')
                if variable_name_elem is not None:
                    skills.append({'name': variable_name_elem.text, 'type': 'variable'})
        
        skill_transfers.append({'moduleName': module_name, 'skills': skills})
    
    return skill_transfers

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract skill transfer modules from a Five9 XML response')
    
    parser.add_argument('--output', type=str, default='private/ivr_skill_transfer_modules.csv', help='Output CSV file name')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--username', type=str, required=True, help='Five9 username')
    parser.add_argument('--password', type=str, required=False, default=None, help='Five9 password')

    args = parser.parse_args()

    password = args.password

    if password is None:
        password = getpass()

    output_file = args.output

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    client = five9_session.Five9Client(five9username=args.username, five9password=password)

    # Get the IVR script definitions
    ivrs = client.service.getIVRScripts()

    ivr_skill_usage = []

    with open(output_file, mode='w', newline='') as csv_file:
        fieldnames = ['IVR Script', 'Skill Transfer Module Name', 'Skill Target', 'Target Type', 'Skill Target Order']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for ivr in ivrs:
            # Extract and print skill transfer modules
            root = ET.fromstring(ivr.xmlDefinition)
            skill_transfer_modules = extract_skill_transfers(root)
            
            # Skip if skill_transfer_modules list is empty or if the IVR name starts with "EXAMPLES..Five9.."
            if len(skill_transfer_modules) == 0 or ivr.name.startswith("EXAMPLES..Five9.."):
                continue
            
            ivr_skill_usage.append({'ivr': ivr.name, 'skill_transfer_modules': skill_transfer_modules})

            for module in skill_transfer_modules:
                skill_target_order = 1
                for skill in module['skills']:
                    writer.writerow({
                        'IVR Script': ivr.name,
                        'Skill Transfer Module Name': module['moduleName'],
                        'Skill Target': skill['name'],
                        'Target Type': skill['type'],
                        'Skill Target Order': skill_target_order
                    })
                    skill_target_order += 1
    
    if args.verbose:
        print(json.dumps(ivr_skill_usage, indent=2))
