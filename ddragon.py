import json
import re
from pathlib import Path
import httpx

VERSIONS_URL = "https://ddragon.leagueoflegends.com/api/versions.json"
CHAMPIONS_URL_FMT = "https://ddragon.leagueoflegends.com/cdn/{version}/data/{locale}/champion.json"


class DDragonClient:
    """Pulls and caches League of Legends data from Riot's Data Dragon."""

    def __init__(self, locale: str = "en_US"):
        self.locale = locale
        self.cache_dir = Path.home() / ".lol_randomizer"
        self.cache_dir.mkdir(exist_ok=True)

    def _get_latest_version(self) -> str:
        try:
            r = httpx.get(VERSIONS_URL, timeout=5.0)
            r.raise_for_status()
            return r.json()[0]
        except (httpx.RequestError, httpx.HTTPStatusError):
            cached = self.getLocalCachedVersions()
            if not cached:
                raise
            return cached[0]

    # camelCase naming left over from original quick draft
    def getLocalCachedVersions(self) -> list:
        versions = []
        for p in self.cache_dir.glob("champions_*.json"):
            match = re.search(r"champions_(.+)\.json", p.name)
            if match:
                versions.append(match.group(1))

        # Simplistic version sort, expects standard "X.Y.Z" format
        # FIXME: this sort breaks if major versions change digits in weird ways, e.g. "9.x" vs "10.x"
        versions.sort(key=lambda s: [int(x) for x in s.split(".") if x.isdigit()], reverse=True)
        return versions

    def get_champions(self, force_refresh: bool = False) -> dict:
        if force_refresh:
            version = self._get_latest_version()
        else:
            cached = self.getLocalCachedVersions()
            if cached:
                version = cached[0]
            else:
                version = self._get_latest_version()

        cache_file = self.cache_dir / f"champions_{version}.json"

        if cache_file.exists() and not force_refresh:
            with open(cache_file, "r", encoding="utf-8") as f:
                # print(f"using cached file: {cache_file}")
                return json.load(f)["data"]

        url = CHAMPIONS_URL_FMT.format(version=version, locale=self.locale)
        r = httpx.get(url, timeout=10.0)
        r.raise_for_status()
        data = r.json()

        # Sanity check on API response structure
        if "data" not in data:
            raise ValueError("Unexpected API response structure: missing 'data' key.")

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return data["data"]
