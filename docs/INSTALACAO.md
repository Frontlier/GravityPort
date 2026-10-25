# Instalação e primeiro uso — GravityPort v0.4.0 (Windows)

## 1. Baixar e verificar

Baixe o **GravityPort-0.4.0-Windows-portable.zip** em
https://github.com/Frontlier/GravityPort/releases/tag/v0.4.0
e salve também o arquivo `.sha256` da mesma versão. No PowerShell, execute:

```powershell
Get-FileHash .\GravityPort-0.4.0-Windows-portable.zip -Algorithm SHA256
```

Compare o hash com o arquivo `.sha256` publicado na mesma página. Extraia o ZIP em uma pasta sua, como `Documentos\GravityPort`, sem executar de dentro do compactado.

Este é um aplicativo Windows **portátil**, sem instalador MSI e sem assinatura digital própria. Somente execute arquivos provenientes do release oficial que você verificou.

## 2. Arquivos do jogo

Você precisa possuir sua própria cópia legítima de **Gravity Rush Remastered** para PS4, já preparada e descompactada por meios autorizados. O port testa primariamente o título **CUSA01113 v01.00**.

Nenhum arquivo `eboot.bin`, pacote `.pkg`, firmware, chave, arquivo de licença PSN ou save é oferecido. Na página **Jogo**, escolha sua pasta original que contém os arquivos do jogo. Não publique essa pasta nem anexe seus arquivos aos issues.

## 3. Jogar e configurar

Execute **GravityPort Launcher.exe** para abrir a interface nativa, selecione o diretório do jogo e clique em **Jogar**. Para iniciar diretamente com as configurações salvas, use **GravityPort.exe**.

Na página **Vídeo**, ajuste:
- **Anti-aliasing:** TAA, FSR 3.1, ou FSR 4 v07 Vulkan (experimental).
- **FSR 4:** nesta release, somente Quality para saída 1920 × 1080 possui modelos de shaders incluídos. A correção de contraste e gama sRGB/linear está no runtime.
- **FPS:** início conservador em **60 FPS** de apresentação, podendo selecionar 120 FPS. O relógio/VBlank emulado do jogo permanece em 60 Hz. Volte a 60 se a física, animação ou resposta dos comandos apresentar problemas.
- **DLSS:** a integração Vulkan NVIDIA existe no código e foi testada localmente, mas o **ZIP público não contém** `nvngx_dlss.dll` ou `gow3_dlss.dll`. A opção só aparece com essas dependências instaladas de maneira legítima, respeitando as licenças NVIDIA e os respectivos requisitos.

Em **Controles**, confira seu gamepad SDL3, analógicos e gatilhos. Existem mapeamentos XInput opcionais de giroscópio e touchpad simulados, úteis quando o controle não tem esses sensores. Use o testador de controle para diagnosticar zonas mortas. Isso não altera os controles físicos do jogo.

## 4. Saves, atualizações e segurança

O launcher guarda suas preferências em `%APPDATA%\gravityport-launcher\settings.json`. Faça backup dos saves antes de testar qualquer nova versão. Não instale por cima de diretórios com dados pessoais sem cópia de segurança.

**Atualizações são manuais nesta prévia.** Obtenha uma nova versão da página Releases, confira a assinatura SHA-256 e preserve suas configurações e saves. A atualização automática herdada não está habilitada para esse pacote.

## 5. Problemas frequentes

- **Jogo não abre:** confira Vulkan 1.3, drivers, versão CUSA01113 e caminho da pasta do jogo.
- **FSR 4 não aparece:** confirme que `fsr4_shaders` contém os modelos e o aviso de licença; em GPUs diferentes da RTX 5070 o recurso ainda não foi validado.
- **DLSS não aparece:** esperado no pacote público sem componentes NVIDIA.
- **120 FPS com física estranha:** escolha 60 FPS.
- **Pequenos movimentos do analógico não respondem:** use o testador SDL3 e compare os números LX/LY; ainda não temos correção universal de zona morta.
- **Títulos diferentes de Gravity Rush:** não suportados por este port.
- **Reportar bugs:** https://github.com/Frontlier/GravityPort/issues. Antes de enviar logs ou capturas, remova informações pessoais.

## 6. Código-fonte e licença

Código-fonte correspondente: tag `v0.4.0` em
https://github.com/Frontlier/GravityPort/tree/v0.4.0.
Inicialize submódulos para compilar: `git submodule update --init --recursive`.
A licença principal é GPL-2.0-or-later; licenças dos componentes e modelos de terceiros estão no ZIP.
