import streamlit as st
import numpy as np
import joblib

# Dicionários de mapeamento para as variáveis categóricas (Assumindo Label Encoding)
# ATENÇÃO: Os inteiros (0, 1, 2, ...) devem corresponder exatamente à codificação usada no treinamento do seu modelo!
MAP_HOTEL = {'City Hotel': 0, 'Resort Hotel': 1}
MAP_MEAL = {'BB (Café da Manhã)': 0, 'HB (Meia Pensão)': 1, 'FB (Pensão Completa)': 2, 'SC (Sem Refeição)': 3, 'Undefined': 4}
MAP_MARKET = {'Online TA': 0, 'Offline TA/TO': 1, 'Corporate': 2, 'Groups': 3, 'Complementary': 4, 'Direct': 5, 'Undefined': 6}
MAP_DISTRIBUTION = {'TA/TO': 0, 'Corporate': 1, 'GDS': 2, 'Direct': 3, 'Undefined': 4}
MAP_ROOM_TYPE = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'L': 8}
MAP_DEPOSIT = {'No Deposit': 0, 'Non Refund': 1, 'Refundable': 2}
MAP_CUSTOMER = {'Transient': 0, 'Transient-Party': 1, 'Group': 2, 'Contract': 3}


st.set_page_config(layout="wide")
st.title("🛎️ Previsão de Cancelamento de Reservas")
st.markdown("Insira os 23 parâmetros da reserva para prever a probabilidade de **Cancelamento (1)** ou **Confirmação (0)**.")


# 1. Configurar as três colunas
col1, col2, col3 = st.columns(3)


# Dicionário para armazenar todos os inputs na ordem final
input_values = {}


# --- COLUNA 1: DETALHES DA ESTADIA E CLIENTE ---
with col1:
    st.subheader("🗓️ Datas e Duração da Estadia")

    input_values['lead_time'] = st.number_input(
        "1. Lead Time (dias)", min_value=0, value=50, step=1, help="Tempo de antecedência da reserva em dias."
    )

    input_values['arrival_date_day_of_month'] = st.number_input(
        "2. Dia da Chegada", min_value=1, max_value=31, value=15, step=1
    )

    input_values['stays_in_weekend_nights'] = st.number_input(
        "3. Noites de Fim de Semana", min_value=0, value=2, step=1
    )

    input_values['stays_in_week_nights'] = st.number_input(
        "4. Noites de Semana", min_value=0, value=3, step=1
    )
    
    st.subheader("👥 Ocupação")

    input_values['adults'] = st.number_input(
        "5. Adultos", min_value=1, value=2, step=1
    )

    input_values['children'] = st.number_input(
        "6. Crianças", min_value=0, value=0, step=1
    )

    input_values['babies'] = st.number_input(
        "7. Bebés", min_value=0, value=0, step=1
    )
    
# --- COLUNA 2: HISTÓRICO, FINANÇAS E PEDIDOS ---
with col2:
    st.subheader("💳 Finanças e Histórico")

    # is_repeated_guest (Assumido 0/1)
    is_repeated_guest_desc = st.selectbox(
        "8. Cliente Repetido?", options=['Não (0)', 'Sim (1)'], index=0
    )
    input_values['is_repeated_guest'] = int(is_repeated_guest_desc.split('(')[1].replace(')', ''))

    input_values['previous_cancellations'] = st.number_input(
        "9. Cancelamentos Anteriores", min_value=0, value=0, step=1
    )

    input_values['previous_bookings_not_canceled'] = st.number_input(
        "10. Reservas Anteriores Não Canceladas", min_value=0, value=0, step=1
    )

    input_values['booking_changes'] = st.number_input(
        "11. Alterações na Reserva", min_value=0, value=0, step=1
    )

    input_values['days_in_waiting_list'] = st.number_input(
        "12. Dias em Lista de Espera", min_value=0, value=0, step=1
    )
    
    input_values['adr'] = st.number_input(
        "13. ADR (Taxa Média Diária)", min_value=0.0, value=99.99, step=0.01, format="%.2f", help="Valor médio da diária em moeda local."
    )
    
    st.subheader("extras")
    
    input_values['required_car_parking_spaces'] = st.number_input(
        "14. Lugares de Estacionamento Necessários", min_value=0, value=0, step=1
    )

    input_values['total_of_special_requests'] = st.number_input(
        "15. Total de Pedidos Especiais", min_value=0, value=0, step=1
    )


# --- COLUNA 3: VARIÁVEIS CATEGÓRICAS CODIFICADAS (Chaves Inteiras) ---
with col3:
    st.subheader("🔢 Detalhes da Reserva (Codificados)")
    st.caption("Selecione a opção e o valor inteiro será usado no modelo.")

    # 16. hotel
    hotel_key = st.selectbox("16. Tipo de Hotel", options=list(MAP_HOTEL.keys()))
    input_values['hotel'] = MAP_HOTEL[hotel_key]

    # 17. meal
    meal_key = st.selectbox("17. Tipo de Refeição", options=list(MAP_MEAL.keys()))
    input_values['meal'] = MAP_MEAL[meal_key]

    # 18. market_segment
    market_key = st.selectbox("18. Segmento de Mercado", options=list(MAP_MARKET.keys()))
    input_values['market_segment'] = MAP_MARKET[market_key]

    # 19. distribution_channel
    dist_key = st.selectbox("19. Canal de Distribuição", options=list(MAP_DISTRIBUTION.keys()))
    input_values['distribution_channel'] = MAP_DISTRIBUTION[dist_key]

    # 20. reserved_room_type
    reserved_key = st.selectbox("20. Tipo de Quarto Reservado", options=list(MAP_ROOM_TYPE.keys()), index=0)
    input_values['reserved_room_type'] = MAP_ROOM_TYPE[reserved_key]

    # 21. assigned_room_type
    assigned_key = st.selectbox("21. Tipo de Quarto Atribuído", options=list(MAP_ROOM_TYPE.keys()), index=0)
    input_values['assigned_room_type'] = MAP_ROOM_TYPE[assigned_key]

    # 22. deposit_type
    deposit_key = st.selectbox("22. Tipo de Depósito", options=list(MAP_DEPOSIT.keys()), index=0)
    input_values['deposit_type'] = MAP_DEPOSIT[deposit_key]

    # 23. customer_type
    customer_key = st.selectbox("23. Tipo de Cliente", options=list(MAP_CUSTOMER.keys()), index=0)
    input_values['customer_type'] = MAP_CUSTOMER[customer_key]


st.divider()

# Garantir a ordem correta das features para o modelo
FEATURE_ORDER = ['lead_time', 'arrival_date_day_of_month', 'stays_in_weekend_nights', 'stays_in_week_nights', 'adults', 'children', 'babies', 'is_repeated_guest', 'previous_cancellations', 'previous_bookings_not_canceled', 'booking_changes', 'days_in_waiting_list', 'adr', 'required_car_parking_spaces', 'total_of_special_requests', 'hotel', 'meal', 'market_segment', 'distribution_channel', 'reserved_room_type', 'assigned_room_type', 'deposit_type', 'customer_type']

# Criar a lista de entrada na ordem correta
X_input = [input_values[feature] for feature in FEATURE_ORDER]


# --- Botão de Classificação e Resultados ---
col_empty, col_btn = st.columns([4, 1])
with col_btn:
    detect_button = st.button("🔎 Prever Cancelamento", type="primary", use_container_width=True, disabled=(len(X_input) != 23))

try:
    if detect_button:
        # Carregar o modelo e fazer a previsão
        # NOTA: O arquivo 'model.joblib' precisa ser o modelo de previsão de cancelamento
        model = joblib.load("model_knn.joblib")
        
        # O modelo pode esperar um array NumPy formatado.
        X_input_reshaped = np.array(X_input, dtype=float).reshape(1, -1)
        
        # Se você usou StandardScaler ou MinMaxScaler, a etapa de normalização/padronização
        # do input DEVE ser aplicada aqui antes de passar para o modelo.
        # Exemplo (se seu scaler foi salvo):
        # scaler = joblib.load("scaler.joblib")
        # X_input_scaled = scaler.transform(X_input_reshaped)
        # prev = model.predict(X_input_scaled)
        
        prev = model.predict(X_input_reshaped)
        
        st.subheader("Resultado da Previsão")
        
        if prev[0] == 0:
            st.success("✅ O modelo prevê que a reserva **NÃO SERÁ CANCELADA** (0).")
        else:
            st.error("⚠️ O modelo prevê que a reserva **SERÁ CANCELADA** (1).")
            
        st.metric(label="Previsão Bruta do Modelo", value=f"{prev[0]}")
    
except FileNotFoundError:
    if detect_button:
        st.error("Erro: O arquivo 'model.joblib' não foi encontrado.")
        st.warning("Certifique-se de que o seu modelo serializado está no mesmo diretório do script.")
except Exception as e:
    if detect_button:
        st.error(f"Erro ao executar a previsão: {e}")
        st.warning("Verifique a ordem dos 23 parâmetros, o tipo de dados (int/float) e se o modelo espera dados normalizados.")