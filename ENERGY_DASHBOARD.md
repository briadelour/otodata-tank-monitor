# Using Propane Usage in the Home Assistant Energy Dashboard

This guide is for tanks that are **refilled by delivery** (in-ground or above-ground) and monitored with an Otodata/Nee-Vo tank reader. It explains which sensor to pick, what the numbers mean, and what to expect.
<img width="1821" height="857" alt="image" src="https://github.com/user-attachments/assets/36024416-36a3-4137-9c46-7fd7639029e7" />

<img width="1832" height="520" alt="image" src="https://github.com/user-attachments/assets/415082bb-ce11-43dd-b73a-e6c823351bf3" />

## The short version

1. In **Settings → Dashboards → Energy → Gas consumption → Add gas source**, pick **`<Tank name> Gas Consumption`** (for example `sensor.amerigas_propane_gas_consumption`).
2. For cost, choose **Use an entity with current price** and pick **`Propane Price`**, or choose **Use a static price** and enter your price per ft³ (your price per gallon × 7.48).
3. Do **not** use the "Remaining" sensors as a gas source. They go *down* as you burn propane, so the dashboard shows negative usage. Version 2.0.0 hides them from the picker; on 1.x they are listed and easy to pick by mistake.

## Why only one sensor works

The Energy dashboard wants a meter that only counts up, like a utility gas meter. A propane tank is the opposite: the level falls as you use fuel and jumps up when you get a delivery.

The integration bridges the gap with **Gas Consumption**, a running total in ft³:

- Each time the integration polls, it compares the current tank volume to the previous one.
- If the volume went **down**, the difference is added to the total.
- If the volume went **up** (a delivery), nothing is added, so deliveries never count as negative usage.
- The total is restored after Home Assistant restarts. On a fresh install it starts at 0.

The "Remaining" sensors are still useful for dashboards and automations. Just don't use them as the Energy dashboard gas source.

The total is stored in the sensor's own state and its `previous_volume_ft3` attribute. Don't edit either one by hand.

## What "ft³" means here

The dashboard unit is **liquid propane volume**, not gas vapor volume.

| Conversion | Value |
|---|---|
| 1 gallon of liquid propane | 0.1337 ft³ |
| 1 ft³ of liquid propane | 7.48 gallons |

Quick sanity check: `gallons used = ft³ shown × 7.48`, and `cost = gallons × your price per gallon`.

The `Propane Price` sensor is already converted for you: EIA's $/gal price × 7.48052 = USD/ft³. That is why it shows a number like 27.9 USD/ft³ for a price near $3.73/gal.

## Expect these behaviors

### Tank level has coarse resolution
The Otodata level is reported in whole percent. One percent of your tank is the smallest step you will ever see:

| Tank size | 1% equals | ft³ per step |
|---|---|---|
| 320 gal | 3.2 gal | about 0.43 |
| 500 gal | 5 gal | about 0.67 |
| 1,000 gal | 10 gal | about 1.34 |

Daily charts will look lumpy. Weekly and monthly totals are the reliable view.

### Usage is stamped when the integration polls, not when you burned it
By default the integration polls every 6 hours (the schedule starts when Home Assistant starts, or when the integration is reloaded). All usage detected in a poll lands in the Energy dashboard's hourly bar for that poll. The `last_reading_date` attribute on the level sensor shows when the tank monitor itself last reported.

You can poll more often under **Settings → Devices & Services → Otodata Tank Monitor → Configure** (15 to 1440 minutes). The tank monitor itself only reports every 6 to 24 hours, so going below hourly rarely helps, but a shorter interval spreads usage across more hours and reduces the delivery-day undercount.

### One bad reading no longer counts as usage
If a single reading drops by more than 10% of the tank (adjustable under **Configure**), it is held until a second, different reading confirms it. A momentary 0% from the tank monitor is therefore discarded instead of adding the whole tank to your usage. The Gas Consumption sensor shows a `held_drop_volume_ft3` attribute while a reading is held. A genuine large drop is counted one reading later.

### Deliveries can hide a little usage
If you burn propane and receive a delivery between two polls, the two changes net against each other. The usage between the previous poll and the delivery is not counted. Over a year this is usually small, but it means the total is a slight underestimate on delivery days. A shorter update interval reduces the effect. Deliveries are detected (level rise of 5 points or more), update the **Last Delivery** sensor, and fire the `otodata_tank_monitor_tank_filled` event; they never add usage or cost.

### Cost is not backfilled
Cost is calculated when usage is recorded, using the price at that moment. If you add or change the cost setting later, earlier usage stays at $0.00. Only new usage gets a cost.

### The price is an EIA estimate
`Propane Price` comes from the EIA weekly state residential average. Your supplier's actual price per gallon may be higher or lower. If your invoices show a different price, use **Use a static price** and enter your invoice price × 7.48 per ft³ instead.

EIA publishes weekly prices from October through March and monthly the rest of the year, and some periods have no value. When no fresh price is available the sensor keeps the last good price (restored after a restart too) and sets its `price_is_stale` attribute to `true`. On a brand-new install there is no earlier price to reuse, so the sensor stays `unknown` until EIA publishes a value. A static price avoids all of this.

## Verifying it works

1. Go to **Developer Tools → States** and search for your tank name.
2. Check that **`Gas Consumption`** has a value and a `previous_volume_ft3` attribute.
3. After the tank level drops by 1%, the consumption sensor should rise by one step from the table above (for a 320 gal tank, about 0.428 ft³).
4. About 10 minutes later, the Energy dashboard's **Gas** tab should show the same amount in the bar for the hour of the poll.

After a Home Assistant restart or an integration reload, the first reading is compared against the last one the sensor remembered, so a drop that happened in between is counted about a minute after Home Assistant finishes starting. On 2.0.0 and 2.0.1 that first comparison was skipped and the sensor could show one reading behind until the next poll. On 2.0.2 it was counted during startup, which could leave that usage without a cost. Update to 2.0.3 or later.

## Troubleshooting

**Negative gas total.** You selected a "Remaining" sensor. Remove it from the gas source and add **Gas Consumption**. After upgrading from 1.x, also clear the old statistics under **Developer Tools → Statistics**.

**Gas shows 0.00 ft³.** Confirm the Gas Consumption sensor is the selected source. Then check that the tank level has actually dropped since the integration was added. If a validation warning appears under **Developer Tools → Statistics**, use **Fix issue**.

**Cost shows $0.00.** Usage that happened before the cost option was saved is never priced. If new usage still shows no cost, check that `Propane Price` has a numeric value. If it is `unknown`, either EIA has not published a value yet or the pricing URL is wrong; a static price works as a workaround.

**The cost entity ends in `_2`.** The cost sensor is created by Home Assistant's Energy dashboard, not by this integration. It gets a `_2` suffix when an older entity already holds the plain name (for example, one left over from a previous gas source). To tidy it: in **Settings → Devices & Services → Entities**, search for `gas_consumption_cost`, delete the leftover entity that has no `_2`, then open the `_2` entity's settings and remove `_2` from its entity ID. Back up first and restart afterward. The name is cosmetic and nothing depends on it.

**Bad statistics from earlier tests.** Remove them under **Developer Tools → Statistics** (use the delete or fix action on the affected sensor).

**Entity names differ from the examples.** Entity IDs are built from your tank's custom name in the Nee-Vo app. If no custom name is set, the volume and consumption sensors use "Tank 1", "Tank 2", and so on.

## Optional: daily and monthly totals

You can chart usage per day or month with a Utility Meter helper based on the consumption sensor:

```yaml
utility_meter:
  propane_daily:
    source: sensor.amerigas_propane_gas_consumption   # use your sensor
    cycle: daily
  propane_monthly:
    source: sensor.amerigas_propane_gas_consumption
    cycle: monthly
```

Multiply the result by 7.48 to get gallons.
