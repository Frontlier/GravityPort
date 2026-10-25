# GravityPort — política de release público v0.4.0

**Distribuição adicional:** `GravityPort-0.4.0-Setup.exe` e `GravityPort-0.4.0-Setup.exe.sha256` fornecem um instalador Inno Setup 6 para o **mesmo payload do ZIP portátil original**. A compilação do instalador verifica o hash do ZIP, extrai os arquivos em uma pasta limpa, compara os 1.367 hashes do manifesto e recusa conteúdo comercial/NGX. O installer instala por usuário (`PrivilegesRequired=lowest`), cria atalhos, opcionalmente seleciona a pasta do jogo e preserva as preferências/saves na atualização e na desinstalação. Código: [GravityPort-Installer.iss](../packaging/windows/GravityPort-Installer.iss) e [build_windows_installer.ps1](../tools/build_windows_installer.ps1).

A opção do instalador **não altera o runtime** da tag v0.4.0 nem inclui dados comerciais do jogo. Os fontes do instalador foram adicionados ao repositório após a tag v0.4.0 e permanecem públicos para auditoria; consultar o commit correspondente na branch principal. Nenhum instalador é um emulador PS4 universal.



## O que o ZIP contém

- Gravidade Rush native Windows runtime baseado no port upstream, executáveis compilados e as DLLs livres necessárias (MSYS2 CLANG64/SDL3/FFmpeg, etc.).
- GravityPort Launcher nativo em Windows (PyInstaller) e GravityPort.exe para jogar diretamente.
- Fontes/ícone/fundo geométrico do launcher, scripts de preparação autorizados, patches e documentação (sem jogo).
- **FSR4 v07 Vulkan** Quality 1080p: shaders SPIR-V, modelos compilados, manifesto hash e aviso MIT de atribuição em `fsr4_shaders/`.
- FSR 3.1, TAA, FXAA e controle 60/120 FPS (60 FPS padrão conservador para download público).
- Licença GPL-2.0-or-later e avisos/licenças das bibliotecas compiladas.
- `MANIFEST-SHA256.json` e arquivo externo de SHA256 para o ZIP.

## O que ele NÃO contém

- **Nenhuma DLL NVIDIA NGX/Streamline**, incluindo `nvngx_dlss.dll`, `nvngx_dlssg.dll`, `gow3_dlss.dll` e `sl.*.dll`. O DLSS SR funciona em builds locais com os componentes oficiais devidamente licenciados, mas não se presume permissão universal para redistribuição conjunta com software GPL.
- Qualquer `eboot.bin`, `.pkg`, `.psarc`, `.prx`, `sce_sys`, `sce_module`, licença PSN, chave de console, firmware, jogo, save, log de usuário, configuração pessoal, cache de shaders gerado ou mod privado.
- O projeto experimental DLSS Frame Generation pronto para uso; não está funcional.
- Arquivos binários cujo direito de redistribuição não tenha sido identificado.

O pacote foi preparado a partir de uma compilação validada no Frontlier e do código da tag. Os itens de terceiros conservam seus avisos; versões de jogo e ferramentas oficiais são responsabilidade dos usuários.

## Licenciamento

Base GPL-2.0-or-later. Código MIT/FFmpeg/SDL3/LibAtrac9/FSR4 e demais dependências preservam suas condições. O modelo FSR4 v07 é uma adaptação comunitária derivada do ecossistema AMD/Q2RTX sob o aviso de modelo distribuído; **não é** AMD FSR 4.1.1 oficial. O pacote NÃO concede licença para redistribuir jogos da Sony, SDKs da NVIDIA ou recursos PSN.

## Processo reproduzível

1. Executar QA de código no commit da versão, verificar licenças e varrer histórico por segredos/dumps.
2. No Windows, preparar MSYS2 CLANG64, Python 3.13, PyInstaller, SDL3 e os executáveis compilados. O script de release usa uma compilação nativa **já validada** e registrada pelo hash SHA-256.
3. Executar:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File tools\build_public_release.ps1 -MainRoot "C:\Users\Valmir\Documents\GravityPort"
   ```
4. Validar os flags de compilação e a execução do launcher e do FSR4 sem bibliotecas NVIDIA. Confirmar que a árvore do ZIP NÃO contém dados do jogo, usuário ou DLLs NGX.
5. Publicar o tag `v0.4.0` com o código-fonte correspondente, o ZIP Windows e seu `.sha256`. Marcar a versão como **pré-release**.
6. Não prometer assinatura digital, 120 FPS de física ou DLC/PSN/troféus.

O release `v0.4.0` é manual, não ativa atualização automática. Questões legais ou pedidos de retirada de conteúdo deverão ser revisados pela pessoa mantenedora do repositório.
