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
