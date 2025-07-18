import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

class SistemaDataAugmentation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Data Augmentation - Wind Turbine Blades Fault")
        self.root.geometry("1200x750")  # Aumenta o tamanho da janela
        self.root.configure(bg='#f0f0f0')
        self.pasta_selecionada = None
        self.arquivo_selecionado = None
        self.configurar_interface()
        self.carregar_logos()

    def configurar_interface(self):
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        top_frame = tk.Frame(main_frame, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, pady=(0, 20))

        self.gva_label = tk.Label(top_frame, bg='#f0f0f0')
        self.gva_label.pack(side=tk.LEFT, padx=10, pady=10)
        self.naat_label = tk.Label(top_frame, bg='#f0f0f0')
        self.naat_label.pack(side=tk.RIGHT, padx=10, pady=10)

        title_frame = tk.Frame(top_frame, bg='#f0f0f0')
        title_frame.pack(side=tk.TOP, expand=True)
        title_label = tk.Label(title_frame, text="Sistema de Data Augmentation", font=("Arial", 24, "bold"), bg='#f0f0f0')
        title_label.pack()
        # subtitle_label = tk.Label(title_frame, text="Wind Turbine Blades Fault Analysis", font=("Arial", 14), bg='#f0f0f0')
        # subtitle_label.pack()

        config_frame = tk.LabelFrame(main_frame, 
                                    text="Configurações de Augmentation",
                                    font=("Arial", 12, "bold"),
                                    bg='#f0f0f0',
                                    fg='#2c3e50')
        config_frame.pack(fill=tk.X, pady=(0, 20))
        params_frame = tk.Frame(config_frame, bg='#f0f0f0')
        params_frame.pack(fill=tk.X, padx=20, pady=20)

        # Tooltip helper
        def create_tooltip(widget, text):
            tooltip = tk.Toplevel(widget)
            tooltip.withdraw()
            tooltip.overrideredirect(True)
            label = tk.Label(tooltip, text=text, background='#ffffe0', relief='solid', borderwidth=1, font=("Arial", 9))
            label.pack(ipadx=1)
            def enter(event):
                x = widget.winfo_rootx() + widget.winfo_width() + 5
                y = widget.winfo_rooty()
                tooltip.geometry(f"+{x}+{y}")
                tooltip.deiconify()
            def leave(event):
                tooltip.withdraw()
            widget.bind('<Enter>', enter)
            widget.bind('<Leave>', leave)

        # Quantidade total de dados desejada
        tk.Label(params_frame, 
                text="Quantidade total de dados desejada:",
                font=("Arial", 10, "bold"),
                bg='#f0f0f0').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.qtd_total_var = tk.StringVar(value="500")
        qtd_total_entry = tk.Entry(params_frame, 
                              textvariable=self.qtd_total_var,
                              font=("Arial", 10),
                              width=10)
        qtd_total_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        interro_qtd = tk.Label(params_frame, text="?", font=("Arial", 10, "bold"), fg="#2980b9", bg="#f0f0f0", cursor="question_arrow")
        interro_qtd.grid(row=0, column=2, sticky=tk.W, padx=(5,0))
        create_tooltip(interro_qtd, "Informe o número total de linhas desejado no arquivo CSV final, incluindo dados originais e interpolados. O sistema irá distribuir os valores interpolados proporcionalmente entre os pontos originais.")
        # (Remover mensagem de feedback daqui)

        # Método de Interpolação
        tk.Label(params_frame,
                text="Método de Interpolação:",
                font=("Arial", 10, "bold"),
                bg='#f0f0f0').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.metodo_var = tk.StringVar(value="cubic")
        metodo_combo = ttk.Combobox(params_frame,
                                   textvariable=self.metodo_var,
                                   values=["linear", "cubic", "spline"],
                                   state="readonly",
                                   width=15)
        metodo_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        interro_metodo = tk.Label(params_frame, text="?", font=("Arial", 10, "bold"), fg="#2980b9", bg="#f0f0f0", cursor="question_arrow")
        interro_metodo.grid(row=1, column=2, sticky=tk.W, padx=(5,0))
        create_tooltip(interro_metodo, "Escolha o tipo de interpolação para gerar os valores intermediários:\n\n- Linear: conecta os pontos com linhas retas. Simples, rápido e preserva tendências abruptas.\n- Cúbica: usa curvas suaves entre os pontos, ideal para sinais contínuos e suaves.\n- Spline: utiliza curvas ainda mais suaves e flexíveis, recomendado para dados com variações suaves e sem ruídos bruscos.\n\nA escolha afeta como os dados aumentados se comportam entre os pontos originais.")

        # Suavização
        tk.Label(params_frame,
                text="Suavização (Savitzky-Golay):",
                font=("Arial", 10, "bold"),
                bg='#f0f0f0').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.suavizacao_var = tk.BooleanVar(value=True)
        suavizacao_check = tk.Checkbutton(params_frame,
                                         variable=self.suavizacao_var,
                                         bg='#f0f0f0')
        suavizacao_check.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        interro_suav = tk.Label(params_frame, text="?", font=("Arial", 10, "bold"), fg="#2980b9", bg="#f0f0f0", cursor="question_arrow")
        interro_suav.grid(row=2, column=2, sticky=tk.W, padx=(5,0))
        create_tooltip(interro_suav, "Se ativado, aplica um filtro de suavização para reduzir ruídos nos dados aumentados, preservando tendências principais.")

        # Remover botão 'Processar e Salvar CSV' (caso ainda exista)
        # (Não adicionar nenhum botão de processar dentro de params_frame)
        # O botão correto já está em data_frame como 'Processar dados'

        data_frame = tk.LabelFrame(main_frame,
                                  text="Seleção de Dados",
                                  font=("Arial", 12, "bold"),
                                  bg='#f0f0f0',
                                  fg='#2c3e50')
        data_frame.pack(fill=tk.X, pady=(0, 20))
        # Botões de seleção e reset
        botoes_frame = tk.Frame(data_frame, bg='#f0f0f0')
        botoes_frame.pack(pady=10)
        # Linha superior: botões de carregamento centralizados
        linha_cima = tk.Frame(botoes_frame, bg='#f0f0f0')
        linha_cima.pack()
        select_pasta_button = tk.Button(linha_cima,
                                 text="Selecionar pasta",
                                 command=self.selecionar_pasta,
                                 font=("Arial", 11, "bold"),
                                 bg='#3498db',
                                 fg='white',
                                 relief=tk.FLAT,
                                 padx=20,
                                 pady=10)
        select_pasta_button.pack(side=tk.LEFT, padx=10)
        select_arquivo_button = tk.Button(linha_cima,
                                 text="Selecionar arquivo",
                                 command=self.selecionar_arquivo,
                                 font=("Arial", 11, "bold"),
                                 bg='#8e44ad',
                                 fg='white',
                                 relief=tk.FLAT,
                                 padx=20,
                                 pady=10)
        select_arquivo_button.pack(side=tk.LEFT, padx=10)
        # Feedback do nome da pasta/arquivo carregado
        self.pasta_label = tk.Label(botoes_frame,
                                   text="Nenhuma pasta ou arquivo selecionado",
                                   font=("Arial", 10),
                                   bg='#f0f0f0',
                                   fg='#7f8c8d')
        self.pasta_label.pack(pady=(8, 8))
        # Linha inferior: processar, segmentar, resetar centralizados
        linha_baixo = tk.Frame(botoes_frame, bg='#f0f0f0')
        linha_baixo.pack(pady=(10,0))
        processar_button = tk.Button(linha_baixo,
                                     text="Processar dados",
                                     command=self.iniciar_processamento,
                                     font=("Arial", 11, "bold"),
                                     bg='#27ae60',
                                     fg='white',
                                     relief=tk.FLAT,
                                     padx=20,
                                     pady=10)
        processar_button.pack(side=tk.LEFT, padx=10)
        segmentar_button = tk.Button(linha_baixo,
                                     text="Segmentar dados",
                                     command=self.abrir_interface_segmentacao,
                                     font=("Arial", 11, "bold"),
                                     bg='#e67e22',
                                     fg='white',
                                     relief=tk.FLAT,
                                     padx=20,
                                     pady=10)
        segmentar_button.pack(side=tk.LEFT, padx=10)
        reset_button = tk.Button(linha_baixo,
                                 text="Resetar dados",
                                 command=self.resetar_dados,
                                 font=("Arial", 11, "bold"),
                                 bg='#e74c3c',
                                 fg='white',
                                 relief=tk.FLAT,
                                 padx=20,
                                 pady=10)
        reset_button.pack(side=tk.LEFT, padx=10)

        # Após todos os campos de configuração, antes do botão de processar dados
        # Mensagem de feedback sobre aplicação individual (visual profissional, em caixa)
        # Mensagem inicial de feedback
        self.feedback_msg_inicial = "A quantidade total de dados será aplicada individualmente a cada arquivo carregado. Por exemplo, se você carregar 10 arquivos e pedir 2000, cada arquivo de saída terá 2000 linhas."
        feedback_frame = tk.LabelFrame(main_frame, text="Informação Importante", font=("Arial", 10, "bold"), bg='#f0f0f0', fg='#2980b9', bd=2, relief=tk.GROOVE, labelanchor='nw')
        feedback_frame.pack(fill=tk.X, pady=(0, 15), padx=10)
        self.feedback_qtd_label = tk.Label(feedback_frame, text=self.feedback_msg_inicial, font=("Arial", 10, "italic"), bg='#f0f0f0', fg='#222', justify='left', anchor='w', wraplength=1000, padx=10, pady=6)
        self.feedback_qtd_label.pack(fill=tk.X, padx=5, pady=5)

        # Botão de processar dados abaixo dos botões principais
        # processar_button = tk.Button(data_frame,
        #                              text="Processar dados",
        #                              command=self.iniciar_processamento,
        #                              font=("Arial", 11, "bold"),
        #                              bg='#27ae60',
        #                              fg='white',
        #                              relief=tk.FLAT,
        #                              padx=20,
        #                              pady=10)
        # processar_button.pack(pady=(10, 0))

        # Botão Segmentar dados
        # segmentar_button = tk.Button(data_frame,
        #                              text="Segmentar dados",
        #                              command=self.abrir_interface_segmentacao,
        #                              font=("Arial", 11, "bold"),
        #                              bg='#e67e22',
        #                              fg='white',
        #                              relief=tk.FLAT,
        #                              padx=20,
        #                              pady=10)
        # segmentar_button.pack(pady=(10, 0))

    def carregar_logos(self):
        try:
            # Logo GVA
            gva_img = Image.open("gva.jpg")
            gva_img = gva_img.resize((90, 90), Image.Resampling.LANCZOS)
            self.gva_photo = ImageTk.PhotoImage(gva_img)
            self.gva_label.configure(image=self.gva_photo)
            # Logo NAAT
            naat_img = Image.open("naat.jpg")
            naat_img = naat_img.resize((90, 90), Image.Resampling.LANCZOS)
            self.naat_photo = ImageTk.PhotoImage(naat_img)
            self.naat_label.configure(image=self.naat_photo)
        except Exception as e:
            print(f"Erro ao carregar logos: {e}")

    def sugerir_configuracao(self, caminho_arquivo):
        import pandas as pd
        import numpy as np
        from scipy.signal import savgol_filter
        from scipy.stats import kurtosis
        # Tentar ler o arquivo
        ext = os.path.splitext(caminho_arquivo)[1].lower()
        df = None
        if ext in ['.xls', '.xlsx']:
            df = pd.read_excel(caminho_arquivo)
        elif ext in ['.csv']:
            delimitadores = [';', ',', '\t']
            decimais = ['.', ',']
            for delim in delimitadores:
                for dec in decimais:
                    try:
                        temp_df = pd.read_csv(caminho_arquivo, delimiter=delim, decimal=dec)
                        temp_conv = temp_df.copy()
                        for col in temp_conv.columns:
                            temp_conv[col] = pd.to_numeric(temp_conv[col], errors='coerce')
                        colunas_numericas = temp_conv.select_dtypes(include=[np.number]).columns.tolist()
                        if colunas_numericas:
                            df = temp_df
                            break
                    except Exception:
                        continue
                if df is not None:
                    break
        if df is None:
            return None
        df_convertido = df.copy()
        for col in df_convertido.columns:
            df_convertido[col] = pd.to_numeric(df_convertido[col], errors='coerce')
        colunas_numericas = df_convertido.select_dtypes(include=[np.number]).columns.tolist()
        if not colunas_numericas:
            return None
        df_numerico = df_convertido[colunas_numericas]
        n = len(df_numerico)
        if n < 2:
            return None
        # Análise do sinal
        y = df_numerico[colunas_numericas[0]].values
        diffs = np.diff(y)
        std = np.std(y)
        std_diff = np.std(diffs)
        max_diff = np.max(np.abs(diffs))
        kurt = kurtosis(y)
        # Critérios
        if std_diff > 2*std or max_diff > 3*std:
            metodo = 'linear'
            motivo = 'Sinal com variações abruptas ou picos.'
        elif kurt > 5:
            metodo = 'linear'
            motivo = 'Sinal com picos acentuados (alta curtose).'
        elif std_diff < 0.2*std:
            metodo = 'spline'
            motivo = 'Sinal muito suave.'
        else:
            metodo = 'cubic'
            motivo = 'Sinal com tendência suave.'
        # Suavização
        if std_diff > 0.5*std:
            suavizacao = True
            motivo_suav = 'Ruído moderado/alto detectado.'
        else:
            suavizacao = False
            motivo_suav = 'Sinal limpo.'
        # Quantidade máxima recomendada
        # Regra: até 3x pontos originais se std_diff/std < 0.5, até 2x se std_diff/std < 1, senão igual ao original
        if std_diff < 0.5*std:
            qtd_max = min(5*n, 2000)
        elif std_diff < std:
            qtd_max = min(3*n, 1500)
        else:
            qtd_max = min(2*n, 1000)
        return {
            'metodo': metodo,
            'motivo': motivo,
            'suavizacao': suavizacao,
            'motivo_suav': motivo_suav,
            'qtd_max': qtd_max,
            'n': n
        }

    def exibir_sugestao(self, sugestao):
        if sugestao is None:
            msg = 'Não foi possível sugerir configuração automática para os dados carregados.'
        else:
            msg = f"Sugestão automática:\n- Método de interpolação: {sugestao['metodo'].capitalize()} ({sugestao['motivo']})\n- Suavização: {'Ativada' if sugestao['suavizacao'] else 'Desativada'} ({sugestao['motivo_suav']})\n- Quantidade máxima recomendada de dados: {sugestao['qtd_max']} (original: {sugestao['n']})"
        self.feedback_qtd_label.config(text=msg)

    def selecionar_arquivo(self):
        arquivo = filedialog.askopenfilename(title="Selecione um arquivo de dados", filetypes=[("Arquivos de dados", "*.csv;*.xls;*.xlsx")])
        if arquivo:
            self.arquivo_selecionado = arquivo
            self.pasta_selecionada = None
            self.pasta_label.config(text=f"Arquivo selecionado: {os.path.basename(arquivo)}")
            sugestao = self.sugerir_configuracao(arquivo)
            self.exibir_sugestao(sugestao)
            # Preencher campos automaticamente
            if sugestao:
                self.metodo_var.set(sugestao['metodo'])
                self.suavizacao_var.set(sugestao['suavizacao'])
                self.qtd_total_var.set(str(sugestao['qtd_max']))

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta contendo arquivos e/ou subpastas de dados")
        if pasta:
            self.pasta_selecionada = pasta
            self.arquivo_selecionado = None
            self.pasta_label.config(text=f"Pasta selecionada: {os.path.basename(pasta)}")
            # Procurar primeiro arquivo válido para sugerir
            for root, dirs, files in os.walk(pasta):
                for f in files:
                    if f.lower().endswith((".csv", ".xls", ".xlsx")):
                        arquivo = os.path.join(root, f)
                        sugestao = self.sugerir_configuracao(arquivo)
                        self.exibir_sugestao(sugestao)
                        if sugestao:
                            self.metodo_var.set(sugestao['metodo'])
                            self.suavizacao_var.set(sugestao['suavizacao'])
                            self.qtd_total_var.set(str(sugestao['qtd_max']))
                        return
            self.exibir_sugestao(None)

    def resetar_dados(self):
        import shutil
        pastas_para_apagar = [
            "dados_aumentados",
            "dados_carregados"
        ]
        for pasta in pastas_para_apagar:
            if os.path.exists(pasta):
                try:
                    shutil.rmtree(pasta)
                except Exception as e:
                    print(f"Erro ao apagar {pasta}: {e}")
        self.pasta_selecionada = None
        self.arquivo_selecionado = None
        self.pasta_label.config(text="Nenhuma pasta ou arquivo selecionado")
        # Restaurar mensagem inicial na caixa de feedback
        self.feedback_qtd_label.config(text=self.feedback_msg_inicial)

    def iniciar_processamento(self):
        import pandas as pd
        import numpy as np
        from scipy import interpolate
        from scipy.signal import savgol_filter
        import os
        import tkinter as tk
        from tkinter import messagebox
        # Obter parâmetros
        try:
            qtd_total = int(self.qtd_total_var.get())
            metodo = self.metodo_var.get()
            aplicar_suavizacao = self.suavizacao_var.get()
        except Exception:
            messagebox.showerror("Erro", "Parâmetros inválidos!")
            return
        arquivos_para_processar = []
        if self.pasta_selecionada:
            for root, dirs, files in os.walk(self.pasta_selecionada):
                for f in files:
                    if f.lower().endswith((".csv", ".xls", ".xlsx")):
                        arquivos_para_processar.append(os.path.join(root, f))
        elif self.arquivo_selecionado:
            if self.arquivo_selecionado.lower().endswith((".csv", ".xls", ".xlsx")):
                arquivos_para_processar.append(self.arquivo_selecionado)
            else:
                from tkinter import messagebox
                messagebox.showwarning("Aviso", "Selecione apenas arquivos .csv, .xls ou .xlsx!")
                return
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo ou pasta selecionado!")
            return
        if not arquivos_para_processar:
            messagebox.showwarning("Aviso", "Nenhum arquivo válido encontrado!")
            return
        # Copiar arquivos carregados para dados_carregados antes de processar
        pasta_carregados = os.path.join(os.getcwd(), "dados_carregados")
        import shutil
        for caminho_arquivo in arquivos_para_processar:
            rel_path = os.path.relpath(os.path.dirname(caminho_arquivo), self.pasta_selecionada) if self.pasta_selecionada else ''
            destino_dir = os.path.join(pasta_carregados, rel_path)
            os.makedirs(destino_dir, exist_ok=True)
            destino = os.path.join(destino_dir, os.path.basename(caminho_arquivo))
            try:
                shutil.copy2(caminho_arquivo, destino)
            except Exception as e:
                print(f"Erro ao copiar {caminho_arquivo} para {destino}: {e}")
        pasta_resultados = os.path.join(os.getcwd(), "dados_aumentados")
        os.makedirs(pasta_resultados, exist_ok=True)
        processados = 0
        primeiro_original = None
        primeiro_interpolado = None
        primeiro_nome = None
        for caminho_arquivo in arquivos_para_processar:
            try:
                ext = os.path.splitext(caminho_arquivo)[1].lower()
                if ext in ['.xls', '.xlsx']:
                    df = pd.read_excel(caminho_arquivo)
                elif ext in ['.csv']:
                    # Tentar diferentes delimitadores e decimais
                    delimitadores = [';', ',', '\t']
                    decimais = ['.', ',']
                    df = None
                    for delim in delimitadores:
                        for dec in decimais:
                            try:
                                temp_df = pd.read_csv(caminho_arquivo, delimiter=delim, decimal=dec)
                                # Tentar converter todas as colunas para numérico
                                temp_conv = temp_df.copy()
                                for col in temp_conv.columns:
                                    temp_conv[col] = pd.to_numeric(temp_conv[col], errors='coerce')
                                colunas_numericas = temp_conv.select_dtypes(include=[np.number]).columns.tolist()
                                if colunas_numericas:
                                    df = temp_df
                                    break
                            except Exception:
                                continue
                        if df is not None:
                            break
                    if df is None:
                        print(f"Arquivo ignorado (não foi possível identificar colunas numéricas em nenhum formato): {caminho_arquivo}")
                        continue
                else:
                    print(f"Arquivo ignorado (extensão não suportada): {caminho_arquivo}")
                    continue
                # Tentar converter todas as colunas para numérico, se possível
                df_convertido = df.copy()
                for col in df_convertido.columns:
                    df_convertido[col] = pd.to_numeric(df_convertido[col], errors='coerce')
                colunas_numericas = df_convertido.select_dtypes(include=[np.number]).columns.tolist()
                if not colunas_numericas:
                    print(f"Arquivo ignorado (sem colunas numéricas): {caminho_arquivo}")
                    continue
                df_numerico = df_convertido[colunas_numericas]
                n = len(df_numerico)
                if n < 2:
                    print(f"Arquivo ignorado (menos de 2 linhas): {caminho_arquivo}")
                    continue
                if qtd_total < n:
                    print(f"Arquivo ignorado (quantidade desejada menor que o número de linhas originais): {caminho_arquivo}")
                    continue
                if qtd_total == n:
                    # Apenas copia os dados e marca como original
                    df_final = df_numerico.copy()
                    df_final['tipo_valor'] = ['original'] * n
                else:
                    # Nova lógica: garantir que os valores 'original' sejam idênticos aos do arquivo original
                    x_original = np.linspace(0, 1, n)
                    x_novo = np.linspace(0, 1, qtd_total)
                    # Encontrar os índices dos pontos originais no novo vetor
                    idxs_originais = np.round(np.linspace(0, qtd_total-1, n)).astype(int)
                    dados_finais = []
                    # Para cada intervalo entre pontos originais, inserir original e interpolados
                    for i in range(n-1):
                        # Adiciona o valor original (copiado fielmente)
                        linha_original = {col: df_numerico.iloc[i][col] for col in colunas_numericas}
                        linha_original['tipo_valor'] = 'original'
                        dados_finais.append(linha_original)
                        # Índices no novo vetor
                        idx_ini = idxs_originais[i]
                        idx_fim = idxs_originais[i+1]
                        n_interp = idx_fim - idx_ini - 1
                        if n_interp > 0:
                            x_interp = x_novo[idx_ini+1:idx_fim]
                            for xi in x_interp:
                                linha_interp = {}
                                for col in colunas_numericas:
                                    y = df_numerico[col].values
                                    if aplicar_suavizacao and len(y) > 15:
                                        y = savgol_filter(y, 15, 3)
                                    if metodo == 'linear':
                                        f_interp = interpolate.interp1d(x_original, y, kind='linear')
                                        val = f_interp(xi)
                                    elif metodo == 'cubic':
                                        f_interp = interpolate.interp1d(x_original, y, kind='cubic')
                                        val = f_interp(xi)
                                    elif metodo == 'spline':
                                        spline = interpolate.UnivariateSpline(x_original, y, s=0)
                                        val = spline(xi)
                                    else:
                                        f_interp = interpolate.interp1d(x_original, y, kind='linear')
                                        val = f_interp(xi)
                                    linha_interp[col] = val
                                linha_interp['tipo_valor'] = 'interpolado'
                                dados_finais.append(linha_interp)
                    # Adiciona o último valor original
                    linha_original = {col: df_numerico.iloc[-1][col] for col in colunas_numericas}
                    linha_original['tipo_valor'] = 'original'
                    dados_finais.append(linha_original)
                    df_final = pd.DataFrame(dados_finais)
                nome_arquivo = os.path.splitext(os.path.basename(caminho_arquivo))[0]
                caminho_saida = os.path.join(pasta_resultados, f"{nome_arquivo}_augmented.csv")
                df_final.to_csv(caminho_saida, index=False)
                # Armazenar dados do primeiro arquivo para o gráfico comparativo
                if processados == 0:
                    import numpy as np
                    primeiro_original = np.array(df_numerico.iloc[:,0]).flatten()
                    primeiro_interpolado = np.array(df_final.iloc[:,0]).flatten()
                    primeiro_nome = os.path.splitext(os.path.basename(caminho_arquivo))[0]
                processados += 1
                print(f"Arquivo processado: {caminho_arquivo} -> {caminho_saida}")
            except Exception as e:
                print(f"Erro ao processar {caminho_arquivo}: {e}")
        # (Remover geração de gráfico comparativo e métricas estatísticas)
        msg_final = f"Data augmentation concluído!\nArquivos processados: {processados}\nResultados salvos em: {os.path.abspath(pasta_resultados)}"
        messagebox.showinfo("Sucesso", msg_final)

    def abrir_interface_segmentacao(self):
        import tkinter as tk
        from tkinter import ttk
        from PIL import Image, ImageTk
        import threading
        import os
        import pandas as pd
        seg_win = tk.Toplevel(self.root)
        seg_win.title("Sistema de Segmentação com janelamento")
        seg_win.geometry("1200x750")
        seg_win.minsize(1200, 750)
        seg_win.configure(bg='#f0f0f0')
        # Frame superior para logos
        top_frame = tk.Frame(seg_win, bg='#f0f0f0')
        top_frame.pack(fill=tk.X, pady=(10, 20))
        # Logo GVA
        try:
            gva_img = Image.open("gva.jpg")
            gva_img = gva_img.resize((90, 90), Image.Resampling.LANCZOS)
            gva_photo = ImageTk.PhotoImage(gva_img)
            gva_label = tk.Label(top_frame, image=gva_photo, bg='#f0f0f0')
            gva_label.image = gva_photo
            gva_label.pack(side=tk.LEFT, padx=10, pady=10)
        except Exception as e:
            gva_label = tk.Label(top_frame, text="[Logo GVA]", bg='#f0f0f0')
            gva_label.pack(side=tk.LEFT, padx=10, pady=10)
        # Logo NAAT
        try:
            naat_img = Image.open("naat.jpg")
            naat_img = naat_img.resize((90, 90), Image.Resampling.LANCZOS)
            naat_photo = ImageTk.PhotoImage(naat_img)
            naat_label = tk.Label(top_frame, image=naat_photo, bg='#f0f0f0')
            naat_label.image = naat_photo
            naat_label.pack(side=tk.RIGHT, padx=10, pady=10)
        except Exception as e:
            naat_label = tk.Label(top_frame, text="[Logo NAAT]", bg='#f0f0f0')
            naat_label.pack(side=tk.RIGHT, padx=10, pady=10)
        # Título centralizado
        title_label = tk.Label(top_frame, text="Sistema de Segmentação com janelamento", font=("Arial", 22, "bold"), bg='#f0f0f0')
        title_label.pack(side=tk.TOP, pady=(10, 0))

        # Tooltip helper
        def create_tooltip(widget, text):
            tooltip = tk.Toplevel(widget)
            tooltip.withdraw()
            tooltip.overrideredirect(True)
            label = tk.Label(tooltip, text=text, background='#ffffe0', relief='solid', borderwidth=1, font=("Arial", 9))
            label.pack(ipadx=1)
            def enter(event):
                x = widget.winfo_rootx() + widget.winfo_width() + 5
                y = widget.winfo_rooty()
                tooltip.geometry(f"+{x}+{y}")
                tooltip.deiconify()
            def leave(event):
                tooltip.withdraw()
            widget.bind('<Enter>', enter)
            widget.bind('<Leave>', leave)

        # Parâmetros de janelamento
        param_frame = tk.LabelFrame(seg_win, text="Configuração do Janelamento", font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#2c3e50')
        param_frame.pack(fill=tk.X, padx=30, pady=(0, 20))
        # Quantidade de segmentos desejada
        tk.Label(param_frame, text="Quantidade de segmentos desejada:", font=("Arial", 10, "bold"), bg='#f0f0f0').grid(row=0, column=0, sticky=tk.W, pady=8)
        qtd_segmentos_var = tk.StringVar(value="20")
        tk.Entry(param_frame, textvariable=qtd_segmentos_var, font=("Arial", 10), width=10).grid(row=0, column=1, sticky=tk.W, padx=(10,0), pady=8)
        interro_qtd = tk.Label(param_frame, text="?", font=("Arial", 10, "bold"), fg="#2980b9", bg="#f0f0f0", cursor="question_arrow")
        interro_qtd.grid(row=0, column=2, sticky=tk.W, padx=(5,0))
        create_tooltip(interro_qtd, "Informe o número total de segmentos desejado para cada arquivo. O sistema irá sugerir automaticamente o tamanho da janela e a sobreposição ideais para cobrir todo o arquivo sem perder o sentido físico dos dados.")
        # Tamanho da janela
        tk.Label(param_frame, text="Tamanho da janela (nº de linhas):", font=("Arial", 10, "bold"), bg='#f0f0f0').grid(row=1, column=0, sticky=tk.W, pady=8)
        tamanho_janela_var = tk.StringVar(value="200")
        tk.Entry(param_frame, textvariable=tamanho_janela_var, font=("Arial", 10), width=10).grid(row=1, column=1, sticky=tk.W, padx=(10,0), pady=8)
        interro_janela = tk.Label(param_frame, text="?", font=("Arial", 10, "bold"), fg="#2980b9", bg="#f0f0f0", cursor="question_arrow")
        interro_janela.grid(row=1, column=2, sticky=tk.W, padx=(5,0))
        create_tooltip(interro_janela, "Define quantos pontos (linhas) cada segmento terá. Segmentos muito pequenos podem perder o sentido físico do sinal. O valor sugerido é calculado para cobrir todo o arquivo com a quantidade de segmentos desejada.")
        # Sobreposição percentual
        tk.Label(param_frame, text="Sobreposição (%):", font=("Arial", 10, "bold"), bg='#f0f0f0').grid(row=2, column=0, sticky=tk.W, pady=8)
        sobreposicao_var = tk.StringVar(value="50")
        tk.Entry(param_frame, textvariable=sobreposicao_var, font=("Arial", 10), width=10).grid(row=2, column=1, sticky=tk.W, padx=(10,0), pady=8)
        interro_sobre = tk.Label(param_frame, text="?", font=("Arial", 10, "bold"), fg="#2980b9", bg="#f0f0f0", cursor="question_arrow")
        interro_sobre.grid(row=2, column=2, sticky=tk.W, padx=(5,0))
        create_tooltip(interro_sobre, "Porcentagem de sobreposição entre segmentos consecutivos. Valores altos (ex: 50%) garantem que os segmentos compartilhem boa parte dos dados, útil para análise de sinais contínuos. Valores baixos reduzem a redundância, mas podem deixar lacunas.")
        # Botão para sugerir parâmetros
        def sugerir_parametros():
            try:
                S = int(qtd_segmentos_var.get())
                if S < 2:
                    feedback_label.config(text="A quantidade de segmentos deve ser pelo menos 2.", fg="#e74c3c")
                    return
                pasta_entrada = os.path.join(os.getcwd(), "dados_aumentados")
                arquivos = [f for f in os.listdir(pasta_entrada) if f.lower().endswith('.csv')]
                if not arquivos:
                    feedback_label.config(text="Nenhum arquivo CSV encontrado em 'dados_aumentados'!", fg="#e74c3c")
                    return
                import pandas as pd
                N_min = None
                for arq in arquivos:
                    df = pd.read_csv(os.path.join(pasta_entrada, arq))
                    n = len(df)
                    if N_min is None or n < N_min:
                        N_min = n
                min_w = 100
                # Cálculo ideal
                step = max((N_min - min_w) // (S - 1), 1)
                W = min_w + step
                if W > N_min:
                    W = N_min
                    step = max(1, N_min // S)
                sobreposicao_frac = 1 - (step / W)
                sobreposicao_pct = int(round(sobreposicao_frac * 100))
                if sobreposicao_pct < 0:
                    sobreposicao_pct = 0
                if sobreposicao_pct > 99:
                    sobreposicao_pct = 99
                tamanho_janela_var.set(str(W))
                sobreposicao_var.set(str(sobreposicao_pct))
                feedback_label.config(text=f"Sugestão: Para {S} segmentos, janela ≈ {W} linhas, sobreposição ≈ {sobreposicao_pct}% (baseado no menor arquivo com {N_min} linhas). Ajuste se necessário.", fg="#2980b9")
            except Exception as e:
                feedback_label.config(text=f"Erro ao sugerir parâmetros: {e}", fg="#e74c3c")
        btn_sugerir = tk.Button(param_frame, text="Sugerir parâmetros", command=sugerir_parametros, font=("Arial", 9, "bold"), bg='#2980b9', fg='white', relief=tk.FLAT)
        btn_sugerir.grid(row=0, column=2, rowspan=3, padx=(20,0), pady=8)

        # Frame para botões de ação alinhados horizontalmente
        botoes_frame = tk.Frame(seg_win, bg='#f0f0f0')
        botoes_frame.pack(pady=(0, 10))

        # Tamanho otimizado para caber na interface minimizada
        btn_width = 18

        # Botão de segmentar (laranja)
        seg_btn = tk.Button(botoes_frame, text="Segmentar", font=("Arial", 11, "bold"), bg='#e67e22', fg='white', relief=tk.FLAT, padx=10, pady=10, width=btn_width)
        seg_btn.pack(side=tk.LEFT, padx=6)

        # Botão de reiniciar processo
        def reiniciar_processo():
            import shutil
            pasta_saida = os.path.join(os.getcwd(), "segmentos_com_janelamento")
            if os.path.exists(pasta_saida):
                try:
                    shutil.rmtree(pasta_saida)
                    feedback_label.config(text="Processo reiniciado: todos os segmentos e logs foram apagados.", fg="#e67e22")
                except Exception as e:
                    feedback_label.config(text=f"Erro ao apagar dados: {e}", fg="#e74c3c")
            else:
                feedback_label.config(text="Nada para apagar: a pasta de segmentos já está vazia.", fg="#2980b9")
        btn_reiniciar = tk.Button(botoes_frame, text="Reiniciar processo", command=reiniciar_processo, font=("Arial", 11, "bold"), bg='#e74c3c', fg='white', relief=tk.FLAT, padx=10, pady=10, width=btn_width)
        btn_reiniciar.pack(side=tk.LEFT, padx=6)

        # Botão de baixar vetores
        def baixar_vetores():
            import shutil
            from tkinter import filedialog, messagebox
            pasta_origem = os.path.join(os.getcwd(), "resultados_segmentos")
            if not os.path.exists(pasta_origem):
                feedback_label.config(text="A pasta 'resultados_segmentos' não existe!", fg="#e74c3c")
                return
            destino = filedialog.askdirectory(title="Escolha a pasta de destino para salvar os vetores segmentados")
            if not destino:
                return
            try:
                # Copiar mantendo estrutura
                for item in os.listdir(pasta_origem):
                    src_path = os.path.join(pasta_origem, item)
                    dst_path = os.path.join(destino, item)
                    if os.path.isdir(src_path):
                        if os.path.exists(dst_path):
                            shutil.rmtree(dst_path)
                        shutil.copytree(src_path, dst_path)
                    else:
                        shutil.copy2(src_path, dst_path)
                feedback_label.config(text=f"Vetores copiados para: {destino}", fg="#27ae60")
            except Exception as e:
                feedback_label.config(text=f"Erro ao copiar vetores: {e}", fg="#e74c3c")
        btn_baixar = tk.Button(botoes_frame, text="Baixar Vetores", command=baixar_vetores, font=("Arial", 11, "bold"), bg='#2980b9', fg='white', relief=tk.FLAT, padx=10, pady=10, width=btn_width)
        btn_baixar.pack(side=tk.LEFT, padx=6)

        # Botão de extrair features
        def abrir_interface_features():
            import shutil
            import os
            import tkinter as tk
            from PIL import Image, ImageTk
            # 1. Apagar todos os dados de /dados_convertidos_csv
            pasta_convertidos = os.path.join(os.getcwd(), "dados_convertidos_csv")
            if os.path.exists(pasta_convertidos):
                try:
                    shutil.rmtree(pasta_convertidos)
                except Exception as e:
                    feedback_label.config(text=f"Erro ao apagar dados convertidos: {e}", fg="#e74c3c")
                    return
            os.makedirs(pasta_convertidos, exist_ok=True)
            # 2. Converter .txt de /segmentos_com_janelamento para .csv
            pasta_origem = os.path.join(os.getcwd(), "segmentos_com_janelamento")
            for root, dirs, files in os.walk(pasta_origem):
                for file in files:
                    if file.lower().endswith('.txt'):
                        caminho_arquivo = os.path.join(root, file)
                        rel_path = os.path.relpath(root, pasta_origem)
                        pasta_saida = os.path.join(pasta_convertidos, rel_path)
                        os.makedirs(pasta_saida, exist_ok=True)
                        nome_csv = os.path.splitext(file)[0] + '.csv'
                        caminho_saida = os.path.join(pasta_saida, nome_csv)
                        with open(caminho_arquivo, 'r', encoding='utf-8') as f_in, open(caminho_saida, 'w', encoding='utf-8') as f_out:
                            for linha in f_in:
                                f_out.write(linha)
            # 3. Abrir interface de features
            features_win = tk.Toplevel(seg_win)
            features_win.title("Extrator de Features")
            features_win.geometry("800x400")
            features_win.minsize(800, 400)
            features_win.configure(bg='#f0f0f0')
            # Frame superior para logos
            top_frame = tk.Frame(features_win, bg='#f0f0f0')
            top_frame.pack(fill=tk.X, pady=(10, 20))
            # Logo GVA
            try:
                gva_img = Image.open("gva.jpg")
                gva_img = gva_img.resize((90, 90), Image.Resampling.LANCZOS)
                gva_photo = ImageTk.PhotoImage(gva_img)
                gva_label = tk.Label(top_frame, image=gva_photo, bg='#f0f0f0')
                gva_label.image = gva_photo
                gva_label.pack(side=tk.LEFT, padx=10, pady=10)
            except Exception as e:
                gva_label = tk.Label(top_frame, text="[Logo GVA]", bg='#f0f0f0')
                gva_label.pack(side=tk.LEFT, padx=10, pady=10)
            # Logo NAAT
            try:
                naat_img = Image.open("naat.jpg")
                naat_img = naat_img.resize((90, 90), Image.Resampling.LANCZOS)
                naat_photo = ImageTk.PhotoImage(naat_img)
                naat_label = tk.Label(top_frame, image=naat_photo, bg='#f0f0f0')
                naat_label.image = naat_photo
                naat_label.pack(side=tk.RIGHT, padx=10, pady=10)
            except Exception as e:
                naat_label = tk.Label(top_frame, text="[Logo NAAT]", bg='#f0f0f0')
                naat_label.pack(side=tk.RIGHT, padx=10, pady=10)
            # Título centralizado
            title_label = tk.Label(top_frame, text="Extrator de Features", font=("Arial", 22, "bold"), bg='#f0f0f0')
            title_label.pack(side=tk.TOP, pady=(10, 0))
            # Frame para botões de ação
            botoes_feat = tk.Frame(features_win, bg='#f0f0f0')
            botoes_feat.pack(pady=(10, 10))
            btn_width = 16
            # Feedback
            feedback_feat = tk.Label(features_win, text="", font=("Arial", 10), bg='#f0f0f0', fg='#e67e22', wraplength=700, justify='left')
            feedback_feat.pack(pady=(0,10))
            def processar_features():
                import shutil
                import os
                import sys
                import importlib.util
                pasta_features = os.path.join(os.getcwd(), "features_extraidas")
                if os.path.exists(pasta_features):
                    try:
                        shutil.rmtree(pasta_features)
                    except Exception as e:
                        feedback_feat.config(text=f"Erro ao apagar features antigas: {e}", fg="#e74c3c")
                        return
                os.makedirs(pasta_features, exist_ok=True)
                try:
                    spec = importlib.util.spec_from_file_location("features_sem_relief", os.path.join(os.getcwd(), "features_sem_relief.py"))
                    features_mod = importlib.util.module_from_spec(spec)
                    sys.modules["features_sem_relief"] = features_mod
                    spec.loader.exec_module(features_mod)
                    features_mod.processar_todas_subpastas()
                    feedback_feat.config(text="Extração de features concluída com sucesso! Resultados em 'features_extraidas'.", fg="#27ae60")
                except Exception as e:
                    feedback_feat.config(text=f"Erro ao extrair features: {e}", fg="#e74c3c")
            btn_proc = tk.Button(botoes_feat, text="Processar", command=processar_features, font=("Arial", 11, "bold"), bg='#e67e22', fg='white', relief=tk.FLAT, padx=10, pady=10, width=btn_width)
            btn_proc.pack(side=tk.LEFT, padx=8)
            def baixar_features():
                import shutil
                from tkinter import filedialog
                pasta_origem = os.path.join(os.getcwd(), "features_extraidas")
                if not os.path.exists(pasta_origem):
                    feedback_feat.config(text="A pasta 'features_extraidas' não existe!", fg="#e74c3c")
                    return
                destino = filedialog.askdirectory(title="Escolha a pasta de destino para salvar as features extraídas")
                if not destino:
                    return
                try:
                    for item in os.listdir(pasta_origem):
                        src_path = os.path.join(pasta_origem, item)
                        dst_path = os.path.join(destino, item)
                        if os.path.isdir(src_path):
                            if os.path.exists(dst_path):
                                shutil.rmtree(dst_path)
                            shutil.copytree(src_path, dst_path)
                        else:
                            shutil.copy2(src_path, dst_path)
                    feedback_feat.config(text=f"Features copiadas para: {destino}", fg="#27ae60")
                except Exception as e:
                    feedback_feat.config(text=f"Erro ao copiar features: {e}", fg="#e74c3c")
            btn_baixar = tk.Button(botoes_feat, text="Baixar Vetores", command=baixar_features, font=("Arial", 11, "bold"), bg='#2980b9', fg='white', relief=tk.FLAT, padx=10, pady=10, width=btn_width)
            btn_baixar.pack(side=tk.LEFT, padx=8)
            def reiniciar_features():
                import shutil
                import os
                pasta_features = os.path.join(os.getcwd(), "features_extraidas")
                if os.path.exists(pasta_features):
                    try:
                        shutil.rmtree(pasta_features)
                        feedback_feat.config(text="Processo reiniciado: todos os dados de features foram apagados.", fg="#e67e22")
                    except Exception as e:
                        feedback_feat.config(text=f"Erro ao apagar features: {e}", fg="#e74c3c")
                else:
                    feedback_feat.config(text="Nada para apagar: a pasta de features já está vazia.", fg="#2980b9")
            btn_reiniciar = tk.Button(botoes_feat, text="Reiniciar processo", command=reiniciar_features, font=("Arial", 11, "bold"), bg='#e74c3c', fg='white', relief=tk.FLAT, padx=10, pady=10, width=btn_width)
            btn_reiniciar.pack(side=tk.LEFT, padx=8)
            # Aqui pode-se adicionar o restante da interface de features futuramente
            # Após fechar, retorna para a interface de segmentação normalmente
        btn_features = tk.Button(botoes_frame, text="Extrair Features", command=abrir_interface_features, font=("Arial", 11, "bold"), bg='#16a085', fg='white', relief=tk.FLAT, padx=10, pady=10, width=btn_width)
        btn_features.pack(side=tk.LEFT, padx=6)

        # Feedback
        feedback_label = tk.Label(seg_win, text="", font=("Arial", 10), bg='#f0f0f0', fg='#e67e22', wraplength=800, justify='left')
        feedback_label.pack(pady=(0,10))

        # Função de segmentação com janelamento
        def segmentar_arquivo_csv(caminho_csv, tamanho_janela, sobreposicao_pct, pasta_saida):
            df = pd.read_csv(caminho_csv)
            n = len(df)
            W = tamanho_janela
            sobreposicao = int(round(W * (sobreposicao_pct / 100)))
            step = W - sobreposicao
            if step <= 0:
                raise ValueError("A sobreposição deve ser menor que o tamanho da janela.")
            os.makedirs(pasta_saida, exist_ok=True)
            caminhos_segmentos = []
            for inicio in range(0, n - W + 1, step):
                fim = inicio + W
                segmento = df.iloc[inicio:fim]
                nome_segmento = f"segmento_{len(caminhos_segmentos)+1}.txt"
                caminho_segmento = os.path.join(pasta_saida, nome_segmento)
                segmento.to_csv(caminho_segmento, sep='\t', index=False)
                caminhos_segmentos.append(caminho_segmento)
            return caminhos_segmentos

        # Função principal de processamento
        def executar_segmentacao():
            try:
                tamanho_janela = int(tamanho_janela_var.get())
                sobreposicao_pct = int(sobreposicao_var.get())
                if tamanho_janela <= 1 or not (0 <= sobreposicao_pct < 100):
                    feedback_label.config(text="Parâmetros inválidos: a sobreposição (%) deve ser entre 0 e 99 e a janela maior que 1.", fg="#e74c3c")
                    return
            except Exception:
                feedback_label.config(text="Parâmetros inválidos!", fg="#e74c3c")
                return
            pasta_entrada = os.path.join(os.getcwd(), "dados_aumentados")
            pasta_saida = os.path.join(os.getcwd(), "segmentos_com_janelamento")
            if not os.path.exists(pasta_entrada):
                feedback_label.config(text="A pasta 'dados_aumentados' não existe!", fg="#e74c3c")
                return
            arquivos = [f for f in os.listdir(pasta_entrada) if f.lower().endswith('.csv')]
            if not arquivos:
                feedback_label.config(text="Nenhum arquivo CSV encontrado em 'dados_aumentados'!", fg="#e74c3c")
                return
            feedback_label.config(text="Segmentando arquivos, aguarde...", fg="#2980b9")
            seg_btn.config(state=tk.DISABLED)
            def rodar():
                log = []
                resultado = {'arquivos': [], 'segmentos': {}, 'erros': {}}
                for arquivo in arquivos:
                    nome_base = os.path.splitext(arquivo)[0]
                    pasta_saida_arq = os.path.join(pasta_saida, nome_base)
                    caminho_csv = os.path.join(pasta_entrada, arquivo)
                    try:
                        caminhos_segmentos = segmentar_arquivo_csv(caminho_csv, tamanho_janela, sobreposicao_pct, pasta_saida_arq)
                        n_segmentos = len(caminhos_segmentos)
                        log.append(f"Arquivo {arquivo}: {n_segmentos} segmentos salvos em {pasta_saida_arq}")
                        resultado['arquivos'].append(arquivo)
                        resultado['segmentos'][arquivo] = caminhos_segmentos
                        if n_segmentos == 0:
                            log.append(f"  [AVISO] Nenhum segmento gerado para {arquivo}!")
                    except Exception as e:
                        log.append(f"Erro ao segmentar {arquivo}: {e}")
                        resultado['erros'][arquivo] = str(e)
                # Salvar log
                os.makedirs(pasta_saida, exist_ok=True)
                log_path = os.path.join(pasta_saida, "log_segmentacao.txt")
                with open(log_path, "w", encoding="utf-8") as f:
                    for linha in log:
                        f.write(linha + "\n")
                n_arquivos = len(resultado['arquivos'])
                n_segmentos = sum(len(v) for v in resultado['segmentos'].values())
                feedback = f"Segmentação concluída! {n_arquivos} arquivos processados, {n_segmentos} segmentos gerados.\nVeja detalhes no log: {log_path}"
                if resultado['erros']:
                    feedback += f"\nErros: {resultado['erros']}"
                feedback_label.config(text=feedback, fg="#27ae60")
                seg_btn.config(state=tk.NORMAL)
            threading.Thread(target=rodar).start()

        seg_btn.config(command=executar_segmentacao)

    def executar(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SistemaDataAugmentation()
    app.executar() 