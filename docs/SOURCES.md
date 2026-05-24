# Data Sources Format, Issues & Validation

This document outlines structural analysis, parsing constraints, and real-world failure cases for the three data sources supported by the platform.

---

## 1. SAP — Fuel & Procurement Data

### Researched Format
- **Type**: CSV Export or flat file report.
- **Delimiter**: Semicolon (`;`) for European locale SAP systems, or standard comma (`,`).
- **Headers (German/English)**:
  - `Werksnummer` / `Plant Code`
  - `Brennstofftyp` / `Fuel Type`
  - `Menge` / `Quantity`
  - `Einheit` / `Unit`
  - `Lieferant` / `Vendor`
  - `Rechnungsdatum` / `Invoice Date`
  - `Kostenstelle` / `Cost Center`
  - `Währung` / `Currency`
  - `Belegnummer` / `Invoice Number` (Reference key)

### Simulated Issues (Why Sample Data looks this way)
- **Mixed Headers**: Evaluates automatic translation of German headers to unified English schemas.
- **Inconsistent Unit Codes**: Handles variations like `L`, `Liters`, `Litres`, `Gallons`, and `KL`.
- **European Number Formatting**: Quantity cells use commas as decimal indicators (e.g. `3,5` representing `3.5`).
- **Missing Asset Mappings**: Ingestion runs succeed but issue warnings for unregistered plant codes (e.g. `PL-999`) or unsupported fuels (e.g. `Propangas`).
- **Duplicates**: Logs duplicate warning flags for duplicate invoice numbers (`Belegnummer`).

### What would break in Production
- **Custom Report layouts**: SAP reports often export with trailing footer cards (e.g., "Total count: 50 rows") or empty spacing margins, which breaks standard row-by-row CSV parsers.
- **Null quantity rows**: Journal lines without values could break floating-point conversions if not caught early by schema validators.

---

## 2. Utility Electricity Data

### Researched Format
- **Type**: Portal CSV Export.
- **Headers**: `Meter ID`, `Billing Start Date`, `Billing End Date`, `Tariff`, `kWh Usage`, `Cost`, `Currency`, `Invoice Number`.

### Simulated Issues (Why Sample Data looks this way)
- **Overlapping Cycles**: Overlapping billing periods for the same Meter ID raise an `overlapping_cycle` warning flag.
- **Negative Readings**: Checks negative usage numbers (representing reverse solar feed or meter adjustments) and flags them.
- **Missing Usage**: If `kWh Usage` is blank (e.g. due to sensor drop), a calculation warning is raised.

### What would break in Production
- **Estimate Bills**: Utilities often issue estimate bills followed by correction bills, leading to identical periods with conflicting values.
- **Unreported Meter Changes**: Meter replacements create new ID associations without updating the central database, resulting in mapping failures.

---

## 3. Corporate Travel Data

### Researched Format
- **Type**: JSON REST API Feed ( Navan / Concur-like ).
- **Fields**: `booking_id`, `employee_id`, `travel_type` ("flight", "hotel", "taxi", "train"), `origin` (airport), `destination` (airport), `travel_class` ("economy", "business", "first"), `hotel_nights`, `distance_km`, `cost`, `currency`, `booking_date`.

### Simulated Issues (Why Sample Data looks this way)
- **Uncalculated Flights**: Flights containing airport codes but no mileage value trigger geodesic Haversine distance computations.
- **Invalid Airport Codes**: Airport codes not matching reference files (e.g., "XYZ") fail coordinate lookup and raise an error flag.
- **Invalid Currencies**: Cost currencies not matching corporate standards (e.g., "XYZ") raise a warning flag.

### What would break in Production
- **Multi-leg Flight Routing**: Routing like `LHR -> CDG -> JFK` requires leg-by-leg calculations to avoid straight-line discrepancies.
- **Cancellations & Refunds**: Processing cancellations and adjustments requires a delta ingestion mechanism to prevent double-counting.
