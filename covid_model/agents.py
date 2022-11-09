from mesa import Agent
import random

class PersonAgent(Agent):

    
    def __init__(self, model, unique_id, state, age_group, wearing_mask, physical_distancing, days_incubating=0, days_infected=0):
        """instantiates the PersonAgent class"""
        super().__init__(unique_id, model)
        self.state = state
        self.age_group = age_group
        self.wearing_mask = wearing_mask
        self.physical_distancing = physical_distancing
        self.days_incubating = days_incubating
        self.days_infected = days_infected

    
    def coin_toss(self, ptrue):
        """generates a pseudo-random choice"""
        if ptrue == 0: 
            return False
        return random.uniform(0.0, 1.0) <= ptrue

    
    def interact(self):
        """interacts with cellmates"""
        if self.state == "I":
            cellmates = self.model.grid.get_cell_list_contents([self.pos])
            if len(cellmates) > 1:
                for cellmate in cellmates:
                        if self.is_susceptible(cellmate):
                            cellmate.state_transition(cellmate.state, "E")

                            
    def is_susceptible(self, cellmate):
        """checks if cellmate is susceptible"""
        susceptibility = cellmate.state == "S"
        susceptibility = susceptibility and self.coin_toss(self.model.contact_matrix[self.age_group][cellmate.age_group])
        susceptibility = susceptibility and not cellmate.protected_by_mask()
        susceptibility = susceptibility and not cellmate.protected_by_physical_distancing()
        susceptibility = susceptibility and cellmate.coin_toss(
            cellmate.model.vector_parameters["infection_rate"][cellmate.age_group])
        return susceptibility 
    
    
    def move(self):
        """moves from one point to another in the grid"""
        # if not dead
        if self.state not in ["D", "R"]:
            possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False,
                radius=self.model.scalar_parameters["agent_movement_range"])
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)
    
    
    def protected_by_mask(self):
        """checks if agent is protected by mask"""
        protection_activated = self.coin_toss(self.model.scalar_parameters["wearing_mask_protection"])
        return self.wearing_mask and protection_activated

    
    def protected_by_physical_distancing(self):
        """checks if agent is protected by physical distancing"""
        protection_activated = self.coin_toss(self.model.scalar_parameters["physical_distancing_protection"])
        return self.physical_distancing and protection_activated
    
    
    def state_transition(self, current_state, next_state):
        """transition: changes the state of the agent"""
        self.model.summary_new_cases[next_state][self.age_group] += 1
        self.model.variables[current_state][self.age_group] -= 1
        self.model.variables[next_state][self.age_group] += 1
        self.state = next_state
        
        
    def step(self):
        """advances the agent by a step"""
        self.status()
        self.interact()
        self.move()

        
    def status(self):
        """checks internal status"""
        # status == exposed
        if self.state == "E":
            self.days_incubating += 1
            if self.days_incubating > self.random.normalvariate(self.model.scalar_parameters["average_incubation_period"], 2):
                self.state_transition(self.state, "I")
        
        # status == infectious
        elif self.state == "I":
            if self.days_infected < self.random.normalvariate(self.model.scalar_parameters["average_infectious_period"], 3):
                self.days_infected += 1
            else:
                if self.coin_toss(self.model.vector_parameters["death_rate"][self.age_group]):
                    self.state_transition(self.state, "D")
                    self.model.grid.remove_agent(self)
                    self.model.scheduler.remove(self)
                elif self.coin_toss(self.model.vector_parameters["recovery_rate"][self.age_group]):
                    self.state_transition(self.state, "R")
                    self.model.grid.remove_agent(self)
                    self.model.scheduler.remove(self)
    
