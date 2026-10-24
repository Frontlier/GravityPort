# GravityPort v0.2.0 — launcher nativo Windows (24/10/2026)

## O que ficou pronto

- Aplicação **Tkinter/Pillow de verdade**, não navegador nem webview.
- Tema escuro GravityPort (azul-petróleo/verde-água), animações nativas
  existentes e imagem de fundo original, sem imagens do jogo.
- Tela inicial em português com status CUSA01113, último save, FPS e p99
  **registrados no último log**, resolução e perfil de controle.
- Páginas de Jogo, Vídeo, Controles, Avançado e Logs preservadas.
- Traduções pt-BR adicionais, com fallback para textos ainda não traduzidos;
  os idiomas upstream permanecem disponíveis.
- Central SDL3 em janela Tkinter separada: detecta gamepads, botões,
  analógicos, gatilhos, touchpads e disponibilidade dos sensores.
  Não altera dados do jogo nem remapeamentos do runtime.
- Correções XInput, controle de touchpad e gyro virtual do commit anterior.
- Atualização automática de motor externo desativada no fork privado.
- Configurações separadas em %APPDATA%/gravityport-launcher/settings.json.
- Imagem de fundo e ícone próprios gerados por tools/render_gravityport_assets.py.

## Testes confirmados

- 7 testes Python de traduções, rotas, defaults, métricas e enums SDL.
- Janela nativa Tkinter aberta em Dashboard, Controles e Vídeo em português,
  com screenshots dentro de out/.
- Testador SDL3 iniciou; nenhum gamepad estava conectado no momento do teste.
- Janela do testador inspecionada por captura.
- PyInstaller gerou out/GravityPort Preview/GravityPort Launcher.exe.
- Teste do EXE confirmou janela nativa em execução e estável após 3 segundos.

## Como testar no Frontlier

Abra no Windows Explorer:

    Documents/GravityPort/out/GravityPort Preview/GravityPort Launcher.exe

Este diretório é uma prévia local, não um instalador público.
A pasta estável antiga permanece utilizável. Saves foram copiados,
não movidos, para Documents/GravityPort/user/savedata (ignorado no Git).

Em Controles, clique em Testar controle, conecte Xbox ou DualSense e
teste L3, analógico direito, View, direcionais, gatilhos e sensores.
O teste automatizado sem gamepad não comprova hardware específico.

Para iniciar jogo pelo launcher novo, feche a instalação anterior,
valide o caminho do jogo e clique em Jogar. Esse fluxo completo precisa
de QA próprio; não classificaremos a versão como final antes disso.

## Limites e autoria

- Código derivado do Gravity Rush PC por LucaPazienza v0.1.8, mantendo
  histórico, LICENSE e avisos. O renderer Vulkan depende do shadPS4.
- Nenhum eboot.bin, .pkg, .prx, .psarc, saves ou credenciais foi enviado
  ao repositório privado ou incluído no pacote preview.
- Não reescrevemos uma engine PS4 universal; estamos trabalhando
  somente no Gravity Rush.
- O pacote preview inclui DLLs de terceiros. Antes de qualquer
  release externo é necessária revisão de licenças, dependências e
  testes de instalação em outro computador.
- Baseline de 60 FPS/16,7ms; mais FPS podem alterar física/animações.

## Ordem das próximas tarefas

1. QA real do botão Jogar pelo EXE, com menu, saves e áudio.
2. Validar controle físico e hotplug, giroscópio/touchpad.
3. Recompilar o core do fork a partir dos submódulos pinados.
4. Medir FPS/p95/p99 no gameplay e reduzir engasgos.
5. Traduzir o restante da interface para pt-BR.
6. Empacotamento de licenças e instalador Windows com rollback.
7. Campanha integral e estabilidade antes da versão 1.0.

## Empacotamento e validação adicionais

- Programa principal: out/GravityPort Preview/GravityPort Launcher.exe.
- Acesso direto: out/GravityPort Preview/GravityPort.exe, compilado em C,
  mantém a execução até o jogo encerrar (derivado do helper upstream).
- Teste sem gameplay via EXE e o pipeline de imports terminou sem exceção.
  Permanecem 50 funções da API do PS4 não implementadas na verificação
  estática, majoritariamente serviços externos/online.
- Durante o teste foi encontrado e corrigido um erro do upstream em
  scripts/patches.py: interseção inválida de set com tuple. Há regressões
  para IDs compatíveis, não compatíveis e XML inválido.
- Prévia local inclui cópias de 182 arquivos de aviso/licença, mas
  release externo ainda depende de auditoria completa.
- CI de código-fonte para Windows definida em .github/workflows.

## Publicações e segurança do GitHub

- Repositório privado Frontlier/GravityPort, sem dados de jogo.
- O workflow de origem chamado Build and release (Windows) foi
  desativado, porque publicava pacotes automaticamente em tags.
- Dois jobs herdados que estavam iniciados foram cancelados.
- O GitHub Actions GravityPort - Source QA permanece ativo.
- Nenhuma release pública ou binário foi enviado. Só o código privado
  e a tag de desenvolvimento estão versionados.
- O empacotamento de releases será reintroduzido somente após QA da
  campanha e revisão das licenças/artefatos.
