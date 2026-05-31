# 📦 Mini-Projeto: Pipeline de Sanitização de Dados (Olist)

Este projeto foi desenvolvido como um Mini-Projeto Avaliativo de programação estruturada aplicada à Engenharia e Análise de Dados. O objetivo principal é construir um ecossistema resiliente de higienização de dados usando estritamente as ferramentas nativas do ecossistema Python (sem frameworks externos como Pandas), simulando as restrições comuns enfrentadas por equipes de dados em ambientes produtivos de alto desempenho.

---

## 🎯 Descrição do Projeto

A equipe de Engenharia de Dados da Olist extraiu lotes transacionais do banco de dados relacional oficial, distribuídos em dois arquivos estruturados primários: `olist_products_dataset.csv` e `olist_orders_dataset.csv`. Contudo, inconsistências estruturais nestes arquivos — tais como strings desalinhadas, registros nulos e formatos temporais heterogêneos — geravam falhas de quebra de esquema e travamentos nos relatórios automatizados de Business Intelligence (BI).

O script desenvolvido resolve esse problema por meio de técnicas estruturadas de:
1. **Validação de Tipagem e Nulos**: Preenchimento condicional de categorias ausentes ("sem categoria") e tratamento de dimensões físicas baseado em regras de integridade transacional (imputação de "0.0").
2. **Normalização de Textos via Regex**: Padronização de strings para minúsculas, remoção de espaçamentos parasitas (.strip()) e expurgo de caracteres de pontuação indevidos através do módulo `re`.
3. **Validação Logística de Hipótese**: Cruzamento de condicionais para validar se toda data de entrega ausente refere-se de fato a um fluxo interrompido (pedido cancelado).
4. **Formatação Temporal**: Conversão e readequação de strings cronológicas brutas para o padrão regional brasileiro (`DD/MM/YYYY`) usando manipulação baseada em objetos `datetime`.

---

## 🚀 Guia de Execução no Google Colab

Siga as instruções abaixo para executar o pipeline:

1. No menu lateral esquerdo do Google Colab, clique no ícone de **Pasta** (Arquivos).
2. Clique no ícone de **Upload** e selecione os arquivos `olist_products_dataset.csv` e `olist_orders_dataset.csv`.
3. Certifique-se de que os nomes estão exatamente iguais aos descritos acima.
4. Execute a célula de código do pipeline.
5. Após o processamento, o sumário estatístico manual será impresso em tela, e os arquivos limpos (`sanitized_products_dataset.csv` e `sanitized_orders_dataset.csv`) estarão disponíveis na aba lateral para download.

---

## 🧠 Reflexão Teórica: Qualidade de Dados vs. Inteligência Artificial (ML)

A aplicação rigorosa de pipelines de programação voltados à higienização e conformidade dos dados é o pilar estrutural que viabiliza o desenvolvimento de modelos preditivos eficientes em Machine Learning. Quando uma base de dados como a da Olist apresenta inconsistências, valores nulos aleatórios ou ruídos em strings de categorias, a inserção direta dessas variáveis brutas em algoritmos estatísticos induz o modelo a aprender padrões irrelevantes ou fictícios. Esse fenômeno compromete diretamente a capacidade de generalização da Inteligência Artificial, gerando modelos suscetíveis ao *Overfitting* (sobreajuste), nos quais o algoritmo performa de forma excelente nos dados de teste históricos, mas falha gravemente ao lidar com novos registros transacionais do mundo real.

Adicionalmente, a ausência de tratamento estruturado e consciente sobre dados nulos insere um forte viés cognitivo nos modelos preditivos. Se os registros vazios nas dimensões físicas de um produto fossem sumariamente descartados do pipeline, por exemplo, o modelo preditivo de custos logísticos ou de propensão de compras seria treinado com uma amostra reduzida e artificialmente selecionada do ecossistema de vendas da plataforma, negligenciando falhas sistêmicas e perfis comportamentais importantes. Desse modo, o tratamento determinístico inicial, apoiado em Expressões Regulares e tipagem coerente, assegura que a entrada de dados nas redes neurais ou árvores de decisão seja limpa, equilibrada e semanticamente íntegra, reduzindo drasticamente os vieses e blindando o sistema contra a propagação de erros em escala.
