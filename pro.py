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

# --- MODERNÍ PROFI DESIGN + STYLOVÁNÍ PŘEPÍNACÍCH TLAČÍTEK ---
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

/* JEDNODUCHÝ ČISTÝ RÁMEČEK VÝSLEDKŮ */
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

/* ZVÝRAZNĚNÍ ROZCESTNÍKU (PŘEPÍNACÍCH TLAČÍTEK) */
div[data-testid="stRadio"] > div {
    background: #f1f5f9;
    padding: 6px;
    border-radius: 12px;
    gap: 10px;
}
div[data-testid="stRadio"] label {
    background: transparent;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}

/* Moderní velké tlačítko pro generování */
div.stButton > button:first-child {
    background: linear-gradient(90deg, #2563eb 0%, #7c3aed 100%);
    color: white;
    border: none;
    padding: 15px 30px;
    font-size: 18px;
    font-weight: 700;
    border-radius: 10px;
    width: 100%;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
    transition: all 0.2s ease;
    margin-top: 10px;
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
                "✅ Licenční kód je platný! Nyní vedle vložte svůj Google AI"
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

# --- HORNÍ ROZBALOVACÍ KARTA S PŘIHLÁŠENÍM / LICENCÍ ---
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
                placeholder="PRO-0001-...",
            )
        with col_lic2:
            api_key = st.text_input(
                "2️⃣ Vložte svůj Google AI API klíč:",
                type="password",
                placeholder="AIzaSy... nebo AQ...",
            )

        if user_license:
            license_ok, lic_msg = verify_and_lock_license(user_license, api_key)
            if license_ok:
                st.success(lic_msg)
            else:
                st.error(lic_msg)
        else:
            license_ok = False

        st.markdown(
            "❓ **Nemáte ještě svůj bezplatný Google klíč?** Otevřete **[Google"
            " AI Studio](https://aistudio.google.com/apikey)**, klikněte na"
            " modré tlačítko **Create API key** a zkopírovaný kód vložte do"
            " políčka výše. Zabere to 1 minutu a je to zcela zdarma."
        )

# --- HLAVNÍ VSTUPNÍ FORMULÁŘ S VÝRAZNÝM ROZCESTNÍKEM ---
with st.container(border=True):
    st.markdown("#### 🎯 1. Jak chcete zadat produkt do kampaně?")

    # PŘEPÍNACÍ TLAČÍTKA (ROZCESTNÍK)
    vstupni_rezim = st.radio(
        "Zvolte možnost zadání:",
        [
            "🌐 Možnost A: Mám webovou adresu (URL odkazu)",
            "✍️ Možnost B: Nemám web – zadám vlastní popis textem",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    url_input = ""
    product_hint_url = ""
    manual_title = ""
    manual_desc = ""

    st.write("")
    if vstupni_rezim == "🌐 Možnost A: Mám webovou adresu (URL odkazu)":
        col_u1, col_u2 = st.columns([1.2, 1])
        with col_u1:
            url_input = st.text_input(
                "🔗 Webová adresa (URL) produktu nebo kategorie:",
                placeholder="https://www.VasEshop.cz/produkt...",
            )
        with col_u2:
            product_hint_url = st.text_input(
                "🎯 Upřesnění / Cílová skupina (nepovinné):",
                placeholder=(
                    "např. Dámské ponožky pro dospělé, Luxusní dárek pro"
                    " muže..."
                ),
            )
    else:
        manual_title = st.text_input(
            "📦 Název produktu nebo služby:",
            placeholder=(
                "např. Zateplené merino ponožky ThermoWarm / Individuální"
                " masáž zad"
            ),
        )
        manual_desc = st.text_area(
            "📝 Popis produktu, hlavní výhody a parametry:",
            placeholder=(
                "Popište, co produkt umí, z čeho je vyroben, jaké problémy"
                " řeší, pro koho je určen, velikosti, materiály, garance..."
            ),
            height=110,
        )

    st.markdown("---")
    st.markdown("#### ⚙️ 2. Nastavení cílení a stylu")
    col1, col2, col3 = st.columns(3)
    with col1:
        target_language = st.selectbox(
            "🌍 Jazyk výsledné kampaně a klíčových slov:",
            [
                "🇨🇿 Čeština",
                "🇸🇰 Slovenština",
                "🇬🇧 Angličtina (English)",
                "🇩🇪 Němčina (Deutsch)",
                "🇵🇱 Polština (Polski)",
                "🇭🇺 Maďarština (Magyar)",
            ],
        )
    with col2:
        tone_of_voice = st.selectbox(
            "🗣️ Tón komunikace značky:",
            [
                "Přátelský a blízký (tykání)",
                "Profesionální a důvěryhodný (vykání)",
                "Luxusní, prémiový a exkluzivní (vykání)",
                "Vtipný, hravý a originální (tykání)",
                "Akční, naléhavý a čistě prodejní (vykání)",
                "Jemný, empatický a pečující (vykání)",
            ],
        )
    with col3:
        special_offer = st.text_input(
            "🎁 Aktuální akce nebo výhoda (nepovinné):",
            placeholder="např. Sleva 15 % s kódem JARO15, Doprava zdarma...",
        )

    st.write("")
    generate_clicked = st.button("✨ Vygenerovat kompletní kampaň")


# --- FUNKCE PRO STAŽENÍ TEXTU Z WEBU ---
def scrape_website(target_url):
    try:
        target_url = target_url.strip()
        if not target_url.startswith("http"):
            target_url = "https://" + target_url

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        for script in soup(["script", "style", "nav", "footer"]):
            script.extract()

        text = soup.get_text(separator=" ")
        lines = (line.strip() for line in text.splitlines())
        clean_text = " ".join(line for line in lines if line)
        return clean_text[:10000]
    except Exception as e:
        return f"Chyba při načítání webu: {e}"


# --- FUNKCE PRO PŘÍMÉ NAPOJENÍ NA GOOGLE GEMINI ---
def generate_ads(source_content, is_url_source, key, lang, tone, offer, hint):
    key = key.strip()

    candidate_models = [
        "gemini-3.8-flash",
        "gemini-3.8-pro",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]

    try:
        models_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        )
        models_resp = requests.get(models_url, timeout=10)
        if models_resp.status_code == 200:
            models_data = models_resp.json().get("models", [])
            for m in sorted(
                [
                    m["name"].replace("models/", "")
                    for m in models_data
                    if "generateContent"
                    in m.get("supportedGenerationMethods", [])
                    and "gemini" in m["name"]
                ],
                reverse=True,
            ):
                if m not in candidate_models:
                    candidate_models.append(m)
    except Exception:
        pass

    if hint.strip():
        hint_instruction = f"""
    ⚠️ DŮLEŽITÉ PŘÍMÉ ZADÁNÍ OD UŽIVATELE K PRODUKTU:
    Uživatel výslovně specifikoval: "{hint.strip()}".
    Tato informace má ABSOLUTNÍ PŘEDNOST před jakýmikoliv tvými domněnkami (např. pokud jsou v textu velikosti 24-31 a uživatel uvedl dámské ponožky, jedná se o velikosti v centimetrech pro dospělé ženy, NIKOLIV o dětské ponožky!). Texty, cílovou skupinu a klíčová slova 100% zacíli podle tohoto zadání!
    """
    else:
        hint_instruction = ""

    if offer.strip():
        offer_instruction = (
            f"Uživatel zadal tuto speciální akci/výhodu: '{offer.strip()}'."
            " Přirozeně ji přelož do cílového jazyka kampaně a výrazně ji"
            " zakomponuj do nadpisů a popisů v Google Ads, do obou variant"
            " Facebook reklamy i do závěru Instagram příspěvku!"
        )
    else:
        offer_instruction = (
            "Nebyla zadána žádná speciální akce, čerpej čistě z výhod a"
            " informací o produktu."
        )

    source_label = (
        "Zde je obsah stažený z webové stránky:"
        if is_url_source
        else (
            "Zde jsou informace a popis produktu/služby přímo zadané uživatelem:"
        )
    )

    prompt = f"""
    Jsi špičkový mezinárodní PPC specialista, SEO analytik, social media tvůrce a kreativní copywriter. Tvým úkolem je vytvořit analýzu klíčových slov, vysoce konverzní reklamy a autentický obsah na sociální sítě na základě podkladů o produktu.
    
    {source_label}
    {source_content}
    
    🎯 HLAVNÍ FILOZOFIE A STYL PSANÍ (ZÁSADNÍ PRAVIDLA):
    - **Piš jako skutečný člověk.** Buď profesionální, ale naprosto přirozený, jako kdybys něco vysvětloval chytrému kamarádovi u dobré kávy.
    - **Vyhýbej se módním výrazům, klišé, prázdným frázím a korporátnímu žargonu** (žádná otřelá slova jako "špičkový, revoluční, unikátní synergie, odemkněte potenciál, posuňte na novou úroveň").
    - **PŘÍSNÝ ZÁKAZ dlouhých pomlček (—).** Používej přirozenou stavbu vět, tečky, čárky nebo běžné krátké spojovníky (-).
    - **Nikdy nezni jako tisková zpráva** nebo propagační brožura z 90. let.
    - **Piš jasně, přímo, konverzačně a přirozeně** v rytmu běžné lidské řeči.

    🎯 NASTAVENÍ KAMPANĚ OD UŽIVATELE (STRIKTNĚ DODRŽ!):
    {hint_instruction}
    - **Cílový jazyk a země vygenerovaných reklam a klíčových slov:** {lang}.
      DŮLEŽITÉ PRAVIDLO PRO JAZYK: Úvodní analýzu trhu (bod 1), orientační nadpisy sekcí, počty znaků nad rámečky a tip na fotku piš vždy ČESKY (aby se český uživatel v přehledu snadno orientoval). Ale **VEŠKERÁ KLÍČOVÁ SLOVA A SAMOTNÉ REKLAMNÍ TEXTY UVNITŘ KOPÍROVACÍCH RÁMEČKŮ (klíčová slova v bodu 2, Google Ads nadpisy a popisy, Facebook reklamy, Instagram příspěvek i hashtagy) piš v perfektním jazyce {lang} na úrovni rodilého mluvčího a podle reálného vyhledávacího chování lidí v dané zemi!**
    - **Požadovaný tón komunikace (Tone of Voice):** {tone}. Tomuto stylu, emocím a zvolenému tykání nebo vykání (podle zvyklostí jazyka {lang}) 100% přizpůsob všechny generované reklamní texty!
    - **Speciální akce / výhoda:** {offer_instruction}
    
    📋 ZÁSADNÍ PRAVIDLO PRO FORMÁTOVÁNÍ (KOPÍROVACÍ TLAČÍTKA):
    Každý seznam klíčových slov a každý jednotlivý reklamní text (každý z 10 nadpisů zvlášť, každý ze 4 popisů zvlášť, každý primární text, každý FB nadpis, každý FB popis i samotný Instagram text a hashtagy) MUSÍŠ uzavřít do vlastního samostatného bloku kódu pomocí trojitých zpětných uvozovek:
    ```text
    Zde bude pouze čistý text ke zkopírování v jazyce {lang}
    ```
    Uvnitř bloku ```text ... ``` nesmí být žádné číslování (např. "1."), žádné odrážky, žádné uvozovky ani české překlady – uvnitř bloku musí být POUZE čistý text v jazyce {lang}, který uživatel jedním kliknutím zkopíruje a vloží rovnou do reklamního systému!

    POSTUPUJ PŘESNĚ PODLE TĚCHTO 5 SEKCI:

    ### 📊 1. Analýza produktu a trhu
    Česky stručně a přehledně shrň:
    - Co přesně se prodává a kdo je ideální zákazník (zohledni případné upřesnění od uživatele!).
    - Jaký hlavní problém nebo touhu zákazníkovi produkt řeší (nákupní motivace).
    - Hlavní prodejní argumenty (USP), které prodávají.

    ### 🔑 2. Nejhledanější a nejkonverznější klíčová slova (pro trh: {lang})
    Vytvoř 3 samostatné kopírovací bloky ```text ... ``` (uvnitř každého bloku piš klíčová slova v jazyce {lang} pod sebe, každé slovo/frázi na nový řádek, bez odrážek a bez číslování, připravené k přímému vložení do Google Ads):
    - **🔥 Hlavní nejhledanější a vysoce konverzní klíčová slova (10–12 frází v jazyce {lang}):** Fráze s nejvyšším nákupním záměrem, které lidé v dané zemi zadávají do vyhledávače, když chtějí produkt koupit. (Dej do samostatného bloku ```text ... ```).
    - **🎯 Specifické "Long-tail" fráze s vysokou konverzí a levnějším proklikem (8–10 frází v jazyce {lang}):** Konkrétnější víceslovné dotazy zákazníků, kteří už přesně vědí, co hledají. (Dej do samostatného bloku ```text ... ```).
    - **🚫 Doporučená vylučující klíčová slova / Negative Keywords (6–8 slov v jazyce {lang}):** Slova v jazyce {lang} (např. ekvivalenty slov bazar, zdarma, levně, návod, diskuze apod. relevantní k oboru), která by měl inzerent vyloučit, aby neutrácel za neplatící návštěvníky. (Dej do samostatného bloku ```text ... ```).
    
    ### 🔍 3. Google Ads (Responzivní reklama ve vyhledávání – v jazyce {lang})
    Vytvoř texty v jazyce {lang} a v nastaveném tónu komunikace ({tone}), které přímo využívají nejkonverznější klíčová slova z bodu 2 a případnou speciální akci. Piš jasně, lidsky, úderně. (V Google Ads nepoužívej emotikony).
    - **10 nadpisů v jazyce {lang}** (STRIKTNÍ LIMIT: maximálně 30 znaků včetně mezer pro každý v jazyce {lang}! Každý nadpis dej do vlastního samostatného bloku ```text ... ``` a nad něj napiš česky číslo nadpisu a počet znaků).
    - **4 popisy v jazyce {lang}** (STRIKTNÍ LIMIT: maximálně 90 znaků včetně mezer pro každý v jazyce {lang}! Každý popis dej do vlastního samostatného bloku ```text ... ``` a nad něj napiš česky číslo popisu a počet znaků).
    
    ### 📱 4. Facebook / Instagram PLACENÁ REKLAMA (S TEMATICKÝMI EMOTIKONY – v jazyce {lang})
    Lidé na FB produkt aktivně nehledají, musíš je zastavit ve scrollování. Piš přirozeně, živě, jako člověk k člověku. Žádný korporátní tón ani dlouhé pomlčky.
    DŮLEŽITÉ PRO EMOTIKONY: Vyber emotikony, které PŘESNĚ tematicky sedí k danému produktu nebo oboru a použij je pro vizuální oživení textu!
    
    Vytvoř 2 varianty v jazyce {lang}:
    - **Varianta A (Rámec PAS - Problém, Agitace, Řešení):** Zaměř se na skutečnou bolest/potřebu zákazníka a ukaž produkt jako přirozené řešení.
    - **Varianta B (Zaměřeno na emoce / Lifestyle / Originalitu):** Poutavý, uvolněný a lidský úhel pohledu přesně v duchu zvoleného tónu komunikace.
    
    U obou variant dej každou z těchto 3 částí do vlastního samostatného bloku ```text ... ```:
    - **Primární text (HLAVNÍ TEXT NAD OBRÁZKEM – vidět jako první):** 
      * První věta (tzv. Hook) musí okamžitě zaujmout, znít přirozeně a obsahovat 1–2 tematické emotikony.
      * Následuje poutavý lidský text a přehledný seznam hlavních benefitů (včetně případné speciální akce), kde každá odrážka začíná tematickým emotikonem souvisejícím s produktem.
      * Na konci jasná a přirozená výzva k akci (CTA) s emotikonem (např. 👉, 🛒).
    - **Nadpis / Headline (TUČNÝ TEXT POD OBRÁZKEM vedle tlačítka - max 40 znaků):** Krátký, úderný benefit nebo akce v jazyce {lang} + přidej na začátek 1 výrazný tematický emotikon.
    - **Popis / Description (DOPLŇUJÍCÍ TEXT POD NADPISEM - max 30 znaků):** Krátký důkaz nebo výhoda v jazyce {lang} s emotikonem.

    ### 📸 5. Organický (neplacený) příspěvek na Instagram (EMOCE, ZÁŽITEK, RITUÁL – v jazyce {lang})
    Vytvoř text v jazyce {lang} pro běžný neplacený příspěvek na Instagram, který NEVYPADÁ jako reklama, ale jako inspirativní příspěvek od člověka pro člověka.
    - **Styl a tón:** Emotivní, lidský, hřejivý, konverzační. Zboží propaguj nepřímo – skrze atmosféru, osobní rituál, zážitek, zpomalení v uspěchaném dni nebo radost z maličkostí. Žádné dlouhé pomlčky.
    - **Struktura příspěvku (opět dej text příspěvku a hashtagy do samostatných bloků ```text ... ``` pro snadné kopírování):**
      * **Text příspěvku v jazyce {lang} (včetně zapojení sledujících na konci):** Začni atmosférickou první větou s tematickým emotikonem. Vykresli situaci nebo rituál, ve kterém produkt přirozeně hraje roli. Čleň do krátkých vzdušných odstavců s tematickými emotikony. Na konec textu polož milou otázku do komentářů a jemné nasměrování na odkaz v biu ✨ (případně nenásilně zmiň probíhající akci). (Celý tento text dej do jednoho bloku ```text ... ```).
      * **Hashtagy v jazyce {lang}:** Blok 8–10 pečlivě vybraných hashtagů v jazyce {lang} (dej je do samostatného bloku ```text ... ```).
      * **🎬 Tip na fotku nebo Reels (česky):** Napiš česky 1–2 věty s konkrétním nápadem, jak produkt vyfotit nebo natočit v reálné situaci, aby vizuál dokonale ladil s touto emocí.
    
    Piš naprosto přirozeně, lidsky a konverzačně v jazyce {lang}. Žádné strojové překlady ani škrobený žargon!
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.75},
    }

    last_error = ""
    for model_id in candidate_models:
        clean_model = model_id.replace("models/", "")

        if key.startswith("AQ."):
            endpoints = [
                f"https://aiplatform.googleapis.com/v1/publishers/google/models/{clean_model}:generateContent?key={key}",
                f"https://aiplatform.googleapis.com/v1beta1/publishers/google/models/{clean_model}:generateContent?key={key}",
                f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={key}",
            ]
        else:
            endpoints = [
                f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={key}",
                f"https://aiplatform.googleapis.com/v1/publishers/google/models/{clean_model}:generateContent?key={key}",
            ]

        for gen_url in endpoints:
            try:
                response = requests.post(gen_url, json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    try:
                        return data["candidates"][0]["content"]["parts"][0][
                            "text"
                        ]
                    except Exception:
                        last_error = f"❌ Neočekávaná odpověď od Googlu: {data}"
                else:
                    last_error = (
                        f"❌ Chyba ({response.status_code}) u modelu"
                        f" {clean_model}: {response.text}"
                    )
            except Exception as e:
                last_error = f"❌ Chyba spojení: {e}"

    return last_error


# --- HLAVNÍ LOGIKA S KONTROLOU VSTUPŮ ---
if generate_clicked:
    is_mode_url = (
        vstupni_rezim == "🌐 Možnost A: Mám webovou adresu (URL odkazu)"
    )

    if not license_ok:
        st.error(
            "🔒 Pro spuštění generátoru se prosím nejprve autorizujte v horní"
            " kartě nad formulářem."
        )
    elif not api_key:
        st.warning(
            "🔑 Prosím, vložte v horní kartě svůj Google AI API klíč (návod"
            " najdete přímo pod políčkem)."
        )
    elif is_mode_url and not url_input.strip():
        st.warning("🔗 Prosím, zadejte webovou adresu (URL) produktu.")
    elif not is_mode_url and not (manual_title.strip() or manual_desc.strip()):
        st.warning(
            "📝 Prosím, vyplňte název nebo popis vašeho produktu či služby."
        )
    else:
        if is_mode_url:
            with st.spinner(
                "⏳ Načítám web, analyzuji klíčová slova a tvořím kampaň..."
            ):
                source_text = scrape_website(url_input)
                is_url = True
                hint_to_use = product_hint_url
        else:
            with st.spinner(
                "⏳ Zpracovávám váš popis produktu, hledám klíčová slova a"
                " tvořím kampaň..."
            ):
                source_text = f"Název: {manual_title}\nPopis a parametry: {manual_desc}"
                is_url = False
                hint_to_use = ""

        if is_url and source_text.startswith("Chyba"):
            st.error(source_text)
        else:
            ads_result = generate_ads(
                source_text,
                is_url,
                api_key,
                target_language,
                tone_of_voice,
                special_offer,
                hint_to_use,
            )
            if ads_result.startswith("❌"):
                st.error(ads_result)
            else:
                st.success(
                    f"✅ Kompletní kampaň i analýza klíčových slov ("
                    f"{target_language}) je připravena! Najetím myší na"
                    " libovolný rámeček zobrazíte ikonku 📋 pro zkopírování:"
                )
                st.markdown(ads_result)

# --- VLASTNÍ NADČASOVÁ PATIČKA ---
st.markdown(
    f"""
<div class="custom-footer">
    © 2026 <strong>{NAZEV_APLIKACE}</strong> | Profesionální AI nástroj pro e-shopy a marketéry
</div>
""",
    unsafe_allow_html=True,
)
