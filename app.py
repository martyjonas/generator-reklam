from bs4 import BeautifulSoup
import requests
import streamlit as st

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(
    page_title="AI Ad & Social Generator PRO", page_icon="🚀", layout="wide"
)

# --- ÚPRAVA VZHLEDU KOPÍROVACÍCH RÁMEČKŮ ---
st.markdown(
    """
<style>
div[data-testid="stCodeBlock"] pre, div[data-testid="stCode"] pre, pre, code {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    font-family: 'Source Sans Pro', sans-serif !important;
    font-size: 16px !important;
    line-height: 1.5 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("🚀 AI Generátor reklam a příspěvků (Google, FB & Instagram)")
st.write(
    "Vložte adresu produktu, zvolte tón komunikace a získejte hotové kampaně"
    " připravené ke zkopírování jedním kliknutím."
)

# --- ROZLIŠENÍ SOUKROMÉ A VEŘEJNÉ VERZE (PODLE TREZORU SECRETS) ---
saved_key = ""
try:
    if "GOOGLE_API_KEY" in st.secrets:
        saved_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    pass

if saved_key:
    api_key = saved_key
    st.sidebar.success("🔑 Soukromá verze: API klíč je uložen a aktivní!")
else:
    st.sidebar.header("⚙️ Nastavení připojení")
    api_key = st.sidebar.text_input(
        "Vložte svůj Google AI API klíč:",
        type="password",
        placeholder="AIzaSy...",
    )
    with st.sidebar.expander(
        "❓ Kde získat API klíč zdarma (za 1 minutu)?"
    ):
        st.markdown("""
        1. Klikněte na **[Google AI Studio](https://aistudio.google.com/apikey)** a přihlaste se svým Google účtem.
        2. Klikněte na modré tlačítko **Create API key**.
        3. Zkopírujte vygenerovaný kód (začíná na `AIzaSy...`) a vložte ho do políčka výše.
        """)

# --- HLAVNÍ VSTUPNÍ FORMULÁŘ ---
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
            "např. Sleva 15 % s kódem JARO15, Doprava zdarma, Dárek k nákupu..."
        ),
    )


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

    # Zpracování speciální akce
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
    1. **Analýza (krátce):** Identifikuj, co se prodává, jaký hlavní problém to zákazníkovi řeší (vyhledávací záměr) a jaké jsou hlavní benefity (USP). Odhadni 5 hlavních klíčových slov, která lidé na Google v souvislosti s tímto produktem hledají.
    
    2. **Google Ads (Responzivní reklama ve vyhledávání):**
    Vytvoř texty v nastaveném tónu komunikace ({tone}), které přesně reagují na to, co lidé hledají. Zakomponuj odhadovaná klíčová slova a případnou speciální akci. (V Google Ads nepoužívej emotikony).
    - **10 nadpisů** (STRIKTNÍ LIMIT: maximálně 30 znaků včetně mezer pro každý! Každý nadpis dej do vlastního samostatného bloku ```text ... ``` a nad něj napiš číslo nadpisu a počet znaků).
    - **4 popisy** (STRIKTNÍ LIMIT: maximálně 90 znaků včetně mezer pro každý! Každý popis dej do vlastního samostatného bloku ```text ... ``` a nad něj napiš číslo popisu a počet znaků).
    
    3. **Facebook / Instagram PLACENÁ REKLAMA (S TEMATICKÝMI EMOTIKONY):**
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

    4. **Organický (neplacený) příspěvek na Instagram (EMOCE, ZÁŽITEK, RITUÁL):**
    Vytvoř text pro běžný neplacený příspěvek na Instagram, který NEVYPADÁ jako reklama, ale jako inspirativní příspěvek (respektuj tykání/vykání ze zvoleného tónu: {tone}).
    - **Styl a tón:** Emotivní, lidský, nenásilný. Zboží propaguj nepřímo – skrze atmosféru, osobní rituál, zážitek, zpomalení v uspěchaném dni nebo radost z maličkostí.
    - **Struktura příspěvku (opět dej text příspěvku a hashtagy do samostatných bloků ```text ... ``` pro snadné kopírování):**
      * **Text příspěvku (včetně zapojení sledujících na konci):** Začni atmosférickou první větou s tematickým emotikonem. Vykresli situaci nebo rituál, ve kterém produkt přirozeně hraje roli. Čleň do krátkých odstavců s tematickými emotikony. Na konec textu polož milou otázku do komentářů a jemné nasměrování na odkaz v biu ✨ (případně nenásilně zmiň probíhající akci). (Celý tento text dej do jednoho bloku ```text ... ```).
      * **Hashtagy:** Blok 8–10 pečlivě vybraných českých hashtagů (dej je do samostatného bloku ```text ... ```).
      * **📸 Tip na fotku nebo Reels:** Napiš 1–2 věty s konkrétním nápadem, jak produkt vyfotit nebo natočit v reálné situaci, aby vizuál dokonale ladil s touto emocí.
    
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
if st.button("Vygenerovat kampaň ✨", type="primary"):
    if not api_key:
        st.warning(
            "Prosím, vložte v levém panelu svůj Google AI API klíč (návod"
            " najdete přímo pod políčkem)."
        )
    elif not url:
        st.warning("Prosím, zadejte webovou adresu (URL) produktu.")
    else:
        with st.spinner(
            "Analyzuji web, nastavuji zvolený tón komunikace a píšu texty..."
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
                        "Hotovo! Najetím myší na libovolný rámeček zobrazíte"
                        " vpravo nahoře ikonku 📋 pro zkopírování:"
                    )
                    st.markdown(ads_result)
