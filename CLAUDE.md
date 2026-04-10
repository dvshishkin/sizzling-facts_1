# CLAUDE.md — sizzling-facts

Персональный сайт Ивана Шишкина. Hugo + GitHub Pages.
Репо: https://github.com/dvshishkin/sizzling-facts_1
Живой сайт: https://dvshishkin.github.io/sizzling-facts_1/

---

## Стек

- Hugo Extended 0.128.0
- GitHub Actions (deploy.yml) — `hugo --minify` → Pagefind → pages artifact
- Pagefind — поисковый индекс строится автоматически при деплое
- Двуязычность: ru (дефолт, `/`), en (`/en/`)

## Структура

```
content/
  _index.md / _index.en.md     — лендинг
  about/_index.md / .en.md     — обо мне
  projects/_index.md / .en.md  — проекты
  portfolio/_index.md / .en.md — портфолио (фото сюда)
  blog/                        — только RU, без .en.md

layouts/
  index.html                   — лендинг (5 секций)
  _default/baseof.html         — обёртка
  _default/list.html           — блог-список + другие секции
  _default/single.html         — статья
  partials/header.html         — шапка + переключатель языка
  partials/footer.html
  shortcodes/gallery.html

i18n/ru.yaml / en.yaml         — переводы (map-формат)
assets/css/main.css            — единый CSS
```

## Критические правила — Hugo + GitHub Pages с subpath

**URL строить ТОЛЬКО через `{{ .Site.BaseURL }}`:**
```html
<!-- ПРАВИЛЬНО -->
<a href="{{ .Site.BaseURL }}about/">
<a href="{{ $base }}{{ $lang }}/about/">

<!-- СЛОМАЕТ GitHub Pages (subpath /sizzling-facts_1/ игнорируется) -->
<a href="{{ "/about/" | absLangURL }}">
<a href="{{ "/about/" | relLangURL }}">
```

**Язык проверять через `.Lang`:**
```html
{{- $isDefault := eq .Lang "ru" }}
<!-- НЕ использовать .Site.DefaultContentLanguage — недоступен в Hugo 0.128.0 -->
```

**`cond` падает если поле не bool:**
```html
<!-- Если поле может быть nil — использовать if/else, не cond -->
{{- if .absolute }}...{{- else }}...{{- end }}
```

**i18n — только map-формат:**
```yaml
# ПРАВИЛЬНО
about: "Обо мне"

# НЕ РАБОТАЕТ надёжно
- id: about
  translation: "Обо мне"
```

## Ключевые параметры hugo.toml

- `defaultContentLanguage = "ru"` — русский без префикса
- `defaultContentLanguageInSubdir = false` — RU на `/`, EN на `/en/`
- `baseURL = "https://dvshishkin.github.io/sizzling-facts_1/"`
- Блог-секция имеет `absolute = true` — всегда ссылается на `/blog/` без языкового префикса

## Что ещё предстоит

1. Наполнить контент: `content/about/_index.md`, `content/projects/_index.md` и `.en.md`-версии
2. Экспорт блога из Ghost (JSON → Hugo Markdown)
3. Перенос изображений из Ghost в `content/blog/`
4. Смена домена: поменять `baseURL` на `https://sizzling-facts.com/` и убрать subpath из всех ссылок
