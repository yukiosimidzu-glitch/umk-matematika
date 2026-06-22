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
    
    text = text.replace('&', '\\&')
    text = text.replace('%', '\\%')
    text = text.replace('#', '\\#')
    text = text.replace('_', '\\_')
    text = text.replace('°', '$^\\circ$')
    text = text.replace('…', '...')
    text = text.replace('≈', '$\\approx$')
    text = text.replace('±', '$\\pm$')
    text = text.replace('≤', '$\\leq$')
    text = text.replace('≥', '$\\geq$')
    text = text.replace('≠', '$\\neq$')
    text = text.replace('×', '$\\times$')
    text = text.replace('÷', '$\\div$')
    text = text.replace('√', '$\\sqrt{}$')
    text = text.replace('π', r'$\pi$')
    text = text.replace('∈', r'$\in$')
    text = text.replace('α', r'$\alpha$')
    text = text.replace('β', r'$\beta$')
    text = text.replace('γ', r'$\gamma$')
    text = text.replace('Δ', r'$\Delta$')
    text = text.replace('θ', r'$\theta$')
    text = text.replace('λ', r'$\lambda$')
    text = text.replace('μ', r'$\mu$')
    text = text.replace('σ', r'$\sigma$')
    text = text.replace('φ', r'$\varphi$')
    text = text.replace('ω', r'$\omega$')
    text = text.replace('∠', r'$\angle$')
    text = text.replace('⊥', r'$\perp$')
    text = text.replace('∥', r'$\parallel$')
    text = text.replace('△', r'$\triangle$')
    text = text.replace('∞', r'$\infty$')
    text = text.replace('⋅', r'$\cdot$')
    text = text.replace('₁', r'$_1$')
    text = text.replace('₂', r'$_2$')
    text = text.replace('₃', r'$_3$')
    text = text.replace('₄', r'$_4$')
    text = text.replace('₅', r'$_5$')
    text = text.replace('₆', r'$_6$')
    text = text.replace('₇', r'$_7$')
    text = text.replace('₈', r'$_8$')
    text = text.replace('₉', r'$_9$')
    text = text.replace('₀', r'$_0$')
    text = text.replace('⟂', r'$\perp$')
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_from_html(filepath, container_class='doc-card'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tasks = []
    cards = re.findall(f'<div class="{container_class}">(.*?)</div>', content, re.DOTALL)
    
    for card in cards:
        cond_match = re.search(r'<p>(.*?)</p>', card, re.DOTALL) or \
                     re.search(r'<div class="task-condition">(.*?)</div>', card, re.DOTALL)
        
        if not cond_match:
            continue
        
        condition = cond_match.group(1)
        condition = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', condition)
        condition = escape_latex(condition)
        
        answer = ''
        ans_match = re.search(r'<p class="answer">(.*?)</p>', card, re.DOTALL) or \
                    re.search(r'<p class="answer-block">(.*?)</p>', card, re.DOTALL)
        if ans_match:
            answer = ans_match.group(1)
            answer = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', answer)
            answer = re.sub(r'<[^>]+>', '', answer).strip()
            answer = escape_latex(answer)
        
        tasks.append({'condition': condition, 'answer': answer})
    
    return tasks

def generate_latex_document(title, subtitle='', tasks=None, is_theory=False):
    subtitle = subtitle or ''
    
    latex = r'\documentclass{umk-matematika}' + '\n'
    latex += r'\begin{document}' + '\n'
    latex += r'\maketitlepage' + '\n'
    latex += r'    {' + escape_latex(title) + '}' + '\n'
    latex += r'    {' + escape_latex(subtitle) + '}' + '\n'
    latex += r'    {}' + '\n\n'

    if is_theory:
        latex += r'\begin{center}' + '\n'
        latex += r'\vspace{1.5cm}' + '\n'
        latex += r'\textit{Полный конспект на сайте:}' + '\n\n'
        latex += r'\texttt{https://umk-matematika.netlify.app}' + '\n'
        latex += r'\end{center}' + '\n'
    elif tasks:
        for i, t in enumerate(tasks, 1):
            latex += r'\textbf{Задача ' + str(i) + r'.} ' + t['condition'] + r'\par\vspace{8pt}' + '\n'
        
        if any(t['answer'] for t in tasks):
            latex += r'\newpage' + '\n'
            latex += r'\section*{Ответы}' + '\n\n'
            latex += r'\begin{enumerate}' + '\n'
            for t in tasks:
                ans = t['answer'] if t['answer'] else '---'
                latex += r'  \item ' + ans + '\n'
            latex += r'\end{enumerate}' + '\n'

    latex += r'\end{document}' + '\n'
    return latex

def main():
    if os.path.exists(TEX_DIR):
        shutil.rmtree(TEX_DIR)
    os.makedirs(TEX_DIR, exist_ok=True)

    cls_src = os.path.join(ROOT_DIR, 'umk-matematika.cls')
    if os.path.exists(cls_src):
        shutil.copy(cls_src, os.path.join(TEX_DIR, 'umk-matematika.cls'))
        print('[OK] umk-matematika.cls скопирован')

    # Практические
    print('\n=== Практические работы ===')
    pr_dir = os.path.join(ROOT_DIR, 'pr')
    if os.path.exists(pr_dir):
        for f in sorted(os.listdir(pr_dir)):
            if f.endswith('.html'):
                path = os.path.join(pr_dir, f)
                tasks = extract_from_html(path)
                if tasks:
                    name = f.replace('.html', '')
                    latex = generate_latex_document(f'Практическая работа {name}', '', tasks)
                    with open(os.path.join(TEX_DIR, f'pr_{name}.tex'), 'w', encoding='utf-8') as fout:
                        fout.write(latex)
                    print(f'[OK] pr_{name}.tex ({len(tasks)} задач)')

    # Самостоятельные
    print('\n=== Самостоятельные работы ===')
    sam_dir = os.path.join(ROOT_DIR, 'kontrol', 'current')
    if os.path.exists(sam_dir):
        for f in sorted(os.listdir(sam_dir)):
            if f.endswith('.html') and f.startswith('sam-'):
                path = os.path.join(sam_dir, f)
                tasks = extract_from_html(path, 'variant-card')
                if tasks:
                    name = f.replace('.html', '')
                    latex = generate_latex_document(f'Самостоятельная работа {name}', '', tasks)
                    with open(os.path.join(TEX_DIR, f'sam_{name}.tex'), 'w', encoding='utf-8') as fout:
                        fout.write(latex)
                    print(f'[OK] sam_{name}.tex ({len(tasks)} задач)')

    # Контрольные
    print('\n=== Контрольные работы ===')
    kr_dir = os.path.join(ROOT_DIR, 'kontrol', 'thematic')
    if os.path.exists(kr_dir):
        for kr_folder in sorted(os.listdir(kr_dir)):
            kr_path = os.path.join(kr_dir, kr_folder)
            if os.path.isdir(kr_path):
                for var_file in sorted(os.listdir(kr_path)):
                    if var_file.endswith('.html'):
                        path = os.path.join(kr_path, var_file)
                        tasks = extract_from_html(path, 'variant-card')
                        if tasks:
                            name = f'{kr_folder}_{var_file.replace(".html", "")}'
                            latex = generate_latex_document(f'Контрольная работа {name}', '', tasks)
                            with open(os.path.join(TEX_DIR, f'kr_{name}.tex'), 'w', encoding='utf-8') as fout:
                                fout.write(latex)
                            print(f'[OK] kr_{name}.tex ({len(tasks)} задач)')

    # Экзамен
    print('\n=== Экзаменационные билеты ===')
    exam_file = os.path.join(ROOT_DIR, 'kontrol', 'final', 'bilety.html')
    if os.path.exists(exam_file):
        tasks = extract_from_html(exam_file, 'variant-card')
        if tasks:
            latex = generate_latex_document('Экзаменационные билеты', '', tasks)
            with open(os.path.join(TEX_DIR, 'exam_bilety.tex'), 'w', encoding='utf-8') as fout:
                fout.write(latex)
            print(f'[OK] exam_bilety.tex ({len(tasks)} задач)')

    # Входной контроль
    print('\n=== Входной контроль ===')
    vhod_file = os.path.join(ROOT_DIR, 'kontrol', 'vhodnoj.html')
    if os.path.exists(vhod_file):
        tasks = extract_from_html(vhod_file, 'variant-card')
        if tasks:
            latex = generate_latex_document('Входной контроль', '', tasks)
            with open(os.path.join(TEX_DIR, 'vhodnoj.tex'), 'w', encoding='utf-8') as fout:
                fout.write(latex)
            print(f'[OK] vhodnoj.tex ({len(tasks)} задач)')

    # Конспекты
    print('\n=== Теоретические конспекты ===')
    theory_dir = os.path.join(ROOT_DIR, 'theory')
    if os.path.exists(theory_dir):
        for f in sorted(os.listdir(theory_dir)):
            if f.endswith('.html'):
                path = os.path.join(theory_dir, f)
                with open(path, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                title_match = re.search(r'<title>(.*?)</title>', content)
                title = title_match.group(1) if title_match else f.replace('.html', '')
                title = title.replace(' — Опорный конспект', '').replace(' | УМК', '')
                latex = generate_latex_document(title, 'Опорный конспект', is_theory=True)
                with open(os.path.join(TEX_DIR, f'theory_{f.replace(".html", "")}.tex'), 'w', encoding='utf-8') as fout:
                    fout.write(latex)
                print(f'[OK] theory_{f}')

    print(f'\nГотово! Файлы в {TEX_DIR}')

if __name__ == '__main__':
    main()
