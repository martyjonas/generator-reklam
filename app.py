from bs4 import BeautifulSoup
import requests
import streamlit as st

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(
    page_title="AI Ad Generator", page_icon="🚀", layout="wide"
)
st.title("🚀 Generátor konverzních reklam (Google & FB)")
st.write(
    "Zadej URL adresu produktu nebo kategorie a získej hotové reklamní kampaně."
)

# --- ZADÁNÍ API KLÍČE A URL ---
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
    key = key.strip()  # Odstranění případných mezer okolo klíče

    # 1. Automatické zjištění dostupného modelu na tvém Google účtu
    models_url = (
        f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    )
    models_resp = requests.get(models_url)

    if models_resp.status_code != 200:
        return (
            "❌ Chyba API klíče: Google klíč nepřijal. Zkontroluj, zda začíná"
            f" na AIza... (Detail: {models_resp.text})"
        )

    models_data = models_resp.json().get("models", [])
    available_models = [
        m["name"]
        for m in models_data
        if "generateContent" in m.get("supportedGenerationMethods", [])
        and "gemini" in m["name"]
    ]

    # Výběr nejlepšího modelu, který máš k dispozici
    preferred = [
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash",
        "models/gemini-1.5-pro",
        "models/gemini-1.5-flash",
    ]
    chosen_model = None
    for p in preferred:
        if p in available_models:
            chosen_model = p
            break
    if not chosen_model and available_models:
        chosen_model = available_models[0]
    if not chosen_model:
        return "❌ Na tvém Google účtu nebyl nalezen žádný textový model Gemini."

    # 2. Zadání (Prompt) pro umělou inteligenci
    prompt = f"""
    Jsi špičkový český PPC specialista a kreativní copywriter. Tvým úkolem je vytvořit vysoce konverzní, originální a poutavé reklamní texty na základě obsahu webové stránky.
    
    Zde je obsah webu:
    {web_content}
    
    POSTUPUJ NÁSLEDOVNĚ:
    1. **Analýza (krátce):** Identifikuj, co se prodává, jaký hlavní problém to zákazníkovi řeší (vyhledávací záměr) a jaké jsou hlavní benefity (USP). Odhadni 5 hlavních klíčových slov, která lidé na Google v souvislosti s tímto produktem hledají.
    
    2. **Google Ads (Responzivní reklama ve vyhledávání):**
    Vytvoř texty, které přesně reagují na to, co lidé hledají. Zakomponuj odhadovaná klíčová slova.
    - Vytvoř 10 nadpisů (STRIKTNÍ LIMIT: maximálně 30 znaků včetně mezer pro každý! Počítej znaky!).
    - Vytvoř 4 popisy (STRIKTNÍ LIMIT: maximálně 90 znaků včetně mezer pro každý!).
    *Styl: Úderný, zaměřený na benefity, čísla, slevy, vyřešení problému a výzvu k akci (CTA).*
    
    3. **Facebook / Instagram Ads:**
    Lidé na FB produkt aktivně nehledají, musíš je zastavit ve scrollování. Buď kreativní, originální, vyhni se klišé.
    - **Varianta A (Rámec PAS - Problém, Agitace, Řešení):** Zaměř se na bolest zákazníka a ukaž produkt jako záchranu.
    - **Varianta B (Zaměřeno na emoce / Lifestyle / Originalitu):** Vtipný, nebo velmi poutavý úhel pohledu (tzv. Hook).
    U obou variant napiš:
    - Primární text (hlavní text příspěvku, použij odrážky a emoji s mírou).
    - Nadpis (Headline - max 40 znaků, tučný text pod obrázkem).
    - Popis (Description - max 30 znaků, doplňující text).
    
    Piš perfektní, přirozenou češtinou. Žádné strojové překlady typu "Odemkněte svůj potenciál".
    """

    # 3. Odeslání požadavku přímo do Googlu
    gen_url = f"https://generativelanguage.googleapis.com/v1beta/{chosen_model}:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7},
    }

    response = requests.post(gen_url, json=payload, timeout=60)
    if response.status_code != 200:
        return (
            f"❌ Chyba při generování ({response.status_code}): {response.text}"
        )

    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return f"❌ Neočekávaná odpověď od Googlu: {data}"


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
                    st.success("Hotovo! Zde jsou tvé kampaně:")
                    st.markdown(ads_result)
