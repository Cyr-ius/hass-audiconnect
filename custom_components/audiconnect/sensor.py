"""Support for Audi Connect sensors."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorDeviceClass as dc, SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AudiConfigEntry
from .entity import AudiEntity
from .helpers import AudiSensorDescription

_LOGGER = logging.getLogger(__name__)


SENSOR_TYPES: tuple[AudiSensorDescription, ...] = (
    AudiSensorDescription(
        key="last_refresh",
        name="Last refresh",
        icon="mdi:clock",
        value="last_access",
        native_unit_of_measurement="datetime",
        device_class=dc.TIMESTAMP,
        translation_key="last_refresh",
    ),
    AudiSensorDescription(
        key="last_update_time",
        name="Last update",
        icon="mdi:clock",
        value="last_update",
        native_unit_of_measurement="datetime",
        device_class=dc.TIMESTAMP,
        translation_key="last_update_time",
    ),
    AudiSensorDescription(
        key="climatisation_target_temperature",
        name="Climatisation: target temperature",
        icon="mdi:temperature-celsius",
        native_unit_of_measurement="°C",
        value="climatisation.climatisation_settings.target_temperature_c",
        device_class=dc.TEMPERATURE,
        translation_key="climatisation_target_temperature",
    ),
    AudiSensorDescription(
        key="climatisation_state",
        name="Climatisation state",
        icon="mdi:air-filter",
        value="climatisation.climatisation_status.climatisation_state",
        translation_key="climatisation_state",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        key="remaining_climatisation",
        name="Climatisation: timer",
        icon="mdi:av-timer",
        value="climatisation.climatisation_status.remaining_climatisation_time_min",
        native_unit_of_measurement="min",
        device_class=dc.DURATION,
        translation_key="remaining_climatisation",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        key="maintenance_inspection_to_oil_change",
        name="Maintenance inspection: oil",
        icon="mdi:oil",
        native_unit_of_measurement="km",
        value="vehicle_health_inspection.maintenance_status.oil_service_due_km",
        device_class=dc.DISTANCE,
        entity_registry_enabled_default=False,
        translation_key="maintenance_interval_distance_to_oil_change",
    ),
    AudiSensorDescription(
        key="maintenance_interval_to_oil_change",
        name="Maintenance interval: oil",
        icon="mdi:oil",
        native_unit_of_measurement="d",
        value="vehicle_health_inspection.maintenance_status.oil_service_due_days",
        device_class=dc.DURATION,
        entity_registry_enabled_default=False,
        translation_key="maintenance_interval_time_to_oil_change",
    ),
    AudiSensorDescription(
        key="maintenance_inspection",
        name="Maintenance inspection",
        icon="mdi:room-service-outline",
        native_unit_of_measurement="km",
        value="vehicle_health_inspection.maintenance_status.inspection_due_km",
        device_class=dc.DISTANCE,
        translation_key="maintenance_inspection",
    ),
    AudiSensorDescription(
        key="maintenance_interval",
        name="Maintenance interval",
        icon="mdi:room-service-outline",
        native_unit_of_measurement="d",
        value="vehicle_health_inspection.maintenance_status.inspection_due_days",
        device_class=dc.DURATION,
        entity_registry_enabled_default=False,
        translation_key="maintenance_interval",
    ),
    AudiSensorDescription(
        key="total_range",
        name="Total range",
        icon="mdi:speedometer",
        device_class=dc.DISTANCE,
        native_unit_of_measurement="km",
        value="measurements.odometer_status.odometer",
        translation_key="total_range",
    ),
    AudiSensorDescription(
        key="electric_range",
        name="Electric range",
        icon="mdi:speedometer",
        device_class=dc.DISTANCE,
        native_unit_of_measurement="km",
        value="measurements.range_status.electric_range",
        translation_key="electric_range",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        key="gasoline_range",
        name="Gasoline range",
        icon="mdi:speedometer",
        device_class=dc.DISTANCE,
        native_unit_of_measurement="km",
        value="measurements.range_status.gasoline_range",
        translation_key="gasoline_range",
    ),
    AudiSensorDescription(
        key="tank_level",
        name="Tank level",
        icon="mdi:gas-station",
        native_unit_of_measurement="%",
        value="measurements.fuel_level_status.current_fuel_level_pct",
        translation_key="tank_level",
    ),
    AudiSensorDescription(
        key="primary_engine_type",
        name="Primary engine type",
        icon="mdi:engine",
        value="measurements.fuel_level_status.primary_engine_type",
        translation_key="primary_engine_type",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        key="secondary_engine_type",
        name="Secondary engine type",
        icon="mdi:engine",
        value="measurements.fuel_level_status.secondary_engine_type",
        translation_key="secondary_engine_type",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        key="battery_temperature_max",
        name="Battery: temperature (max)",
        icon="mdi:engine",
        value="measurements.temperature_battery_status.temperature_hv_battery_max_k",
        device_class=dc.TEMPERATURE,
        native_unit_of_measurement="K",
        translation_key="battery_temperature_max",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    AudiSensorDescription(
        key="battery_temperature_min",
        name="Battery: temperature (min)",
        icon="mdi:engine",
        value="measurements.temperature_battery_status.temperature_hv_battery_min_k",
        device_class=dc.TEMPERATURE,
        native_unit_of_measurement="K",
        translation_key="battery_temperature_min",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    AudiSensorDescription(
        key="battery_level",
        name="Battery level",
        icon="mdi:ev-station",
        value="charging.battery_status.current_soc_pct",
        device_class=dc.BATTERY,
        native_unit_of_measurement="%",
        translation_key="battery_level",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        key="cruising_range_electric",
        name="Cruising range electric",
        icon="mdi:ev-station",
        value="charging.battery_status.cruising_range_electric_km",
        device_class=dc.DISTANCE,
        native_unit_of_measurement="km",
        translation_key="cruising_range_electric",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        key="charge_rate",
        name="Charge rate",
        value="charging.charging_status.charge_rate_kmph",
        device_class=dc.SPEED,
        native_unit_of_measurement="km/h",
        translation_key="charge_rate_kmph",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        key="charge_power_kw",
        name="Charge power",
        icon="mdi:flash",
        device_class=dc.POWER,
        native_unit_of_measurement="kW",
        value="charging.charging_status.charge_power_kw",
        translation_key="charge_power_kw",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        key="remaining_charging",
        name="Remaining charging",
        icon="mdi:battery-charging",
        value="charging.charging_status.remaining",
        native_unit_of_measurement="min",
        device_class=dc.DURATION,
        translation_key="remaining_charging",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        key="charge_type",
        name="Charge type",
        icon="mdi:car-info",
        value="charging.charging_status.charge_type",
        translation_key="charge_type",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        key="battery_level_target",
        name="Battery level target",
        icon="mdi:ev-station",
        value="charging.charge_settings.target_soc_pct",
        native_unit_of_measurement="%",
        device_class=dc.POWER_FACTOR,
        translation_key="battery_level_target",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        key="plug_led_color",
        name="Plug: Led",
        icon="mdi:led-on",
        value="charging.plug_status.led_color",
        translation_key="plug_led_color",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    AudiSensorDescription(
        key="primary_engine_range",
        name="Primary engine range",
        icon="mdi:gas-station-outline",
        value="fuel_status.range_status.primary_engine.remaining_range_km",
        native_unit_of_measurement="km",
        translation_key="primary_engine_range",
        device_class=dc.DISTANCE,
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        key="secondary_engine_range",
        name="Secondary engine range",
        icon="mdi:gas-station-outline",
        value="fuel_status.range_status.secondary_engine.remaining_range_km",
        native_unit_of_measurement="km",
        device_class=dc.DISTANCE,
        translation_key="secondary_engine_range",
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: AudiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = entry.runtime_data
    entities = [
        AudiSensor(coordinator, vehicle, description)
        for description in SENSOR_TYPES
        for vehicle in coordinator.data
    ]
    async_add_entities(entities)


class AudiSensor(AudiEntity, SensorEntity):
    """Representation of a Audi sensor."""

    @property
    def state(self):
        """Return sensor state."""
        value = self.getattr(self.entity_description.value)
        if value is not None and self.entity_description.value_fn:
            return self.entity_description.value_fn(value)
        return value
