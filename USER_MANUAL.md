# Manual do Usuário - InfoOverlay (v1.0.0)

Este documento fornece as diretrizes operacionais, de configuração e de ciclo de vida para o sistema de painéis informativos de Unidades Básicas de Saúde (UBS). 

---

## 1. Arquitetura de Personas e Papéis

Para manter a separação de responsabilidades, as instruções deste manual são divididas em dois perfis operacionais:
* **Operador de TI / Infraestrutura**: Responsável pela instalação portátil, mapeamento de diretórios e integridade física do ambiente.
* **Administrador da Clínica (Usuário final)**: Pessoal de enfermagem ou administrativo responsável por alterar conteúdos, atualizar letreiros e gerenciar o volume dos vídeos no dia a dia.

---

## 2. Guia do Operador de TI (Infraestrutura e Implantação)

O sistema foi desenhado sob o princípio de **implantação portátil de custo zero**, não necessitando de instaladores complexos ou privilégios de administrador de rede para rodar.

### Estrutura de Diretórios e Ciclo de Vida do Executável
Ao descompactar o arquivo `InfoOverlay.zip`, a seguinte topologia de arquivos será apresentada:

```text
📂 InfoOverlay_Distribution/
├── 📄 Iniciar.bat                <── INICIALIZADOR PRINCIPAL
└── 📂 InfoOverlay/                <── Binários Ocultos do Sistema
    ├── ⚙️ InfoOverlay.exe
    ├── 📂 app_assets/             <── Recursos Visuais Internos (Ícones/Grip)
    └── 📂 resources/              <── CAMINHO DE MAPEAMENTO EXTERNO
        ├── 📂 images/             <── Inserção de Campanhas de Imagem (.png, .jpg)
        └── 📂 videos/             <── Inserção de Campanhas de Vídeo (.mp4, .mov)

```

> ⚠️ **CRÍTICO PARA INFRAESTRUTURA:** Se um usuário deletar acidentalmente a pasta `resources` ou suas subpastas (`images` / `videos`), o sistema não irá travar graças ao isolamento de cache, mas nenhum conteúdo novo será carregado. Para mitigar, basta recriar manualmente as pastas com a exata grafia descrita acima e reiniciar a aplicação.

### Inicialização Segura

Para evitar que o Windows bloqueie o programa em computadores institucionais devido à falta de certificados digitais caros, **nunca execute o arquivo `InfoOverlay.exe` diretamente**.

* Sempre instrua a equipe local a dar duplo clique no arquivo **`Iniciar.bat`** localizado na raiz da pasta compactada. 
* *Nota de Operação:* Ao iniciar pelo `.bat`, o Windows ainda poderá exibir uma janela de confirmação de execução ou abrir rapidamente uma tela preta de terminal. Esse comportamento é normal, muito mais intuitivo para o usuário final e confirma que o bloqueio do SmartScreen foi evitado com sucesso.

---

## 3. Guia do Administrador da Clínica (Operação Diária)

O gerenciamento de telas da UBS é feito de forma visual e em tempo real através de interações de mouse sobre o canvas transparente do sistema.

### Movimentação, Redimensionamento e Múltiplas Telas

* **Movimentar a Janela**: Clique com o **botão esquerdo** do mouse em qualquer área transparente ou de conteúdo e arraste. O sistema possui um algoritmo de segurança (*clamping algebraico*) que impede que a janela seja arrastada para fora dos limites físicos do monitor.
* **Redimensionar**: Clique e arraste o ícone de chevron (canto inferior direito) para ajustar o tamanho ideal do painel informativo na TV ou monitor.
* **Múltiplos Monitores (Nova Janela)**: Clique com o **botão direito** em qualquer lugar da janela para abrir o menu de contexto. Selecione **"Nova Janela"**. Você pode arrastar essa nova janela para um segundo monitor (como uma TV na recepção) e configurá-la de forma independente. Uma janela pode rodar vídeos em looping enquanto a outra exibe uma playlist de imagens na triagem.

### Regras de Nomenclatura de Arquivos (Orientação de Tela)

O sistema gerencia de forma inteligente e automatizada a orientação das imagens e vídeos para que o conteúdo não fique distorcido ou esticado na tela. Para que o sistema reconheça os arquivos, você **deve** renomear as mídias seguindo a convenção de sufixos abaixo antes de jogá-las nas pastas:

| Tipo de Tela / Monitor | Sufixo Obrigatório | Exemplo de Arquivo correto |
| --- | --- | --- |
| **Horizontal / Paisagem** (TV padrão de parede) | `_h` | `campanha_vacinacao_h.png`, `video_alerta_h.mp4` |
| **Vertical / Retrato** (Totens informativos de pé) | `_v` | `painel_atendimento_v.jpg`, `guia_ubs_v.mov` |

> 🚫 **Aviso:** Arquivos que não contiverem os sufixos `_h` ou `_v` em seus nomes serão completamente ignorados pelo motor de busca do sistema e não aparecerão na playlist.

### Modo Letreiro (Atualização de Textos em Tempo Real)

Ao alternar para o modo **Letreiro** através do menu de contexto, um texto informativo padrão começará a rodar continuamente na tela.

1. Dê um **duplo clique com o botão esquerdo** em cima do texto em movimento para abrir a interface flutuante de edição (HUD).
2. No campo **"Insira seu texto"**, digite o aviso atualizado da UBS (ex: *"Atenção: Vacinação da Gripe liberada na sala 4"*).
3. Pressione **Enter** no teclado para salvar e fechar a interface de edição imediatamente.
4. *(Opcional)* Clique no botão **"Mudar Cor"** dentro da HUD para alternar a paleta de cores do texto e destacar alertas críticos.
5. Se abrir a HUD por engano e não quiser alterar nada, basta pressionar **Enter** com o texto original inalterado para fechar a interface com segurança.

### Modo Vídeo (Controle de Áudio)

Ao entrar no modo Vídeo, os arquivos da pasta correspondente entrarão em reprodução cíclica aleatória.

* Para ajustar o som, passe o ponteiro do mouse (Hover) por cima da janela de vídeo para revelar os controles ocultos de áudio.
* Utilize a barra deslizante (Slider) para aumentar/diminuir o volume ou clique no botão de alto-falante para mutar/desmutar a transmissão. O sistema salva o estado do volume escolhido para os próximos vídeos da playlist.
