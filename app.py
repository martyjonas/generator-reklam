from bs4 import BeautifulSoup
import requests
import streamlit as st

# ==============================================================================
# 🎨 NASTAVENÍ ZNAČKY (Zde si můžeš kdykoliv změnit texty a licenční heslo)
# ==============================================================================
NAZEV_APLIKACE = "AI Marketing Studio PRO"
PODTITULEK_APLIKACE = (
    "Chytrý generátor vysoce konverzních reklam pro Google, Facebook a"
    " Instagram"
)
NAZEV_TVE_ZNACKY = "Martin Jonas Studio"  # Změň si na název svého e-shopu/značky
ODKAZ_NA_TVUJ_WEB = "https://www.martinjonas.cz"  # Změň si na adresu svého webu
LICENCNI_KOD_PRO_ZAKAZNIKY = (
    "START2026"  # Heslo, které dáš zákazníkům po nákupu
)
# ==============================================================================

st.set_page_config(page_title=NAZEV_APLIKACE, page_icon="✨", layout="wide")

# --- MODERNÍ PROFI DESIGN (CSS STYLOVÁNÍ) ---
st.markdown(
    """
<style>
/* Skrytí výchozí patičky Streamlitu */
footer {visibility: hidden;}

/* Horní luxusní banner s barevným přechodem */
.hero-banner {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #6b46c1 100%);
    padding: 35px 30px;
    border-radius: 16px;
    color: white;
    margin-bottom: 25px;
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

/* Vzhled kopírovacích rámečků */
div[data-testid="stCodeBlock"] pre, div[data-testid="stCode"] pre, pre, code {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    font-family: 'Source Sans Pro', sans-serif !important;
    font-size: 16px !important;
    line-height: 1.55 !important;
    background-color: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
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

# --- LEVÝ PANEL (SOUKROMÁ VERZE vs. ZÁKAZNICKÁ VERZE S LICENCÍ) ---
saved_key = ""
try:
    if "GOOGLE_API_KEY" in st.secrets:
        saved_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    pass

st.sidebar.markdown(f"### 🛡️ {NAZEV_APLIKACE}")
st.sidebar.caption(f"Oficiální nástroj od [{NAZEV_TVE_ZNACKY}]({ODKAZ_NA_TVUJ_WEB})")
st.sidebar.markdown("---")

if saved_key:
    api_key = saved_key
    license_ok = True
    st.sidebar.success("🔑 VIP Majitelská verze: Klíč je aktivní!")
else:
    st.sidebar.subheader("1️⃣ Aktivace licence")
    user_license = st.sidebar.text_input(
        "Zadejte licenční kód z objednávky:",
        type="password",
        placeholder="Např. START2026",
    )

    if user_license.strip() == LICENCNI_KOD_PRO_ZAKAZNIKY:
        license_ok = True
        st.sidebar.success("✅ Licence úspěšně ověřena!")
    else:
        license_ok = False
        if user_license:
            st.sidebar.error("❌ Neplatný licenční kód.")

    st.sidebar.subheader("2️⃣ Váš Google AI klíč")
    api_key = st.sidebar.text_input(
        "Vložte svůj Google AI API klíč:",
        type="password",
        placeholder="AIzaSy...",
    )

    with st.sidebar.expander("❓ Jak získat klíč zdarma (za 1 minutu)?"):
        st.markdown("""
        1. Otevřete **[Google AI Studio](https://aistudio.google.com/apikey)** a přihlaste se svým Google účtem.
        2. Klikněte na modré tlačítko **Create API key**.
        3. Zkopírujte vygenerovaný kód (začíná na `AIzaSy...`) a vložte ho do políčka výše.
        """)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Tip:** Po vygenerování kampaně stačí najet myší na libovolný text a"
    " kliknout vpravo nahoře na ikonku 📋 pro zkopírování."
)

# --- HLAVNÍ VSTUPNÍ FORMULÁŘ V KARTĚ ---
with st.container(border=True):
    st.markdown("#### 🎯 Nastavení vaší kampaně")
    url = st.text_input(
        "🔗 1. Webová adresa (URL) produktu nebo kategorie:",
        placeholder="https://www.VasEshop.cz/produkt...",
    )

    col1, col2 = st.columns(2)
    with col1:
        tone_of_voice = st.selectbox(
            "🗣️ 2. Tón komunikace značky (Tone of Voice):",
            [
                "Přátelský a blízký (tykání)",
                "Profesionální a důvěryhodný (vykání)",
                "Luxusní, prémiový a exkluzivní (vykání)",
                "Vtipný, hravý a originální (tykání)",
                "Akční, naléhavý a čistě prodejní (vykání)",
                "Jemný, empatický a pečující (vykání)",
            ],
        )
    with col2:
        special_offer = st.text_input(
            "🎁 3. Aktuální akce, sleva nebo výhoda (nepovinné):",
            placeholder=(
                "např. Sleva 15 % s kódem JARO15, Doprava zdarma, Dárek k"
                " nákupu..."
            ),
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
def generate_ads(web_content, key, tone, offer):
    key = key.strip()

    models_url = (
        f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    )
    models_resp = requests.get(models_url)

    if models_resp.status_code != 200:
        return (
            "❌ Chyba API klíče: Google klíč nepřijal. Zkontrolujte, zda jste"
            " ho zkopírovali celý a zda začíná na AIzaSy..."
        )

    models_data = models_resp.json().get("models", [])
    available_models = [
        m["name"]
        for m in models_data
        if "generateContent" in m.get("supportedGenerationMethods", [])
        and "gemini" in m["name"]
    ]

    candidate_models = [
        "models/gemini-3.8-flash",
        "models/gemini-3.8-pro",
    ]
    for m in sorted(available_models, reverse=True):
        if m not in candidate_models:
            candidate_models.append(m)

    if offer.strip():
        offer_instruction = (
            f"Uživatel zadal tuto speciální akci/výhodu: '{offer.strip()}'."
            " Výrazně a přirozeně ji zakomponuj do nadpisů a popisů v Google"
            " Ads, do obou variant Facebook reklamy (jako silný argument k"
            " nákupu) a jemně ji zmiň i v závěru Instagram příspěvku!"
        )
    else:
        offer_instruction = (
            "Nebyla zadána žádná speciální akce, čerpej čistě z výhod a"
            " informací na webu."
        )

    prompt = f"""
    Jsi špičkový český PPC specialista, social media tvůrce a kreativní copywriter. Tvým úkolem je vytvořit vysoce konverzní reklamy a autentický obsah na sociální sítě na základě obsahu webové stránky.
    
    Zde je obsah webu:
    {web_content}
    
    🎯 NASTAVENÍ KAMPANĚ OD UŽIVATELE (STRIKTNĚ DODRŽ!):
    - **Požadovaný tón komunikace (Tone of Voice):** {tone}. Tomuto stylu, emocím a zvolenému tykání nebo vykání 100% přizpůsob úplně všechny generované texty!
    - **Speciální akce / výhoda:** {offer_instruction}
    
    📋 ZÁSADNÍ PRAVIDLO PRO FORMÁTOVÁNÍ (KOPÍROVACÍ TLAČÍTKA):
    Každý jednotlivý reklamní text (každý z 10 nadpisů zvlášť, každý ze 4 popisů zvlášť, každý primární text, každý FB nadpis, každý FB popis i samotný Instagram text a hashtagy) MUSÍŠ uzavřít do vlastního samostatného bloku kódu pomocí trojitých zpětných uvozovek:
    ```text
    Zde bude pouze čistý text ke zkopírování
    ```
    Uvnitř bloku ```text ... ``` nesmí být žádné číslování (např. "1."), žádné uvozovky na začátku a na konci ani počet znaků – uvnitř bloku musí být POUZE čistý text, který uživatel jedním kliknutím zkopíruje a vloží rovnou do reklamního systému! Popisky (např. "Nadpis 1 (25 znaků):") piš vždy NAD daný blok.

    POSTUPUJ NÁSLEDOVNĚ:
    1. **📊 Analýza produktu a klíčových slov (krátce):** Identifikuj, co se prodává, jaký hlavní problém to zákazníkovi řeší a jaké jsou hlavní benefity (USP). Odhadni 5 hlavních klíčových slov, která lidé na Google v souvislosti s tímto produktem hledají.
    
    2. **🔍 Google Ads (Responzivní reklama ve vyhledávání):**
    Vytvoř texty v nastaveném tónu komunikace ({tone}), které přesně reagují na to, co lidé hledají. Zakomponuj odhadovaná klíčová slova a případnou speciální akci. (V Google Ads nepoužívej emotikony).
    - **10 nadpisů** (STRIKTNÍ LIMIT: maximálně 30 znaků včetně mezer pro každý! Každý nadpis dej do vlastního samostatného bloku ```text ... ``` a nad něj napiš číslo nadpisu a počet znaků).
    - **4 popisy** (STRIKTNÍ LIMIT: maximálně 90 znaků včetně mezer pro každý! Každý popis dej do vlastního samostatného bloku ```text ... ``` a nad něj napiš číslo popisu a počet znaků).
    
    3. **📱 Facebook / Instagram PLACENÁ REKLAMA (S TEMATICKÝMI EMOTIKONY):**
    Lidé na FB produkt aktivně nehledají, musíš je zastavit ve scrollování. Piš ve zvoleném tónu ({tone}).
    DŮLEŽITÉ PRO EMOTIKONY: Vyber emotikony, které PŘESNĚ tematicky sedí k danému produktu nebo oboru a použij je pro vizuální oživení textu!
    
    Vytvoř 2 varianty:
    - **Varianta A (Rámec PAS - Problém, Agitace, Řešení):** Zaměř se na bolest/potřebu zákazníka a ukaž produkt jako ideální řešení.
    - **Varianta B (Zaměřeno na emoce / Lifestyle / Originalitu):** Poutavý úhel pohledu přesně v duchu zvoleného tónu komunikace.
    
    U obou variant dej každou z těchto 3 částí do vlastního samostatného bloku ```text ... ```:
    - **Primární text (HLAVNÍ TEXT NAD OBRÁZKEM – vidět jako první):** 
      * První věta (tzv. Hook) musí okamžitě zaujmout a obsahovat 1–2 tematické emotikony.
      * Následuje poutavý text a přehledný seznam hlavních benefitů (včetně případné speciální akce), kde každá odrážka začíná tematickým emotikonem souvisejícím s produktem.
      * Na konci jasná výzva k akci (CTA) s emotikonem (např. 👉, 🛒).
    - **Nadpis / Headline (TUČNÝ TEXT POD OBRÁZKEM vedle tlačítka - max 40 znaků):** Krátký, úderný benefit nebo akce + přidej na začátek 1 výrazný tematický emotikon.
    - **Popis / Description (DOPLŇUJÍCÍ TEXT POD NADPISEM - max 30 znaků):** Krátký důkaz nebo výhoda s emotikonem (např. ⭐ Skladem, 🚚 Doprava zdarma).

    4. **📸 Organický (neplacený) příspěvek na Instagram (EMOCE, ZÁŽITEK, RITUÁL):**
    Vytvoř text pro běžný neplacený příspěvek na Instagram, který NEVYPADÁ jako reklama, ale jako inspirativní příspěvek (respektuj tykání/vykání ze zvoleného tónu: {tone}).
    - **Styl a tón:** Emotivní, lidský, nenásilný. Zboží propaguj nepřímo – skrze atmosféru, osobní rituál, zážitek, zpomalení v uspěchaném dni nebo radost z maličkostí.
    - **Struktura příspěvku (opět dej text příspěvku a hashtagy do samostatných bloků ```text ... ``` pro snadné kopírování):**
      * **Text příspěvku (včetně zapojení sledujících na konci):** Začni atmosférickou první větou s tematickým emotikonem. Vykresli situaci nebo rituál, ve kterém produkt přirozeně hraje roli. Čleň do krátkých odstavců s tematickými emotikony. Na konec textu polož milou otázku do komentářů a jemné nasměrování na odkaz v biu ✨ (případně nenásilně zmiň probíhající akci). (Celý tento text dej do jednoho bloku ```text ... ```).
      * **Hashtagy:** Blok 8–10 pečlivě vybraných českých hashtagů (dej je do samostatného bloku ```text ... ```).
      * **🎬 Tip na fotku nebo Reels:** Napiš 1–2 věty s konkrétním nápadem, jak produkt vyfotit nebo natočit v reálné situaci, aby vizuál dokonale ladil s touto emocí.
    
    Piš perfektní, přirozenou češtinou. Žádné strojové překlady typu "Odemkněte svůj potenciál".
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.75},
    }

    last_error = ""
    for chosen_model in candidate_models:
        gen_url = f"https://generativelanguage.googleapis.com/v1beta/{chosen_model}:generateContent?key={key}"
        response = requests.post(gen_url, json=payload, timeout=60)

        if response.status_code == 200:
            data = response.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                last_error = f"❌ Neočekávaná odpověď od Googlu: {data}"
        else:
            last_error = f"❌ Chyba ({response.status_code}) u modelu {chosen_model}: {response.text}"
            if response.status_code in [404, 400]:
                continue
            else:
                break

    return last_error


# --- HLAVNÍ LOGIKA APLIKACE ---
if generate_clicked:
    if not license_ok:
        st.error(
            "🔒 Pro spuštění generátoru zadejte prosím v levém panelu platný"
            " licenční kód z vaší objednávky."
        )
    elif not api_key:
        st.warning(
            "🔑 Prosím, vložte v levém panelu svůj Google AI API klíč (návod"
            " najdete přímo pod políčkem)."
        )
    elif not url:
        st.warning("🔗 Prosím, zadejte webovou adresu (URL) produktu.")
    else:
        with st.spinner(
            "⏳ Analyzuji web, nastavuji tón značky a tvořím vaši kampaň..."
        ):
            scraped_text = scrape_website(url)
            if scraped_text.startswith("Chyba"):
                st.error(scraped_text)
            else:
                ads_result = generate_ads(
                    scraped_text, api_key, tone_of_voice, special_offer
                )
                if ads_result.startswith("❌"):
                    st.error(ads_result)
                else:
                    st.success(
                        "✅ Kampaň je připravena! Najetím myší na libovolný"
                        " rámeček zobrazíte vpravo nahoře ikonku 📋 pro"
                        " zkopírování:"
                    )
                    st.markdown(ads_result)

# --- VLASTNÍ PATIČKA ---
st.markdown(
    f"""
<div class="custom-footer">
    © 2026 <strong>{NAZEV_APLIKACE}</strong> | Vytvořeno exkluzivně pro zákazníky <a href="{ODKAZ_NA_TVUJ_WEB}" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: bold;">{NAZEV_TVE_ZNACKY}</a>
</div>
""",
    unsafe_allow_html=True,
)
