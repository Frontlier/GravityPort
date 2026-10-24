# GravityPort Graphics Lab — DLSS SR, FSR 4 v07 e Frame Generation

**Estado: laboratório isolado; NÃO publicado na main.**
Desenvolvido em 24/10/2026 no Frontlier.
Branch: `feature/dlss-fg-fsr4-vulkan`.

## Testes locais confirmados

| Tecnologia | Estado | Resultado inicial |
|---|---|---|
| FSR 3.1 | Estável na base | Fallback e referência |
| DLSS Super Resolution | **Funcionando em laboratório** | NGX 310.9.16 inicializa; criação real do recurso 1280x720 -> 1920x1080 e frames processados, 120 FPS apresentados após aquecimento |
| FSR 4 v07 Vulkan INT8 | **Funcionando em laboratório (experimental)** | Modelo `quality`, tier 1080, dispatch real após correção do caminho de Gravity Rush; ~120 FPS apresentados após aquecimento |
| DLSS Frame Generation | **NÃO IMPLEMENTADO** | Exige integração do Vulkan swapchain/presenter com API Streamline ou NGX DLSSG, HUD-less, depth/motion, Reflex e sincronização. Não mostrar botão falso no launcher |
| FSR 4.1.1 oficial AMD | **Não testado/não disponível como DX12 oficial** | Esta branch usa o caminho comunitário v07 Vulkan, não o SDK oficial AMD |

### Hardware / ambiente de teste
- NVIDIA GeForce RTX 5070 12 GB; driver 617.42.
- Monitor 1920x1080 a 144 Hz, cap de apresentação 120 FPS.
- VBlank de PS4 continua em 60 Hz para preservar o timing.
- Jogo de teste: CUSA01113, executável do usuário, sem upload ou cópia no Git.
- Resolução de jogo 1280x720; tela final 1920x1080.
- A inicialização NGX pode demorar. Em uma tentativa, o NGX não retornou
  antes de 8s e fez fallback; com 25s de espera **apenas no laboratório**,
  log reportou `DLSS: ready` e `DLSS: DLSS 1280x720 -> 1920x1080`.
- FSR4 v07 inicialmente falhou por dois defeitos específicos do caminho
  Gravity Rush. Correções: conversão explícita de UNORM8 para R16F
  na passagem FSR4, e seleção do modelo Quality ao invés do Native.
  Depois o log registrou `Upscaler: FSR 4 v07 INT8 quality model, 1080 tier, output 1920x1080`.
- Os dois tiveram ~120 FPS apresentados em amostras finais de 5 segundos,
  mas o primeiro intervalo registrou uma pausa grande de inicialização
  do modelo. Isto **não** é benchmark da campanha nem garante imagem
  correta ou ausência de glitches na câmera ou UI.

## Como abrir a versão de teste

Use o atalho **GravityPort - Laboratório DLSS e FSR4** dentro
de `Documents/GravityPort`. Este aplicativo tem perfil separado:
`%APPDATA%/gravityport-graphics-lab/settings.json`.
Os saves/cache de teste ficam em `Documents/GravityPort/out/graphics-lab/user`.
A instalação principal fica em `out/GravityPort Preview`; **não é alterada**.

No launcher: **Vídeo > Anti-aliasing**
- **DLSS Super Resolution**: selecione depois de confirmar que as DLLs
  NVIDIA assinadas estão na pasta `bin`. Modo Qualidade usa 720p->1080p.
- **FSR 4 v07 Vulkan (experimental)**: disponível apenas quando o modelo
  correspondente existe em `fsr4_shaders`. Neste momento **só Qualidade
  1080p** é distribuído dentro do laboratório.
- **FSR 3.1**: modo comparativo confiável e fallback.
- Não ative FPS "Unlimited" ao avaliar interpolação temporal;
  mantenha 120 apresentados e guest VBlank 60 Hz.

O launcher mantém DLSS Frame Generation desabilitado: ainda não é uma
opção tecnicamente funcional. Para aceitar geração de quadros, verificar
capacidade NGX DLSSG, inserir imagens de interpolação entre frames
reais no present loop e manter HUD desacoplado com frame pacing.

## Artefatos locais (não versionados)
- `out/sdk/NVIDIA-DLSS-v310.9.16`: headers, import lib e DLL, v310.9.16
  (NVIDIA, licença própria, DLL Authenticode válida).
- `out/sdk/Vulkan-Headers-Msvc`: cabeçalhos oficiais Vulkan Khronos.
- `out/dlss-bridge-v310.9.16/Release/gow3_dlss.dll`: ponte MSVC x64.
- `out/graphics-lab/fsr4_shaders`: 20 shaders/modelos v07 Quality 1080,
  licença incluída, origem GitHub FireBurn/Q2RTX commit
  `ae8d628fae208813172446d1e49ed94150b04658`.
- `out/graphics-lab/probes/dlss/result.json`
- `out/graphics-lab/probes/fsr4/result.json`
- `out/GravityPort Graphics Lab`: executável Windows experimental.

**Não copiar conteúdo do SDK, blobs FSR4 ou arquivos do jogo para o Git.
**A licença NVIDIA precisa ser revisada antes de qualquer distribuição
externa. Implementação comunitária FSR4 não deve ser apresentada como
suporte AMD oficial.**

## Pendências de qualidade

1. Comparar imagens de FSR3.1, DLSS SR e FSR4 v07 nas mesmas cenas,
   parado, em movimento, HUD/legendas, gravidade, efeitos e cenas escuras.
2. FSR4 recebe inicialmente cor 8-bit já tonemapped, convertida para
   float R16G16B16A16. É suficiente para o dispatch Vulkan mas **não é
   equivalente à entrada linear HDR ideal do FSR4**. Pode causar
   diferenças de gamma, cor ou detalhe. Melhorar o input de cena HDR.
3. Medir média/p95/p99 de frametime, uso VRAM e uso GPU em gameplay.
4. Testar warmup do NGX e do FSR4 sem pausas de ~10s na primeira partida.
5. Integrar DLSS Frame Generation 2x no Vulkan; vide
   `docs/DLSS_FRAMEGEN_VULKAN.md`.
6. Obter aprovação de QA antes de integrar/lançar no GravityPort principal.
