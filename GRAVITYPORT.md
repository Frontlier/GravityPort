# GravityPort — implementação e estado técnico (v0.4.0)

O GravityPort é um fork comunitário do [Gravity Rush PC Native Port](https://github.com/LucaPazienza/gravityrush_pc), inicialmente baseado no upstream **v0.1.8** e posteriormente ampliado. O histórico Git, as licenças e a atribuição aos autores originais foram mantidos. O objetivo aqui é aprimorar **Gravity Rush Remastered**, não criar um emulador PS4 genérico.

## Recursos com implementação confirmada

| Área | GravityPort v0.4.0 | Escopo da validação |
|---|---|---|
| Launcher Windows | Python/Tkinter compilado como aplicativo nativo, menus e pt-BR | Interface e empacotamento Windows testados |
| Diagnóstico | Logs de FPS/frametime, p99, cache de shaders, GPU, save e controle | Testes automatizados e UI |
| Controle Xbox | SDL3/XInput, botões e mapeamentos, giroscópio simulado opcional com L3 + analógico direito e gesto de touchpad por View + D-pad direito | Testes de código; sensibilidade/zonas mortas exigem comparação com controle real |
| 60/120 FPS | Configuração persistente de limite de apresentação, mantendo VBlank do convidado a 60 Hz | Logs A/B e partidas do usuário; **não** significa 120 FPS de física |
| Áudio/menus/saves | Base original preservada; backups e restauração protegidos | Campanha já jogável segundo upstream; sem novo QA integral nesta versão |
| FSR 3.1 | Temporal upscaling Vulkan presente | Base original |
| DLSS SR | NGX no Vulkan, modos DLAA/Quality/Balanced/Performance; timeout de inicialização adaptativo de 25 s quando instalado e selecionado | **Funcionando localmente** na RTX 5070 com DLL NVIDIA assinada; não incluída na release pública |
| FSR 4 v07 | Modelo Vulkan INT8 de comunidade, **Quality 1080p**; sRGB de entrada decodificado para linear float e saída recodificada antes de compor o HUD | **Funcionando localmente**; o usuário confirmou a correção visual e foram observados 120 FPS apresentados |
| DLSS-G / Streamline | Carregamento experimental assinado, teste de GPU/driver e inicialização Vulkan | **Não há interpolação funcional ou quadros gerados** |
| Pacote público | Windows ZIP portátil, licença, versão, manifestos, hashes SHA-256 | Sujeito a teste e limitações descritas no release |

### O que não foi concluído

- **DLSS Frame Generation** de verdade: ainda faltam tagging de profundidade/movimento/HUD, Vulkan swapchain, Reflex, sincronização, tokens por frame e medição dos quadros gerados.
- Troféus do PlayStation, multiplayer/PSN e serviços online.
- Testes de longa duração em múltiplas GPUs, todas as resoluções e campanha completa para esta revisão.
- Garantia de física/animação correta com cap de 120 FPS; a lógica convidada continua em 60 Hz.
- Empacotamento público das DLLs NVIDIA ou FrameGen proprietário, sem análise de licença.
- Modelos FSR 4 Native AA, Balanced, Performance ou 1440p/4K para o SDK v07 disponível: **não instalados** na prévia.

## Arquitetura resumida

O jogo original executa código x86-64 preparado em runtime nativo. As funções PS4 são implementadas sob `src/` e a GPU utiliza a arquitetura do projeto shadPS4 com Vulkan em `gpu/`. O launcher `launcher/gravityrush_launcher.py` com `launcher/launcher_ui.py` coordena configurações, controle, backups, preparação e execução. Não é renderização via streaming de vídeo nem um navegador.

O FSR 4 é acionado no upscaler dedicado de Gravity Rush no caminho corrigido `vk_temporal_upscaler.cpp`. Para a cena SDR de upscaling, o novo pipeline faz cópia byte a byte de UNORM→SRGB, blit SRGB→RGBA16F linear, processamento FSR 4 e blit de RGBA16F→SRGB, finalizando com composição do HUD. A conversão não é aplicada ao DLSS.

## Versão pública e variantes

O aplicativo de desenvolvimento local do Frontlier contém DLLs NGX assinadas da NVIDIA, usadas nos testes aprovados. A **release pública** é **deliberadamente diferente**: não inclui componentes proprietários NGX/Streamline, arquivos do jogo ou saves pessoais. DLSS Super Resolution aparece apenas quando seus componentes opcionais forem instalados localmente; não constitui promessa de que essa DLL possa ser redistribuída sob GPL.

A prévia pública inclui FSR 3.1 e o modelo **FSR4 v07 Quality/1080p** com aviso de origem/licença do modelo. Trata-se da porta experimental comunitária para Vulkan, não do AMD FSR 4.1.1 oficial, que não é equivalente. O limite conservador inicial no download público é **60 FPS**, ajustável em Vídeo para 120 FPS.

## Evidências e qualidade

- Build Windows com Clang/MSYS2, teste PyInstaller nativo, smoke tests que executam o jogo a partir de instalação separada, testes Python e GitHub Actions.
- A correção FSR4 foi testada com o modelo Quality real, sem fallback para FSR 3.1; mesmo pacote verificado com DLSS NGX.
- O usuário forneceu captura de cores incorretas e confirmou a correção visual em gameplay.
- Em registros estáveis foram observados cerca de **120 FPS apresentados**, 8,3 ms/frame. São medições locais específicas; não se devem extrapolar para todos os dispositivos/cenas.
- A zona morta de pequenos movimentos do analógico esquerdo foi investigada; não houve alteração de código do SDL3/analógico entre os pacotes investigados. Diagnóstico físico ainda recomendado.

## Códigos, dados e contribuições

A origem do software e a autoria dos colaboradores constam em [GRAVITYPORT-CREDITS.md](docs/GRAVITYPORT-CREDITS.md) e no histórico Git. O fork preserva a GPL-2.0-or-later; módulos e submódulos têm avisos adicionais. Arquivos de jogos, console keys, saves, cache e DLLs NVIDIA não pertencem ao repositório nem ao pacote público.

Para executar, leia [INSTALACAO.md](docs/INSTALACAO.md). Para reproduzir o empacotamento, leia [PUBLIC-RELEASE.md](docs/PUBLIC-RELEASE.md). Para histórico por etapa, consulte [CHANGELOG-GRAVITYPORT.md](CHANGELOG-GRAVITYPORT.md).
