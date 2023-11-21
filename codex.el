(setq org-cite-csl-styles-dir
      (concat (getenv "LILAC_ROOT") "/deps/styles/"))

(setq org-latex-pdf-process
  '("lualatex --shell-escape --interaction nonstopmode --output-directory=%o %f"))

; See https://stackoverflow.com/a/27285582/437583.
(setq lilac-html-head
      (concat
       "<link rel=\"stylesheet\" type=\"text/css\" href=\"codex.css\" />\n"
       "<link rel=\"stylesheet\" href="
        "\"https://fonts.googleapis.com/css2"
        "?family=Bungee+Shade:wght@400"
       "\">"
       ))
