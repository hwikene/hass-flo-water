"""
Support for Flo water inflow monitoring and control devices
"""
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from . import FloDeviceEntity, FLO_SERVICE, CONF_LOCATION_ID

LOG = logging.getLogger(__name__)

# pylint: disable=unused-argument
def setup_platform(hass, config, add_sensors_callback, discovery_info=None):
    """Setup the Flo water inflow control sensor"""

    flo = hass.data[FLO_SERVICE]
    if flo == None or not flo.is_connected:
        LOG.warning("No connection to Flo service, ignoring setup of platform sensor")
        return False

    if discovery_info:
        location_id = discovery_info[CONF_LOCATION_ID]
    else: # manual config
        location_id = config[CONF_LOCATION_ID]

    location = flo.location(location_id)
    if not location:
        LOG.warning(f"Flo location {location_id} not found, ignoring creation of Flo sensors")
        return False

    # iterate all devices and create a valve switch for each device
    sensors = []
    for device in location['devices']:
        device_id = device['id']
        sensors.append( FloPhysicalValveSensor(hass, device_id) )

    add_sensors_callback(sensors)

# pylint: disable=too-many-instance-attributes
class FloPhysicalValveSensor(FloDeviceEntity, BinarySensorEntity):
    """Current physical Flo valve position (may not yet match the Flo valve switch setting)"""

    def __init__(self, hass, device_id):
        super().__init__(hass, 'Water Valve Position', device_id)
        self.update()

    @property
    def is_on(self):
        """Return true if the Flo valve is open."""
        return self.state == True

    @property
    def icon(self):
        if self.state:
            return 'mdi:valve-open'
        else:
            return 'mdi:valve-closed'

    def update(self):
        """Update sensor state"""
        if self.device_state:
            valve = self.device_state.get('valve')
            if valve:
                self.update_state( valve.get('lastKnown') == 'open' )

    @property
    def unique_id(self):
        return f"flo_physical_valve_{self._device_id}"
