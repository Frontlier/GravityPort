# GravityPort - instalador Windows da v0.4.0

## Para quem quer apenas jogar

Na [release v0.4.0](https://github.com/Frontlier/GravityPort/releases/tag/v0.4.0), baixe **GravityPort-0.4.0-Setup.exe**. Voce nao precisa instalar Python, MSYS2, Inno Setup nem compilar codigo.

1. Execute o instalador no Windows 10/11 de 64 bits. A instalacao ocorre no perfil do usuario e **nao exige privilegios de administrador**. O programa ficara normalmente em `%LOCALAPPDATA%\Programs\GravityPort`.
2. Na etapa **Sua copia de Gravity Rush Remastered**, escolha opcionalmente sua pasta de jogo **ja descompactado** que contenha `eboot.bin` (por exemplo, `...\CUSA01113\Image0`). O jogo NAO vem no download. Se preferir, marque **Vou escolher depois** e selecione a pasta no launcher.
3. Conclua o assistente e marque **Abrir GravityPort agora**. Se escolheu uma pasta valida e ainda nao possuia preferencias do GravityPort, o caminho estara salvo. Caso contrario, abra **Jogo** e selecione a pasta. Clique em **Jogar**.
4. O Menu Iniciar recebe atalhos para **GravityPort** (configuracao) e **GravityPort - Jogar** (abrir o jogo diretamente). A criacao de atalho na area de trabalho e opcional.

**Nao e necessario copiar, mover ou importar o jogo para a pasta da instalacao.** Se nao encontrar `eboot.bin`, o assistente ajuda a selecionar a pasta correta.

## Versoes e compatibilidade

- Testado principalmente com **Gravity Rush Remastered PS4, CUSA01113 v01.00**, obtido legalmente e descompactado por meios autorizados.
- O port nao e um emulador PS4 generico. Exige uma GPU Vulkan 1.3 com drivers atualizados.
- O instalador entrega o mesmo runtime e modelos **FSR 4 v07 Vulkan Quality/1080p** do ZIP. FSR 3.1 tambem esta disponivel.
- **DLSS Super Resolution esta implementado no codigo**, mas o download publico NAO contem as DLLs NVIDIA necessarias. DLSS Frame Generation ainda nao gera quadros.
- **FPS:** limite inicial de 60 quadros apresentados; opcao 120 apos testar; VBlank do jogo continua em 60 Hz.
- O instalador **nao e assinado digitalmente**. Confira o SHA-256 publicado e nunca execute uma copia de procedencia desconhecida.

## Atualizar e desinstalar

Em novas versoes, execute o instalador atualizado no mesmo local. O caminho do jogo, mapeamento de controle e preferencias em `%APPDATA%\gravityport-launcher\settings.json` nao sao substituidos. O `gravityrush.ini` instalado **nao e sobrescrito** em atualizacoes.

Para desinstalar, abra **Configuracoes > Aplicativos > Aplicativos instalados > GravityPort > Desinstalar**. O desinstalador remove arquivos que o instalador colocou e seus atalhos, mas **preserva** configuracoes do perfil, saves, mods, caches e outros arquivos criados apos a instalacao. Assim, uma pasta com dados pessoais pode permanecer. Faca backup antes de apagar qualquer resto manualmente.

O ZIP portatil permanece no release para quem prefere nao instalar.

## Para desenvolvedores

O instalador tem codigo-fonte em [GravityPort-Installer.iss](../packaging/windows/GravityPort-Installer.iss) e [build_windows_installer.ps1](../tools/build_windows_installer.ps1). Sao necessarios Inno Setup 6, PowerShell, Python para verificacao e o **ZIP oficial v0.4.0 acompanhado do .sha256**.

O script verifica checksum de release, extrai o ZIP original em nova pasta limpa, confere cada item do manifesto de 1.367 arquivos e **bloqueia** arquivos comerciais do jogo, saves, chaves e DLLs NVIDIA. Ele nao reutiliza as pastas onde o game foi testado, pois o runtime pode criar binarios vinculados temporarios nelas.

Exemplo:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\build_windows_installer.ps1 -OriginalZip "D:\Downloads\GravityPort-0.4.0-Windows-portable.zip"
```

Saida: `out\installer-output\GravityPort-0.4.0-Setup.exe` e seu `.sha256`. Esses arquivos sao anexados a mesma release v0.4.0. O codigo de empacotamento foi adicionado publicamente apos a tag original v0.4.0, sem mudar o executavel/runtime contido nela.

Instalador criado com **Inno Setup 6**, copyright de Jordan Russell, Martijn Laan e demais contribuidores. O GravityPort permanece GPL-2.0-or-later, creditando o port original de LucaPazienza e as bibliotecas associadas.
