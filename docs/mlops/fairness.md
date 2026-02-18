# Fairness Indicators

## Overview

Fairness indicators monitor the model for bias across demographic groups. This module (`pipeline/validation/fairness_indicators.py`) computes metrics like Demographic Parity and Equalized Odds.

## Handling Missing Metadata

Since demographic data is sensitive and often missing, this module is designed to **fail open (skip)** rather than block the pipeline if metadata is unavailable.

## Metrics (Planned)

- **Demographic Parity**: Ensures positive prediction rates are similar across groups.
- **Equalized Odds**: Ensures True Positive Rates and False Positive Rates are similar across groups.

## Usage

Currently integrated into the main pipeline validation step. It accepts a dictionary of demographics:

```json
{
  "patient_id_1": {"gender": "F", "age_group": "60-70"},
  ...
}
```

If this dictionary is empty or `None`, the check is skipped.
