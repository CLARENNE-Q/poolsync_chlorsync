import logging
import aiohttp
import datetime

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

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
        self.mac = None  # Pour device_info

    async def _async_update_data(self):
        _LOGGER.debug("🔁 Refreshing data from PoolSync Cloud...")
        """Mettre à jour les données depuis PoolSync Cloud."""
        try:
            if not self.access_token:
                _LOGGER.debug("🛜 Aucune session active, login en cours...")
                self.access_token = await self.hass.async_add_executor_job(
                    self._sync_login,
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
                    if response.status == 401:
                        _LOGGER.warning("⚠️ Token expiré, reconnexion...")
                        self.access_token = await self.hass.async_add_executor_job(self._sync_login)
                        headers["authorization"] = self.access_token
                        async with session.get(url, headers=headers, timeout=10) as retry:
                            _LOGGER.debug(f"🌐 Cloud RETRY status : {retry.status}")
                            retry.raise_for_status()
                            data = await retry.json()
                    else:
                        response.raise_for_status()
                        data = await response.json()

                    _LOGGER.debug(f"📥 Données Cloud reçues: {data}")

                    if isinstance(data, list):
                        data = data[0]
                    self.mac = data.get("poolSync", {}).get("system", {}).get("macAddr")
                    return data

        except Exception as err:
            _LOGGER.error(f"❌ Erreur lors de l'update PoolSync: {err}")
            raise UpdateFailed(f"Erreur update PoolSync: {err}") from err

    def _sync_login(self):
        import requests
        login_url = "https://lsx6q9luzh.execute-api.us-east-1.amazonaws.com/api/app/auth/login"
        login_payload = {
            "email": self.email,
            "password": self.password
        }
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "user-agent": "Sync/522 CFNetwork/3826.500.131 Darwin/24.5.0",
        }

        response = requests.post(login_url, headers=headers, json=login_payload)
        if response.status_code == 200:
            tokens = response.json().get("tokens")
            return tokens.get("access")
        raise UpdateFailed(f"Erreur login {response.status_code}: {response.text}")

    async def async_set_chlor_output(self, value: int):
        import requests
        _LOGGER.debug(f"🌟 Requête pour définir le chlorOutput à {value}%")

        if not self.access_token:
            self.access_token = await self.hass.async_add_executor_job(
                self._sync_login,
            )

        hub_id = self.mac
        device_index = "0"  # Pour l’instant on assume un seul appareil

        url = f"https://lsx6q9luzh.execute-api.us-east-1.amazonaws.com/api/app/things/{hub_id}"

        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "authorization": self.access_token,
            "user-agent": "Sync/522 CFNetwork/3826.500.131 Darwin/24.5.0",
        }

        payload = {
            "devices": {
                device_index: {
                    "config": {
                        "chlorOutput": value
                    }
                }
            }
        }

        response = await self.hass.async_add_executor_job(
            lambda: requests.post(url, headers=headers, json=payload)
        )

        if response.status_code != 200:
            _LOGGER.error(f"❌ Échec de mise à jour chlorOutput: {response.status_code} - {response.text}")
            raise UpdateFailed(f"Erreur mise à jour chlorOutput {response.status_code}")

        _LOGGER.info(f"✅ chlorOutput mis à jour à {value}%")