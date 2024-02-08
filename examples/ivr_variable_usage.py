import collections
import json
import re

def ivr_variable_usage(ivrs, verbose=False):
    """
    Analyzes a list of IVR (Interactive Voice Response) objects to identify the usage of script variables within them.

    Args:
    ivrs (list): A list of IVR objects (should be obtained from the getIvrScripts method).
    verbose (bool): If True, the function prints the dictionary of variables and their corresponding IVRs in JSON format. Defaults to False.

    The function scans through the 'xmlDefinition' of each IVR object looking for script variables. It ignores any IVR objects with "EXAMPLE" in their name. Each variable is then cataloged along with the IVR names where it appears.

    Returns:
    OrderedDict: A dictionary where keys are script variable names and values are lists of IVR names where these variables are used. The dictionary is sorted alphabetically by the variable names.
    """

    # Initialize an empty dictionary to store the script variables and the IVRs where they appear
    ivr_variables = {}

    # Compile a regular expression to find script variables in the xmlDefinition attribute
    script_variable_pattern = re.compile(
        r"(?<=<variableName>)(.*?)(?=<\/variableName>)"
    )

    # Iterate over the IVR objects
    for ivr in ivrs:
        # Skip IVRs with "EXAMPLE" in their name
        if "EXAMPLE" in ivr.name:
            continue

        # Find all instances of script variables in the xmlDefinition attribute
        script_variables = script_variable_pattern.finditer(ivr.xmlDefinition)

        # Iterate over the script variables
        for var in script_variables:
            # Extract the variable name
            b = var.span()[0]
            e = var.span()[1]
            variable = ivr.xmlDefinition[b:e]
            # Split the variable name into parts at the period
            variable_parts = variable.split(".")

            # If the variable has more than one part, add it to the ivr_variables dictionary
            if len(variable_parts) > 1:
                if ivr_variables.get(variable, None) == None:
                    ivr_variables[variable] = []
                if ivr.name not in ivr_variables[variable]:
                    ivr_variables[variable].append(ivr.name)

    # Sort the ivr_variables dictionary
    ivr_variables = collections.OrderedDict(sorted(ivr_variables.items()))

    # If verbose is True, print the ivr_variables dictionary as a JSON object
    if verbose == True:
        j = json.dumps(ivr_variables, indent=4)
        print(j)

    # Return the ivr_variables dictionary
    return ivr_variables
