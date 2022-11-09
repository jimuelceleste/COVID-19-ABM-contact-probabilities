from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from covid_model.agents import PersonAgent
import random
import pandas as pd


class Covid19Model(Model):
    
    
    def __init__(self, vector_parameters, scalar_parameters, variables, contact_matrix): 
        """instantiates the Covid19Model class"""
        
        # model inputs
        self.vector_parameters = vector_parameters 
        self.scalar_parameters = scalar_parameters 
        self.variables = variables 
        self.contact_matrix = contact_matrix 
        
        # grid and scheduler
        self.grid = MultiGrid(50, 50, True)
        self.scheduler = RandomActivation(self)
        
        # agents, place in the grid and add to scheduler
        self.agents = self.instantiate_agents(self.variables, self.scalar_parameters)
        self.add_to_grid(self.grid, self.agents)
        self.add_to_scheduler(self.scheduler, self.agents)
    
        # summary data
        # summary_time is updated in this class; summary_new_cases is updated in PersonAgent class
        self.summary_time = pd.DataFrame([variables.sum(axis=0)], columns=variables.columns) # time series
        self.summary_new_cases = pd.DataFrame(columns=variables.columns, index=variables.index).fillna(0) # age stratified
        
        # steps counter
        self.steps = 0
        self.running = True
        
        
    def add_to_grid(self, grid, agents):
        """Adds agents to the grid"""
        for agent in agents:
            x = self.random.randrange(grid.width)
            y = self.random.randrange(grid.height)
            position = (x, y)
            grid.place_agent(agent, position)
            
            
    def add_to_scheduler(self, scheduler, agents):
        """Adds agents to the scheduler"""
        for agent in agents:
            scheduler.add(agent)
    
    
    def coin_toss(self, ptrue):
        """generates a pseudo-random choice"""
        if ptrue == 0:
            return False
        return random.uniform(0.0, 1.0) <= ptrue

    
    def instantiate_agents(self, variables, scalar_parameters):
        """instantiates the agents"""
        agents = []
        for state in ['S', 'E', 'I']: 
            for age_group in variables.index:
                n = variables[state][age_group] # agent count 
                for i in range(n):
                    unique_id = state + age_group + str(i) # unique agent ID 
                    wearing_mask = self.coin_toss(self.scalar_parameters['wearing_mask'])
                    physical_distancing = self.coin_toss(self.scalar_parameters['physical_distancing'])
                    agent = PersonAgent(
                        model=self, 
                        unique_id=unique_id, 
                        state=state, 
                        age_group=age_group,
                        wearing_mask=wearing_mask,
                        physical_distancing=physical_distancing
                    )
                    agents.append(agent)
        return agents
                        
        
    def step(self):
        """advances the model by one step"""
        self.steps += 1
        self.scheduler.step()
        self.update_summary_time()
    
    def update_summary_time(self):
        """updates the time series summary variable"""
        self.summary_time.at[self.steps] = self.variables.sum(axis=0)
    
