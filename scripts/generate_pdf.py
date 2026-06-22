"""
Генератор PDF для практических работ УМК «Математика строит будущее»
Читает HTML-файлы из pr/ и генерирует LaTeX-файлы для компиляции в PDF.
"""

import os
import re

# Настройки
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PR_DIR = os.path.join(SCRIPT_DIR, '..', 'pr')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, '..', 'pr', 'tex')

def escape_latex_text(text):
    """Экранирование текста (но не формул)."""
    # Временно заменяем формулы на метки
    formulas = []
    def save_formula(match):
        formulas.append(match.group(0))
        return f'<<<FORMULA{len(formulas)-1}>>>'
    
    # Сохраняем всё, что похоже на формулы
    text = re.sub(r'\$[^$]+\$', save_formula, text)
    text = re.sub(r'\\[a-zA-Z]+(\{[^}]*\})*', save_formula, text)
    
    # Экранируем обычный текст
    text = text.replace('&', '\\&')
    text = text.replace('%', '\\%')
    text = text.replace('#', '\\#')
    text = text.replace('_', '\\_')
    text = text.replace('°', '$^\\circ$')
    text = text.replace('…', '...')
    
    # Восстанавливаем формулы
    for i, formula in enumerate(formulas):
        text = text.replace(f'<<<FORMULA{i}>>>', formula)
    
    return text

def extract_tasks_from_html(filepath):
    """Извлекает задачи и ответы из HTML-файла."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tasks = []
    
    # Ищем все блоки doc-card с задачами
    cards = re.findall(r'<div class="doc-card">(.*?)</div>\s*</div>', content, re.DOTALL)
    
    for card in cards:
        if 'level' not in card:
            continue
        
        # Условие задачи
        cond_match = re.search(r'<p>(.*?)</p>', card, re.DOTALL)
        if not cond_match:
            continue
        
        condition = cond_match.group(1)
        condition = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', condition)
        condition = re.sub(r'<[^>]+>', '', condition)
        condition = re.sub(r'\s+', ' ', condition).strip()
        condition = escape_latex_text(condition)
        
        # Ответ
        answer = ''
        ans_match = re.search(r'<p class="answer">Ответ:\s*(.*?)</p>', card, re.DOTALL)
        if ans_match:
            answer = ans_match.group(1)
            answer = re.sub(r'<span[^>]*data-katex="([^"]*)"[^>]*></span>', r'$\1$', answer)
            answer = re.sub(r'<[^>]+>', '', answer)
            answer = re.sub(r'\s+', ' ', answer).strip()
            answer = escape_latex_text(answer)
        
        tasks.append({'condition': condition, 'answer': answer})
    
    return tasks

def generate_latex(work_number, work_title, tasks):
    """Генерирует LaTeX-файл."""
    
    latex = r'''\documentclass{umk-matematika}

\begin{document}

\maketitlepage
    {Практическая работа №''' + str(work_number) + r'''}
    {''' + work_title + r'''}
    {}

'''

    # Задачи по уровням
    for i, task in enumerate(tasks, 1):
        if i <= 4:
            points = i
        elif i <= 7:
            points = i
        else:
            points = i
        
        if i == 1:
            latex += r'\section{Фундамент (1--4 балла)}' + '\n\n'
        elif i == 5:
            latex += r'\section{Стены (5--7 баллов)}' + '\n\n'
        elif i == 8:
            latex += r'\section{Кровля (8--10 баллов)}' + '\n\n'
        
        suff = 'а' if points in (2,3,4) else ('ов' if points >= 5 else '')
        latex += r'\textbf{Задача ' + str(i) + ' (' + str(points) + r' балл' + suff + r').} ' + task['condition'] + '\n\n'
    
    # Ответы на отдельной странице
    latex += r'\newpage' + '\n'
    latex += r'\section*{Ответы}' + '\n\n'
    latex += r'\begin{enumerate}' + '\n'
    for task in tasks:
        if task['answer']:
            latex += r'  \item ' + task['answer'] + '\n'
        else:
            latex += r'  \item \textit{(ответ не найден)}' + '\n'
    latex += r'\end{enumerate}' + '\n\n'
    
    latex += r'\end{document}'
    
    return latex

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    work_titles = {
        1: 'Радианная мера углов', 2: 'Значения тригонометрических функций',
        3: 'Тригонометрические тождества', 4: 'Решение тригонометрических уравнений',
        5: 'Аксиомы стереометрии. Сечения', 6: 'Корень n-й степени. Свойства',
        7: 'Иррациональные уравнения', 8: 'Вычисление производных',
        9: 'Уравнение касательной', 10: 'Экстремумы функции',
        11: 'Параллельность прямых и плоскостей', 12: 'Перпендикулярность прямой и плоскости',
        13: 'Теорема о трёх перпендикулярах', 14: 'Двугранный угол',
        15: 'Перпендикулярность плоскостей', 16: 'Степень с рациональным показателем',
        17: 'Показательные уравнения', 18: 'Показательные неравенства',
        19: 'Призма. Площадь поверхности и объём', 20: 'Параллелепипед. Объём',
        21: 'Пирамида. Площадь поверхности и объём', 22: 'Усечённая пирамида. Объём',
        23: 'Логарифмы. Свойства', 24: 'Логарифмические уравнения',
        25: 'Логарифмические неравенства', 26: 'Сфера и шар',
        27: 'Цилиндр. Площадь поверхности и объём', 28: 'Конус. Площадь поверхности и объём',
    }
    
    generated = 0
    for num, title in work_titles.items():
        html_file = os.path.join(PR_DIR, f'{num:02d}.html')
        
        if not os.path.exists(html_file):
            print(f'[X] Файл не найден: {html_file}')
            continue
        
        tasks = extract_tasks_from_html(html_file)
        
        if not tasks:
            print(f'[!] Задачи не извлечены: {html_file}')
            continue
        
        latex_code = generate_latex(num, title, tasks)
        
        tex_file = os.path.join(OUTPUT_DIR, f'pr-{num:02d}.tex')
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_code)
        
        print(f'[OK] pr-{num:02d}.tex ({len(tasks)} задач)')
        generated += 1
    
    print(f'\nГотово! {generated}/28 файлов создано в {OUTPUT_DIR}')

if __name__ == '__main__':
    main()
