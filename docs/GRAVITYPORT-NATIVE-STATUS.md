# GravityPort v0.4.0 — status da prévia Windows

Atualizado em 24/10/2026 (horário de Brasília). O GravityPort tem um **launcher nativo**, um **runtime jogável** para Gravity Rush Remastered CUSA01113 e builds de teste de melhorias visuais.

## Disponível

- Launcher Python/Tkinter compilado para Windows sem servidor ou navegador, com identidade visual GravityPort e interface pt-BR (além de idiomas upstream).
- Páginas Jogo, Vídeo, Controles, Avançado e Logs; dashboard com histórico de FPS, frametime e dados do controle/saves; testes SDL3 dos botões/eixos.
- Fallback Xbox/XInput de sensor/gesto de touchpad em combinações opcionais; SDL3 DualSense e gyro compatíveis.
- Logs de performance com contagem de FPS de apresentação e frametime, opção 60/120 FPS com VBlank do PS4 em 60 Hz.
- FSR 3.1 e FSR 4 v07 INT8 Vulkan Quality (1080p); correção de cor sRGB→linear→sRGB validada pelo usuário em uma cena jogável e por smoke test.
- Ponte Vulkan DLSS Super Resolution (NGX), testada em laboratório e no app principal local RTX 5070; DLL NVIDIA **não inclusa no pacote público**.
- Pacote Windows portátil ZIP e instalador EXE Inno Setup 6, com SHA-256, licenças e código-fonte. Instalador inclui atalhos, seleção opcional da pasta do jogo, desinstalador e preservação de dados.
- GitHub Actions com suíte de testes e testes nativos de integração no Frontlier.

## Não disponível ou em estudo

- **DLSS Frame Generation**: o bootstrap Streamline funciona na RTX 5070, mas recursos/frame tokens/swapchain ainda não estão integrados. Não gera quadros.
- Troféus PSN e serviços online do PS4.
- Versão final 1.0, assinatura digital Windows, instalador MSI e atualização automática pública.
- Modelos FSR4 v07 Native AA, 1440p, 4K e Performance/Balanced; suporte oficial AMD FSR 4.1.1 não incluído.
- QA integral de campanha, cutscenes e latência na versão atual, placas AMD e Intel.

## Condições de teste documentadas

Frontlier com Windows, RTX 5070, 1080p. O usuário informou que DLSS SR estava funcionando, depois relatou cores escuras/saturadas em FSR 4 v07, e em seguida confirmou que a correção de cor resolveu o problema. Os logs de ambos os upscalers registraram 120 FPS apresentados em trechos estáveis. Esse valor **não prova** 120 FPS de simulação, frame generation ou compatibilidade com todos os sistemas.

## Contribuidores e licenças

Origem: [LucaPazienza/gravityrush_pc](https://github.com/LucaPazienza/gravityrush_pc). Mantenedores e colaboradores históricos em [GRAVITYPORT-CREDITS.md](GRAVITYPORT-CREDITS.md). GPL-2.0-or-later e licenças adicionais de terceiros, sem jogo/saves/chaves incluídos. Consulte [INSTALACAO.md](INSTALACAO.md) e [PUBLIC-RELEASE.md](PUBLIC-RELEASE.md).

Esta é uma **prévia comunitária** — bugs são esperados.
