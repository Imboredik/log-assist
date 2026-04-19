import os
import logging
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from datetime import datetime

class PDFGenerator:
    def __init__(self):
        self.fonts_registered = False
        self.register_fonts()
    
    def register_fonts(self):
        """Регистрируем шрифты с поддержкой кириллицы"""
        try:
            # Базовый путь к шрифтам
            base_dir = os.path.dirname(os.path.dirname(__file__))
            font_dir = os.path.join(base_dir, 'assets', 'fonts')
            
            if not os.path.exists(font_dir):
                logging.warning(f"Директория со шрифтами не найдена: {font_dir}")
                return
            
            logging.info(f"Используется директория шрифтов: {font_dir}")
            
            # Регистрируем шрифты
            font_paths = {
                'DejaVuSans': os.path.join(font_dir, 'DejaVuSans.ttf'),
                'DejaVuSans-Bold': os.path.join(font_dir, 'DejaVuSans-Bold.ttf'),
            }
            
            for font_name, font_path in font_paths.items():
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        logging.info(f"Шрифт {font_name} зарегистрирован")
                        self.fonts_registered = True
                    except Exception as e:
                        logging.error(f"Ошибка регистрации шрифта {font_name}: {e}")
                else:
                    logging.warning(f"Файл шрифта не найден: {font_path}")
            
            # Регистрируем семейство шрифтов
            if self.fonts_registered:
                from reportlab.lib.fonts import addMapping
                addMapping('DejaVuSans', 0, 0, 'DejaVuSans')
                addMapping('DejaVuSans', 1, 0, 'DejaVuSans-Bold')
                
        except Exception as e:
            logging.error(f"Ошибка при регистрации шрифтов: {e}", exc_info=True)

    def generate_ticket_pdf(self, ticket_data: dict) -> BytesIO:
        """Генерация PDF файла тикета"""
        buffer = BytesIO()
        
        try:
            # Создаем документ
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )
            
            styles = getSampleStyleSheet()
            
            # Определяем используемые шрифты
            if self.fonts_registered:
                normal_font = 'DejaVuSans'
                bold_font = 'DejaVuSans-Bold'
            else:
                normal_font = 'Helvetica'
                bold_font = 'Helvetica-Bold'
                logging.warning("Используются стандартные шрифты Helvetica")
            
            # Создаем стили с правильными шрифтами
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontName=bold_font,
                fontSize=16,
                spaceAfter=12,
                alignment=1
            )
            
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Normal'],
                fontName=bold_font,
                fontSize=10,
                spaceAfter=6
            )
            
            value_style = ParagraphStyle(
                'ValueStyle',
                parent=styles['Normal'],
                fontName=normal_font,
                fontSize=9,
                spaceAfter=6
            )
            
            # Создаем специальный стиль для таблицы (без установки цвета текста)
            table_header_style = ParagraphStyle(
                'TableHeaderStyle',
                parent=styles['Normal'],
                fontName=bold_font,
                fontSize=9
            )
            
            table_value_style = ParagraphStyle(
                'TableValueStyle',
                parent=styles['Normal'],
                fontName=normal_font,
                fontSize=9
            )
            
            # Элементы документа
            elements = []
            
            # Заголовок
            elements.append(Paragraph(f"Тикет ID-{ticket_data.get('id', 'N/A')}", title_style))
            
            # Дата создания
            date_formatted = self.format_date(ticket_data.get('date_of_create', ''))
            elements.append(Paragraph(f"Дата создания: {date_formatted}", value_style))
            elements.append(Spacer(1, 20))
            
            # Основная информация в таблице - используем Paragraph для корректного отображения кириллицы
            basic_info = [
                [Paragraph('ID тикета', table_header_style), Paragraph(str(ticket_data.get('id', 'N/A')), table_value_style)],
                [Paragraph('ID чата', table_header_style), Paragraph(str(ticket_data.get('chat_id', 'N/A')), table_value_style)],
                [Paragraph('Приоритет', table_header_style), Paragraph(str(ticket_data.get('priority', 'Не указан')), table_value_style)],
                [Paragraph('Сервис', table_header_style), Paragraph(str(ticket_data.get('service', 'Не указан')), table_value_style)],
                [Paragraph('Пользователь', table_header_style), Paragraph(f"{ticket_data.get('username', 'N/A')} ({ticket_data.get('email', 'N/A')})", table_value_style)],
                [Paragraph('Роль', table_header_style), Paragraph(str(ticket_data.get('role', 'Не указана')), table_value_style)],
                [Paragraph('Дата создания', table_header_style), Paragraph(date_formatted, table_value_style)]
            ]
            
            basic_table = Table(basic_info, colWidths=[40*mm, 100*mm])
            basic_table.setStyle(TableStyle([
                # Стиль для заголовочной строки - белый текст на сером фоне
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), bold_font),
                
                # Стиль для остальных строк - черный текст на бежевом фоне
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), normal_font),
                
                # Общие стили для всей таблицы
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(basic_table)
            elements.append(Spacer(1, 20))
            
            # Добавляем разделы с данными
            sections = [
                ('Краткое описание', 'summary', 1000),
                ('Шаги воспроизведения', 'trace', 2000),
                ('Логи бэкенда', 'back_logs', 3000),
                ('Логи фронтенда', 'front_logs', 3000)
            ]
            
            for section_name, data_key, max_length in sections:
                data = str(ticket_data.get(data_key, '') or '')[:max_length]
                if data.strip():
                    elements.append(Paragraph(f"{section_name}:", header_style))
                    # Заменяем специальные символы для корректного отображения
                    cleaned_data = data.replace('�', '').strip()
                    if cleaned_data:
                        elements.append(Paragraph(cleaned_data, value_style))
                        elements.append(Spacer(1, 15))
            
            # Собираем документ
            doc.build(elements)
            
        except Exception as e:
            logging.error(f"Ошибка при создании PDF: {e}", exc_info=True)
            # Создаем простой PDF с сообщением об ошибке
            buffer = BytesIO()
            try:
                simple_doc = SimpleDocTemplate(buffer, pagesize=A4)
                simple_styles = getSampleStyleSheet()
                error_elements = [
                    Paragraph("Ошибка при создании PDF", ParagraphStyle(
                        'ErrorStyle',
                        fontName='Helvetica-Bold',
                        fontSize=16,
                        alignment=1
                    )),
                    Paragraph(f"Произошла ошибка: {str(e)}", simple_styles['Normal'])
                ]
                simple_doc.build(error_elements)
            except:
                # Минимальный корректный PDF
                buffer = BytesIO()
                buffer.write(b'%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<</Size 4/Root 1 0 R>>\nstartxref\n180\n%%EOF\n')
            
        buffer.seek(0)
        return buffer

    def format_date(self, date_str):
        """Форматирование даты"""
        if isinstance(date_str, str):
            try:
                # Убираем временную зону если есть
                date_str = date_str.replace('Z', '').split('+')[0]
                date_obj = datetime.fromisoformat(date_str)
                return date_obj.strftime('%d.%m.%Y %H:%M')
            except:
                return str(date_str)
        elif hasattr(date_str, 'strftime'):
            return date_str.strftime('%d.%m.%Y %H:%M')
        else:
            return str(date_str or 'Не указана')

def generate_pdf_response(ticket_data: dict):
    """Создает PDF файл и возвращает его как ответ"""
    generator = PDFGenerator()
    pdf_buffer = generator.generate_ticket_pdf(ticket_data)
    pdf_buffer.seek(0)
    return pdf_buffer