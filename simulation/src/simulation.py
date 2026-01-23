"""
Factory Simulation - Main Simulation Logic
"""

import simpy
import random
import logging
from typing import Dict, List, Any
from components.warehouse import PartsWarehouse
from components.machine import ProductionMachine
from components.logistics import LorryDriver
from analysis.data_collector import DataCollector

class FactorySimulation:
    """Main factory simulation class"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.env = simpy.Environment()
        self.data_collector = DataCollector()
        
        # Set random seed for reproducibility
        random.seed(config['simulation']['random_seed'])
        
        # Initialize components
        self._setup_components()
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('simulation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _setup_components(self):
        """Initialize all simulation components"""
        # Parts warehouse
        warehouse_config = self.config['parts_warehouse']
        self.warehouse = PartsWarehouse(
            self.env,
            initial_parts=warehouse_config['initial_parts'],
            capacity=warehouse_config['capacity'],
            replenishment_interval=warehouse_config['replenishment_interval_hours'],
            replenishment_quantity=warehouse_config['replenishment_quantity'],
            data_collector=self.data_collector
        )
        
        # Production machines
        production_config = self.config['production_line']
        self.machines = []
        
        for i, machine_config in enumerate(production_config['machines']):
            machine = ProductionMachine(
                self.env,
                name=machine_config['name'],
                processing_time=machine_config['processing_time_minutes'],
                mtbf=machine_config['mtbf_hours'],
                mttr=machine_config['mttr_hours'],
                data_collector=self.data_collector
            )
            self.machines.append(machine)
        
        # Buffers between machines
        self.pending_orders = simpy.Store(self.env)
        self.buffer_A_B = simpy.Store(self.env, capacity=production_config['buffer_A_B_size'])
        self.buffer_B_C = simpy.Store(self.env, capacity=production_config['buffer_B_C_size'])
        
        # Finished products storage
        storage_config = self.config['finished_storage']
        self.finished_storage = simpy.Store(self.env, capacity=storage_config['capacity'])
        
        # Logistics
        logistics_config = self.config['logistics']
        self.lorry_driver = LorryDriver(
            self.env,
            finished_storage=self.finished_storage,
            capacity=logistics_config['lorry_capacity'],
            car_issue_prob=logistics_config['driver']['car_issue_prob'],
            issue_delay=logistics_config['driver']['issue_delay_hours'],
            data_collector=self.data_collector
        )
    
    def order_arrival_process(self):
        """Process for generating customer orders"""
        order_id = 0
        arrival_config = self.config['order_arrival']
        
        while True:
            # Wait for next order arrival (exponential distribution)
            interarrival_time = random.expovariate(1.0 / arrival_config['interarrival_time_hours'])
            yield self.env.timeout(interarrival_time)
            
            order_id += 1
            self.logger.info(f"Order {order_id} arrived at time {self.env.now:.2f}")
            
            # Record order arrival
            self.data_collector.record_event('order_arrival', {
                'order_id': order_id,
                'time': self.env.now
            })
            
            # Put order into pending queue
            yield self.pending_orders.put(order_id)

    def machine_a_worker(self):
        """Process for Machine A pulling from pending orders"""
        while True:
            order_id = yield self.pending_orders.get()
            
            # Get parts from warehouse
            yield self.env.process(self.warehouse.get_parts(1))
            
            # Process through Machine A
            yield self.env.process(self.machines[0].process_item(order_id))
            
            # Move to buffer A-B
            yield self.buffer_A_B.put(order_id)
            self.data_collector.record_metric('buffer_A_B_level', len(self.buffer_A_B.items), self.env.now)

    def machine_b_worker(self):
        """Process for Machine B pulling from buffer A-B"""
        while True:
            order_id = yield self.buffer_A_B.get()
            self.data_collector.record_metric('buffer_A_B_level', len(self.buffer_A_B.items), self.env.now)
            
            # Process through Machine B
            yield self.env.process(self.machines[1].process_item(order_id))
            
            # Move to buffer B-C
            yield self.buffer_B_C.put(order_id)
            self.data_collector.record_metric('buffer_B_C_level', len(self.buffer_B_C.items), self.env.now)

    def machine_c_worker(self):
        """Process for Machine C pulling from buffer B-C"""
        while True:
            order_id = yield self.buffer_B_C.get()
            self.data_collector.record_metric('buffer_B_C_level', len(self.buffer_B_C.items), self.env.now)
            
            # Process through Machine C
            yield self.env.process(self.machines[2].process_item(order_id))
            
            # Move to finished storage
            yield self.finished_storage.put(order_id)
            self.data_collector.record_metric('finished_storage_level', len(self.finished_storage.items), self.env.now)
            
            self.logger.info(f"Order {order_id} completed at time {self.env.now:.2f}")
            
            # Record completion
            self.data_collector.record_event('order_completed', {
                'order_id': order_id,
                'time': self.env.now
            })

    def run(self) -> Dict[str, Any]:
        """Run the simulation and return results"""
        duration = self.config['simulation']['duration_hours']
        
        self.logger.info(f"Starting simulation for {duration} hours")
        
        # Start processes
        self.env.process(self.order_arrival_process())
        self.env.process(self.machine_a_worker())
        self.env.process(self.machine_b_worker())
        self.env.process(self.machine_c_worker())
        
        self.env.process(self.warehouse.replenishment_process())
        self.env.process(self.lorry_driver.departure_process())
        
        # Start machine failure processes
        for machine in self.machines:
            self.env.process(machine.failure_process())
        
        # Run simulation
        self.env.run(until=duration)
        
        self.logger.info("Simulation completed")
        
        # Return collected data
        return self.data_collector.get_results()