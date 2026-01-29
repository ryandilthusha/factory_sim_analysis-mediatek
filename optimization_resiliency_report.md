# Production Line Optimization & Resiliency Report

## 1. Executive Summary

This report presents the analysis and optimization of a factory production line simulation. The baseline analysis identified Machine B as the primary bottleneck with 52% utilization, causing upstream blocking and downstream starvation. Three key optimizations were implemented: reducing Machine B processing time from 7 to 6 minutes, increasing the buffer between Machine A and B from 5 to 10 units, and expanding finished goods storage from 30 to 50 units. These changes resulted in an 11% increase in throughput (4.44 to 4.94 orders/hour) and a 31% reduction in average lead time (28.8 to 20.0 hours). The optimized configuration demonstrates improved flow stability and balanced machine utilization. However, Machine B remains the system bottleneck, and the recommendation includes safety margins to handle variability. Confidence level is moderate-high, with the understanding that real-world factors such as quality defects, operator behavior, and supply chain variability are not fully captured in the simulation.

---

## 2. Baseline Analysis

### 2.1. KPI Measurements from Initial Run

| KPI | Baseline Value |
|-----|----------------|
| Throughput | 4.44 orders/hour |
| Average Lead Time | 28.80 hours |
| Machine A Utilization | 37.4% |
| Machine B Utilization | 52.0% |
| Machine C Utilization | 29.6% |
| Buffer A → B (avg / max) | 4.59 / 5 |
| Buffer B → C (avg / max) | 0.42 / 5 |
| Average Warehouse Inventory | 389 parts |
| Average Warehouse Wait Time | 0.0 hours |

### 2.2. Identified Bottlenecks with Evidence

#### Primary Bottleneck: Machine B

The primary bottleneck in the production line is **Machine B**.

#### Secondary Constraints Analysis

**1. Buffer Constraints Around Machine B**

The buffers around Machine B are quite tight. The buffer between Machine A and Machine B has an average level of about 4.6 items, with a maximum of 5, which means it is often close to full. This shows that items frequently wait before reaching Machine B. This supports the fact that Machine B cannot process items as fast as they arrive. When this buffer fills up Machine A is forced to wait. This increases idle time of Machine A.

**2. Machine C Starvation**

At the same time Machine C has much lower utilization compared to Machine B. In the baseline results, Machine C utilization is only about 29%, compared to 52% for Machine B. This indicates that Machine C is often waiting for items to arrive rather than being busy processing them. In other words, Machine C is starving because Machine B cannot supply it fast enough. This further confirms that the bottleneck is Machine B.

**3. System Load with Machine Failures**

Another contributing factor is the overall system load with machine failures. Orders arrive roughly every 0.15 hours (9 min), which keeps the system busy. Even though machine failures are not highly frequent (43 failures and 42 repairs over the simulation period), they still introduce variability. Because Machine B is already heavily utilized. So even short breakdowns can quickly create queues and increase waiting times across the line.

**4. Warehouse and Logistics (Not Limiting Factors)**

Finally, the warehouse and logistics do not appear to be limiting factors in the baseline scenario. The average warehouse inventory is high (around 389 parts) and the average warehouse wait time is 0.0. This means production is never blocked due to missing parts. Similarly, logistics operates mostly as expected. The lorry always leaves full (20 products per shipment) and delays are rare (delay rate 2.7% with only one car issue event). These factors may cause low probable delays, but they do not significantly limit throughput compared to the production bottleneck.

#### Summary of Bottleneck Analysis

- Machine B is the bottleneck (52% utilization)
- Buffer A→B is often near full (avg 4.6 / max 5)
- Machine C is starved (29%)
- Warehouse and logistics are NOT the problem

---

## 3. Optimization Strategy

### 3.1. Change 1: Reduce Machine B Processing Time (Primary Fix)

**Configuration Change:**
```yaml
Machine B:
  processing_time_minutes: 7 → 6
```

**Why This Helps:**
- Since the Machine B is the bottleneck
- By reducing its processing time:
  - Machine B can finish items faster
  - Overall throughput increases
  - Lead time decreases

**Trade-off:**
- Making a machine faster usually costs something (energy and resources) in real life.

---

### 3.2. Change 2: Increase Buffer Before Machine B (Flow Stabilization)

**Configuration Change:**
```yaml
production_line:
  buffer_A_B_size: 5 → 10
```

**Why This Helps:**
- Since in baseline results the Buffer A→B is often full
- When it's full, Machine A has to stop and wait
- Increasing it reduces blocking of Machine A

**Trade-off:**
- More items are waiting in the queue at the same time

---

### 3.3. Change 3: Increase Finished Goods Storage (Avoid Blocking)

**Configuration Change:**
```yaml
finished_storage:
  capacity: 30 → 50
```

**Why This Helps:**
- Prevents Machine C from blocking when shipping is delayed
- Fewer production stops due to logistics issues

**Trade-off:**
- More space required
- Storing more finished products has a cost.

---

## 4. Results Comparison

### 4.1. Side-by-Side KPI Comparison (Baseline vs Optimized)

| KPI | Baseline | Optimized | Change |
|-----|----------|-----------|--------|
| Throughput | 4.44 orders/hour | 4.94 orders/hour | **+11%** |
| Average Lead Time | 28.80 hours | 20.00 hours | **-31%** |
| Machine A Utilization | 37.4% | 42.1% | +4.7% |
| Machine B Utilization | 52.0% | 49.8% | -2.2% |
| Machine C Utilization | 29.6% | 33.0% | +3.4% |
| Buffer A → B (avg / max) | 4.59 / 5 | 7.43 / 10 | Less blocking |
| Buffer B → C (avg / max) | 0.42 / 5 | 0.27 / 5 | Still bottleneck |
| Average Warehouse Inventory | 389 parts | 354 parts | -35 parts reduced |
| Average Warehouse Wait Time | 0.0 hours | 0.0 hours | No change |

### 4.2. Analysis of Improvements

The optimized configuration increases throughput and significantly reduces average lead time and this is a good sign.

And main thing is this has lowered the utilization pressure on the primary bottleneck Machine B. And also significantly increased machine A and C utilization pressure which also good. As per my point of view, having nearly 50% of utilization pressure on each machine is ideal. Not too greater or lower makes negative impact.

Seems like increased buffering before Machine B has improved flow stability and allowed the 3 machines to operate more efficiently.

### 4.3. Summary of KPI Improvements

- **Throughput:** increased from 4.44 to 4.94 orders/hour (+11%).
- **Average lead time:** decreased from 28.8 to 20.0 hours (−31%).
- **Machine B utilization:** decreased from 52.0% to 49.8%. This reduced bottleneck pressure.
- **Machine C utilization:** increased 29.6% to 33.0%. This improves downstream flow.
- **Warehouse wait time:** remained at 0. This confirms that material availability is still sufficient.

So this new optimized configuration produces more output in less time with better balanced machine utilization.

---

## 5. Resiliency Assessment ⚠️

### 5.1. Model Assumptions and Limitations

#### Assumption 1: Perfect Quality Conditions Without Unexpectations

The simulation assumes that every item produced is correct and ready to ship. Which means this model assumes there are no defects, inspections, rework or scrapped products. In a real factory, this is rarely the case. Some products may fail quality checks and need to be reworked or discarded. This would require additional processing time, extra machine usage and possibly repeated passes through the production line. As a result, real-world throughput would be lower and lead times would be longer than what the simulation predicts.

#### Assumption 2: Constant Processing Times

The model assumes that each machine always takes the same amount of time to process an item. For example, Machine B always processes one item in exactly the same number of minutes (Optimised Machine B always takes 6 minutes). In reality, processing times vary. This is because differences in operator experience, machine condition, tool wear, setup adjustments or material quality can all cause tasks to take longer or shorter than expected. This variability can lead to unexpected queues, idle time and higher lead time variability, which are not fully captured by the simulation.

#### Assumption 3: Single-Product, Single-Routing Flow

The simulation model assume there are only one product type and it always follows the same fixed sequence of machines (Machine A → Machine B → Machine C). In real factories, there are multiple product types and they are often produced at the same time. Different products may require different processing steps or machine setups. Changeovers between products can also introduce downtime. These factors increase complexity and can significantly affect machine utilization and overall performance, which are not represented in the simulation.

---

### 5.2. Stress Test Results or Analysis

#### Scenario 1: Machine Failures Occur 50% More Frequently

If machine failures happened 50% more often the system would experience more interruptions. The increased buffer between Machine A and Machine B (from 5 to 10) would help absorb short breakdowns by allowing Machine A to continue producing items even when Machine B is temporarily unavailable. This reduces immediate upstream blocking and helps maintain smoother flow.

However, Machine B would still remain the primary bottleneck. With more frequent or longer failures at this B machine results queues in front of Machine B which cause longer waiting times and higher lead times. Throughput would decrease because the most critical resource in the system is unavailable more often.

And also preventive maintenance strategies could be considered to reduce failure frequency. For example we can do that by reducing processing time further. Or we can add parallel machines (adding another Machine B) would be ideal to maintain acceptable performance.

#### Scenario 2: Demand Increases by 30%

If a sudden 30% increase in demand would push the system much closer to its capacity limits. Even though the optimized configuration improves flow and slightly reduces bottleneck pressure, Machine B would again become highly utilized. As demand approaches or exceeds Machine B's processing capacity, items would start to queue in front of it, then increases the lead times.

This scenario shows that while the current optimization improves performance under normal conditions, it does not eliminate the primary capacity limitation at the bottleneck.

To handle sustained demand growth, as mentioned above the configuration would need to be adjusted by increasing capacity at Machine B. Such as further reducing its processing time or introducing additional parallel capacity (another machine) in a real world setting.

#### Scenario 3: Parts Replenishment is Delayed by 12 Hours

If parts replenishment were delayed by 12 hours, the warehouse inventory would temporarily decrease. In the optimized configuration, still the average warehouse inventory remains relatively high. This allows short replenishment delays to be absorbed without immediately stopping production.

However, if the delay lasted longer or occurred repeatedly, the warehouse could eventually run out of parts. In that case, production would stop regardless of machine capacity or buffer sizes, as no work can proceed without raw materials.

This can be handled by raising initial inventory levels or replenishment quantities. Additionally, reducing replenishment intervals would help ensure continuous production during extended supply disruptions.

---

### 5.3. Identified Risks and Mitigations (Single Points of Failure)

#### Risk 1: Lorry Breakdown for an Extended Period

If the lorry breaks down and is unavailable for an extended period, finished products would start to gather in the finished goods storage. Once this storage becomes full, Machine C would no longer be able to completed items forward and would be forced to stop. As a result, production would eventually halt even though Machines A and B may still be capable of working.

This shows that logistics is a single point of failure for the entire system. Even though shipping issues are rare, a long disruption can completely stop production.

**Possible Mitigation:**
We can increase finished goods storage provides some protection. If possible this issue can be prevented by having backup transport options.

#### Risk 2: Major Machine Repair (24+ Hours)

The impact depends on which machine fails. A long breakdown of Machine B would have the most severe effect because it is the primary bottleneck. During this downtime, queues would quickly build up in front of Machine B and throughput would drop significantly.

Even with larger buffers, extended downtime at the bottleneck would result in long lead times and reduced system throughput. This cause downstream machines would be starved and upstream machines would eventually block.

**Possible Mitigation:**
Having preventive maintenance and faster repair strategies would be necessary in the real world setting. And also as mentioned, adding parallel machines at the bottleneck machine would reduce the risk.

#### Risk 3: Warehouse Running Out of Parts

The production would stop entirely. Machines cannot process items without materials. So even perfectly functioning machines and buffers would not prevent downtime. This highlights the warehouse raw materials as a critical dependency.

**Possible Mitigation:**
This can be handled by raising initial inventory levels or replenishment quantities. Additionally, reducing replenishment intervals would help ensure continuous production during extended supply disruptions. Having alternative suppliers would help reduce the risk of production stoppages.

---

### 5.4. Safety Margins in Your Design

#### Safety Margin 1: Increased Buffer Before the Bottleneck (Machine A → Machine B)

The buffer capacity between Machine A and Machine B was increased from 5 to 10. This buffer acts as a safety margin that absorbs short term variability caused by machine failures or processing time differences or temporary slowdowns at Machine B. And also with that, Machine A blocking is reduced and the overall flow becomes smoother.

This safety margin helps prevent frequent blocking behavior in the production line.

#### Safety Margin 2: Reduced Utilization Pressure at the Bottleneck Machine B

By reducing the processing time of Machine B, its utilization was slightly lowered compared to the baseline. Having some unused capacity at the bottleneck machine B allows the system to better handle variabilities. Such as short failures or demand variations or unexpected maintenances.

#### Safety Margin 3: Increased Finished Items Storage Capacity

Finished goods storage capacity was increased from 30 to 50 units. This provides a safety margin against logistics disruptions. Such as delayed truck or temporary vehicle issues. And also with more storage space, Machine C can continue operating even when shipping is interrupted. So, this helps to reduce the risk of blocking the downstream machines.

---

### 5.5. Real-World Gaps (Factors Not Modeled)

#### Gap 1: Operator Shifts, Breaks, and Fatigue

The simulation assumes that machines are always available and operate continuously without considering human operators. In a real factory, operators work in shifts, take breaks and may experience fatigue over time. These factors can reduce effective machine availability and slow down production.

#### Gap 2: Preventive Maintenance Schedules

The model only includes random failures and repairs only. But this doesn't consider planned preventive maintenance. In reality, machines are often taken offline intentionally for servicing and maintenance. So this also reduces machine availability and production.

#### Gap 3: Quality Inspections and Defect Rates

The simulation assumes perfect production with no defective items. But in real factories, products are often inspected and some may require rework or scrapping. Rework increases machine workload and lead time, while scrapped items reduce effective throughput.

#### Gap 4: Supply Chain Variability Beyond Fixed Replenishment Intervals

The model assumes parts arrive at fixed intervals and in fixed quantities. In reality, suppliers may deliver late, early, or in partial quantities due to transportation issues, supplier capacity limits or external factors. Hence, variability in supply could lead to unexpected material shortages, machine lead time and throughput and increase average warehouse wait time.

#### Gap 5: Human Decision-Making and Prioritization Rules

The simulation follows fixed, rule-based logic for processing and shipping items. In real factories, human decisions such as prioritizing urgent orders, changing schedules or responding to unexpected events can significantly affect system behavior. These decisions may improve or worsen performance depending on how they are made, introducing additional variability not captured by the simulation.

---

## 6. Recommendations

### 6.1. Final Recommended Configuration

#### Recommendation 1: Reduction of Processing Time at Machine B (Primary Improvement)

**Change:**
Machine B processing time was reduced from 7 minutes to 6 minutes.

**Justification:**
Machine B was identified as the primary bottleneck in the system. By reducing its processing time, Machine B can process items faster. This directly increases throughput and reduces the queue of items waiting in front of it. This change improves overall system performance by addressing the most limiting resource in the production line.

#### Recommendation 2: Increase of Buffer Capacity Before Machine B

**Change:**
Buffer capacity between Machine A and Machine B was increased from 5 to 10.

**Justification:**
In the baseline configuration, the buffer before Machine B was often full. This cause Machine A to block and stop producing in different situations. Increasing this buffer allows more items to wait safely before the bottleneck, reducing machine A blocking and smoothing the production flow. This change improves the flow, especially during short machine failures or processing variability.

#### Recommendation 3: Increase of Finished Goods Storage Capacity

**Change:**
Finished goods storage capacity was increased from 30 to 50 units.

**Justification:**
This change reduces the risk of Machine C blocking during shipping delays. With more storage available, finished products can gather more temporarily without stopping production. This adds resilience against logistics disruptions and helps maintain steady output even when shipments are delayed.

---

### 6.2. Limitations and Risks of the Recommendation

#### Limitation 1: Bottleneck Still Exists at Machine B

Although the processing time of Machine B was reduced, it remains the primary bottleneck in the system. This means that large increases in demand or extended failures at this machine could still cause significant queues and long lead times. The optimization reduces bottleneck pressure but does not completely remove the system's dependency on Machine B.

#### Limitation 2: Increased Work-in-Progress and Inventory Levels

Increasing buffer sizes and finished goods storage improves stability, but it also leads to higher levels of work-in-progress and inventory. In a real factory, this can increase holding costs, require additional space and make it harder to detect production problems early. If buffers are increased too much, they may hide inefficiencies rather than solve them.

#### Limitation 3: Higher Cost and Operational Effort

Reducing the processing time of Machine B may require additional investment in better tooling, operator training or higher energy usage. These costs are not represented in the simulation but would need to be justified in a real implementation. The economic benefit of improved throughput must exceed these additional expenses.

#### Limitation 4: Sensitivity to External Disruption Events

The optimized configuration improves robustness against short disruptions, but it is still sensitive to major external events. Extended machine failures, long logistics disruptions, or severe supply chain delays can still stop production entirely. These risks highlight the importance of backup plans and contingency strategies.

#### Limitation 5: Simplified Model Assumptions

The recommendation is based on a simplified simulation that does not include factors such as quality defects, operator or human behavior, multi-product flows, or complex scheduling decisions. These real world factors could reduce the effectiveness of the optimized configuration or introduce new bottlenecks that are not visible in the model.

---

### 6.3. Implementation Considerations for a Real Factory

#### Step 1: Start with the Bottleneck Improvement

Implementation should begin by focusing on Machine B, as it is the primary bottleneck. Improvements such as tooling upgrades, operator training or process optimization should be tested gradually rather than all at once. This allows monitor performance and identify bottlenecks while minimizing operational risk.

#### Step 2: Apply Buffer Changes Gradually

Increased buffer capacity improves stability, but buffers should not be expanded too aggressively. It is recommended to increase buffer sizes in small steps and monitor lead times and machine utilization. This helps ensure that buffers improve flow without causing excessive inventory buildup.

#### Step 3: Monitor Key Performance Indicators (KPIs) Continuously

After implementation, key KPIs such as throughput, lead time, machine utilization and buffer levels should be monitored regularly. Continuous monitoring helps detect new bottlenecks early. So then we can ensure the performance improvements are sustained over time.

#### Step 4: Prepare for Logistics and Supply Variability

Finished goods storage and logistics processes should be reviewed to ensure they can handle temporary disruptions. Backup transport options, having flexible shipment schedules or additional storage capacity can help prevent production stoppages caused by shipping delays and issues.

#### Step 5: Strengthen Preventive Maintenance Plans

Having preventive maintenance and faster repair strategies would be necessary in the real world setting. And also adding parallel machines at the bottleneck machine would reduce risks.

#### Step 6: Validate Through Pilot Runs and Reviews

Before full scale deployment, the optimized configuration should be tested through pilot runs or limited production periods. Feedbacks from operators and supervisors should be included and the configuration should be adjusted if unexpected issues arise.

---

### 6.4. Monitoring Suggestions for Production Use

| What to Monitor | How Often | Why This Matters |
|-----------------|-----------|------------------|
| Throughput (orders per hour) | Every hour | To see if the factory is producing at the expected speed |
| Average Lead Time | Once per day | To check how long orders take from start to finish |
| Longest / Variable Lead Time | Once per day | To spot instability or growing queues in the system |
| Machine Utilization (especially Machine B) | Real-time | To see which machine is overloaded and becoming the bottleneck |
| Buffer Levels (A → B, B → C) | Real-time | To detect blocking (too full) or starvation (too empty) |
| Warehouse Inventory | Every shift | To make sure enough parts are available for production |
| Parts Replenishment Delays | Every delivery | To catch supply problems early before production stops |
| Machine Downtime | Every time it happens | To understand reliability problems and maintenance needs |
| Shipment Delays | Every shipment | To monitor transport issues that could block production |

---

## Appendix: Configuration Files Summary

### Baseline Configuration (`config.yaml`)

| Parameter | Value |
|-----------|-------|
| Machine B Processing Time | 7 minutes |
| Buffer A→B Size | 5 |
| Buffer B→C Size | 5 |
| Finished Storage Capacity | 30 |
| Warehouse Capacity | 500 |
| Replenishment Interval | 12 hours |
| Replenishment Quantity | 100 parts |
| Lorry Capacity | 20 products |

### Optimized Configuration (`config_optimized.yaml`)

| Parameter | Baseline | Optimized | Change |
|-----------|----------|-----------|--------|
| Machine B Processing Time | 7 min | 6 min | -1 min |
| Buffer A→B Size | 5 | 10 | +5 |
| Buffer B→C Size | 5 | 5 | No change |
| Finished Storage Capacity | 30 | 50 | +20 |

---

*Report generated based on simulation analysis of a 168-hour (1 week) production run.*
