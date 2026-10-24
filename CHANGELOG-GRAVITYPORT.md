# GravityPort — histórico de melhorias

## 0.1.0-lab — 24/10/2026

- Repositório privado de desenvolvimento criado sem perder o histórico do upstream.
- Importadas as alterações locais já testadas: fallback do controle XInput,
  controles de touchpad, opção de simulação de gyro e correção da métrica FPS.
- Adicionado teste para controle virtual Xbox e testes do launcher.
- Preservadas como patch as alterações locais opcionais do submódulo FSR4.
- Dumps e saves nunca foram adicionados a este repositório.

## Próxima entrega

- Interface nativa GravityPort para Windows, português brasileiro e
  diagnóstico de hardware/controle, preservando a lógica original.

## 0.2.0-native-preview — 24/10/2026

- Launcher nativo em português, com identidade visual GravityPort e tela inicial
  de diagnóstico (FPS histórico, p99, resolução, saves e controle).
- Preservadas as cinco páginas existentes do port e a lógica de runtime.
- Central SDL3 em Tkinter para testar botões, eixos e presença de sensores.
- Preferências isoladas da instalação original e atualizações privadas desativadas.
- Fundo geométrico/ícone original e empacotamento via PyInstaller.
- Testes de unidade e smoke test do aplicativo nativo.
- Release público e QA de gameplay ainda pendentes.

## 0.3.0-high-fps-lab (branch experimental, ainda nao mergeada)

- Diagnóstico de 60 FPS estáveis, monitor local 1080p a 144 Hz.
- Confirmado por log do usuário e por A/B isolado: apresentação perto de
  120 FPS com VBlank convidado de 60 Hz e cap de 120 FPS.
- Testes automatizados de 34 s: 60,0 vs 120,0 FPS após aquecimento;
  último p99 18,07 vs 9,65 ms. Isso não comprova física, animação nem
  quadros distintos e não é benchmark de campanha.
- Correção para opções inexistentes de engine FPS 120/240:
  fallback seguro para 60 FPS do motor sem quebrar patches.
- Toggle experimental no launcher nativo, para uma execução apenas;
  retorno automático a 60 FPS dentro do build separado de laboratório.
- Novo pacote Windows isolado "GravityPort 120Hz Lab", sem sobrescrever
  versão principal nem saves originais.
- Documentação, relatórios locais e regressões em tests/test_gravityport_highfps.py.
- Documentado em docs/HIGH_REFRESH_LAB.md. Aguardar validação manual
  antes de habilitar modo em main ou publicar release.


## 0.3.0 - 120 FPS no GravityPort principal - 24/10/2026

- Apos teste e aprovacao de gameplay pelo usuario, o limite de 120 FPS
  passa a ser selecionavel de forma permanente na pagina Video.
- O VBlank do PS4 continua em 60 Hz (nao e usado patch binario de
  120/240 FPS do motor, ausente neste CUSA01113).
- Configuracao padrao do instalador passa a 120 FPS, com escolha de
  60 FPS para compatibilidade ou preferencia.
- O menu interno agora informa o cap de apresentacao real (antes
  declarava incorretamente que o teto de 60 Hz da simulacao limitava
  todos os frames apresentados).
- Laboratorio e perfil experimental continuam isolados; na versao
  principal nao existe toggle de execucao unica.
- Instalacao principal Windows atualizada sem apagar os saves, mods
  ou as preferencias de controle; instalacao anterior arquivada.
- Provas A/B, testes automatizados e roteiros tecnicos em
  docs/HIGH_REFRESH_LAB.md. Usar 60 FPS se houver regressao.

## DLSS Super Resolution no principal (instalacao local, 24/10/2026)

- DLSS Super Resolution aprovado pelo jogador no Graphics Lab; promovido ao
  aplicativo nativo principal do Frontlier, com DLSS instalado localmente.
- Instala apenas a ponte Vulkan criada com o SDK NVIDIA e a DLL oficial NGX
  assinada; nao copia modelos FSR4 experimentais nem arquivos do jogo.
- Quando o usuario escolhe DLSS e a DLL esta instalada, o launcher reserva
  ate 25 segundos para inicializar o NGX; os demais modos preservam o comportamento anterior.
- Mantem 120 FPS apresentados / VBlank 60 Hz do PS4 e as configuracoes de
  controle, saves, sombras e tela cheia existentes.
- DLAA (resolucao nativa) no primeiro teste; DLSS Quality pode ser escolhido
  separadamente em Video. O DLSS Frame Generation ainda NAO foi implementado.
- Inclui suite de regressao, smoke test nativo com perfil isolado,
  copia de rollback e orientacoes em docs/MAIN_DLSS_LOCAL.md.
- Nenhuma DLL proprietaria ou arquivo do jogo publicado no GitHub.
