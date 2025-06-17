import os
import numpy as np
import pandas as pd
import csv

# Caminhos
pasta_dados = os.path.join(os.getcwd(), 'dados_convertidos_csv')
pasta_features = os.path.join(os.getcwd(), 'features_extraidas')
pasta_segmentos = os.path.join(pasta_features, 'features_por_segmento')
os.makedirs(pasta_features, exist_ok=True)
os.makedirs(pasta_segmentos, exist_ok=True)

def ler_dados_arquivo(caminho_arquivo):
    """Lê dados de arquivos CSV"""
    dados = []
    
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
        
    return dados

def calcular_features_completas(dados):
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
        'peak_to_rms': np.max(np.abs(dados)) / np.sqrt(np.mean(dados**2)) if np.sqrt(np.mean(dados**2)) != 0 else 0,
        'mediana': np.median(dados),
        'amplitude': np.max(dados) - np.min(dados),
        'coeficiente_variacao': np.std(dados) / np.mean(dados) if np.mean(dados) != 0 else 0,
        'range': np.max(dados) - np.min(dados),
        'percentil_25': np.percentile(dados, 25),
        'percentil_75': np.percentile(dados, 75),
        'iqr': np.percentile(dados, 75) - np.percentile(dados, 25),
        'entropia': -np.sum(np.histogram(dados, bins=min(20, len(dados)//2))[0]/len(dados) * np.log2(np.histogram(dados, bins=min(20, len(dados)//2))[0]/len(dados) + 1e-10)),
        'autocorrelacao_lag1': np.corrcoef(dados[:-1], dados[1:])[0,1] if len(dados) > 1 else 0,
        'autocorrelacao_lag2': np.corrcoef(dados[:-2], dados[2:])[0,1] if len(dados) > 2 else 0,
        'autocorrelacao_lag3': np.corrcoef(dados[:-3], dados[3:])[0,1] if len(dados) > 3 else 0,
        'autocorrelacao_lag5': np.corrcoef(dados[:-5], dados[5:])[0,1] if len(dados) > 5 else 0,
        'autocorrelacao_lag10': np.corrcoef(dados[:-10], dados[10:])[0,1] if len(dados) > 10 else 0,
        'fft_media': np.mean(np.abs(np.fft.fft(dados))),
        'fft_max': np.max(np.abs(np.fft.fft(dados))),
        'fft_std': np.std(np.abs(np.fft.fft(dados))),
        'fft_energia': np.sum(np.abs(np.fft.fft(dados))**2),
        'fft_centroide': np.sum(np.arange(len(dados)) * np.abs(np.fft.fft(dados))) / np.sum(np.abs(np.fft.fft(dados))) if np.sum(np.abs(np.fft.fft(dados))) != 0 else 0,
        'fft_bandwidth': np.sqrt(np.sum((np.arange(len(dados)) - np.sum(np.arange(len(dados)) * np.abs(np.fft.fft(dados))) / np.sum(np.abs(np.fft.fft(dados))))**2 * np.abs(np.fft.fft(dados))) / np.sum(np.abs(np.fft.fft(dados)))) if np.sum(np.abs(np.fft.fft(dados))) != 0 else 0,
        'fft_rolloff': np.percentile(np.cumsum(np.abs(np.fft.fft(dados))), 85),
        'fft_flux': np.sum(np.abs(np.diff(np.abs(np.fft.fft(dados))))) if len(dados) > 1 else 0,
        'fft_mfcc_1': np.mean(np.abs(np.fft.fft(dados))[:len(dados)//4]),
        'fft_mfcc_2': np.mean(np.abs(np.fft.fft(dados))[len(dados)//4:len(dados)//2]),
        'fft_mfcc_3': np.mean(np.abs(np.fft.fft(dados))[len(dados)//2:3*len(dados)//4]),
        'fft_mfcc_4': np.mean(np.abs(np.fft.fft(dados))[3*len(dados)//4:]),
        'wavelet_haar_1': np.mean(np.abs(np.diff(dados))),
        'wavelet_haar_2': np.std(np.abs(np.diff(dados))),
        'wavelet_haar_3': np.max(np.abs(np.diff(dados))),
        'wavelet_haar_4': np.min(np.abs(np.diff(dados))),
        'wavelet_haar_5': np.median(np.abs(np.diff(dados))),
        'estatisticas_ordem_1': np.mean(dados),
        'estatisticas_ordem_2': np.mean(dados**2),
        'estatisticas_ordem_3': np.mean(dados**3),
        'estatisticas_ordem_4': np.mean(dados**4),
        'momento_central_2': np.mean((dados - np.mean(dados))**2),
        'momento_central_3': np.mean((dados - np.mean(dados))**3),
        'momento_central_4': np.mean((dados - np.mean(dados))**4),
        'momento_central_5': np.mean((dados - np.mean(dados))**5),
        'momento_central_6': np.mean((dados - np.mean(dados))**6),
        'momento_central_7': np.mean((dados - np.mean(dados))**7),
        'momento_central_8': np.mean((dados - np.mean(dados))**8),
        'momento_central_9': np.mean((dados - np.mean(dados))**9),
        'momento_central_10': np.mean((dados - np.mean(dados))**10),
        'momento_absoluto_1': np.mean(np.abs(dados)),
        'momento_absoluto_2': np.mean(np.abs(dados)**2),
        'momento_absoluto_3': np.mean(np.abs(dados)**3),
        'momento_absoluto_4': np.mean(np.abs(dados)**4),
        'momento_absoluto_5': np.mean(np.abs(dados)**5),
        'momento_absoluto_6': np.mean(np.abs(dados)**6),
        'momento_absoluto_7': np.mean(np.abs(dados)**7),
        'momento_absoluto_8': np.mean(np.abs(dados)**8),
        'momento_absoluto_9': np.mean(np.abs(dados)**9),
        'momento_absoluto_10': np.mean(np.abs(dados)**10),
        'momento_central_absoluto_1': np.mean(np.abs(dados - np.mean(dados))),
        'momento_central_absoluto_2': np.mean(np.abs(dados - np.mean(dados))**2),
        'momento_central_absoluto_3': np.mean(np.abs(dados - np.mean(dados))**3),
        'momento_central_absoluto_4': np.mean(np.abs(dados - np.mean(dados))**4),
        'momento_central_absoluto_5': np.mean(np.abs(dados - np.mean(dados))**5),
        'momento_central_absoluto_6': np.mean(np.abs(dados - np.mean(dados))**6),
        'momento_central_absoluto_7': np.mean(np.abs(dados - np.mean(dados))**7),
        'momento_central_absoluto_8': np.mean(np.abs(dados - np.mean(dados))**8),
        'momento_central_absoluto_9': np.mean(np.abs(dados - np.mean(dados))**9),
        'momento_central_absoluto_10': np.mean(np.abs(dados - np.mean(dados))**10),
        'momento_central_absoluto_11': np.mean(np.abs(dados - np.mean(dados))**11),
        'momento_central_absoluto_12': np.mean(np.abs(dados - np.mean(dados))**12),
        'momento_central_absoluto_13': np.mean(np.abs(dados - np.mean(dados))**13),
        'momento_central_absoluto_14': np.mean(np.abs(dados - np.mean(dados))**14),
        'momento_central_absoluto_15': np.mean(np.abs(dados - np.mean(dados))**15),
        'momento_central_absoluto_16': np.mean(np.abs(dados - np.mean(dados))**16),
        'momento_central_absoluto_17': np.mean(np.abs(dados - np.mean(dados))**17),
        'momento_central_absoluto_18': np.mean(np.abs(dados - np.mean(dados))**18),
        'momento_central_absoluto_19': np.mean(np.abs(dados - np.mean(dados))**19),
        'momento_central_absoluto_20': np.mean(np.abs(dados - np.mean(dados))**20),
        'momento_central_absoluto_21': np.mean(np.abs(dados - np.mean(dados))**21),
        'momento_central_absoluto_22': np.mean(np.abs(dados - np.mean(dados))**22),
        'momento_central_absoluto_23': np.mean(np.abs(dados - np.mean(dados))**23),
        'momento_central_absoluto_24': np.mean(np.abs(dados - np.mean(dados))**24),
        'momento_central_absoluto_25': np.mean(np.abs(dados - np.mean(dados))**25),
        'momento_central_absoluto_26': np.mean(np.abs(dados - np.mean(dados))**26),
        'momento_central_absoluto_27': np.mean(np.abs(dados - np.mean(dados))**27),
        'momento_central_absoluto_28': np.mean(np.abs(dados - np.mean(dados))**28),
        'momento_central_absoluto_29': np.mean(np.abs(dados - np.mean(dados))**29),
        'momento_central_absoluto_30': np.mean(np.abs(dados - np.mean(dados))**30),
        'momento_central_absoluto_31': np.mean(np.abs(dados - np.mean(dados))**31),
        'momento_central_absoluto_32': np.mean(np.abs(dados - np.mean(dados))**32),
        'momento_central_absoluto_33': np.mean(np.abs(dados - np.mean(dados))**33),
        'momento_central_absoluto_34': np.mean(np.abs(dados - np.mean(dados))**34),
        'momento_central_absoluto_35': np.mean(np.abs(dados - np.mean(dados))**35),
        'momento_central_absoluto_36': np.mean(np.abs(dados - np.mean(dados))**36),
        'momento_central_absoluto_37': np.mean(np.abs(dados - np.mean(dados))**37),
        'momento_central_absoluto_38': np.mean(np.abs(dados - np.mean(dados))**38),
        'momento_central_absoluto_39': np.mean(np.abs(dados - np.mean(dados))**39),
        'momento_central_absoluto_40': np.mean(np.abs(dados - np.mean(dados))**40),
        'momento_central_absoluto_41': np.mean(np.abs(dados - np.mean(dados))**41),
        'momento_central_absoluto_42': np.mean(np.abs(dados - np.mean(dados))**42),
        'momento_central_absoluto_43': np.mean(np.abs(dados - np.mean(dados))**43),
        'momento_central_absoluto_44': np.mean(np.abs(dados - np.mean(dados))**44),
        'momento_central_absoluto_45': np.mean(np.abs(dados - np.mean(dados))**45),
        'momento_central_absoluto_46': np.mean(np.abs(dados - np.mean(dados))**46),
        'momento_central_absoluto_47': np.mean(np.abs(dados - np.mean(dados))**47),
        'momento_central_absoluto_48': np.mean(np.abs(dados - np.mean(dados))**48),
        'momento_central_absoluto_49': np.mean(np.abs(dados - np.mean(dados))**49),
        'momento_central_absoluto_50': np.mean(np.abs(dados - np.mean(dados))**50),
        'momento_central_absoluto_51': np.mean(np.abs(dados - np.mean(dados))**51),
        'momento_central_absoluto_52': np.mean(np.abs(dados - np.mean(dados))**52),
        'momento_central_absoluto_53': np.mean(np.abs(dados - np.mean(dados))**53),
        'momento_central_absoluto_54': np.mean(np.abs(dados - np.mean(dados))**54),
        'momento_central_absoluto_55': np.mean(np.abs(dados - np.mean(dados))**55),
        'momento_central_absoluto_56': np.mean(np.abs(dados - np.mean(dados))**56),
        'momento_central_absoluto_57': np.mean(np.abs(dados - np.mean(dados))**57),
        'momento_central_absoluto_58': np.mean(np.abs(dados - np.mean(dados))**58),
        'momento_central_absoluto_59': np.mean(np.abs(dados - np.mean(dados))**59),
        'momento_central_absoluto_60': np.mean(np.abs(dados - np.mean(dados))**60),
        'momento_central_absoluto_61': np.mean(np.abs(dados - np.mean(dados))**61),
        'momento_central_absoluto_62': np.mean(np.abs(dados - np.mean(dados))**62),
        'momento_central_absoluto_63': np.mean(np.abs(dados - np.mean(dados))**63),
        'momento_central_absoluto_64': np.mean(np.abs(dados - np.mean(dados))**64),
        'momento_central_absoluto_65': np.mean(np.abs(dados - np.mean(dados))**65),
        'momento_central_absoluto_66': np.mean(np.abs(dados - np.mean(dados))**66),
        'momento_central_absoluto_67': np.mean(np.abs(dados - np.mean(dados))**67),
        'momento_central_absoluto_68': np.mean(np.abs(dados - np.mean(dados))**68),
        'momento_central_absoluto_69': np.mean(np.abs(dados - np.mean(dados))**69),
        'momento_central_absoluto_70': np.mean(np.abs(dados - np.mean(dados))**70),
        'momento_central_absoluto_71': np.mean(np.abs(dados - np.mean(dados))**71),
        'momento_central_absoluto_72': np.mean(np.abs(dados - np.mean(dados))**72),
        'momento_central_absoluto_73': np.mean(np.abs(dados - np.mean(dados))**73),
        'momento_central_absoluto_74': np.mean(np.abs(dados - np.mean(dados))**74),
        'momento_central_absoluto_75': np.mean(np.abs(dados - np.mean(dados))**75),
        'momento_central_absoluto_76': np.mean(np.abs(dados - np.mean(dados))**76),
        'momento_central_absoluto_77': np.mean(np.abs(dados - np.mean(dados))**77),
        'momento_central_absoluto_78': np.mean(np.abs(dados - np.mean(dados))**78),
        'momento_central_absoluto_79': np.mean(np.abs(dados - np.mean(dados))**79),
        'momento_central_absoluto_80': np.mean(np.abs(dados - np.mean(dados))**80),
        'momento_central_absoluto_81': np.mean(np.abs(dados - np.mean(dados))**81),
        'momento_central_absoluto_82': np.mean(np.abs(dados - np.mean(dados))**82),
        'momento_central_absoluto_83': np.mean(np.abs(dados - np.mean(dados))**83),
        'momento_central_absoluto_84': np.mean(np.abs(dados - np.mean(dados))**84),
        'momento_central_absoluto_85': np.mean(np.abs(dados - np.mean(dados))**85),
        'momento_central_absoluto_86': np.mean(np.abs(dados - np.mean(dados))**86),
        'momento_central_absoluto_87': np.mean(np.abs(dados - np.mean(dados))**87),
        'momento_central_absoluto_88': np.mean(np.abs(dados - np.mean(dados))**88),
        'momento_central_absoluto_89': np.mean(np.abs(dados - np.mean(dados))**89),
        'momento_central_absoluto_90': np.mean(np.abs(dados - np.mean(dados))**90),
        'momento_central_absoluto_91': np.mean(np.abs(dados - np.mean(dados))**91),
        'momento_central_absoluto_92': np.mean(np.abs(dados - np.mean(dados))**92),
        'momento_central_absoluto_93': np.mean(np.abs(dados - np.mean(dados))**93),
        'momento_central_absoluto_94': np.mean(np.abs(dados - np.mean(dados))**94),
        'momento_central_absoluto_95': np.mean(np.abs(dados - np.mean(dados))**95),
        'momento_central_absoluto_96': np.mean(np.abs(dados - np.mean(dados))**96),
        'momento_central_absoluto_97': np.mean(np.abs(dados - np.mean(dados))**97),
        'momento_central_absoluto_98': np.mean(np.abs(dados - np.mean(dados))**98),
        'momento_central_absoluto_99': np.mean(np.abs(dados - np.mean(dados))**99),
        'momento_central_absoluto_100': np.mean(np.abs(dados - np.mean(dados))**100)
    }

# ============================================================================
# FUNÇÃO 1: EXTRAÇÃO CONSOLIDADA (features_sem_relief.py original)
# ============================================================================

def extrair_features_todos_segmentos():
    """Extrai todas as features de todos os segmentos CSV nas subpastas"""
    print("=== EXTRAÇÃO DE FEATURES COMPLETAS ===")
    print("Processando todos os segmentos CSV...")
    
    todas_features = []
    nomes_segmentos = []
    condicoes = []
    labels = []
    
    arquivos_processados = 0
    arquivos_erro = 0
    
    # Percorre todas as subpastas
    for root, dirs, files in os.walk(pasta_dados):
        for file in files:
            if file.lower().endswith('.csv'):
                caminho_arquivo = os.path.join(root, file)
                try:
                    # Lê os dados do arquivo
                    dados = ler_dados_arquivo(caminho_arquivo)
                    
                    if len(dados) == 0:
                        print(f"Arquivo {file} não contém dados válidos, pulando...")
                        continue
                    
                    if len(dados) < 3:
                        print(f"Arquivo {file} tem apenas {len(dados)} pontos, pulando...")
                        continue
                    
                    print(f"Processando {file} com {len(dados)} pontos de dados...")
                    
                    dados = np.array(dados)
                    
                    # Calcula todas as features
                    features = calcular_features_completas(dados)
                    
                    todas_features.append(list(features.values()))
                    nomes_segmentos.append(file.replace('.csv', ''))
                    
                    # Obtém a condição (nome da pasta)
                    condicao = os.path.basename(root)
                    condicoes.append(condicao)
                    
                    # Define label baseado no nome da pasta
                    nome_pasta = condicao.lower()
                    if 'h' in nome_pasta or 'normal' in nome_pasta:
                        labels.append(0)  # Estado normal
                    elif 'fault' in nome_pasta or 'crack' in nome_pasta or 'erosion' in nome_pasta or 'unbalance' in nome_pasta:
                        labels.append(1)  # Estado com falha
                    else:
                        labels.append(0)  # Padrão como normal
                    
                    arquivos_processados += 1
                    if arquivos_processados % 100 == 0:
                        print(f"Processados {arquivos_processados} arquivos...")
                        
                except Exception as e:
                    print(f"Erro ao processar {caminho_arquivo}: {e}")
                    arquivos_erro += 1
                    continue
    
    print(f"Extraídas features de {len(todas_features)} segmentos")
    print(f"Arquivos processados com sucesso: {arquivos_processados}")
    print(f"Arquivos com erro: {arquivos_erro}")
    
    return todas_features, nomes_segmentos, condicoes, labels

def salvar_features_completas():
    """Salva todas as features extraídas"""
    print("\n=== SALVANDO FEATURES COMPLETAS ===")
    
    todas_features, nomes_segmentos, condicoes, labels = extrair_features_todos_segmentos()
    
    if not todas_features:
        print("Nenhum segmento válido encontrado para extração de features.")
        return
    
    # Obtém os nomes das features
    features_exemplo = calcular_features_completas(np.array([1, 2, 3, 4, 5]))
    colunas_features = list(features_exemplo.keys())
    
    # Cria DataFrame com todas as features
    df_features = pd.DataFrame(todas_features, columns=colunas_features)
    df_features['segmento'] = nomes_segmentos
    df_features['condicao'] = condicoes
    df_features['label'] = labels
    
    print(f"Dataset criado com {len(df_features)} amostras e {len(colunas_features)} features")
    
    # Salva todas as features
    caminho_features = os.path.join(pasta_features, 'features_completas.csv')
    df_features.to_csv(caminho_features, index=False)
    
    # Salva estatísticas das features
    estatisticas_features = df_features[colunas_features].describe()
    caminho_estatisticas = os.path.join(pasta_features, 'estatisticas_features_completas.csv')
    estatisticas_features.to_csv(caminho_estatisticas)
    
    # Salva informações dos segmentos
    info_segmentos = df_features[['segmento', 'condicao', 'label']].copy()
    caminho_info = os.path.join(pasta_features, 'info_segmentos_completos.csv')
    info_segmentos.to_csv(caminho_info, index=False)
    
    # Salva features por condição
    pasta_por_condicao = os.path.join(pasta_features, 'features_por_condicao')
    os.makedirs(pasta_por_condicao, exist_ok=True)
    
    for condicao in df_features['condicao'].unique():
        df_condicao = df_features[df_features['condicao'] == condicao]
        caminho_condicao = os.path.join(pasta_por_condicao, f'features_{condicao.replace(" ", "_").replace("-", "_")}.csv')
        df_condicao.to_csv(caminho_condicao, index=False)
    
    print(f"\nResultados salvos:")
    print(f"- Features completas: {caminho_features}")
    print(f"- Estatísticas das features: {caminho_estatisticas}")
    print(f"- Informações dos segmentos: {caminho_info}")
    print(f"- Features por condição: {pasta_por_condicao}")
    
    # Estatísticas dos dados
    print(f"\nEstatísticas dos dados:")
    print(f"- Total de amostras: {len(df_features)}")
    labels_array = np.array(labels)
    print(f"- Amostras normais (label 0): {sum(labels_array == 0)}")
    print(f"- Amostras com falha (label 1): {sum(labels_array == 1)}")
    print(f"- Features extraídas: {len(colunas_features)}")
    print(f"- Condições únicas: {len(df_features['condicao'].unique())}")
    
    # Mostra as condições encontradas
    print(f"\nCondições encontradas:")
    for i, condicao in enumerate(df_features['condicao'].unique(), 1):
        count = len(df_features[df_features['condicao'] == condicao])
        print(f"{i}. {condicao} ({count} segmentos)")
    
    # Mostra as primeiras features como exemplo
    print(f"\nPrimeiras 20 features extraídas:")
    for i, feature in enumerate(colunas_features[:20], 1):
        print(f"{i}. {feature}")
    
    print(f"... e mais {len(colunas_features) - 20} features")

# ============================================================================
# FUNÇÃO 2: EXTRAÇÃO POR SEGMENTO INDIVIDUAL (extrair_features_por_segmento.py)
# ============================================================================

def extrair_features_por_segmento(pasta_condicao):
    """Extrai features de cada segmento individualmente"""
    nome_condicao = os.path.basename(pasta_condicao)
    print(f"\n--- Processando: {nome_condicao} ---")
    
    # Cria pasta para a condição
    pasta_condicao_features = os.path.join(pasta_segmentos, nome_condicao)
    os.makedirs(pasta_condicao_features, exist_ok=True)
    
    arquivos_processados = 0
    arquivos_erro = 0
    
    # Lista todos os arquivos CSV na pasta
    arquivos_csv = [f for f in os.listdir(pasta_condicao) if f.lower().endswith('.csv')]
    arquivos_csv.sort()  # Ordena os arquivos
    
    print(f"Encontrados {len(arquivos_csv)} arquivos CSV")
    
    for arquivo in arquivos_csv:
        caminho_arquivo = os.path.join(pasta_condicao, arquivo)
        nome_segmento = arquivo.replace('.csv', '')
        
        try:
            # Lê os dados do arquivo
            dados = ler_dados_arquivo(caminho_arquivo)
            
            if len(dados) == 0:
                print(f"  Arquivo {arquivo} não contém dados válidos, pulando...")
                continue
            
            if len(dados) < 3:
                print(f"  Arquivo {arquivo} tem apenas {len(dados)} pontos, pulando...")
                continue
            
            dados = np.array(dados)
            
            # Calcula todas as features
            features = calcular_features_completas(dados)
            
            # Cria DataFrame com as features
            df_features = pd.DataFrame([features])
            df_features['segmento'] = nome_segmento
            df_features['condicao'] = nome_condicao
            
            # Define label baseado no nome da pasta
            nome_pasta = nome_condicao.lower()
            if 'h' in nome_pasta or 'normal' in nome_pasta:
                df_features['label'] = 0  # Estado normal
            elif 'fault' in nome_pasta or 'crack' in nome_pasta or 'erosion' in nome_pasta or 'unbalance' in nome_pasta:
                df_features['label'] = 1  # Estado com falha
            else:
                df_features['label'] = 0  # Padrão como normal
            
            # Salva features do segmento individual
            caminho_segmento = os.path.join(pasta_condicao_features, f'features_{nome_segmento}.csv')
            df_features.to_csv(caminho_segmento, index=False)
            
            arquivos_processados += 1
            
            # Mostra progresso a cada 20 arquivos
            if arquivos_processados % 20 == 0:
                print(f"  Processados {arquivos_processados}/{len(arquivos_csv)} arquivos...")
            
        except Exception as e:
            print(f"  Erro ao processar {arquivo}: {e}")
            arquivos_erro += 1
            continue
    
    print(f"  ✓ Concluído: {arquivos_processados} arquivos processados, {arquivos_erro} erros")
    return arquivos_processados, arquivos_erro

# ============================================================================
# FUNÇÃO 3: PROCESSAMENTO DE TODAS AS SUBPASTAS (extrair_features_todas_subpastas.py)
# ============================================================================

def processar_todas_subpastas():
    """Processa todas as subpastas de dados_convertidos_csv"""
    print("=== EXTRAÇÃO DE FEATURES POR SEGMENTO - TODAS AS SUBPASTAS ===")
    print(f"Pasta de dados: {pasta_dados}")
    print(f"Pasta de resultados: {pasta_features}")
    
    if not os.path.exists(pasta_dados):
        print(f"ERRO: Pasta de dados não encontrada: {pasta_dados}")
        return
    
    # Lista todas as subpastas
    subpastas = [d for d in os.listdir(pasta_dados) if os.path.isdir(os.path.join(pasta_dados, d))]
    subpastas.sort()
    
    print(f"\nEncontradas {len(subpastas)} subpastas:")
    for i, subpasta in enumerate(subpastas, 1):
        print(f"  {i}. {subpasta}")
    
    total_arquivos_processados = 0
    total_arquivos_erro = 0
    
    # Processa cada subpasta
    for i, subpasta in enumerate(subpastas, 1):
        pasta_condicao = os.path.join(pasta_dados, subpasta)
        print(f"\n[{i}/{len(subpastas)}] Processando subpasta: {subpasta}")
        
        arquivos_processados, arquivos_erro = extrair_features_por_segmento(pasta_condicao)
        total_arquivos_processados += arquivos_processados
        total_arquivos_erro += arquivos_erro
    
    print(f"\n=== PROCESSO CONCLUÍDO ===")
    print(f"Total de subpastas processadas: {len(subpastas)}")
    print(f"Total de segmentos processados: {total_arquivos_processados}")
    print(f"Total de segmentos com erro: {total_arquivos_erro}")
    print(f"Features salvas em: {pasta_segmentos}")
    
    # Mostra estrutura das pastas criadas
    print(f"\nEstrutura das pastas criadas:")
    for subpasta in subpastas:
        pasta_condicao_features = os.path.join(pasta_segmentos, subpasta)
        if os.path.exists(pasta_condicao_features):
            num_arquivos = len([f for f in os.listdir(pasta_condicao_features) if f.endswith('.csv')])
            print(f"  {subpasta}/ - {num_arquivos} arquivos de features")

# ============================================================================
# MENU PRINCIPAL
# ============================================================================

def main():
    """Função principal - executa automaticamente a extração por segmento individual"""
    print("=== SISTEMA DE EXTRAÇÃO DE FEATURES SEM RELIEF ===")
    print(f"Pasta de dados: {pasta_dados}")
    print(f"Pasta de resultados: {pasta_features}")
    
    # Verifica se as pastas existem
    if not os.path.exists(pasta_dados):
        print(f"ERRO: Pasta de dados não encontrada: {pasta_dados}")
        return
    
    print("\n" + "="*60)
    print("EXECUTANDO EXTRAÇÃO DE FEATURES POR SEGMENTO INDIVIDUAL")
    print("PARA TODAS AS SUBPASTAS AUTOMATICAMENTE")
    print("="*60)
    
    # Executa automaticamente a extração por segmento individual para todas as subpastas
    processar_todas_subpastas()
    
    print("\n=== PROCESSO CONCLUÍDO AUTOMATICAMENTE ===")

if __name__ == "__main__":
    main()
