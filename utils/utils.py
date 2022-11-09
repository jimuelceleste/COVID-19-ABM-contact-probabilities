import json

def parse_json(filename):
    content = {}
    with open(filename) as file:
        content = json.load(file)
    return content

def get_parameters(filename):
    parameters = parse_json(filename)

    spaces = parameters["spaces"]

    variable_params = []
    for filename in parameters["variable_params"]:
        variable_params.append(parse_json(filename))

    fixed_params = []
    for filename in parameters["fixed_params"]:
        fixed_params.append(parse_json(filename))

    contact_matrix = parse_json(parameters["contact_matrix"])

    return {
        "spaces": spaces,
        "variable_params": variable_params,
        "fixed_params": fixed_params,
        "contact_matrix": contact_matrix}
