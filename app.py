import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Grade Mestra Pro", layout="wide")

# CSS para garantir que a tabela fique legível e pronta para print
st.markdown("""
<style>
    @media print { .no-print, .stSidebar, button { display: none !important; } }
    .stTable { background-color: white !important; color: black !important; width: 100%; border-collapse: collapse; }
    td { white-space: pre-wrap !important; font-size: 13px !important; text-align: center !important; border: 1px solid #ddd !important; padding: 6px !important; color: black !important; }
    th { background-color: #f0f2f6 !important; color: black !important; border: 1px solid #ddd !important; }
</style>
""", unsafe_allow_html=True)

st.title("📚 Grade Mestra Pro")
escola = st.text_input("🏢 Nome da Escola", "Minha Escola")

# --- LÓGICA DE CÁLCULO ---
def calcular_grade(inicio, dur_aula, h_rec, dur_rec):
    blocos = []
    h_at = datetime.combine(datetime.today(), inicio)
    h_rec_ini = datetime.combine(datetime.today(), h_rec)
    h_rec_fim = h_rec_ini + timedelta(minutes=dur_rec)
    for i in range(1, 6):
        fim_prev = h_at + timedelta(minutes=dur_aula)
        if h_at < h_rec_ini and fim_prev > h_rec_ini:
            blocos.append(f"{i}ª Aula (A): {h_at.strftime('%H:%M')}-{h_rec_ini.strftime('%H:%M')}")
            blocos.append(f"☕ RECREIO: {h_rec_ini.strftime('%H:%M')}-{h_rec_fim.strftime('%H:%M')}")
            restante = (fim_prev - h_rec_ini).seconds // 60
            fim_b = h_rec_fim + timedelta(minutes=restante)
            blocos.append(f"{i}ª Aula (B): {h_rec_fim.strftime('%H:%M')}-{fim_b.strftime('%H:%M')}")
            h_at = fim_b
        else:
            if h_at >= h_rec_ini and h_at < h_rec_fim: h_at = h_rec_fim
            if h_at == h_rec_ini:
                blocos.append(f"☕ RECREIO: {h_rec_ini.strftime('%H:%M')}-{h_rec_fim.strftime('%H:%M')}")
                h_at = h_rec_fim
            ini_s = h_at.strftime("%H:%M")
            h_at += timedelta(minutes=dur_aula)
            blocos.append(f"{i}ª Aula: {ini_s}-{h_at.strftime('%H:%M')}")
    return blocos

# --- ABAS ---
abas = st.tabs(["🌅 MATUTINO", "☀️ VESPERTINO", "🌙 NOTURNO"])
turnos = [("Matutino", "07:07", abas[0]), ("Vespertino", "13:03", abas[1]), ("Noturno", "18:30", abas[2])]

for nome, h_padrao, aba in turnos:
    with aba:
        with st.sidebar:
            # FORMULÁRIO PARA EVITAR O RESET AUTOMÁTICO
            with st.form(key=f"form_{nome}"):
                st.header(f"⚙️ Config {nome}")
                hi = st.time_input(f"Início {nome}", datetime.strptime(h_padrao, "%H:%M"))
                da = st.number_input(f"Duração Aula (min)", 15, 120, 45)
                hr = st.time_input(f"Início Recreio", datetime.strptime("09:15", "%H:%M"))
                dr = st.number_input(f"Duração Recreio", 5, 60, 20)
                submit = st.form_submit_button("✅ Aplicar Horários")

        horarios = calcular_grade(hi, da, hr, dr)
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        grade_dados = {"Horário": horarios}
        
        cols = st.columns(5)
        for idx, dia in enumerate(dias):
            with cols[idx]:
                st.markdown(f"**{dia}**")
                col_dia = []
                for h in horarios:
                    if "☕" in h:
                        col_dia.append("☕ RECREIO")
                    else:
                        with st.expander(f"⌚ {h}"):
                            tipo = st.radio("Status", ["Aula", "Vaga"], key=f"t_{nome}_{dia}_{h}", horizontal=True)
                            if tipo == "Aula":
                                s = st.text_input("Sala", key=f"s_{nome}_{dia}_{h}")
                                p = st.text_input("Prof", key=f"p_{nome}_{dia}_{h}")
                                col_dia.append(f"{s}|{p}" if s else " ")
                            else:
                                col_dia.append("AULA VAGA")
                grade_dados[dia] = col_dia

        st.markdown("---")
        if st.button(f"🚀 GERAR TABELA {nome.upper()}", key=f"btn_{nome}"):
            st.markdown(f"<h2 style='text-align:center;'>{escola}</h2>", unsafe_allow_html=True)
            df = pd.DataFrame(grade_dados)
            for d in dias: df[d] = df[d].apply(lambda x: x.replace("|", "\n") if "|" in x else x)
            st.table(df)
            st.markdown('<button onclick="window.print()" style="width:100%; padding:15px; background-color:#28a745; color:white; border-radius:8px; cursor:pointer;">📸 PRINTAR / SALVAR</button>', unsafe_allow_html=True)
            
