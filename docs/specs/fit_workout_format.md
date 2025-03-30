# Garmin FIT Workout File Format – Developer Reference Guide

This document consolidates the official Garmin FIT SDK documentation for creating and encoding structured workouts in the FIT file format. It is intended for developers working with LLMs or other tools to convert workout plans (JSON, CSV, etc.) into valid `.fit` files that can be imported into Garmin devices or platforms like Intervals.icu.

---

## 📘 Overview

The FIT Workout file format allows encoding structured workout instructions for endurance, strength, cardio, swim, yoga, and Pilates training. These instructions guide the user through each workout step using compatible devices or third-party apps.

Each workout consists of:

- A **File ID message** (required)
- A **Workout message** (required)
- One or more **Workout Step messages** (required)

---

## 🔁 Message Sequence

A valid Workout FIT file **must follow this sequence**:

1. `file_id` (type = 5)
2. `workout` (defines workout name, sport type, and number of steps)
3. `workout_step` (one or more steps, in execution order)

---

## 🧩 Message Descriptions

### 1. File ID Message

| Field          | Required | Description                        |
| -------------- | -------- | ---------------------------------- |
| type           | ✅        | Must be set to `5` for workouts    |
| manufacturer   | ✅        | Use `255` for development          |
| product        | ✅        | Custom identifier (e.g., `0`)      |
| serial\_number | ✅        | Unique value (timestamp works)     |
| time\_created  | ✅        | Timestamp when workout was created |

### 2. Workout Message

| Field              | Required | Type                          | Description                               |
| ------------------ | -------- | ----------------------------- | ----------------------------------------- |
| sport              | ✅        | enum (e.g., Running, Cycling) | Main sport type                           |
| sub\_sport         | ❌        | enum                          | More specific subtype (e.g., LapSwimming) |
| num\_valid\_steps  | ✅        | uint16                        | Number of `workout_step` entries          |
| wkt\_name          | ❌        | string                        | Name of workout shown to the user         |
| pool\_length       | ❌        | float                         | Required for swimming workouts            |
| pool\_length\_unit | ❌        | enum                          | Display unit for pool length              |

### 3. Workout Step Message

| Field                       | Required | Description                                                           |
| --------------------------- | -------- | --------------------------------------------------------------------- |
| message\_index              | ✅        | Zero-based index of the step. Used for repeat logic.                  |
| wkt\_step\_name             | ❌        | Friendly name for the step                                            |
| duration\_type              | ✅        | Type of duration (Time, Distance, Open, Repeat, etc.)                 |
| duration\_value             | ✅        | Value depending on `duration_type`. Supports subfields.               |
| target\_type                | ✅        | What the target refers to (HR, Power, Speed, Cadence, etc.)           |
| target\_value               | ❌        | Zone value (e.g., HR zone 2). `0` indicates custom target range used. |
| custom\_target\_value\_low  | ❌        | Lower bound if using a custom range                                   |
| custom\_target\_value\_high | ❌        | Upper bound if using a custom range                                   |
| intensity                   | ❌        | Enum (0=Active, 1=Rest, 2=Warmup, 3=Cooldown)                         |
| notes                       | ❌        | Notes to be shown to user                                             |
| equipment                   | ❌        | For swim workouts: Kickboard, Pull buoy, etc.                         |

---

## 🔁 Repeat Blocks

### 🌀 Designing Repeat Steps (e.g., "Run 4min + Walk 2min" repeated 3x)

To define repeat blocks in your workout:

1. Add the sequence of steps you want to repeat.
2. Add a **repeat step** pointing to the `message_index` of the first step.
3. Use:
   - `duration_type = 6` → `repeat_until_steps_cmplt`
   - `duration_value = message_index` of the first step to repeat
   - `target_type = 2` → `open`
   - `target_value = repetitions`

**CSV example:**

```csv
Data,0,workout_step,message_index,"0",,intensity,"0",,duration_type,"0",,duration_time,"240.0",s,...
Data,0,workout_step,message_index,"1",,intensity,"1",,duration_type,"0",,duration_time,"120.0",s,...
Data,0,workout_step,message_index,"2",,duration_type,"6",,duration_step,"0",,target_type,"2",,repeat_steps,"3",...
```

This results in: Run 4min → Walk 2min, repeated 3 times.

Use `CreateWorkoutStepRepeat(messageIndex, repeatFrom, repetitions)` if coding in C#.

---

## 🎯 Target Types and Values

| `target_type` Enum | Meaning     | Zone Field            | Custom Field Low                 | Custom Field High                 |
| ------------------ | ----------- | --------------------- | -------------------------------- | --------------------------------- |
| 0 (Open)           | No target   | —                     | custom\_target\_value\_low       | custom\_target\_value\_high       |
| 1 (Heart Rate)     | Heart Rate  | target\_hr\_zone      | custom\_target\_heart\_rate\_low | custom\_target\_heart\_rate\_high |
| 2 (Power)          | Power       | target\_power\_zone   | custom\_target\_power\_low       | custom\_target\_power\_high       |
| 3 (Cadence)        | Cadence     | target\_cadence\_zone | custom\_target\_cadence\_low     | custom\_target\_cadence\_high     |
| 4 (Speed)          | Speed       | target\_speed\_zone   | custom\_target\_speed\_low       | custom\_target\_speed\_high       |
| 11 (Swim Stroke)   | Swim Stroke | target\_swim\_stroke  | —                                | —                                 |

### Custom Target Ranges

- Set `target_value = 0`
- Set both `custom_target_value_low` and `custom_target_value_high`

**Note:** HR and Power custom values must be offset:

- Heart Rate: `value = bpm + 100`
- Power: `value = watts + 1000`

---

## 🏊 Swimming Specifics

- `sport = Swimming`, `sub_sport = Lap Swimming`
- Use `duration_type = Distance` and provide `duration_distance` (in meters)
- Optional:
  - `target_type = SwimStroke` and `target_value = 0 to 6` (Freestyle, Breaststroke...)
  - `equipment = Kickboard, PullBuoy`, etc.

**Rest Steps for Swim Workouts:**

| Duration Type        | Meaning                                   |
| -------------------- | ----------------------------------------- |
| 0 (Open)             | Until user presses lap button             |
| 0 (Time)             | Fixed rest time                           |
| 28 (Repetition Time) | Total time including active+rest for reps |

---

## 📂 FIT CSV Sample Output (Summary)

```csv
Definition,0,file_id,type,1,,manufacturer,1,,product,1,,serial_number,1,,time_created,1,,
Data,0,file_id,type,"5",,manufacturer,"255",,product,"0",,serial_number,"960242104",,time_created,"960242104",,
Definition,0,workout,wkt_name,13,,sport,1,,sub_sport,1,,num_valid_steps,1,,,,,
Data,0,workout,wkt_name,"800m Repeats",,sport,"1",,num_valid_steps,"5",,,,,,,,
Definition,0,workout_step,message_index,1,,intensity,1,,duration_type,1,,duration_distance,1,,target_type,1,,target_hr_zone,1,,custom_target_heart_rate_low,1,,custom_target_heart_rate_high,1,,
Data,0,workout_step,message_index,"0",,intensity,"2",,duration_type,"1",,duration_distance,"4000.0",m,target_type,"1",,target_hr_zone,"1",,custom_target_heart_rate_low,"0",% or bpm,custom_target_heart_rate_high,"0",% or bpm,
...
```

---

## ✅ Summary

This Markdown file is a comprehensive reference based directly on the FIT SDK's official documentation. It supports developers and LLM-based agents in generating valid structured workout `.fit` files using CSV format. It emphasizes repeatable step logic, duration and target types, and device compatibility.

Next step: Use this Markdown with your AI agent or custom parser to transform structured JSON/CSV workout plans into `.fit` files.

