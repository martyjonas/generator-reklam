from bs4 import BeautifulSoup
import requests
import streamlit as st

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(
    page_title="AI Ad & Social Generator", page_icon="🚀", layout="wide"
)

# --- ÚPRAVA VZHLEDU KOPÍROVACÍCH RÁMEČKŮ (aby se dlouhé texty hezky zalamovaly) ---
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

st.title("🚀 Generátor reklam a příspěvků (Google, FB & Instagram)")
st.write(
    "Zadej URL adresu produktu nebo kategorie. Každý vygenerovaný text si můžeš"
    " zkopírovat jedním kliknutím na ikonku v pravém rohu rámečku."
)

# --- AUTOMATICKÉ NAČTENÍ KLÍČE Z TREZORU (SECRETS) ---
saved_key = ""
try:
    if "GOOGLE_API_KEY" in st.secrets:
        saved_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    pass

if saved_key:
    api_key = saved_key
    st.sidebar.success("🔑 API klíč je bezpečně uložen a připraven!")
else:
    api_key = st.sidebar.text_input(
        "Zadej svůj Google AI Studio klíč:", type="password"
    )

url = st.text_input(
    "URL adresa produktu/kategorie:", placeholder="https://www.TvujEshop.cz/..."
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
def generate_ads(web_content, key):
    key = key.strip()

    models_url = (
        f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    )
    models_resp = requests.get(models_url)

    if models_resp.status_code != 200:
        return (
            "❌ Chyba API klíče: Google klíč nepřijal. (Detail:"
            f" {models_resp.text})"
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

    prompt = f"""
    Jsi špičkový český PPC specialista, social media tvůrce a kreativní copywriter. Tvým úkolem je vytvořit vysoce konverzní reklamy a autentický obsah na sociální sítě na základě obsahu webové stránky.
    
    Zde je obsah webu:
    {web_content}
    
     ZÁSADNÍ PRAVIDLO PRO FORMÁTOVÁNÍ (KOPÍROVACÍ TLAČÍTKA):
    Každý jednotlivý reklamní text (každý z 10 nadpisů zvlášť, každý ze 4 popisů zvlášť, každý primární text, každý FB nadpis, každý FB popis i samotný Instagram text a hashtagy) MUSÍŠ uzavřít do vlastního samostatného bloku kódu pomocí trojitých zpětných uvozovek:
    ```text
    Zde bude pouze čistý text ke zkopírování
    ```
    Uvnitř bloku ```text ... ``` nesmí být žádné číslování (např. "1."), žádné uvozovky na začátku a na konci ani počet znaků – uvnitř bloku musí být POUZE čistý text, který uživatel jedním kliknutím zkopíruje a vloží rovnou do reklamního systému! Popisky (např. "Nadpis 1 (25 znaků):") piš vždy NAD daný blok.

    POSTUPUJ NÁSLEDOVNĚ:
    1. **Analýza (krátce):** Identifikuj, co se prodává, jaký hlavní problém to zákazníkovi řeší (vyhledávací záměr) a jaké jsou hlavní benefity (USP). Odhadni 5 hlavních klíčových slov, která lidé na Google v souvislosti s tímto produktem hledají.
    
    2. **Google Ads (Responzivní reklama ve vyhledávání):**
    Vytvoř texty, které přesně reagují na to, co lidé hledají. Zakomponuj odhadovaná klíčová slova. (V Google Ads nepoužívej emotikony).
    - **10 nadpisů** (STRIKTNÍ LIMIT: maximálně 30 znaků včetně mezer pro každý! Každý nadpis dej do vlastního samostatného bloku ```text ... ``` a nad něj napiš číslo nadpisu a počet znaků).
    - **4 popisy** (STRIKTNÍ LIMIT: maximálně 90 znaků včetně mezer pro každý! Každý popis dej do vlastního samostatného bloku ```text ... ``` a nad něj napiš číslo popisu a počet znaků).
    *Styl: Úderný, zaměřený na benefity, čísla, slevy, vyřešení problému a výzvu k akci (CTA).*
    
    3. **Facebook / Instagram PLACENÁ REKLAMA (S TEMATICKÝMI EMOTIKONY):**
    Lidé na FB produkt aktivně nehledají, musíš je zastavit ve scrollování. Buď kreativní, originální, vyhni se klišé.
    DŮLEŽITÉ PRO EMOTIKONY: Vyber emotikony, které PŘESNĚ tematicky sedí k danému produktu nebo oboru a použij je pro vizuální oživení textu!
    
    Vytvoř 2 varianty:
    - **Varianta A (Rámec PAS - Problém, Agitace, Řešení):** Zaměř se na bolest/potřebu zákazníka a ukaž produkt jako ideální řešení.
    - **Varianta B (Zaměřeno na emoce / Lifestyle / Originalitu):** Vtipný, nebo velmi poutavý úhel pohledu.
    
    U obou variant dej každou z těchto 3 částí do vlastního samostatného bloku ```text ... ```:
    - **Primární text (HLAVNÍ TEXT NAD OBRÁZKEM – vidět jako první):** 
      * První věta (tzv. Hook) musí okamžitě zaujmout a obsahovat 1–2 tematické emotikony.
      * Následuje poutavý text a přehledný seznam hlavních benefitů, kde každá odrážka začíná tematickým emotikonem souvisejícím s produktem.
      * Na konci jasná výzva k akci (CTA) s emotikonem (např. 👉, 🛒).
    - **Nadpis / Headline (TUČNÝ TEXT POD OBRÁZKEM vedle tlačítka - max 40 znaků):** Krátký, úderný benefit + přidej na začátek 1 výrazný tematický emotikon.
    - **Popis / Description (DOPLŇUJÍCÍ TEXT POD NADPISEM - max 30 znaků):** Krátký důkaz nebo výhoda s emotikonem (např. ⭐ Skladem, 🚚 Doprava zdarma).

    4. **Organický (neplacený) příspěvek na Instagram (EMOCE, ZÁŽITEK, RITUÁL):**
    Vytvoř text pro běžný neplacený příspěvek na Instagram, který NEVYPADÁ jako reklama, ale jako inspirativní příspěvek.
    - **Styl a tón:** Emotivní, lidský, hřejivý, nenásilný. Zboží propaguj nepřímo – skrze atmosféru, osobní rituál, zážitek, zpomalení v uspěchaném dni nebo radost z maličkostí.
    - **Struktura příspěvku (opět dej text příspěvku a hashtagy do samostatných bloků ```text ... ``` pro snadné kopírování):**
      * **Text příspěvku (včetně zapojení sledujících na konci):** Začni atmosférickou první větou s tematickým emotikonem. Vykresli situaci nebo rituál, ve kterém produkt přirozeně hraje roli. Čleň do krátkých odstavců s tematickými emotikony. Na konec textu polož milou otázku do komentářů a jemné nasměrování na odkaz v biu ✨. (Celý tento text dej do jednoho bloku ```text ... ```).
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
if st.button("Vygenerovat kampaň ✨"):
    if not api_key:
        st.warning(
            "Prosím, zadej v levém panelu svůj Google AI Studio API klíč."
        )
    elif not url:
        st.warning("Prosím, zadej URL adresu.")
    else:
        with st.spinner(
            "Analyzuji web, zkoumám psychologii zákazníků a píšu texty..."
        ):
            scraped_text = scrape_website(url)
            if scraped_text.startswith("Chyba"):
                st.error(scraped_text)
            else:
                ads_result = generate_ads(scraped_text, api_key)
                if ads_result.startswith("❌"):
                    st.error(ads_result)
                else:
                    st.success(
                        "Hotovo! Najetím myší na libovolný šedý rámeček"
                        " zobrazíš vpravo nahoře ikonku pro zkopírování:"
                    )
                    st.markdown(ads_result)
