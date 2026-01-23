# Assignment: Production Line Optimization & Resiliency Challenge

## 1. Objective

Your task is to **optimize and validate a factory production line** using Discrete Event Simulation (DES). You will be provided with a baseline simulation built with Python and SimPy. Your goal is to:

1. **Understand** the existing production line simulation
2. **Measure** the baseline performance using Key Performance Indicators (KPIs)
3. **Analyze** bottlenecks and inefficiencies
4. **Optimize** the configuration to improve throughput and efficiency
5. **Validate** your optimizations under realistic conditions
6. **Assess** the resiliency of your proposed configuration

## 2. Scenario Description

You are given a factory simulation with the following components:

### 2.1. Order Arrival
- Customer orders arrive following an **Exponential distribution**
- Orders trigger the production process

### 2.2. Parts Warehouse
- Raw parts are stored in a warehouse with **finite capacity**
- Parts are replenished periodically (fixed interval and quantity)
- Production cannot proceed without available parts

### 2.3. Production Line
The line has three sequential machines: **Machine A → Machine B → Machine C**

- Each machine processes one item at a time
- Each machine has a specific **processing time**
- Machines are subject to **failures** (MTBF - Mean Time Between Failures)
- Failed machines require **repair time** (MTTR - Mean Time To Repair)
- **Buffer space between machines is limited** - if full, upstream machines must wait

### 2.4. Finished Products Storage
- Completed products are stored in a **limited capacity** storage area
- If storage is full, Machine C must wait to offload

### 2.5. Logistics
- A lorry driver ships finished products
- The lorry has a **fixed capacity** and departs only when full
- The driver may experience **vehicle issues** (stochastic delays)

## 3. Your Tasks

### Phase 1: Baseline Measurement (Required)
1. Run the simulation with the provided baseline configuration (`config.yaml`)
2. Collect and document the following KPIs:
   - **Throughput**: Products completed per hour
   - **Lead Time**: Average time from order arrival to completion
   - **Machine Utilization**: % time each machine is busy vs idle vs broken
   - **Buffer Utilization**: Average and maximum queue lengths
   - **Warehouse Stock Levels**: Average parts availability

### Phase 2: Bottleneck Analysis (Required)
1. Identify the **primary bottleneck** in the production line
2. Analyze **secondary constraints** that limit throughput
3. Document your findings with supporting data from the simulation

### Phase 3: Optimization (Required)
1. Propose **at least 3 configuration changes** to improve performance
2. For each change, explain:
   - What parameter(s) you are modifying
   - Why you expect this to improve performance
   - The trade-offs involved
3. Run simulations with your optimized configuration(s)
4. Compare results against the baseline

### Phase 4: Resiliency Assessment (Required) ⚠️

**Critical:** A simulation is a simplified model of reality. Before recommending your optimized configuration for real-world implementation, you must assess its **robustness**.

Answer the following questions:

1. **Model Assumptions**: What assumptions does the simulation make that may not hold in a real factory? List at least 3 significant assumptions.

2. **Stress Testing**: How would your optimized configuration perform if:
   - Machine failures occurred 50% more frequently?
   - Demand suddenly increased by 30%?
   - Parts replenishment was delayed by 12 hours?

3. **Single Points of Failure**: What happens if critical components fail? Consider:
   - The lorry breaks down for an extended period
   - A machine requires major repair (24+ hours)
   - The warehouse runs out of parts

4. **Safety Margins**: What buffers or safety margins have you built into your recommendation? Why?

5. **Real-World Gaps**: What factors present in a real factory are **not modeled** in this simulation? How might these affect your optimization?

### Phase 5: Final Recommendation (Required)
1. Present your **recommended configuration** with justification
2. Show the **improvement in KPIs** compared to baseline
3. Discuss the **limitations and risks** of your recommendation
4. Provide **implementation guidance** for a real factory

## 4. Provided Materials

You will receive:
- Complete Python/SimPy simulation code in `simulation/`
- Baseline `config.yaml` with initial parameters
- Instructions for running the simulation in `README.md`
- Optimization guide in `OPTIMIZATION_GUIDE.md`

## 5. Configuration Parameters You Can Modify

| Category | Parameter | Description |
|----------|-----------|-------------|
| Warehouse | `initial_parts` | Starting inventory |
| Warehouse | `capacity` | Maximum storage capacity |
| Warehouse | `replenishment_interval_hours` | How often parts arrive |
| Warehouse | `replenishment_quantity` | How many parts per delivery |
| Production | `buffer_A_B_size` | Queue capacity between A and B |
| Production | `buffer_B_C_size` | Queue capacity between B and C |
| Production | `processing_time_minutes` | Time per item (per machine) |
| Storage | `capacity` | Finished goods storage limit |
| Logistics | `lorry_capacity` | Products per shipment |

**Note:** You cannot modify machine reliability parameters (MTBF/MTTR) as these represent fixed equipment characteristics.

## 6. Deliverables

### 6.1. Optimization & Resiliency Report (Markdown or PDF)
Your report should include:

1. **Executive Summary** (1 paragraph)
   - Key findings, recommended configuration, and confidence level

2. **Baseline Analysis**
   - KPI measurements from initial run
   - Identified bottlenecks with evidence

3. **Optimization Strategy**
   - Each proposed change with rationale
   - Expected impact analysis

4. **Results Comparison**
   - Side-by-side KPI comparison (baseline vs optimized)
   - Visualization of improvements

5. **Resiliency Assessment** ⚠️
   - Model assumptions and limitations
   - Stress test results or analysis
   - Identified risks and mitigations
   - Safety margins in your design

6. **Recommendations**
   - Final recommended configuration
   - Implementation considerations
   - Monitoring suggestions for production use

### 6.2. Configuration Files
- `config_baseline.yaml` - Original configuration (unchanged)
- `config_optimized.yaml` - Your optimized configuration

### 6.3. Simulation Output
- KPI data from baseline run
- KPI data from optimized run(s)
- Any stress test results

## 7. Evaluation Criteria

Your submission will be evaluated on:

| Criteria | Weight | Description |
|----------|--------|-------------|
| Analysis Quality | 30% | Depth of bottleneck analysis, data-driven insights |
| Optimization Effectiveness | 25% | Actual improvement in KPIs achieved |
| Resiliency Assessment | 25% | Understanding of model limitations, risk awareness |
| Reasoning & Justification | 10% | Clear explanation of choices |
| Report Quality | 10% | Clarity, structure, professionalism |

**Note:** A highly optimized configuration that ignores real-world risks will score lower than a moderately optimized configuration with strong resiliency analysis.

## 8. Getting Started

See the root `README.md` for installation and execution instructions.

## 9. Important Considerations

### Think Beyond the Simulation
The simulation is a **simplified model**. Real factories have:
- Shift changes and breaks
- Quality control and defects
- Supply chain variability
- Human factors (training, fatigue, communication)
- Unexpected events

**Ask yourself:** "What could go wrong that this simulation doesn't capture?"

### Balance Optimization with Robustness
- Tight optimization (minimal buffers, just-in-time) is efficient but fragile
- Robust systems have safety margins but may be less efficient
- The best solutions balance both

### Consider Implementation Reality
- Changes have costs (capital, time, disruption)
- Some changes are easier to implement than others
- Prioritize high-impact, low-risk improvements

## 10. Tips for Success

1. **Start with data**: Run the baseline simulation multiple times to understand variability
2. **Focus on bottlenecks**: The biggest gains come from addressing the primary constraint
3. **Consider trade-offs**: Larger buffers help throughput but increase work-in-progress
4. **Validate changes**: Test one change at a time to understand its impact
5. **Think holistically**: The production line is a system - changes affect the whole
6. **Question assumptions**: What does the simulation assume that reality doesn't guarantee?
7. **Build in margins**: Optimizations that work "just barely" will fail in practice

## 11. Time Allocation Suggestion

- Phase 1 (Baseline): 15% of your time
- Phase 2 (Analysis): 20% of your time
- Phase 3 (Optimization): 25% of your time
- Phase 4 (Resiliency): 25% of your time
- Phase 5 (Report): 15% of your time

## 12. Questions to Guide Your Thinking

As you work through this challenge, consider:

- What would happen on the worst day?
- Would you stake your reputation on these numbers?
- What's the first thing that would break in production?
- How would you explain the risks to a factory manager?
- What monitoring would you put in place?

Good luck! We look forward to seeing both your optimization skills and your practical engineering judgment.