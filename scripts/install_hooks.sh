#!/usr/bin/env bash
# Устанавливает pre-commit hook для автофикса путей к картинкам.
# Запускать один раз после клонирования репозитория:
#   bash scripts/install_hooks.sh

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOK_FILE="$HOOKS_DIR/pre-commit"
SCRIPT="$REPO_ROOT/scripts/fix_image_paths.py"

# Проверяем, что скрипт на месте
if [ ! -f "$SCRIPT" ]; then
  echo "❌  Не найден $SCRIPT"
  exit 1
fi

# Если хук уже существует — не затираем, а дописываем вызов
if [ -f "$HOOK_FILE" ]; then
  if grep -q "fix_image_paths.py" "$HOOK_FILE"; then
    echo "✅  pre-commit hook уже содержит fix_image_paths — ничего не меняю."
    exit 0
  fi
  echo "⚠   pre-commit hook уже существует, дописываю вызов в конец."
  cat >> "$HOOK_FILE" <<'EOF'

# fix Obsidian image paths → Hugo paths (добавлено install_hooks.sh)
python3 "$(git rev-parse --show-toplevel)/scripts/fix_image_paths.py"
EOF
else
  # Создаём новый хук
  cat > "$HOOK_FILE" <<'EOF'
#!/usr/bin/env bash
# pre-commit hook: fix Obsidian image paths → Hugo paths

python3 "$(git rev-parse --show-toplevel)/scripts/fix_image_paths.py"
EOF
  chmod +x "$HOOK_FILE"
fi

echo "✅  pre-commit hook установлен: $HOOK_FILE"
echo "    Теперь при каждом git commit пути к картинкам исправляются автоматически."
echo "    Локальные файлы остаются нетронутыми (Obsidian продолжает их видеть)."
