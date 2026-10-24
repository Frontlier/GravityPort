# GravityPort - DLSS Super Resolution (instalacao local)

O DLSS Super Resolution foi aprovado manualmente no Graphics Lab e pode
ser instalado no **GravityPort Preview** principal do Frontlier.
A configuracao de FPS permanece 120 apresentados com VBlank do PS4 a 60 Hz.
O usuario pode voltar a TAA ou FSR 3.1 no menu Video do launcher.

## Distribuicao e licencas

A ponte Vulkan (gow3_dlss.dll) e compilada localmente contra o SDK NGX.
A NVIDIA assina nvngx_dlss.dll. A copia da DLL deve vir do SDK oficial
NVIDIA/DLSS com licenca e assinatura verificadas. O pacote local inclui
os avisos de licenca em THIRD-PARTY-LICENSES. Nenhuma DLL proprietaria,
modelo FSR4, arquivo comercial do jogo ou perfil pessoal e versionado.
**Nao publicar este pacote com DLLs NVIDIA sem revisar a licenca aplicavel.**

## Seletor e modo inicial

Video > Anti-aliasing > DLSS Super Resolution.
Video > Mode > DLAA / Quality / Balanced / Performance.
DLAA mantem a resolucao interna nativa e aplica o AA da NVIDIA.
Quality pode desenhar a 720p e ampliar para 1080p, dependendo da tela.
O modo de inicio deve ser o ultimo modo escolhido pelo usuario, e nao
um reset de perfil. O jogo continua com o limite de 120 FPS e VBlank 60.

## Timeout NVIDIA

Quando o executavel principal possui nvngx_dlss.dll e o modo DLSS esta
selecionado, o launcher da ate 25 s para NGX iniciar, evitando fallback
prematuro da primeira inicializacao. Outras tecnologias mantem o watchdog
original de 8 s. A biblioteca e testada em RTX 5070, mas resultados em
outros sistemas podem variar.

## Seguranca e rollback

A versao anterior do executavel e sua configuracao sao copiadas antes
da substituicao. Saves e controles sao mantidos na pasta original.
Uma compilacao candidata e testada com AppData e saves isolados.
FSR4 v07 continua experimental no Graphics Lab (sem modelos no principal).
DLSS Frame Generation ainda NAO esta implementado/ativado no principal.
