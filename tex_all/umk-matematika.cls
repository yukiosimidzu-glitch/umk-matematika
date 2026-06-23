% ============================================
% УМК «Математика строит будущее»
% Класс документа для практических работ
% Автор: Станулевич А.В., ГГКСТ
% ============================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{umk-matematika}[2026/01/15 v1.0 УМК Математика]

\LoadClass[12pt,a4paper]{article}

% Кодировки
\RequirePackage[utf8]{inputenc}
\RequirePackage[T2A]{fontenc}
\RequirePackage[russian]{babel}

% Геометрия
\RequirePackage[top=2cm, bottom=2cm, left=2.5cm, right=2cm]{geometry}

% Математика
\RequirePackage{amsmath,amssymb}

% Цвета
\RequirePackage{xcolor}
\definecolor{gold}{HTML}{D4A017}

% Колонтитулы
\RequirePackage{fancyhdr}
\RequirePackage{lastpage}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small УМК Математика строит будущее}
\fancyhead[R]{\small Станулевич А.В.}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.5pt}

% Гиперссылки
\RequirePackage{hyperref}
\hypersetup{colorlinks=true,linkcolor=black,urlcolor=blue}

% Титульная страница
\newcommand{\maketitlepage}[3]{
    \thispagestyle{empty}
    \begin{center}
        \vspace*{3cm}
        {\Large\bfseries Министерство образования Республики Беларусь}\\[5pt]
        {\large Гродненский государственный колледж строительных технологий}
        \vspace{2cm}
        {\Huge\bfseries\color{gold} Математика строит будущее}
        \vspace{1cm}
        {\Large\bfseries #1}\\[0.5cm]
        {\large #2}\\[1cm]
        {\normalsize\strut #3}
        \vfill
        {\normalsize Гродно, 2026}
    \end{center}
    \newpage
}

% Заголовки
\RequirePackage{titlesec}
\titleformat{\section}{\Large\bfseries\color{gold}}{}{0em}{}

\endinput
