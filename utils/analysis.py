import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_average_time_series(sim_id, iterations, steps, state, output_dir):
    # Returns the average of the desired time series
    # given by state parameter.
    output = np.zeros(steps)

    for i in range(iterations):
        with open("%s/%s_iter_%i.pkl" % (output_dir, sim_id, i), "rb") as file:
            data = pickle.load(file)
            output += np.array(data["seirdv_total_time_series"][state])

    return output / iterations

def get_average_age_dist(sim_id, iterations, states, output_dir):
    # Returns the age-stratified average of the values
    # of all the states for simulation with id sim_id.
    results = []

    for state in states:
        results.append(get_average_age_dist_state(sim_id, iterations, state, output_dir))

    return results

def get_average_age_dist_state(sim_id, iterations, state, output_dir):
    # Returns the age-stratified average of the values
    # of a state/compartment for simulation with id sim_id.
    output = np.zeros(17)

    for i in range(iterations):
        with open("%s/%s_iter_%i.pkl" % (output_dir, sim_id, i), "rb") as file:
            # Loading the pickle file
            data = pickle.load(file)

            # Output
            output += np.array(data["seirdv_total_final"][state])

    return output / iterations

def generate_age_groups(size, groups):
    age_range = lambda x: (x * size, (x + 1) * size - 1)
    return [age_range(i) for i in range(groups)]

def plot_average_age_dist(sim_ids, states, iterations, total_population, scale, colors, styles, output_dir):
    states_legend = {
        "S": "Susceptible",
        "E": "Exposed",
        "I": "Infectious",
        "R": "Recovered",
        "D": "Dead",
        "V": "Vaccinated"
    }

    age_groups = ["%i to %i" % (group[0], group[1]) for group in generate_age_groups(5, 16)]
    age_groups.append("80+")

    for state in states:
        for sim_id in sim_ids:
            average_age_dist = (get_average_age_dist_state(sim_id, iterations, state, output_dir) / total_population) * scale
            plt.plot(age_groups, average_age_dist, styles[sim_id] + colors[sim_id], label=sim_ids[sim_id])

        plt.title(states_legend[state])
        plt.xlabel("Age Groups")
#         plt.ylabel("(%s / N) * %i" % (state, scale))
        plt.ylabel("%s per %i individuals" % (states_legend[state], scale))
        plt.xticks(rotation=90)
        plt.legend()
        plt.savefig('%s/age_%s.png' % (output_dir, states_legend[state]), dpi=300, bbox_inches='tight')
        plt.show()

def plot_average_time_series(sim_ids, states, steps, iterations, total_population, scale, colors, styles, output_dir):
    states_legend = {
        "S": "Susceptible",
        "E": "Exposed",
        "I": "Infectious",
        "R": "Recovered",
        "D": "Dead",
        "V": "Vaccinated"
    }

    for state in states:
        for sim_id in sim_ids:
            average_time_series = (get_average_time_series(sim_id, iterations, steps, state, output_dir) / total_population) * scale
            plt.plot(average_time_series, styles[sim_id] + colors[sim_id], label=sim_ids[sim_id])

        plt.title(states_legend[state])
        plt.xlabel("Time Step")
#         plt.ylabel("(%s / N) * %i" % (state, scale))
        plt.ylabel("%s per %i individuals" % (states_legend[state], scale))
        plt.legend()
        plt.savefig('%s/time_%s.png' % (output_dir, states_legend[state]), dpi=300, bbox_inches='tight')
        plt.show()

def save_results_as_excel(sim_ids, iterations, states, output_dir, filename='results.xlsx'):
    with pd.ExcelWriter(filename) as writer:
        for sim_id in sim_ids:
            sim_results = pd.DataFrame(get_average_age_dist(sim_id, iterations, states, output_dir))
            sim_results.to_excel(writer, sheet_name=sim_ids[sim_id])
