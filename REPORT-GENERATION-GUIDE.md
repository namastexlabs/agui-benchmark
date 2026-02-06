# 📊 Automated Report Generation Guide

## Complete Workflow

### Step 1: Run the Full Benchmark
```bash
uv run python test_agents.py
```

This will:
- Run 609 tests (9 test types × 26-27 agents)
- Capture all AG-UI events
- Save JSON results to `benchmark-runs/TIMESTAMP/`

### Step 2: Auto-Generate Reports
```bash
python3 generate_reports.py
```

This will automatically generate 4 comprehensive markdown reports with matrices:

---

## 📋 Generated Reports

### 1. **EVENT-COVERAGE-MATRIX.md**
**26 Event Type × 26+ Agent Matrix**

| Feature | Details |
|---------|---------|
| Rows | All 26 AG-UI spec events |
| Columns | All agent implementations |
| Cells | ✅ (event emitted) or ❌ (not emitted) |
| Sections | Event coverage statistics by percentage |

**What it shows:**
- Which agents emit which events
- Event adoption rates across ecosystem
- High/Medium/Low coverage breakdown
- Quick visual overview of protocol compliance

---

### 2. **FRAMEWORK-COMPARISON-MATRIX.md**
**Framework Capabilities Comparison**

| Metric | Details |
|--------|---------|
| Performance | Median response time, throughput |
| Success Rate | % tests passing per framework |
| Streaming | Characters per second |
| Tool Calls | Number of tool invocations |
| Features | Streaming, Tools, State, Steps |

**What it shows:**
- Which frameworks are fastest
- Which are most reliable
- Feature support matrix (Tools, State, Streaming, etc.)
- Framework rankings by multiple metrics

---

### 3. **EVENT-TYPE-ANALYSIS.md**
**Detailed Event Type Breakdown**

| Section | Details |
|---------|---------|
| Event Coverage | % of agents supporting each event |
| By Category | Events grouped (Lifecycle, Text, Tools, etc.) |
| Statistics | Adoption rates, agent counts per event |

**What it shows:**
- Which events are widely adopted (100%)
- Which are rarely used (0-20%)
- Events grouped by semantic category
- Complete adoption statistics

---

### 4. **BENCHMARK-SUMMARY.md**
**Overall Benchmark Statistics**

| Section | Details |
|---------|---------|
| Overall Stats | Total agents, tests, success rate |
| Performance | Fastest/slowest tests, median times |
| Coverage | Total unique events, % of spec |
| Top Performers | 5 fastest agents, 5 best streaming |

**What it shows:**
- High-level project health metrics
- Performance extremes and medians
- Overall protocol coverage percentage
- Rankings of top performers

---

## 🚀 Complete Usage

```bash
# 1. Run full benchmark (takes 5-10 minutes)
uv run python test_agents.py

# 2. Generate all reports automatically
python3 generate_reports.py

# 3. View results
# All markdown files are generated in the current directory:
# - EVENT-COVERAGE-MATRIX.md
# - FRAMEWORK-COMPARISON-MATRIX.md
# - EVENT-TYPE-ANALYSIS.md
# - BENCHMARK-SUMMARY.md
```

---

## 📊 Matrix Features

### EVENT-COVERAGE-MATRIX.md Features
- ✅ 26×26 (event × agent) matrix
- ✅ Color-coded (✅ ❌)
- ✅ Coverage statistics
- ✅ Adoption breakdown by percentage

**Example row:**
```
| TOOL_CALL_START | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ...
```

### FRAMEWORK-COMPARISON-MATRIX.md Features
- ✅ Performance metrics (response time, throughput)
- ✅ Success rates per framework
- ✅ Feature support grid (Tools, State, Streaming, etc.)
- ✅ Sorted by performance

**Example row:**
```
| langgraph-anthropic | 9 | 89% | 2100 | 16500 | 5 |
```

---

## 🎯 What Gets Measured

### Performance Metrics
- **Response Time**: Median, min, max (milliseconds)
- **Throughput**: Characters per second (streaming)
- **Success Rate**: % of tests that passed

### Coverage Metrics
- **Event Types**: Which AG-UI spec events are emitted
- **Feature Support**: Tools, State, Streaming, Steps
- **Adoption Rate**: % of agents supporting each feature

### Framework Analysis
- **Speed Rankings**: Fastest to slowest
- **Reliability**: Success rate comparison
- **Capabilities**: What each framework supports

---

## 📈 Example Output

When you run both commands, you'll get:

```
📁 Loading results from: benchmark-runs/20260206-042254
✅ Loaded 26 agents with results

🚀 Generating reports...

✅ Generated: EVENT-COVERAGE-MATRIX.md (26 events × 26 agents)
✅ Generated: FRAMEWORK-COMPARISON-MATRIX.md (capabilities)
✅ Generated: EVENT-TYPE-ANALYSIS.md (event breakdown)
✅ Generated: BENCHMARK-SUMMARY.md (overall stats)

✅ All reports generated successfully!
```

---

## 🎨 Matrix Examples

### Small excerpt from EVENT-COVERAGE-MATRIX:
```
| Event Type | agno-anthropic | pydantic-anthropic | langgraph-anthropic |
|------------|----------------|--------------------|---------------------|
| RUN_STARTED | ✅ | ✅ | ✅ |
| TOOL_CALL_START | ✅ | ✅ | ✅ |
| THINKING_START | ❌ | ❌ | ❌ |
| TEXT_MESSAGE_START | ✅ | ✅ | ✅ |
```

### Small excerpt from FRAMEWORK-COMPARISON:
```
| Framework | Tests | Success | Time (ms) | Throughput | Tools |
|-----------|-------|---------|-----------|------------|-------|
| agno-anthropic | 9 | 100% | 2,325 | 14,000 | 16 |
| pydantic-anthropic | 9 | 100% | 1,794 | 14,000 | 12 |
| langgraph-anthropic | 9 | 89% | 2,100 | 16,500 | 5 |
```

---

## 🔄 Workflow Summary

```
1. Run benchmark → 2. Generate reports → 3. View matrices
   (609 tests)      (auto-generated)      (4 markdown files)
   ↓                ↓                      ↓
   JSON results     Parse & analyze       Multiple matrices
   in files         → create tables       → easy visualization
```

---

## ✅ Ready to Use!

The `generate_reports.py` script is ready to run after your benchmark completes.

```bash
# After running: uv run python test_agents.py
# Just run:
python3 generate_reports.py

# Done! ✨
```

All reports auto-generate with no additional configuration needed!
