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
        '°': r'$^\circ$', '…': '...',
        '≈': r'$\approx$', '±': r'$\pm$', '≤': r'$\leq$',
        '≥': r'$\geq$', '≠': r'$\neq$', '×': r'$\times$',
        '÷': r'$\div$', 'π': r'$\pi$', '∈': r'$\in$',
        'α': r'$\alpha$', 'β': r'$\beta$', 'γ': r'$\gamma$',
        'Δ': r'$\Delta$', 'θ': r'$\theta$', 'λ': r'$\lambda$',
        'μ': r'$\mu$', 'σ': r'$\sigma$', 'φ': r'$\varphi$',
        'ω': r'$\omega$', '∠': r'$\angle$', '⊥': r'$\perp$',
        '∥': r'$\parallel$', '△': r'$\triangle$', '∞': r'$\infty$',
        '⋅': r'$\cdot$', '⟂': r'$\perp$', '⊂': r'$\subset$',
        '₁': r'$_1$', '₂': r'$_2$', '₃': r'$_3$', '₄': r'$_4$',
        '₅': r'$_5$', '₆': r'$_6$', '₇': r'$_7$', '₈': r'$_8$',
        '₉': r'$_9$', '₀': r'$_0$',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    text = text.replace('√', '$\\sqrt{}$')
    text = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_from_html(filepath, container_class='variant-card'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tasks = []
    
    # Ищем все блоки с классом container_class
    pattern = f'<div class="{container_class}">'
    start_positions = [m.start() for m in re.finditer(pattern, content)]
    
    for start in start_positions:
        # Находим конец этого div (с учётом вложенности)
        depth = 0
        i = start
        while i < len(content):
            if content[i:i+4] == '<div':
                depth += 1
                i += 4
            elif content[i:i+6] == '</div>':
                depth -= 1
                if depth == 0:
                    card = content[start:i+6]
                    break
                i += 6
            else:
                i += 1
        else:
            continue
        
        # Проверяем, есть ли внутри <div class="task">
        has_task_divs = '<div class="task">' in card
        
        if has_task_divs:
            # Формат с task div (самостоятельные, контрольные, входной, экзамен)
            task_starts = [m.start() for m in re.finditer(r'<div class="task">', card)]
            
            for t_start in task_starts:
                depth = 0
                i = t_start
                while i < len(card):
                    if card[i:i+4] == '<div':
                        depth += 1
                        i += 4
                    elif card[i:i+6] == '</div>':
                        depth -= 1
                        if depth == 0:
                            task = card[t_start:i+6]
                            break
                        i += 6
                    else:
                        i += 1
                else:
                    continue
                
                # Условие задачи
                cond_match = re.search(r'<div class="task-condition">(.*?)</div>', task, re.DOTALL)
                if not cond_match:
                    cond_match = re.search(r'<p>(.*?)</p>', task, re.DOTALL)
                if not cond_match:
                    continue
                
                condition = cond_match.group(1)
                condition = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', condition)
                condition = escape_latex(condition)
                
                # Ответ
                answer = ''
                ans_match = re.search(r'<p class="answer-block">(.*?)</p>', task, re.DOTALL)
                if not ans_match:
                    ans_match = re.search(r'<p class="answer">(.*?)</p>', task, re.DOTALL)
                if ans_match:
                    answer = ans_match.group(1)
                    answer = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', answer)
                    answer = re.sub(r'<[^>]+>', '', answer).strip()
                    answer = escape_latex(answer)
                
                tasks.append({'condition': condition, 'answer': answer})
        else:
            # Формат практических работ (doc-card с <p> напрямую)
            # Ищем все <p> внутри карточки
            paragraphs = re.findall(r'<p>(.*?)</p>', card, re.DOTALL)
            # Ищем ответы отдельно
            answers = re.findall(r'<p class="answer">(.*?)</p>', card, re.DOTALL)
            
            for p in paragraphs:
                # Пропускаем параграфы с кнопками
                if '<button' in p:
                    continue
                # Убираем HTML-теги внутри (например, <span>)
                condition = p
                condition = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', condition)
                condition = escape_latex(condition)
                if condition.strip():
                    tasks.append({'condition': condition, 'answer': ''})
            
            # Добавляем ответы (если есть) к последним задачам
            if answers:
                for idx, ans in enumerate(answers):
                    ans_clean = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', ans)
                    ans_clean = re.sub(r'<[^>]+>', '', ans_clean).strip()
                    ans_clean = escape_latex(ans_clean)
                    # Привязываем ответ к соответствующей задаче (с конца)
                    task_idx = len(tasks) - len(answers) + idx
                    if 0 <= task_idx < len(tasks):
                        tasks[task_idx]['answer'] = ans_clean
    
    return tasks

def generate_latex_document(title, subtitle='', tasks=None, is_theory=False):
    title = escape_latex(title or "Без названия")
    subtitle = escape_latex(subtitle or "")
    
    latex = r'\documentclass{umk-matematika}' + '\n'
    latex += r'\begin{document}' + '\n\n'
    latex += r'\begin{center}' + '\n'
    latex += r'{\Large\bfseries ' + title + '}' + '\n'
    if subtitle:
        latex += r'\\[0.3cm]{\large ' + subtitle + '}' + '\n'
    latex += r'\end{center}' + '\n'
    latex += r'\vspace{0.5cm}' + '\n\n'

    if is_theory:
        latex += r'\begin{center}' + '\n'
        latex += r'\textit{Полный конспект на сайте:}' + '\\' + '\n'
        latex += r'\texttt{https://umk-matematika.netlify.app}' + '\n'
        latex += r'\end{center}' + '\n'
    elif tasks and len(tasks) > 0:
        for i, t in enumerate(tasks, 1):
            condition = t['condition'].strip()
            if condition:
                latex += r'\textbf{Задача ' + str(i) + r'.} ' + condition + r'\par\vspace{10pt}' + '\n'
        
        if any(t.get('answer') for t in tasks):
            latex += r'\newpage' + '\n'
            latex += r'\section*{Ответы}' + '\n\n'
            latex += r'\begin{enumerate}' + '\n'
            for t in tasks:
                ans = t.get('answer', '').strip() or '---'
                latex += r'  \item ' + ans + '\n'
            latex += r'\end{enumerate}' + '\n'
    else:
        latex += r'\vspace{2cm}' + '\n'
        latex += r'\begin{center}\Large Нет задач\end{center}' + '\n'

    latex += r'\end{document}' + '\n'
    return latex

def add_pdf_buttons_to_pr():
    """Добавляет кнопку 'Скачать PDF' во все файлы практических работ"""
    pr_dir = os.path.join(ROOT_DIR, 'pr')
    if not os.path.exists(pr_dir):
        print('[!] Папка pr/ не найдена')
        return
    
    script = r'''<script>
(function() {
    var path = window.location.pathname;
    var match = path.match(/\/(\d+)\.html$/);
    if (match) {
        var num = match[1];
        var pdfUrl = 'pdf/pr_' + num + '.pdf';
        var btn = document.createElement('a');
        btn.href = pdfUrl;
        btn.className = 'pdf-download-btn';
        btn.innerHTML = '📥 Скачать PDF';
        btn.setAttribute('download', '');
        btn.style.cssText = 'display:inline-block;padding:10px 20px;background:#2c3e50;color:white;text-decoration:none;border-radius:5px;margin:15px 0;font-size:14px;border:1px solid #D4A017;';
        document.body.insertBefore(btn, document.body.firstChild);
    }
})();
</script>
</body>'''
    
    count = 0
    for f in sorted(os.listdir(pr_dir)):
        if f.endswith('.html'):
            path = os.path.join(pr_dir, f)
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            
            if 'pdf-download-btn' in content:
                print(f'[~] Кнопка уже есть в {f}, пропускаем')
                continue
            
            if '</body>' in content:
                content = content.replace('</body>', script)
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(content)
                count += 1
                print(f'[OK] Кнопка PDF добавлена в {f}')
            else:
                print(f'[!] Не найден </body> в {f}')
    
    print(f'[OK] Всего обновлено файлов: {count}')

def add_pdf_buttons_to_theory():
    """Добавляет кнопку 'Скачать PDF' во все файлы конспектов"""
    theory_dir = os.path.join(ROOT_DIR, 'theory')
    if not os.path.exists(theory_dir):
        print('[!] Папка theory/ не найдена')
        return
    
    script = r'''<script>
(function() {
    var path = window.location.pathname;
    var parts = path.split('/');
    var filename = parts[parts.length - 1].replace('.html', '');
    if (filename) {
        var pdfUrl = 'pdf/theory_' + filename + '.pdf';
        var btn = document.createElement('a');
        btn.href = pdfUrl;
        btn.className = 'pdf-download-btn';
        btn.innerHTML = '📥 Скачать конспект (PDF)';
        btn.setAttribute('download', '');
        btn.style.cssText = 'display:inline-block;padding:10px 20px;background:#2c3e50;color:white;text-decoration:none;border-radius:5px;margin:15px 0;font-size:14px;border:1px solid #D4A017;';
        document.body.insertBefore(btn, document.body.firstChild);
    }
})();
</script>
</body>'''
    
    count = 0
    if os.path.exists(theory_dir):
        for f in sorted(os.listdir(theory_dir)):
            if f.endswith('.html'):
                path = os.path.join(theory_dir, f)
                with open(path, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                
                if 'pdf-download-btn' in content:
                    print(f'[~] Кнопка уже есть в {f}, пропускаем')
                    continue
                
                if '</body>' in content:
                    content = content.replace('</body>', script)
                    with open(path, 'w', encoding='utf-8') as fh:
                        fh.write(content)
                    count += 1
                    print(f'[OK] Кнопка PDF добавлена в {f}')
                else:
                    print(f'[!] Не найден </body> в {f}')
    
    print(f'[OK] Всего обновлено файлов: {count}')

def add_pdf_buttons_to_kontrol():
    """Добавляет кнопку 'Скачать PDF' в файлы контроля"""
    kontrol_dir = os.path.join(ROOT_DIR, 'kontrol')
    if not os.path.exists(kontrol_dir):
        print('[!] Папка kontrol/ не найдена')
        return
    
    # Входной контроль
    vhod_path = os.path.join(kontrol_dir, 'vhodnoj.html')
    if os.path.exists(vhod_path):
        script = r'''<script>
(function() {
    var btn = document.createElement('a');
    btn.href = 'pdf/vhodnoj.pdf';
    btn.className = 'pdf-download-btn';
    btn.innerHTML = '📥 Скачать PDF';
    btn.setAttribute('download', '');
    btn.style.cssText = 'display:inline-block;padding:10px 20px;background:#2c3e50;color:white;text-decoration:none;border-radius:5px;margin:15px 0;font-size:14px;border:1px solid #D4A017;';
    document.body.insertBefore(btn, document.body.firstChild);
})();
</script>
</body>'''
        with open(vhod_path, 'r', encoding='utf-8') as fh:
            content = fh.read()
        if 'pdf-download-btn' not in content and '</body>' in content:
            content = content.replace('</body>', script)
            with open(vhod_path, 'w', encoding='utf-8') as fh:
                fh.write(content)
            print('[OK] Кнопка PDF добавлена в vhodnoj.html')
    
    # Экзаменационные билеты
    exam_path = os.path.join(kontrol_dir, 'final', 'bilety.html')
    if os.path.exists(exam_path):
        script = r'''<script>
(function() {
    var btn = document.createElement('a');
    btn.href = '../pdf/exam_bilety.pdf';
    btn.className = 'pdf-download-btn';
    btn.innerHTML = '📥 Скачать PDF';
    btn.setAttribute('download', '');
    btn.style.cssText = 'display:inline-block;padding:10px 20px;background:#2c3e50;color:white;text-decoration:none;border-radius:5px;margin:15px 0;font-size:14px;border:1px solid #D4A017;';
    document.body.insertBefore(btn, document.body.firstChild);
})();
</script>
</body>'''
        with open(exam_path, 'r', encoding='utf-8') as fh:
            content = fh.read()
        if 'pdf-download-btn' not in content and '</body>' in content:
            content = content.replace('</body>', script)
            with open(exam_path, 'w', encoding='utf-8') as fh:
                fh.write(content)
            print('[OK] Кнопка PDF добавлена в bilety.html')
    
    # Самостоятельные работы
    sam_dir = os.path.join(kontrol_dir, 'current')
    if os.path.exists(sam_dir):
        for f in sorted(os.listdir(sam_dir)):
            if f.endswith('.html') and f.startswith('sam-'):
                path = os.path.join(sam_dir, f)
                name = f.replace('.html', '')
                script = f'''<script>
(function() {{
    var btn = document.createElement('a');
    btn.href = '../pdf/sam_{name}.pdf';
    btn.className = 'pdf-download-btn';
    btn.innerHTML = '📥 Скачать PDF';
    btn.setAttribute('download', '');
    btn.style.cssText = 'display:inline-block;padding:10px 20px;background:#2c3e50;color:white;text-decoration:none;border-radius:5px;margin:15px 0;font-size:14px;border:1px solid #D4A017;';
    document.body.insertBefore(btn, document.body.firstChild);
}})();
</script>
</body>'''
                with open(path, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                if 'pdf-download-btn' not in content and '</body>' in content:
                    content = content.replace('</body>', script)
                    with open(path, 'w', encoding='utf-8') as fh:
                        fh.write(content)
                    print(f'[OK] Кнопка PDF добавлена в {f}')
    
    # Контрольные работы
    kr_dir = os.path.join(kontrol_dir, 'thematic')
    if os.path.exists(kr_dir):
        for kr_folder in sorted(os.listdir(kr_dir)):
            kr_path = os.path.join(kr_dir, kr_folder)
            if os.path.isdir(kr_path):
                for var_file in sorted(os.listdir(kr_path)):
                    if var_file.endswith('.html'):
                        path = os.path.join(kr_path, var_file)
                        name = f'{kr_folder}_{var_file.replace(".html", "")}'
                        script = f'''<script>
(function() {{
    var btn = document.createElement('a');
    btn.href = '../../pdf/kr_{name}.pdf';
    btn.className = 'pdf-download-btn';
    btn.innerHTML = '📥 Скачать PDF';
    btn.setAttribute('download', '');
    btn.style.cssText = 'display:inline-block;padding:10px 20px;background:#2c3e50;color:white;text-decoration:none;border-radius:5px;margin:15px 0;font-size:14px;border:1px solid #D4A017;';
    document.body.insertBefore(btn, document.body.firstChild);
}})();
</script>
</body>'''
                        with open(path, 'r', encoding='utf-8') as fh:
                            content = fh.read()
                        if 'pdf-download-btn' not in content and '</body>' in content:
                            content = content.replace('</body>', script)
                            with open(path, 'w', encoding='utf-8') as fh:
                                fh.write(content)
                            print(f'[OK] Кнопка PDF добавлена в {kr_folder}/{var_file}')

def main():
    if os.path.exists(TEX_DIR):
        shutil.rmtree(TEX_DIR)
    os.makedirs(TEX_DIR, exist_ok=True)

    cls_src = os.path.join(ROOT_DIR, 'umk-matematika.cls')
    if os.path.exists(cls_src):
        shutil.copy(cls_src, os.path.join(TEX_DIR, 'umk-matematika.cls'))
        print('[OK] umk-matematika.cls скопирован')

    # ========== ДОБАВЛЯЕМ КНОПКИ PDF ==========
    print('\n=== Добавление кнопок PDF на страницы ===')
    add_pdf_buttons_to_pr()
    add_pdf_buttons_to_theory()
    add_pdf_buttons_to_kontrol()

    # Практические (используют doc-card)
    print('\n=== Практические работы ===')
    pr_dir = os.path.join(ROOT_DIR, 'pr')
    if os.path.exists(pr_dir):
        for f in sorted(os.listdir(pr_dir)):
            if f.endswith('.html'):
                path = os.path.join(pr_dir, f)
                tasks = extract_from_html(path, 'doc-card')
                if tasks:
                    name = f.replace('.html', '')
                    latex = generate_latex_document(f'Практическая работа {name}', '', tasks)
                    with open(os.path.join(TEX_DIR, f'pr_{name}.tex'), 'w', encoding='utf-8') as fout:
                        fout.write(latex)
                    print(f'[OK] pr_{name}.tex ({len(tasks)} задач)')

    # Самостоятельные (используют variant-card)
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

    # Контрольные (используют variant-card)
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
