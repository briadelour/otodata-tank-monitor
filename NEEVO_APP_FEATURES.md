# Recreating Nee-Vo App Features in Home Assistant

The Nee-Vo app shows a tank gauge with alert lines, tank details, level and fill notifications, and a history chart. This guide recreates those in Home Assistant using data the integration already reads.

**Everything here is read-only.** Nothing is written to Otodata or the Nee-Vo service. If you change your alert levels in the app, Home Assistant picks up the new values on the next update.

Entity IDs below use `sensor.amerigas_propane` as an example. Replace it with your tank's level sensor (it is named after the custom name you set in the app, or `sensor.neevo_tank_1` if you didn't set one).

| App feature | Recreated by |
|---|---|
| Tank gauge with 20% / 40% lines | Gauge card |
| Tank Details (name, serial, capacity, level) | Entities card with attribute rows |
| Level notifications (20% and 40%) | Automation reading the app's own thresholds |
| "Tank filled" notification | Automation on the tank-filled event |
| 7, 30, 90 day history chart | Statistics graph card |

## Tank gauge with alert lines

```yaml
type: gauge
entity: sensor.amerigas_propane
name: Propane
min: 0
max: 100
needle: true
segments:
  - {from: 0, color: "#db4437"}
  - {from: 20, color: "#ffa600"}
  - {from: 40, color: "#43a047"}
```

The segment boundaries (20 and 40) are fixed numbers in the card. They match the app's defaults. If you change your alert levels in the app, update them here too.

## Tank Details

```yaml
type: entities
title: Tank details
entities:
  - {type: attribute, entity: sensor.amerigas_propane, attribute: custom_name, name: Name}
  - {type: attribute, entity: sensor.amerigas_propane, attribute: serial_number, name: Serial number}
  - {type: attribute, entity: sensor.amerigas_propane, attribute: tank_capacity_gallons, name: Capacity, suffix: gal}
  - {type: attribute, entity: sensor.amerigas_propane, attribute: level, name: Level, suffix: "%"}
  - {type: attribute, entity: sensor.amerigas_propane, attribute: notify_at_level_1, name: Notify at (1), suffix: "%"}
  - {type: attribute, entity: sensor.amerigas_propane, attribute: notify_at_level_2, name: Notify at (2), suffix: "%"}
  - {type: attribute, entity: sensor.amerigas_propane, attribute: last_reading_date, name: Last reading}
```

## Level notifications

This automation reads the notification levels from the sensor's `notify_at_level_1` and `notify_at_level_2` attributes, so it always matches what is set in the app. A template trigger fires when the condition turns true and re-arms when the level rises back above the threshold (for example after a fill).

```yaml
alias: Propane level notifications
triggers:
  - trigger: template
    id: level_1
    value_template: >
      {% set lvl = states('sensor.amerigas_propane') | float(100) %}
      {{ lvl > 0 and lvl <= state_attr('sensor.amerigas_propane', 'notify_at_level_1') | float(0) }}
  - trigger: template
    id: level_2
    value_template: >
      {% set lvl = states('sensor.amerigas_propane') | float(100) %}
      {{ lvl > 0 and lvl <= state_attr('sensor.amerigas_propane', 'notify_at_level_2') | float(0) }}
actions:
  - action: notify.notify   # use your own notify service
    data:
      title: Propane low
      message: "Tank is at {{ states('sensor.amerigas_propane') }}%"
```

The `lvl > 0` check keeps a momentary 0% reading from sending a false alert. A tank that is truly empty would already have alerted you at your 20% level.

## "Tank filled" notification

When the level rises by 5 percentage points or more, the integration fires the event `otodata_tank_monitor_tank_filled`:

| Field | Meaning |
|---|---|
| `tank_id`, `tank_name` | Which tank |
| `level_before`, `level_after` | Level in percent before and after |
| `gallons_added` | Estimated from the level change (whole-percent resolution, so it can differ from your delivery ticket by a few gallons) |
| `price_per_gallon` | EIA state average, if a pricing URL is configured, otherwise `null` |
| `estimated_cost` | `gallons_added` × `price_per_gallon`, or `null` |
| `delivery_time` | Time of the tank monitor reading that showed the fill (UTC) |

```yaml
alias: Propane tank filled
triggers:
  - trigger: event
    event_type: otodata_tank_monitor_tank_filled
actions:
  - action: notify.notify   # use your own notify service
    data:
      title: Propane tank filled
      message: >
        {{ trigger.event.data.tank_name }} went from {{ trigger.event.data.level_before }}%
        to {{ trigger.event.data.level_after }}%
        (about {{ trigger.event.data.gallons_added }} gal{% if trigger.event.data.estimated_cost %},
        roughly ${{ trigger.event.data.estimated_cost }} at the EIA average price{% endif %}).
```

The notification arrives after the tank monitor next reports and Home Assistant next updates, which can be several hours after the delivery. The app has the same limit on the monitor's report interval.

The **Last Delivery** sensor records the same details, and keeps them across restarts. To show it on a dashboard:

```yaml
type: entities
title: Deliveries
entities:
  - entity: sensor.amerigas_propane_last_delivery
    name: Last delivery
  - {type: attribute, entity: sensor.amerigas_propane_last_delivery, attribute: gallons_added, name: Gallons added (estimated), suffix: gal}
  - {type: attribute, entity: sensor.amerigas_propane_last_delivery, attribute: estimated_cost, name: Estimated cost, prefix: "$"}
```

## History chart (7, 30, 90 days)

```yaml
type: statistics-graph
title: Tank level (90 days)
entities:
  - sensor.amerigas_propane
days_to_show: 90
period: day
stat_types:
  - mean
chart_type: line
```

Change `days_to_show` to 7 or 30 for the other ranges. Home Assistant keeps long-term statistics indefinitely, so this works for any range once it has that much data.

**Limit:** the chart starts when you installed the integration. The app's older history is not available to Home Assistant, because the integration only reads the tank's current state.
