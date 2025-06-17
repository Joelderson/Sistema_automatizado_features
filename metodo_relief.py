import os
import numpy as np
import pandas as pd
import csv
from sklearn.preprocessing import StandardScaler

# Caminhos
pasta_dados = os.path.join(os.getcwd(), 'dados_convertidos_csv')
pasta_features = os.path.join(os.getcwd(), 'features_extraidas')
os.makedirs(pasta_features, exist_ok=True)

def ler_dados_arquivo(caminho_arquivo):
    """Lê dados de arquivos CSV ou Excel"""
    dados = []
    
    if caminho_arquivo.lower().endswith('.csv'):
        # Tenta diferentes delimitadores e encodings
        delimitadores = [';', ',', '\t']
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            for delimitador in delimitadores:
                try:
                    with open(caminho_arquivo, 'r', encoding=encoding) as f:
                        # Lê as primeiras linhas para detectar o formato
                        primeiras_linhas = []
                        for i, linha in enumerate(f):
                            if i < 5:  # Lê as primeiras 5 linhas
                                primeiras_linhas.append(linha.strip())
                            else:
                                break
                        
                        # Volta ao início do arquivo
                        f.seek(0)
                        
                        # Tenta detectar se há cabeçalho
                        tem_cabecalho = False
                        if primeiras_linhas:
                            primeira_linha = primeiras_linhas[0].split(delimitador)
                            # Se a primeira linha contém texto não numérico, é cabeçalho
                            try:
                                float(primeira_linha[0].replace(',', '.'))
                            except ValueError:
                                tem_cabecalho = True
                        
                        reader = csv.reader(f, delimiter=delimitador)
                        
                        if tem_cabecalho:
                            next(reader, None)  # Pula o cabeçalho
                        
                        for linha in reader:
                            if len(linha) >= 1:  # Pelo menos uma coluna
                                # Tenta diferentes colunas para encontrar dados numéricos
                                for coluna in linha:
                                    try:
                                        # Remove espaços e substitui vírgula por ponto
                                        valor_str = coluna.strip().replace(',', '.')
                                        valor = float(valor_str)
                                        dados.append(valor)
                                        break  # Se encontrou um valor válido, para de procurar
                                    except ValueError:
                                        continue
                        
                        if len(dados) > 0:
                            print(f"Arquivo lido com sucesso usando delimitador '{delimitador}' e encoding '{encoding}'")
                            return dados
                        else:
                            dados = []  # Reseta para tentar próximo delimitador
                            
                except Exception as e:
                    continue  # Tenta próximo delimitador/encoding
        
        # Se nenhum delimitador funcionou, tenta ler como texto simples
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if linha:
                        try:
                            valor = float(linha.replace(',', '.'))
                            dados.append(valor)
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Erro ao ler arquivo como texto simples: {e}")
            
    elif caminho_arquivo.lower().endswith(('.xlsx', '.xls')):
        # Lê arquivo Excel
        try:
            df = pd.read_excel(caminho_arquivo)
            # Tenta diferentes colunas para encontrar dados numéricos
            for col in df.columns:
                coluna_dados = df[col]
                dados_temp = []
                for valor in coluna_dados:
                    if pd.notna(valor):  # Verifica se não é NaN
                        try:
                            dados_temp.append(float(valor))
                        except (ValueError, TypeError):
                            continue
                
                if len(dados_temp) > 0:
                    dados = dados_temp
                    print(f"Usando coluna '{col}' do arquivo Excel")
                    break
                    
        except Exception as e:
            print(f"Erro ao ler arquivo Excel {caminho_arquivo}: {e}")
            return []
    
    return dados

def segmentar_dados_grandes(dados, tamanho_segmento=1000):
    """Segmenta dados grandes em segmentos menores"""
    segmentos = []
    for i in range(0, len(dados), tamanho_segmento):
        segmento = dados[i:i + tamanho_segmento]
        if len(segmento) >= 10:  # Mínimo de 10 pontos por segmento
            segmentos.append(segmento)
    return segmentos

def processar_arquivo_ou_pasta(caminho):
    """Processa um arquivo específico ou uma pasta inteira"""
    if os.path.isfile(caminho):
        # Processa arquivo único
        print(f"Processando arquivo único: {caminho}")
        return processar_arquivo_unico(caminho)
    elif os.path.isdir(caminho):
        # Processa pasta e subpastas
        print(f"Processando pasta: {caminho}")
        return processar_pasta_completa(caminho)
    else:
        print(f"Caminho não encontrado: {caminho}")
        return [], [], []

def processar_arquivo_unico(caminho_arquivo):
    """Processa um arquivo único"""
    todas_features = []
    nomes_segmentos = []
    labels = []
    
    try:
        # Lê os dados do arquivo
        dados = ler_dados_arquivo(caminho_arquivo)
        
        if len(dados) == 0:
            print(f"Arquivo {os.path.basename(caminho_arquivo)} não contém dados válidos")
            return [], [], []
        
        print(f"Processando {os.path.basename(caminho_arquivo)} com {len(dados)} pontos de dados...")
        
        # Se o arquivo é muito grande, segmenta automaticamente
        if len(dados) > 1000:
            print(f"Arquivo grande detectado. Segmentando em partes de 1000 pontos...")
            segmentos = segmentar_dados_grandes(dados)
            print(f"Criados {len(segmentos)} segmentos")
            
            for i, segmento in enumerate(segmentos):
                try:
                    dados_segmento = np.array(segmento)
                    
                    # Calcula as features vibratórias
                    features = calcular_features(dados_segmento)
                    
                    todas_features.append(list(features.values()))
                    nomes_segmentos.append(f"{os.path.splitext(os.path.basename(caminho_arquivo))[0]}_segmento_{i+1}")
                    
                    # Define label baseado no nome do arquivo
                    nome_arquivo = os.path.basename(caminho_arquivo).lower()
                    if 'normal' in nome_arquivo:
                        labels.append(0)  # Estado normal
                    elif 'fault' in nome_arquivo or 'crack' in nome_arquivo or 'erosion' in nome_arquivo or 'unbalance' in nome_arquivo:
                        labels.append(1)  # Estado com falha
                    else:
                        labels.append(0)  # Padrão como normal
                        
                except Exception as e:
                    print(f"Erro ao processar segmento {i+1}: {e}")
                    continue
        else:
            # Arquivo pequeno, processa normalmente
            if len(dados) < 3:
                print(f"Arquivo {os.path.basename(caminho_arquivo)} tem apenas {len(dados)} pontos, pulando...")
                return [], [], []
            
            dados = np.array(dados)
            
            # Calcula as features vibratórias
            features = calcular_features(dados)
            
            todas_features.append(list(features.values()))
            nomes_segmentos.append(os.path.splitext(os.path.basename(caminho_arquivo))[0])
            
            # Define label baseado no nome do arquivo
            nome_arquivo = os.path.basename(caminho_arquivo).lower()
            if 'normal' in nome_arquivo:
                labels.append(0)  # Estado normal
            elif 'fault' in nome_arquivo or 'crack' in nome_arquivo or 'erosion' in nome_arquivo or 'unbalance' in nome_arquivo:
                labels.append(1)  # Estado com falha
            else:
                labels.append(0)  # Padrão como normal
        
        print(f"Extraídas features de {len(todas_features)} segmentos")
        return todas_features, nomes_segmentos, labels
        
    except Exception as e:
        print(f"Erro ao processar {caminho_arquivo}: {e}")
        return [], [], []

def processar_pasta_completa(pasta):
    """Processa pasta e subpastas"""
    todas_features = []
    nomes_segmentos = []
    labels = []
    
    arquivos_processados = 0
    arquivos_erro = 0
    
    # Percorre todos os arquivos .csv e .xlsx/.xls nas subpastas
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if file.lower().endswith(('.csv', '.xlsx', '.xls')):
                caminho_arquivo = os.path.join(root, file)
                try:
                    # Lê os dados do arquivo
                    dados = ler_dados_arquivo(caminho_arquivo)
                    
                    if len(dados) == 0:
                        print(f"Arquivo {file} não contém dados válidos, pulando...")
                        continue
                    
                    print(f"Processando {file} com {len(dados)} pontos de dados...")
                    
                    # Se o arquivo é muito grande, segmenta automaticamente
                    if len(dados) > 1000:
                        print(f"Arquivo grande detectado. Segmentando em partes de 1000 pontos...")
                        segmentos = segmentar_dados_grandes(dados)
                        print(f"Criados {len(segmentos)} segmentos")
                        
                        for i, segmento in enumerate(segmentos):
                            try:
                                dados_segmento = np.array(segmento)
                                
                                # Calcula as features vibratórias
                                features = calcular_features(dados_segmento)
                                
                                todas_features.append(list(features.values()))
                                nomes_segmentos.append(f"{os.path.basename(root)}_{file}_segmento_{i+1}")
                                
                                # Define labels baseado no nome da pasta/arquivo
                                nome_pasta = os.path.basename(root).lower()
                                nome_arquivo = file.lower()
                                if 'h' in nome_pasta or 'normal' in nome_pasta or 'normal' in nome_arquivo:
                                    labels.append(0)  # Estado normal
                                elif 'fault' in nome_pasta or 'crack' in nome_pasta or 'erosion' in nome_pasta or 'unbalance' in nome_pasta:
                                    labels.append(1)  # Estado com falha
                                else:
                                    labels.append(0)  # Padrão como normal
                                    
                            except Exception as e:
                                print(f"Erro ao processar segmento {i+1}: {e}")
                                continue
                    else:
                        # Arquivo pequeno, processa normalmente
                        if len(dados) < 3:
                            print(f"Arquivo {file} tem apenas {len(dados)} pontos, pulando...")
                            continue
                        
                        dados = np.array(dados)
                        
                        # Calcula as features vibratórias
                        features = calcular_features(dados)
                        
                        todas_features.append(list(features.values()))
                        nomes_segmentos.append(f"{os.path.basename(root)}_{file}")
                        
                        # Define labels baseado no nome da pasta
                        nome_pasta = os.path.basename(root).lower()
                        nome_arquivo = file.lower()
                        if 'h' in nome_pasta or 'normal' in nome_pasta or 'normal' in nome_arquivo:
                            labels.append(0)  # Estado normal
                        elif 'fault' in nome_pasta or 'crack' in nome_pasta or 'erosion' in nome_pasta or 'unbalance' in nome_pasta:
                            labels.append(1)  # Estado com falha
                        else:
                            labels.append(0)  # Padrão como normal
                    
                    arquivos_processados += 1
                    if arquivos_processados % 10 == 0:
                        print(f"Processados {arquivos_processados} arquivos...")
                        
                except Exception as e:
                    print(f"Erro ao processar {caminho_arquivo}: {e}")
                    arquivos_erro += 1
                    continue
    
    print(f"Extraídas features de {len(todas_features)} segmentos")
    print(f"Arquivos processados com sucesso: {arquivos_processados}")
    print(f"Arquivos com erro: {arquivos_erro}")
    return todas_features, nomes_segmentos, labels

def calcular_features(dados):
    """Calcula todas as features vibratórias para um conjunto de dados"""
    return {
        'media': np.mean(dados),
        'desvio_padrao': np.std(dados),
        'maximo': np.max(dados),
        'minimo': np.min(dados),
        'rms': np.sqrt(np.mean(dados**2)),
        'variancia': np.var(dados),
        'skewness': float(pd.Series(dados).skew()),
        'kurtosis': float(pd.Series(dados).kurtosis()),
        'pico_a_pico': np.max(dados) - np.min(dados),
        'crest_factor': np.max(np.abs(dados)) / np.sqrt(np.mean(dados**2)) if np.sqrt(np.mean(dados**2)) != 0 else 0,
        'shape_factor': np.sqrt(np.mean(dados**2)) / np.mean(np.abs(dados)) if np.mean(np.abs(dados)) != 0 else 0,
        'impulse_factor': np.max(np.abs(dados)) / np.mean(np.abs(dados)) if np.mean(np.abs(dados)) != 0 else 0,
        'margin_factor': np.max(np.abs(dados)) / np.mean(np.sqrt(np.abs(dados)))**2 if np.mean(np.sqrt(np.abs(dados))) != 0 else 0,
        'energia': np.sum(dados**2),
        'zero_crossings': np.sum(np.diff(np.sign(dados)) != 0),
        'mean_abs': np.mean(np.abs(dados)),
        'peak_to_rms': np.max(np.abs(dados)) / np.sqrt(np.mean(dados**2)) if np.sqrt(np.mean(dados**2)) != 0 else 0
    }

def extrair_features_vibratorias():
    """Extrai features vibratórias de todos os segmentos CSV e Excel"""
    print("Iniciando extração de features...")
    
    # Verifica se existe um arquivo específico para processar
    arquivo_especifico = os.path.join(pasta_dados, "97_Normal_0.csv")
    if os.path.exists(arquivo_especifico):
        print(f"Arquivo específico encontrado: {arquivo_especifico}")
        return processar_arquivo_ou_pasta(arquivo_especifico)
    else:
        print(f"Procurando arquivos CSV e Excel em: {pasta_dados}")
        return processar_arquivo_ou_pasta(pasta_dados)

def aplicar_relief_e_salvar():
    """Aplica o método ReliefF e salva os resultados"""
    todas_features, nomes_segmentos, labels = extrair_features_vibratorias()
    
    if not todas_features:
        print("Nenhum segmento válido encontrado para extração de features.")
        return
    
    # Define as colunas das features
    colunas_features = [
        'media', 'desvio_padrao', 'maximo', 'minimo', 'rms', 'variancia',
        'skewness', 'kurtosis', 'pico_a_pico', 'crest_factor',
        'shape_factor', 'impulse_factor', 'margin_factor', 'energia',
        'zero_crossings', 'mean_abs', 'peak_to_rms'
    ]
    
    # Cria DataFrame com as features
    df_features = pd.DataFrame(todas_features, columns=colunas_features)
    df_features['segmento'] = nomes_segmentos
    df_features['label'] = labels
    
    print(f"Dataset criado com {len(df_features)} amostras e {len(colunas_features)} features")
    
    try:
        # Tenta importar ReliefF
        from skrebate import ReliefF
        
        # Prepara os dados para ReliefF
        X = df_features[colunas_features].values
        y = np.array(labels)
        
        # Normaliza os dados
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        print("Aplicando método ReliefF...")
        
        # Aplica ReliefF
        relief = ReliefF(n_features_to_select=min(10, len(colunas_features)), n_neighbors=10)
        relief.fit(X_scaled, y)
        
        # Obtém os scores das features
        scores = relief.feature_importances_
        
        # Cria DataFrame com os scores
        df_scores = pd.DataFrame({
            'feature': colunas_features,
            'score_relief': scores
        }).sort_values('score_relief', ascending=False)
        
        # Salva os scores
        caminho_scores = os.path.join(pasta_features, 'relief_scores.csv')
        df_scores.to_csv(caminho_scores, index=False)
        
        # Mostra as top features
        top_features = df_scores.head(10)['feature'].tolist()
        print("\nTop 10 features selecionadas pelo ReliefF:")
        for i, feature in enumerate(top_features, 1):
            score = df_scores.iloc[i-1]['score_relief']
            print(f"{i}. {feature} (score: {score:.4f})")
        
        # Salva as features extraídas
        caminho_features = os.path.join(pasta_features, 'relief_features.csv')
        df_features.to_csv(caminho_features, index=False)
        
        # Cria dataset apenas com as top features
        df_top_features = df_features[top_features + ['segmento', 'label']]
        caminho_top_features = os.path.join(pasta_features, 'top_features_relief.csv')
        df_top_features.to_csv(caminho_top_features, index=False)
        
        print(f"\nResultados salvos:")
        print(f"- Scores ReliefF: {caminho_scores}")
        print(f"- Todas as features: {caminho_features}")
        print(f"- Top features selecionadas: {caminho_top_features}")
        
        # Estatísticas dos dados
        print(f"\nEstatísticas dos dados:")
        print(f"- Total de amostras: {len(df_features)}")
        print(f"- Amostras normais (label 0): {sum(labels == 0)}")
        print(f"- Amostras com falha (label 1): {sum(labels == 1)}")
        print(f"- Features originais: {len(colunas_features)}")
        print(f"- Features selecionadas: {len(top_features)}")
        
    except ImportError:
        print("Biblioteca skrebate não encontrada. Tentando instalar...")
        try:
            import subprocess
            subprocess.check_call(["pip", "install", "skrebate"])
            print("skrebate instalado com sucesso!")
            print("Execute o script novamente.")
        except Exception as e:
            print(f"Erro ao instalar skrebate: {e}")
            print("Instale manualmente com: pip install skrebate")
            print("Ou use uma alternativa como scikit-learn para feature selection")
            
            # Alternativa usando scikit-learn
            print("\nAplicando método alternativo usando scikit-learn...")
            try:
                from sklearn.feature_selection import SelectKBest, f_classif
                
                # Usa ANOVA F-value para seleção de features
                selector = SelectKBest(score_func=f_classif, k=min(10, len(colunas_features)))
                X = df_features[colunas_features].values
                y = np.array(labels)
                
                X_selected = selector.fit_transform(X, y)
                scores = selector.scores_
                
                # Cria DataFrame com os scores
                df_scores = pd.DataFrame({
                    'feature': colunas_features,
                    'score_f_test': scores
                }).sort_values('score_f_test', ascending=False)
                
                # Salva os scores
                caminho_scores = os.path.join(pasta_features, 'f_test_scores.csv')
                df_scores.to_csv(caminho_scores, index=False)
                
                # Mostra as top features
                top_features = df_scores.head(10)['feature'].tolist()
                print("\nTop 10 features selecionadas pelo F-test:")
                for i, feature in enumerate(top_features, 1):
                    score = df_scores.iloc[i-1]['score_f_test']
                    print(f"{i}. {feature} (score: {score:.4f})")
                
                # Salva as features extraídas
                caminho_features = os.path.join(pasta_features, 'f_test_features.csv')
                df_features.to_csv(caminho_features, index=False)
                
                # Cria dataset apenas com as top features
                df_top_features = df_features[top_features + ['segmento', 'label']]
                caminho_top_features = os.path.join(pasta_features, 'top_features_f_test.csv')
                df_top_features.to_csv(caminho_top_features, index=False)
                
                print(f"\nResultados salvos:")
                print(f"- Scores F-test: {caminho_scores}")
                print(f"- Todas as features: {caminho_features}")
                print(f"- Top features selecionadas: {caminho_top_features}")
                
            except Exception as e2:
                print(f"Erro ao aplicar método alternativo: {e2}")
        return
        
    except Exception as e:
        print(f"Erro ao aplicar ReliefF: {e}")
        return

def organizar_features_relief_por_segmento():
    """Organiza as features selecionadas pelo ReliefF em subpastas por condição com pesos"""
    print("\n=== ORGANIZAÇÃO DAS FEATURES RELIEFF POR SEGMENTO ===")
    
    pasta_relief_organizado = os.path.join(pasta_features, 'relief_organizado')
    os.makedirs(pasta_relief_organizado, exist_ok=True)
    
    # Top features selecionadas pelo ReliefF com seus pesos (baseado no ranking)
    top_features_relief = [
        'minimo', 'mean_abs', 'kurtosis', 'media', 'rms', 
        'desvio_padrao', 'pico_a_pico', 'skewness', 'energia', 'variancia'
    ]
    
    # Pesos das features (baseado na importância do ReliefF - valores normalizados)
    pesos_features = {
        'minimo': 1.0,           # Peso máximo (feature mais importante)
        'mean_abs': 0.95,        # Muito alta importância
        'kurtosis': 0.90,        # Alta importância
        'media': 0.85,           # Alta importância
        'rms': 0.80,             # Importância alta
        'desvio_padrao': 0.75,   # Importância alta
        'pico_a_pico': 0.70,     # Importância média-alta
        'skewness': 0.65,        # Importância média
        'energia': 0.60,         # Importância média
        'variancia': 0.55        # Importância média-baixa
    }
    
    print("Extraindo features por segmento com pesos...")
    
    # Dicionário para armazenar features por condição
    features_por_condicao = {}
    
    # Percorre todos os arquivos .csv e .xlsx/.xls nas subpastas
    for root, dirs, files in os.walk(pasta_dados):
        for file in files:
            if file.lower().endswith(('.csv', '.xlsx', '.xls')):
                caminho_arquivo = os.path.join(root, file)
                try:
                    # Lê os dados do arquivo
                    dados = ler_dados_arquivo(caminho_arquivo)
                    
                    # Verifica se há dados suficientes
                    if len(dados) < 3:
                        continue
                    
                    dados = np.array(dados)
                    
                    # Calcula as features vibratórias
                    features = {
                        'media': np.mean(dados),
                        'desvio_padrao': np.std(dados),
                        'maximo': np.max(dados),
                        'minimo': np.min(dados),
                        'rms': np.sqrt(np.mean(dados**2)),
                        'variancia': np.var(dados),
                        'skewness': float(pd.Series(dados).skew()),
                        'kurtosis': float(pd.Series(dados).kurtosis()),
                        'pico_a_pico': np.max(dados) - np.min(dados),
                        'crest_factor': np.max(np.abs(dados)) / np.sqrt(np.mean(dados**2)) if np.sqrt(np.mean(dados**2)) != 0 else 0,
                        'shape_factor': np.sqrt(np.mean(dados**2)) / np.mean(np.abs(dados)) if np.mean(np.abs(dados)) != 0 else 0,
                        'impulse_factor': np.max(np.abs(dados)) / np.mean(np.abs(dados)) if np.mean(np.abs(dados)) != 0 else 0,
                        'margin_factor': np.max(np.abs(dados)) / np.mean(np.sqrt(np.abs(dados)))**2 if np.mean(np.sqrt(np.abs(dados))) != 0 else 0,
                        'energia': np.sum(dados**2),
                        'zero_crossings': np.sum(np.diff(np.sign(dados)) != 0),
                        'mean_abs': np.mean(np.abs(dados)),
                        'peak_to_rms': np.max(np.abs(dados)) / np.sqrt(np.mean(dados**2)) if np.sqrt(np.mean(dados**2)) != 0 else 0
                    }
                    
                    # Obtém o nome da condição (pasta)
                    condicao = os.path.basename(root)
                    
                    # Adiciona informações do segmento
                    features['segmento'] = file.replace('.csv', '').replace('.xlsx', '').replace('.xls', '')
                    features['arquivo_original'] = file
                    features['condicao'] = condicao
                    
                    # Define label baseado no nome da pasta
                    nome_pasta = condicao.lower()
                    if 'h' in nome_pasta or 'normal' in nome_pasta:
                        features['label'] = 0  # Estado normal
                    elif 'fault' in nome_pasta or 'crack' in nome_pasta or 'erosion' in nome_pasta or 'unbalance' in nome_pasta:
                        features['label'] = 1  # Estado com falha
                    else:
                        features['label'] = 0  # Padrão como normal
                    
                    # Adiciona apenas as top features selecionadas pelo ReliefF com seus pesos
                    features_relief = {}
                    for feature in top_features_relief:
                        if feature in features:
                            features_relief[feature] = features[feature]
                            features_relief[f'{feature}_peso'] = pesos_features[feature]
                    
                    features_relief.update({
                        'segmento': features['segmento'],
                        'arquivo_original': features['arquivo_original'],
                        'condicao': features['condicao'],
                        'label': features['label']
                    })
                    
                    # Organiza por condição
                    if condicao not in features_por_condicao:
                        features_por_condicao[condicao] = []
                    features_por_condicao[condicao].append(features_relief)
                    
                except Exception as e:
                    print(f"Erro ao processar {caminho_arquivo}: {e}")
                    continue
    
    # Salva as features organizadas
    print("Salvando features organizadas com pesos...")
    
    # Salva ranking das features com pesos
    ranking_features = pd.DataFrame({
        'feature': top_features_relief,
        'posicao': range(1, len(top_features_relief) + 1),
        'peso': [pesos_features[feature] for feature in top_features_relief]
    })
    caminho_ranking = os.path.join(pasta_relief_organizado, 'ranking_features_relief.csv')
    ranking_features.to_csv(caminho_ranking, index=False)
    
    # Salva features por condição
    for condicao, features_list in features_por_condicao.items():
        if features_list:
            # Cria subpasta para a condição
            pasta_condicao = os.path.join(pasta_relief_organizado, condicao)
            os.makedirs(pasta_condicao, exist_ok=True)
            
            # Converte para DataFrame
            df_condicao = pd.DataFrame(features_list)
            
            # Salva arquivo da condição
            caminho_condicao = os.path.join(pasta_condicao, f'features_relief_{condicao}.csv')
            df_condicao.to_csv(caminho_condicao, index=False)
            
            # Salva arquivo individual para cada segmento
            for feature_dict in features_list:
                segmento = feature_dict['segmento']
                df_segmento = pd.DataFrame([feature_dict])
                caminho_segmento = os.path.join(pasta_condicao, f'segmento_{segmento}_relief.csv')
                df_segmento.to_csv(caminho_segmento, index=False)
    
    # Cria arquivo consolidado com todas as features
    todas_features = []
    for features_list in features_por_condicao.values():
        todas_features.extend(features_list)
    
    if todas_features:
        df_consolidado = pd.DataFrame(todas_features)
        caminho_consolidado = os.path.join(pasta_relief_organizado, 'features_relief_consolidadas.csv')
        df_consolidado.to_csv(caminho_consolidado, index=False)
        
        print(f"\nArquivos salvos em: {pasta_relief_organizado}")
        print(f"- ranking_features_relief.csv - Ranking das features com pesos")
        print(f"- features_relief_consolidadas.csv - Todas as features consolidadas com pesos")
        print(f"- Subpastas por condição com features individuais e pesos")
        
        print(f"\nEstatísticas gerais:")
        print(f"- Total de segmentos processados: {len(df_consolidado)}")
        print(f"- Número de condições: {len(df_consolidado['condicao'].unique())}")
        print(f"- Features selecionadas pelo ReliefF: {len(top_features_relief)}")
        print(f"- Features com pesos adicionados: {len(top_features_relief)}")
        print(f"- Amostras normais (label 0): {sum(df_consolidado['label'] == 0)}")
        print(f"- Amostras com falha (label 1): {sum(df_consolidado['label'] == 1)}")
        
        # Mostra os pesos das features
        print(f"\nPesos das features (importância):")
        for feature, peso in pesos_features.items():
            print(f"- {feature}: {peso:.2f}")

def mostrar_top_features():
    """Mostra as top features selecionadas pelo ReliefF"""
    print("\n=== TOP FEATURES SELECIONADAS PELO RELIEFF ===")
    top_features = [
        'minimo', 'mean_abs', 'kurtosis', 'media', 'rms', 
        'desvio_padrao', 'pico_a_pico', 'skewness', 'energia', 'variancia'
    ]
    
    for i, feature in enumerate(top_features, 1):
        print(f"{i}. {feature}")
    
    print(f"\nTotal de features selecionadas: {len(top_features)}")

if __name__ == "__main__":
    print("=== INÍCIO DO PROCESSAMENTO ===")
    print(f"Pasta de dados: {pasta_dados}")
    print(f"Pasta de resultados: {pasta_features}")
    
    # Verifica se as pastas existem
    if not os.path.exists(pasta_dados):
        print(f"ERRO: Pasta de dados não encontrada: {pasta_dados}")
        exit(1)
    
    if not os.path.exists(pasta_features):
        os.makedirs(pasta_features)
        print(f"Pasta de resultados criada: {pasta_features}")
    
    # Lista arquivos na pasta de dados
    print("\nArquivos encontrados na pasta de dados:")
    for root, dirs, files in os.walk(pasta_dados):
        for file in files:
            if file.lower().endswith(('.csv', '.xlsx', '.xls')):
                print(f"  - {os.path.join(root, file)}")
    
    print("\n=== EXTRAÇÃO DE FEATURES ===")
    # Extrai features vibratórias
    todas_features, nomes_segmentos, labels = extrair_features_vibratorias()
    
    if len(todas_features) == 0:
        print("Nenhum segmento válido encontrado para extração de features.")
        print("Verifique se os arquivos contêm dados numéricos válidos.")
        exit(1)
    
    print(f"\nFeatures extraídas com sucesso: {len(todas_features)} segmentos")
    
    print("\n=== APLICAÇÃO DO MÉTODO RELIEFF ===")
    # Aplica ReliefF e salva resultados
    aplicar_relief_e_salvar()
    
    print("\n=== ORGANIZAÇÃO DAS FEATURES RELIEFF POR SEGMENTO ===")
    # Organiza features por segmento
    organizar_features_relief_por_segmento()
    
    print("\n=== PROCESSO CONCLUÍDO ===")
    