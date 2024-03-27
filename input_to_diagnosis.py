class Diagnosis():
    def __init__(self,treated=None,original=None):
        self.treated_prompt = treated
        self.original_prompt = original
    def set_prompt(self,treated,original):
        self.treated_prompt = treated
        self.original_prompt = original
    def get_treated_prompt(self):
        return self.treated_prompt, self.original_prompt