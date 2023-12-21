import collections
import json
import random
import re
import string

def get_random_password(
    length=20,
    required_digits=2,
    required_lower=2,
    required_caps=2,
    required_special=1,
    characters_to_avoid=["O", "0", "=", "|", " ", '"', "'", ",", "`"],
):
    """
    Generates a random password based on specified requirements.

    Args:
    length (int): The total length of the password. Defaults to 20.
    required_digits (int): Minimum number of numeric characters in the password. Defaults to 2.
    required_lower (int): Minimum number of lowercase alphabetic characters. Defaults to 2.
    required_caps (int): Minimum number of uppercase alphabetic characters. Defaults to 2.
    required_special (int): Minimum number of special (non-alphanumeric) characters. Defaults to 1.
    characters_to_avoid (list): A list of characters that should be excluded from the password. 
                                Defaults to ["O", "0", "=", "|", " ", '"', "'", ",", "`"].

    Returns:
    str: The generated random password.
    """

    # Seed the random number generator for randomness
    random.seed()

    # Create a pool of characters for the password, excluding specified characters
    password_characters = (
        string.ascii_letters + string.digits + string.punctuation
    ).translate({ord(x): "" for x in characters_to_avoid})

    # Generate the required lowercase characters
    password_lower = "".join(
        random.choice(
            string.ascii_letters.lower().translate(
                {ord(x): "" for x in characters_to_avoid}
            )
        )
        for i in range(required_lower)
    )

    # Generate the required uppercase characters
    password_caps = "".join(
        random.choice(
            string.ascii_letters.upper().translate(
                {ord(x): "" for x in characters_to_avoid}
            )
        )
        for i in range(required_caps)
    )

    # Generate the required digit characters
    password_digits = "".join(
        random.choice(
            string.digits.translate({ord(x): "" for x in characters_to_avoid})
        )
        for i in range(required_digits)
    )

    # Generate the required special characters
    password_spec = "".join(
        random.choice(
            string.punctuation.translate({ord(x): "" for x in characters_to_avoid})
        )
        for i in range(required_special)
    )

    # Calculate the number of additional random characters needed
    rnd_char_count = (
        length - required_digits - required_lower - required_caps - required_special
    )

    # Generate the additional random characters
    password_base = "".join(
        random.choice(password_characters) for i in range(rnd_char_count)
    )

    # Combine all parts of the password
    password = (
        password_base + password_lower + password_caps + password_digits + password_spec
    )

    # Shuffle the combined password to mix the character types
    password = list(password)
    random.shuffle(password)
    password = "".join(password)

    # Return the final password
    return password


def ivr_variable_usage(ivrs, verbose=False):
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


## TODO add a __main__ handler with command line arguments to run the utilities as stand-alones.
