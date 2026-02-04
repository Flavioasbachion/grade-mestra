import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Grade Mestra Pro", layout="wide")

# Estilos de Visualização
st.markdown("""
<style>
    @media print { .no-print, .stSidebar, button { display: none !important; } }
    .stTable { background-color: white !important; color: black !important; width: 100%; border-collapse: collapse; }
    td { white-space: pre-wrap !important; font-size: 13px !important; text-align: center !important; border: 1px solid #ddd !important; padding: 6px !important; color: black !important; }
    th { background-color: #f0f2f6 !important; color: black !important; border: 1px solid #ddd !important; }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE MEMÓRIA CRÍTICA ---
# Isso garante que os horários não resetem ao interagir com a tela
if 'config' not in st.session_state:
    st.session_state.config = {
        "Matutino_ini": datetime.strptime("07:07", "%H:%M").time(),
        "Matutino_rec": datetime.strptime("09:15", "%H:%M").time(),
        "Vespertino_ini": datetime.strptime("13:03", "%H:%M").time(),
        "Vespertino_rec": datetime.strptime("15:15", "%H:%M").time(),
        "Noturno_ini": datetime.strptime("18:30", "%H:%M").time(),
        "Noturno_rec": datetime.strptime("20:30", "%H:%M").time(),
        "salas": [],
        "profs": []
    }

st.title("📚 Grade Mestra Pro")
escola = st.text_input("🏢 Escola", "Minha Escola Municipal")

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
turnos = [("Matutino", abas[0]), ("Vespertino", abas[1]), ("Noturno", abas[2])]

for nome, aba in turnos:
    with aba:
        with st.sidebar:
            st.header(f"⚙️ Config {nome}")
            
            # CHAVE DE OURO: O componente usa a memória da sessão como valor e salva nela mesma
            hi = st.time_input(f"Início {nome}", 
                              value=st.session_state.config[f"{nome}_ini"], 
                              key=f"time_ini_{nome}")
            st.session_state.config[f"{nome}_ini"] = hi
            
            da = st.number_input(f"Duração Aula (min)", 15, 120, 45, key=f"dur_{nome}")
            
            hr = st.time_input(f"Recreio {nome}", 
                              value=st.session_state.config[f"{nome}_rec"], 
                              key=f"time_rec_{nome}")
            st.session_state.config[f"{nome}_rec"] = hr
            
            dr = st.number_input(f"Duração Recreio", 5, 60, 20, key=f"dr_val_{nome}")

        horarios = calcular_grade(hi, da, hr, dr)
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        grade_final = {"Horário": horarios}
        
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
                            tipo = st.radio("Status", ["Aula", "Vaga"], key=f"tp_{nome}_{dia}_{h}", horizontal=True)
                            if tipo == "Aula":
                                # Sugestões baseadas no que já foi digitado
                                s_txt = st.text_input("Sala", key=f"s_{nome}_{dia}_{h}")
                                p_txt = st.text_input("Prof", key=f"p_{nome}_{dia}_{h}")
                                col_dia.append(f"{s_txt}|{p_txt}" if s_txt else " ")
                            else:
                                col_dia.append("AULA VAGA")
                grade_final[dia] = col_dia

        if st.button(f"🚀 GERAR TABELA {nome.upper()}", key=f"btn_{nome}"):
            st.markdown(f"<h2 style='text-align:center;'>{escola}</h2><h3 style='text-align:center;'>Turno {nome}</h3>", unsafe_allow_html=True)
            df = pd.DataFrame(grade_final)
            df_v = df.copy()
            for d in dias: df_v[d] = df_v[d].apply(lambda x: x.replace("|", "\n") if "|" in x else x)
            st.table(df_v)
            st.markdown('<button onclick="window.print()" style="width:100%; padding:10px; background-color:#28a745; color:white; border-radius:5px; cursor:pointer;">📸 SALVAR PRINT</button>', unsafe_allow_html=True)
            
