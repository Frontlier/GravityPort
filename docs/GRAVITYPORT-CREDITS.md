# Créditos, colaboradores e direitos — GravityPort

O **GravityPort** é uma continuação comunitária baseada no **Gravity Rush PC Native Port**. As contribuições novas ao fork não substituem a autoria das obras que tornaram o port possível. A licença principal é **GPL-2.0-or-later** e o histórico Git upstream está preservado.

## Origem principal

- [**LucaPazienza**](https://github.com/LucaPazienza) — autor do projeto [gravityrush_pc](https://github.com/LucaPazienza/gravityrush_pc) e da integração específica de Gravity Rush Remastered, usada como base.
- [**FelipePrado0**](https://github.com/FelipePrado0), [**deadinside28**](https://github.com/deadinside28), [**Supermedo**](https://github.com/Supermedo), [**bc160201983**](https://github.com/bc160201983) — autores que constam no histórico Git herdado e/ou em projetos-fonte antecessores. Seus créditos e o contexto exato das mudanças permanecem no histórico.
- **bilal** — nome de autor registrado em commits herdados do histórico; sem atribuir uma identidade pública não verificada.
- [**God of War Native Port**](https://github.com/Waffle565/God-Of-War-Native-Port), [**gow3_pc/SpartanPort**](https://github.com/FelipePrado0/gow3_pc), [**MediEvil 2019 PC Port**](https://github.com/bc160201983/medievil_2019_pc_port) — referências e trabalhos predecessores mencionados no projeto original. Suas licenças e avisos são preservados conforme aplicáveis.

## Adaptações neste fork

- [**Frontlier**](https://github.com/Frontlier) — manutenção do repositório GravityPort, integração do launcher nativo pt-BR, testes, Xbox/XInput, diagnóstico, apresentação a 120 FPS, integração experimental DLSS/FSR4, correção de cor do FSR 4, empacotamento, documentação e controle de releases, como registrado nos commits.
- **FrontBite** — nome de autoria de commits encontrados no histórico de desenvolvimento local; a atribuição específica de código segue os commits, sem presumir a identidade de uma pessoa.

O GitHub pode listar colaboradores em ordem e contagem diferentes, pois o código também inclui commits de outros projetos. O histórico de commits e seus autores é a referência mais precisa. Nenhum desses créditos implica endosso de outra organização ao GravityPort.

## Renderização, IA de imagem e bibliotecas

- [**shadPS4**](https://github.com/shadps4-emu/shadPS4) — núcleo de renderização Vulkan e bibliotecas relacionadas; equipe e contribuidores respectivos.
- [**IFreemz/shadPS4-Bloodborne-DLSS-FSR**](https://github.com/IFreemz/shadPS4-Bloodborne-DLSS-FSR) — referência para parte da ponte DLSS Vulkan (consulte a atribuição SPDX do `gpu/dlss_bridge`).
- [**NVIDIA Streamline**](https://github.com/NVIDIA-RTX/Streamline) e [**NVIDIA DLSS**](https://github.com/NVIDIA/DLSS) — SDKs e documentações técnicas usadas localmente no desenvolvimento. O conteúdo proprietário NGX/SDK **não é distribuído no ZIP público**. NVIDIA não é colaboradora declarada deste fork.
- [**AMD FidelityFX / FSR**](https://github.com/GPUOpen-LibrariesAndSDKs/FidelityFX-SDK), [**FireBurn/FSR-Vulkan**](https://github.com/FireBurn/FSR-Vulkan), [**Q2RTX**](https://github.com/NVIDIA/Q2RTX), [**WinLinux1028/FidelityFX-SDK_WithFSR4**](https://github.com/WinLinux1028/FidelityFX-SDK_WithFSR4) — componentes e referências para FSR 3.1 e a adaptação comunitária Vulkan FSR 4 v07; confira a licença MIT e a proveniência documentadas nos arquivos distribuídos em `fsr4_shaders`.
- **SDL3**, **LibAtrac9**, **FFmpeg**, **FreeType**, **Dear ImGui**, **Vulkan Memory Allocator**, **sirit**, **miniz**, **xbyak**, **magic_enum**, **PyInstaller**, **Python/Tkinter**, **Pillow**, **cryptography**, **MSYS2/LLVM** — conforme suas licenças e arquivos de aviso no pacote.
- **Cabin** (SIL Open Font License) e **DejaVu Sans** (licença própria): avisos incluídos no código/pacote conforme componentes utilizados.

## Propriedade intelectual do jogo

**Gravity Rush**, personagens, ilustrações e demais direitos do jogo pertencem a **Sony Interactive Entertainment**, Japan Studio e titulares correspondentes. **Nenhum arquivo do jogo é incluído.** O GravityPort é um projeto **não oficial**, sem afiliação, patrocínio ou aprovação da Sony, NVIDIA ou AMD.

Veja `LICENSE` (GNU GPL v2 ou posterior), os avisos de copyright nos arquivos de código, as licenças dos submódulos e `THIRD-PARTY-LICENSES` no ZIP Windows. O nome de um colaborador ou empresa aqui é atribuição, não endosso. Não suprima avisos de autoria ao redistribuir modificações.
