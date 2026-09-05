import streamlit as st
import pandas as pd
import stripe
from google import genai

# 1. Configuration de la page
st.set_page_config(page_title="IA Voyage & Budget Copilot", page_icon="🌍", layout="centered")

st.title("🌍 Mon Copilot de Voyage IA")
st.subheader("Générez votre itinéraire, visualisez la carte et estimez votre budget")

# ==========================================
# 🔑 RÉCUPÉRATION DE VOS SECRETS STREAMLIT
# ==========================================
try:
    # Clés Stripe en production
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
    ID_PRIX_STRIPE = st.secrets["STRIPE_PRICE_ID"]
    
    # Clé Gemini
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    MODELE_GEMINI = "gemini-1.5-pro"
    
except Exception as e:
    st.error(f"⚠️ Erreur de configuration: {e}")
    st.stop()

# ==========================================
# 💳 GESTION DE L'ÉTAT DU PAIEMENT
# ==========================================
if "est_paye" not in st.session_state:
    st.session_state.est_paye = False

# Vérification du paiement réussi
query_params = st.query_params
if query_params.get("success") == "true":
    st.session_state.est_paye = True
    st.query_params.clear()

# ==========================================
# 🧠 FONCTION POUR L'IA
# ==========================================
def demander_ia(prompt):
    try:
        response = client.models.generate_content(
            model=MODELE_GEMINI,
            contents=prompt + "\n\nRéponds avec des informations réelles, courtes et structurées sous forme de tableau ou liste Markdown."
        )
        return response.text
    except Exception as e:
        return f"⚠️ Erreur de connexion à l'IA : {e}."

# ==========================================
# 🗺️ FORMULAIRE UTILISATEUR
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

# Calculs
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

# Itinéraire gratuit (Jours 1 & 2)
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
# 🔒 PARTIE PAYANTE
# ==========================================
if not st.session_state.est_paye:
    st.error("🔒 **CONTENU PREMIUM DISPONIBLE**")
    st.markdown(f"""
    ### 🚀 Débloquez votre Guide Premium pour {destination}
    Accédez instantanément à vos outils d'optimisation et à votre itinéraire complet pour seulement **4,99 EUR** :
    *   🗺️ **L'itinéraire complet** du Jour 3 au Jour {jours} sur mesure.
    *   🏨 Activation du bouton **Chercher un hôtel moins cher**.
    *   🍔 Activation du bouton **Restaurant pas cher**.
    *   🚗 Activation du guide de **Location de voiture**.
    """)
    
    # URL de votre application en production
    # À MODIFIER AVEC VOTRE URL STREAMLIT CLOUD
    APP_URL = "https://votre-app.streamlit.app"  # <-- REMPLACEZ PAR VOTRE URL
    
    if st.button("💳 Débloquer mon itinéraire (4,99 EUR)", key="pay_button"):
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
            )
            
            # Redirection vers Stripe
            st.markdown(f"""
            <div style="text-align: center; padding: 30px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 15px; color: white;">
                <h2>💳 Paiement sécurisé</h2>
                <p style="font-size: 18px; margin: 20px 0;">
                    Vous allez être redirigé vers Stripe pour finaliser votre paiement de 4,99 €
                </p>
                <a href="{checkout_session.url}" 
                   style="display: inline-block; padding: 15px 40px; 
                          background-color: white; color: #667eea; 
                          text-decoration: none; border-radius: 50px;
                          font-weight: bold; font-size: 18px;
                          margin: 10px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    ✅ Payer maintenant
                </a>
                <br>
                <small style="opacity: 0.8;">🔒 Paiement sécurisé par Stripe - Cryptage SSL</small>
                <script>
                    // Redirection automatique après 1.5 secondes
                    setTimeout(function() {{
                        window.location.href = '{checkout_session.url}';
                    }}, 1500);
                </script>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Erreur lors de l'initialisation du paiement : {e}")
            st.info("Veuillez réessayer ou contacter le support.")

    # Boutons verrouillés
    st.markdown("---")
    st.markdown("### ⚙️ Outils d'optimisation (Verrouillés)")
    st.caption("💡 Débloquez après paiement")
    
    col_lock1, col_lock2, col_lock3 = st.columns(3)
    with col_lock1:
        st.button("🔒 Hôtel pas cher", disabled=True, key="btn_h_lock")
    with col_lock2:
        st.button("🔒 Restaurant pas cher", disabled=True, key="btn_r_lock")
    with col_lock3:
        st.button("🔒 Location de voiture", disabled=True, key="btn_c_lock")

# ==========================================
# 🔓 CONTENU DÉBLOQUÉ
# ==========================================
else:
    st.success("✅ **Paiement validé ! Contenu premium débloqué.**")
    
    # Itinéraire complet généré par l'IA
    with st.spinner("Génération de votre itinéraire personnalisé..."):
        prompt_suite = f"Rédige de manière condensée la suite de l'itinéraire du Jour 3 au Jour {jours} pour un voyage {style} à {destination}."
        st.markdown(demander_ia(prompt_suite))
            
    st.markdown("---")
    st.markdown("### ⚙️ Outils d'optimisation débloqués")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏨 Hôtel pas cher", key="btn_h_open"):
            with st.spinner(f"Recherche de logements à {destination}..."):
                prompt_hotel = f"Donne 3 vrais noms d'hôtels ou maisons d'hôtes réels et bien notés à {destination} à moins de {budget_hotel}€ par nuit. Présente sous forme de tableau Markdown."
                st.markdown(demander_ia(prompt_hotel))
                
    with col2:
        if st.button("🍔 Restaurant pas cher", key="btn_r_open"):
            with st.spinner(f"Recherche de restaurants à {destination}..."):
                prompt_resto = f"Donne 3 vrais noms de restaurants locaux ou street food pas chers pour manger local à {destination} pour moins de {budget_nourriture}€ par repas."
                st.markdown(demander_ia(prompt_resto))
                
    with col3:
        if st.button("🚗 Location de voiture", key="btn_c_open"):
            with st.spinner(f"Recherche de transports à {destination}..."):
                prompt_voiture = f"Donne les meilleures options de location de voiture réelles ou alternatives de transports économiques à {destination}."
                st.markdown(demander_ia(prompt_voiture))

