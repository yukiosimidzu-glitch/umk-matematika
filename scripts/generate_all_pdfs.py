"""
Универсальный генератор PDF для УМК «Математика строит будущее»
"""

import os
import re
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(SCRIPT_DIR, '..')
TEX_DIR = os.path.join(SCRIPT_DIR, '..', 'tex_all')


def escape_latex(text):
    if not text or not isinstance(text, str):
        return ''
    
    text = str(text)
    
    replacements = {
        '&': r'\&', '%': r'\%', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '$': r'\$', '^': r'\^{}', '~': r'\~{}',
        '°': r'$^\circ$', '…': '...', '≈': r'$\approx$',
        '±': r'$\pm$', '≤': r'$\leq$', '≥': r'$\geq$', '≠': r'$\neq$',
        '×': r'$\times$', '÷': r'$\div$', '→': r'$\to$', '←': r'$\gets$',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Корни
    text = re.sub(r'√(\d+)', r'$\sqrt{\1}$', text)
    text = re.sub(r'√', r'$\sqrt{}$', text)
    
    # KaTeX → LaTeX
    text = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', text, flags=re.IGNORECASE)
    
    # Удаляем HTML-теги
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def add_download_button_to_html(html_path, pdf_filename):
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        button = f'''
        <div style="text-align:center; margin:35px 0 20px;">
            <a href="{pdf_filename}" class="btn btn-gold" download style="padding:12px 32px; font-size:15px;">
                📥 Скачать PDF версию
            </a>
        </div>
        '''
        
        content = re.sub(r'(</div>\s*)</body>', button + r'\1</body>', content, flags=re.DOTALL)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'[+] Кнопка PDF добавлена в {os.path.basename(html_path)}')
    except Exception as e:
        print(f'[!] Кнопка не добавлена: {e}')


def extract_from_html(filepath, container_class='doc-card'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tasks = []
    cards = re.findall(f'<div class="{container_class}">(.*?)</div>', content, re.DOTALL)
    
    for card in cards:
        cond_match = re.search(r'<p>(.*?)</p>', card, re.DOTALL) or \
                     re.search(r'<h5>(.*?)</h5>', card, re.DOTALL)
        if not cond_match:
            continue
        condition = escape_latex(cond_match.group(1))
        
        answer = ''
        ans_match = re.search(r'<p class="answer">(.*?)</p>', card, re.DOTALL) or \
                    re.search(r'Ответ:\s*(.*?)(?=</p>|<div)', card, re.DOTALL)
        if ans_match:
            answer = escape_latex(ans_match.group(1))
        
        tasks.append({'condition': condition, 'answer': answer})
    
    return tasks


def generate_latex_document(title, subtitle='', tasks=None, is_theory=False):
    title = escape_latex(title or "Без названия")
    subtitle = escape_latex(subtitle or "")
    author = "Станулевич А.В."
    
    latex = rf'''\documentclass{{umk-matematika}}
\begin{{document}}

\maketitlepage
    {{{title}}}
    {{{subtitle}}}
    {{{author}}}
'''

    if is_theory:
        latex += r'''\begin{center}
\vspace{1.5cm}
\textit{Полный интерактивный конспект доступен на сайте:}\\
\texttt{https://umk-matematika.netlify.app}
\end{center}
'''
    elif tasks:
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

    cls_src = os.path.join(ROOT_DIR, 'umk-matematika.cls')
    if os.path.exists(cls_src):
        shutil.copy(cls_src, os.path.join(TEX_DIR, 'umk-matematika.cls'))
        print('[OK] Класс скопирован')

    # Практические работы
    print('\n=== Практические работы ===')
    pr_dir = os.path.join(ROOT_DIR, 'pr')
    if os.path.exists(pr_dir):
        for f in sorted(os.listdir(pr_dir)):
            if f.endswith('.html'):
                path = os.path.join(pr_dir, f)
                tasks = extract_from_html(path)
                if tasks:
                    name = f.replace('.html', '')
                    title = f'Практическая работа {name}'
                    latex = generate_latex_document(title, '', tasks)
                    tex_file = os.path.join(TEX_DIR, f'pr_{name}.tex')
                    with open(tex_file, 'w', encoding='utf-8') as fout:
                        fout.write(latex)
                    add_download_button_to_html(path, f'pr_{name}.pdf')
                    print(f'[OK] {name} — {len(tasks)} задач')

    print(f'\nГотово! Файлы .tex сохранены в {TEX_DIR}')


if __name__ == '__main__':
    main()
