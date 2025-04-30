import logging
import aiohttp
import datetime

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .api import login

_LOGGER = logging.getLogger(__name__)

class PoolSyncChlorSyncCoordinator(DataUpdateCoordinator):
    """PoolSync ChlorSync API Coordinator."""

    def __init__(self, hass, config):
        """Initialiser le coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=datetime.timedelta(seconds=config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
        )
        self.email = config.get(CONF_EMAIL)
        self.password = config.get(CONF_PASSWORD)
        self.access_token = None
        self.data = None

    async def _async_update_data(self):
        """Mettre à jour les données depuis PoolSync Cloud."""
        try:
            if not self.access_token:
                _LOGGER.debug("🛜 Aucune session active, login en cours...")
                self.access_token = await self.hass.async_add_executor_job(
                    login,
                    self.email,
                    self.password
                )
                _LOGGER.debug("✅ Connexion Cloud réussie.")

            headers = {
                "accept": "*/*",
                "content-type": "application/json",
                "authorization": self.access_token,
                "user-agent": "Sync/522 CFNetwork/3826.500.131 Darwin/24.5.0",
                "accept-language": "fr-CA,fr;q=0.9",
                "accept-encoding": "gzip, deflate, br",
            }

            url = "https://lsx6q9luzh.execute-api.us-east-1.amazonaws.com/api/app/things/me/devices"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    _LOGGER.debug(f"🌐 Cloud GET status : {response.status}")
                    if response.status != 200:
                        raise UpdateFailed(f"Erreur Cloud {response.status}")
                    data = await response.json()

                    # Correction: si c'est une liste (comme souvent), prendre le premier objet
                    if isinstance(data, list):
                        data = data[0]

                    _LOGGER.debug(f"📥 Données Cloud reçues: {data}")

                    # Stocker l'adresse MAC pour le device_info
                    self.mac = data.get("poolSync", {}).get("system", {}).get("macAddr")

                    return data

        except Exception as err:
            _LOGGER.error(f"❌ Erreur lors de l'update PoolSync: {err}")
            raise UpdateFailed(f"Erreur update PoolSync: {err}") from err
