# 🎵 BaixaFy - Spotify Music Downloader

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

Um aplicativo desktop moderno e intuitivo para baixar músicas e playlists do Spotify usando  **spotDL** . Interface limpa, funcional e fácil de usar!

## ✨ Características

* 🎨  **Interface Moderna** : Design limpo e intuitivo com tema escuro
* 🔍  **Busca Inteligente** : Cole qualquer URL do Spotify (música ou playlist)
* ✅  **Seleção Flexível** : Escolha quais músicas baixar individualmente
* 📁  **Pasta Personalizada** : Escolha onde salvar suas músicas
* 📊  **Progresso Visual** : Barra de progresso para cada download
* 🚀  **Executável Único** : Não precisa instalar, apenas execute o .exe

## 🖼️ Screenshots

```
┌─────────────────────────────────────────┐
│           🎵 BaixaFy                    │
│    Baixe suas músicas favoritas do     │
│            Spotify                      │
├─────────────────────────────────────────┤
│ 🔗 Cole a URL do Spotify:              │
│ [https://open.spotify.com/playlist/...] │
│            [🔍 Pesquisar Músicas]       │
├─────────────────────────────────────────┤
│ 📁 Pasta de destino:                   │
│ [C:\Users\User\Music] [Escolher Pasta] │
├─────────────────────────────────────────┤
│ 🎶 Músicas encontradas:                │
│ ☑️ Song 1 - Artist 1      ✅ Concluído │
│ ☑️ Song 2 - Artist 2      ⏳ Baixando  │
│ ☐ Song 3 - Artist 3      ❌ Erro      │
│                                         │
│ [✅ Selecionar Todas] [❌ Dessel. Todas]│
│        [⬇️ Baixar Músicas Selecionadas] │
└─────────────────────────────────────────┘
```

## 🚀 Instalação Rápida

### Opção 1: Executável Pronto (Recomendado)

1. Baixe o arquivo `BaixaFy.exe`
2. Execute o arquivo
3. Pronto! 🎉

### Opção 2: Executar do Código Fonte

**Pré-requisitos:**

* Python 3.8 ou superior
* pip (gerenciador de pacotes do Python)

**Passos:**

1. **Clone ou baixe os arquivos:**
   ```bash
   # Baixe todos os arquivos para uma pasta
   ```
2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Execute o programa:**
   ```bash
   python baixar.py
   ```

### Opção 3: Criar Seu Próprio Executável

1. **Execute o setup automático:**

   ```bash
   python setup.py
   ```

   OU use o arquivo batch no Windows:

   ```cmd
   criar_executavel.bat
   ```
2. **O executável será criado como `BaixaFy.exe`**

## 📋 Como Usar

### Passo a Passo:

1. **🚀 Abra o BaixaFy**
   * Execute `BaixaFy.exe` ou `python baixar.py`
2. **🔗 Cole a URL do Spotify**
   * Copie o link de uma música ou playlist do Spotify
   * Cole no campo "Cole a URL do Spotify"
   * Exemplo: `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M`
3. **🔍 Pesquise as Músicas**
   * Clique em "Pesquisar Músicas"
   * Aguarde a busca (pode demorar alguns segundos)
4. **✅ Selecione as Músicas**
   * Marque/desmarque as músicas que deseja baixar
   * Use "Selecionar Todas" ou "Desselecionar Todas" para rapidez
5. **📁 Escolha a Pasta (Opcional)**
   * Por padrão, salva na pasta "Música" do Windows
   * Clique em "Escolher Pasta" para mudar
6. **⬇️ Baixe as Músicas**
   * Clique em "Baixar Músicas Selecionadas"
   * Acompanhe o progresso de cada música
   * Pronto! 🎉

## 🛠️ Dependências

O BaixaFy utiliza as seguintes bibliotecas:

* **customtkinter** : Interface gráfica moderna
* **spotdl** : Download de músicas do Spotify via YouTube
* **pillow** : Manipulação de imagens
* **tkinter** : Interface gráfica base (inclusa no Python)

## ⚙️ Configurações Avançadas

### Formato e Qualidade

O BaixaFy baixa músicas em:

* **Formato** : MP3
* **Qualidade** : 320kbps (máxima qualidade)

### Pasta Padrão

* **Windows** : `C:\Users\[Usuario]\Music`
* **Linux/Mac** : `~/Music`

## 🐛 Resolução de Problemas

### SpotDL não encontrado

```
❌ SpotDL não está instalado!
```

**Solução:**

```bash
pip install spotdl
```

### Erro na busca de playlist

```
❌ Erro ao buscar músicas
```

**Possíveis causas:**

* URL inválida (deve ser do Spotify)
* Problemas de conexão
* Playlist privada ou restrita

**Soluções:**

* Verifique se a URL está correta
* Teste sua conexão com internet
* Tente com uma playlist pública

### Erro no download

```
❌ Erro no download
```

**Possíveis causas:**

* Música não disponível no YouTube
* Problemas de conexão
* Pasta de destino sem permissão de escrita

**Soluções:**

* Tente baixar uma música por vez
* Verifique permissões da pasta
* Escolha uma pasta diferente

## 📝 Notas Legais

* Este software utiliza o **spotDL** para buscar músicas no YouTube
* Respeite os direitos autorais e termos de uso do Spotify e YouTube
* Use apenas para fins pessoais e educacionais
* O BaixaFy não armazena nem distribui conteúdo protegido por direitos autorais

## 🤝 Contribuições

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](https://claude.ai/chat/LICENSE) para detalhes.

## 🙏 Agradecimentos

* **spotDL** - Ferramenta fantástica para download de músicas
* **CustomTkinter** - Interface moderna para Python
* **Comunidade Python** - Por todas as bibliotecas incríveis

---

**Desenvolvido com ❤️ para a comunidade Python**

🎵 **Divirta-se baixando suas músicas favoritas!** 🎵
