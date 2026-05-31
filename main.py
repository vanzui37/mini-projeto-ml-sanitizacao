import csv
import re
from datetime import datetime

# =====================================================================
# FUNÇÕES DE HIGIENIZAÇÃO, TRANSFORMAÇÃO E VALIDAÇÃO (REQUISITOS DO PROJETO)
# =====================================================================

def limpar_categoria(nome_categoria):
    """
    [Sprint 2]: Converte para minúsculas, limpa espaços extras (.strip()) e 
    usa Regex (re) para expurgar caracteres especiais ou pontuações indevidas.
    """
    if not nome_categoria or nome_categoria.strip() == "":
        return "sem categoria"
    
    nome_limpo = nome_categoria.strip().lower()
    nome_limpo = re.sub(r'[^a-z0-9\s_]', '', nome_limpo)
    nome_limpo = re.sub(r'\s+', ' ', nome_limpo).strip()
    return nome_limpo


def tratar_dimensoes_fisicas(valor, default_value="0.0"):
    """
    [Sprint 3]: Valida valores nulos/vazios das dimensões físicas dos produtos.
    """
    if not valor or valor.strip() == "" or valor.lower() in ["null", "none"]:
        return default_value
    return valor.strip()


def formatar_data_br(data_string):
    """
    [Sprint 4]: Converte strings temporais do formato original ISO (YYYY-MM-DD HH:MM:SS) 
    para o formato de data simplificado brasileiro (DD/MM/YYYY) via módulo datetime.
    """
    if not data_string or data_string.strip() == "" or data_string.lower() in ["null", "none"]:
        return ""
    try:
        dt = datetime.strptime(data_string.strip(), "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        return ""


def validar_hipotese_cancelamento(status, data_entrega):
    """
    [Sprint 4]: Estrutura condicional completa para cruzar o status logístico 
    com o preenchimento da data física de entrega do cliente.
    """
    status_limpo = status.strip().lower() if status else ""
    data_vazia = (not data_entrega or data_entrega.strip() == "" or data_entrega.lower() in ["null", "none"])
    
    if status_limpo == "canceled" and data_vazia:
        return True
    return False

# =====================================================================
# PIPELINE PRINCIPAL DE INGESTÃO E GERAÇÃO DE RELATÓRIO
# =====================================================================

def executar_pipeline_olist():
    PATH_PRODUCTS_IN = "olist_products_dataset.csv"
    PATH_PRODUCTS_OUT = "sanitized_products_dataset.csv"
    
    PATH_ORDERS_IN = "olist_orders_dataset.csv"
    PATH_ORDERS_OUT = "sanitized_orders_dataset.csv"
    
    metricas = {
        "produtos_linhas_processadas": 0,
        "produtos_categorias_corrigidas": 0,
        "produtos_dimensoes_corrigidas": 0,
        "pedidos_linhas_processadas": 0,
        "pedidos_cancelados_confirmados": 0,
        "pedidos_ausentes_nao_cancelados": 0
    }
    
    # --- PROCESSAMENTO: PRODUTOS ---
    try:
        with open(PATH_PRODUCTS_IN, mode='r', encoding='utf-8') as infile, \
             open(PATH_PRODUCTS_OUT, mode='w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            
            for row in reader:
                metricas["produtos_linhas_processadas"] += 1
                cat_original = row.get("product_category_name")
                if not cat_original or cat_original.strip() == "":
                    metricas["produtos_categorias_corrigidas"] += 1
                
                row["product_category_name"] = limpar_categoria(cat_original)
                
                campos_dimensoes = ["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]
                dimensao_corrigida_na_linha = False
                
                for campo in campos_dimensoes:
                    valor_original = row.get(campo)
                    valor_tratado = tratar_dimensoes_fisicas(valor_original)
                    if valor_original != valor_tratado:
                        dimensao_corrigida_na_linha = True
                    row[campo] = valor_tratado
                
                if dimensao_corrigida_na_linha:
                    metricas["produtos_dimensoes_corrigidas"] += 1
                
                writer.writerow(row)
    except FileNotFoundError:
        print(f"❌ Erro Crítico: Arquivo '{PATH_PRODUCTS_IN}' não foi localizado.")
        return

    # --- PROCESSAMENTO: PEDIDOS ---
    try:
        with open(PATH_ORDERS_IN, mode='r', encoding='utf-8') as infile, \
             open(PATH_ORDERS_OUT, mode='w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            
            for row in reader:
                metricas["pedidos_linhas_processadas"] += 1
                status = row.get("order_status")
                dt_entrega = row.get("order_delivered_customer_date")
                
                is_vazia = (not dt_entrega or dt_entrega.strip() == "" or dt_entrega.lower() in ["null", "none"])
                
                if is_vazia:
                    if validar_hipotese_cancelamento(status, dt_entrega):
                        metricas["pedidos_cancelados_confirmados"] += 1
                    else:
                        metricas["pedidos_ausentes_nao_cancelados"] += 1
                
                row["order_approved_at"] = formatar_data_br(row.get("order_approved_at"))
                writer.writerow(row)
    except FileNotFoundError:
        print(f"❌ Erro Crítico: Arquivo '{PATH_ORDERS_IN}' não foi localizado.")
        return

    # =====================================================================
    # [Sprint 5]: RELATÓRIO DE STATUS MANUAL (EXIBIÇÃO DE METRICAS)
    # =====================================================================
    print("\n" + "="*60)
    print("      SUMÁRIO ESTATÍSTICO DE SANITIZAÇÃO DE DADOS (OLIST)      ")
    print("="*60)
    print(f"🔹 DATASET DE PRODUTOS:")
    print(f"  - Total de linhas varridas: {metricas['produtos_linhas_processadas']}")
    print(f"  - Registros de categoria vazios mapeados/corrigidos: {metricas['produtos_categorias_corrigidas']}")
    print(f"  - Produtos com dimensões nulas imputados como 0.0: {metricas['produtos_dimensoes_corrigidas']}")
    print(f"\n🔹 DATASET DE PEDIDOS:")
    print(f"  - Total de linhas varridas: {metricas['pedidos_linhas_processadas']}")
    print(f"  - Pedidos Cancelados Legítimos (Data Vazia e Status Canceled): {metricas['pedidos_cancelados_confirmados']}")
    print(f"  - Pedidos com Data Vazia por motivos logísticos/fluxo: {metricas['pedidos_ausentes_nao_cancelados']}")
    print("-"*60)
    print("🔬 COMPROVAÇÃO DO TESTE DE HIPÓTESE DA DIRETORIA:")
    if metricas["pedidos_ausentes_nao_cancelados"] > 0:
        print("  ❌ REJEITADA: Nem todos os registros com data de entrega vazia são\n"
              "     pedidos cancelados! Existem pedidos ativos em status de processamento ou trânsito.")
    else:
        print("  ▲ CONFIRMADA: Todas as datas de entrega nulas pertencem estritamente a pedidos cancelados.")
    print("="*60 + "\n")
    print("🎉 Sucesso! Os novos arquivos estruturados e limpos foram exportados.")

if __name__ == "__main__":
    executar_pipeline_olist()
