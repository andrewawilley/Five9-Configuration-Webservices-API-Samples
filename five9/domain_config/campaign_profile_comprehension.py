from domain_config import domain_capture
import re


def prettify(ugly="", open_set="{[(<", close_set="}])>"):
    ugly += " "
    level = 0
    while ugly.find('  ') > -1:
        ugly = ugly.replace('  ', ' ')
    while ugly.find('( (') > -1:
        ugly = ugly.replace('( (', '((')
    while ugly.find(') )') > -1:
        ugly = ugly.replace(') )', '))')
    indent_level = 0
    # print(f'\n\n{ugly}\n\n')
    output = ""
    for idx, char in enumerate(ugly):
        if char in open_set:
            level += 1
            output += char + "\n" + "\t"*(level)
        elif char in close_set:
            level -= 1
            output += "\n" + "\t"*level + char 
            if ugly[idx+1] not in close_set:
                output += '\n'
        elif ugly[idx-1:idx+4] == ' AND ':
            output += "\n" + "\t"*level+ " "*(-4) + char
        elif ugly[idx-1:idx+3] == ' OR ':
            output += "\n" + "\t"*level+ " "*(-3) + char
        else:
            output += char
    # print(output)
    return output


def demystify_filter(profile_filter, verbose=False):
    '''
    profile_filter = profile filter information object with a ["grouping"]["expression"] attribute
    verbose=False by default, set True to spool output to console
    '''
    numbers = re.compile(r'(\d+)')
    parens_open = "|||||"
    parens_close = "+_+_+_+_"
    expression_operators = {
        "Equals": "=",
        "NotEqual": "!=",
        "Like": "LIKE",
        "Less": "<",
        "LessOrEqual": "<=",
        "Greater": ">",
        "GreaterOrEqual": ">="
    }
    grouping_expression = profile_filter["grouping"]["expression"]
    grouping_expression = numbers.sub(r'[\1]', grouping_expression)
    for idx, criteria in enumerate(profile_filter["crmCriteria"]):
        i = idx+1
        rightValue = (criteria["rightValue"] or "null").replace("(", parens_open).replace(")", parens_close)
        condition = f'{criteria["leftValue"]} {criteria["compareOperator"]} "{rightValue}"'
        # print(f'{i:03d}  {criteria["leftValue"]} {criteria["compareOperator"]} {criteria["rightValue"]}')
        grouping_expression = grouping_expression.replace(f'[{i}]', f'[{condition}][{i}]')
    demystified = prettify(grouping_expression, "(", ")").replace(parens_open, "(").replace(parens_close, ")")
    if verbose == True:
        print(f'{demystified}')
    return demystified
