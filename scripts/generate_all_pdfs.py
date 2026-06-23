"""
Универсальный генератор PDF для УМК «Математика строит будущее»
"""

import os
import re
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(SCRIPT_DIR, '..')
TEX_DIR = os.path.join(ROOT_DIR, 'tex_all')


def escape_latex(text):
    """Надёжная обработка текста для LaTeX"""
    if not text or not isinstance(text, str):
        return ''
    
    text = str(text)
    
    # Основные замены
    replacements = {
        '&': r'\&', '%': r'\%', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '$': r'\$', '^': r'\^{}', '~': r'\~{}',
        '°': r'$^\circ$', '…': '...', '≈': r'$\approx$',
        '±': r'$\pm$', '≤': r'$\leq$', '≥': r'$\geq$', '≠': r'$\neq$',
        '×': r'$\times$', '÷': r'$\div$',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Корни — исправленный вариант (без проблемного \1)
    text = re.sub(r'√(\d+)', lambda m: r'$\sqrt{' + m.group(1) + r'}$', text)
    text = re.sub(r'√(?!\$)', r'$\sqrt{}$', text)
    
    # KaTeX → LaTeX
    text = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', text, flags=re.IGNORECASE)
    
    # Удаляем HTML-теги
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def generate_latex_document(title, subtitle='', tasks=None, is_theory=False):
    title = escape_latex(title or "Без названия")
    subtitle = escape_latex(subtitle or "")
    
    latex = rf'''\documentclass{{umk-matematika}}
\begin{{document}}

\maketitlepage
    {{{title}}}
    {{{subtitle}}}
    {{Станулевич А.В.}}
'''

    if is_theory:
        latex += r'''\begin{center}
\vspace{1.5cm}
\textit{Полный интерактивный конспект доступен на сайте:}\\
\texttt{https://umk-matematika.netlify.app}
\end{center}
'''
    elif tasks and len(tasks) > 0:
        latex += '\n\\section*{Задачи}\n\n'
        for i, t in enumerate(tasks, 1):
            cond = t.get('condition', '').strip()
            if cond:
                latex += rf'\textbf{{Задача {i}.}} {cond}\par\vspace{{0.9em}}' + '\n'
        
        if any(t.get('answer') for t in tasks):
            latex += r'\newpage\section*{Ответы}' + '\n\n'
            latex += r'\begin{enumerate}' + '\n'
            for t in tasks:
                ans = t.get('answer', '').strip() or r'—'
                latex += rf' \item {ans}' + '\n'
            latex += r'\end{enumerate}' + '\n'

    latex += r'\end{document}'
    return latex


def main():
    if os.path.exists(TEX_DIR):
        shutil.rmtree(TEX_DIR)
    os.makedirs(TEX_DIR, exist_ok=True)

    # Копируем класс
    cls_src = os.path.join(ROOT_DIR, 'umk-matematika.cls')
    if os.path.exists(cls_src):
        shutil.copy(cls_src, os.path.join(TEX_DIR, 'umk-matematika.cls'))
        print('[OK] Класс umk-matematika.cls скопирован')

    # Практические работы
    print('\n=== Практические работы ===')
    pr_dir = os.path.join(ROOT_DIR, 'pr')
    if os.path.exists(pr_dir):
        count = 0
        for f in sorted(os.listdir(pr_dir)):
            if f.endswith('.html'):
                name = f.replace('.html', '')
                title = f'Практическая работа {name}'
                latex = generate_latex_document(title, '', [])
                tex_file = os.path.join(TEX_DIR, f'pr_{name}.tex')
                with open(tex_file, 'w', encoding='utf-8') as fout:
                    fout.write(latex)
                print(f'[OK] pr_{name}.tex создан')
                count += 1
        print(f'Обработано практических работ: {count}')

    print(f'\nГотово! .tex файлы сохранены в: {TEX_DIR}')
    print(f'Всего файлов: {len(os.listdir(TEX_DIR))}')


if __name__ == '__main__':
    main()
