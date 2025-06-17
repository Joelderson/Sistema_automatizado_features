# Sistema Automatizado de Segmentação e Extração de Features

Este projeto é um sistema completo para processamento, segmentação e extração de features de dados vibratórios, desenvolvido em Python com interface gráfica.

## 🚀 Funcionalidades Principais

- **Interface Gráfica Intuitiva**: Sistema completo com GUI usando Tkinter
- **Processamento de Dados**: Suporte a múltiplos formatos (TXT, CSV)
- **Segmentação Automática**: Divisão de dados em segmentos configuráveis
- **Extração de Features**: Features estatísticas e de frequência
- **Método ReliefF**: Seleção automática de features mais relevantes
- **Sistema de Reset**: Reinicialização completa do processo
- **Exportação de Resultados**: Download organizado dos dados processados

## 📁 Estrutura do Projeto

```
sistema_segmentacao/
├── sistema_automatizado.py      # Interface principal do sistema
├── sistema_segmentacao.py       # Sistema básico de segmentação
├── metodo_relief.py             # Implementação do método ReliefF
├── features_sem_relief.py       # Extração de features básicas
├── conversor_csv.py             # Conversor de formatos
├── requirements.txt             # Dependências do projeto
├── gva.jpg                      # Logo GVA
├── naat.jpg                     # Logo NAAT
├── dados_testes/                # Dados de teste
├── resultados_segmentos/        # Segmentos processados
├── features_extraidas/          # Features extraídas
└── dados_convertidos_csv/       # Dados convertidos
```

## 🛠️ Instalação

1. **Clone o repositório**:
```bash
git clone https://github.com/Joelderson/Sistema_automatizado_features.git
cd Sistema_automatizado_features
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Execute o sistema**:
```bash
python sistema_automatizado.py
```

## 📋 Dependências

- `tkinter` - Interface gráfica
- `PIL` - Processamento de imagens
- `numpy` - Computação numérica
- `pandas` - Manipulação de dados
- `scikit-learn` - Machine Learning
- `scipy` - Processamento de sinais
- `matplotlib` - Visualização de dados

## 🎯 Como Usar

### 1. Interface Principal
- Execute `sistema_automatizado.py`
- Selecione arquivo ou pasta com dados
- Configure o número de segmentos
- Use os botões para processar, baixar ou resetar dados

### 2. Extração de Features
- Clique em "Extrair Features"
- Escolha se deseja aplicar o método ReliefF
- Aguarde o processamento
- Baixe os resultados

### 3. Reset Completo
- Use "Resetar dados" para limpar tudo
- O sistema reiniciará automaticamente o processo completo

## 🔧 Funcionalidades Detalhadas

### Segmentação de Dados
- Divisão automática em segmentos iguais
- Organização em subpastas por arquivo
- Tratamento de arquivos duplicados

### Extração de Features
**Features Estatísticas:**
- Média, desvio padrão, variância
- Máximo, mínimo, amplitude
- RMS, assimetria, curtose
- Mediana, quartis, IQR
- Cruzamentos por zero, energia

**Features de Frequência (FFT):**
- Frequência dominante
- Amplitude máxima e média FFT
- Energia FFT

### Método ReliefF
- Seleção automática de features mais relevantes
- Ranking de importância das features
- Organização dos resultados por segmento

## 📊 Resultados

O sistema gera:
- **Segmentos processados** em `resultados_segmentos/`
- **Features extraídas** em `features_extraidas/`
- **Dados convertidos** em `dados_convertidos_csv/`
- **Logs detalhados** do processamento

## 🎨 Interface Gráfica

- Design moderno com logos GVA e NAAT
- Botões intuitivos e responsivos
- Feedback visual do processamento
- Janelas modais para configurações

## 🔄 Processo Automatizado

1. **Conversão**: Dados originais → CSV
2. **Segmentação**: Divisão em segmentos
3. **Extração**: Features estatísticas e de frequência
4. **Seleção**: Aplicação do método ReliefF (opcional)
5. **Organização**: Resultados estruturados

## 🚨 Tratamento de Erros

- Validação de entrada de dados
- Tratamento de arquivos corrompidos
- Logs detalhados de erros
- Recuperação automática de falhas

## 📝 Logs e Monitoramento

- Logs detalhados de cada etapa
- Timestamps de processamento
- Resumos de execução
- Relatórios de erro

## 🔒 Segurança

- Validação de tipos de arquivo
- Verificação de integridade
- Backup automático de dados críticos
- Tratamento seguro de exceções

## 🤝 Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 👨‍💻 Autor

**Joelderson** - [GitHub](https://github.com/Joelderson)

## 🙏 Agradecimentos

- GVA - Grupo de Vibrações e Acústica
- NAAT - Núcleo de Análise e Aplicação de Tecnologias

---

**Desenvolvido com ❤️ para análise de dados vibratórios** 