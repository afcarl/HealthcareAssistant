import pandas as pd
class Planner:
    def __init__(self):
        self.treatmentTable = pd.DataFrame()
        self.complementaryTable = pd.DataFrame()

    '''
    accesses the Patient and generates the list of all effects,
    finds the conflicts and stores them in the patient object
    '''