# GravityPort - FSR 4 v07: cor linear no Vulkan (Frontlier)

Status: correção de espaço de cor compilada, validada pelo usuário na RTX 5070.
Este é um aprimoramento do **upscaling FSR 4**, não de Frame Generation.

## Problema original

Na imagem fornecida, o céu ficou laranja fortemente saturado, o ambiente e
os personagens ficaram escuros. O HUD era desenhado normalmente. O modelo
FSR4 v07 em formato INT8 estava ativo e a apresentação atingia 120 FPS, mas
sua entrada estava incorreta.

O caminho Gravity Rush:
- gera a cena em ponto flutuante HDR;
- aplica o tonemapping original em R8G8B8A8 SRGB/UNORM;
- envia as cores já codificadas para a exibição diretamente ao modelo
  FSR4 v07, convertendo bits para R16G16B16A16_FLOAT via blit;
- recompõe o HUD sobre a imagem ampliada.

Isso não garante a linearização necessária: um blit de uma view UNORM
para float apenas preserva valores normalizados, não reverte a curva sRGB.
O FSR4 com flags HIGH_DYNAMIC_RANGE e AUTO_EXPOSURE pode reconstruir
sombras e luminância incorretamente. A saída ainda era tratada como se
já estivesse codificada para a tela, introduzindo mais erro.

## Correção

Somente quando FSR 4 está selecionado no caminho de upscaling da
Gravity Rush, o renderizador cria duas imagens de transferência SRGB:
- Entrada: copia sem transformação os bytes do tonemapped R8 para uma
  imagem SRGB, então faz `vkCmdBlitImage` de SRGB para RGBA16F.
  A conversão da GPU aplica EOTF de sRGB para valores RGB lineares.
- Saída: faz `vkCmdBlitImage` do output RGBA16F do FSR4 para SRGB
  (OETF), então cópia pura dos bytes de SRGB para o buffer UNORM que
  o compositor HUD e o apresentador esperam.
- Preserva motion vectors, depth, temporal jitter, sharpen e os 120 FPS.
- O DLSS continua em seu caminho original, sem mudança de imagem.
- O FSR4 em Native AA (entrada de cena HDR) não usa essa conversão,
  pois já recebe dados lineares antes do tonemapping.
- Recursos são recriados quando alternar entre FSR4 e DLSS/FSR3,
  inclusive se resolução e formato não mudarem.

## Build e teste

Código: `gpu/shadps4/video_core/renderer_vulkan/vk_temporal_upscaler.{cpp,h}`.
Cópia de desenvolvimento: Documents/GravityPort_FSR4_ColorFix, branch
`fix/fsr4-linear-colorspace`.

A compilação Windows CLANG64 concluiu com sucesso. O smoke test isolado
de 65s confirmou FSR4 v07 real, a nova conversão de cor, 60 Hz de VBlank
e picos sustentados de 120 FPS. A checagem `DEMO BEGIN` do harness não
passou porque abriu em tela de carregamento de save, não na demonstração
de uma partida nova. **A imagem final foi confirmada pelo usuário em
uma cena jogável.**

## Pacote

O FSR4 v07 só tem o modelo Quality/1080p instalado no Frontlier, não
se deve anunciar modos não instalados. O main mantém DLSS como opção
padrão, com FSR4 v07 Quality disponível no seletor Video.
Os modelos, SPIR-V e pesos ficam em `fsr4_shaders/` localmente,
fora do Git. Inclua `LICENSE-FSR4-v07.txt` e revise as licenças
provenientes do modelo antes de distribuir a aplicação.

A versão stable DLSS e os saves do usuário devem ser copiados
antes da promoção; nenhum save, controle ou configuração pessoal
deve ser substituído. O Graphics Lab permanece separado para testes.

Não prometer suporte a todos os jogos, GPUs ou espaços HDR. O teste
foi feito exclusivamente com a build de Gravity Rush da RTX 5070.
