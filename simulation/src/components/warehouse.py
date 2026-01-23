"""
Parts Warehouse Component
"""

import simpy
import logging
from typing import Any

class PartsWarehouse:
    """Parts warehouse with replenishment logic"""
    
    def __init__(self, env: simpy.Environment, initial_parts: int, capacity: int,
                 replenishment_interval: float, replenishment_quantity: int,
                 data_collector: Any):
        self.env = env
        self.capacity = capacity
        self.replenishment_interval = replenishment_interval
        self.replenishment_quantity = replenishment_quantity
        self.data_collector = data_collector
        self.logger = logging.getLogger(__name__)
        
        # Create container for parts
        self.parts = simpy.Container(env, capacity=capacity, init=initial_parts)
        
        self.logger.info(f"Warehouse initialized with {initial_parts} parts (capacity: {capacity})")
        self._record_level()
    
    def _record_level(self):
        """Record current inventory level"""
        self.data_collector.record_metric('warehouse_level', self.parts.level, self.env.now)
    
    def get_parts(self, quantity: int):
        """Get parts from warehouse"""
        start_time = self.env.now
        
        # Wait for parts to be available
        yield self.parts.get(quantity)
        
        wait_time = self.env.now - start_time
        current_level = self.parts.level
        
        self.logger.debug(f"Retrieved {quantity} parts at time {self.env.now:.2f} "
                         f"(wait: {wait_time:.2f}h, remaining: {current_level})")
        
        # Record warehouse event
        self.data_collector.record_event('warehouse_get', {
            'time': self.env.now,
            'quantity': quantity,
            'wait_time': wait_time,
            'remaining_parts': current_level
        })
        self._record_level()
    
    def replenishment_process(self):
        """Periodic replenishment of warehouse"""
        while True:
            # Wait for replenishment interval
            yield self.env.timeout(self.replenishment_interval)
            
            # Calculate how many parts to add (don't exceed capacity)
            current_level = self.parts.level
            space_available = self.capacity - current_level
            parts_to_add = min(self.replenishment_quantity, space_available)
            
            if parts_to_add > 0:
                yield self.parts.put(parts_to_add)
                new_level = self.parts.level
                
                self.logger.info(f"Warehouse replenished with {parts_to_add} parts at time {self.env.now:.2f} "
                               f"(level: {current_level} -> {new_level})")
                
                # Record replenishment event
                self.data_collector.record_event('warehouse_replenishment', {
                    'time': self.env.now,
                    'parts_added': parts_to_add,
                    'new_level': new_level
                })
                self._record_level()
            else:
                self.logger.warning(f"Warehouse full at replenishment time {self.env.now:.2f}")