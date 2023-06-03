; See https://stackoverflow.com/a/27285582/437583.
(defun codex-test-file-name ()
  (concat "test_" (file-name-nondirectory
                   (directory-file-name
                    (file-name-directory (buffer-file-name))))  ".py"))

(setq org-cite-csl-styles-dir
      (concat (getenv "LILAC_ROOT") "/deps/styles/"))
