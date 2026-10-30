import hashlib
import json
import os
from bs4 import BeautifulSoup
import requests
import streamlit as st

# ==============================================================================
# 🎨 BRAND & GUMROAD CONFIGURATION
# ==============================================================================
APP_NAME = "AI Marketing Studio Global PRO"
APP_SUBTITLE = "Instant High-Converting Ads & Keyword Strategy for Google, Meta & Instagram"
BRAND_NAME = "AI Marketing Studio"
GUMROAD_PRODUCT_ID = (
    "K78kgNe50ECXOy403pPUTw=="  # Tvé přesné Product ID z Gumroadu!
)
# ==============================================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- MODERN ULTRA-CLEAN CSS STYLING ---
st.markdown(
    """
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stAppDeployButton {display: none !important;}
section[data-testid="stSidebar"] {display: none;}

.hero-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #4338ca 100%);
    padding: 35px 30px;
    border-radius: 16px;
    color: white;
    margin-bottom: 20px;
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.25);
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

div[data-testid="stCodeBlock"] pre, div[data-testid="stCode"] pre {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
    font-size: 15px !important;
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
    font-family: 'Inter', -apple-system, sans-serif !important;
    font-size: 15px !important;
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}

div[data-testid="stRadio"] > div {
    background: #f1f5f9;
    padding: 8px;
    border-radius: 12px;
    gap: 12px;
}
div[data-testid="stRadio"] label {
    background: white;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

div.stButton > button:first-child {
    background: linear-gradient(90deg, #2563eb 0%, #4f46e5 100%);
    color: white;
    border: none;
    padding: 16px 32px;
    font-size: 19px;
    font-weight: 800;
    border-radius: 10px;
    width: 100%;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
    transition: all 0.2s ease;
    margin-top: 10px;
}
div.stButton > button:first-child:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.45);
}

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


# --- AUTOMATICKÉ OVĚŘOVÁNÍ LICENCÍ PROTI GUMROAD API ---
LICENSE_DB_FILE = "activated_licenses_global.json"


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


def verify_and_lock_license(code, user_api_key):
    code = code.strip()
    clean_key = user_api_key.strip()

    if len(code) < 6:
        return False, "❌ Invalid license key format. Please check your order."

    # 1. Živé ověření přímo proti serverům Gumroadu
    try:
        gum_resp = requests.post(
            "https://api.gumroad.com/v2/licenses/verify",
            data={"product_id": GUMROAD_PRODUCT_ID, "license_key": code},
            timeout=10,
        )
        if gum_resp.status_code == 200 and gum_resp.json().get(
            "success", False
        ):
            is_valid = True
        else:
            # Podpora i pro ručně vygenerované GLOBAL- kódy nebo offline testování
            is_valid = code.startswith("GLOBAL-") or len(code) > 20
    except Exception:
        is_valid = True

    if not is_valid:
        return False, "❌ License key not found or refunded on Gumroad."

    if not clean_key:
        return (
            True,
            (
                "✅ License verified! Now please enter your Google AI Key"
                " beside."
            ),
        )

    # 2. Spárování s Google AI klíčem
    key_hash = hashlib.sha256(clean_key.encode()).hexdigest()
    db = get_activated_licenses()

    if code not in db:
        db[code] = key_hash
        save_activated_licenses(db)
        return (
            True,
            "✅ License successfully activated and bound to your API key!",
        )
    else:
        if db[code] == key_hash:
            return True, "✅ License active and verified!"
        else:
            return (
                False,
                (
                    "❌ This license has already been activated by another user"
                    " key."
                ),
            )


# --- HERO BANNER ---
st.markdown(
    f"""
<div class="hero-banner">
    <div class="hero-title">✨ {APP_NAME}</div>
    <div class="hero-subtitle">{APP_SUBTITLE}</div>
</div>
""",
    unsafe_allow_html=True,
)

# --- RECOVER SECRETS ---
saved_key = ""
try:
    if "GOOGLE_API_KEY" in st.secrets:
        saved_key = st.secrets["GOOGLE_API_KEY"].strip()
except Exception:
    pass

# --- AUTHORIZATION ACCORDION ---
if saved_key:
    api_key = saved_key
    license_ok = True
    with st.expander("🔑 VIP Owner Mode (Master API Key is active)"):
        st.success("You are running in VIP Owner Mode.")
else:
    with st.expander(
        "🔑 License Activation & Google AI Key Setup", expanded=True
    ):
        col_lic1, col_lic2 = st.columns(2)
        with col_lic1:
            user_license = st.text_input(
                "1️⃣ Enter your Gumroad license key from your receipt:",
                placeholder="Paste your license key here...",
            )
        with col_lic2:
            api_key = st.text_input(
                "2️⃣ Enter your Google AI API key (Lifetime Free):",
                type="password",
                placeholder="Paste your key from Google AI Studio...",
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
            "❓ **Need your free Google AI Key?** Visit **[Google AI"
            " Studio](https://aistudio.google.com/apikey)**, click **Create API"
            " key**, and paste it above. It takes 60 seconds and is completely"
            " free."
        )

# --- MAIN FORM CONTAINER ---
with st.container(border=True):
    st.markdown("#### 🎯 1. How would you like to provide your product?")

    input_mode = st.radio(
        "Choose input mode:",
        [
            "🌐 Option A: From Web URL (eCommerce / Landing page)",
            "✍️ Option B: From Product Description (No website needed)",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    url_input = ""
    product_hint_url = ""
    manual_title = ""
    manual_desc = ""

    st.write("")
    if "Option A" in input_mode:
        col_u1, col_u2 = st.columns([1.2, 1])
        with col_u1:
            url_input = st.text_input(
                "🔗 Product or Category URL:",
                placeholder="https://www.your-store.com/product...",
            )
        with col_u2:
            product_hint_url = st.text_input(
                "🎯 Audience / Product Specification (Optional):",
                placeholder=(
                    "e.g. Premium gift for women, target beginners, B2B"
                    " wholesale..."
                ),
            )
    else:
        manual_title = st.text_input(
            "📦 Product or Service Name:",
            placeholder=(
                "e.g. Ergonomic Memory Foam Pillow / 1-on-1 Executive Coaching"
            ),
        )
        manual_desc = st.text_area(
            "📝 Description, Key Features & Specifications:",
            placeholder=(
                "Describe what your product does, materials, key benefits,"
                " target audience, problem it solves, guarantees..."
            ),
            height=110,
        )

    st.markdown("---")
    st.markdown("#### ⚙️ 2. Campaign Targeting & Tone")
    col1, col2, col3 = st.columns(3)
    with col1:
        target_language = st.selectbox(
            "🌍 Output Language & Market:",
            [
                "🇺🇸 English (US / Global)",
                "🇬🇧 English (UK)",
                "🇩🇪 German (Deutsch)",
                "🇫🇷 French (Français)",
                "🇪🇸 Spanish (Español)",
                "🇮🇹 Italian (Italiano)",
                "🇵🇹 Portuguese (Português)",
                "🇳🇱 Dutch (Nederlands)",
                "🇵🇱 Polish (Polski)",
                "🇨🇿 Czech (Čeština)",
                "🇸🇰 Slovak (Slovenčina)",
            ],
        )
    with col2:
        tone_of_voice = st.selectbox(
            "🗣️ Brand Tone of Voice:",
            [
                "Conversational & Friendly (Casual / Relatable)",
                "Professional & Authoritative (Corporate / Trustworthy)",
                "Luxury, Sophisticated & High-End (Exclusive)",
                "Witty, Playful & Bold (Entertaining / Quirky)",
                "Direct Response & Urgent (High-Conversion Sales)",
                "Empathetic, Gentle & Caring (Wellness / Lifestyle)",
            ],
        )
    with col3:
        special_offer = st.text_input(
            "🎁 Special Offer / Discount Promo (Optional):",
            placeholder=(
                "e.g. Free Worldwide Shipping, 15% OFF with code SUMMER15..."
            ),
        )

    st.write("")
    is_mode_url = "Option A" in input_mode
    has_valid_input = bool(
        url_input.strip()
        if is_mode_url
        else (manual_title.strip() or manual_desc.strip())
    )

    if not license_ok:
        st.warning(
            "🔒 Please enter and verify your license key in the top box."
        )
    elif not api_key.strip():
        st.warning("🔑 Missing Google AI API key in the top box.")
    elif not has_valid_input:
        if is_mode_url:
            st.info("ℹ️ Please enter a valid product URL above to proceed.")
        else:
            st.info(
                "ℹ️ Please describe your product or service above to proceed."
            )
    else:
        st.success("🟢 Ready to generate your high-converting campaign!")

    generate_clicked = st.button("✨ Generate Full Campaign")

status_placeholder = st.empty()


# --- SCRAPING FUNCTION ---
def scrape_website(target_url):
    try:
        target_url = target_url.strip()
        if not target_url.startswith("http"):
            target_url = "https://" + target_url

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        for script in soup(["script", "style", "nav", "footer"]):
            script.extract()

        text = soup.get_text(separator=" ")
        lines = (line.strip() for line in text.splitlines())
        clean_text = " ".join(line for line in lines if line)
        return clean_text[:12000]
    except Exception as e:
        return f"Error reading website content: {e}"


# --- 100% TIMELESS DYNAMIC ENGINE ---
def generate_ads(source_content, is_url_source, key, lang, tone, offer, hint):
    key = key.strip()
    headers = {"Content-Type": "application/json", "x-goog-api-key": key}

    discovered_models = []
    try:
        models_url = "https://generativelanguage.googleapis.com/v1beta/models"
        res = requests.get(
            models_url, headers=headers, params={"key": key}, timeout=8
        )
        if res.status_code == 200:
            for item in res.json().get("models", []):
                m_name = item.get("name", "").replace("models/", "")
                methods = item.get("supportedGenerationMethods", [])
                if "generateContent" in methods and "gemini" in m_name.lower():
                    discovered_models.append(m_name)
    except Exception:
        pass

    candidate_models = sorted(discovered_models, reverse=True)
    fallback_list = [
        "gemini-3.8-flash",
        "gemini-3.8-pro",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]
    for fb in fallback_list:
        if fb not in candidate_models:
            candidate_models.append(fb)

    if hint.strip():
        hint_instruction = f"""
    ⚠️ CRITICAL USER SPECIFICATION:
    The user explicitly specified: "{hint.strip()}".
    This user note takes 100% PRIORITY over any inferred assumptions from the raw content. Tailor the positioning, audience, and keywords accordingly.
    """
    else:
        hint_instruction = ""

    if offer.strip():
        offer_instruction = (
            f"The user has an active promotion: '{offer.strip()}'."
            " Seamlessly incorporate this offer into Google Search Ads"
            " headlines/descriptions, Meta ad angles, and the closing CTA of"
            " the Instagram post!"
        )
    else:
        offer_instruction = (
            "No special promotion provided. Focus on primary product benefits"
            " and unique selling propositions."
        )

    source_label = (
        "Here is the product content extracted from the website:"
        if is_url_source
        else "Here are the product details provided directly by the user:"
    )

    prompt = f"""
    You are a world-class direct-response copywriter, PPC strategist, and social media creative director. Your mission is to analyze the product and create an elite, high-converting ad campaign.
    
    {source_label}
    {source_content}
    
    🎯 HUMAN COPYWRITING RULES (STRICT COMPLIANCE):
    - **Write like a real human.** Speak like a smart, knowledgeable friend explaining a brilliant discovery over a good cup of coffee.
    - **ZERO corporate fluff, marketing clichés, or AI buzzwords.** NEVER use words like "tapestry", "delve", "unlock your potential", "elevate your journey", "game-changer", "testament", or "seamless synergy".
    - **STRICTLY NO em-dashes (—).** Use natural cadence, periods, commas, or standard hyphens (-).
    - **Never sound like a press release or a corporate manual.**
    - Write punchy, persuasive, clear, and authentic copy designed to sell.

    🎯 TARGETING & TONE SPECIFICATIONS:
    {hint_instruction}
    - **Target Language & Market:** {lang}.
      IMPORTANT: Keep section headings and character counts in English for universal clarity, but **ALL actual ad copy, headlines, descriptions, keywords, social posts, and hashtags MUST be written natively in fluent, culturally attuned {lang} as written by an elite local copywriter.**
    - **Tone of Voice:** {tone}.
    - **Special Offer:** {offer_instruction}
    
    📋 1-CLICK COPY FORMATTING RULES:
    Every single ad component (each headline, each description, each primary text, each hook, keywords list) MUST be wrapped inside its own individual code block using triple backticks:
    ```text
    Clean copy ready to copy-paste in {lang}
    ```
    Inside the ```text ... ``` block, do NOT include numbering (like "1."), quotes, or character counts. ONLY pure copy that can be directly pasted into Google Ads or Meta Ads Manager. Put titles and character counts outside the blocks.

    DELIVER IN THESE 5 STRUCTURED SECTIONS:

    ### 📊 1. Product & Audience Psychology Breakdown
    Briefly analyze:
    - What is being sold and who the ideal buyer persona is.
    - Core emotional pain point or primary desire solved.
    - Top 3 Unique Selling Propositions (USPs).

    ### 🔑 2. High-Intent Keywords ({lang})
    Create 3 clean copyable blocks:
    - **🔥 Primary High-Converting Commercial Keywords (10-12 phrases in {lang}):** Search terms with immediate buyer intent. (One code block).
    - **🎯 Long-Tail Keywords (8-10 phrases in {lang}):** Specific, cost-effective high-intent search queries. (One code block).
    - **🚫 Negative Keywords (6-8 words in {lang}):** Non-buyer terms (e.g., free, jobs, tutorial, torrent, cheap, DIY) to eliminate wasted ad spend. (One code block).

    ### 🔍 3. Google Search Ads (Responsive Search Ads in {lang})
    Create punchy, benefit-driven text using the target keywords:
    - **10x Headlines** (STRICT LIMIT: Maximum 30 characters including spaces each! Put each in its own ```text``` block with character count outside).
    - **4x Descriptions** (STRICT LIMIT: Maximum 90 characters including spaces each! Put each in its own ```text``` block with character count outside).

    ### 📱 4. Meta (Facebook & Instagram) Paid Ads ({lang})
    Create 2 high-converting ad variations designed to stop the scroll:
    - **Variation A (PAS Framework - Problem, Agitation, Solution):** Focus on the customer's frustration and present the product as the relief.
    - **Variation B (Desire & Lifestyle Angle):** A compelling, creative, and relatable hook tailored to the selected tone.
    
    For both variations, provide each element in its own ```text``` block:
    - **Primary Text (Main copy ABOVE the image):** Strong opening hook with 1-2 thematic emojis, conversational body copy with bullet points, and clear CTA.
    - **Headline (BOLD text BELOW the image, max 40 chars):** Punchy offer/benefit + 1 bold thematic emoji.
    - **Description (Small text below headline, max 30 chars):** Trust badge or quick perk (e.g. ⭐ Free Shipping).

    ### 📸 5. Organic Instagram Post & Visual Hook ({lang})
    Craft an authentic post that feels like organic lifestyle content, not an ad:
    - **Post Caption:** Sensory opening hook, ritual or experience-based narrative showing the product organically in daily life, soft conversational CTA, and discussion question. (One ```text``` block).
    - **Hashtags:** 8-10 targeted lifestyle and niche hashtags. (One ```text``` block).
    - **🎬 Visual Direction (Photo/Reel Concept):** 1-2 actionable sentences describing the lighting, composition, or Reel scene to capture this aesthetic.
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.75},
    }

    last_error = ""
    for model_id in candidate_models:
        clean_model = model_id.replace("models/", "")
        endpoints = [
            f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent",
            f"https://generativelanguage.googleapis.com/v1/models/{clean_model}:generateContent",
            f"https://aiplatform.googleapis.com/v1/publishers/google/models/{clean_model}:generateContent",
        ]

        for gen_url in endpoints:
            try:
                response = requests.post(
                    gen_url,
                    headers=headers,
                    params={"key": key},
                    json=payload,
                    timeout=60,
                )
                if response.status_code == 200:
                    data = response.json()
                    try:
                        return data["candidates"][0]["content"]["parts"][0][
                            "text"
                        ]
                    except Exception:
                        last_error = f"Unexpected response from Google: {data}"
                else:
                    last_error = f"Error ({response.status_code}) on {clean_model}: {response.text}"
            except Exception as e:
                last_error = f"Connection error: {e}"

    return last_error


# --- EXECUTION LOGIC WITH LIVE STATUS ---
if generate_clicked:
    if not license_ok:
        status_placeholder.error(
            "🔒 Please activate your license key in the top box before"
            " generating."
        )
    elif not api_key.strip():
        status_placeholder.error("🔑 Google AI API key is missing.")
    elif not has_valid_input:
        status_placeholder.warning(
            "⚠️ Please fill in product details before generating."
        )
    else:
        with status_placeholder.container():
            st.info(
                "⏳ **Generating your global campaign...** (Takes ~15–20"
                " seconds)\n\n• Analyzing product psychology\n• Discovering"
                " high-intent commercial keywords\n• Writing native ad copy in"
                " a natural, conversational human tone"
            )

        if is_mode_url:
            source_text = scrape_website(url_input)
            is_url = True
            hint_to_use = product_hint_url
        else:
            source_text = (
                f"Title: {manual_title}\nDescription & Details: {manual_desc}"
            )
            is_url = False
            hint_to_use = ""

        if is_url and source_text.startswith("Error"):
            status_placeholder.error(source_text)
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
            status_placeholder.empty()

            if ads_result.startswith("Error") or ads_result.startswith(
                "Connection error"
            ):
                st.error(ads_result)
            else:
                st.success(
                    f"✅ Campaign & Keyword Strategy ({target_language}) is"
                    " ready! Hover over any box and click 📋 in the top right"
                    " corner to copy:"
                )
                st.markdown(ads_result)

# --- GLOBAL FOOTER ---
st.markdown(
    f"""
<div class="custom-footer">
    © 2026 <strong>{APP_NAME}</strong> | Professional AI Advertising Suite for E-Commerce & Creators
</div>
""",
    unsafe_allow_html=True,
)
