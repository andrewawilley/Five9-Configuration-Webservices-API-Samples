import re


def grouping_expression(nice_filter):
    """
    Returns a modified filter string with conditions replaced by their corresponding numbers.

    Args:
    - nice_filter (str): A filter string containing condition patterns in the form of [text][number].

    Returns:
    - str: A modified filter string with conditions replaced by their corresponding numbers.
    """

    # Replace the input filter string with the default central_blue filter
    nice_filter = central_blue

    # Define a regular expression pattern to match condition patterns in the input filter string
    condition_pattern = re.compile("\[(.*?)\]\[(.*?)\]")
    conditions = condition_pattern.finditer(nice_filter)

    # Replace any newline or tab characters with a space character
    new_filter = nice_filter.replace("\n", " ").replace("\t", " ")

    # Replace each condition in the input filter string with its corresponding number
    for c in conditions:
        # Get the start and end positions of the condition in the input filter string
        b = c.span()[0]
        e = c.span()[1]

        # Extract the condition text and number from the condition pattern
        cond = nice_filter[b:e]
        cond_number = cond.split("][")[1]
        cond_number = cond_number.replace("]", "")

        # Replace the condition with its corresponding number in the modified filter string
        new_filter = new_filter.replace(cond, cond_number)

    # Remove any extra spaces from the modified filter string
    while new_filter.find("  ") > -1:
        new_filter = new_filter.replace("  ", " ")

    # Replace any remaining double spaces with single spaces
    return new_filter.replace("  ", " ")
