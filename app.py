import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuração de Layout
st.set_page_config(page_title="Grade Mestra Pro", layout="wide")

# CSS para garantir cores no Print e visual limpo
st.markdown("""
<style>
    @media print { .no-print, .stSidebar, button { display: none !important; } }
    .stTable { background-color: white !important; color: black !important; width: 100%; border-collapse: collapse; }
    td { white-space: pre-wrap !important; font-size: 13px !important; text-align: center !important; border: 1px solid #ddd !important; padding: 6px !important; color: black !important; }
    th { background-color: #f0f2f6 !important; color: black !important; border: 1px solid #ddd !important; }
</style>
""", unsafe_allow_html=True)

st.title("📚 Grade Mestra Pro")
escola = st.text_input("🏢 Escola", "Minha Escola Municipal")

# --- MEMÓRIA DO APP (Persistência de dados) ---
if 'h_salas' not in st.session_state: st.session_state['h_salas'] = []
if 'h_profs' not in st.session_state: st.session_state['h_profs'] = []

# --- LÓGICA DE HORÁRIO FLEXÍVEL ---
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

# --- ABAS DE TURNOS ---
abas = st.tabs(["🌅 MATUTINO", "☀️ VESPERTINO", "🌙 NOTURNO"])
turnos = [("Matutino", "07:07", abas[0]), ("Vespertino", "13:03", abas[1]), ("Noturno", "18:30", abas[2])]

for nome, h_p, aba in turnos:
    with aba:
        with st.sidebar:
            st.header(f"⚙️ Config {nome}")
            hi = st.time_input(f"Início {nome}", datetime.strptime(h_p, "%H:%M"), key=f"hi_{nome}")
            da = st.number_input(f"Duração Aula (min)", 15, 120, 45, key=f"da_{nome}")
            hr = st.time_input(f"Recreio {nome}", datetime.strptime("09:15", "%H:%M"), key=f"hr_{nome}")
            dr = st.number_input(f"Duração Recreio", 5, 60, 20, key=f"dr_{nome}")
        
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
                            # OPÇÃO DE AULA VAGA VOLTOU
                            tipo = st.radio("Status", ["Aula", "Vaga"], key=f"tp_{nome}_{dia}_{h}", horizontal=True)
                            
                            if tipo == "Aula":
                                # MEMÓRIA DE SALAS E PROFS VOLTOU
                                s_sel = st.selectbox("Sala Salva", [""] + sorted(list(set(st.session_state['h_salas']))), key=f"ss_{nome}_{dia}_{h}")
                                s_txt = st.text_input("Nova Sala", key=f"s_{nome}_{dia}_{h}")
                                sala_f = s_sel if s_sel != "" else s_txt
                                
                                p_sel = st.selectbox("Prof Salva", [""] + sorted(list(set(st.session_state['h_profs']))), key=f"ps_{nome}_{dia}_{h}")
                                p_txt = st.text_input("Nova Prof", key=f"p_{nome}_{dia}_{h}")
                                prof_f = p_sel if p_sel != "" else p_txt
                                
                                # Salva na memória se for algo novo
                                if s_txt and s_txt not in st.session_state['h_salas']: st.session_state['h_salas'].append(s_txt)
                                if p_txt and p_txt not in st.session_state['h_profs']: st.session_state['h_profs'].append(p_txt)
                                
                                col_dia.append(f"{sala_f}|{prof_f}" if sala_f else " ")
                            else:
                                col_dia.append("AULA VAGA")
                grade_dados[dia] = col_dia
        
        st.markdown("---")
        if st.button(f"🚀 GERAR TABELA {nome.upper()}", key=f"G_{nome}"):
            st.markdown(f"<h2 style='text-align:center;'>{escola}</h2>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center;'>Turno {nome}</h3>", unsafe_allow_html=True)
            
            df = pd.DataFrame(grade_dados)
            # Limpeza visual para o Print (substitui o | por quebra de linha)
            df_view = df.copy()
            for d in dias:
                df_view[d] = df_view[d].apply(lambda x: x.replace("|", "\n") if "|" in x else x)
            
            st.table(df_view)
            
            st.markdown(f"""
                <button onclick="window.print()" style="width:100%; padding:15px; background-color:#28a745; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">
                📸 CLIQUE PARA SALVAR / TIRAR PRINT
                </button>
            """, unsafe_allow_html=True)
                                
