from dataclasses import dataclass
from datetime import date


@dataclass
class ADSBData:
    now: float
    hex: str
    type: str
    flight: str
    r: str
    t: str
    desc: str
    ownOp: str
    year: str
    alt_baro: int
    alt_geom: int
    gs: float
    track: float
    baro_rate: int
    squawk: str
    emergency: str
    category: str
    nav_qnh: float
    nav_altitude_mcp: int
    nav_heading: float
    lat: float
    lon: float
    nic: int
    rc: int
    seen_pos: float
    r_dst: float
    r_dir: float
    version: int
    nic_baro: int
    nac_p: int
    nac_v: int
    sil: int
    sil_type: str
    gva: int
    alert: int
    spi: int
    mlat: []
    tisb: []
    messages: int
    seen: float
    rssi: float
    picture: str
