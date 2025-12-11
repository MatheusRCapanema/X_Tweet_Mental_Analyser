
import streamlit as st
import joblib
import pandas as pd
import plotly.express as px
import os
from src.scraper import run_scrape
from src.utils import analyze_profile, translate_text

# Page Config
st.set_page_config(
    page_title="Mental Health Tweet Analyzer",
    page_icon="🧠",
    layout="wide"
)

# Load Model
@st.cache_resource
def load_model():
    model_path = "models/mental_health_model.pkl"
    if not os.path.exists(model_path):
        return None
    return joblib.load(model_path)

model = load_model()

# Title
st.title("🧠 Análise de Saúde Mental (Twikit Edition)")

# Sidebar for Credentials
# Sidebar for Credentials
st.sidebar.header("🔐 Autenticação X (Twitter)")

auth_method = st.sidebar.radio("Método de Login", ["Cookies (Recomendado)", "Usuário/Senha"])

cookies_file_path = None
auth_info = None

if auth_method == "Cookies (Recomendado)":
    st.sidebar.info("Exporte seus cookies usando a extensão 'EditThisCookie' e salve como `cookies.json`.")
    uploaded_cookies = st.sidebar.file_uploader("Upload cookies.json", type="json")
    if uploaded_cookies:
        # Save loaded file temporarily
        cookies_file_path = "cookies.json"
        with open(cookies_file_path, "wb") as f:
            f.write(uploaded_cookies.getbuffer())
        st.sidebar.success("Cookies carregados!")
else:
    st.sidebar.info("Login direto pode ser bloqueado pelo Cloudflare.")
    my_username = st.sidebar.text_input("Username (@)", value="MatheusDev") 
    my_email = st.sidebar.text_input("Email")
    my_password = st.sidebar.text_input("Senha", type="password")
    
    if my_username and my_email and my_password:
        auth_info = {
            'username': my_username.replace("@", ""),
            'email': my_email,
            'password': my_password
        }
    else:
        st.sidebar.warning("Preencha todos os campos.")

# Tabs
tab1, tab2 = st.tabs(["📝 Análise de Frase", "👤 Análise de Perfil (Login Required)"])

# --- TAB 1 ---
with tab1:
    st.subheader("Análise Rápida")
    user_input = st.text_area("Digite um tweet:", height=100)
    if st.button("Analisar Frase"):
        if not model:
            st.error("Erro: Modelo não encontrado.")
        elif not user_input.strip():
            st.warning("Digite algo.")
        else:
            with st.spinner("Analisando..."):
                translated = translate_text(user_input)
                prediction_class = model.predict([translated])[0]
                prediction_probs = model.predict_proba([translated])[0]
                classes = model.classes_
                
                c1, c2 = st.columns(2)
                with c1:
                    st.success(f"Original: {user_input}")
                    st.metric("Resultado", prediction_class)
                with c2:
                    prob_df = pd.DataFrame({'Categoria': classes, 'Probabilidade': prediction_probs})
                    st.plotly_chart(px.bar(prob_df, x='Probabilidade', y='Categoria', orientation='h'), use_container_width=True)

# --- TAB 2 ---
with tab2:
    st.subheader("Análise de Perfil (Via Twikit)")
    
    target_user = st.text_input("Perfil Alvo (ex: elonmusk):")
    
    if st.button("🔍 Buscar e Analisar"):
        if not (cookies_file_path or auth_info):
            st.error("⚠️ Configure a autenticação na barra lateral (Cookies ou Login).")
        elif not target_user:
            st.warning("Digite o perfil alvo.")
        else:
            target_user = target_user.replace("@", "").strip()
            
            with st.status("Autenticando e Buscando Tweets...", expanded=True) as status:
                st.write("Conectando ao Twitter...")
                try:
                    df_tweets = run_scrape(target_user, auth_info, cookies_file_path)
                    
                    if df_tweets is None or df_tweets.empty:
                        status.update(label="Erro no Login/Busca", state="error")
                        st.error("⚠️ O Twitter/X bloqueou o acesso automático (Cloudflare Block). Isso é comum em ferramentas de scraping.")
                        
                        st.markdown("### 🛠️ Modo Manual (Salva-vidas)")
                        st.info("Não se preocupe! Você ainda pode analisar o perfil colando os tweets abaixo:")
                        manual_text = st.text_area("Cole os tweets aqui (um por linha):", height=200)
                        
                        if st.button("Analisar Texto Manual"):
                            lines = [line.strip() for line in manual_text.split('\n') if line.strip()]
                            if lines:
                                # Simulate dataframe
                                df_analyzed = analyze_profile(pd.DataFrame({'text': lines}), model)
                                
                                # --- RESULTS DASHBOARD REPEATED (Manual Mode) ---
                                st.divider()
                                
                                counts = df_analyzed['prediction'].value_counts()
                                total_tweets = len(df_analyzed)
                                
                                # Risk Logic
                                if 'Suicidal' in counts and counts['Suicidal'] > 0:
                                    most_common = "⚠️ Risco de Suicídio Detectado"
                                    st.error("🚨 ALERTA: Conteúdo indica Comportamento Suicida.")
                                elif 'Depression' in counts and (counts['Depression'] / total_tweets > 0.15):
                                    most_common = "Depressão"
                                else:
                                    most_common = df_analyzed['prediction'].mode()[0]
                                
                                m1, m2 = st.columns(2)
                                m1.metric("Diagnóstico Sugerido", most_common)
                                m2.metric("Confiança Média", f"{df_analyzed['probability'].mean():.1%}")
                                
                                c1, c2 = st.columns(2)
                                c1.plotly_chart(px.pie(df_analyzed, names='prediction', title="Distribuição",
                                     color='prediction',
                                     color_discrete_map={
                                         "Normal": "#2ecc71",
                                         "Suicidal": "#e74c3c",
                                         "Depression": "#e67e22", 
                                         "Anxiety": "#f1c40f"
                                     }), use_container_width=True)
                                c2.dataframe(df_analyzed)
                            else:
                                st.warning("Cole algo!")
                    else:
                        status.update(label="Sucesso!", state="complete")
                        st.success(f"Baixados {len(df_tweets)} tweets de @{target_user}.")
                        
                        # Analyze
                        df_analyzed = analyze_profile(df_tweets, model)
                        
                        # Dashboard
                        st.divider()
                        
                      # --- RESULTS DASHBOARD ---
                    st.divider()
                    
                    # 1. Overview Metrics (With Severity Logic)
                    # Priority: Suicidal > Depression > Bipolar > Anxiety > Normal
                    counts = df_analyzed['prediction'].value_counts()
                    total_tweets = len(df_analyzed)
                    
                    # Risk Detection Logic
                    if 'Suicidal' in counts and counts['Suicidal'] > 0:
                        most_common = "⚠️ Risco de Suicídio Detectado"
                        st.error("🚨 ALERTA: Este perfil contém indícios de Comportamento Suicida.")
                    elif 'Depression' in counts and (counts['Depression'] / total_tweets > 0.15): # If > 15% depression
                        most_common = "Depressão (Tendência Dominante)"
                    elif 'Anxiety' in counts and (counts['Anxiety'] / total_tweets > 0.15):
                         most_common = "Ansiedade (Tendência Dominante)"
                    else:
                        most_common = df_analyzed['prediction'].mode()[0]

                    avg_prob = df_analyzed['probability'].mean()
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Tweets Analisados", total_tweets)
                    m2.metric("Diagnóstico do Perfil", most_common)
                    m3.metric("Confiança Média", f"{avg_prob:.1%}")
                    
                    # 2. Breakdown Chart
                    st.subheader("Distribuição de Sentimentos")
                    counts_df = counts.reset_index()
                    counts_df.columns = ['Categoria', 'Contagem']
                    fig_pie = px.pie(counts_df, values='Contagem', names='Categoria', hole=0.4, 
                                     color='Categoria',
                                     color_discrete_map={
                                         "Normal": "#2ecc71",
                                         "Suicidal": "#e74c3c",
                                         "Depression": "#e67e22",
                                         "Anxiety": "#f1c40f",
                                         "Bipolar": "#9b59b6",
                                         "Stress": "#34495e"
                                     })
                    st.plotly_chart(fig_pie, use_container_width=True)
                        
                    # Display raw data
                    st.subheader("Tweets Analisados")
                    if 'date' in df_analyzed.columns:
                        st.dataframe(df_analyzed[['date', 'original_text', 'prediction']])
                            
                except Exception as e:
                    status.update(label="Erro Crítico", state="error")
                    st.error(f"Ocorreu um erro: {e}")
