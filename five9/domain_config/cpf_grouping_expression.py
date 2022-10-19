import re

def grouping_expression(nice_filter):
    nice_filter = central_blue
    condition_pattern = re.compile('\[(.*?)\]\[(.*?)\]')
    conditions = condition_pattern.finditer(nice_filter)
    
    new_filter = nice_filter.replace('\n', ' ').replace('\t',' ')
    for c in conditions:
        # print(c)
        b = c.span()[0]
        e = c.span()[1]
        cond = nice_filter[b:e]
        # print(cond)
        cond_number = cond.split("][")[1]
        cond_number = cond_number.replace(']','')
        new_filter = new_filter.replace(cond,cond_number)
    
    while new_filter.find('  ') > -1:
        new_filter = new_filter.replace('  ', ' ')
    
    return new_filter.replace('  ', ' ')
