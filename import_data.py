import pandas as pd
import re
from app.db.session import engine, SessionLocal
from app.models.elevator import Building, Elevator

EXCEL_FILE = "Лифты.xlsx"
SHEET_NAME = "Лист1" 

def import_data():
    try:
        # Читаем файл, пропускаем первую строку с заголовками, если нужно, 
        # но pandas сам подхватит колонки по первой строке
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    except FileNotFoundError:
        print(f"Ошибка: Файл {EXCEL_FILE} не найден в папке проекта!")
        return

    # Очищаем названия колонок от пробелов
    df.columns = df.columns.str.strip()
    
    # Создаем сессию БД
    db = SessionLocal()
    total_added = 0
    total_skipped = 0

    try:
        for index, row in df.iterrows():
            address_raw = str(row.get('Адрес', '')).strip()
            
            # Пропускаем мусорные строки (Всего, примечания, пустые адреса)
            if not address_raw or address_raw.lower() == 'nan' or 'всего' in address_raw.lower() or 'управляющей' in address_raw.lower():
                continue

            try:
                lift_count = int(row.get('Количество лифтов', 0))
            except (ValueError, TypeError):
                lift_count = 0

            if lift_count == 0:
                continue

            # Ищем или создаем здание
            building = db.query(Building).filter(Building.address == address_raw).first()
            if not building:
                building = Building(address=address_raw)
                db.add(building)
                db.flush() # Получаем ID

            # Генерируем безопасный префикс для заводского номера (транслит/очистка)
            safe_address = re.sub(r'[^a-zA-Z0-9а-яА-Я]', '_', address_raw)

            # Размножаем лифты по подъездам
            for entrance_num in range(1, lift_count + 1):
                # Формируем уникальный временный номер
                serial = f"UNK-{safe_address}-{entrance_num}"

                # Проверяем, есть ли уже такой
                existing_elevator = db.query(Elevator).filter(Elevator.serial_number == serial).first()
                
                if not existing_elevator:
                    elevator = Elevator(
                        building_id=building.id,
                        entrance=entrance_num,
                        serial_number=serial,
                        model="Не указана"
                    )
                    db.add(elevator)
                    total_added += 1
                else:
                    total_skipped += 1

        db.commit()
        print(f"--- Импорт успешно завершен! ---")
        print(f"Добавлено лифтов: {total_added}")
        print(f"Пропущено (уже были в базе): {total_skipped}")

    except Exception as e:
        db.rollback()
        print(f"Произошла ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_data()
