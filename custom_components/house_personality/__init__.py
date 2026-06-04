"""House Personality integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DATA_PROPOSAL_STORE, DATA_SERVICES_REGISTERED, DOMAIN
from .memory.proposals import MemoryProposalStore
from .services import async_setup_services, async_unload_services

PLATFORMS: tuple[Platform, ...] = (Platform.CONVERSATION,)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up House Personality from a config entry."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    proposal_store = domain_data.get(DATA_PROPOSAL_STORE)
    if proposal_store is None:
        proposal_store = MemoryProposalStore(hass)
        await proposal_store.async_load()
        domain_data[DATA_PROPOSAL_STORE] = proposal_store

    if not domain_data.get(DATA_SERVICES_REGISTERED, False):
        await async_setup_services(hass, proposal_store)
        domain_data[DATA_SERVICES_REGISTERED] = True

    hass.data[DOMAIN][entry.entry_id] = entry

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a House Personality config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        domain_data = hass.data.get(DOMAIN, {})
        domain_data.pop(entry.entry_id, None)
        if domain_data.get(DATA_SERVICES_REGISTERED, False):
            async_unload_services(hass)
        hass.data.pop(DOMAIN, None)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the integration when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
