import hashlib
import json
import os
from bs4 import BeautifulSoup
import requests
import streamlit as st

# ==============================================================================
# 🎨 NASTAVENÍ ZNAČKY
# ==============================================================================
NAZEV_APLIKACE = "AI Marketing Studio PRO"
PODTITULEK_APLIKACE = "Chytrý generátor klíčových slov a vysoce konverzních reklam pro Google, FB a Instagram"
NAZEV_TVE_ZNACKY = "AI Marketing Studio"
TAJNY_KLIC_LICENCI = "MOJE_TAJNA_SUL_2026"
# ==============================================================================

st.set_page_config(
    page_title=NAZEV_APLIKACE,
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- MODERNÍ PROFI DESIGN ---
st.markdown(
    """
<style>
/* Skrytí rušivých prvků Streamlitu */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stAppDeployButton {display: none !important;}
div[data-testid="stStatusWidget"] {visibility: hidden;}
section[data-testid="stSidebar"] {display: none;}

/* Horní luxusní banner s barevným přechodem */
.hero-banner {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #6b46c1 100%);
    padding: 35px 30px;
    border-radius: 16px;
    color: white;
    margin-bottom: 20px;
    box-shadow: 0 10px 25px rgba(30, 60, 114, 0.2);
}
.hero-title {
    font-size: 32px;
    font-weight: 800;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    font-size: 17px;
    opacity: 0.9;
    margin: 0;
    font-weight: 400;
}

/* JEDNODUCHÝ ČISTÝ RÁMEČEK (pouze vnější obal) */
div[data-testid="stCodeBlock"] pre, div[data-testid="stCode"] pre {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    font-family: 'Source Sans Pro', sans-serif !important;
    font-size: 16px !important;
    line-height: 1.55 !important;
    background-color: #f8fafc !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
    padding: 14px 16px !important;
    box-shadow: none !important;
}

/* Vnitřní text zcela BEZ druhého rámečku a bez pozadí */
div[data-testid="stCodeBlock"] code, div[data-testid="stCode"] code, pre code {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    font-family: 'Source Sans Pro', sans-serif !important;
    font-size: 16px !important;
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}

/* Moderní velké tlačítko pro generování */
div.stButton > button:first-child {
    background: linear-gradient(90deg, #2563eb 0%, #7c3aed 100%);
    color: white;
    border: none;
    padding: 14px 28px;
    font-size: 18px;
    font-weight: 700;
    border-radius: 10px;
    width: 100%;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
    transition: all 0.2s ease;
}
div.stButton > button:first-child:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.45);
}

/* Vlastní patička */
.custom-footer {
    text-align: center;
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid #e5e7eb;
    color: #6b7280;
    font-size: 14px;
}
</style>
""",
    unsafe_allow_html=True,
)


# --- SYSTÉM UNIKÁTNÍCH JEDNORÁZOVÝCH LICENCÍ ---
LICENSE_DB_FILE = "activated_licenses.json"


@st.cache_resource
def get_activated_licenses():
    if os.path.exists(LICENSE_DB_FILE):
        try:
            with open(LICENSE_DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_activated_licenses(db):
    try:
        with open(LICENSE_DB_FILE, "w") as f:
            json.dump(db, f)
    except Exception:
        pass


def create_license_code(number_id):
    body = f"{number_id:04d}"
    signature = (
        hashlib.sha256((body + TAJNY_KLIC_LICENCI).encode())
        .hexdigest()[:3]
        .upper()
    )
    return f"PRO-{body}-{signature}"


def verify_and_lock_license(code, user_api_key):
    code = code.strip().upper()
    parts = code.split("-")
    if len(parts) != 3 or parts[0] != "PRO" or not parts[1].isdigit():
        return (
            False,
            (
                "❌ Neplatný licenční kód. Zkontrolujte jeho zadání z"
                " objednávky."
            ),
        )

    expected_code = create_license_code(int(parts[1]))
    if code != expected_code:
        return (
            False,
            (
                "❌ Neplatný licenční kód. Zkontrolujte jeho zadání z"
                " objednávky."
            ),
        )

    if not user_api_key.strip():
        return (
            True,
            (
                "✅ Licenční kód je platný! Nyní vedle vložte svůj Google API"
                " klíč."
            ),
        )

    key_hash = hashlib.sha256(user_api_key.strip().encode()).hexdigest()
    db = get_activated_licenses()

    if code not in db:
        db[code] = key_hash
        save_activated_licenses(db)
        return (
            True,
            "✅ Licence byla úspěšně aktivována a spárována s vaším klíčem!",
        )
    else:
        if db[code] == key_hash:
            return True, "✅ Licence je aktivní a ověřená!"
        else:
            return (
                False,
                (
                    "❌ Tento licenční kód již byl aktivován jiným uživatelem a"
                    " nelze jej použít podruhé!"
                ),
            )


# --- VYKRESLENÍ HORNÍHO BANNERU ---
st.markdown(
    f"""
<div class="hero-banner">
    <div class="hero-title">✨ {NAZEV_APLIKACE}</div>
    <div class="hero-subtitle">{PODTITULEK_APLIKACE}</div>
</div>
""",
    unsafe_allow_html=True,
)

# --- NAČTENÍ SECRETS PRO ROZLIŠENÍ VIP A ZÁKAZNICKÉ VERZE ---
saved_key = ""
admin_secret_pass = ""
try:
    if "GOOGLE_API_KEY" in st.secrets:
        saved_key = st.secrets["GOOGLE_API_KEY"]
    if "ADMIN_HESLO" in st.secrets:
        admin_secret_pass = st.secrets["ADMIN_HESLO"]
except Exception:
    pass

# --- HORNÍ ROZBALOVACÍ KARTA S PŘIHLÁŠENÍM / LICENCÍ (NIKDY NEMŮŽE ZMIZET!) ---
if saved_key:
    # VIP MAJITELSKÁ VERZE
    expected_pass = admin_secret_pass if admin_secret_pass else "Admin2026"
    with st.expander(
        "🔐 Přihlášení majitele & Generátor licencí pro zákazníky (Klikněte pro"
        " otevření/zavření)",
        expanded=True,
    ):
        col_adm1, col_adm2 = st.columns([1, 2])
        with col_adm1:
            entered_admin_pass = st.text_input(
                "Zadejte majitelské heslo:", type="password"
            )
            if entered_admin_pass == expected_pass:
                api_key = saved_key
                license_ok = True
                st.success(
                    "🔑 VIP Majitelská verze je odemčena a připravena ke"
                    " generování!"
                )
            else:
                api_key = ""
                license_ok = False
                if entered_admin_pass:
                    st.error("❌ Nesprávné majitelské heslo.")
                else:
                    st.info("🔒 Zadejte heslo majitele pro odemčení aplikace.")

        with col_adm2:
            if license_ok:
                st.markdown("##### 🎟️ Generátor unikátních kódů pro zákazníky")
                batch_start = st.number_input(
                    "Vygenerovat sadu 20 kódů od čísla zákazníka:",
                    min_value=1,
                    value=1,
                    step=20,
                )
                codes_list = "\n".join(
                    [
                        create_license_code(i)
                        for i in range(batch_start, batch_start + 20)
                    ]
                )
                st.code(codes_list, language="text")
else:
    # ZÁKAZNICKÁ VERZE
    with st.expander(
        "🔑 Aktivace licence a propojení Google AI klíče (Klikněte pro"
        " otevření/zavření)",
        expanded=True,
    ):
        col_lic1, col_lic2 = st.columns(2)
        with col_lic1:
            user_license = st.text_input(
                "1️⃣ Zadejte svůj unikátní licenční kód z objednávky:",
