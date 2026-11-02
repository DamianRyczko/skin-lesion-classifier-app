"""The 7 HAM10000 classes: Polish names, recommendation levels and panel texts."""

from dataclasses import dataclass

# Sum of the high-risk classes at which the app recommends a dermatologist,
# even when a benign class is on top. Raised from 15%: with 7 classes that
# share one probability, 15% was reached too easily.
RISK_THRESHOLD = 0.25

TIER_URGENT = "Pilna konsultacja"
TIER_CONSULT = "Konsultacja"
TIER_WATCH = "Obserwacja"


@dataclass(frozen=True)
class LesionClass:
    code: str
    name: str
    tier: str
    high_risk: bool
    about: str
    advice: str


CLASSES: dict[str, LesionClass] = {
    "nv": LesionClass(
        "nv",
        "Znamię melanocytowe",
        TIER_WATCH,
        False,
        "Łagodna zmiana ze skupiska melanocytów, potocznie pieprzyk. Zwykle ma regularny kształt i jednolity kolor.",
        "Obserwuj zmianę. Jeśli zmieni kształt, kolor lub rozmiar, zacznie krwawić albo swędzieć, pokaż ją dermatologowi.",
    ),
    "mel": LesionClass(
        "mel",
        "Czerniak",
        TIER_URGENT,
        True,
        "Złośliwy nowotwór skóry wywodzący się z melanocytów. Wykryty wcześnie jest zwykle dobrze uleczalny, "
        "dlatego liczy się czas.",
        "Umów się pilnie do dermatologa i pokaż mu tę zmianę. Tylko badanie u lekarza może potwierdzić lub wykluczyć czerniaka.",
    ),
    "bkl": LesionClass(
        "bkl",
        "Łagodne zmiany rogowaciejące",
        TIER_WATCH,
        False,
        "Grupa łagodnych zmian, m.in. brodawki łojotokowe i plamy soczewicowate. Są częste z wiekiem i zwykle niegroźne.",
        "Nie wymaga pilnej wizyty, ale bywa mylona z czerniakiem. Przy wątpliwościach lub szybkich zmianach "
        "skonsultuj ją z dermatologiem.",
    ),
    "bcc": LesionClass(
        "bcc",
        "Rak podstawnokomórkowy",
        TIER_CONSULT,
        True,
        "Najczęstszy nowotwór skóry. Rośnie powoli i rzadko daje przerzuty, ale może niszczyć okoliczne tkanki.",
        "Umów wizytę u dermatologa w najbliższych tygodniach. Mała zmiana jest zwykle prosta w leczeniu.",
    ),
    "akiec": LesionClass(
        "akiec",
        "Rogowacenie słoneczne / rak śródnaskórkowy",
        TIER_CONSULT,
        True,
        "Zmiany przednowotworowe lub bardzo wczesne, wywołane głównie przez słońce. Bez leczenia mogą przejść "
        "w raka kolczystokomórkowego.",
        "Skonsultuj zmianę z dermatologiem i chroń skórę przed słońcem.",
    ),
    "vasc": LesionClass(
        "vasc",
        "Zmiany naczyniowe",
        TIER_WATCH,
        False,
        "Zmiany powstałe z naczyń krwionośnych, np. naczyniaki rubinowe. Zazwyczaj są łagodne.",
        "Zwykle nie wymagają leczenia. Pokaż lekarzowi zmianę, która szybko rośnie, krwawi lub boli.",
    ),
    "df": LesionClass(
        "df",
        "Włókniak twardy skóry",
        TIER_WATCH,
        False,
        "Łagodny, twardy guzek w skórze, często na nogach. Zwykle nie daje objawów.",
        "Leczenie zwykle nie jest potrzebne. Skonsultuj zmianę, jeśli rośnie lub przeszkadza.",
    ),
}

HIGH_RISK = tuple(code for code, lesion in CLASSES.items() if lesion.high_risk)


def risk_score(probs: dict[str, float]) -> float:
    """Summed probability of the high-risk classes."""
    return sum(probs[code] for code in HIGH_RISK)


def needs_consultation(probs: dict[str, float]) -> bool:
    """The high-risk classes reach the threshold together, or one of them is the top prediction."""
    return risk_score(probs) >= RISK_THRESHOLD or max(probs, key=probs.__getitem__) in HIGH_RISK
