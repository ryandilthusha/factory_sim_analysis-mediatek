#!/usr/bin/env python3
"""
Factory Simulation - Main Entry Point
"""

import yaml
import sys
import os
from pathlib import Path

# Add src to path and ensure we're using the local modules
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

# Import with explicit path to avoid conflicts
from simulation import FactorySimulation
from analysis.reporting import generate_report

def load_config(config_path='../config.yaml'):
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        print("Using default configuration...")
        return get_default_config()

def get_default_config():
    """Default configuration with complete logistics parameters"""
    return {
        'simulation': {
            'duration_hours': 168,
            'random_seed': 42
        },
        'order_arrival': {
            'interarrival_time_hours': 0.5
        },
        'parts_warehouse': {
            'initial_parts': 500,
            'capacity': 1000,
            'replenishment_interval_hours': 24,
            'replenishment_quantity': 500
        },
        'production_line': {
            'buffer_A_B_size': 10,
            'buffer_B_C_size': 10,
            'machines': [
                {'name': 'Machine A', 'processing_time_minutes': 5, 'mtbf_hours': 10, 'mttr_hours': 2},
                {'name': 'Machine B', 'processing_time_minutes': 7, 'mtbf_hours': 15, 'mttr_hours': 3},
                {'name': 'Machine C', 'processing_time_minutes': 4, 'mtbf_hours': 12, 'mttr_hours': 2.5}
            ]
        },
        'finished_storage': {
            'capacity': 50
        },
        'logistics': {
            'lorry_capacity': 20,
            'driver': {
                'car_issue_prob': 0.05,
                'issue_delay_hours': 4
            }
        }
    }

def main():
    """Main function"""
    print("=== Factory Production & Logistics Simulation ===")
    
    # Load configuration
    config = load_config()
    
    # Create and run simulation
    factory = FactorySimulation(config)
    results = factory.run()
    
    # Generate report
    print("\nGenerating analysis report...")
    generate_report(results, config)
    
    print("\nSimulation completed successfully!")
    print("Check 'results/' directory for output files.")

if __name__ == "__main__":
    main()