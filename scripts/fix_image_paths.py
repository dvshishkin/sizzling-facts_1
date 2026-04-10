#!/usr/bin/env python3
"""
Pre-commit hook: fixes Obsidian image paths → Hugo-compatible paths.

Работает с git INDEX, рабочий файл не трогает. Поэтому:
  - В Obsidian локально: ![alt](static/images/2026/04/photo.jpg)  ← Obsidian видит и показывает
  - В коммите:           ![alt](/sizzling-facts_1/images/2026/04/photo.jpg)  ← Hugo видит правильно

Что фиксит:
  1. Пути к картинкам в теле поста:
       ![alt](static/images/...) → ![alt](/sizzling-facts_1/images/...)
  2. Поле cover: в front matter:
       cover: "static/images/..." → cover: "/sizzling-facts_1/images/..."
  3. Wikilinks-картинки (если вдруг забыть выключить в Obsidian):
       ![[photo.jpg]] → WARNING, путь не трогает (нужно вручную)

Что НЕ трогает:
  - Уже правильные пути: /sizzling-facts_1/images/...
  - Внешние URL: http://, https://
  - Всё остальное (ссылки без картинок, shortcodes и т.д.)
"""

import re
import sys
import os
import subprocess
import tempfile

# ── Настройки ──────────────────────────────────────────────────────────────
OBSIDIAN_PREFIX = "static/images/"
HUGO_PREFIX     = "/sizzling-facts_1/images/"
CONTENT_DIR     = "content/"   # только файлы в content/ обрабатываются
# ───────────────────────────────────────────────────────────────────────────


def fix_content(text: str) -> tuple[str, list[str]]:
    """
    Возвращает (исправленный текст, список предупреждений).
    """
    warnings = []
    count = 0

    # 1. Тело поста: ![alt](static/images/...)
    #    Не трогаем: уже /..., http/https://...
    def fix_inline_image(m):
        nonlocal count
        alt  = m.group(1)
        path = m.group(2)
        # Уже абсолютный или внешний — пропускаем
        if path.startswith(("/", "http://", "https://")):
            return m.group(0)
        if path.startswith(OBSIDIAN_PREFIX):
            count += 1
            return f"![{alt}]({HUGO_PREFIX}{path[len(OBSIDIAN_PREFIX):]})"
        return m.group(0)

    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', fix_inline_image, text)

    # 2. Front matter cover: "static/images/..."
    #    Поддерживаем и одинарные, и двойные кавычки, и без кавычек
    def fix_cover(m):
        nonlocal count
        quote = m.group(1)   # кавычка (может быть пустой)
        path  = m.group(2)
        if path.startswith(("/", "http://", "https://")):
            return m.group(0)
        if path.startswith(OBSIDIAN_PREFIX):
            count += 1
            new_path = HUGO_PREFIX + path[len(OBSIDIAN_PREFIX):]
            return f"cover: {quote}{new_path}{quote}"
        return m.group(0)

    text = re.sub(
        r'^cover:\s*(["\']?)(' + re.escape(OBSIDIAN_PREFIX) + r'[^"\'\s]+)\1',
        fix_cover,
        text,
        flags=re.MULTILINE,
    )

    # 3. Wikilinks ![[...]] — предупреждаем, не трогаем
    wikilinks = re.findall(r'!\[\[([^\]]+)\]\]', text)
    for wl in wikilinks:
        warnings.append(f"  ⚠  Wikilink не фиксится автоматически: ![[{wl}]]  — переключи в Obsidian на стандартные ссылки")

    return text, warnings


# ── Git-утилиты ────────────────────────────────────────────────────────────

def get_staged_md_files() -> list[str]:
    """Список .md файлов в content/, добавленных/изменённых в стейдже."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True, check=True,
    )
    return [
        f for f in result.stdout.splitlines()
        if f.endswith(".md") and f.startswith(CONTENT_DIR)
    ]


def read_from_index(rel_path: str) -> bytes:
    """Читает содержимое файла из git index (не с диска)."""
    result = subprocess.run(
        ["git", "show", f":{rel_path}"],
        capture_output=True, check=True,
    )
    return result.stdout


def write_to_index(rel_path: str, content: bytes) -> None:
    """Записывает исправленный контент в git index, не трогая диск."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Создаём git-объект
        result = subprocess.run(
            ["git", "hash-object", "-w", tmp_path],
            capture_output=True, text=True, check=True,
        )
        obj_hash = result.stdout.strip()

        # Обновляем index (рабочий файл не изменяется)
        subprocess.run(
            ["git", "update-index", "--cacheinfo", f"100644,{obj_hash},{rel_path}"],
            check=True,
        )
    finally:
        os.unlink(tmp_path)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    try:
        staged = get_staged_md_files()
    except subprocess.CalledProcessError as e:
        print(f"fix_image_paths: ошибка git: {e}", file=sys.stderr)
        sys.exit(1)

    if not staged:
        sys.exit(0)

    fixed_files   = []
    all_warnings  = []

    for rel_path in staged:
        try:
            raw = read_from_index(rel_path)
        except subprocess.CalledProcessError:
            continue

        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue

        fixed_text, warnings = fix_content(text)

        if warnings:
            all_warnings.extend([f"  [{rel_path}]"] + warnings)

        if fixed_text != text:
            write_to_index(rel_path, fixed_text.encode("utf-8"))
            fixed_files.append(rel_path)

    if fixed_files:
        print("🔧 fix_image_paths: пути исправлены в коммите (локальные файлы не тронуты):")
        for f in fixed_files:
            print(f"   ✓ {f}")

    if all_warnings:
        print("\n" + "\n".join(all_warnings))

    sys.exit(0)


if __name__ == "__main__":
    main()
