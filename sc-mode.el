;;; sc-mode.el --- Major mode for editing SC files

(defvar sc-mode-hook nil)

(defconst sc-comment-re      "\\(^#.*\\)" "" )
(defconst sc-plingcomment-re "\\(!.*\\)" "" )
(defconst sc-spword-re
       "\\(SKIP\\|NOSKIP\\|END\\|PRE\\|POST\\|BEFORE\\)" "" )

(defconst sc-catdef-re   "\\(^\\w+\\)\s*=" "" )
(defconst sc-catval-re   "=\s*\\(.+\\)" "" )
(defconst sc-dialects-re "\\(^\\w+\\)\s*[^=]" "" )

(defconst sc-cat1-re     "<\\(\\w*\\)>" "" )
(defconst sc-cat2-re     "<\\^\\(\\w*\\)>" "" )
(defconst sc-cat3-re     "<\\(\\w+\\)[-+]" "" )
(defconst sc-cat4-re     "<[-+]\\(\\w*\\)>" "" )
(defconst sc-cat5-re     "<.*[-+]\\(\\w*\\)>" "" )
(defconst sc-cat6-re     ":\\(\\w+\\):" "" )
(defconst sc-cat7-re     ":\\(\\w+\\)\\}" "" )
(defconst sc-cat8-re     "\{.\\(\\w+\\)\}" "" )

(defconst sc-env-re     "\\(@\\w+\\)" "" )
(defconst sc-index1-re  "\\(#[0-9]\\)" "" )
(defconst sc-index2-re  "\{\\([0-9<>%]\\)" "" )

(defconst sc-special-re "\\([#%<|>`={}:]\\)" "" )
(defconst sc-text-re    "\\(\\w+\\)" "" )
(defconst sc-regexp-re  "\\([-+*|?^]\\)" "" )
(defconst sc-flag-re    "\s\\(\\w+\\)$" "" )

; (defconst sc-envalt-re  "\\({\\w+}\\)" "" )

(defvar sc-font-lock-keywords
  (list
    (cons sc-comment-re      '(1 font-lock-comment-face))
    (cons sc-plingcomment-re '(1 font-lock-comment-face))
    (cons sc-spword-re       '(1 font-lock-keyword-face))

    (cons sc-catdef-re       '(1 font-lock-variable-name-face))
    (cons sc-catval-re       '(1 font-lock-string-face))
    (cons sc-dialects-re     '(1 font-lock-constant-face))

    (cons sc-cat1-re         '(1 font-lock-variable-name-face))
    (cons sc-cat2-re         '(1 font-lock-variable-name-face))
    (cons sc-cat3-re         '(1 font-lock-variable-name-face))
    (cons sc-cat4-re         '(1 font-lock-string-face))
    (cons sc-cat5-re         '(1 font-lock-string-face))
    (cons sc-cat6-re         '(1 font-lock-variable-name-face))
    (cons sc-cat7-re         '(1 font-lock-variable-name-face))
    (cons sc-cat8-re         '(1 font-lock-variable-name-face))

    (cons sc-env-re          '(1 font-lock-variable-name-face))
    (cons sc-index1-re       '(1 font-lock-constant-face))
    (cons sc-index2-re       '(1 font-lock-constant-face))

    (cons sc-special-re      '(1 font-lock-type-face))
    (cons sc-regexp-re       '(1 font-lock-keyword-face))
    (cons sc-flag-re         '(1 font-lock-keyword-face))
    (cons sc-text-re         '(1 font-lock-constant-face))
  )
  "Minimal highlighting expressions for sc mode")

(defun sc-mode ()
  "Major mode for editing files for Geoff's Sound Change Applier"
  (interactive)
  (kill-all-local-variables)
  (set (make-local-variable 'font-lock-defaults)
       '(sc-font-lock-keywords))
)
