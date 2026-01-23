# Production Line Optimization Challenge

Welcome to the Production Line Optimization Challenge!

## Quick Start

### 1. Install Dependencies
```bash
pip install simpy pyyaml pandas matplotlib
```

### 2. Run Baseline Simulation
```bash
cd simulation
python main.py
```

### 3. Review Results
Results are saved to `simulation/results/` directory:
- `analysis_report.md` - Summary report
- `kpis.json` - Key Performance Indicators
- `simulation_events.csv` - Detailed event log
- `simulation_analysis.png` - Visualization charts

### 4. Read the Assignment
See `ASSIGNMENT.md` for full instructions.

### 5. Optimize
1. Analyze the baseline results
2. Identify bottlenecks
3. Create `config_optimized.yaml` based on the template
4. Run simulation with your optimized config
5. Compare results

## Files in This Package

| File | Description |
|------|-------------|
| `ASSIGNMENT.md` | Full assignment instructions |
| `OPTIMIZATION_GUIDE.md` | Background knowledge and strategies |
| `config.yaml` | Baseline configuration (analyze this) |
| `config_optimized_template.yaml` | Template for your optimization |
| `simulation/` | The simulation code |

## Deliverables

1. **Optimization Report** (Markdown or PDF)
2. **config_optimized.yaml** - Your optimized configuration
3. **Simulation outputs** - KPI data from baseline and optimized runs

## Tips

1. Run the baseline simulation first
2. Identify the bottleneck before making changes
3. Test one change at a time
4. Consider real-world factors the simulation doesn't model
5. Build safety margins into your design

Good luck!