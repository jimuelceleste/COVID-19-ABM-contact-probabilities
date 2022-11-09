from utils import parse_json
import pandas as pd
import numpy as np
import json

def rescale_agent_population(input_filename, output_filename, agent_population=15000):
    data = pd.DataFrame(parse_json(input_filename))
    N = data.sum().sum()

    # Distribution
    data /= N

    # Rescale
    data *= agent_population

    # Gets ceiling of values
    data = data.apply(np.ceil)

    print("Agent Population: %i" % (data.sum().sum()))

    # Makes data a dict
    data = dict([(state, [int(i) for i in list(data[state].values)]) for state in "SEIRDV"])

    # Saves changes to the file
    with open(output_filename, "w") as file:
        json.dump(data, file, indent=4)

rescale_agent_population(
    "vaccination_scenarios_raw/seirdv_0.json",
    "vaccination_scenarios/seirdv_0.json",
    agent_population=8000)
rescale_agent_population(
    "vaccination_scenarios_raw/seirdv_1.json",
    "vaccination_scenarios/seirdv_1.json",
    agent_population=8000)
rescale_agent_population(
    "vaccination_scenarios_raw/seirdv_2.json",
    "vaccination_scenarios/seirdv_2.json",
    agent_population=8000)
rescale_agent_population(
    "vaccination_scenarios_raw/seirdv_3.json",
    "vaccination_scenarios/seirdv_3.json",
    agent_population=8000)
rescale_agent_population(
    "vaccination_scenarios_raw/seirdv_4.json",
    "vaccination_scenarios/seirdv_4.json",
    agent_population=8000)
    
# Agent Population: 8057
# Agent Population: 8060
# Agent Population: 8059
# Agent Population: 8063
# Agent Population: 8059

