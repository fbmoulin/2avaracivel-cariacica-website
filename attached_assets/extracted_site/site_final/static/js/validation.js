/**
 * Script de validação para o frontend modernizado
 * Site da 2ª Vara Cível de Cariacica
 * 
 * Este script verifica a integridade e funcionamento dos componentes após as mudanças visuais
 */

// Namespace para validação
const AvaraValidation = {
    // Resultados dos testes
    results: {
        passed: 0,
        failed: 0,
        warnings: 0,
        tests: []
    },
    
    // Iniciar validação
    init: function() {
        console.log('🔍 Iniciando validação do frontend modernizado...');
        
        // Executar testes
        this.validateStructure();
        this.validateComponents();
        this.validateImages();
        this.validateResponsiveness();
        this.validateAccessibility();
        this.validatePerformance();
        
        // Exibir resultados
        this.showResults();
    },
    
    // Validar estrutura HTML
    validateStructure: function() {
        console.log('📋 Validando estrutura HTML...');
        
        // Verificar elementos essenciais
        this.testElement('header', '.header-section', 'Header principal');
        this.testElement('footer', 'footer, .footer-section', 'Footer');
        this.testElement('navegação', '.navbar-nav', 'Menu de navegação');
        this.testElement('conteúdo principal', 'main, #main-content', 'Conteúdo principal');
        
        // Verificar estrutura semântica
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const hasHeadings = headings.length > 0;
        this.addResult(
            hasHeadings, 
            'Estrutura de títulos', 
            hasHeadings ? `${headings.length} títulos encontrados` : 'Nenhum título encontrado'
        );
        
        // Verificar links
        const links = document.querySelectorAll('a');
        const brokenLinks = Array.from(links).filter(link => !link.href || link.href === '#' || link.href === 'javascript:void(0)');
        this.addResult(
            brokenLinks.length === 0,
            'Links válidos',
            brokenLinks.length === 0 ? 'Todos os links têm destinos válidos' : `${brokenLinks.length} links sem destino válido`
        );
        
        // Verificar formulários
        const forms = document.querySelectorAll('form');
        if (forms.length > 0) {
            forms.forEach((form, index) => {
                const hasAction = form.hasAttribute('action');
                const hasMethod = form.hasAttribute('method');
                this.addResult(
                    hasAction && hasMethod,
                    `Formulário #${index + 1}`,
                    hasAction && hasMethod ? 'Atributos action e method presentes' : 'Faltam atributos action ou method'
                );
            });
        }
    },
    
    // Validar componentes interativos
    validateComponents: function() {
        console.log('🧩 Validando componentes interativos...');
        
        // Verificar botões
        const buttons = document.querySelectorAll('button, .btn');
        const disabledButtons = Array.from(buttons).filter(button => button.disabled);
        this.addResult(
            buttons.length > 0,
            'Botões',
            `${buttons.length} botões encontrados, ${disabledButtons.length} desabilitados`
        );
        
        // Verificar cards
        this.testElement('cards', '.card, .quick-access-card', 'Cards');
        
        // Verificar chatbot
        this.testElement('chatbot', '#chatbot-container, .chatbot-modern', 'Chatbot');
        
        // Verificar tutoriais
        this.testElement('tutoriais', '.tutorial-container, .tutorial-section', 'Tutoriais');
        
        // Verificar dropdown
        const dropdowns = document.querySelectorAll('.dropdown');
        if (dropdowns.length > 0) {
            dropdowns.forEach((dropdown, index) => {
                const hasToggle = dropdown.querySelector('.dropdown-toggle') !== null;
                const hasMenu = dropdown.querySelector('.dropdown-menu') !== null;
                this.addResult(
                    hasToggle && hasMenu,
                    `Dropdown #${index + 1}`,
                    hasToggle && hasMenu ? 'Estrutura completa' : 'Estrutura incompleta'
                );
            });
        }
        
        // Verificar modais
        this.testElement('modais', '.modal', 'Modais');
        
        // Verificar tabs
        this.testElement('tabs', '.nav-tabs, .tab-content', 'Tabs');
    },
    
    // Validar imagens e recursos visuais
    validateImages: function() {
        console.log('🖼️ Validando imagens e recursos visuais...');
        
        // Verificar imagens
        const images = document.querySelectorAll('img');
        const imagesWithAlt = Array.from(images).filter(img => img.hasAttribute('alt'));
        this.addResult(
            images.length > 0,
            'Imagens',
            `${images.length} imagens encontradas, ${imagesWithAlt.length} com atributo alt`
        );
        
        // Verificar se há imagens quebradas
        const brokenImages = Array.from(images).filter(img => !img.complete || img.naturalWidth === 0);
        this.addResult(
            brokenImages.length === 0,
            'Integridade de imagens',
            brokenImages.length === 0 ? 'Todas as imagens estão carregando corretamente' : `${brokenImages.length} imagens quebradas`
        );
        
        // Verificar GIFs
        const gifs = Array.from(images).filter(img => img.src.toLowerCase().endsWith('.gif'));
        this.addResult(
            true,
            'GIFs',
            `${gifs.length} GIFs encontrados`
        );
        
        // Verificar ícones
        const icons = document.querySelectorAll('.fa, .fas, .far, .fab, .icon');
        this.addResult(
            icons.length > 0,
            'Ícones',
            `${icons.length} ícones encontrados`
        );
    },
    
    // Validar responsividade
    validateResponsiveness: function() {
        console.log('📱 Validando responsividade...');
        
        // Verificar viewport meta tag
        const viewportMeta = document.querySelector('meta[name="viewport"]');
        this.addResult(
            viewportMeta !== null,
            'Meta tag viewport',
            viewportMeta !== null ? 'Presente' : 'Ausente'
        );
        
        // Verificar uso de media queries
        const styleSheets = document.styleSheets;
        let mediaQueriesCount = 0;
        
        try {
            for (let i = 0; i < styleSheets.length; i++) {
                const rules = styleSheets[i].cssRules || styleSheets[i].rules;
                if (rules) {
                    for (let j = 0; j < rules.length; j++) {
                        if (rules[j].type === CSSRule.MEDIA_RULE) {
                            mediaQueriesCount++;
                        }
                    }
                }
            }
        } catch (e) {
            // Erro de segurança ao acessar folhas de estilo de outros domínios
            console.warn('Não foi possível acessar todas as folhas de estilo devido a restrições de segurança');
        }
        
        this.addResult(
            mediaQueriesCount > 0,
            'Media queries',
            `${mediaQueriesCount} media queries encontradas`
        );
        
        // Verificar elementos responsivos
        this.testElement('contêineres responsivos', '.container, .container-fluid', 'Contêineres responsivos');
        this.testElement('grid responsivo', '.row, .col, [class*="col-"]', 'Sistema de grid');
    },
    
    // Validar acessibilidade básica
    validateAccessibility: function() {
        console.log('♿ Validando acessibilidade básica...');
        
        // Verificar idioma do documento
        const htmlLang = document.documentElement.lang;
        this.addResult(
            htmlLang && htmlLang.length > 0,
            'Atributo lang',
            htmlLang ? `Idioma definido: ${htmlLang}` : 'Idioma não definido'
        );
        
        // Verificar skip link
        this.testElement('skip link', '.skip-link', 'Link para pular para o conteúdo');
        
        // Verificar ARIA roles
        const elementsWithRoles = document.querySelectorAll('[role]');
        this.addResult(
            true,
            'ARIA roles',
            `${elementsWithRoles.length} elementos com atributos role`
        );
        
        // Verificar contraste (simplificado)
        this.addResult(
            true,
            'Contraste de cores',
            'Verificação manual necessária para contraste de cores'
        );
        
        // Verificar foco visível
        this.addResult(
            true,
            'Indicadores de foco',
            'Verificação manual necessária para indicadores de foco'
        );
        
        // Verificar painel de acessibilidade
        this.testElement('painel de acessibilidade', '#accessibility-panel, .accessibility-panel', 'Painel de acessibilidade');
    },
    
    // Validar performance básica
    validatePerformance: function() {
        console.log('⚡ Validando performance básica...');
        
        // Contar scripts
        const scripts = document.querySelectorAll('script');
        const externalScripts = Array.from(scripts).filter(script => script.src);
        this.addResult(
            true,
            'Scripts',
            `${scripts.length} scripts no total, ${externalScripts.length} externos`
        );
        
        // Contar folhas de estilo
        const styleSheets = document.styleSheets;
        this.addResult(
            true,
            'Folhas de estilo',
            `${styleSheets.length} folhas de estilo`
        );
        
        // Verificar lazy loading
        const lazyImages = document.querySelectorAll('img[loading="lazy"]');
        this.addResult(
            lazyImages.length > 0,
            'Lazy loading',
            `${lazyImages.length} imagens com lazy loading`
        );
    },
    
    // Testar presença de elemento
    testElement: function(name, selector, description) {
        const elements = document.querySelectorAll(selector);
        this.addResult(
            elements.length > 0,
            description,
            elements.length > 0 ? `${elements.length} elementos encontrados` : 'Não encontrado'
        );
    },
    
    // Adicionar resultado de teste
    addResult: function(passed, name, message) {
        const status = passed ? 'PASSOU' : 'FALHOU';
        const type = passed ? 'passed' : 'failed';
        
        console.log(`${passed ? '✅' : '❌'} ${name}: ${message}`);
        
        this.results[type]++;
        this.results.tests.push({
            name,
            status,
            message
        });
    },
    
    // Mostrar resultados
    showResults: function() {
        console.log('\n==== RESULTADOS DA VALIDAÇÃO ====');
        console.log(`✅ Passou: ${this.results.passed}`);
        console.log(`❌ Falhou: ${this.results.failed}`);
        console.log(`⚠️ Avisos: ${this.results.warnings}`);
        console.log('===============================\n');
        
        // Criar relatório visual se possível
        if (document.body) {
            const reportContainer = document.createElement('div');
            reportContainer.id = 'validation-report';
            reportContainer.style.position = 'fixed';
            reportContainer.style.top = '20px';
            reportContainer.style.right = '20px';
            reportContainer.style.backgroundColor = 'white';
            reportContainer.style.border = '1px solid #ccc';
            reportContainer.style.borderRadius = '5px';
            reportContainer.style.padding = '15px';
            reportContainer.style.maxWidth = '400px';
            reportContainer.style.maxHeight = '80vh';
            reportContainer.style.overflow = 'auto';
            reportContainer.style.zIndex = '9999';
            reportContainer.style.boxShadow = '0 0 10px rgba(0,0,0,0.2)';
            
            const header = document.createElement('h3');
            header.textContent = 'Relatório de Validação';
            header.style.marginTop = '0';
            reportContainer.appendChild(header);
            
            const summary = document.createElement('div');
            summary.innerHTML = `
                <div style="display: flex; margin-bottom: 15px;">
                    <div style="flex: 1; text-align: center; padding: 10px; background-color: #e6f4ea; border-radius: 5px; margin-right: 5px;">
                        <div style="font-size: 24px; font-weight: bold; color: #137333;">${this.results.passed}</div>
                        <div>Passou</div>
                    </div>
                    <div style="flex: 1; text-align: center; padding: 10px; background-color: #fce8e6; border-radius: 5px; margin-left: 5px;">
                        <div style="font-size: 24px; font-weight: bold; color: #c5221f;">${this.results.failed}</div>
                        <div>Falhou</div>
                    </div>
                </div>
            `;
            reportContainer.appendChild(summary);
            
            const list = document.createElement('div');
            this.results.tests.forEach(test => {
                const item = document.createElement('div');
                item.style.padding = '8px';
                item.style.borderBottom = '1px solid #eee';
                item.style.display = 'flex';
                
                const icon = document.createElement('div');
                icon.style.marginRight = '10px';
                icon.textContent = test.status === 'PASSOU' ? '✅' : '❌';
                item.appendChild(icon);
                
                const content = document.createElement('div');
                content.style.flex = '1';
                
                const title = document.createElement('div');
                title.style.fontWeight = 'bold';
                title.textContent = test.name;
                content.appendChild(title);
                
                const message = document.createElement('div');
                message.style.fontSize = '0.9em';
                message.style.color = '#555';
                message.textContent = test.message;
                content.appendChild(message);
                
                item.appendChild(content);
                list.appendChild(item);
            });
            reportContainer.appendChild(list);
            
            const closeButton = document.createElement('button');
            closeButton.textContent = 'Fechar';
            closeButton.style.marginTop = '15px';
            closeButton.style.padding = '8px 15px';
            closeButton.style.backgroundColor = '#f0f0f0';
            closeButton.style.border = '1px solid #ccc';
            closeButton.style.borderRadius = '4px';
            closeButton.style.cursor = 'pointer';
            closeButton.onclick = function() {
                reportContainer.remove();
            };
            reportContainer.appendChild(closeButton);
            
            document.body.appendChild(reportContainer);
        }
        
        return this.results;
    }
};

// Executar validação quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar um pouco para garantir que todos os recursos foram carregados
    setTimeout(() => {
        AvaraValidation.init();
    }, 1000);
});
