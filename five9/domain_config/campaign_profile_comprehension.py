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
        condition = f'{criteria["leftValue"]} ::{criteria["compareOperator"]}:: {rightValue}'
        # print(f'{i:03d}  {criteria["leftValue"]} {criteria["compareOperator"]} {criteria["rightValue"]}')
        grouping_expression = grouping_expression.replace(f'[{i}]', f'[{condition}][{i}]')
    demystified = prettify(grouping_expression, "(", ")").replace(parens_open, "(").replace(parens_close, ")")
    if verbose == True:
        print(f'{demystified}')
    return demystified

def remystify_filter(nice_filter):
    nice_filter = re.sub(r'(\[([0-9]*)\])', '', nice_filter)
    condition_pattern = re.compile('\[(.*?)\]')
    # condition_pattern = re.compile('\[(.*?)\]\[([0-9]*)\]')
    conditions = condition_pattern.finditer(nice_filter)

    unique_conditions = []
    crmCriteria = []
    new_grouping_expression = nice_filter

    for c in conditions:
        b = c.span()[0]
        e = c.span()[1]
        cond = nice_filter[b:e]
        unique_condition = cond.split("]")[0][1:]
        
        if unique_condition not in unique_conditions:
            unique_conditions.append(unique_condition)

    # unique_conditions.sort(key=lambda v: v.upper())

    for unique_condition in unique_conditions:
        criteria = unique_condition.split("::")
        compareOperator = criteria[1]
        leftValue = criteria[0][:-1]
        rightValue = criteria[2][1:]
        if rightValue == "null":
            rightValue = None
        crmCriteria.append({
            "compareOperator": compareOperator,
            "leftValue": leftValue,
            "rightValue": rightValue
        })

    # new_grouping_expression = re.sub(r'(\[([0-9]*)\])', '', new_grouping_expression)
    for idx, condition in enumerate(unique_conditions):
        new_grouping_expression = re.sub(condition, f'{idx+1}', new_grouping_expression)

    new_grouping_expression = new_grouping_expression.replace(
        '[', '').replace(
        ']', '').replace(
        '\n', ' ').replace(
        '\t', ' ').strip()

    while new_grouping_expression.find('  ') > -1:
        new_grouping_expression = new_grouping_expression.replace('  ', ' ')


    for idx, condition in enumerate(unique_conditions):
        print(f'{idx+1:02} {condition}')

    # for idx, condition in enumerate(crmCriteria):
    #     print(f'{idx+1:02} {condition}')

    print(new_grouping_expression)

    return {
        "crmCriteria": crmCriteria,
        "grouping": {
            "expression": new_grouping_expression,
            "type": "Custom"
        },
        "orderByFields": []
    }
