# Week 1 — Spark Architecture

## Study Checklist
- [ ] Understand Driver vs Executor roles
- [ ] Understand what a DAG is and how Spark builds one
- [ ] Know the difference between transformation and action
- [ ] Know narrow vs wide transformations
- [ ] Understand what a shuffle is and why it's expensive

## Key Concepts

### Spark Architecture
```
Driver Program
  ├── SparkContext / SparkSession
  ├── Builds DAG (logical plan)
  ├── Schedules tasks on executors
  └── Collects results

Cluster Manager (YARN / Kubernetes / Databricks)
  └── Allocates resources

Executor (worker nodes)
  ├── Runs tasks
  ├── Stores data in memory/disk
  └── Reports back to driver
```

### DAG — Directed Acyclic Graph
- Spark builds a DAG from your transformations (lazy — nothing runs yet)
- When an action is called, the DAG is submitted to the cluster
- Spark optimizes the DAG using Catalyst optimizer

### Transformations vs Actions
| Type | Examples | Behavior |
|------|---------|---------|
| Transformation | filter, select, join, groupBy, map | Lazy — builds DAG |
| Action | show, count, collect, write, take | Triggers execution |

### Narrow vs Wide Transformations
| Type | Examples | Shuffle? |
|------|---------|---------|
| Narrow | filter, select, map, union | No shuffle — fast |
| Wide | groupBy, join, distinct, repartition | Shuffle — expensive |

### What is a Shuffle?
- Data moves between partitions/executors across the network
- Happens on wide transformations
- Most expensive operation in Spark — minimize where possible

### RDD vs DataFrame vs Dataset
| Type | Description | Use |
|------|------------|-----|
| RDD | Low-level, unstructured | Avoid unless necessary |
| DataFrame | Distributed table (rows + named columns) | Default — use this |
| Dataset | Typed DataFrame | Scala/Java only |

## Notes
_(Write your own notes here as you study)_
