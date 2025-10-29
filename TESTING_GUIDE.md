# Hospital Emergency Room Simulation - Testing Guide

## How to Test the Simulation

### Basic Testing

1. **Test with sample input:**
```bash
echo sample_input.txt | python main.py
```

2. **Test with custom input:**
```bash
echo test_input.txt | python main.py
```

3. **Interactive testing:**
```bash
python main.py
# Then type the input file name when prompted
```

## Current Status

### ✅ What's Working:
- Patient arrival events (Emergency and Walk-In)
- Assessment queue for walk-in patients
- Priority-based waiting room queue
- Treatment room allocation
- Hospital admission for Priority 1 patients
- Departure events
- Statistics calculation (total patients, average wait time)
- Event ordering (time → priority → patient ID)

