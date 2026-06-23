import os
import re

ROOT = '.'  # текущая папка

def add_button(filepath, pdf_url, label='📥 Скачать PDF'):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    if 'pdf-download-btn' in html:
        print(f'Уже есть: {filepath}')
        return
    
    button = f'<a href="{pdf_url}" class="pdf-download-btn" download style="display:inline-block;padding:10px 20px;background:#2c3e50;color:white;text-decoration:none;border-radius:5px;margin:15px 0;font-size:14px;border:1px solid #D4A017;">{label}</a>'
    
    # Вставляем после <body>
    if '<body>' in html:
        html = html.replace('<body>', f'<body>\n{button}')
    else:
        print(f'Нет <body>: {filepath}')
        return
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Добавлено: {filepath}')

# Практические работы
for i in range(1, 29):
    num = f'{i:02d}'
    path = f'pr/{num}.html'
    if os.path.exists(path):
        add_button(path, f'pdf/pr_{num}.pdf')

# Самостоятельные
for f in os.listdir('kontrol/current'):
    if f.endswith('.html'):
        name = f.replace('.html', '')
        add_button(f'kontrol/current/{f}', f'../pdf/sam_{name}.pdf')

# Контрольные
for folder in os.listdir('kontrol/thematic'):
    folder_path = f'kontrol/thematic/{folder}'
    if os.path.isdir(folder_path):
        for f in os.listdir(folder_path):
            if f.endswith('.html'):
                name = f'{folder}_{f.replace(".html", "")}'
                add_button(f'{folder_path}/{f}', f'../../pdf/kr_{name}.pdf')

# Входной
add_button('kontrol/vhodnoj.html', 'pdf/vhodnoj.pdf')

# Экзамен
add_button('kontrol/final/bilety.html', '../pdf/exam_bilety.pdf')

print('\nГотово! Коммитьте и пушьте.')