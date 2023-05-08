; Set garbage-collection threshold to 16 GiB.
(setq gc-cons-threshold #x400000000)

(defun codex-disable-syntax-highlighting (_orig-func &rest args)
  (apply 'codex-org-html-fontify-code args))
(defun codex-org-html-fontify-code (code lang) (org-html-encode-plain-text code))

(defun codex-publish-profile ()
  (interactive)
  (profiler-start 'cpu)
  (codex-publish)
  (profiler-stop)
  (profiler-report)
  (profiler-report-write-profile "emacs-profile-weave.txt") t)

(defun codex-tangle-profile ()
  (interactive)
  (profiler-start 'cpu)
  (org-babel-tangle)
  (profiler-stop)
  (profiler-report)
  (profiler-report-write-profile "emacs-profile-tangle.txt") t)

;; Built-in packages (distributed with Emacs).
(require 'tex-mode)
(require 'elisp-mode)

;; Third-party packages (checked in as Git submodules)
(add-to-list 'load-path (concat (getenv "PWD") "/deps/elisp/s.el"))
(require 's)
(add-to-list 'load-path (concat (getenv "PWD") "/deps/elisp/compat.el"))
(require 'compat)
(add-to-list 'load-path (concat (getenv "PWD") "/deps/elisp/dash.el"))
(require 'dash)
(add-to-list 'load-path (concat (getenv "PWD") "/deps/elisp/dr-qubit.org"))
(add-to-list 'load-path (concat (getenv "PWD") "/deps/elisp/f.el"))
(add-to-list 'load-path (concat (getenv "PWD") "/deps/elisp/parsebib"))
(add-to-list 'load-path (concat (getenv "PWD") "/deps/elisp/citeproc-el"))
(require 'citeproc)
(require 'oc-csl)
(add-to-list 'load-path (concat (getenv "PWD") "/deps/elisp/emacs-htmlize"))
(require 'htmlize)
(add-to-list 'load-path (concat (getenv "PWD") "/deps/elisp/magit/lisp"))
(require 'magit-section)
(add-to-list 'load-path (concat (getenv "PWD") "/deps/elisp/nix-mode"))
(require 'nix-mode)

(setq org-export-time-stamp-file nil)
(setq org-html-postamble nil)
(defun org-export-deterministic-reference (references)
  (let ((new (length references)))
     (while (rassq new references) (setq new (+ new 1)))
     new))
(advice-add #'org-export-new-reference :override #'org-export-deterministic-reference)

; This optimization can be used to crudely speed up weaving time by disabling fontification (no syntax highlighting of source code blocks).
(if (getenv "CODEX_LP_QUICK")
    (progn
      (message "CODEX_LP_QUICK set; invoking some cost-cutting measures")
      (advice-add 'org-html-fontify-code :around #'codex-disable-syntax-highlighting)))

(defun codex-publish ()
  (interactive)
  (codex-publish-1)
  (clrhash codex-polyblock-names-totals)
  (codex-publish-2))

;; This is here solely to populate the codex-child-HTML_ID-hash-table.
(defun codex-publish-1 ()
  (let (
        (org-export-before-parsing-hook
         '(codex-noweb-source-code-block-captions
           codex-UID-for-all-headlines
           codex-UID-for-all-polyblocks))

        (org-export-filter-src-block-functions
         '(codex-populate-child-HTML_ID-hash-table
           codex-populate-org_id-human_id-hash-table))

        (org-html-htmlize-output-type 'css))
    (org-html-export-to-html)))

(defun codex-publish-2 ()
  (let (
        (org-export-before-parsing-hook
         '(codex-noweb-source-code-block-captions
           codex-UID-for-all-headlines
           codex-UID-for-all-polyblocks))

        (org-export-filter-src-block-functions
         '(codex-link-to-children-from-parent-body
           codex-prettify-source-code-captions))
        (org-export-filter-final-output-functions
         '(codex-replace-org_ids-with-human_ids))

        (org-html-htmlize-output-type 'css))
    ;; Debugging
    ;(message "codex-child-HTML_ID-hash-table: %s" codex-child-HTML_ID-hash-table)
    ;(message "codex-org_id-human_id-hash-table: %s" codex-org_id-human_id-hash-table)
    (org-html-export-to-html)))

;; Modify Org buffer
(defun codex-noweb-source-code-block-captions (_backend)
  (let* ((parent-blocks
           ;; parent-blocks is a let* binding, not a function call.
           (org-element-map (org-element-parse-buffer) 'src-block
             (lambda (src-block)
                (if (codex-is-parent-block src-block) src-block))))
         (child-parent-hash-table
           (let ((hash-table (make-hash-table :test 'equal)))
             (mapc
              (lambda (parent-block)
               (let* ((parent-name (org-element-property :name parent-block))
                      (parent-body (org-element-property :value parent-block))
                      (child-names (codex-get-noweb-children parent-body)))
                 (mapc (lambda (child-name) (puthash child-name parent-name hash-table)) child-names)))
              parent-blocks)
             hash-table))
         (all-src-blocks
           (org-element-map (org-element-parse-buffer) 'src-block 'identity))
         (smart-captions
           (-remove 'null
             (cl-loop for src-block in all-src-blocks collect
               (let* ((child (codex-get-src-block-name src-block))
                      (child-name (car child))
                      (NSCB_NAME (format "=%s= " child-name))                  ;ref:NSCB_NAME
                      (NSCB_POLYBLOCK_INDICATOR (car (cdr child)))             ;ref:NSCB_POLYBLOCK_INDICATOR
                      (polyblock-counter (gethash child-name codex-polyblock-names-totals 0))
                      (polyblock-counter-incremented (puthash child-name (+ 1 polyblock-counter) codex-polyblock-names-totals))
                      (parent (gethash child-name child-parent-hash-table))
                      (pos (org-element-property :begin src-block))
                      (NSCB_LINK_TO_PARENT                                     ;ref:NSCB_LINK_TO_PARENT
                       (if parent (format " [[%s][PARENT]]" parent) ""))
                      (smart-caption
                       (concat
                         "#+caption: "
                         NSCB_NAME
                         NSCB_POLYBLOCK_INDICATOR
                         NSCB_LINK_TO_PARENT
                         "\n")))
                 (when parent (cons pos smart-caption)))))))
    (cl-loop for smart-caption in (reverse smart-captions) do
      (let ((pos (car smart-caption))
            (caption (cdr smart-caption)))
        (goto-char pos)
        (insert caption)))))

(defun codex-is-parent-block (src-block)
  (let ((body (org-element-property :value src-block)))
    (codex-get-noweb-children body)))
(defun codex-get-noweb-children (s)
  (let* ((lines (split-string s "\n"))
         (refs (-remove 'null
                 (mapcar
                  (lambda (line)
                   (if (string-match (codex-nref-rx nil) line)
                       (match-string-no-properties 1 line)))
                  lines))))
    refs))
(defun codex-get-noweb-ref-polyblock-name (source-code-block)
  (let* ((headers (org-element-property :header source-code-block))
         (noweb-ref-name
          (nth 0
           (-remove 'null
            (mapcar
             (lambda (header)
               (if (string-match ":noweb-ref \\(.+\\)" header)
                   (match-string-no-properties 1 header)))
             headers)))))
    noweb-ref-name))
(defun codex-get-src-block-name (src-block)
  (let* ((name-direct (org-element-property :name src-block))
         (name-indirect (codex-get-noweb-ref-polyblock-name src-block)))
    (if name-direct
        `(,name-direct "")
        `(,name-indirect "(polyblock)"))))

(defun codex-UID-for-all-headlines (_backend)
  (let* ((all-headlines
           (org-element-map (org-element-parse-buffer) 'headline 'identity))

         (headline-uid-hash-table (make-hash-table :test 'equal))
         (headline-UIDs
           (-remove 'null
             (cl-loop for headline in all-headlines collect
               (let* ((headline-UID (codex-get-unique-id headline headline-uid-hash-table))
                      ;; Get the position just after the headline (just underneath it).
                      (pos (progn
                             (goto-char (org-element-property :begin headline))
                             (re-search-forward "\n"))))
                 (cons pos (concat
                            ":PROPERTIES:\n"
                            ":CUSTOM_ID: " headline-UID "\n"
                            ":END:\n")))))))
    ; (message "custom ID insertions: %s" headline-UIDs)
    (cl-loop for pos-insertion in (reverse headline-UIDs) do
        (let ((pos (car pos-insertion))
              (insertion (cdr pos-insertion)))
            (goto-char pos)
            (insert insertion)))))

(defun codex-get-unique-id (headline hash-table)
  (let* ((name (org-element-property :raw-value headline))
         (disambiguation-number 0)
         (key (concat "h-" (codex-normalize-string name)))
         (val (gethash key hash-table)))
    ;; Discard the key if a value already exists. This drives up the
    ;; disambiguation number.
    (while val
      (setq disambiguation-number (+ 1 disambiguation-number))
      (setq key (concat "h-"
                        (codex-normalize-string
                         (format "%s-%s" name disambiguation-number))))
      (setq val (gethash key hash-table)))
    (puthash key t hash-table)
    key))

(defun codex-normalize-string (s)
  (string-trim
    (replace-regexp-in-string "[^A-Za-z0-9]" "-" s)
    "-"
    "-"))

(defun codex-UID-for-all-polyblocks (_)
  (let* ((all-src-blocks
           (org-element-map (org-element-parse-buffer) 'src-block 'identity))
         (polyblock-id 0)
         (noweb-ref-last "")
         (polyblock-UIDs
           (-remove 'null
             (cl-loop for src-block in all-src-blocks collect
               (let* ((noweb-ref (codex-get-noweb-ref-polyblock-name src-block))
                      (is-polyblock
                       (and
                         noweb-ref
                         (not (org-element-property :name src-block))))
                      (pos (org-element-property :begin src-block))
                      (name-field-with-uid (format "#+name: ___polyblock-%s\n" polyblock-id)))
                 (when (and
                         is-polyblock
                         (not (string= noweb-ref noweb-ref-last)))
                   (setq noweb-ref-last noweb-ref)
                   (setq polyblock-id (+ 1 polyblock-id))
                   (cons pos name-field-with-uid)))))))
    (cl-loop for polyblock-UID in (reverse polyblock-UIDs) do
        (let ((pos (car polyblock-UID))
              (name-field-with-uid (cdr polyblock-UID)))
            (goto-char pos)
            (insert name-field-with-uid)))))

;; Modify HTML
; Define a global hash table for mapping child source block names to their HTML IDs.
(setq codex-child-HTML_ID-hash-table (make-hash-table :test 'equal))

(defun codex-populate-child-HTML_ID-hash-table (src-block-html backend info)
  (when (org-export-derived-backend-p backend 'html)
    (let* ((child-name (codex-get-src-block-name-from-html src-block-html))
           (child-HTML_ID (codex-get-src-block-HTML_ID src-block-html)))
      (if child-HTML_ID ; Skip blocks that lack an HTML ID, such as non-head polyblocks.
        (puthash child-name child-HTML_ID codex-child-HTML_ID-hash-table))
      ; Return src-block-html as-is (no modifications).
      src-block-html)))

(defun codex-get-src-block-name-from-html (src-block-html)
  (let* ((match-nref (string-match
                      (concat
                       "<label.+?<code>"
                       (codex-nref-rx nil)
                       "</code>")
                      src-block-html))
         (match-raw (if (not match-nref)
                        (string-match
                         (rx-to-string
                          '(and
                            "<label"
                            (+ (not ">"))
                            ">"
                            (group (*? anychar))
                            "</label>"))
                         src-block-html)))
         (matched-contents (match-string-no-properties 1 src-block-html)))
    (if match-nref
        matched-contents
        (if match-raw
            (codex-clean-up-match-raw matched-contents)))))

(defun codex-clean-up-match-raw (s)
  (let* ((normalized (codex-normalize-string s))
         (rx (rx-to-string
                '(and
                  "Listing-"
                  (+ (any digit))
                  (+ "-")
                  "span"
                  (* "-")
                  (group (+ anychar)))))
         (match (string-match rx normalized)))
    (if match
        (match-string-no-properties 1 normalized)
        normalized)))

(defun codex-get-src-block-HTML_ID (src-block-html) ;ref:codex-get-src-block-HTML_ID
  (let ((match (string-match "<pre [^>]+?id=\"\\([^\"]+\\)\">" src-block-html)))
    (if match (match-string-no-properties 1 src-block-html))))

(defun codex-link-to-children-from-parent-body (src-block-html backend info)
  (when (org-export-derived-backend-p backend 'html)
    ;; Break up source block into 3 subparts --- the leading <div ...>, the <label ...></label> (if any) and
    ;; <pre ...></pre>.
    ;; Then run the linkifying logic against only the body, and then return the
    ;; original label and new body.
    (let* ((div-caption-body (codex-get-source-block-html-parts-without-newlines src-block-html))
           (leading-div (nth 0 div-caption-body))
           (caption (nth 1 div-caption-body))
           (body (nth 2 div-caption-body))
           (body-linkified-without-newlines
            (replace-regexp-in-string
             (codex-nref-rx nil)
             (lambda (child-name-text)
                 (let* ((HTML_ID (gethash child-name-text codex-child-HTML_ID-hash-table)))
                  (if HTML_ID
                      (concat "<span class=\"codex-child-link-from-parent\"><a href=\"#" HTML_ID "\">"
                              (string-remove-prefix "__NREF__" child-name-text)
                              "</a></span>")
                      child-name-text)))
             body))
           (body-linkified-with-newlines
            (codex-to-multi-line body-linkified-without-newlines)))
      (concat leading-div caption body-linkified-with-newlines "</div>"))))

(defun codex-to-single-line (s)
  (replace-regexp-in-string "\n" "<<<NEWLINE>>>" s))

(defun codex-to-multi-line (s)
  (replace-regexp-in-string "<<<NEWLINE>>>" "\n" s))

(setq org-babel-noweb-wrap-start "__NREF__")
(setq org-babel-noweb-wrap-end "")

(defun codex-nref-rx (match-optional-params)
  (rx-to-string
   (codex-nref-rx-primitive match-optional-params)))

(defun codex-nref-rx-primitive (match-optional-params)
  (if match-optional-params
   `(group
           "__NREF__"
          (any alpha) ;; Noweb reference must start with a letter...
          ;; ...and must be followed by letters,numbers,dashes,underscores,periods...
          (* (or (any alnum) "-" "_" "."))
          ;; ...and may terminate with a "(...)" where the "..." may be an empty string, or some other argument.
          (* (or "()"
                 (and "("
                      (* (not ")"))
                      ")"))))
   `(group
          "__NREF__"
          (any alpha)
          (* (or (any alnum) "-" "_" ".")))))

;; Customize noweb delimiters. Unlike traditional << and >> delimiters, we just use the "__NREF__" prefix as our only delimiter. This has the advantage of being encoded the same way into HTML, which makes our HTML modifications easier and more consistent across different source code languages.
;; See https://emacs.stackexchange.com/a/73720/13006.
(defun org-babel-noweb-wrap (&optional regexp)
  "Return regexp matching a Noweb reference.

Match any reference, or only those matching REGEXP, if non-nil.
When matching, reference is stored in match group 1."
  (codex-nref-rx t))

(setq codex-polyblock-names (make-hash-table :test 'equal))
(setq codex-polyblock-names-totals (make-hash-table :test 'equal))

(defun codex-prettify-source-code-captions (src-block-html backend info)
  (when (org-export-derived-backend-p backend 'html)
    ;; Break up source block into 3 subparts --- the leading <div ...>, the <label ...></label> (if any) and
    ;; <pre ...></pre>.
    ;; Then run the linkifying logic against only the body, and then return the
    ;; original label and new body.
    (let* ((div-caption-body (codex-get-source-block-html-parts-without-newlines src-block-html))
           (leading-div (nth 0 div-caption-body))
           (body (nth 2 div-caption-body))
           (pre-id-match
             (string-match
               (rx-to-string
                 '(and
                       "<pre "
                       (* (not ">"))
                       "id=\""
                       (group (+ (not "\"")))))
               body))
           (pre-id
             (if pre-id-match
                 (match-string-no-properties 1 body)
                 "#deadlink"))
           (body-with-newlines
            (codex-to-multi-line body))
           (caption (nth 1 div-caption-body))
           (caption-parts
             (let* ((caption-match
                      (string-match "<label [^>]+>\\(.*?\\)</label>" caption)))
               (if caption-match
                   (match-string-no-properties 1 caption)
                   "")))
           (source-block-name-match
             (string-match
               (rx-to-string
                 '(and
                       "<code>"
                       (group (+ (not "<")))
                       "</code>"))
               caption-parts))
           ;; A source code block is anonymous if: (1) it does not have a "#+name: ..." line, or (2) it does not have a "#+header: :noweb-ref ..." line.
           (source-block-name
             (if source-block-name-match
                 (match-string-no-properties 1 caption-parts)
                 "anonymous"))
           ;; This is just used for the side effect of recording the
           ;; source-block-name, to be used for the fallback-id.
           (source-block-counter (gethash source-block-name codex-polyblock-names 0))
           (source-block-counter-incremented (puthash source-block-name (+ 1 source-block-counter) codex-polyblock-names))
           (source-block-name-styled
             (cond ((string-prefix-p "__NREF__" source-block-name)
                    (concat
                      "<span class=\"codex-caption-source-code-block-name\">"
                      (string-remove-prefix "__NREF__" source-block-name)
                      "</span>"))
                   (t
                    (concat
                      "<span class=\"codex-caption-source-code-block-name\">"
                      "&#x1f4c4; "
                      source-block-name
                      "</span>"))))
           (polyblock-chain-total (gethash source-block-name codex-polyblock-names-totals 0))
           (polyblock-chain-location (if (= polyblock-chain-total 0) "" (format "(%s of %s) " source-block-counter-incremented polyblock-chain-total)))
           (polyblock-indicator
             (if (string-match "\(polyblock\)" caption-parts)
                 polyblock-chain-location ""))
           (parent-id-match
             (string-match
               (rx-to-string
                 '(and
                       " <a href=\""
                       (group (+ (not "\"")))))
               caption-parts))
           (parent-id
             (if parent-id-match
                 (format "<span class=\"codex-caption-parent-link\"><a href=\"%s\">%s</a></span>"
                   (match-string-no-properties 1 caption-parts) (string-remove-prefix "__NREF__" source-block-name))
                 ""))
           ;; For polyblocks, only the first (head) block gets an id field for a
           ;; <pre> tag. The rest (tail) don't have this field so they would
           ;; normally get assigned a deadlink. To avoid this, use a counter for
           ;; the parent-id, because this parent-id is shared across all
           ;; polyblocks. Then use this with the parent-id to generate an
           ;; alternate, fallback-id. This way the tail polyblocks get assigned
           ;; a unique (meaningful) ID and not just "##deadlink".
           (fallback-id
             (if (string= pre-id "#deadlink")
                 (format "%s-%s" source-block-name source-block-counter-incremented)
                 pre-id))
           (pre-tag-match
             (string-match
               (rx-to-string
                 '(and
                       "<pre "
                       (group (* (not ">")))
                       ">"))
               body))
           (pre-tag-entire (match-string-no-properties 0 body))
           (pre-tag-contents (match-string-no-properties 1 body))
           (body-with-replaced-pre
             (if pre-id-match
                 body-with-newlines
                 (string-replace pre-tag-entire
                                 (concat "<pre " pre-tag-contents
                                         (format " id=\"%s\"" fallback-id) ">") body-with-newlines)))
           (link-symbol
             (format "<span class=\"codex-caption-link-symbol\"><a href=\"#%s\">&#x1f517;</a></span>"
               fallback-id))
           (caption-without-listing-prefix (replace-regexp-in-string "<span.+?span>" "" caption))
           (caption-text
            (if (s-blank? parent-id)
                (concat
                  "<div class=\"codex-caption\">"
                    caption-without-listing-prefix
                    link-symbol
                  "</div>")
                (concat
                  "<div class=\"codex-caption\">"
                    polyblock-indicator
                    parent-id
                    link-symbol
                  "</div>")))
           )
      (if (s-blank? caption)
       src-block-html
       (concat
        leading-div
          "<div class=\"codex-pre-with-caption\">"
            caption-text
            body-with-replaced-pre
          "</div>"
        "</div>")))))

(defun codex-get-source-block-html-parts-without-newlines (src-block-html)
    (let* ((one-line (codex-to-single-line src-block-html))
           (leading-div
             (let ((div-match
                    (string-match "<div [^>]+>" one-line)))
               (match-string-no-properties 0 one-line)))
           (caption
             (let* ((caption-match
                      (string-match "<label [^>]+>.*?</label>" one-line)))
               (if caption-match
                   (match-string-no-properties 0 one-line)
                   "")))
           (body (progn (string-match "<pre [^>]+>.*?</pre>" one-line)
                        (match-string-no-properties 0 one-line))))
      `(,leading-div ,caption ,body)))

; Define a global hash table for mapping Org-mode-generated ids (that look like "org00012") for source code blocks to a more human-readable ID.
(setq codex-org_id-human_id-hash-table (make-hash-table :test 'equal))

(defun codex-populate-org_id-human_id-hash-table (src-block-html backend info)
  (when (org-export-derived-backend-p backend 'html)
    (let* ((block-name (codex-get-src-block-name-from-html src-block-html))
           (orgid (codex-get-src-block-HTML_ID src-block-html)))
      (when orgid
        (puthash orgid block-name codex-org_id-human_id-hash-table))
      src-block-html)))

(defun codex-replace-org_ids-with-human_ids (entire-html backend info)
  (when (org-export-derived-backend-p backend 'html)
    (let ((html-oneline (codex-to-single-line entire-html)))
      (maphash
       (lambda (k v)
        (when (and k v)
         (setq html-oneline
               (replace-regexp-in-string
                (rx-to-string `(and " id=" (* (not "\"")) "\"" ,k "\""))
                (format " id=\"%s\"" v) html-oneline))
         (setq html-oneline
               (replace-regexp-in-string
                (rx-to-string `(and " href=" (* (not "\"")) "\"#" ,k "\""))
                (format " href=\"#%s\"" v) html-oneline))))
       codex-org_id-human_id-hash-table)
      (codex-to-multi-line html-oneline))))

(defun batch-org-gen-css-and-exit (org-file)
  (find-file org-file)
  (font-lock-flush)
  (font-lock-fontify-buffer)
  (org-html-htmlize-generate-css)
  (with-current-buffer "*html*"
    (write-file "syntax-highlighting.css"))
  (kill-emacs))

;; Without this, batch-org-gen-css-and-exit produces a near-empty CSS file.
(require 'font-lock)
(require 'subr-x) ;; for `when-let'

(unless (boundp 'maximal-integer)
  (defconst maximal-integer (lsh -1 -1)
    "Maximal integer value representable natively in emacs lisp."))

(defun face-spec-default (spec)
  "Get list containing at most the default entry of face SPEC.
Return nil if SPEC has no default entry."
  (let* ((first (car-safe spec))
     (display (car-safe first)))
    (when (eq display 'default)
      (list (car-safe spec)))))

(defun face-spec-min-color (display-atts)
  "Get min-color entry of DISPLAY-ATTS pair from face spec."
  (let* ((display (car-safe display-atts)))
    (or (car-safe (cdr (assoc 'min-colors display)))
    maximal-integer)))

(defun face-spec-highest-color (spec)
  "Search face SPEC for highest color.
That means the DISPLAY entry of SPEC
with class 'color and highest min-color value."
  (let ((color-list (cl-remove-if-not
             (lambda (display-atts)
               (when-let ((display (car-safe display-atts))
                  (class (and (listp display)
                          (assoc 'class display)))
                  (background (assoc 'background display)))
             (and (member 'light (cdr background))
                  (member 'color (cdr class)))))
             spec)))
    (cl-reduce (lambda (display-atts1 display-atts2)
         (if (> (face-spec-min-color display-atts1)
            (face-spec-min-color display-atts2))
             display-atts1
           display-atts2))
           (cdr color-list)
           :initial-value (car color-list))))

(defun face-spec-t (spec)
  "Search face SPEC for fall back."
  (cl-find-if (lambda (display-atts)
        (eq (car-safe display-atts) t))
          spec))

; This is slightly tweaked from the original, because the incoming "face" value can look like (fixed-pitch face-name) --- so we take the second element.
(defun my-face-attribute (face attribute &optional frame inherit)
  "Get FACE ATTRIBUTE from `face-user-default-spec' and not from `face-attribute'."
  (let* ((face-spec (face-user-default-spec (if (listp face) (car (cdr face)) face)))
     (display-attr (or (face-spec-highest-color face-spec)
               (face-spec-t face-spec)))
     (attr (cdr display-attr))
     (val (or (plist-get attr attribute) (car-safe (cdr (assoc attribute attr))))))
    ;; (message "attribute: %S" attribute) ;; for debugging
    (when (and (null (eq attribute :inherit))
           (null val))
      (let ((inherited-face (my-face-attribute face :inherit)))
    (when (and inherited-face
           (null (eq inherited-face 'unspecified)))
      (setq val (my-face-attribute inherited-face attribute)))))
    ;; (message "face: %S attribute: %S display-attr: %S, val: %S" face attribute display-attr val) ;; for debugging
    (or val 'unspecified)))

(advice-add 'face-attribute :override #'my-face-attribute)

;; Debugging
(defmacro print-args-and-ret (fun)
  "Prepare FUN for printing args and return value."
  `(advice-add (quote ,fun) :around
           (lambda (oldfun &rest args)
         (let ((ret (apply oldfun args)))
           (message ,(concat "Calling " (symbol-name fun) " with args %S returns %S.") args ret)
           ret))
           '((name "print-args-and-ret"))))

; (print-args-and-ret htmlize-faces-in-buffer)
; (print-args-and-ret htmlize-get-override-fstruct)
; (print-args-and-ret htmlize-face-to-fstruct)
; (print-args-and-ret htmlize-attrlist-to-fstruct)
; (print-args-and-ret face-foreground)
; (print-args-and-ret face-background)
; (print-args-and-ret face-attribute)

(setq make-backup-files nil)
(setq org-src-preserve-indentation t)

; See https://stackoverflow.com/a/27285582/437583.
(defun codex-test-file-name ()
  (concat "test_" (file-name-nondirectory (directory-file-name (file-name-directory (buffer-file-name))))  ".py"))

(setq org-html-doctype "html5")
