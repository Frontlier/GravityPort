# GravityPort

**Port nativo não oficial de Gravity Rush Remastered para Windows.** Projeto comunitário derivado de [Gravity Rush PC Native Port, de LucaPazienza](https://github.com/LucaPazienza/gravityrush_pc), com o histórico Git e a licença **GPL-2.0-or-later** preservados. Não é um emulador universal, nem um projeto oficial da Sony.

[**Releases e downloads**](https://github.com/Frontlier/GravityPort/releases) · [Instalação e compatibilidade](docs/INSTALACAO.md) · [O que foi implementado](GRAVITYPORT.md) · [Créditos e colaboradores](docs/GRAVITYPORT-CREDITS.md) · [Changelog](CHANGELOG-GRAVITYPORT.md)

## Versão 0.4.0 — prévia comunitária

A aplicação nativa **GravityPort Launcher.exe** reúne um lançador Windows (Python/Tkinter compilado), o runtime de Gravity Rush Remastered e opções de vídeo, controle e diagnóstico. O jogo original **não é fornecido**; você precisa possuir e preparar sua própria cópia legalmente obtida.

| Recurso | Estado nesta versão |
|---|---|
| Jogo e história no port de origem | Jogável de início ao fim segundo testes documentados no projeto original |
| Launcher nativo do Windows | Implementado, com interface em português e outros idiomas |
| Controles SDL3 e Xbox/XInput | Implementados; opções de giroscópio e touchpad simulados |
| DualSense com giroscópio | Suportado pelo runtime original |
| Saves, áudio, cenas e menus | Implementados na base original; testes adicionais recomendados |
| 60/120 FPS apresentados | Selecionável; o VBlank e a lógica convidada permanecem a 60 Hz |
| FSR 3.1 / TAA / FXAA | Disponíveis sem SDK proprietário |
| **FSR 4 v07 Vulkan — Quality 1080p** | Experimental, corrigida conversão sRGB/linear; inclui modelo com licença |
| **DLSS Super Resolution (RTX)** | Integração implementada e testada na RTX 5070; **DLLs proprietárias não incluídas no ZIP público** |
| DLSS Frame Generation / NVIDIA Streamline | **Não implementado**: apenas bootstrap/prova de conceito desativados por padrão |
| Troféus PSN e suporte a outras versões do jogo | Não implementados/sem validação |

**Sobre os 120 FPS:** os valores observados são de apresentação de quadros. Não significam automaticamente 120 atualizações de física, quadros gerados por IA ou ausência de latência. Para solucionar problemas, retorne a **60 FPS**.

## Download para Windows

Na aba [Releases](https://github.com/Frontlier/GravityPort/releases), obtenha o arquivo **GravityPort-0.4.0-Windows-portable.zip** e seu **.sha256**, extraia o ZIP em uma pasta própria e abra **GravityPort Launcher.exe**. Existe também **GravityPort.exe**, que inicia diretamente o jogo usando as preferências salvas.

O pacote público é portátil e não instala serviços, drivers, firmware ou arquivos do jogo. Ele é **prévia**, ainda não um instalador MSI/EXE com assinatura digital. Pode haver alerta do Windows SmartScreen por ausência de assinatura; confira a origem no GitHub e a soma SHA-256 antes de executar. Não ignore alertas em arquivos de terceiros.

**Requisitos:** Windows 10/11 64 bits; GPU com Vulkan 1.3 e driver atualizado; controle compatível com SDL3 ou teclado/mouse; cópia pessoal compatível de Gravity Rush Remastered para PS4. Versão de jogo testada: **CUSA01113 v01.00**. Testes de DLSS/FSR 4 e 120 FPS ocorreram em **Windows + NVIDIA GeForce RTX 5070, 1080p**; não significam compatibilidade universal.

**Primeiro início:** em **Jogo**, selecione a pasta contendo seu próprio `eboot.bin` e os arquivos associados ao jogo; configure opções de vídeo e clique em **Jogar**. **Vídeo → Anti-aliasing** permite escolher FSR 3.1 ou FSR 4 v07 Quality. A opção DLSS só aparece quando o usuário obtém e instala separadamente os componentes oficiais compatíveis. Detalhes em [INSTALACAO.md](docs/INSTALACAO.md).

## O que desenvolvemos no GravityPort

- Identidade visual e navegação nativa para Windows, traduções pt-BR e painel com métricas da última sessão (FPS, frametime/p99, GPU, saves e resolução).
- Diagnóstico SDL3 dos botões, gatilhos e eixos do controle; fallback XInput opcional para comandos do touchpad e giroscópio virtual.
- Ajustes de overlay e apresentação em **120 FPS** com **VBlank convidado de 60 Hz**, limites configuráveis e testes de regressão.
- Integração Vulkan com **DLSS Super Resolution** e implementação experimental comunitária **FSR 4 v07 INT8**, incluindo a correção do escurecimento/saturação na conversão de cor **sRGB → RGBA16F linear → sRGB**.
- Ensaios isolados de compatibilidade NVIDIA Streamline Vulkan para um futuro Frame Generation; **nenhuma geração de quadros DLSS está ativa**.
- Compilações PyInstaller, testes Python/Windows, backups de saves, rollback e CI via GitHub Actions.

A distinção entre resultados medidos, experimentais e ainda pendentes está detalhada em [GRAVITYPORT.md](GRAVITYPORT.md) e no [changelog](CHANGELOG-GRAVITYPORT.md).

## Segurança, dados e licenciamento

- Não incluímos `eboot.bin`, `.pkg`, `.psarc`, `.prx`, firmware, chaves de console, saves pessoais nem jogos comerciais nos downloads.
- Código-fonte principal sob **GNU GPL v2 ou posterior**; componentes e modelos de terceiros têm licenças próprias, acompanhadas pelos avisos de redistribuição.
- **NVIDIA DLSS SDK/NGX não é open source.** O código de integração existe no repositório, mas as DLLs da NVIDIA não acompanham esta distribuição pública. Consulte os termos oficiais antes de instalar, compilar, redistribuir ou publicar outra versão.
- O FSR 4 apresentado é uma adaptação Vulkan experimental de **FSR4 v07**, **não** o SDK oficial AMD FSR 4.1.1, nem geração de quadros. A licença do modelo é fornecida no diretório `fsr4_shaders`.
- Sem assinatura de código ou garantia de execução em todos os sistemas. Não publique arquivos privados de saves ou logs que revelem caminhos pessoais nos issues.

## Compilação e colaboração

Dependências e processo de compilação disponíveis em [packaging/windows/README.md](packaging/windows/README.md). Para compilar o runtime, inicialize os submódulos com `git submodule update --init --recursive` e use MSYS2 CLANG64; recursos NVIDIA opcionais exigem o SDK oficial e ferramentas compatíveis.

Agradecemos contribuições por [issues](https://github.com/Frontlier/GravityPort/issues) e pull requests. Leia [CONTRIBUTING.md](CONTRIBUTING.md) antes de propor alterações. Preserve os avisos de autoria e mantenha código, documentos e testes separados de arquivos comerciais do jogo. Veja os [créditos completos](docs/GRAVITYPORT-CREDITS.md).

---

### English summary

**GravityPort** is an unofficial community development fork of [LucaPazienza's Gravity Rush Remastered native PC port](https://github.com/LucaPazienza/gravityrush_pc). It adds a Windows-native launcher with Brazilian Portuguese, controller testing and optional Xbox input fallbacks, 60/120 displayed-FPS controls, DLSS Super Resolution integration, and an experimental FSR4 v07 Vulkan Quality/1080p path with corrected SDR colors.

The Windows preview download contains the executable and open-source/appropriately licensed components, **but no PS4 game files or proprietary NVIDIA DLSS/NGX DLLs**. DLSS Frame Generation is **not functional**. The port is tested primarily on Windows with an RTX 5070 and Gravity Rush Remastered CUSA01113 v01.00. See [installation](docs/INSTALACAO.md), [features/status](GRAVITYPORT.md), [contributors](docs/GRAVITYPORT-CREDITS.md) and [license](LICENSE).

**Trademark notice:** Gravity Rush and related characters are properties of Sony Interactive Entertainment and their respective owners. GravityPort is not affiliated with, endorsed by, or sponsored by Sony, NVIDIA or AMD.
