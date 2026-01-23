"""
Reporting Module - Generate analysis reports and visualizations
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
from typing import Dict, Any
import json
import numpy as np

def generate_report(results: Dict[str, Any], config: Dict[str, Any]):
    """Generate comprehensive analysis report"""
    
    # Create results directory
    os.makedirs('results', exist_ok=True)
    
    # Get data
    events_df = results.get('events_df', pd.DataFrame())
    
    if events_df.empty:
        print("No data to analyze!")
        return
    
    # Calculate KPIs
    from analysis.data_collector import DataCollector
    collector = DataCollector()
    collector.events = results['events']
    collector.metrics = results['metrics']
    kpis = collector.calculate_kpis()
    summary_stats = collector.get_summary_stats()
    
    # Generate text report
    generate_text_report(kpis, summary_stats, config)
    
    # Generate visualizations
    generate_visualizations(events_df, kpis)
    
    # Save raw data
    save_raw_data(results, kpis, summary_stats)
    
    print("Report generation completed!")

def generate_text_report(kpis: Dict[str, float], summary_stats: Dict[str, Any], 
                        config: Dict[str, Any]):
    """Generate text-based analysis report"""
    
    report_lines = []
    report_lines.append("# Factory Simulation Analysis Report")
    report_lines.append("=" * 50)
    report_lines.append("")
    
    # Configuration summary
    report_lines.append("## Configuration Summary")
    report_lines.append(f"- Simulation Duration: {config['simulation']['duration_hours']} hours")
    report_lines.append(f"- Order Arrival Rate: {config['order_arrival']['interarrival_time_hours']} hours")
    report_lines.append(f"- Warehouse Capacity: {config['parts_warehouse']['capacity']} parts")
    report_lines.append(f"- Lorry Capacity: {config['logistics']['lorry_capacity']} products")
    report_lines.append("")
    
    # Key Performance Indicators
    report_lines.append("## Key Performance Indicators")
    report_lines.append("")
    
    if 'throughput_orders_per_hour' in kpis:
        report_lines.append(f"### Production Performance")
        report_lines.append(f"- **Throughput**: {kpis['throughput_orders_per_hour']:.2f} orders/hour")
        
        if 'average_lead_time_hours' in kpis:
            report_lines.append(f"- **Average Lead Time**: {kpis['average_lead_time_hours']:.2f} hours")
            report_lines.append(f"- **Min Lead Time**: {kpis['min_lead_time_hours']:.2f} hours")
            report_lines.append(f"- **Max Lead Time**: {kpis['max_lead_time_hours']:.2f} hours")
        report_lines.append("")
    
    # Machine utilization
    report_lines.append("### Machine Utilization")
    for key, value in kpis.items():
        if 'utilization' in key:
            machine_name = key.replace('_utilization', '').replace('_', ' ').title()
            report_lines.append(f"- **{machine_name}**: {value:.1%}")
    report_lines.append("")
    
    # Buffer and Inventory
    report_lines.append("### Inventory & Buffers")
    if 'average_warehouse_inventory' in kpis:
        report_lines.append(f"- **Avg Warehouse Inventory**: {kpis['average_warehouse_inventory']:.1f} parts")
    
    # Group buffer stats
    buffers = set()
    for key in kpis:
        if key.startswith('average_buffer_') or key.startswith('max_buffer_'):
            buffers.add(key.replace('average_', '').replace('max_', '').replace('_level', ''))
    
    for buf in sorted(list(buffers)):
        avg_val = kpis.get(f'average_{buf}_level', 0)
        max_val = kpis.get(f'max_{buf}_level', 0)
        buf_name = buf.replace('_', ' ').title()
        report_lines.append(f"- **{buf_name}**: Avg: {avg_val:.2f}, Max: {max_val:.0f}")
    report_lines.append("")

    # Logistics performance
    if 'total_shipments' in kpis:
        report_lines.append("### Logistics Performance")
        report_lines.append(f"- **Total Shipments**: {kpis['total_shipments']}")
        report_lines.append(f"- **Products Shipped**: {kpis['total_products_shipped']}")
        report_lines.append(f"- **Avg Products/Shipment**: {kpis['average_products_per_shipment']:.1f}")
        
        if 'delay_rate' in kpis:
            report_lines.append(f"- **Delay Rate**: {kpis['delay_rate']:.1%}")
            if 'average_delay_time_hours' in kpis:
                report_lines.append(f"- **Average Delay**: {kpis['average_delay_time_hours']:.2f} hours")
        report_lines.append("")
    
    # Bottleneck analysis
    report_lines.append("## Bottleneck Analysis")
    report_lines.append("")
    
    # Find lowest utilization machine
    utilizations = {k: v for k, v in kpis.items() if 'utilization' in k}
    if utilizations:
        min_util_machine = min(utilizations.items(), key=lambda x: x[1])
        max_util_machine = max(utilizations.items(), key=lambda x: x[1])
        
        report_lines.append(f"- **Highest Utilization**: {max_util_machine[0].replace('_', ' ').title()} ({max_util_machine[1]:.1%})")
        report_lines.append(f"- **Lowest Utilization**: {min_util_machine[0].replace('_', ' ').title()} ({min_util_machine[1]:.1%})")
        
        if max_util_machine[1] > 0.8:
            report_lines.append(f"- **Warning**: {max_util_machine[0].replace('_', ' ').title()} is highly utilized and may be a bottleneck")
    
        report_lines.append("")
        
        # Recommendations
        report_lines.append("## Recommendations")
        report_lines.append("")
        
        if max_util_machine[1] > 0.85:
            report_lines.append(f"1. Consider adding capacity to {max_util_machine[0].replace('_', ' ').title()}")
        
        if 'delay_rate' in kpis and kpis['delay_rate'] > 0.1:
            report_lines.append("2. Consider backup transportation or preventive maintenance for lorry")
        
        if 'average_warehouse_wait_time' in kpis and kpis['average_warehouse_wait_time'] > 0.1:
            report_lines.append("3. Consider increasing warehouse replenishment frequency")
    
    # Write report to file
    with open('results/analysis_report.md', 'w') as f:
        f.write('\n'.join(report_lines))

def generate_visualizations(events_df: pd.DataFrame, kpis: Dict[str, float]):
    """Generate visualization plots"""
    
    plt.style.use('seaborn-v0_8')
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Factory Simulation Analysis', fontsize=16)
    
    # 1. Order arrivals over time
    order_arrivals = events_df[events_df['event_type'] == 'order_arrival']
    if not order_arrivals.empty:
        axes[0, 0].hist(order_arrivals['timestamp'], bins=20, alpha=0.7, color='blue')
        axes[0, 0].set_title('Order Arrivals Over Time')
        axes[0, 0].set_xlabel('Time (hours)')
        axes[0, 0].set_ylabel('Number of Orders')
    
    # 2. Machine utilization
    utilizations = {k.replace('_utilization', '').replace('_', ' ').title(): v 
                   for k, v in kpis.items() if 'utilization' in k}
    if utilizations:
        machines = list(utilizations.keys())
        utils = list(utilizations.values())
        axes[0, 1].bar(machines, utils, color=['red', 'green', 'blue'])
        axes[0, 1].set_title('Machine Utilization')
        axes[0, 1].set_ylabel('Utilization Rate')
        axes[0, 1].set_ylim(0, 1)
        for i, v in enumerate(utils):
            axes[0, 1].text(i, v + 0.01, f'{v:.1%}', ha='center')
    
    # 3. Lead time distribution
    order_completions = events_df[events_df['event_type'] == 'order_completed']
    order_arrivals = events_df[events_df['event_type'] == 'order_arrival']
    
    if not order_completions.empty and not order_arrivals.empty:
        lead_times = []
        for _, completion in order_completions.iterrows():
            order_id = completion['order_id']
            arrival = order_arrivals[order_arrivals['order_id'] == order_id]
            if not arrival.empty:
                lead_time = completion['timestamp'] - arrival.iloc[0]['timestamp']
                lead_times.append(lead_time)
        
        if lead_times:
            axes[1, 0].hist(lead_times, bins=15, alpha=0.7, color='orange')
            axes[1, 0].set_title('Lead Time Distribution')
            axes[1, 0].set_xlabel('Lead Time (hours)')
            axes[1, 0].set_ylabel('Frequency')
    
    # 4. Logistics performance
    departures = events_df[events_df['event_type'] == 'lorry_departure']
    if not departures.empty:
        # Products shipped over time
        cumulative_products = departures['products_shipped'].cumsum()
        axes[1, 1].plot(departures['departure_time'], cumulative_products, marker='o')
        axes[1, 1].set_title('Cumulative Products Shipped')
        axes[1, 1].set_xlabel('Time (hours)')
        axes[1, 1].set_ylabel('Total Products Shipped')
    
    plt.tight_layout()
    plt.savefig('results/simulation_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Additional plot: Timeline of events
    plt.figure(figsize=(12, 8))
    
    event_types = events_df['event_type'].unique()
    
    # Use a standard colormap name
    cmap = plt.get_cmap('Set3')
    colors = [cmap(i % 12) for i in range(len(event_types))]
    
    for i, event_type in enumerate(event_types):
        event_data = events_df[events_df['event_type'] == event_type]
        plt.scatter(event_data['timestamp'], [i] * len(event_data), 
                   alpha=0.6, label=event_type, color=colors[i])
    
    plt.xlabel('Time (hours)')
    plt.ylabel('Event Type')
    plt.title('Simulation Events Timeline')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('results/events_timeline.png', dpi=300, bbox_inches='tight')
    plt.close()

class NpEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super(NpEncoder, self).default(o)

def save_raw_data(results: Dict[str, Any], kpis: Dict[str, float], 
                 summary_stats: Dict[str, Any]):
    """Save raw data to files"""
    
    # Save events to CSV
    events_df = results.get('events_df', pd.DataFrame())
    if not events_df.empty:
        events_df.to_csv('results/simulation_events.csv', index=False)
    
    # Save KPIs to JSON
    with open('results/kpis.json', 'w') as f:
        json.dump(kpis, f, indent=2, cls=NpEncoder)
    
    # Save summary statistics
    with open('results/summary_stats.json', 'w') as f:
        # Convert any non-serializable objects
        serializable_stats = {}
        for key, value in summary_stats.items():
            if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
                serializable_stats[key] = value
            else:
                serializable_stats[key] = str(value)
        
        json.dump(serializable_stats, f, indent=2, cls=NpEncoder)
    
    print("Raw data saved to results/ directory")