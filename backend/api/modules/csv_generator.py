import csv
from io import StringIO, BytesIO
from datetime import datetime
import html
import logging

class CSVGenerator:
    def generate_ticket_csv(self, ticket_data: dict) -> BytesIO:
        """Генерация CSV файла тикета"""
        logging.info(f"Начало генерации CSV для тикета {ticket_data.get('id', 'unknown')}")
        
        output = StringIO()
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        try:
            # Заголовки
            writer.writerow(['Поле', 'Значение'])
            writer.writerow([])
            
            # Основная информация
            writer.writerow(['Основная информация', ''])
            writer.writerow(['ID тикета', str(ticket_data.get('id', ''))])
            writer.writerow(['ID чата', str(ticket_data.get('chat_id', ''))])
            writer.writerow(['Приоритет', str(ticket_data.get('priority', ''))])
            writer.writerow(['Сервис', str(ticket_data.get('service', 'Не указан'))])
            writer.writerow(['Пользователь', f"{ticket_data.get('username', '')} ({ticket_data.get('email', '')})"])
            writer.writerow(['Роль', str(ticket_data.get('role', ''))])
            
            # Дата создания
            date_str = ticket_data.get('date_of_create', '')
            if isinstance(date_str, str):
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_formatted = date_obj.strftime('%d.%m.%Y %H:%M')
                except:
                    date_formatted = str(date_str)
            else:
                date_formatted = date_str.strftime('%d.%m.%Y %H:%M') if hasattr(date_str, 'strftime') else str(date_str)
            writer.writerow(['Дата создания', date_formatted])
            writer.writerow([])
            
            # Описание проблемы
            writer.writerow(['Описание проблемы', ''])
            
            # Краткое описание (ограничиваем длину)
            summary = str(ticket_data.get('summary', ''))[:1000] if ticket_data.get('summary') else ''
            writer.writerow(['Краткое описание', summary])
            writer.writerow([])
            
            # Шаги воспроизведения (ограничиваем длину)
            trace = str(ticket_data.get('trace', ''))[:2000] if ticket_data.get('trace') else ''
            writer.writerow(['Шаги воспроизведения', ''])
            # Разбиваем на несколько строк если слишком длинный
            if trace and len(trace) > 300:
                for i in range(0, len(trace), 300):
                    writer.writerow(['', trace[i:i+300]])
            else:
                writer.writerow(['', trace])
            writer.writerow([])
            
            # Логи
            writer.writerow(['Логи', ''])
            
            # Логи бэкенда
            back_logs = str(ticket_data.get('back_logs', ''))[:3000] if ticket_data.get('back_logs') else ''
            writer.writerow(['Логи бэкенда', ''])
            if back_logs and len(back_logs) > 300:
                for i in range(0, len(back_logs), 300):
                    writer.writerow(['', back_logs[i:i+300]])
            else:
                writer.writerow(['', back_logs])
            writer.writerow([])
            
            # Логи фронтенда
            front_logs = str(ticket_data.get('front_logs', ''))[:3000] if ticket_data.get('front_logs') else ''
            writer.writerow(['Логи фронтенда', ''])
            if front_logs and len(front_logs) > 300:
                for i in range(0, len(front_logs), 300):
                    writer.writerow(['', front_logs[i:i+300]])
            else:
                writer.writerow(['', front_logs])
                
            logging.info("CSV данные успешно сформированы")
                
        except Exception as e:
            logging.error(f"Ошибка при создании CSV: {e}", exc_info=True)
            # Очищаем output и пишем сообщение об ошибке
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['Ошибка при создании CSV файла'])
            writer.writerow([str(e)])
        
        # Конвертируем в bytes
        csv_content = output.getvalue()
        output.close()
        
        logging.info(f"CSV контент создан, размер: {len(csv_content)} символов")
        
        return BytesIO(csv_content.encode('utf-8-sig'))

def generate_csv_response(ticket_data: dict):
    """Создает CSV файл и возвращает его как ответ"""
    generator = CSVGenerator()
    csv_buffer = generator.generate_ticket_csv(ticket_data)
    
    # Сбрасываем позицию буфера
    csv_buffer.seek(0)
    
    return csv_buffer