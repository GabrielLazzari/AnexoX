// Função que transforma o texto do elemento em spans por letra
  function splitLetters(el) {
    const text = el.textContent.trim();
    el.innerHTML = '';
    const fragment = document.createDocumentFragment();
    const words = text.split(' ').map(w => w === '' ? ' ' : w);

    words.forEach((word, wi) => {
      for (let i = 0; i < word.length; i++) {
        const ch = word[i];
        const span = document.createElement('span');
        span.className = 'char';
        span.textContent = ch;
        const delay = (wi * 0.08) + (i * 0.05);
        span.style.setProperty('--d', `${delay}s`);
        fragment.appendChild(span);
      }
      const spacer = document.createElement('span');
      spacer.textContent = ' ';
      spacer.style.display = 'inline-block';
      spacer.style.width = '0.5ch';
      fragment.appendChild(spacer);
    });

    el.appendChild(fragment);
  }

  // Função para inicializar a animação quando o elemento entra na tela
  function initAnimatedTitles() {
    const titles = document.querySelectorAll('.animated-title');
    if (!titles.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const el = entry.target;
        if (entry.isIntersecting) {
          // dispara a animação
          splitLetters(el);
          el.classList.add('animated-once');

          // opção: parar de observar depois que animar uma vez
          observer.unobserve(el);
        }
      });
    }, {
      threshold: 0.2 // só considera "visível" quando 20% do elemento está na tela
    });

    Array.prototype.forEach.call(titles, (el) => {
      if (!el) return;

      el.style.cursor = 'pointer';
      el.title = 'Clique para animar novamente';

      // permite reanimar manualmente clicando
      el.addEventListener('click', () => splitLetters(el));

      // observa o elemento
      observer.observe(el);
    });
  }

  document.addEventListener('DOMContentLoaded', initAnimatedTitles);

var style = document.createElement('style');
style.textContent = `

    /* o elemento que conterá as letras */
    .animated-title {
        letter-spacing: 2px;
        overflow: hidden;
    }

    /* cada letra é um span com comportamento de animação */
    .animated-title .char {
        font-size: 36px;
        display: inline-block;
        transform: translateY(24px);
        opacity: 0;
        will-change: transform, opacity;
        /* usamos uma variável --d para atraso (delay) por letra */
        animation: rise 560ms cubic-bezier(.2, .9, .2, 1) forwards;
        animation-delay: var(--d, 0s);
    }

    /* animação que faz a letra subir e ficar visível */
    @keyframes rise {
        0% {
            transform: translateY(24px) rotate(-2deg) scale(0.98);
            opacity: 0;
            filter: blur(2px);
        }

        60% {
            transform: translateY(-6px) rotate(0deg) scale(1.02);
            opacity: 1;
            filter: blur(0);
        }

        100% {
            transform: translateY(0) rotate(0deg) scale(1);
            opacity: 1;
        }
    }

    /* efeito extra: se quiser repetir o movimento em loop suave */
    .animated-title.loop .char {
        animation: riseLoop 3200ms ease-in-out var(--d, 0s) infinite;
    }

    @keyframes riseLoop {
        0% {
            transform: translateY(0);
            opacity: 1;
        }

        30% {
            transform: translateY(-14px);
            opacity: 0.95;
        }

        60% {
            transform: translateY(0);
            opacity: 1;
        }

        100% {
            transform: translateY(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);