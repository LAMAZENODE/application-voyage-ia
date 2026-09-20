import streamlit as st
import pandas as pd
import stripe
from google import genai
import json
import os

# ==========================================
# 🌍 SYSTÈME MULTILINGUE
# ==========================================
@st.cache_data
def charger_traductions():
    chemin_script = os.path.dirname(os.path.abspath(__file__))
    chemin_fichier = os.path.join(chemin_script, "translations_travel.json")
    with open(chemin_fichier, "r", encoding="utf-8") as f:
        return json.load(f)

TRADUCTIONS = charger_traductions()


LANGUES = {
    "🇫🇷 Français": "fr",
    "🇬🇧 English": "en",
    "🇩🇪 Deutsch": "de",
    "🇪🇸 Español": "es",
    "🇮🇹 Italiano": "it",
    "🇸🇦 العربية": "ar"
}

if "langue" not in st.session_state:
    st.session_state.langue = "fr"

# CSS pour l'arabe (droite à gauche)
def injecter_css_arabe():
    if st.session_state.langue == "ar":
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
        html, body, [class*="css"], .stApp {
            direction: rtl;
            text-align: right;
            font-family: 'Cairo', sans-serif;
        }
        .stTextArea textarea, .stTextInput input,
        .stNumberInput input, .stSelectbox select {
            direction: rtl;
            text-align: right;
        }
        .stMarkdown, .stMarkdown p, .stMarkdown li,
        h1, h2, h3, h4, h5, h6 {
            direction: rtl;
            text-align: right;
        }
        [data-testid="stSidebar"] {
            direction: rtl;
            text-align: right;
        }
        .stButton > button, .stDownloadButton > button {
            direction: rtl;
        }
        .katex, .MathJax, .katex-display {
            direction: ltr !important;
        }
        </style>
        """, unsafe_allow_html=True)
def injecter_css_arabe():
    if st.session_state.langue == "ar":
        st.markdown("""
        ...
        """, unsafe_allow_html=True)


# ==========================================
# 🌊 ARRIÈRE-PLAN ANIMÉ (VOYAGE VIVANT)
# ==========================================
def injecter_fond_anime():          # ← LA FONCTION VIENT ICI
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg,
            #ffedd5 0%, #e0f2fe 25%, #bae6fd 50%,
            #7dd3fc 75%, #38bdf8 100%) !important;
        background-size: 400% 400% !important;
        animation: fondVoyage 20s ease infinite !important;
    }

    @keyframes fondVoyage {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    section.main, .main {
        background: transparent !important;
    }

    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        background-image:
            radial-gradient(2px 2px at 15% 25%, rgba(14, 165, 233, 0.55), transparent),
            radial-gradient(2px 2px at 45% 65%, rgba(56, 189, 248, 0.45), transparent),
            radial-gradient(1.5px 1.5px at 75% 15%, rgba(125, 211, 252, 0.65), transparent),
            radial-gradient(2px 2px at 30% 85%, rgba(14, 165, 233, 0.4), transparent),
            radial-gradient(1.5px 1.5px at 88% 55%, rgba(56, 189, 248, 0.5), transparent),
            radial-gradient(2px 2px at 60% 40%, rgba(125, 211, 252, 0.45), transparent),
            radial-gradient(1px 1px at 10% 70%, rgba(14, 165, 233, 0.5), transparent),
            radial-gradient(2px 2px at 95% 90%, rgba(56, 189, 248, 0.35), transparent);
        animation: particulesMontent 22s linear infinite;
    }

    @keyframes particulesMontent {
        0%   { transform: translateY(0); opacity: 0.7; }
        50%  { transform: translateY(-50vh); opacity: 0.4; }
        100% { transform: translateY(-100vh); opacity: 0; }
    }

    [data-testid="stAppViewContainer"]::after {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        background:
            linear-gradient(90deg, transparent 0%, rgba(14,165,233,0.35) 50%, transparent 100%) no-repeat,
            linear-gradient(90deg, transparent 0%, rgba(56,189,248,0.25) 50%, transparent 100%) no-repeat;
        background-size: 250px 1.5px, 180px 1px;
        background-position: -300px 20%, -300px 65%;
        animation: lignesVol 15s linear infinite;
    }

    @keyframes lignesVol {
        0%   { background-position: -300px 20%, -300px 65%; opacity: 0; }
        10%  { opacity: 1; }
        90%  { opacity: 1; }
        100% { background-position: 120vw 20%, 120vw 65%; opacity: 0; }
    }

    .block-container {
        background: rgba(255, 255, 255, 0.82) !important;
        backdrop-filter: blur(16px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(160%) !important;
        border-radius: 24px !important;
        box-shadow: 0 20px 50px rgba(3, 105, 161, 0.10) !important;
        border: 1px solid rgba(255, 255, 255, 0.55) !important;
    }

    @media (prefers-reduced-motion: reduce) {
        .stApp,
        [data-testid="stAppViewContainer"]::before,
        [data-testid="stAppViewContainer"]::after {
            animation: none !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
def t(cle, **kwargs):
    texte = TRADUCTIONS[st.session_state.langue].get(cle, cle)
    if kwargs:
        try:
            return texte.format(**kwargs)
        except (KeyError, IndexError):
            return texte
    return texte

# ==========================================
# 1. Configuration de la page
# ==========================================
st.set_page_config(page_title="AI Travel Copilot", page_icon="🌍", layout="centered")

# Sélecteur de langue dans la sidebar
with st.sidebar:
    st.markdown("### 🌍 Language")
    choix = st.selectbox(
        "Choisissez votre langue :",
        options=list(LANGUES.keys()),
        index=list(LANGUES.values()).index(st.session_state.langue),
        label_visibility="collapsed"
    )
    st.session_state.langue = LANGUES[choix]

# Injecter le CSS arabe si nécessaire
injecter_css_arabe()
injecter_fond_anime()   # ← AJOUTEZ CETTE LIGNE

st.title(t("hero_title"))
st.subheader(t("hero_subtitle"))

# ==========================================
# 🔑 RÉCUPÉRATION DE VOS SECRETS STREAMLIT
# ==========================================
try:
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
    ID_PRIX_STRIPE = st.secrets["STRIPE_PRICE_ID"]
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    MODELE_GEMINI = "gemini-2.5-flash"
except Exception as e:
    st.error(t("config_error", error=str(e)))
    st.stop()

# ==========================================
# 💳 GESTION DE L'ÉTAT DU PAIEMENT
# ==========================================
if "est_paye" not in st.session_state:
    st.session_state.est_paye = False

query_params = st.query_params
if query_params.get("success") == "true":
    st.session_state.est_paye = True
    st.query_params.clear()

# ==========================================
# 🧠 FONCTION POUR L'IA (multilingue)
# ==========================================
def demander_ia(prompt):
    try:
        noms_langues = {
            "fr": "français",
            "en": "anglais",
            "de": "allemand",
            "es": "espagnol",
            "it": "italien",
            "ar": "arabe standard moderne"
        }
        nom_langue = noms_langues.get(st.session_state.langue, "français")
        prompt_multilingue = (
            f"Réponds IMPÉRATIVEMENT en {nom_langue}. "
            f"{prompt} "
            f"Réponds avec des informations réelles, courtes et structurées sous forme de tableau ou liste Markdown."
        )
        response = client.models.generate_content(
            model=MODELE_GEMINI,
            contents=prompt_multilingue
        )
        return response.text
    except Exception as e:
        return t("ai_error", error=str(e))

# ==========================================
# 🗺️ FORMULAIRE UTILISATEUR
# ==========================================
st.markdown(f"### {t('trip_details')}")
destination = st.text_input(t("where_label"), value=t("default_country"))
jours = st.slider(t("duration_label"), min_value=1, max_value=14, value=7)

styles = [t("style_culturel"), t("style_luxe"), t("style_eco"), t("style_aventure")]
style = st.selectbox(t("style_label"), styles)

st.markdown(f"### {t('budget_title')}")
budget_hotel = st.number_input(t("hotel_label"), value=68)
budget_nourriture = st.number_input(t("food_label"), value=29)
budget_activites = st.number_input(t("activities_label"), value=20)
transport_ar = st.number_input(t("transport_label"), value=158)

# Calculs
logement_total = budget_hotel * jours
vie_sur_place = (budget_nourriture + budget_activites) * jours
budget_total = logement_total + vie_sur_place + transport_ar

# Récapitulatif
st.markdown(f"### {t('summary_title', days=jours, country=destination)}")
col_b1, col_b2, col_b3 = st.columns(3)
col_b1.metric(t("accommodation_total"), f"{logement_total} EUR")
col_b2.metric(t("living_total"), f"{vie_sur_place} EUR")
col_b3.metric(t("total_budget"), f"{budget_total} EUR")

st.markdown("---")
st.markdown(f"### {t('itinerary_title', country=destination)}")

# Itinéraire gratuit (Jours 1 & 2)
st.markdown(f"""
**{t('day1_title', country=destination)}**
*   **{t('day1_morning', budget=budget_hotel)}**
*   **{t('day1_afternoon', country=destination)}**
*   **{t('day1_evening')}**

**{t('day2_title')}**
*   **{t('day2_morning')}**
*   **{t('day2_afternoon')}**
*   **{t('day2_tip', budget=budget_nourriture + budget_activites)}**
""")

# ==========================================
# 🔒 PARTIE PAYANTE
# ==========================================
if not st.session_state.est_paye:
    st.error(t("premium_lock"))
    st.markdown(f"""
    ### {t('premium_title', country=destination)}
    {t('premium_desc')}
    *   {t('premium_bullet1', days=jours)}
    *   {t('premium_bullet2')}
    *   {t('premium_bullet3')}
    *   {t('premium_bullet4')}
    *   {t('premium_bullet5')}
    """)

    APP_URL = st.secrets.get("MON_URL_STREAMLIT", "https://votre-app.streamlit.app")

    if st.button(t("pay_button"), key="pay_button", type="primary"):
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': ID_PRIX_STRIPE,
                    'quantity': 1
                }],
                mode='payment',
                success_url=f"{APP_URL}?success=true",
                cancel_url=f"{APP_URL}?cancel=true",
                                locale={
                    "fr": "fr",
                    "en": "en",
                    "de": "de",
                    "es": "es",
                    "it": "it",
                    "ar": "fr",   # ← arabe → page Stripe en français
                }.get(st.session_state.langue, "auto"),
            )

            st.markdown(f"""
            <div style="text-align: center; padding: 30px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 15px; color: white;">
                <h2>{t('pay_title')}</h2>
                <p style="font-size: 18px; margin: 20px 0;">
                    {t('pay_redirect')}
                </p>
                <a href="{checkout_session.url}"
                   style="display: inline-block; padding: 15px 40px;
                          background-color: white; color: #667eea;
                          text-decoration: none; border-radius: 50px;
                          font-weight: bold; font-size: 18px;
                          margin: 10px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    {t('pay_now')}
                </a>
                <br>
                <small style="opacity: 0.8;">{t('pay_secure')}</small>
                <script>
                    setTimeout(function() {{
                        window.location.href = '{checkout_session.url}';
                    }}, 1500);
                </script>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(t("stripe_error", error=str(e)))
            st.info(t("retry_support"))

    # Boutons verrouillés
    st.markdown("---")
    st.markdown(f"### {t('tools_locked')}")
    st.caption(t("unlock_hint"))

    col_lock1, col_lock2, col_lock3, col_lock4 = st.columns(4)
    with col_lock1:
        st.button(t("btn_hotel_lock"), disabled=True, key="btn_h_lock")
    with col_lock2:
        st.button(t("btn_resto_lock"), disabled=True, key="btn_r_lock")
    with col_lock3:
        st.button(t("btn_car_lock"), disabled=True, key="btn_c_lock")
    with col_lock4:
        st.button(t("btn_camping_lock"), disabled=True, key="btn_camping_lock")

# ==========================================
# 🔓 CONTENU DÉBLOQUÉ
# ==========================================
else:
    st.success(t("payment_success"))

    # Itinéraire complet généré par l'IA
    with st.spinner(t("spinner_itinerary")):
        prompt_suite = f"Rédige de manière condensée la suite de l'itinéraire du Jour 3 au Jour {jours} pour un voyage {style} à {destination}."
        st.markdown(demander_ia(prompt_suite))

    st.markdown("---")
    st.markdown(f"### {t('tools_unlocked')}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(t("btn_hotel"), key="btn_h_open"):
            with st.spinner(t("spinner_search")):
                prompt_hotel = f"Donne 3 vrais noms d'hôtels ou maisons d'hôtes réels et bien notés à {destination} à moins de {budget_hotel}€ par nuit. Présente sous forme de tableau Markdown."
                st.markdown(demander_ia(prompt_hotel))

    with col2:
        if st.button(t("btn_resto"), key="btn_r_open"):
            with st.spinner(t("spinner_search")):
                prompt_resto = f"Donne 3 vrais noms de restaurants locaux ou street food pas chers pour manger local à {destination} pour moins de {budget_nourriture}€ par repas. Présente sous forme de tableau Markdown."
                st.markdown(demander_ia(prompt_resto))

    with col3:
        if st.button(t("btn_car"), key="btn_c_open"):
            with st.spinner(t("spinner_search")):
                prompt_voiture = f"Donne les meilleures options de location de voiture réelles ou alternatives de transports économiques à {destination}. Présente sous forme de tableau Markdown."
                st.markdown(demander_ia(prompt_voiture))

    with col4:
        if st.button(t("btn_camping"), key="btn_camping_open"):
            with st.spinner(t("spinner_search")):
                prompt_camping = f"Donne 3 vrais noms d'aires de camping-car ou campings avec emplacements bien notés à {destination}. Inclus prix approximatif par nuit, services disponibles (électricité, eau, vidange) et avis sur l'emplacement. Présente sous forme de tableau Markdown."
                st.markdown(demander_ia(prompt_camping))
