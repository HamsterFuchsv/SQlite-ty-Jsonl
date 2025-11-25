import sys
import subprocess
import time
import os
import sqlite3
import json
import art 

# --- АВТОМАТИЧЕСКАЯ УСТАНОВКА ЗАВИСИМОСТЕЙ ---
def install_dependencies():
    """Проверяет и устанавливает необходимые пакеты, если они отсутствуют."""
    required_packages = ['art'] 
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("🛠️ Обнаружены отсутствующие зависимости. Попытка установки...")
        print(f"   Установка: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("✅ Зависимости успешно установлены.")
            time.sleep(1) 
        except subprocess.CalledProcessError:
            print("❌ Ошибка при установке зависимостей с помощью pip. Проверьте подключение.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Непредвиденная ошибка при установке: {e}")
            sys.exit(1)

install_dependencies()
# ---------------------------------------------

def print_title():
    """Печатает стилизованный заголовок скрипта."""
    try:
        ascii_art = art.text2art("SQlite3 ty JsonL", font='small')
        title = f"{ascii_art}\n by HamsterFuchs\n"
        print(title)
    except Exception:
        print("--- SQlite3 ty JsonL by hamsterfuchs ---")

def select_db_file():
    """Позволяет пользователю выбрать файл SQLite3 с помощью нумерованного списка."""
    valid_extensions = ('.sqlite3', '.db', '.sqlite', '.SQLite3', '.DB', '.SQLite')
    db_files = [f for f in os.listdir('.') if f.endswith(valid_extensions)]
    
    if not db_files:
        print("❌ Ошибка: В текущей папке не найдено файлов SQLite3 (.sqlite3, .db, .sqlite).")
        return None

    print("\nВыберите файл SQLite3 для конвертации:")
    for i, file in enumerate(db_files):
        print(f"[{i+1}] {file}")

    while True:
        selection = input("Введите номер файла (или 'q' для выхода): ")
        if selection.lower() == 'q':
            print("🚫 Выбор файла отменен. Выход.")
            return None
        
        try:
            index = int(selection) - 1
            if 0 <= index < len(db_files):
                selected_file = db_files[index]
                return os.path.abspath(selected_file)
            else:
                print("⚠️ Неверный номер. Попробуйте еще раз.")
        except ValueError:
            print("⚠️ Неверный ввод. Введите номер или 'q'.")

def list_and_select_tables(db_path):
    """Подключается к БД и позволяет выбрать таблицы для конвертации."""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        all_tables = [row[0] for row in cursor.fetchall()]

        if not all_tables:
            print(f"❌ В базе данных не найдено таблиц.")
            return None

        print("\nВыберите таблицы для конвертации:")
        for i, table in enumerate(all_tables):
            print(f"[{i+1}] {table}")

        while True:
            selection = input("Введите номера таблиц через запятую (например, '1,3,5' или 'q' для выхода): ")
            if selection.lower() == 'q':
                return []
            
            try:
                selected_indices = []
                input_parts = [p.strip() for p in selection.split(',') if p.strip()]
                
                if not input_parts:
                    print("⚠️ Ничего не выбрано. Попробуйте еще раз.")
                    continue
                
                for part in input_parts:
                    index = int(part) - 1
                    if 0 <= index < len(all_tables):
                        selected_indices.append(index)
                    else:
                        raise ValueError(f"Неверный номер: {part}")
                
                unique_indices = sorted(list(set(selected_indices)))
                selected_tables = [all_tables[i] for i in unique_indices]
                return selected_tables

            except ValueError as e:
                print(f"⚠️ Неверный ввод: {e}. Попробуйте еще раз.")

    except sqlite3.OperationalError as e:
        print(f"❌ Ошибка SQLite: Не удалось открыть базу данных. Ошибка: {e}", file=sys.stderr)
        return None
    finally:
        if conn:
            conn.close()

def convert_table_to_jsonl(db_path, table_name, outfile):
    """
    Извлекает данные из одной таблицы и записывает в ОБЩИЙ файл (outfile).
    """
    conn = None
    rows_processed = 0
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()

        print(f"   [--] Обработка таблицы: '{table_name}'...")
        
        query = f"SELECT * FROM \"{table_name}\"" 
        cursor.execute(query)

        for row in cursor:
            data_dict = dict(row)
            json_line = json.dumps(data_dict, ensure_ascii=False)
            outfile.write(json_line + '\n')
            rows_processed += 1
        
        print(f"   [--] **ГОТОВО**: Таблица '{table_name}'. Обработано строк: {rows_processed}")
        return rows_processed

    except sqlite3.OperationalError as e:
        print(f"   [❌] Ошибка SQLite при чтении таблицы '{table_name}': {e}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"   [❌] Непредвиденная ошибка при конвертации таблицы '{table_name}': {e}", file=sys.stderr)
        return 0
    finally:
        if conn:
            conn.close()

def main():
    print_title()
    
    # 1. Выбор DB файла
    db_file_path = select_db_file()
    if not db_file_path:
        return
        
    print(f"\n✅ Выбран файл: {db_file_path}")
    print("-" * 50)

    # Определяем директорию и имя выходного файла
    base_name = os.path.basename(db_file_path)
    root, ext = os.path.splitext(base_name)
    
    # Формируем имя: [BTI'15] + ByHamsterFuchs.jsonl
    output_file_name = f"{root}ByHamsterFuchs.jsonl"
    output_directory = os.path.dirname(db_file_path) or os.getcwd()
    output_file_path = os.path.join(output_directory, output_file_name)


    # 2. Выбор таблиц
    selected_tables = list_and_select_tables(db_file_path)
    if selected_tables is None:
        return 
    if not selected_tables:
        print("🚫 Нет выбранных таблиц для конвертации. Выход.")
        return

    print("-" * 50)
    print(f"Начало конвертации {len(selected_tables)} таблиц. Результат будет записан в: {output_file_path}")
    print("-" * 50)

    # 3. Конвертация (в один файл)
    total_rows_processed = 0
    successfully_converted_tables = 0
    
    try:
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            for table in selected_tables:
                rows_count = convert_table_to_jsonl(db_file_path, table, outfile)
                if rows_count > 0:
                    total_rows_processed += rows_count
                    successfully_converted_tables += 1
                
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА записи в файл: {e}", file=sys.stderr)
        return

    print("-" * 50)
    if successfully_converted_tables == len(selected_tables):
        print(f"🎉 **КОНВЕРТАЦИЯ ЗАВЕРШЕНА!**")
        print(f"   Успешно обработано таблиц: {successfully_converted_tables}")
        print(f"   Общее количество строк: {total_rows_processed}")
        print(f"   Файл сохранён: {output_file_path}")
    else:
        print(f"⚠️ **ЧАСТИЧНЫЙ УСПЕХ/НЕУДАЧА:** Успешно обработано {successfully_converted_tables} из {len(selected_tables)} таблиц.")

if __name__ == "__main__":
    main()