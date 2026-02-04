import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Grade Mestra Pro", layout="wide")

# Estilo para manter cores no Print
st.markdown("""
<style>
    @media print { .no-print, .stSidebar, button { display: none !important; } }
    .stTable { background-color: white !important; color: black !important; width: 100%; border-collapse: collapse; }
    td { white-space: pre-wrap !important; font-size: 13px !important; text-align: center !important; border: 1px solid #ddd !important; padding: 6px !important; color: black !important; }
    th { background-color: #f0f2f6 !important; color: black !important; border: 1px solid #ddd !important; }
</style>
""", unsafe_allow_html=True)

# --- A CHAVE DA SOLUÇÃO: MEMÓRIA TOTAL ---
if 'dados' not in st.session_state:
    st.session_state.dados = {
        "Matutino_ini": datetime.strptime("07:07", "%H:%M").time(),
        "Matutino_rec": datetime.strptime("09:15", "%H:%M").time(),
        "Vespertino_ini": datetime.strptime("13:03", "%H:%M").time(),
        "Vespertino_rec": datetime.strptime("15:15", "%H:%M").time(),
        "Noturno_ini": datetime.strptime("18:30", "%H:%M").time(),
        "Noturno_rec": datetime.strptime("20:30", "%H:%M").time(),
        "salas_salvas": [],
        "profs_salvos": []
    }

st.title("📚 Grade Mestra Pro")
escola = st.text_input("🏢 Nome da Escola", "Minha Escola")

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
            # Vinculamos o valor diretamente à memória da sessão
            hi = st.time_input(f"Início {nome}", value=st.session_state.dados[f"{nome}_ini"], key=f"ti_{nome}")
            st.session_state.dados[f"{nome}_ini"] = hi # Salva na hora
            
            da = st.number_input(f"Duração Aula (min)", 15, 120, 45, key=f"da_{nome}")
            
            hr = st.time_input(f"Início Recreio {nome}", value=st.session_state.dados[f"{nome}_rec"], key=f"tr_{nome}")
            st.session_state.dados[f"{nome}_rec"] = hr # Salva na hora
            
            dr = st.number_input(f"Duração Recreio", 5, 60, 20, key=f"dr_{nome}")

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
                                # MEMÓRIA DE SALA/PROF VOLTOU
                                s_sel = st.selectbox("Sala Salva", [""] + sorted(list(set(st.session_state.dados["salas_salvas"]))), key=f"ss_{nome}_{dia}_{h}")
                                s_txt = st.text_input("Nova Sala", key=f"s_{nome}_{dia}_{h}")
                                sala_f = s_sel if s_sel != "" else s_txt
                                
                                p_sel = st.selectbox("Prof Salva", [""] + sorted(list(set(st.session_state.dados["profs_salvos"]))), key=f"ps_{nome}_{dia}_{h}")
                                p_txt = st.text_input("Nova Prof", key=f"p_{nome}_{dia}_{h}")
                                prof_f = p_sel if p_sel != "" else p_txt
                                
                                if s_txt and s_txt not in st.session_state.dados["salas_salvas"]: st.session_state.dados["salas_salvas"].append(s_txt)
                                if p_txt and p_txt not in st.session_state.dados["profs_salvos"]: st.session_state.dados["profs_salvos"].append(p_txt)
                                
                                col_dia.append(f"{sala_f}|{prof_f}" if sala_f else " ")
                            else:
                                col_dia.append("AULA VAGA")
                grade_final[dia] = col_dia

        if st.button(f"🚀 GERAR TABELA {nome.upper()}", key=f"btn_{nome}"):
            st.markdown(f"### {escola} - Turno {nome}")
            df = pd.DataFrame(grade_final)
            for d in dias: df[d] = df[d].apply(lambda x: x.replace("|", "\n") if "|" in x else x)
            st.table(df)
            st.markdown('<button onclick="window.print()" style="width:100%; padding:10px; background-color:#28a745; color:white; border-radius:5px;">📸 SALVAR PRINT</button>', unsafe_allow_html=True)
            
