import os

pasta_origem = os.path.join(os.getcwd(), 'resultados_segmentos')
pasta_destino = os.path.join(os.getcwd(), 'dados_convertidos_csv')
os.makedirs(pasta_destino, exist_ok=True)

for root, dirs, files in os.walk(pasta_origem):
    for file in files:
        if file.lower().endswith('.txt'):
            caminho_arquivo = os.path.join(root, file)
            rel_path = os.path.relpath(root, pasta_origem)
            pasta_saida = os.path.join(pasta_destino, rel_path)
            os.makedirs(pasta_saida, exist_ok=True)
            nome_csv = os.path.splitext(file)[0] + '.csv'
            caminho_saida = os.path.join(pasta_saida, nome_csv)
            # Copiar conteúdo do txt para csv
            with open(caminho_arquivo, 'r', encoding='utf-8') as f_in, open(caminho_saida, 'w', encoding='utf-8') as f_out:
                for linha in f_in:
                    f_out.write(linha)
print(f'Conversão concluída. Arquivos CSV salvos em: {pasta_destino}')
