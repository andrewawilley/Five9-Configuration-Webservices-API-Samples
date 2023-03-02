import re


def prettify(ugly="", open_set="{[(<", close_set="}])>"):
    # Add a space to the end of the string to ensure the last character is processed
    ugly += " "

    # Initialize a variable to keep track of the current indentation level
    level = 0

    # Remove any double spaces in the string
    while ugly.find("  ") > -1:
        ugly = ugly.replace("  ", " ")
    while ugly.find("( (") > -1:
        ugly = ugly.replace("( (", "((")
    while ugly.find(") )") > -1:
        ugly = ugly.replace(") )", "))")

    # Initialize a variable to store the formatted output
    output = ""

    # Iterate through each character in the string
    for idx, char in enumerate(ugly):
        # If the character is an opening delimiter, increase the indentation level and add a newline
        if char in open_set:
            level += 1
            output += char + "\n" + "\t" * (level)
        # If the character is a closing delimiter, decrease the indentation level and add a newline
        elif char in close_set:
            level -= 1
            output += "\n" + "\t" * level + char
            # If the next character is not a closing delimiter, add an extra newline
            if ugly[idx + 1] not in close_set:
                output += "\n"
        # If the character is "AND" preceded by a space, add a newline and indent
        elif ugly[idx - 1 : idx + 4] == " AND ":
            output += "\n" + "\t" * level + " " * (-4) + char
        # If the character is "OR" preceded by a space, add a newline and indent
        elif ugly[idx - 1 : idx + 3] == " OR ":
            output += "\n" + "\t" * level + " " * (-3) + char
        # For all other characters, simply add them to the output string
        else:
            output += char

    # Return the formatted string
    return output


def demystify_filter(profile_filter, verbose=False):
    """
    profile_filter = profile filter information object with a ["grouping"]["expression"] attribute
    verbose=False by default, set True to spool output to console
    """
    # Compile a regular expression to match numbers
    numbers = re.compile(r"(\d+)")

    # Set up placeholder strings for parentheses
    parens_open = "|||||"
    parens_close = "+_+_+_+_"

    # Create a dictionary to map expression operator strings to their corresponding symbols
    expression_operators = {
        "Equals": "=",
        "NotEqual": "!=",
        "Like": "LIKE",
        "Less": "<",
        "LessOrEqual": "<=",
        "Greater": ">",
        "GreaterOrEqual": ">=",
    }

    # Get the grouping expression from the profile filter object
    grouping_expression = profile_filter["grouping"]["expression"]

    # Replace numbers in the expression with brackets
    grouping_expression = numbers.sub(r"[\1]", grouping_expression)

    # Iterate through each criteria in the filter
    for idx, criteria in enumerate(profile_filter["crmCriteria"]):
        # Get the index of the current criteria
        i = idx + 1

        # Replace parentheses in the right value with placeholder strings
        rightValue = (
            (criteria["rightValue"] or "null")
            .replace("(", parens_open)
            .replace(")", parens_close)
        )

        # Construct the condition string using the left value, compare operator, and right value
        condition = (
            f'{criteria["leftValue"]} ::{criteria["compareOperator"]}:: {rightValue}'
        )

        # Replace the bracketed number in the grouping expression with the condition string
        grouping_expression = grouping_expression.replace(
            f"[{i}]", f"[{condition}][{i}]"
        )

    # Use the prettify function to format the grouping expression
    demystified = (
        prettify(grouping_expression, "(", ")")
        .replace(parens_open, "(")
        .replace(parens_close, ")")
    )

    # If verbose is True, print the demystified expression to the console
    if verbose == True:
        print(f"{demystified}")

    # Return the demystified expression
    return demystified


def remystify_filter_in_place(nice_filter):
    nice_filter = re.sub(r"\[.*?\]\[", "", nice_filter)
    nice_filter = nice_filter.replace("]", "").replace("\t", "").replace("\n", "")
    return nice_filter


def remystify_filter(nice_filter):
    # Remove all bracketed numbers from the nice filter string
    nice_filter = re.sub(r"(\[([0-9]*)\])", "", nice_filter)

    # Compile a regular expression to match strings enclosed in brackets
    condition_pattern = re.compile("\[(.*?)\]")

    # Find all occurrences of the condition pattern in the nice filter string
    conditions = condition_pattern.finditer(nice_filter)

    # Initialize a list to store unique conditions and an empty list for the crmCriteria
    unique_conditions = []
    crmCriteria = []

    # Set the new grouping expression to the nice filter string
    new_grouping_expression = nice_filter

    # Iterate through the found conditions
    for c in conditions:
        # Get the start and end indices of the condition string
        b = c.span()[0]
        e = c.span()[1]

        # Get the condition string
        cond = nice_filter[b:e]

        # Get the unique condition by taking the portion of the string before the closing bracket
        unique_condition = cond.split("]")[0][1:]

        # If the unique condition has not yet been added to the list, add it
        if unique_condition not in unique_conditions:
            unique_conditions.append(unique_condition)

    # Iterate through the unique conditions
    for unique_condition in unique_conditions:
        # Split the condition string on the "::" separator
        criteria = unique_condition.split("::")

        # Get the compare operator, left value, and right value from the criteria
        compareOperator = criteria[1]
        leftValue = criteria[0][:-1]
        rightValue = criteria[2][1:]

        # If the right value is "null", set it to None
        if rightValue == "null":
            rightValue = None

        # Add a new crmCriteria object to the list
        crmCriteria.append(
            {
                "compareOperator": compareOperator,
                "leftValue": leftValue,
                "rightValue": rightValue,
            }
        )

    # Replace all occurrences of the unique conditions in the new grouping expression with the index of the condition
    for idx, condition in enumerate(unique_conditions):
        new_grouping_expression = re.sub(condition, f"{idx+1}", new_grouping_expression)

    # Remove brackets and newlines from the new grouping expression, and trim leading/trailing whitespace
    new_grouping_expression = (
        new_grouping_expression.replace("[", "")
        .replace("]", "")
        .replace("\n", " ")
        .replace("\t", " ")
        .strip()
    )

    # Remove any double spaces from the new grouping expression
    while new_grouping_expression.find("  ") > -1:
        new_grouping_expression = new_grouping_expression.replace("  ", " ")

    # Print the index and value of each unique condition
    for idx, condition in enumerate(unique_conditions):
        print(f"{idx+1:02} {condition}")

    # for idx, condition in enumerate(crmCriteria):
    #     print(f'{idx+1:02} {condition}')

    print(new_grouping_expression)

    return {
        "crmCriteria": crmCriteria,
        "grouping": {"expression": new_grouping_expression, "type": "Custom"},
        "orderByFields": [],
    }
