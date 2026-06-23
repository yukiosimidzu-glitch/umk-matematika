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
    
    if container_class == 'doc-card':
        cards = re.findall(r'<div class="doc-card">(.*?)</div>\s*(?=<div class="doc-card">|<script|$)', content, re.DOTALL)
        for card in cards:
            cond_match = re.search(r'<p>(.*?)</p>', card, re.DOTALL)
            if not cond_match:
                continue
            condition = cond_match.group(1)
            condition = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', condition)
            condition = escape_latex(condition)
            
            answer = ''
            ans_match = re.search(r'<p class="answer">(.*?)</p>', card, re.DOTALL)
            if ans_match:
                answer = ans_match.group(1)
                answer = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', answer)
                answer = re.sub(r'<[^>]+>', '', answer).strip()
                answer = escape_latex(answer)
            
            tasks.append({'condition': condition, 'answer': answer})
        return tasks
    
    pattern = f'<div class="{container_class}">'
    start_positions = [m.start() for m in re.finditer(pattern, content)]
    
    for start in start_positions:
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
            
            cond_match = re.search(r'<div class="task-condition">(.*?)</div>', task, re.DOTALL)
            if not cond_match:
                cond_match = re.search(r'<p>(.*?)</p>', task, re.DOTALL)
            if not cond_match:
                continue
            
            condition = cond_match.group(1)
            condition = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', condition)
            condition = escape_latex(condition)
            
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
    
    return tasks

def extract_konspekt_text(html_content):
    """Извлекает текст конспекта из HTML для вставки в LaTeX"""
    cards = re.findall(
        r'<div class="konspekt-card">(.*?)</div>\s*(?=<div class="konspekt-card">|<div class="prof-block">|<div class="nav-bottom">)',
        html_content, re.DOTALL
    )
    
    latex_blocks = []
    
    for card in cards:
        title_match = re.search(r'<div class="konspekt-title">(.*?)</div>', card, re.DOTALL)
        if title_match:
            title = title_match.group(1)
            title = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', title)
            title = re.sub(r'<span[^>]*>.*?</span>', '', title)
            title = re.sub(r'<[^>]+>', '', title).strip()
            title = escape_latex(title)
            latex_blocks.append(r'\subsection*{' + title + '}')
        
        blocks = re.findall(r'<div class="block">(.*?)</div>', card, re.DOTALL)
        for block in blocks:
            label_match = re.search(r'<span class="block-label">(.*?)</span>', block, re.DOTALL)
            if label_match:
                label = label_match.group(1)
                label = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', label)
                label = re.sub(r'<span[^>]*>.*?</span>', '', label)
                label = re.sub(r'<[^>]+>', '', label).strip()
                label = escape_latex(label)
                latex_blocks.append(r'\textbf{' + label + r'}' + '\n')
            
            paragraphs = re.findall(r'<p>(.*?)</p>', block, re.DOTALL)
            for p in paragraphs:
                p = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', p)
                p = re.sub(r'<[^>]+>', ' ', p)
                p = re.sub(r'\s+', ' ', p).strip()
                p = escape_latex(p)
                if p:
                    latex_blocks.append(p + r'\par')
            
            uls = re.findall(r'<ul>(.*?)</ul>', block, re.DOTALL)
            for ul in uls:
                items = re.findall(r'<li>(.*?)</li>', ul, re.DOTALL)
                if items:
                    latex_blocks.append(r'\begin{itemize}')
                    for item in items:
                        item = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', item)
                        item = re.sub(r'<[^>]+>', ' ', item)
                        item = re.sub(r'\s+', ' ', item).strip()
                        item = escape_latex(item)
                        if item:
                            latex_blocks.append(r'  \item ' + item)
                    latex_blocks.append(r'\end{itemize}')
            
            tables = re.findall(r'<table class="formula-table">(.*?)</table>', block, re.DOTALL)
            for table in tables:
                rows = re.findall(r'<tr>(.*?)</tr>', table, re.DOTALL)
                if rows:
                    first_row_cells = re.findall(r'<td>(.*?)</td>', rows[0], re.DOTALL)
                    num_cols = len(first_row_cells)
                    if num_cols > 0:
                        cols_str = '|' + 'l|' * num_cols
                        latex_blocks.append(r'\begin{tabular}{' + cols_str + '}')
                        latex_blocks.append(r'\hline')
                        for row in rows:
                            cells = re.findall(r'<td>(.*?)</td>', row, re.DOTALL)
                            cells_clean = []
                            for cell in cells:
                                cell = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', cell)
                                cell = re.sub(r'<[^>]+>', ' ', cell)
                                cell = re.sub(r'\s+', ' ', cell).strip()
                                cell = escape_latex(cell)
                                cells_clean.append(cell)
                            latex_blocks.append(r'\hline')
                            latex_blocks.append(' & '.join(cells_clean) + r'\\')
                        latex_blocks.append(r'\hline')
                        latex_blocks.append(r'\end{tabular}')
                        latex_blocks.append(r'\vspace{6pt}')
        
        examples = re.findall(r'<div class="example-box">(.*?)</div>', card, re.DOTALL)
        for example in examples:
            label_match = re.search(r'<span class="example-label">(.*?)</span>', example, re.DOTALL)
            if label_match:
                label = label_match.group(1)
                label = re.sub(r'<[^>]+>', '', label).strip()
                label = escape_latex(label)
                latex_blocks.append(r'\textbf{' + label + r'}')
            
            paragraphs = re.findall(r'<p>(.*?)</p>', example, re.DOTALL)
            for p in paragraphs:
                p = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', p)
                p = re.sub(r'<[^>]+>', ' ', p)
                p = re.sub(r'\s+', ' ', p).strip()
                p = escape_latex(p)
                if p:
                    latex_blocks.append(p + r'\par')
        
        latex_blocks.append(r'\vspace{12pt}')
    
    return '\n'.join(latex_blocks)

def generate_latex_document(title, subtitle='', tasks=None, is_theory=False, konspekt_text=''):
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
        if konspekt_text:
            latex += konspekt_text + '\n\n'
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
            elif '</html>' in content:
                content = content.replace('</html>', script.replace('</body>', '') + '\n</html>')
            else:
                print(f'[!] Не найден </body> или </html> в {f}')
                continue
            
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(content)
            count += 1
            print(f'[OK] Кнопка PDF добавлена в {f}')
    
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
                elif '</html>' in content:
                    content = content.replace('</html>', script.replace('</body>', '') + '\n</html>')
                else:
                    print(f'[!] Не найден </body> или </html> в {f}')
                    continue
                
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(content)
                count += 1
                print(f'[OK] Кнопка PDF добавлена в {f}')
    
    print(f'[OK] Всего обновлено файлов: {count}')

def add_pdf_buttons_to_kontrol():
    """Добавляет кнопку 'Скачать PDF' в файлы контроля"""
    kontrol_dir = os.path.join(ROOT_DIR, 'kontrol')
    if not os.path.exists(kontrol_dir):
        print('[!] Папка kontrol/ не найдена')
        return
    
    def insert_button(filepath, script):
        with open(filepath, 'r', encoding='utf-8') as fh:
            content = fh.read()
        if 'pdf-download-btn' in content:
            return False
        if '</body>' in content:
            content = content.replace('</body>', script)
        elif '</html>' in content:
            content = content.replace('</html>', script.replace('</body>', '') + '\n</html>')
        else:
            return False
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(content)
        return True
    
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
        if insert_button(vhod_path, script):
            print('[OK] Кнопка PDF добавлена в vhodnoj.html')
    
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
        if insert_button(exam_path, script):
            print('[OK] Кнопка PDF добавлена в bilety.html')
    
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
                if insert_button(path, script):
                    print(f'[OK] Кнопка PDF добавлена в {f}')
    
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
                        if insert_button(path, script):
                            print(f'[OK] Кнопка PDF добавлена в {kr_folder}/{var_file}')

def main():
    if os.path.exists(TEX_DIR):
        shutil.rmtree(TEX_DIR)
    os.makedirs(TEX_DIR, exist_ok=True)

    cls_src = os.path.join(ROOT_DIR, 'umk-matematika.cls')
    if os.path.exists(cls_src):
        shutil.copy(cls_src, os.path.join(TEX_DIR, 'umk-matematika.cls'))
        print('[OK] umk-matematika.cls скопирован')

    print('\n=== Добавление кнопок PDF на страницы ===')
    add_pdf_buttons_to_pr()
    add_pdf_buttons_to_theory()
    add_pdf_buttons_to_kontrol()

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

    print('\n=== Экзаменационные билеты ===')
    exam_file = os.path.join(ROOT_DIR, 'kontrol', 'final', 'bilety.html')
    if os.path.exists(exam_file):
        tasks = extract_from_html(exam_file, 'variant-card')
        if tasks:
            latex = generate_latex_document('Экзаменационные билеты', '', tasks)
            with open(os.path.join(TEX_DIR, 'exam_bilety.tex'), 'w', encoding='utf-8') as fout:
                fout.write(latex)
            print(f'[OK] exam_bilety.tex ({len(tasks)} задач)')

    print('\n=== Входной контроль ===')
    vhod_file = os.path.join(ROOT_DIR, 'kontrol', 'vhodnoj.html')
    if os.path.exists(vhod_file):
        tasks = extract_from_html(vhod_file, 'variant-card')
        if tasks:
            latex = generate_latex_document('Входной контроль', '', tasks)
            with open(os.path.join(TEX_DIR, 'vhodnoj.tex'), 'w', encoding='utf-8') as fout:
                fout.write(latex)
            print(f'[OK] vhodnoj.tex ({len(tasks)} задач)')

    # Конспекты пока отключены для скорости
    # print('\n=== Теоретические конспекты ===')
    # theory_dir = os.path.join(ROOT_DIR, 'theory')
    # if os.path.exists(theory_dir):
    #     for f in sorted(os.listdir(theory_dir)):
    #         if f.endswith('.html'):
    #             path = os.path.join(theory_dir, f)
    #             with open(path, 'r', encoding='utf-8') as fh:
    #                 content = fh.read()
    #             title_match = re.search(r'<title>(.*?)</title>', content)
    #             title = title_match.group(1) if title_match else f.replace('.html', '')
    #             title = title.replace(' — Опорный конспект', '').replace(' | УМК', '')
    #             
    #             konspekt_text = extract_konspekt_text(content)
    #             
    #             latex = generate_latex_document(title, 'Опорный конспект', is_theory=True, konspekt_text=konspekt_text)
    #             with open(os.path.join(TEX_DIR, f'theory_{f.replace(".html", "")}.tex'), 'w', encoding='utf-8') as fout:
    #                 fout.write(latex)
    #             print(f'[OK] theory_{f}')

    print(f'\nГотово! Файлы в {TEX_DIR}')

if __name__ == '__main__':
    main()
