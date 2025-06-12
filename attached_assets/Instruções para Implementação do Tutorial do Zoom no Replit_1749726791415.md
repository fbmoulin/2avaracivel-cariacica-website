# Instruções para Implementação do Tutorial do Zoom no Replit

Este documento fornece instruções detalhadas para implementar o tutorial de configuração de áudio do Zoom no site da 2ª Vara Cível de Cariacica hospedado no Replit.

## Arquivos Necessários

1. **Templates HTML:**
   - `/templates/services/zoom_tutorial.html` - Template principal do tutorial
   - `/templates/services/zoom_tutorial_acessivel.html` - Versão com acessibilidade aprimorada

2. **Arquivos CSS:**
   - `/static/css/tutorial-visuals.css` - Estilos específicos para o tutorial

3. **Arquivos JavaScript:**
   - `/static/js/tutorial-accessibility.js` - Funcionalidades de acessibilidade
   - `/static/js/tutorial-toggle.js` - Alternância entre GIF e imagens estáticas

4. **Imagens:**
   - `/static/images/zoom_tutorial/zoom_audio_config_1_pt.png` - Passo 1
   - `/static/images/zoom_tutorial/zoom_audio_config_2_pt.png` - Passo 2
   - `/static/images/zoom_tutorial/zoom_audio_config_3_pt.png` - Passo 3
   - `/static/images/zoom_tutorial_gif/tutorial_zoom_audio_pt.gif` - GIF animado

## Passos para Implementação no Replit

### 1. Preparação da Estrutura de Diretórios

Certifique-se de que a estrutura de diretórios esteja correta no Replit:

```
- /templates/services/
- /static/css/
- /static/js/
- /static/images/zoom_tutorial/
- /static/images/zoom_tutorial_gif/
```

Se algum diretório não existir, crie-o usando o painel de arquivos do Replit.

### 2. Upload dos Arquivos HTML

1. Navegue até `/templates/services/` no Replit
2. Faça upload dos arquivos `zoom_tutorial.html` e `zoom_tutorial_acessivel.html`
3. Verifique se os arquivos foram carregados corretamente

### 3. Upload dos Arquivos CSS e JavaScript

1. Navegue até `/static/css/` e faça upload do arquivo `tutorial-visuals.css`
2. Navegue até `/static/js/` e faça upload dos arquivos `tutorial-accessibility.js` e `tutorial-toggle.js`
3. Verifique se os arquivos foram carregados corretamente

### 4. Upload das Imagens

1. Navegue até `/static/images/zoom_tutorial/` e faça upload das imagens PNG
2. Navegue até `/static/images/zoom_tutorial_gif/` e faça upload do GIF
3. Verifique se as imagens foram carregadas corretamente

### 5. Atualização das Rotas no Backend

Adicione a rota para o tutorial do Zoom no arquivo principal do backend (geralmente `main.py` ou `app.py`):

```python
@app.route('/servicos/tutorial-zoom')
def tutorial_zoom():
    return render_template('services/zoom_tutorial.html')

@app.route('/servicos/tutorial-zoom-acessivel')
def tutorial_zoom_acessivel():
    return render_template('services/zoom_tutorial_acessivel.html')
```

### 6. Adição do Link no Menu de Navegação

Adicione um link para o tutorial no menu de navegação do site. Localize o arquivo `base.html` ou o arquivo que contém o menu de navegação e adicione:

```html
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('tutorial_zoom') }}">Tutorial Zoom</a>
</li>
```

Ou adicione como submenu em "Serviços" se já existir:

```html
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" id="servicesDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
        Serviços
    </a>
    <ul class="dropdown-menu" aria-labelledby="servicesDropdown">
        <!-- Outros itens do menu -->
        <li><a class="dropdown-item" href="{{ url_for('tutorial_zoom') }}">Tutorial Zoom</a></li>
    </ul>
</li>
```

### 7. Teste de Funcionamento

1. Execute o aplicativo no Replit
2. Navegue até a página do tutorial do Zoom
3. Verifique se:
   - As imagens e o GIF estão sendo exibidos corretamente
   - A alternância entre o GIF e as imagens estáticas funciona
   - Os recursos de acessibilidade estão funcionando
   - O layout está responsivo em diferentes tamanhos de tela

### 8. Solução de Problemas Comuns

#### Imagens não aparecem:
- Verifique se os caminhos das imagens estão corretos
- Confirme se as imagens foram carregadas nos diretórios corretos
- Verifique se há erros de console relacionados a recursos não encontrados

#### JavaScript não funciona:
- Verifique se os arquivos JavaScript foram carregados corretamente
- Confirme se não há erros no console do navegador
- Verifique se as dependências (como Bootstrap) estão sendo carregadas antes dos scripts

#### Problemas de layout:
- Verifique se o arquivo CSS está sendo carregado
- Teste em diferentes navegadores e tamanhos de tela
- Use as ferramentas de desenvolvedor do navegador para identificar problemas de CSS

### 9. Verificação de Acessibilidade

Após a implementação, verifique a acessibilidade do tutorial:

1. Teste com um leitor de tela (como NVDA ou VoiceOver)
2. Verifique se todos os elementos interativos são acessíveis por teclado
3. Confirme se as descrições alternativas das imagens são informativas
4. Teste o contraste de cores para garantir legibilidade

## Considerações Finais

- O tutorial foi projetado para ser acessível e fácil de entender para todos os usuários
- A versão acessível inclui recursos adicionais para usuários com necessidades especiais
- As instruções são escritas em linguagem simples para facilitar a compreensão por usuários leigos
- O design é responsivo e funciona em dispositivos móveis e desktop
