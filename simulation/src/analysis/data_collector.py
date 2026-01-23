"""
Data Collector - Collects simulation events and metrics
"""

import pandas as pd
from typing import Dict, List, Any
from collections import defaultdict

class DataCollector:
    """Collects and stores simulation data for analysis"""
    
    def __init__(self):
        self.events = []
        self.metrics = defaultdict(list)
        
    def record_event(self, event_type: str, data: Dict[str, Any]):
        """Record a simulation event"""
        event = {
            'event_type': event_type,
            'timestamp': data.get('time', 0),
            **data
        }
        self.events.append(event)
    
    def record_metric(self, metric_name: str, value: float, timestamp: float):
        """Record a metric value at a specific time"""
        self.metrics[metric_name].append({
            'timestamp': timestamp,
            'value': value
        })
    
    def get_events_df(self) -> pd.DataFrame:
        """Get events as pandas DataFrame"""
        if not self.events:
            return pd.DataFrame()
        return pd.DataFrame(self.events)
    
    def get_metrics_df(self, metric_name: str) -> pd.DataFrame:
        """Get specific metric as pandas DataFrame"""
        if metric_name not in self.metrics:
            return pd.DataFrame()
        return pd.DataFrame(self.metrics[metric_name])
    
    def get_results(self) -> Dict[str, Any]:
        """Get all collected data"""
        return {
            'events': self.events,
            'metrics': dict(self.metrics),
            'events_df': self.get_events_df()
        }
    
    def calculate_kpis(self) -> Dict[str, float]:
        """Calculate Key Performance Indicators"""
        df = self.get_events_df()
        
        if df.empty:
            return {}
        
        kpis = {}
        
        # Order-related KPIs
        order_arrivals = df[df['event_type'] == 'order_arrival']
        order_completions = df[df['event_type'] == 'order_completed']
        
        if not order_arrivals.empty and not order_completions.empty:
            # Throughput (orders per hour)
            simulation_duration = df['timestamp'].max()
            kpis['throughput_orders_per_hour'] = len(order_completions) / simulation_duration
            
            # Lead time calculation (for completed orders)
            lead_times = []
            for _, completion in order_completions.iterrows():
                order_id = completion['order_id']
                arrival = order_arrivals[order_arrivals['order_id'] == order_id]
                if not arrival.empty:
                    lead_time = completion['timestamp'] - arrival.iloc[0]['timestamp']
                    lead_times.append(lead_time)
            
            if lead_times:
                kpis['average_lead_time_hours'] = sum(lead_times) / len(lead_times)
                kpis['max_lead_time_hours'] = max(lead_times)
                kpis['min_lead_time_hours'] = min(lead_times)
        
        # Machine utilization
        machine_events = df[df['event_type'] == 'machine_processing']
        if not machine_events.empty:
            for machine_name in machine_events['machine'].unique():
                machine_data = machine_events[machine_events['machine'] == machine_name]
                total_processing_time = machine_data['processing_time'].sum()
                simulation_duration = df['timestamp'].max()
                utilization = total_processing_time / simulation_duration
                kpis[f'{machine_name.lower().replace(" ", "_")}_utilization'] = utilization
        
        # Logistics KPIs
        departures = df[df['event_type'] == 'lorry_departure']
        if not departures.empty:
            kpis['total_shipments'] = len(departures)
            kpis['total_products_shipped'] = departures['products_shipped'].sum()
            kpis['average_products_per_shipment'] = departures['products_shipped'].mean()
            
            # Delay analysis
            delays = departures[departures['delay_time'] > 0]
            kpis['delay_rate'] = len(delays) / len(departures)
            if not delays.empty:
                kpis['average_delay_time_hours'] = delays['delay_time'].mean()
        
        # Warehouse KPIs
        warehouse_gets = df[df['event_type'] == 'warehouse_get']
        if not warehouse_gets.empty:
            kpis['average_warehouse_wait_time'] = warehouse_gets['wait_time'].mean()
        
        # Average inventory level
        if 'warehouse_level' in self.metrics:
            inv_df = self.get_metrics_df('warehouse_level')
            kpis['average_warehouse_inventory'] = inv_df['value'].mean()
            
        # Buffer utilization
        for m_name in self.metrics:
            if m_name.startswith('buffer_'):
                buf_df = self.get_metrics_df(m_name)
                kpis[f'average_{m_name}_level'] = buf_df['value'].mean()
                kpis[f'max_{m_name}_level'] = buf_df['value'].max()

        return kpis
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        df = self.get_events_df()
        
        if df.empty:
            return {'total_events': 0}
        
        stats = {
            'total_events': len(df),
            'simulation_duration': df['timestamp'].max(),
            'event_types': df['event_type'].value_counts().to_dict(),
            'kpis': self.calculate_kpis()
        }
        
        return stats