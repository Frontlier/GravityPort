# DLSS Frame Generation no GravityPort — plano de integração Vulkan

**Estado: em projeto. Nenhuma interpolação de quadros é executada atualmente.**
Qualquer indicador de "120 FPS" nos testes de DLSS SR/FSR4 se refere
ao FPS APRESENTADO medido pelo runtime, não a frames gerados por DLSS-G.

## Caminho de implementação escolhido

A GeForce RTX 5070 suporta DLSS Frame Generation e o SDK oficial NVIDIA
310.9.16 inclui `nvsdk_ngx_helpers_dlssg_vk.h`, com funções como
`NGX_VK_CREATE_DLSSG` e `NGX_VK_EVALUATE_DLSSG`, que recebem
backbuffer, depth, motion vectors, imagem HUD-less, máscara/UI e buffers
de saída interpolado/real. A integração recomendada para Vulkan é
**NVIDIA Streamline 2.14.16** e interposer Vulkan (DLSS-G 2x).
Vulkan NÃO é anunciado como suporte à geração multi-frame dinâmica
3x/4x da linha RTX 50 no guia de integração do Streamline,
que documenta essa capacidade para D3D12.

Referências de implementação:
- https://github.com/NVIDIA-RTX/Streamline
- https://github.com/NVIDIA-RTX/Streamline/blob/main/docs/ProgrammingGuideDLSS_G.md
- https://github.com/NVIDIA/DLSS/tree/main/include
- https://github.com/eFMann/shadPS4-Bloodborne-DLSS-FSR
  (especialmente vk_bb_frame_gen.cpp, vk_platform.cpp, vk_swapchain.cpp)

## Fluxo de quadros do GravityPort que precisa mudar

Código afetado (branch experimental, ainda não portado):

1. `gpu/shadps4/video_core/renderer_vulkan/vk_instance.cpp`:
   iniciar interposer antes de criar VkInstance/VkDevice,
   enumerar extensões/requirements e não quebrar DLSS SR já funcional.
2. `gpu/shadps4/video_core/renderer_vulkan/vk_temporal_upscaler.cpp`:
   capturar cor sem HUD, frame real com HUD, profundidade e vetores de
   movimento, com escala e jitter corretos. O código já dispõe dessas
   imagens em `slot.pre_hud`/`slot.composed` e `motion_image`, mas
   precisa garantir o tempo de vida e as layouts Vulkan apropriadas.
3. `gpu/shadps4/video_core/renderer_vulkan/vk_swapchain.cpp` e
   `vk_presenter.cpp`: inserir os frames interpolados na cadência de
   apresentação, com acquire/present, semaphores, frame identifiers,
   dimensionamento da swapchain e janela. Uma alteração aqui sem
   sincronização pode causar tela preta, crash ou quadros duplicados.
4. `gpu/shim/gow3_settings.cpp`, overlay e launcher:
   seletor `Off / DLSS Frame Generation 2x` apenas depois do teste
   real com o SDK. Desabilitar em GPU incompatível, fullscreen não
   suportado, vídeo/cutscene e bugs de Vulkan.
5. Reflex/latência: evitar aumentar fila de frames e medir resposta a
   comandos; gerador de quadros não acelera a física do PS4.

## Critérios de aceite

- Inicialização real de Streamline DLSSG com recurso suportado (não
  basta existir DLL).
- Vulkan valida layout de recursos, máscaras e barriers.
- Quadro interpolado distinto, entre duas imagens reais, sem duplicação
  artificial de HUD ou descompasso de áudio.
- Com 60 reais de base, medir ~120 exibidos no monitor, porém tempo de
  simulação continua idêntico. Monitor 144Hz permite ajustar a cadência.
- Com 120 reais de base, testar se FG acrescenta benefício prático
  (pode ser pouco num monitor 144Hz e até piorar latência).
- Física da Kat, mudança de gravidade, câmera, cutscenes e controles Xbox
  e DualSense, sem stutter no começo do framegen.
- Botão desativado até que todos os requisitos sejam cumpridos.
- A integração do SDK NVIDIA exige revisão de licença antes de release.

## Entrega desta etapa

DLSS **Super Resolution** e o FSR4 v07 **upscaling** estão em laboratório.
O **DLSS Frame Generation** ainda não foi implementado, e não deve ser
confundido com 120 FPS de apresentação direta. A etapa seguinte será
criar o Vulkan Streamline adapter, compilar, instrumentar e realizar
testes A/B com usuário.


## Alternativa disponível imediatamente: NVIDIA Smooth Motion para Vulkan

**Não é DLSS Frame Generation/Streamline.** É um gerador de quadros
por IA no próprio driver NVIDIA, compatível com DirectX 11, DirectX 12
e **Vulkan**, inclusive GeForce RTX série 50 (como a RTX 5070).
A NVIDIA confirma que pode ser usado junto de DLSS Super Resolution
e outras técnicas de upscale.

Fonte oficial NVIDIA: https://nvidia.custhelp.com/app/answers/detail/a_id/5621

Como testar no Frontlier sem alterar o código do GravityPort:

1. Abra o **NVIDIA App** e vá em **Gráficos > Configurações do programa**.
2. Adicione o EXE que realmente renderiza o jogo:
   `Documents/GravityPort/out/GravityPort Graphics Lab/bin/gravityrush-runtime.exe`,
   NÃO o executável visual `GravityPort Launcher.exe`.
3. Em **Configurações do driver**, ative **Smooth Motion**.
4. Reinicie o jogo. Para a experiência no monitor de 144Hz, compare
   o modo de 60 FPS reais (ideal para testar 120 gerados) com o modo
   já existente de 120 FPS reais.
5. Verifique contador do driver e captura visual; o contador do GravityPort
   continua mostrando os FPS do runtime, não necessariamente os frames
   gerados pelo driver. Meça latência e qualidade durante mudança de
   gravidade e câmera.
6. Desative Smooth Motion na NVIDIA App se houver artefatos, latência
   elevada ou duplicação do HUD.

Não existe um toggle funcional integrado para essa opção no GravityPort:
o driver decide a interpolação. Ativar Smooth Motion no NVIDIA App
**não completa a tarefa de portar DLSSG via Streamline**, mas oferece
geração de quadros NVIDIA para Vulkan enquanto desenvolvemos o
plugin verdadeiro.
