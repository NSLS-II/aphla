"""
Knob-related Classes

:author: Yoshiteru Hidaka
"""

########################################################################
class Knob():
    """"""

    #----------------------------------------------------------------------
    def __init__(self, channel_obj):
        """Constructor"""
        
        import copy
        
        self.__dict__ = copy.copy(channel_obj.__dict__)
        delattr(self,'read_only')
        
        self.pv_unit = ''
        self.pvrb_val = None
        self.pvrb_val_time_stamp = None
        self.pvsp_val = None
        self.pvsp_val_time_stamp = None
        
########################################################################
class KnobGroup():
    """"""

    #----------------------------------------------------------------------
    def __init__(self, name, knob_list, weight_factor):
        """Constructor"""
        
        self.name = name
        self.knobs = knob_list
        self.weight = weight_factor
    
########################################################################
class KnobGroupList():
    """"""

    #----------------------------------------------------------------------
    def __init__(self, **kwargs):
        """Constructor"""
        
        self.knobGroups = \
            kwargs.get('KnobGroup_list', [])
        self.refKnobGroupName = \
            kwargs.get('reference_KnobGroup_name', '')
        self.refStepSize = \
            kwargs.get('reference_step_size', 0)
        
        self.ref_index = 0
        self.normalized_weight_list = []
        self.step_size_list = []

        self.updateDerivedProperties()
    
    #----------------------------------------------------------------------
    def _changeRefStepSize(self, new_ref_step_size):
        """"""
        
        self.refStepSize = new_ref_step_size
        self.updateDerivedProperties()
    
    #----------------------------------------------------------------------
    def _changeRefKnobGroupName(self, new_ref_knob_group_name):
        """"""
        
        self.refKnobGroupName = new_ref_knob_group_name
        self.updateDerivedProperties()
        
    
    #----------------------------------------------------------------------
    def updateDerivedProperties(self):
        """"""
        
        if self.knobGroups:
            
            # If reference knob group has not been selected yet,
            # set it to first knob group name by default
            if not self.refKnobGroupName:
                self.refKnobGroupName = self.knobGroups[0].name
            
            self.weight_list = [g.weight for g in self.knobGroups]
        
            self.update_reference_index()
            self.update_normalized_weight_list()
            self.update_step_size_list()
        else:
            self.weight_list = []
        
        
    #----------------------------------------------------------------------
    def update_reference_index(self):
        """"""
        
        knobGroup_name_list = [g.name for g in self.knobGroups]
        self.ref_index = knobGroup_name_list.index(self.refKnobGroupName)
        
    #----------------------------------------------------------------------
    def update_normalized_weight_list(self):
        """"""
        
        ref_weight = self.weight_list[self.ref_index]
        self.normalized_weight_list = \
            [w/ref_weight for w in self.weight_list]
        
    #----------------------------------------------------------------------
    def update_step_size_list(self):
        """"""
        
        self.step_size_list = [nw*self.refStepSize 
                               for nw in self.normalized_weight_list]   

    #----------------------------------------------------------------------
    def extend(self, new_KnobGroupList):
        """"""
        
        self.knobGroups.extend(new_KnobGroupList.knobGroups)
        
        self.updateDerivedProperties()