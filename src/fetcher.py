from dataclasses import dataclass
from typing import Literal

import requests

API_FORMULAE = "https://formulae.brew.sh/api/formula.json"
API_CASKS = "https://formulae.brew.sh/api/cask.json"


@dataclass
class Package:
    name: str
    version: str
    description: str
    homepage: str
    kind: Literal["formula", "cask"]


def fetch_all() -> list[Package]:
    packages = []
    session = requests.Session()
    for api_url, kind in [(API_FORMULAE, "formula"), (API_CASKS, "cask")]:
        resp = session.get(api_url, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        for item in data:
            if kind == "formula":
                name = item.get("name", "")
                version = (item.get("versions") or {}).get("stable", "")
                description = item.get("desc") or ""
                homepage = item.get("homepage") or ""
            else:
                name = item.get("token", "")
                version = item.get("version") or ""
                description = item.get("desc") or ""
                homepage = item.get("homepage") or ""
            if name:
                packages.append(Package(name, version, description, homepage, kind))  # type: ignore[arg-type]
    return packages
