# CLAUDE.md — sizzling-facts

Персональный сайт Ивана Шишкина. Hugo + GitHub Pages.
Репо: https://github.com/dvshishkin/sizzling-facts_1
Живой сайт: https://dvshishkin.github.io/sizzling-facts_1/

---

## Стек

- Hugo Extended 0.128.0
- GitHub Actions (deploy.yml) — `hugo --minify` → Pagefind → pages artifact
- Pagefind — поисковый индекс строится автоматически при деплое
- GLightbox — лайтбокс для галерей (подключается только на страницах с `{{< gallery >}}`)
- Двуязычность: ru (дефолт, `/`), en (`/en/`)

## Структура проекта

```
hugo.toml                        — конфиг, языки, параметры навигации
i18n/ru.yaml / en.yaml           — ВСЕ тексты интерфейса и навигации

content/
  _index.md / _index.en.md       — лендинг (5 секций)
  about/_index.md / .en.md       — Обо мне
  projects/_index.md / .en.md    — Проекты
  portfolio/_index.md / .en.md   — Портфолио
  blog/                          — только RU
    _index.md                    — заголовок и описание раздела

layouts/
  index.html                     — лендинг
  _default/baseof.html           — базовая обёртка
  _default/list.html             — блог-список + секции
  _default/single.html           — статья
  _default/_markup/render-image.html — render hook: alt → <figcaption>
  partials/header.html           — шапка + переключатель языка
  partials/head.html             — <meta>, CSS, GLightbox, Pagefind
  partials/footer.html
  shortcodes/gallery.html        — сетка 3 кол. + GLightbox

assets/css/main.css              — единый CSS
static/images/                   — все фото (Hugo отдаёт рекурсивно)
scripts/
  fix_image_paths.py             — конвертер путей Obsidian→Hugo (git index)
  install_hooks.sh               — установщик pre-commit hook
```

---

## Где менять названия разделов

**Навигация и все тексты интерфейса** — только в i18n:
- `i18n/ru.yaml` — русская версия
- `i18n/en.yaml` — английская версия

Ключи навигации:
```yaml
about:     "Обо мне"        # ← менять здесь
interests: "Интересы"
projects:  "Проекты"
portfolio: "Портфолио"
blog:      "Блог"
```

Заголовки секций лендинга (крупный текст внутри блока):
```yaml
section_label_about:     "Обо мне"
section_label_interests: "Интересы"
section_label_projects:  "Проекты и воркшопы"
section_label_portfolio: "Фото-портфолио"
section_label_blog:      "Последнее из блога"
```

Остальное в i18n-файлах: подписи кнопок, плейсхолдер поиска, tagline.

**Порядок пунктов меню** — в `hugo.toml`, секция `[[params.sections]]`.

---

## Наполнение контента

### Новый пост в блог
Файл: `content/blog/slug-poста.md`

Front matter:
```yaml
---
title: "Заголовок"
date: 2026-04-10
slug: "slug-posta"
cover: "static/images/2026/04/cover.jpg"   ← Obsidian-путь, hook исправит
excerpt: "Краткое описание. Можно [ссылки](https://t.me/fullscoop)."
tags: ["ферментация"]
draft: false
---
```

### Разделы (about, projects, portfolio)
Файл: `content/about/_index.md`

```yaml
---
title: "Обо мне"
---
Обычный markdown-контент.
```

### Портфолио
Файл: `content/portfolio/_index.md` — туда идёт markdown с галереями:
```
{{< gallery caption="Гамбург, весна 2026" >}}
![Подпись](static/images/2026/04/photo.jpg)
![Подпись](static/images/2026/04/photo2.jpg)
{{< /gallery >}}
```

---

## Obsidian — рабочий процесс

**Настройки Obsidian (один раз):**
- Vault = папка `sizzling-facts/`
- Settings → Files & Links → Use [[Wikilinks]]: **выключить**
- New link format: **Absolute path in vault**
- Attachments folder: `static/images`

**Workflow:**
1. Пишешь пост в Obsidian, перетаскиваешь фото — они падают в `static/images/`
2. Ссылки вида `static/images/photo.jpg` — Obsidian показывает превью
3. `git add` + `git commit` — pre-commit hook автоматически конвертирует пути в коммите в `/sizzling-facts_1/images/photo.jpg`
4. Локальный файл остаётся нетронутым

**После клонирования репо** установить хук:
```bash
bash scripts/install_hooks.sh
```

---

## Критические правила — Hugo + GitHub Pages с subpath

**URL строить ТОЛЬКО через `{{ .Site.BaseURL }}`:**
```html
<!-- ПРАВИЛЬНО -->
<a href="{{ .Site.BaseURL }}about/">

<!-- СЛОМАЕТ (subpath /sizzling-facts_1/ игнорируется) -->
<a href="{{ "/about/" | absLangURL }}">
<a href="{{ "/about/" | relLangURL }}">
```

**Язык проверять через `.Lang`:**
```html
{{- $isDefault := eq .Lang "ru" }}
<!-- НЕ использовать .Site.DefaultContentLanguage — недоступен в Hugo 0.128.0 -->
```

**i18n — только map-формат:**
```yaml
# ПРАВИЛЬНО
about: "Обо мне"

# НЕ РАБОТАЕТ надёжно
- id: about
  translation: "Обо мне"
```

**Пути к картинкам в шаблонах:**
```html
<!-- В .md-файлах после hook: /sizzling-facts_1/images/... — уже абсолютные -->
<!-- В шаблонах Hugo: использовать {{ . | absURL }} для og:image -->
```

**`markdownify` для front matter полей с разметкой:**
```html
{{ .Params.excerpt | markdownify }}       <!-- рендерит ссылки, bold и т.д. -->
{{ .Description | markdownify | plainify }} <!-- для <meta> — чистый текст -->
```

**`cond` падает если поле не bool — использовать if/else.**

---

## Ключевые параметры hugo.toml

- `defaultContentLanguage = "ru"` — русский без префикса
- `defaultContentLanguageInSubdir = false` — RU на `/`, EN на `/en/`
- `baseURL = "https://dvshishkin.github.io/sizzling-facts_1/"` ← при переносе на домен менять здесь

---

## Локальный запуск

```bash
cd ~/Documents/Claude/Projects/Сайт\ на\ GitHub/sizzling-facts
hugo server
```
Сайт на http://localhost:1313/sizzling-facts_1/

---

## Переход на домен sizzling-facts.com (когда придёт время)

1. `hugo.toml` → `baseURL = "https://sizzling-facts.com/"`
2. Все захардкоженные пути `/sizzling-facts_1/images/` в .md-файлах → `/images/`
3. В `scripts/fix_image_paths.py` поменять `HUGO_PREFIX = "/images/"`
4. В GitHub: Settings → Pages → Custom domain → `sizzling-facts.com`
5. У регистратора домена: CNAME `dvshishkin.github.io`

---

## Что предстоит

- Наполнить `content/about/`, `content/projects/`, `content/portfolio/`
- Черновик «Veddel Gallery» (был draft в Ghost — не перенесён)
- Перенос на домен sizzling-facts.com
