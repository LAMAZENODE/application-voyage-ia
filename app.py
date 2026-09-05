import streamlit as st
import pandas as pd
import stripe
from google import genai
import os  # <-- Garder cet import

# 1. Configuration de la page
st.set_page_config(page_title="IA Voyage & Budget Copilot", page_icon="🌍", layout="centered")

st.title("🌍 Mon Copilot de Voyage IA")
st.subheader("Générez votre itinéraire, visualisez la carte et estimez votre budget")

# ==========================================
# 🔑 RÉCUPÉRATION DE VOS SECRETS STREAMLIT
# ==========================================
try:
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
    ID_PRIX_STRIPE = st.secrets["STRIPE_PRICE_ID"]
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    MODELE_GEMINI = "gemini-1.5-pro"
except Exception as e:
    st.warning(f"⚠️ Clés manquantes dans vos Streamlit Secrets : {e}")
    ID_PRIX_STRIPE = "VOTRE_PRICE_ID_ICI"

# ==========================================
# 🌐 URL DE REDIRECTION POUR STRIPE - CORRIGÉE
# ==========================================
# 👇 PRODUCTION (Streamlit Cloud) - DÉCOMMENTEZ POUR DÉPLOYER
BASE_URL = "https://application1-voyage-ia-y4uuyrrbw4nzirmc4skpyv.streamlit.app"

# 👇 LOCAL (développement) - DÉCOMMENTEZ POUR TESTER EN LOCAL
# BASE_URL = "http://localhost:8501"

# ==========================================
# 💳 GESTION DE L'ÉTAT DU PAIEMENT
# ==========================================
if "est_paye" not in st.session_state:
    st.session_state.est_paye = False

# Si Stripe renvoie l'utilisateur avec ?success=true dans l'URL
if st.query_params.get("success") == "true":
    st.session_state.est_paye = True
    st.query_params.clear()

# ... LE RESTE DE VOTRE CODE (inchangé) ...

# ==========================================
# 🧠 FONCTION COMMUNE POUR L'IA (GEMINI)
# ==========================================
def demander_ia(prompt):
    try:
        response = client.models.generate_content(
            model=MODELE_GEMINI,
            contents=prompt + "\n\nRéponds avec des informations réelles, courtes et structurées sous forme de tableau ou liste Markdown."
        )
        return response.text
    except Exception as e:
        return f"⚠️ Erreur de connexion à l'IA Gemini : {e}."

# ==========================================
# 🗺️ ENTRÉES DE L'UTILISATEUR (DYNAMIQUES)
# ==========================================
st.markdown("### 🗺️ Les détails du voyage")
destination = st.text_input("📍 Où souhaitez-vous aller ?", value="Tunisie")
jours = st.slider("📅 Durée du séjour (jours)", min_value=1, max_value=14, value=7)
style = st.selectbox("🎒 Style de voyage", ["Culturel & Historique", "Luxe & Détente", "Économique", "Aventure"])

st.markdown("### 💰 Vos estimations budgétaires par jour")
budget_hotel = st.number_input("🏨 Hébergement / nuit (EUR)", value=68)
budget_nourriture = st.number_input("🍔 Nourriture / jour (EUR)", value=29)
budget_activites = st.number_input("🎟️ Activités / jour (EUR)", value=20)
transport_ar = st.number_input("✈️ Prix total des billets de transport Aller-Retour (EUR)", value=158)

# Calculs automatiques du Budget
logement_total = budget_hotel * jours
vie_sur_place = (budget_nourriture + budget_activites) * jours
budget_total = logement_total + vie_sur_place + transport_ar

# Récapitulatif
st.markdown(f"### 📊 Récapitulatif du Budget pour {jours} jours à {destination}")
col_b1, col_b2, col_b3 = st.columns(3)
col_b1.metric("Logement Total", f"{logement_total} EUR")
col_b2.metric("Vie sur place", f"{vie_sur_place} EUR")
col_b3.metric("BUDGET TOTAL ESTIMÉ", f"{budget_total} EUR")

st.markdown("---")
st.markdown(f"### ✨ Votre itinéraire personnalisé pour : **{destination}**")

# --- PARTIE PUBLIQUE : Toujours visible (Jours 1 & 2) ---
st.markdown(f"""
**Jour 1 : Immersion à {destination}**
*   **Matin :** Accueil et installation à votre hébergement (Adapté à votre budget de {budget_hotel} EUR/nuit). Découverte du centre historique à pied.
*   **Après-midi :** Visite des monuments incontournables et balade dans les parcs locaux de {destination}.
*   **Soir :** Dîner traditionnel dans un restaurant local pour tester la gastronomie typique.

**Jour 2 : Exploration Culturelle**
*   **Matin :** Visite des grands musées nationaux ou des sites archéologiques de la région.
*   **Après-midi :** Quartier libre pour faire du shopping dans les marchés traditionnels ou artisanaux.
*   **Conseil secret :** Utilisez les transports collectifs locaux, très avantageux pour votre budget de {budget_nourriture + budget_activites} EUR/jour.
""")

# ==========================================
# 🔒 CAS N°1 : LE CLIENT N'A PAS ENCORE PAYÉ
# ==========================================
if not st.session_state.est_paye:
    st.error("🔒 **CONTENU PREMIUM DISPONIBLE**")
    st.markdown(f"""
    ### 🚀 Débloquez votre Guide Premium pour {destination}
    Accédez instantanément à vos outils d'optimisation et à votre itinéraire complet pour seulement **4,99 EUR** :
    *   🗺️ **L'itinéraire complet** du Jour 3 au Jour {jours} sur mesure.
    *   🏨 Activation du bouton **Chercher un hôtel moins cher** (Hôtels réels sous les {budget_hotel} EUR).
    *   🍔 Activation du bouton **Restaurant pas cher** (Adresses locales et de terroir).
    *   🚗 Activation du guide de **Location de voiture** (Agences locales éco et astuces transports).
    """)
    
    # Le bouton de paiement Stripe réel
    if st.button("💳 Débloquer mon itinéraire & mes outils de réduction (4,99 EUR)"):
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': ID_PRIX_STRIPE,
                    'quantity': 1
                }],
                mode='payment',
                success_url=f"{BASE_URL}?success=true",
                cancel_url=f"{BASE_URL}?cancel=true",
            )
            # Redirection automatique vers votre Stripe Checkout réel
            st.markdown(f'<meta http-equiv="refresh" content="0; url={checkout_session.url}">', unsafe_allow_html=True)
            st.link_button("➡️ Aller vers la page de paiement sécurisée", checkout_session.url)
        except Exception as e:
            st.error(f"Erreur d'initialisation Stripe : {e}")

    # 👀 PREUVE VISUELLE POUR LE CLIENT : Les boutons apparaissent mais sont bloqués
    st.markdown("---")
    st.markdown("### ⚙️ Vos outils d'optimisation budgétaire (Verrouillés)")
    st.caption("💡 *Ces 3 boutons s'activeront et interrogeront l'IA en direct dès la validation de votre paiement.*")
    
    col_lock1, col_lock2, col_lock3 = st.columns(3)
    with col_lock1:
        st.button("🔒 🏨 Chercher hôtel pas cher", disabled=True, key="btn_h_lock")
    with col_lock2:
        st.button("🔒 🍔 Restaurant pas cher", disabled=True, key="btn_r_lock")
    with col_lock3:
        st.button("🔒 🚗 Location de voiture", disabled=True, key="btn_c_lock")

# ==========================================
# 🔓 CAS N°2 : LE CLIENT A PAYÉ (TOUT SE DÉBLOQUE)
# ==========================================
else:
    st.success("✅ **Félicitations ! Votre paiement a été validé. Vos outils premium et l'IA sont actifs.**")
    
    # La suite de l'itinéraire générée par Gemini
    with st.spinner("L'IA rédige la suite de votre parcours d'expert..."):
        prompt_suite = f"Rédige de manière condensée la suite de l'itinéraire du Jour 3 au Jour {jours} pour un voyage {style} à {destination}."
        st.markdown(demander_ia(prompt_suite))
            
    st.markdown("---")
    st.markdown("### ⚙️ Vos outils d'optimisation budgétaire débloqués (Recherche IA en direct)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏨 Chercher hôtel pas cher", key="btn_h_open"):
            with st.spinner(f"Recherche de logements économiques à {destination}..."):
                prompt_hotel = f"Donne 3 vrais noms d'hôtels ou maisons d'hôtes réels et bien notés à {destination} à moins de {budget_hotel}€ par nuit. Présente sous forme de tableau Markdown (Nom, Prix, Quartier)."
                st.markdown(demander_ia(prompt_hotel))
                
    with col2:
        if st.button("🍔 Restaurant pas cher", key="btn_r_open"):
            with st.spinner(f"Trouvailles culinaires à {destination}..."):
                prompt_resto = f"Donne 3 vrais noms de restaurants locaux ou street food pas chers pour manger local à {destination} pour moins de {budget_nourriture}€ par repas. Ajoute une spécialité à tester."
                st.markdown(demander_ia(prompt_resto))
                
    with col3:
        if st.button("🚗 Location de voiture", key="btn_c_open"):
            with st.spinner(f"Analyse des transports à {destination}..."):
                prompt_voiture = f"Donne les meilleures options de location de voiture réelles ou alternatives de transports économiques à {destination}. Sois concis."
                st.markdown(demander_ia(prompt_voiture))
