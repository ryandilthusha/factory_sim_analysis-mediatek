"""
Production Machine Component
"""

import simpy
import random
import logging
from typing import Any

class ProductionMachine:
    """Production machine with failure and repair logic"""
    
    def __init__(self, env: simpy.Environment, name: str, processing_time: float,
                 mtbf: float, mttr: float, data_collector: Any):
        self.env = env
        self.name = name
        self.processing_time = processing_time / 60.0  # Convert minutes to hours
        self.mtbf = mtbf  # Mean Time Between Failures (hours)
        self.mttr = mttr  # Mean Time To Repair (hours)
        self.data_collector = data_collector
        self.logger = logging.getLogger(__name__)
        
        # Machine resource (capacity 1 = single machine)
        self.machine = simpy.Resource(env, capacity=1)
        
        # Machine state tracking
        self.is_broken = False
        self.total_processing_time = 0.0
        self.total_broken_time = 0.0
        self.items_processed = 0
        
        self.logger.info(f"{self.name} initialized (processing: {processing_time}min, "
                        f"MTBF: {mtbf}h, MTTR: {mttr}h)")
    
    def process_item(self, item_id: int):
        """Process a single item"""
        start_time = self.env.now
        
        # Request machine resource
        with self.machine.request() as request:
            yield request
            
            # Check if machine is broken
            if self.is_broken:
                self.logger.debug(f"{self.name} is broken, waiting for repair...")
                # Wait until machine is repaired
                while self.is_broken:
                    yield self.env.timeout(0.05)
            
            processing_start = self.env.now
            wait_time = processing_start - start_time
            
            # Process the item
            yield self.env.timeout(self.processing_time)
            
            processing_end = self.env.now
            actual_processing_time = processing_end - processing_start
            
            self.items_processed += 1
            self.total_processing_time += actual_processing_time
            
            self.logger.debug(f"{self.name} processed item {item_id} in {actual_processing_time:.2f}h "
                            f"(wait: {wait_time:.2f}h) at time {self.env.now:.2f}")
            
            # Record processing event
            self.data_collector.record_event('machine_processing', {
                'machine': self.name,
                'item_id': item_id,
                'start_time': processing_start,
                'end_time': processing_end,
                'processing_time': actual_processing_time,
                'wait_time': wait_time
            })
    
    def failure_process(self):
        """Machine failure and repair process"""
        while True:
            # Time until next failure (exponential distribution)
            time_to_failure = random.expovariate(1.0 / self.mtbf)
            yield self.env.timeout(time_to_failure)
            
            # Machine breaks down
            if not self.is_broken:
                self.is_broken = True
                failure_time = self.env.now
                
                self.logger.warning(f"{self.name} failed at time {failure_time:.2f}")
                
                # Record failure event
                self.data_collector.record_event('machine_failure', {
                    'machine': self.name,
                    'failure_time': failure_time
                })
                
                # Repair time (exponential distribution)
                repair_time = random.expovariate(1.0 / self.mttr)
                yield self.env.timeout(repair_time)
                
                # Machine is repaired
                self.is_broken = False
                repair_complete_time = self.env.now
                self.total_broken_time += repair_time
                
                self.logger.info(f"{self.name} repaired at time {repair_complete_time:.2f} "
                               f"(downtime: {repair_time:.2f}h)")
                
                # Record repair event
                self.data_collector.record_event('machine_repair', {
                    'machine': self.name,
                    'repair_time': repair_complete_time,
                    'downtime': repair_time
                })