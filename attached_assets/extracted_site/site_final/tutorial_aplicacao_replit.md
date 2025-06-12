# Tutorial de Aplicação das Melhorias no Replit

Este tutorial detalhado explica como aplicar as melhorias visuais e funcionais ao site da 2ª Vara Cível de Cariacica no ambiente Replit. O guia foi elaborado para ser acessível mesmo para usuários com pouca experiência técnica.

## Índice

1. [Preparação Inicial](#1-preparação-inicial)
2. [Upload dos Arquivos](#2-upload-dos-arquivos)
3. [Estrutura de Arquivos](#3-estrutura-de-arquivos)
4. [Aplicação das Melhorias Visuais](#4-aplicação-das-melhorias-visuais)
5. [Integração das Imagens e GIFs](#5-integração-das-imagens-e-gifs)
6. [Configuração do Ambiente](#6-configuração-do-ambiente)
7. [Testando as Alterações](#7-testando-as-alterações)
8. [Solução de Problemas Comuns](#8-solução-de-problemas-comuns)
9. [Publicação do Site](#9-publicação-do-site)

## 1. Preparação Inicial

### Acessando o Replit

1. Abra seu navegador e acesse [replit.com](https://replit.com/)
2. Faça login na sua conta Replit
3. Localize o projeto existente da 2ª Vara Cível de Cariacica na sua lista de Repls

**Dica:** Se você ainda não tem o projeto no Replit, crie um novo Repl usando o template "Python" e nomeie-o como "2vara-civel-cariacica".

### Fazendo Backup do Projeto Atual

Antes de aplicar as alterações, é importante fazer um backup do projeto atual:

1. No painel lateral do Replit, clique com o botão direito na pasta principal do projeto
2. Selecione "Download as zip"
3. Salve o arquivo ZIP em seu computador como backup

## 2. Upload dos Arquivos

### Preparando os Arquivos para Upload

Você recebeu um arquivo ZIP contendo todas as melhorias. Existem duas maneiras de aplicá-las:

#### Opção 1: Upload Completo (Recomendado para iniciantes)

1. No Replit, clique com o botão direito na pasta principal do projeto
2. Selecione "Upload Folder"
3. Selecione a pasta extraída do ZIP que você recebeu
4. Confirme a substituição de arquivos quando solicitado

#### Opção 2: Upload Seletivo (Para usuários mais experientes)

1. Extraia o arquivo ZIP em seu computador
2. No Replit, navegue para cada pasta específica (templates, static/css, static/js, etc.)
3. Faça upload dos arquivos modificados em suas respectivas pastas

**Importante:** Se você escolher a Opção 2, certifique-se de não pular nenhum arquivo essencial.

## 3. Estrutura de Arquivos

Para garantir que todos os arquivos estejam no lugar certo, verifique se a estrutura de pastas está organizada da seguinte forma:

```
AvaraWebsite/
├── static/
│   ├── css/
│   │   ├── modern/
│   │   │   ├── components.css
│   │   │   ├── layouts.css
│   │   │   ├── responsive.css
│   │   │   ├── typography.css
│   │   │   └── variables.css
│   │   ├── modern-main.css
│   │   ├── responsive.css
│   │   ├── style.css
│   │   └── tutorial-visuals.css
│   ├── js/
│   │   ├── accessibility-tests.js
│   │   ├── modern-main.js
│   │   ├── validation.js
│   │   └── [outros arquivos JS]
│   └── images/
│       ├── banners/
│       ├── icons/
│       ├── zoom_tutorial/
│       └── zoom_tutorial_gif/
├── templates/
│   ├── services/
│   │   ├── zoom_tutorial.html
│   │   └── [outros arquivos HTML]
│   ├── base.html
│   ├── index.html
│   └── [outros arquivos HTML]
├── main.py
└── requirements.txt
```

**Verificação importante:** Certifique-se de que a pasta `static/images` contenha todas as subpastas com as imagens e GIFs necessários.

## 4. Aplicação das Melhorias Visuais

### Atualizando os Templates HTML

Os principais templates HTML foram atualizados com novos elementos visuais. Verifique se os seguintes arquivos foram substituídos corretamente:

1. `templates/base.html` - Template base com o novo cabeçalho e rodapé
2. `templates/index.html` - Página inicial com seções modernizadas
3. `templates/services/zoom_tutorial.html` - Nova página de tutorial com GIF e imagens

### Atualizando os Estilos CSS

Os arquivos CSS foram reorganizados para melhor manutenção. Verifique se os seguintes arquivos estão presentes:

1. `static/css/modern-main.css` - Arquivo principal que importa os módulos CSS modernos
2. `static/css/responsive.css` - Estilos responsivos para todos os dispositivos
3. `static/css/tutorial-visuals.css` - Estilos específicos para tutoriais visuais

### Atualizando os Scripts JavaScript

Os scripts JavaScript foram otimizados e novos foram adicionados:

1. `static/js/modern-main.js` - Script principal modernizado
2. `static/js/validation.js` - Script para validação do frontend
3. `static/js/accessibility-tests.js` - Script para testes de acessibilidade

## 5. Integração das Imagens e GIFs

### Criando a Estrutura de Pastas para Imagens

Se a pasta `static/images` não existir ou estiver incompleta:

1. No Replit, clique com o botão direito na pasta `static`
2. Selecione "New Folder" e nomeie como "images"
3. Dentro da pasta "images", crie as seguintes subpastas:
   - banners
   - icons
   - zoom_tutorial
   - zoom_tutorial_gif

### Fazendo Upload das Imagens

1. Faça upload das imagens para suas respectivas pastas:
   - Banner principal em `static/images/banners/`
   - Ícones de serviços em `static/images/icons/`
   - Imagens do tutorial Zoom em `static/images/zoom_tutorial/`
   - GIF do tutorial em `static/images/zoom_tutorial_gif/`

**Dica:** Você pode arrastar e soltar múltiplos arquivos de uma vez para fazer upload mais rapidamente.

## 6. Configuração do Ambiente

### Atualizando o Arquivo main.py

O arquivo `main.py` precisa ser atualizado para incluir as novas rotas:

1. Abra o arquivo `main.py` no editor do Replit
2. Verifique se ele contém a rota para a página de tutorial do Zoom:

```python
@app.route('/services/zoom_tutorial')
def zoom_tutorial():
    return render_template('services/zoom_tutorial.html')
```

3. Se a rota não existir, adicione-a antes da linha `if __name__ == '__main__':`

### Atualizando o Arquivo requirements.txt

Verifique se o arquivo `requirements.txt` contém todas as dependências necessárias:

1. Abra o arquivo `requirements.txt`
2. Certifique-se de que ele contenha pelo menos:

```
flask==2.0.1
gunicorn==20.1.0
```

3. Se estiver faltando alguma dependência, adicione-a ao arquivo

## 7. Testando as Alterações

### Executando o Projeto

1. No Replit, clique no botão "Run" no topo da página
2. Aguarde até que o console mostre a mensagem "Running on http://0.0.0.0:8080"
3. O Replit abrirá automaticamente uma janela de visualização com o site

### Verificando as Páginas Principais

Verifique se as seguintes páginas estão funcionando corretamente:

1. **Página Inicial**: Deve mostrar o novo banner, cards de serviços com ícones e seções modernizadas
2. **Tutorial do Zoom**: Acesse através do menu ou card na página inicial, deve mostrar o GIF e imagens do tutorial
3. **Modo de Alto Contraste**: Teste o botão de acessibilidade para ativar o modo de alto contraste

### Testando a Responsividade

1. No painel de visualização do Replit, clique no ícone de dispositivo móvel para alternar entre visualizações desktop e mobile
2. Verifique se todos os elementos se ajustam corretamente em diferentes tamanhos de tela

## 8. Solução de Problemas Comuns

### Imagens Não Aparecem

Se as imagens não estiverem aparecendo:

1. Verifique se os arquivos de imagem foram carregados nas pastas corretas
2. Verifique os caminhos nos templates HTML (devem usar `{{ url_for('static', filename='images/...') }}`)
3. Verifique se os nomes dos arquivos correspondem exatamente aos referenciados no código

### Erros de JavaScript

Se as funcionalidades JavaScript não estiverem funcionando:

1. Abra o console do navegador na visualização do Replit (clique com o botão direito > Inspecionar > Console)
2. Verifique se há mensagens de erro
3. Certifique-se de que todos os arquivos JS foram carregados corretamente

### Problemas de Estilo CSS

Se os estilos não estiverem sendo aplicados corretamente:

1. Verifique se todos os arquivos CSS foram carregados nas pastas corretas
2. Certifique-se de que os links para os arquivos CSS no `base.html` estão corretos
3. Limpe o cache do navegador e recarregue a página

## 9. Publicação do Site

### Configurando para Produção

Antes de publicar o site, certifique-se de que:

1. O arquivo `.replit` está configurado corretamente:

```
run = "python main.py"
language = "python3"
```

2. O arquivo `main.py` está configurado para produção:

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Tornando o Site Público

1. No Replit, clique no botão "Share" no canto superior direito
2. Na janela que se abre, clique em "Publish to Replit"
3. Preencha as informações solicitadas:
   - Title: 2ª Vara Cível de Cariacica
   - Description: Site oficial da 2ª Vara Cível de Cariacica/ES
   - Tags: judicial, vara-civel, cariacica
4. Clique em "Publish"

### Obtendo o Link Público

Após publicar, você receberá um link público para o site. Este link pode ser compartilhado com qualquer pessoa e estará sempre disponível enquanto seu Repl estiver ativo.

O link terá o formato: `https://2vara-civel-cariacica.seuusuario.repl.co`

## Conclusão

Parabéns! Você aplicou com sucesso todas as melhorias visuais e funcionais ao site da 2ª Vara Cível de Cariacica no Replit. O site agora conta com um design moderno, recursos visuais engajantes e melhor acessibilidade.

Se você encontrar qualquer problema durante o processo, revise as etapas correspondentes neste tutorial ou consulte a documentação detalhada incluída nos arquivos do projeto.

---

## Recursos Adicionais

- [Documentação do Flask](https://flask.palletsprojects.com/)
- [Documentação do Replit](https://docs.replit.com/)
- [Guia de Acessibilidade Web](https://www.w3.org/WAI/WCAG21/quickref/)
