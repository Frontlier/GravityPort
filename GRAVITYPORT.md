# GravityPort — desenvolvimento privado de Gravity Rush PC

## Projeto

GravityPort é nosso **fork de desenvolvimento do Gravity Rush Remastered para Windows**.
A base original e seu histórico são preservados:
[Gravity Rush PC, por LucaPazienza](https://github.com/LucaPazienza/gravityrush_pc),
versão original de referência `v0.1.8`, GPL-2.0-or-later.

O repositório privado não é uma declaração de autoria do port original.
Mantemos os direitos e os avisos aplicáveis aos contribuidores e bibliotecas
e só reivindicamos as melhorias de código efetivamente criadas neste trabalho.

**Escopo atual: apenas Gravity Rush Remastered CUSA01113 v01.00.**
Não há intenção de iniciar outro título antes de estabilizar, testar e
empacotar Gravity Rush.

## Primeira etapa: base preservada e controle Xbox

- FPS exibidos agora derivam das apresentações de frames do runtime.
- Unidade `ms/frame` separada de FPS.
- Controle XInput sem sensor pode simular giroscópio por `L3 + analógico direito`,
  opcional e sem interferência com o uso normal do analógico.
- Controle sem touchpad pode simular lado direito por `View + direcional direito`.
- Launcher oferece opções para habilitar esses fallbacks.
- Testes automatizados de mapeamento de botões, indicador e entrada virtual.

## Etapa 0.2: launcher nativo do Windows (implementada em prévia)

Modernizar o Tkinter/Pillow existente (sem navegador/web server):
navegação, identidade visual GravityPort, português brasileiro, área de
diagnóstico e indicadores de estabilidade. Preservar funções existentes:
controles, tradução, saves, mods, FSR/DLSS, resolução, atalhos, autoupdate.
Empacotar via PyInstaller depois de validar o comportamento da interface.

## Laboratório experimental de FPS

O trabalho de 120 FPS é mantido na branch `feature/high-refresh-120-lab`.
Leia [o laboratório de 120 FPS](docs/HIGH_REFRESH_LAB.md) para comparar
as medições locais, os riscos à física e o procedimento de rollback.
O build experimental não modifica a versão estável nem os saves.

## Especificação de qualidade

1. Boot e menu reproduzíveis em múltiplas execuções.
2. Controle Xbox, DualSense e teclado/mouse: todos os comandos necessários
   testados em gameplay, não somente em testes simulados.
3. Áudio, cutscenes, salvamento/restauração e estabilidade testados.
4. Frametime p95/p99 e spikes monitorados em cenas comparáveis.
5. Resoluções 1080p/1440p/4K validadas; não prometer FPS sem medição.
6. Launcher .exe e instalador Windows, com licenças e documentação.

## Código, dados e licenças

NÃO publicar `eboot.bin`, arquivos `.pkg`, `.psarc`, `.prx`, saves, chaves,
dados pessoais, caches de shaders ou backups do usuário.
O jogo original deve ser fornecido separadamente pelo usuário autorizado.
GPL-2.0-or-later, sem alterar os avisos de direitos de terceiros.
Submódulos mantêm suas licenças e commits originais.

### Submódulo FSR4 local

As alterações opcionais de profiling que já existiam no checkout local do
FSR-Vulkan foram preservadas como patch em
`patches/fsr4-local-profiling.patch` para evitar alterar a referência do
submódulo sem publicar um commit correspondente.
A aplicação é opcional via `tools/apply_fsr4_local_patch.py`; o jogo não
depende do profiling para rodar.

## Organização de repositórios

- `origin`: `https://github.com/Frontlier/GravityPort.git` (**privado**).
- `upstream`: `https://github.com/LucaPazienza/gravityrush_pc.git` (leitura).
- `main`: integração estável e validada; novas melhorias versionadas em
  commits separados para revisão. Não dar push ao upstream sem aprovação.

O fork é mantido como repositório separado; a cópia original já funcional em
`Documents/Gravity Rush PC Port/gravityrush_pc` não será sobrescrita.


## Laboratório de upscaling DLSS / FSR 4 (branch experimental)

O trabalho de upscaling NVIDIA DLSS Super Resolution e FSR 4 v07
Vulkan está isolado na branch `feature/dlss-fg-fsr4-vulkan`.
Em testes de boot/demo no Frontlier, os dois recursos iniciaram seus
processadores reais e registraram 120 FPS apresentados após aquecimento.
Ainda é necessário comparar a imagem em gameplay. A implementação
**não está habilitada no GravityPort principal**.

O gerador de quadros DLSS-G via Vulkan/Streamline **ainda não foi
implementado** e não deve ser confundido com DLSS Super Resolution.
A NVIDIA oferece o Smooth Motion no driver para títulos Vulkan como
solução provisória, mas é uma tecnologia diferente do DLSS-G.

Detalhes: `docs/GRAPHICS_LAB_DLSS_FSR4.md` e
`docs/DLSS_FRAMEGEN_VULKAN.md`. O aplicativo nativo local foi criado
separadamente em `out/GravityPort Graphics Lab` e precisa de DLLs
NVIDIA assinadas e modelos FSR4 locais que **não são versionados**.
