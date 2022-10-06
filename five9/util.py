import collections
import json
import random
import re
import string

def get_random_password(length=20, required_digits=2, required_lower=2, required_caps=2, required_special=1, \
                                            characters_to_avoid=["O", "0", "=", "|", " ", "\"", "'", ",", "`" ]):
    '''
    Return a randomly generated password of a specified length and composition

    Keyword arguments:
    length -- the desired password length, default 20
    required_digits -- minimum number of password characters that are digits, default 2
    required_lower  -- minimum number of password characters that are lowercase a-z, default 2
    required_caps   -- minimum number of password characters that are uppercase A-Z, default 2
    required_special-- minimum number of password characters that are non-alphanumeric, default 2
    
    characters_to_avoid -- list of characters that should be excluded from the password, 
                           default = ["O", "0", "=", "|", " ", "\"", "'", ",", "`" ]
        
    '''
    random.seed()
    
    password_characters =(string.ascii_letters + string.digits + string.punctuation).translate(
        {ord(x): '' for x in characters_to_avoid})

    password_lower = ''.join(random.choice(string.ascii_letters.lower().translate(
        {ord(x): '' for x in characters_to_avoid})) for i in range(required_lower)) 
    
    password_caps = ''.join(random.choice(string.ascii_letters.upper().translate(
        {ord(x): '' for x in characters_to_avoid})) for i in range(required_caps))
    
    password_digits = ''.join(random.choice(string.digits.translate(
        {ord(x): '' for x in characters_to_avoid})) for i in range(required_digits))    
    
    password_spec =  ''.join(random.choice(string.punctuation.translate(
        {ord(x): '' for x in characters_to_avoid})) for i in range(required_special))

    rnd_char_count = length - required_digits - required_lower - required_caps - required_special

    password_base = ''.join(random.choice(password_characters) for i in range(rnd_char_count))
    password = password_base + password_lower + password_caps + password_digits + password_spec
    password = list(password)
    random.shuffle(password)
    password = ''.join(password)
    # print(f'{password_base} {password_lower} {password_caps} {password_digits} {password_spec} = {password}')
    return password

def ivr_variable_usage(ivrs, verbose=False):

    ivr_variables = {}

    script_variable_pattern = re.compile(r'(?<=<variableName>)(.*?)(?=<\/variableName>)')
    for ivr in ivrs:
        if 'EXAMPLE' in ivr.name:
            continue
        script_variables = script_variable_pattern.finditer(ivr.xmlDefinition)
        for var in script_variables:
            b = var.span()[0]
            e = var.span()[1]
            variable = ivr.xmlDefinition[b:e]
            variable_parts = variable.split(".")
            if len(variable_parts) > 1:
                if ivr_variables.get(variable, None) == None:
                    ivr_variables[variable] = []
                if ivr.name not in ivr_variables[variable]:
                    ivr_variables[variable].append(ivr.name)

    ivr_variables = collections.OrderedDict(sorted(ivr_variables.items()))
    if verbose == True:
        j = json.dumps(ivr_variables, indent=4)
        print(j)

    return ivr_variables
