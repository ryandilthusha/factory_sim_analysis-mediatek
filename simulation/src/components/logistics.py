"""
Logistics Component - Lorry Driver and Departure Process
"""

import simpy
import random
import logging
from typing import Any

class LorryDriver:
    """Lorry driver responsible for shipping finished products"""
    
    def __init__(self, env: simpy.Environment, finished_storage: simpy.Store,
                 capacity: int, car_issue_prob: float, issue_delay: float,
                 data_collector: Any):
        self.env = env
        self.finished_storage = finished_storage
        self.capacity = capacity
        self.car_issue_prob = car_issue_prob
        self.issue_delay = issue_delay
        self.data_collector = data_collector
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.total_shipments = 0
        self.total_products_shipped = 0
        self.total_delays = 0
        self.total_delay_time = 0.0
        
        self.logger.info(f"Lorry driver initialized (capacity: {capacity}, "
                        f"issue prob: {car_issue_prob:.1%}, issue delay: {issue_delay}h)")
    
    def departure_process(self):
        """Main departure process - collect and ship products"""
        while True:
            # Wait until we have enough products to fill the lorry
            products_to_ship = []
            
            # Collect products up to lorry capacity
            for _ in range(self.capacity):
                try:
                    # Wait for a product to be available
                    product = yield self.finished_storage.get()
                    products_to_ship.append(product)
                except simpy.Interrupt:
                    break
            
            if products_to_ship:
                departure_time = self.env.now
                num_products = len(products_to_ship)
                
                self.logger.info(f"Lorry loaded with {num_products} products at time {departure_time:.2f}")
                
                # Check for car issues
                delay_time = 0.0
                if random.random() < self.car_issue_prob:
                    delay_time = random.expovariate(1.0 / self.issue_delay)
                    self.total_delays += 1
                    self.total_delay_time += delay_time
                    
                    self.logger.warning(f"Car issue occurred! Delay: {delay_time:.2f}h at time {self.env.now:.2f}")
                    
                    # Record car issue event
                    self.data_collector.record_event('car_issue', {
                        'time': self.env.now,
                        'delay_time': delay_time,
                        'products_affected': num_products
                    })
                    
                    # Wait for the delay
                    yield self.env.timeout(delay_time)
                
                # Simulate departure (assume instant for now, could add travel time)
                actual_departure_time = self.env.now
                
                # Update statistics
                self.total_shipments += 1
                self.total_products_shipped += num_products
                
                self.logger.info(f"Lorry departed at time {actual_departure_time:.2f} "
                               f"with {num_products} products (delay: {delay_time:.2f}h)")
                
                # Record departure event
                self.data_collector.record_event('lorry_departure', {
                    'departure_time': actual_departure_time,
                    'products_shipped': num_products,
                    'delay_time': delay_time,
                    'product_ids': products_to_ship
                })
                
                # Simulate time for lorry to return (could be configurable)
                return_time = 2.0  # 2 hours round trip
                yield self.env.timeout(return_time)
            
            else:
                # No products available, wait a bit before checking again
                yield self.env.timeout(0.5)  # Check every 30 minutes
    
    def get_logistics_stats(self):
        """Get logistics performance statistics"""
        if self.total_shipments == 0:
            return {
                'total_shipments': 0,
                'total_products_shipped': 0,
                'average_products_per_shipment': 0,
                'delay_rate': 0,
                'average_delay_time': 0
            }
        
        avg_products_per_shipment = self.total_products_shipped / self.total_shipments
        delay_rate = self.total_delays / self.total_shipments
        avg_delay_time = self.total_delay_time / max(self.total_delays, 1)
        
        return {
            'total_shipments': self.total_shipments,
            'total_products_shipped': self.total_products_shipped,
            'average_products_per_shipment': avg_products_per_shipment,
            'delay_rate': delay_rate,
            'average_delay_time': avg_delay_time,
            'total_delay_time': self.total_delay_time
        }