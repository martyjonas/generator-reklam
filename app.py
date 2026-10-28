from bs4 import BeautifulSoup
from openai import OpenAI
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
def scrape_website(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        for script in soup(["script", "style", "nav", "footer"]):
            script.extract()

        text = soup.get_text(separator=" ")
        lines = (line.strip() for line in text.splitlines())
        clean_text = " ".join(line for line in lines if line)
        return clean_text[:10000]
    except Exception as e:
        return f"Chyba při načítání webu: {e}"


# --- FUNKCE PRO GENEROVÁNÍ REKLAM PŘES GOOGLE GEMINI ---
def generate_ads(web_content, api_key):
    # Napojení na Google AI Studio
    client = OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    prompt = f"""
    Jsi seniorní PPC specialista a kreativní copywriter. Tvým úkolem je vytvořit vysoce konverzní, originální a poutavé reklamní texty na základě obsahu webové stránky.
    
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

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {
                "role": "system",
                "content": "Jsi špičkový český copywriter a marketingový stratég.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content


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
            if "Chyba" in scraped_text:
                st.error(scraped_text)
            else:
                ads_result = generate_ads(scraped_text, api_key)
                st.success("Hotovo! Zde jsou tvé kampaně:")
                st.markdown(ads_result)
