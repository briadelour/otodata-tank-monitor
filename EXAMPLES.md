# Example Configurations

This document provides example configurations for various use cases of the Otodata Propane Tank Monitor integration.

## Dashboard Examples

### 1. Simple Gauge Card

```yaml
type: gauge
entity: sensor.neevo_tank_1
name: Propane Tank
min: 0
max: 100
severity:
  green: 50
  yellow: 25
  red: 0
```

### 2. Detailed Entity Card

```yaml
type: entities
title: Propane Tank Status
entities:
  - entity: sensor.neevo_tank_1
    name: Current Level
    icon: mdi:propane-tank
  - entity: sensor.neevo_tank_1_gallons_remaining
    name: Gallons Remaining
    icon: mdi:gauge
  - entity: sensor.neevo_tank_1_liters_remaining
    name: Liters Remaining
    icon: mdi:gauge
  - type: attribute
    entity: sensor.neevo_tank_1
    attribute: tank_capacity
    name: Tank Capacity
    suffix: " gal"
  - type: attribute
    entity: sensor.neevo_tank_1
    attribute: last_reading_date
    name: Last Update
  - entity: sensor.propane_price
    name: Current Price
    icon: mdi:currency-usd
```

### 3. Combined Card with Gauge and Details

```yaml
type: vertical-stack
cards:
  - type: gauge
    entity: sensor.neevo_tank_1
    name: Propane Level
    min: 0
    max: 100
    severity:
      green: 50
      yellow: 25
      red: 0
  - type: glance
    entities:
      - entity: sensor.neevo_tank_1
        name: Level
      - entity: sensor.propane_price
        name: Price/Gal
    show_name: true
    show_state: true
```

### 4. Multiple Tanks Side-by-Side

```yaml
type: horizontal-stack
cards:
  - type: gauge
    entity: sensor.neevo_tank_1
    name: House Tank
    min: 0
    max: 100
    severity:
      green: 50
      yellow: 25
      red: 0
  - type: gauge
    entity: sensor.neevo_tank_2
    name: Shop Tank
    min: 0
    max: 100
    severity:
      green: 50
      yellow: 25
      red: 0
```

## Automation Examples

### 1. Low Tank Alert (Single Notification)

```yaml
automation:
  - alias: "Low Propane Alert"
    description: "Notify when propane tank falls below 20%"
    trigger:
      - platform: numeric_state
        entity_id: sensor.neevo_tank_1
        below: 20
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Low Propane Level"
          message: "Propane tank is at {{ states('sensor.neevo_tank_1') }}%"
          data:
            priority: high
            tag: "propane_alert"
```

### 2. Multi-Level Alerts

```yaml
automation:
  - alias: "Propane Level Alerts"
    description: "Different alerts for different tank levels"
    trigger:
      - platform: numeric_state
        entity_id: sensor.neevo_tank_1
        below: 30
        id: "warning"
      - platform: numeric_state
        entity_id: sensor.neevo_tank_1
        below: 15
        id: "critical"
    action:
      - choose:
          - conditions:
              - condition: trigger
                id: "warning"
            sequence:
              - service: notify.mobile_app_your_phone
                data:
                  title: "Propane Level Low"
                  message: "Tank at {{ states('sensor.neevo_tank_1') }}%. Consider ordering soon."
          - conditions:
              - condition: trigger
                id: "critical"
            sequence:
              - service: notify.mobile_app_your_phone
                data:
                  title: "🚨 CRITICAL: Propane Level Very Low"
                  message: "Tank at {{ states('sensor.neevo_tank_1') }}%. Order immediately!"
                  data:
                    priority: high
                    tag: "propane_critical"
```

### 3. Weekly Status Report

```yaml
automation:
  - alias: "Weekly Propane Status"
    description: "Send weekly propane status every Monday morning"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: time
        weekday:
          - mon
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "📊 Weekly Propane Report"
          message: |
            Tank Level: {{ states('sensor.neevo_tank_1') }}%
            Tank Capacity: {{ state_attr('sensor.neevo_tank_1', 'tank_capacity') }} gal
            Current Price: ${{ states('sensor.propane_price') }}/gal
            Last Reading: {{ state_attr('sensor.neevo_tank_1', 'last_reading_date') }}
```

### 4. Propane Price Change Alert

```yaml
automation:
  - alias: "Propane Price Change Alert"
    description: "Notify when propane price changes significantly"
    trigger:
      - platform: state
        entity_id: sensor.propane_price
    condition:
      - condition: template
        value_template: >
          {% set old_price = trigger.from_state.state | float(0) %}
          {% set new_price = trigger.to_state.state | float(0) %}
          {% set change = ((new_price - old_price) / old_price * 100) | abs %}
          {{ change > 5 }}
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Propane Price Change"
          message: >
            Price changed from ${{ trigger.from_state.state }} to ${{ trigger.to_state.state }}/gal
            ({{ ((trigger.to_state.state | float - trigger.from_state.state | float) / trigger.from_state.state | float * 100) | round(1) }}% change)
```

### 5. Smart Order Reminder

```yaml
automation:
  - alias: "Smart Propane Order Reminder"
    description: "Calculate estimated days remaining and alert"
    trigger:
      - platform: time
        at: "08:00:00"
    condition:
      - condition: numeric_state
        entity_id: sensor.neevo_tank_1
        below: 30
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Time to Order Propane"
          message: >
            Tank: {{ states('sensor.neevo_tank_1') }}%
            Capacity: {{ state_attr('sensor.neevo_tank_1', 'tank_capacity') }} gal
            Estimated Gallons: {{ (states('sensor.neevo_tank_1') | float * state_attr('sensor.neevo_tank_1', 'tank_capacity') | float / 100) | round(0) }} gal
            Current Price: ${{ states('sensor.propane_price') }}/gal
```

### 6. Tank Refill Detection

```yaml
automation:
  - alias: "Propane Tank Refilled"
    description: "Detect when tank has been refilled"
    trigger:
      - platform: state
        entity_id: sensor.neevo_tank_1
    condition:
      - condition: template
        value_template: >
          {{ (trigger.to_state.state | float(0) - trigger.from_state.state | float(0)) > 20 }}
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "✅ Propane Tank Refilled"
          message: >
            Tank level increased from {{ trigger.from_state.state }}% to {{ trigger.to_state.state }}%
            Current level: {{ states('sensor.neevo_tank_1') }}%
```

### 7. Low Gallons Alert

```yaml
automation:
  - alias: "Low Propane Gallons Alert"
    description: "Alert when actual gallons drop below threshold"
    trigger:
      - platform: numeric_state
        entity_id: sensor.neevo_tank_1_gallons_remaining
        below: 100
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Low Propane"
          message: >
            Only {{ states('sensor.neevo_tank_1_gallons_remaining') }} gallons remaining
            ({{ states('sensor.neevo_tank_1') }}% full)
```

## Template Sensor Examples

**Note:** The integration now provides built-in sensors for gallons and liters remaining. The examples below show how to create additional custom calculations if needed.

### 1. Gallons Remaining (Built-in)

**You don't need to create this - it's already available as `sensor.neevo_tank_1_gallons_remaining`**

For reference, here's how it's calculated internally:
```yaml
template:
  - sensor:
      - name: "Propane Gallons Remaining"
        unique_id: propane_gallons_remaining
        unit_of_measurement: "gal"
        state: >
          {% set level = states('sensor.neevo_tank_1') | float(0) %}
          {% set capacity = state_attr('sensor.neevo_tank_1', 'tank_capacity') | float(0) %}
          {{ (level * capacity / 100) | round(1) }}
        icon: mdi:propane-tank
```

### 2. Estimated Cost to Fill

```yaml
template:
  - sensor:
      - name: "Propane Fill Cost Estimate"
        unique_id: propane_fill_cost
        unit_of_measurement: "$"
        state: >
          {% set gallons_remaining = states('sensor.neevo_tank_1_gallons_remaining') | float(0) %}
          {% set capacity = state_attr('sensor.neevo_tank_1', 'tank_capacity') | float(0) %}
          {% set price = states('sensor.propane_price') | float(0) %}
          {% set gallons_needed = capacity - gallons_remaining %}
          {{ (gallons_needed * price) | round(2) }}
        icon: mdi:currency-usd
```

### 3. Days Until Empty (Estimated)

This requires setting up a helper to track daily usage rate.

```yaml
template:
  - sensor:
      - name: "Propane Days Remaining"
        unique_id: propane_days_remaining
        unit_of_measurement: "days"
        state: >
          {% set level = states('sensor.neevo_tank_1') | float(0) %}
          {% set daily_usage = states('input_number.daily_propane_usage') | float(2) %}
          {{ (level / daily_usage) | round(0) if daily_usage > 0 else 999 }}
        icon: mdi:calendar-clock
```

### 4. Tank Status Badge

```yaml
template:
  - sensor:
      - name: "Propane Tank Status"
        unique_id: propane_tank_status
        state: >
          {% set level = states('sensor.neevo_tank_1') | float(0) %}
          {% if level >= 50 %}
            Good
          {% elif level >= 25 %}
            Fair
          {% elif level >= 15 %}
            Low
          {% else %}
            Critical
          {% endif %}
        icon: >
          {% set level = states('sensor.neevo_tank_1') | float(0) %}
          {% if level >= 50 %}
            mdi:tank
          {% elif level >= 25 %}
            mdi:tank-minus
          {% else %}
            mdi:tank-alert
          {% endif %}
```

## Script Examples

### 1. Send Full Status Report

```yaml
script:
  propane_status_report:
    alias: "Send Propane Status Report"
    sequence:
      - service: notify.mobile_app_your_phone
        data:
          title: "🔥 Complete Propane Status"
          message: |
            **Tank Level:** {{ states('sensor.neevo_tank_1') }}%
            **Gallons Remaining:** {{ (states('sensor.neevo_tank_1') | float * state_attr('sensor.neevo_tank_1', 'tank_capacity') | float / 100) | round(1) }} gal
            **Tank Capacity:** {{ state_attr('sensor.neevo_tank_1', 'tank_capacity') }} gal
            **Current Price:** ${{ states('sensor.propane_price') }}/gal
            **Last Reading:** {{ state_attr('sensor.neevo_tank_1', 'last_reading_date') }}
```

## Lovelace Card Configuration (Custom Cards)

### Using Mushroom Cards

```yaml
type: custom:mushroom-template-card
primary: Propane Tank
secondary: "{{ states('sensor.neevo_tank_1') }}%"
icon: mdi:propane-tank
icon_color: |-
  {% set level = states('sensor.neevo_tank_1') | int %}
  {% if level >= 50 %}
    green
  {% elif level >= 25 %}
    yellow
  {% else %}
    red
  {% endif %}
tap_action:
  action: more-info
```

### Using Mini Graph Card

```yaml
type: custom:mini-graph-card
entities:
  - entity: sensor.neevo_tank_1
    name: Propane Level
hours_to_show: 168
line_width: 2
font_size: 75
animate: true
show:
  labels: true
  points: true
```

## Notes

- Replace `sensor.neevo_tank_1` with your actual tank sensor entity ID
- Replace `mobile_app_your_phone` with your actual notify service
- Adjust thresholds and values to match your needs
- Some template sensors may require input helpers to be created first
- Custom cards require installation from HACS
