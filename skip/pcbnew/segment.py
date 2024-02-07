'''
Created on Feb 1, 2024

@author: Pat Deegan
@copyright: Copyright (C) 2024 Pat Deegan, https://psychogenic.com
'''


from skip.sexp.parser import ParsedValue, ParsedValueWrapper

class SegmentWrapper(ParsedValueWrapper):
    def __init__(self, v:ParsedValue):
        super().__init__(v)
        self._net = None 
        self._layer = None
        
    def translation(self, by_x:float, by_y:float):
        '''
            Shift this segment a certain amount in x and y.
            
            If you want to rotate and do weird things, well, you're on 
            your own.  User seg.start and .end values.
        '''
        coords_end = self.end.value
        coords_start = self.start.value 
        
        self.start.value = [coords_start[0] + by_x, coords_start[1] + by_y]
        self.end.value =   [coords_end[0] + by_x,   coords_end[1] + by_y]
    
    @property
    def layer(self):
        if self._layer is None:
            layer_name = self.wrapped_parsed_value.layer.value
            pcb = self.parent # segments are top level
            if layer_name in pcb.layers:
                self._layer = pcb.layers[layer_name]
            else:
                self._layer = -1 # something wrong
                
        return self._layer
    
    
    @layer.setter 
    def layer(self, setTo):
        if isinstance(setTo, str):
            layer_name = setTo
        else:
            layer_name = setTo.name # needs to be a thing with name ya
        
        self.wrapped_parsed_value.layer.value = layer_name 
        self._layer = None 
        return 
        
        
    
    
    @property 
    def net(self):
        if self._net is None:
            net_id = self.wrapped_parsed_value.net.value
            pcb = self.parent # segments are top level
            if net_id < len(pcb.net):
                self._net = pcb.net[net_id]
            else:
                self._net = -1 # something wrong
                
        return self._net
    
    @net.setter 
    def net(self, setTo):
        try:
            net_id = int(setTo)
        except:
            net_id = int(setTo.id) # must be a thing with an id, presumably a Net
        
        self.wrapped_parsed_value.net.value = net_id 
        self._net = None 
            
        
    
    def __repr__(self):
        return f'<Segment in {self.net.name} on {self.layer.name}>'
        
