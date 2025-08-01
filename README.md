# 🎵 BaixaFy - Baixador de Músicas do Spotify

## 📋 Visão Geral

BaixaFy é um aplicativo completo para Windows que permite baixar músicas e playlists do Spotify em formato MP3 de alta qualidade (320kbps). Utiliza SpotDL + YouTube para encontrar e baixar as músicas.

## 📁 Estrutura de Arquivos

Certifique-se que sua pasta do BaixaFy contenha:

```
BaixaFy/
├── BaixaFy.bat                 # ⭐ EXECUTAR ESTE ARQUIVO
├── BaixaFy_Launcher.py         # Launcher robusto
├── launcher_debug.py           # Diagnóstico de problemas  
├── Reparar_BaixaFy.py         # Correção de problemas
├── baixafy_interface.py        # Interface principal
├── baixar.py                   # Script original
├── Instruções.txt              # Manual do usuário
├── venv_portable/              # Python portátil + dependências
│   └── Scripts/
│       ├── python.exe
│       ├── pip.exe
│       └── spotdl.exe
├── ffmpeg-7.1.1/              # FFmpeg para conversão
│   └── bin/
│       └── ffmpeg.exe
└── python/                     # Runtime Python (se usado)
```

## 🚀 Como Usar

### ✅ Método Recomendado
1. **Clique duas vezes em `BaixaFy.bat`**
2. Aguarde a verificação automática
3. A interface gráfica será aberta
4. Cole o link do Spotify e baixe!

### 🔧 Se Houver Problemas
1. Execute `launcher_debug.py` para diagnosticar
2. Execute `Reparar_BaixaFy.py` para corrigir
3. Tente novamente o `BaixaFy.bat`

## 🌐 Links Suportados

- ✅ **Música**: `https://open.spotify.com/track/...`
- ✅ **Playlist**: `https://open.spotify.com/playlist/...`
- ✅ **Álbum**: `https://open.spotify.com/album/...`
- ✅ **Links curtos**: `https://spotify.link/...`

## 🛠️ Solução de Problemas

### ❌ "Prompt abre e fecha rapidamente"

**Possíveis causas:**
- Arquivos faltando na pasta
- Antivírus bloqueando execução
- Dependências corrompidas
- Erro no Python portátil

**Soluções:**
1. **Execute o diagnóstico:**
   ```bash
   # Clique duas vezes em:
   launcher_debug.py
   ```

2. **Repare o BaixaFy:**
   ```bash
   # Clique duas vezes em:
   Reparar_BaixaFy.py
   ```

3. **Verifique estrutura de pastas:**
   - Certifique-se que `venv_portable/` existe
   - Verifique se `ffmpeg-7.1.1/` está presente
   - Confirme que `baixafy_interface.py` está na pasta

### ❌ "SpotDL não encontrado"

**Solução:**
1. Execute `Reparar_BaixaFy.py`
2. Marque "Reinstalar dependências Python"
3. Aguarde a reinstalação automática

### ❌ "Erro de permissão"

**Solução:**
1. Clique com botão direito em `BaixaFy.bat`
2. Selecione "Executar como administrador"

### ❌ "Interface não abre"

**Verificações:**
1. Windows 10/11 atualizado
2. Antivírus não está bloqueando
3. Pasta não está em área protegida (Desktop, Downloads)

**Solução:**
1. Mova BaixaFy para `C:\BaixaFy\`
2. Execute como administrador
3. Adicione exceção no antivírus

## 📦 Para Desenvolvedores

### Criando Pacote Portátil

```bash
# 1. Criar venv portátil
python -m venv venv_portable

# 2. Ativar venv
venv_portable\Scripts\activate

# 3. Instalar dependências
pip install spotdl customtkinter yt-dlp requests

# 4. Baixar FFmpeg
# Extrair em ffmpeg-7.1.1/

# 5. Copiar scripts Python
# BaixaFy_Launcher.py, baixafy_interface.py, etc.

# 6. Criar BaixaFy.bat como ponto de entrada

# 7. Testar em máquina limpa
```

### Estrutura de Inicialização

```
BaixaFy.bat → BaixaFy_Launcher.py → baixafy_interface.py
              ↓
           Verificações:
           - Estrutura de arquivos ✓
           - Python portátil ✓  
           - Dependências ✓
           - FFmpeg ✓
```

### Logs e Debug

- **Logs automáticos**: Interface captura erros em tempo real
- **Debug manual**: `launcher_debug.py` para diagnóstico
- **Reparo automático**: `Reparar_BaixaFy.py` reinstala dependências

## 🔄 Distribuição

### Criando Pacote para Distribuição

1. **Prepare a estrutura completa**
2. **Teste em máquina limpa** (importante!)
3. **Comprima em ZIP**:
   ```
   BaixaFy_v1.0.zip
   ├── Todos os arquivos e pastas
   └── LEIA-ME.txt (instruções básicas)
   ```

### Checklist de Distribuição

- [ ] Todas as pastas incluídas (`venv_portable`, `ffmpeg-7.1.1`)
- [ ] Scripts Python funcionais
- [ ] `BaixaFy.bat` como ponto de entrada
- [ ] Testado em Windows 10/11 limpo
- [ ] Instruções claras para usuário final
- [ ] Scripts de reparo incluídos

## 🚨 Notas Importantes

### Para Usuários Finais
- **NÃO DELETE** nenhuma pasta ou arquivo
- **SEMPRE** use `BaixaFy.bat` para iniciar
- **RESPEITE** direitos autorais das músicas
- **MANTENHA** todos os arquivos na mesma pasta

### Para Desenvolvedores
- **TESTE** sempre em ambiente limpo antes de distribuir
- **INCLUA** ferramentas de diagnóstico e reparo
- **DOCUMENTE** problemas conhecidos e soluções
- **VERSIONE** releases adequadamente

## 📞 Suporte

### Informações para Suporte
Ao reportar problemas, inclua:

1. **Versão do Windows** (Win 10/11)
2. **Link que tentou baixar**
3. **Mensagem de erro completa**
4. **Log do `launcher_debug.py`**
5. **Resultado do `Reparar_BaixaFy.py`**

### Problemas Conhecidos

| Problema | Causa | Solução |
|----------|-------|---------|
| Prompt fecha rapidamente | Dependência faltando | Execute `Reparar_BaixaFy.py` |
| SpotDL não funciona | Instalação corrompida | Reinstalar dependências |
| Interface não abre | Problema CustomTkinter | Executar como admin + reparo |
| Erro FFmpeg | FFmpeg faltando/corrompido | Re-extrair arquivo completo |

## 📄 Licença

Este projeto é para uso educacional. Respeite os direitos autorais das músicas baixadas.

---

**Desenvolvido com ❤️ | BaixaFy v1.0 | 2025**