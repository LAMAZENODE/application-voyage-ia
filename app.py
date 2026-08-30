import streamlit as st
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim
from fpdf import FPDF
import io
import openai

# Configuration de la page visuelle
st.set_page_config(page_title="IA Voyage & Budget Copilot", page_icon="🌍", layout="centered")

st.title("🌍 Mon Copilot de Voyage IA")
st.subheader("Générez votre itinéraire, visualisez la carte et estimez votre budget")

# --- ENTRÉES DE L'UTILISATEUR ---
st.markdown("### 🗺️ Les détails du voyage")
destination_input = st.text_input("📍 Où souhaitez-vous aller ?", placeholder="Ex: Tokyo, Rome, Paris...")
duree_input = st.slider("📅 Durée du séjour (jours)", min_value=1, max_value=14, value=7)
style_input = st.selectbox("🎒 Style de voyage", ["Culturel & Historique", "Gastronomie & Local", "Petit budget / Sac à dos", "Luxe & Détente"])

st.markdown("### 💰 Vos estimations budgétaires par jour")
col1, col2, col3 = st.columns(3)
with col1:
    hotel_par_jour = st.number_input("🏨 Hébergement / nuit (EUR)", min_value=0, value=68)
with col2:
    repas_par_jour = st.number_input("🍔 Nourriture / jour (EUR)", min_value=0, value=29)
with col3:
    loisirs_par_jour = st.number_input("🎟️ Activités / jour (EUR)", min_value=0, value=20)
    
billet_avion = st.number_input("✈️ Prix total des billets de transport Aller-Retour (EUR)", min_value=0, value=158)

# Bouton de validation standard
bouton_valider = st.button("Calculer le budget et créer l'itinéraire ✨", type="primary")

# --- LOGIQUE AU CLIC ---
if bouton_valider:
    if not destination_input:
        st.warning("Veuillez entrer une destination !")
    else:
        st.session_state["calcul_ok"] = True
        st.session_state["dest"] = destination_input
        st.session_state["dur"] = duree_input
        st.session_state["sty"] = style_input
        
        # Calculs mathématiques Python
        st.session_state["logement_total"] = hotel_par_jour * (duree_input - 1)
        st.session_state["vie_total"] = (repas_par_jour + loisirs_par_jour) * duree_input
        st.session_state["budget_global"] = st.session_state["logement_total"] + st.session_state["vie_total"] + billet_avion

        # --- APPEL À L'INTELLIGENCE ARTIFICIELLE ---
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
            client = openai.OpenAI(api_key=api_key)
            
            prompt_ia = f"""
            Agis en tant qu'expert en voyage et conseiller budgétaire. Crée un itinéraire détaillé de {duree_input} jours pour visiter {destination_input} (Style : {style_input}).
            L'utilisateur a un budget de {st.session_state['budget_global']} EUR ({hotel_par_jour} EUR/nuit d'hôtel et {repas_par_jour + loisirs_par_jour} EUR/jour sur place).
            Rédige le programme jour par jour de manière claire pour toute la duree demandee. Utilisez uniquement des tirets standards '-' pour les listes. Utilisez le mot 'EUR' au lieu du symbole de l'euro. N'utilisez aucun caractère spécial ni emoji.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt_ia}]
            )
            st.session_state["texte_ia"] = response.choices.message.content
            
        except Exception:
            # TEXTE DE DÉMONSTRATION COMPLET DE 7 JOURS SI PAS DE CLÉ API
            st.session_state["texte_ia"] = f"""Jour 1 : Immersion a {destination_input.capitalize()}
- Matin : Accueil et installation a votre hebergement (Adapte a votre budget de {hotel_par_jour} EUR/nuit). Decouverte du centre historique a pied.
- Apres-midi : Visite des monuments incontournables et balade dans les parcs locaux.
- Soir : Diner traditionnel dans un restaurant local pour tester la gastronomie typique.

Jour 2 : Exploration Culturelle
- Matin : Visite des grands musees nationaux ou des sites archeologiques de la region.
- Apres-midi : Quartier libre pour faire du shopping dans les marches traditionnels ou artisanaux.
- Conseil secret : Utilisez les transports collectifs (metro/tramway), tres avantageux pour votre budget de {repas_par_jour + loisirs_par_jour} EUR/jour.

Jour 3 : Quartiers Historiques et Architecture
- Matin : Promenade architecturale guidee à travers les plus vieux quartiers de la ville.
- Apres-midi : Visite d'un monument emblematique moins connu des touristes pour eviter la foule.

Jour 4 : Journee Excursion et Nature
- Matin : Depart pour une excursion en dehors de la ville vers un lac, une plage ou une montagne proche.

Jour 5 : Gastronomie Fine et Rencontres
- Matin : Cours de cuisine locale ou degustation de produits du terroir chez un artisan.

Jour 6 : Detente et Panoramas
- Matin : Grasse matinee et brunch dans un quartier branche.

Jour 7 : Souvenirs et Depart
- Matin : Derniers achats de souvenirs locaux et preparation des bagages.
- Apres-midi : Transfert vers la gare ou l'aeroport grace a vos frais de transport."""

        # --- ARCHITECTURE DU PDF SÉCURISÉ ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(30, 58, 138)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 18)
        pdf.ln(10)
        pdf.cell(0, 10, "VOTRE RAPPORT DE VOYAGE SUR-MESURE", ln=True, align="C")
        pdf.ln(15)
        pdf.set_text_color(40, 40, 40)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, f"Fiche de route : {destination_input.capitalize()}", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, f"Duree du sejour : {duree_input} jours", ln=True)
        pdf.cell(0, 7, f"Style selectionne : {style_input}", ln=True)
        pdf.cell(0, 7, f"Budget Total Estime : {st.session_state['budget_global']} EUR", ln=True)
        pdf.ln(10)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Votre Itineraire Jour par Jour", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        pdf.set_font("Helvetica", "", 11)
        texte_utf8 = st.session_state["texte_ia"].encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, texte_utf8)
        
        st.session_state["pdf_cree"] = bytes(pdf.output())

# --- BLOC D'AFFICHAGE PERSISTANT ---
if "calcul_ok" in st.session_state and st.session_state["calcul_ok"]:
    st.markdown("---")
    st.markdown(f"### 📊 Récapitulatif du Budget pour {st.session_state['dur']} jours à {st.session_state['dest'].capitalize()}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Logement Total", f"{st.session_state['logement_total']} EUR")
    c2.metric("Vie sur place", f"{st.session_state['vie_total']} EUR")
    c3.metric("BUDGET TOTAL ESTIMÉ", f"{st.session_state['budget_global']} EUR", delta_color="inverse")
    st.markdown("---")
    
    st.markdown("### 🗺️ Localisation de votre destination")
    try:
        geolocator = Nominatim(user_agent="mon_super_copilot_voyage_ia_2026", timeout=5)
        location = geolocator.geocode(st.session_state["dest"])
        if location:
            m = folium.Map(location=[location.latitude, location.longitude], zoom_start=5)
            folium.Marker([location.latitude, location.longitude], popup=st.session_state["dest"].capitalize()).add_to(m)
            st_folium(m, width=700, height=400, key="carte_voyage_stable")
    except Exception:
        st.info("Affichage visuel de la carte.")

    st.markdown("---")
    st.success("✨ Votre aperçu d'itinéraire personnalisé selon votre budget est prêt !")
    
    # --- COUPE DU TEXTE POUR APERÇU GRATUIT (JOUR 1 & 2) ---
    texte_complet = st.session_state["texte_ia"]
    if "Jour 3" in texte_complet:
        texte_gratuit = texte_complet.split("Jour 3")[0]
        st.markdown(texte_gratuit)
        
        # --- ENCART DE PAIEMENT STRIPE POUR LE RESTE ---
        st.markdown("---")
        st.markdown("### 🔒 Débloquez l'itinéraire complet et téléchargez votre guide PDF pro !")
        st.markdown("Pour seulement **4,99 EUR** en paiement unique, accédez instantanément à la totalité de votre fiche de route optimisée, vos conseils secrets et votre planificateur budgétaire exportable.")
        
        # COLO_ICI votre lien Stripe Link
        lien_de_paiement_stripe = "https://stripe.com" 
        st.link_button("💳 Débloquer mon itinéraire complet (4,99 EUR)", lien_de_paiement_stripe, type="primary")
    else:
        st.markdown(texte_complet)
        st.sidebar.markdown("### 📥 Téléchargement")
        st.sidebar.download_button(
            label="Télécharger le Guide PDF Pro 📄",
            data=st.session_state["pdf_cree"],
            file_name=f"Guide_Voyage_{st.session_state['dest']}.pdf",
            mime="application/pdf"
        )


















