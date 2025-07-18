import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os
import re
import shutil
import pandas as pd

# Variável global para armazenar o caminho do arquivo
definir_caminho = {'arquivo': None, 'pasta': None, 'tipo': None}

# Função para selecionar pasta
def selecionar_pasta():
    pasta = filedialog.askdirectory(title="Selecione a pasta com arquivos de dados")
    if pasta:
        definir_caminho['pasta'] = pasta
        definir_caminho['arquivo'] = None
        definir_caminho['tipo'] = 'pasta'
    else:
        definir_caminho['pasta'] = None
        definir_caminho['tipo'] = None
    atualizar_label_selecionado()

# Função para selecionar arquivo
def selecionar_arquivo():
    arquivo = filedialog.askopenfilename(
        title="Selecione um arquivo para processar",
        filetypes=[
            ("Arquivos de dados", "*.csv;*.xls;*.xlsx"),
            ("CSV", "*.csv"),
            ("Excel", "*.xls;*.xlsx"),
            ("Todos os arquivos", "*.*")
        ]
    )
    if arquivo:
        definir_caminho['arquivo'] = arquivo
        definir_caminho['pasta'] = None
        definir_caminho['tipo'] = 'arquivo'
    else:
        definir_caminho['arquivo'] = None
        definir_caminho['tipo'] = None
    atualizar_label_selecionado()

# Função para processar os dados
def processar_dados():
    tipo = definir_caminho['tipo']
    arquivos_para_processar = []
    if tipo == 'arquivo':
        caminho_arquivo = definir_caminho['arquivo']
        if not caminho_arquivo:
            messagebox.showerror("Erro", "Selecione um arquivo ou pasta antes de processar.")
            return
        arquivos_para_processar.append(caminho_arquivo)
    elif tipo == 'pasta':
        pasta = definir_caminho['pasta']
        if not pasta:
            messagebox.showerror("Erro", "Selecione uma pasta antes de processar.")
            return
        # Buscar arquivos de dados em todas as subpastas
        for root, dirs, files in os.walk(pasta):
            for file in files:
                if file.lower().endswith(('.txt', '.csv', '.xls', '.xlsx')):
                    arquivos_para_processar.append(os.path.join(root, file))
        if not arquivos_para_processar:
            messagebox.showerror("Erro", "Nenhum arquivo de dados (.txt, .csv, .xls, .xlsx) encontrado na pasta.")
            return
    else:
        messagebox.showerror("Erro", "Selecione um arquivo ou pasta antes de processar.")
        return
    try:
        n_segmentos = int(entrada_segmentos.get())
        if n_segmentos <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Erro", "Digite um número válido de segmentos.")
        return
    pasta_base = os.path.join(os.getcwd(), 'resultados_segmentos')
    os.makedirs(pasta_base, exist_ok=True)
    for caminho_arquivo in arquivos_para_processar:
        try:
            ext = os.path.splitext(caminho_arquivo)[1].lower()
            if ext in ['.csv', '.txt']:
                try:
                    df = pd.read_csv(caminho_arquivo, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        df = pd.read_csv(caminho_arquivo, encoding='latin1')
                    except Exception as e:
                        messagebox.showerror("Erro ao ler arquivo", f"{caminho_arquivo}: {e}")
                        continue
                linhas = df.to_csv(index=False, header=True).splitlines(keepends=True)
                total_linhas = len(linhas)
                if n_segmentos > total_linhas:
                    messagebox.showerror("Erro", f"O número de segmentos é maior que o número de linhas do arquivo: {os.path.basename(caminho_arquivo)}.")
                    continue
                tamanho_segmento = total_linhas // n_segmentos
                resto = total_linhas % n_segmentos
                segmentos = []
                inicio = 0
                for i in range(n_segmentos):
                    fim = inicio + tamanho_segmento + (1 if i < resto else 0)
                    segmentos.append(linhas[inicio:fim])
                    inicio = fim
                nome_arquivo = os.path.splitext(os.path.basename(caminho_arquivo))[0]
                subpasta_nome = nome_arquivo
                subpastas_existentes = [d for d in os.listdir(pasta_base) if os.path.isdir(os.path.join(pasta_base, d))]
                if subpasta_nome in subpastas_existentes:
                    idx = 1
                    while f"{nome_arquivo}_{idx}" in subpastas_existentes:
                        idx += 1
                    subpasta_nome = f"{nome_arquivo}_{idx}"
                pasta_saida = os.path.join(pasta_base, subpasta_nome)
                if os.path.exists(pasta_saida):
                    shutil.rmtree(pasta_saida)
                os.makedirs(pasta_saida, exist_ok=True)
                for idx, segmento in enumerate(segmentos):
                    nome_saida = os.path.join(pasta_saida, f'segmento_{idx+1}.txt')
                    with open(nome_saida, 'w', encoding='utf-8') as f:
                        f.writelines(segmento)
            elif ext in ['.xls', '.xlsx']:
                try:
                    df = pd.read_excel(caminho_arquivo)
                except Exception as e:
                    messagebox.showerror("Erro ao ler arquivo Excel", f"{caminho_arquivo}: {e}")
                    continue
                total_linhas = len(df)
                if n_segmentos > total_linhas:
                    messagebox.showerror("Erro", f"O número de segmentos é maior que o número de linhas do arquivo: {os.path.basename(caminho_arquivo)}.")
                    continue
                tamanho_segmento = total_linhas // n_segmentos
                resto = total_linhas % n_segmentos
                inicio = 0
                nome_arquivo = os.path.splitext(os.path.basename(caminho_arquivo))[0]
                subpasta_nome = nome_arquivo
                subpastas_existentes = [d for d in os.listdir(pasta_base) if os.path.isdir(os.path.join(pasta_base, d))]
                if subpasta_nome in subpastas_existentes:
                    idx = 1
                    while f"{nome_arquivo}_{idx}" in subpastas_existentes:
                        idx += 1
                    subpasta_nome = f"{nome_arquivo}_{idx}"
                pasta_saida = os.path.join(pasta_base, subpasta_nome)
                if os.path.exists(pasta_saida):
                    shutil.rmtree(pasta_saida)
                os.makedirs(pasta_saida, exist_ok=True)
                for i in range(n_segmentos):
                    fim = inicio + tamanho_segmento + (1 if i < resto else 0)
                    segmento_df = df.iloc[inicio:fim]
                    nome_saida = os.path.join(pasta_saida, f'segmento_{i+1}.txt')
                    segmento_df.to_csv(nome_saida, index=False)
                    inicio = fim
            else:
                messagebox.showerror("Erro", f"Formato de arquivo não suportado: {ext}")
                continue
        except Exception as e:
            messagebox.showerror("Erro ao ler arquivo", f"{caminho_arquivo}: {e}")
            continue
    messagebox.showinfo("Sucesso", f"Processamento concluído! Resultados em: {pasta_base}")

def baixar_dados():
    pasta_origem = os.path.join(os.getcwd(), 'resultados_segmentos')
    if not os.path.exists(pasta_origem):
        messagebox.showerror("Erro", "A pasta 'resultados_segmentos' não existe.")
        return
    pasta_destino = filedialog.askdirectory(title="Selecione a pasta de destino para baixar os resultados")
    if not pasta_destino:
        return
    nome_pasta_final = os.path.join(pasta_destino, 'resultados_segmentos')
    # Se já existir, remover para evitar duplicidade
    if os.path.exists(nome_pasta_final):
        try:
            shutil.rmtree(nome_pasta_final)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível sobrescrever a pasta de destino: {e}")
            return
    try:
        shutil.copytree(pasta_origem, nome_pasta_final)
        messagebox.showinfo("Sucesso", f"Dados copiados para: {nome_pasta_final}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao copiar dados: {e}")

def resetar_dados():
    """Apaga todas as pastas de resultados e reinicia o processo do zero"""
    
    # Lista de pastas para apagar
    pastas_para_apagar = [
        "resultados_segmentos",
        "features_extraidas", 
        "dados_convertidos_csv"
    ]
    
    # Verifica se alguma pasta existe
    pastas_existentes = [pasta for pasta in pastas_para_apagar if os.path.exists(pasta)]
    
    if not pastas_existentes:
        messagebox.showinfo("Info", "Nenhum dado processado para resetar.")
        return
    
    # Confirma com o usuário
    mensagem = "Tem certeza que deseja apagar TODOS os dados processados?\n\n"
    mensagem += "Serão apagadas as seguintes pastas:\n"
    for pasta in pastas_existentes:
        mensagem += f"• {pasta}\n"
    mensagem += "\nEsta ação não pode ser desfeita."
    
    confirm = messagebox.askyesno("Confirmar Reset", mensagem)
    if not confirm:
        return
    
    try:
        # Apaga cada pasta
        for pasta in pastas_para_apagar:
            if os.path.exists(pasta):
                shutil.rmtree(pasta)
        
        messagebox.showinfo("Sucesso", "Todos os dados processados foram removidos com sucesso!")
        
        # Resetar variáveis globais
        definir_caminho['arquivo'] = None
        definir_caminho['pasta'] = None
        definir_caminho['tipo'] = None
        atualizar_label_selecionado()
        
        # Pergunta se deseja reiniciar o processo
        if messagebox.askyesno("Reiniciar Processo", 
                              "Deseja reiniciar o processo completo?\n\n"
                              "Isso irá:\n"
                              "1. Converter dados originais para CSV\n"
                              "2. Segmentar os dados\n"
                              "3. Extrair features e aplicar ReliefF"):
            reiniciar_processo_completo()
            
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao remover dados: {e}")

def reiniciar_processo_completo():
    """Reinicia o processo completo de conversão, segmentação e extração de features"""
    
    try:
        # Verifica se existe a pasta de dados originais
        pasta_dados_originais = "dados_originais"
        if not os.path.exists(pasta_dados_originais):
            messagebox.showerror("Erro", 
                               f"Pasta '{pasta_dados_originais}' não encontrada!\n\n"
                               "Por favor, coloque os dados originais na pasta 'dados_originais' antes de continuar.")
            return
        
        # Executa o processo de conversão
        messagebox.showinfo("Processo", "1. Convertendo dados originais para CSV...")
        try:
            import converter_dados
            converter_dados.converter_todos_arquivos()
        except Exception as e:
            messagebox.showerror("Erro na Conversão", f"Erro ao converter dados: {e}")
            return
        
        # Executa o processo de segmentação
        messagebox.showinfo("Processo", "2. Segmentando dados...")
        try:
            import segmentador
            segmentador.segmentar_todos_arquivos()
        except Exception as e:
            messagebox.showerror("Erro na Segmentação", f"Erro ao segmentar dados: {e}")
            return
        
        # Executa o processo de extração de features
        messagebox.showinfo("Processo", "3. Extraindo features e aplicando ReliefF...")
        try:
            import metodo_relief
            # Chama as funções principais do método relief
            todas_features, nomes_segmentos, labels = metodo_relief.extrair_features_vibratorias()
            if len(todas_features) > 0:
                metodo_relief.aplicar_relief_e_salvar()
                metodo_relief.organizar_features_relief_por_segmento()
            else:
                messagebox.showwarning("Aviso", "Nenhum dado válido encontrado para extração de features.")
        except Exception as e:
            messagebox.showerror("Erro na Extração", f"Erro ao extrair features: {e}")
            return
        
        messagebox.showinfo("Sucesso", 
                           "🎉 PROCESSO COMPLETO REINICIADO COM SUCESSO!\n\n"
                           "Todos os dados foram processados do zero:\n"
                           "✓ Conversão de dados\n"
                           "✓ Segmentação\n"
                           "✓ Extração de features\n"
                           "✓ Aplicação do método ReliefF\n\n"
                           "O sistema está pronto para uso!")
        
    except Exception as e:
        messagebox.showerror("Erro Geral", f"Erro durante o reinício do processo: {e}")

def reposicionar_elementos(event=None):
    largura = janela.winfo_width()
    altura = janela.winfo_height()
    # Título
    titulo.place(relx=0.5, y=18, anchor="center")
    # Logos
    label_gva.place(x=10, y=5)
    label_naat.place(x=largura-70, y=10)
    # Botão de seleção
    botao_pasta.place(relx=0.35, y=110, anchor="center")
    botao_arquivo.place(relx=0.65, y=110, anchor="center")
    # Label do arquivo/pasta selecionado
    label_selecionado.place(relx=0.5, y=135, anchor="center")
    # Pergunta e caixa de entrada
    nova_y_pergunta = 230 if altura < 400 else int(altura*0.55)
    txt_pergunta.place(relx=0.5, y=nova_y_pergunta, anchor="center")
    entrada_segmentos.place(relx=0.5, y=nova_y_pergunta+30, anchor="center")
    # Botões inferiores
    largura_total = 330
    x_inicial = (largura - largura_total) // 2
    y_botoes = altura - 50
    botao_processar.place(x=x_inicial + 0, y=y_botoes)
    botao_baixar.place(x=x_inicial + 130, y=y_botoes)
    botao_resetar.place(x=x_inicial + 260, y=y_botoes)

# Criação da janela principal
janela = tk.Tk()
janela.title("Sistema de Segmentação de Dados")
janela.geometry("420x350")

# Título centralizado (ainda menor)
titulo = ttk.Label(janela, text="Sistema de Segmentação de Dados", font=("Arial", 10, "bold"))
titulo.place(relx=0.5, y=18, anchor="center")

# Logo GVA canto superior esquerdo (ampliada)
gva_img = Image.open("gva.jpg")
gva_img = gva_img.resize((75, 75), Image.Resampling.LANCZOS)
gva_photo = ImageTk.PhotoImage(gva_img)
label_gva = ttk.Label(janela, image=gva_photo)
label_gva.image = gva_photo
label_gva.place(x=10, y=5)

# Logo NAAT canto superior direito (ampliada)
naat_img = Image.open("naat.jpg")
naat_img = naat_img.resize((60, 60), Image.Resampling.LANCZOS)
naat_photo = ImageTk.PhotoImage(naat_img)
label_naat = ttk.Label(janela, image=naat_photo)
label_naat.image = naat_photo
label_naat.place(x=350, y=10)

# Botão para selecionar pasta
botao_pasta = ttk.Button(janela, text="Selecionar Pasta", command=selecionar_pasta)
botao_pasta.place(relx=0.35, y=110, anchor="center")

# Botão para selecionar arquivo
botao_arquivo = ttk.Button(janela, text="Selecionar Arquivo", command=selecionar_arquivo)
botao_arquivo.place(relx=0.65, y=110, anchor="center")

# Label para mostrar o nome do arquivo ou pasta selecionado
label_selecionado = ttk.Label(janela, text="Nenhum arquivo ou pasta selecionado.", font=("Arial", 9))
label_selecionado.place(relx=0.5, y=165, anchor="center")

def atualizar_label_selecionado():
    if definir_caminho['tipo'] == 'arquivo' and definir_caminho['arquivo']:
        nome = os.path.basename(definir_caminho['arquivo'])
        label_selecionado.config(text=f"Arquivo: {nome}")
    elif definir_caminho['tipo'] == 'pasta' and definir_caminho['pasta']:
        nome = os.path.basename(definir_caminho['pasta'])
        label_selecionado.config(text=f"Pasta: {nome}")
    else:
        label_selecionado.config(text="Nenhum arquivo ou pasta selecionado.")

# Pergunta e caixa de entrada para número de segmentos
nova_y_pergunta = 230
txt_pergunta = ttk.Label(janela, text="Em quantos segmentos você deseja dividir seus dados?", font=("Arial", 10))
txt_pergunta.place(relx=0.5, y=nova_y_pergunta, anchor="center")

entrada_segmentos = ttk.Entry(janela, width=8, font=("Arial", 10))
entrada_segmentos.place(relx=0.5, y=nova_y_pergunta+30, anchor="center")

# Botões alinhados lado a lado, mais separados
largura_total = 330  # largura total ocupada pelos 3 botões e espaçamentos
x_inicial = (420 - largura_total) // 2

y_botoes = 300
botao_processar = ttk.Button(janela, text="Processar dados", command=processar_dados)
botao_processar.place(x=x_inicial + 0, y=y_botoes)
botao_baixar = ttk.Button(janela, text="Baixar dados", command=baixar_dados)
botao_baixar.place(x=x_inicial + 130, y=y_botoes)
botao_resetar = ttk.Button(janela, text="Resetar dados", command=resetar_dados)
botao_resetar.place(x=x_inicial + 260, y=y_botoes)

# Após criar todos os elementos, vincular o evento de resize
janela.bind('<Configure>', reposicionar_elementos)
reposicionar_elementos()  # Chamada inicial para posicionar

janela.mainloop()
