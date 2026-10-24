# GravityPort - Laboratório de 120 FPS (experimental)

Data: 24 de outubro de 2026.
Branch: `feature/high-refresh-120-lab`.
Situação: teste automatizado A/B concluído; jogabilidade e física ainda não validadas.

## Hardware e dados verificados na máquina Frontlier

- CPU Intel Core i7-13700K; GPU NVIDIA GeForce RTX 5070.
- Monitor 27G2G4 em 1920x1080, 144 Hz (confirmado pelo SDL3).
- Configuração observada na sessão real: `engine_fps=60`, `vsync=1`,
  e `fps_limit` alterado dentro do jogo de 60 para 120.
- O log mostra `VideoOut: vblank 60 Hz, frame limit 120 FPS`.
- Na medição de 112 intervalos do log: média de FPS após aquecimento
  aproximadamente 117 e mediana 120; frametime p99 recente de ~10 ms.
- Há picos de compilação de shaders no carregamento e em cenas novas.
- **FPS apresentados não comprovam quadros distintos nem física correta**.
  Não há garantia de que 120 FPS seja benefício em toda a campanha.

## Erro identificado no port original

O menu oferece `engine_fps=120` e `240`, mas o arquivo de patches
`patches/CUSA01113.xml` NÃO contém `Frame Rate Patch - 120 FPS` ou
`Frame Rate Patch - 240 FPS`. Escolher esses valores causava erro
no preparador. O fork agora retorna a 60 FPS do motor com aviso
em vez de tentar aplicar um patch inexistente.

## Experimento preferível: mais apresentações, VBlank conservador

- `stable60`: guest VBlank=60, limite de apresentação 60.
- `probe120`: guest VBlank=60, limite de apresentação 120.
  Essa combinação já apareceu no log do usuário, com ~120 FPS.
- `probe_vblank120`: guest VBlank=120, limite de apresentação 120.
  **Mais arriscado:** pode acelerar física, animações, cutscenes e input.
  Não é modo padrão nem melhoria demonstrada.

A interface nativa tem uma opção **120 FPS experimental (uma execução)**
que configura o segundo modo e se desmarca ANTES de iniciar o jogo.
Ela não altera os arquivos do PS4 nem ativa patches desconhecidos.

## Como medir quando o jogo estiver fechado

O benchmark nunca fecha uma partida já aberta e cria seus
próprios diretórios de cache, configuração, logs e salvamentos em
`out/fps-lab/<modo>/`. Não copia dados comerciais nem saves do usuário.

No PowerShell, em sua cópia local de desenvolvimento:

    cd "$env:USERPROFILE\Documents\GravityPort"
    $env:MSYS2_ROOT='C:\msys64'
    $env:PATH='C:\msys64\clang64\bin;'+$env:PATH
    $game = '<pasta da cópia extraída do Gravity Rush>'
    C:\msys64\clang64\bin\python.exe tools\fps_lab.py --mode stable60 --seconds 45 --game-dir $game
    C:\msys64\clang64\bin\python.exe tools\fps_lab.py --mode probe120 --seconds 45 --game-dir $game --experimental-confirmed

Somente após comparar e validar a simulação, opcionalmente:

    C:\msys64\clang64\bin\python.exe tools\fps_lab.py --mode probe_vblank120 --seconds 45 --game-dir $game --experimental-confirmed

Os resultados ficam em `out/fps-lab/<modo>/result.json` e
`benchmark.log`. O analisador histórico (não A/B) é
`tools/report_existing_fps.py`.

## Critérios para aceitar 120 FPS

- Quadros visualmente distintos, sem apenas repetir imagens.
- Tempo de deslocamento, câmera e gravidade equivalentes a 60 FPS.
- Física, animação, combate, áudio e cutscenes sem aceleração.
- Frametime p95/p99 e spikes comparados na mesma cena, várias vezes.
- Sem regressões em shaders, saves, texturas e entrada.
- Gameplay completo antes de habilitar este modo por padrão.

## Limitações atuais

- A sessão inicial do usuário foi preservada e não interrompida.
- Depois que ela foi encerrada, executamos A/B com processos separados,
  configurações e caches isolados (34 segundos cada), no fluxo inicial/demo.
- O código de menu interno C++ precisa ser recompilado do fork
  para atualizar a interface in-game; o novo laboratório Python
  pode ser testado antes dessa recompilação.
- Branch experimental não deve ser mesclada ao main até o QA.
- Fontes derivadas do Gravity Rush PC, GPL-2.0-or-later, com
  créditos preservados e sem distribuição de conteúdo do jogo.


## Resultados A/B obtidos — Frontlier, 24/10/2026

Cada perfil rodou por ~34 segundos usando o mesmo executável, mesmo
jogo CUSA01113, resolução 1920×1080 e VBlank de 60 Hz.
Os arquivos de jogo foram lidos, sem serem copiados; as pastas de
cache/saves/logs ficaram separadas em out/fps-lab.

| Medida | stable60 | probe120 |
|---|---:|---:|
| FPS médio após aquecimento (4 intervalos) | 60,0 | 120,0 |
| FPS mínimo/máximo após aquecimento | 60/60 | 120/120 |
| p99 do último intervalo (ms) | 18,07 | 9,65 |
| Maior frametime, com carregamento (ms) | 266,1 | 254,2 |
| Compilações de shaders registradas | 82 | 82 |
| Tempo total de compilação dos shaders | 62,9 ms | 62,7 ms |
| VBlank PS4 | 60 Hz | 60 Hz |
| Falha do processo | Não | Não |

A relação registrada entre médias de FPS apresentados foi **2,0×**.
O último p99 melhorou 8,42 ms, porém esse cálculo não substitui
estatística de toda a campanha, nem confirma frames distintos.

Fontes locais, não versionadas no Git:

- `out/fps-lab/stable60/result.json`
- `out/fps-lab/probe120/result.json`
- `out/fps-lab/comparison_present60_120.json`
- `out/fps-lab/observed_present120_guest_vblank60.json` (sessão real,
  sem controle de cena; não confundir com benchmark).

**Importante:** a própria documentação do renderizador alerta que
acima de 120 FPS o ritmo de movimento pode quebrar. Por isso, o
objetivo inicial é 120, não 144/240 FPS, mesmo o monitor sendo 144 Hz.

## Aplicativo experimental Windows já preparado

O binário Tkinter/PyInstaller **não altera a instalação estável**:

`Documents/GravityPort/out/GravityPort 120Hz Lab/GravityPort Launcher.exe`

O perfil do laboratório usa:
- `%APPDATA%/gravityport-120hz-lab/settings.json` (separado).
- `Documents/GravityPort/out/GravityPort 120Hz Lab/user`
  (saves e cache do laboratório, separados do usuário estável).
- O mesmo diretório de arquivos comerciais do jogo é apenas lido.
- Preset 120 FPS vem **desativado por padrão**. Ative na tela
  **Avançado → Desempenho**, depois clique Jogar; após uma execução
  o toggle volta automaticamente a desligado.
- Para retornar ao port estável, use o atalho
  `GravityPort - Abrir.lnk`, sem utilizar o executável de laboratório.

Não há release público nem alteração em `main` até a aprovação
dos controles, física, cutscenes e saves em gameplay real.
