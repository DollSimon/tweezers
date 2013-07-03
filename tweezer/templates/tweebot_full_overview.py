\documentclass[a4paper, landscape, 10pt, onesided, twocolumn]{scrreprt}

\usepackage[a4paper, landscape, nomarginpar, margin=0.5cm,top=1.0cm, bottom=1.0cm, nohead]{geometry} 

\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}

\usepackage[table]{xcolor}
\usepackage{colortbl}
\usepackage{ctable}
\usepackage{booktabs}
\usepackage{tabulary}
\usepackage{tabularx}
\usepackage{underscore}
\usepackage{array}
\usepackage{stfloats}
\usepackage{tikz} 
\usepackage[framemethod=TikZ]{mdframed}
\usepackage{siunitx}
\usepackage{fullpage}

\usepackage[small, bf]{caption}
\captionsetup{width=0.3\textwidth}
\usepackage[section]{placeins}
\renewcommand*{\raggedsection}{\centering}

\definecolor{darkblue}{rgb}{0.1,0.115,0.4981}
\definecolor{darkred}{rgb}{0.45,0.025,0.1551}
\definecolor{darkbrown}{rgb}{0.3,0.157,0.013}

\usepackage[colorlinks, linkcolor=darkblue, citecolor=darkblue, urlcolor=darkblue, bookmarks=true]{hyperref}

\input{tweezer_commands}   

\pagestyle{empty} 

% \pgfrealjobname{tweebot_overview_template} 
\title{TweeBot Experiment} 
\author{Marcus Jahnel}

\begin{document}
\section*{Tweebot Experiment}

Here is a code chunk. this is this $\Sexpr{4}$ 

<<imports, echo=FALSE>=
r = 4 + 4
@

<<foo, fig.width=4, fig.height=4>>=

@

\end{document}
