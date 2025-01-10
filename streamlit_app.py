import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, date
import matplotlib.pyplot as plt

# Configuration de la page Streamlit
st.set_page_config(page_title="Analyse DCA Bitcoin", layout="wide", initial_sidebar_state="expanded")

# Ajout d'un lien vers ton profil X
st.markdown("""
<div style='text-align: right; margin-bottom: -10px;'>
    <a href="https://x.com/besbtc" target="_blank" style="color: #1DA1F2; font-size: 24px; text-decoration: none;">
        🐦 Suivez-moi sur X
    </a>
</div>
""", unsafe_allow_html=True)

# Titre principal avec description
st.title("📊 Analyse DCA ₿itcoin")
st.markdown("""
Cette application vous permet d'analyser une stratégie de Dollar-Cost Averaging (DCA) sur Bitcoin.
""")

# Sidebar pour les paramètres de DCA
with st.sidebar:
    st.header("🔧 Paramètres de DCA")
    start_date = st.date_input("Début du DCA", value=date(2020, 1, 1))
    end_date = st.date_input("Fin du DCA", value=datetime.today().date())
    monthly_investment = st.number_input("Montant mensuel en $", value=500, min_value=10)

# Vérification des dates
if start_date >= end_date:
    st.error("La date de début doit être antérieure à la date de fin.")
else:
    # Récupération des données Bitcoin
    try:
        btc_data = yf.download("BTC-USD", start=start_date, end=end_date)
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données Bitcoin : {e}")
        st.stop()

    # Préparation des données
    btc_data = btc_data[["Close"]].reset_index()
    btc_data.columns = ["Date", "Close"]

    # Simulation DCA
    dca_dates = pd.date_range(start=start_date, end=end_date, freq="MS")
    dca_data = []
    total_btc = 0
    total_invested = 0
    portfolio_values = []  # Stocker les valeurs pour les drawdowns

    for i, dca_date in enumerate(dca_dates):
        closest_price = btc_data[btc_data["Date"] <= dca_date].iloc[-1]["Close"]
        btc_bought = monthly_investment / closest_price

        total_btc += btc_bought
        total_invested += monthly_investment

        current_value = total_btc * closest_price
        roi = ((current_value - total_invested) / total_invested) * 100
        average_price_over_time = total_invested / total_btc  # Prix moyen d'achat évolutif
        portfolio_values.append(current_value)

        dca_data.append({
            "Date": dca_date,
            "BTC Price ($)": closest_price,
            "BTC Bought": btc_bought,
            "Total BTC": total_btc,
            "Total Invested ($)": total_invested,
            "Current Value ($)": current_value,
            "ROI (%)": roi,
            "Average Price ($)": average_price_over_time  # Ajout du prix moyen à chaque moment
        })

    # Création du DataFrame pour le DCA
    dca_df = pd.DataFrame(dca_data)

    # Calculs statistiques clés
    portfolio_series = pd.Series(portfolio_values)
    cumulative_max = portfolio_series.cummax()
    drawdowns = (portfolio_series - cumulative_max) / cumulative_max
    max_drawdown = drawdowns.min()  # Max drawdown
    last_drawdown = drawdowns.iloc[-1]  # Dernier drawdown

    average_buy_price = total_invested / total_btc  # Prix moyen d'achat
    cagr = ((portfolio_values[-1] / portfolio_values[0]) ** (1 / ((end_date.year - start_date.year) + 1)) - 1) * 100

    # Statistiques visuelles améliorées
    st.markdown("### 📈 Statistiques clés")
    col1, col2, col3 = st.columns(3)

    # Total investi
    col1.metric(
        "Total investi ($)",
        f"${total_invested:,.2f}",
        help="Montant total investi dans la stratégie DCA."
    )

    # Valeur portefeuille
    col2.metric(
        "Valeur portefeuille ($)",
        f"${portfolio_values[-1]:,.2f}",
        delta=f"{portfolio_values[-1] - total_invested:,.2f}",
        help="Valeur actuelle du portefeuille basée sur le prix du BTC.",
        delta_color="normal"  # Vert si positif, rouge si négatif
    )

    # ROI Total
    col3.metric(
        "ROI Total (%)",
        f"{dca_df['ROI (%)'].iloc[-1]:.2f} %",
        delta=f"{dca_df['ROI (%)'].iloc[-1] - 100:.2f} %",
        help="Retour sur investissement total.",
        delta_color="normal"  # Vert pour positif, rouge pour négatif
    )

    col4, col5, col6 = st.columns(3)

    # Total BTC possédé
    col4.metric(
        "Total BTC possédé",
        f"{total_btc:.6f} ₿",
        help="Quantité totale de Bitcoin accumulée avec cette stratégie."
    )

    # Prix moyen d'achat
    col5.metric(
        "Prix moyen d'achat ($)",
        f"${average_buy_price:.2f}",
        help="Prix moyen d'achat du Bitcoin basé sur le montant investi."
    )

    # CAGR
    col6.metric(
        "CAGR (%)",
        f"{cagr:.2f} %",
        help="Taux de croissance annuel composé."
    )

    col7, col8 = st.columns(2)

    # Max Drawdown
    col7.metric(
        "Max Drawdown (%)",
        f"{max_drawdown:.2%}",
        help="Perte maximale par rapport au pic précédent.",
        delta_color="inverse"  # Rouge pour négatif
    )

    # Dernier Drawdown
    col8.metric(
        "Dernier Drawdown (%)",
        f"{last_drawdown:.2%}",
        help="Perte actuelle par rapport au dernier pic.",
        delta_color="inverse"  # Rouge pour négatif
    )

    # **Graphiques combinés**
    st.markdown("### 📊 Évolution du portefeuille, prix du Bitcoin et prix moyen d'achat")
    #st.markdown("#### Évolution du portefeuille, prix du Bitcoin et prix moyen d'achat")

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Graphique de la valeur du portefeuille
    ax1.plot(dca_df["Date"], dca_df["Current Value ($)"], color="blue", label="Valeur du portefeuille ($)")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Valeur du portefeuille ($)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")

    # Graphique du prix du Bitcoin
    ax2 = ax1.twinx()
    ax2.plot(btc_data["Date"], btc_data["Close"], color="orange", label="Prix du Bitcoin ($)")
    ax2.set_ylabel("Prix du Bitcoin ($)", color="orange")
    ax2.tick_params(axis="y", labelcolor="orange")

    # Courbe du prix moyen d'achat
    ax2.plot(dca_df["Date"], dca_df["Average Price ($)"], color="green", linestyle="-", label="Prix moyen d'achat ($)")

    # Annotation personnalisée
    ax1.annotate("@besbtc", xy=(0.5, 0.5), xycoords="axes fraction",
                 fontsize=12, color="gray", ha="center", va="center", alpha=0.6)

    # Ajustement de la légende
    ax1_lines, ax1_labels = ax1.get_legend_handles_labels()
    ax2_lines, ax2_labels = ax2.get_legend_handles_labels()
    lines = ax1_lines + ax2_lines
    labels = ax1_labels + ax2_labels
    ax1.legend(lines, labels, loc="upper left", bbox_to_anchor=(0.05, 0.95), fontsize=10)

    st.pyplot(fig)

    # **Tableau des résultats détaillés**
    st.markdown("### 📋 Résultats détaillés")
    st.dataframe(dca_df.style.format({"BTC Price ($)": "${:.2f}", "Total Invested ($)": "${:.2f}",
                                      "Current Value ($)": "${:.2f}", "ROI (%)": "{:.2f}%"}))
