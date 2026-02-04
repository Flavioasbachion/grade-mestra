import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Grade Mestra Pro", layout="wide")

st.markdown("""
<style>
    @media print { .no-print, .stSidebar, button { display: none !important; } }
    .stTable { background-color: white !important; color: black !important; width: 100%; border-collapse: collapse; }
    td { white-space: pre-wrap !important; font-size: 13px !important; text-align: center !important; border: 1px solid #ddd !important; padding: 6px !important; color: black !important; }
    th { background-color: #f0f2f6 !important; color: black !important; border: 1px solid #ddd !important; }
</style>
""", unsafe_allow_html=True)

st.title("📚 Grade Mestra Pro")
escola = st.text_input("🏢 Escola", "Minha Escola")

if 'h_salas' not in st.session_state: st.session_state['h_salas'] = []
if 'h_profs' not in st.session_state: st.session_state['h_profs'] = []

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

abas = st.tabs(["🌅 MATUTINO", "☀️ VESPERTINO", "🌙 NOTURNO"])
turnos = [("Matutino", "07:03", abas[0]), ("Vespertino", "13:07", abas[1]), ("Noturno", "18:30", abas[2])]

for nome, h_p, aba in turnos:
    with aba:
        with st.sidebar:
            st.header(f"⚙️ {nome}")
            hi = st.time_input(f"Início {nome}", datetime.strptime(h_p, "%H:%M"), key=f"hi_{nome}")
            da = st.number_input(f"Duração Aula", 15, 120, 45, key=f"da_{nome}")
            hr = st.time_input(f"Recreio {nome}", datetime.strptime("09:15", "%H:%M"), key=f"hr_{nome}")
            dr = st.number_input(f"Duração Recreio", 5, 60, 20, key=f"dr_{nome}")
        
        horarios = calcular_grade(hi, da, hr, dr)
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        grade = {"Horário": horarios}
        
        cols = st.columns(5)
        for idx, dia in enumerate(dias):
            with cols[idx]:
                st.markdown(f"**{dia}**")
                col_dados = []
                for h in horarios:
                    if "☕" in h: col_dados.append("☕ RECREIO")
                    else:
                        with st.expander(f"⌚ {h}"):
                            s = st.text_input("Sala", key=f"s_{nome}_{dia}_{h}")
                            p = st.text_input("Prof", key=f"p_{nome}_{dia}_{h}")
                            col_dados.append(f"{s}|{p}" if s else "AULA VAGA")
                grade[dia] = col_dados
        
        if st.button(f"🚀 GERAR {nome.upper()}", key=f"G_{nome}"):
            st.write(f"### {escola} - {nome}")
            df = pd.DataFrame(grade)
            for d in dias: df[d] = df[d].apply(lambda x: x.replace("|", "\n"))
            st.table(df)
            st.markdown('<button onclick="window.print()">📸 SALVAR PRINT</button>', unsafe_allow_html=True)
          
