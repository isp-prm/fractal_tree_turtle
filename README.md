# Fractal Tree (turtle + minimal UI) — macOS

Приложение на Python, рисующее фрактал "дерево" с помощью turtle.
UI выполнен на tkinter, turtle рисует на встроенном Canvas.

Параметры доступные для изменения:
- Depth (Количество шагов)
- Angle (Угол между ветвями)
- Shrink (Величина уменьшения длины ветви на каждом шаге)
- Thickness (Толщина)
- Th.decey (Величина уменьшения толщины ветви на каждом шаге)
- Randomness (Величина внесения фактора случайности)
- Seed (Добавление случайно составляющей)
- Stroke (Возможность выбора фигруы для рисования: линия либо четерхугольник)
- Palette (Цветовые режимы отрисовки)

## Требования
- Python 3.10+ (на macOS обычно: python3)
- Tkinter (обычно уже есть вместе с Python.org installer)

Проверка tkinter:
```bash
python3 -c "import tkinter; print('tk ok')"
# fractal_tree_turtle
