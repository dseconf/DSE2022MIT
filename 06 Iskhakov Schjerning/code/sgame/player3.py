import numpy as np

class player:
    name = 'Bertel'
    def __init__(self): 
        self.i = None
    
    def play(self, state, history):
        i = self.i 
        j = 1-self.i 
        
        pmin,pmax = state['actions'][i]
        
        if len(history) == 0: 
            # initial play 
            p = pmax
        else: 
            # dynamic play 
            p_lag = history[-1]
            pi_lag = p_lag[i]
            pj_lag = p_lag[j]

            p = max(pj_lag*0.95,state['marginal'])  

        # verify we have not done something stupid 
        FAIL = (p < pmin) or (p > pmax)
        if FAIL: # choose a random allowed action 
            p = np.random.uniform(pmin, pmax)
        
        return p 