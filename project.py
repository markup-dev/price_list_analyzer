import os
import csv
from prettytable import PrettyTable
from typing import List, Tuple, Optional


class PriceMachine:
	"""
	Основной класс для обработки и анализа прайс-листов.

	Класс предоставляет функционал для загрузки данных из CSV файлов,
	поиска товаров и экспорта результатов в HTML формат.
	"""

	def __init__(self) -> None:
		self.data: List[List] = []

	def load_prices(self, file_path: str = './') -> List[List]:
		"""
		Загрузка данных из CSV файлов.
		
		Args:
				file_path: Путь к директории с файлами
		Returns:
				list: Обработанные данные
		Raises:
				FileNotFoundError: Если директория не существует
				ValueError: Если не найдены CSV файлы с ценами
				Exception: Если возникла ошибка при обработке файла
		"""
		if not os.path.exists(file_path):
			raise FileNotFoundError(f"Директория {file_path} не найдена")

		price_files = [file for file in os.listdir(file_path) if 'price' in file and file.endswith('.csv')]

		if not price_files:
			raise ValueError("Не найдены CSV файлы")

		for file in price_files:
			try:
				with open(file, 'r', encoding='utf-8') as csvfile:
					csvreader = [row for row in csv.reader(csvfile, delimiter=',')]
					# в ТЗ прописано, что данные разделяются ';', по факту они через ','
					if not csvreader:
						print(f"Предупреждение: Файл {file} пуст")
						continue

				headers = csvreader[0]
				name_index, price_index, weight_index = self._search_product_price_weight(headers)

				filtered_data = []

				for row in csvreader[1:]:
					product_name = row[name_index].lower().strip()
					product_price = int(row[price_index])
					product_weight = int(row[weight_index])
					file_name = csvfile.name
					price_per_kg = round(product_price / product_weight, 1)

					filtered_data.append([product_name, product_price, product_weight, file_name, price_per_kg])
				self.data += filtered_data

			except Exception as e:
				print(f"Ошибка при обработке файла {file}: {e}")
				continue

		return self.data

	@staticmethod
	def _search_product_price_weight(headers: List[str]) -> Tuple[Optional[int], Optional[int], Optional[int]]:
		"""
		Поиск индексов нужных колонок.
		
		Args:
				headers: Список заголовков
		Returns:
				tuple: Индексы колонок (name, price, weight)
		"""
		name_col = next((i for i, h in enumerate(headers) if h in ['название', 'продукт', 'товар', 'наименование']), None)
		price_col = next((i for i, h in enumerate(headers) if h in ['цена', 'розница']), None)
		weight_col = next((i for i, h in enumerate(headers) if h in ['фасовка', 'масса', 'вес']), None)

		return name_col, price_col, weight_col

	def export_to_html(self, fname: str = 'output.html') -> str:
		"""
		Экспорт данных в HTML файл.

		Args:
				fname (str): Имя выходного файла (по умолчанию 'output.html')

		Returns:
				str: Сообщение об успешном сохранении
		"""
		result = '''
			<!DOCTYPE html>
			<html>
			<head>
				<title>Позиции продуктов</title>
				<style>
					table { border-collapse: collapse; width: 100%; }
					th, td { border: 1px solid black; padding: 8px; text-align: left; }
					th { background-color: #f2f2f2; }
				</style>
			</head>
			<body>
				<table>
				<thead>
				<tr>
					<th>Номер</th>
					<th>Название</th>
					<th>Цена</th>
					<th>Фасовка</th>
					<th>Файл</th>
					<th>Цена за кг.</th>
				</tr>
				</thead>
				<tbody>
		'''
		for number, item in enumerate(self.data):
			product_name, product_price, product_weight, file_name, price_per_kg = item
			result += (
				f'<tr>\n'
				f'<td>{number + 1}</td>\n'
				f'<td>{product_name}</td>\n'
				f'<td>{product_price}</td>\n'
				f'<td>{product_weight}</td>\n'
				f'<td>{file_name}</td>\n'
				f'<td>{price_per_kg}</td>\n'
				'</tr>\n'
			)

		result += '''
				</tbody>
				</table>
			</body>
		</html>
		'''

		with open(fname, 'w', encoding='utf-8') as f:
			f.write(result)

		return f'Данные сохранены в файле {fname}'

	def find_text(self, text: str) -> List[List]:
		"""
		Поиск товаров по текстовому запросу.

		Args:
				text (str): Текст для поиска в названиях товаров

		Returns:
				list: Отсортированный список товаров, содержащих искомый текст
		"""
		search_output = sorted([data_row for data_row in self.data if text in data_row[0]], key=lambda x: x[-1])

		return search_output


def display_search_results(filtered_data: List[List], search_query: str, table: PrettyTable) -> None:
	"""
	Отображение результатов поиска в табличном виде.

	Args:
			filtered_data (list): Отфильтрованные данные для отображения
			search_query (str): Поисковый запрос
			table (PrettyTable): Объект таблицы для отображения данных
	"""
	table.clear_rows()
	if not filtered_data:
		print('К сожалению по вашему запросу ничего не найдено, повторите попытку.\n')
		return

	for index, product in enumerate(filtered_data, 1):
		table.add_row([index, *product])

	print(f'\nРезультат поиска по запросу "{search_query}":')
	print(table)
	print(f'Найдено позиций: {len(filtered_data)}\n')


def main():
	"""Основная функция программы."""
	table = PrettyTable()
	table.field_names = ['№', 'Наименование', 'цена', 'вес', 'файл', 'цена за кг']

	pm = PriceMachine()
	try:
		pm.load_prices()
	except Exception as e:
		print(f"Ошибка при загрузке данных: {e}")
		return

	print('Добро пожаловать в Анализатор прайс-листов!')
	print('-------------------------------------------\n')

	while True:
		try:
			search_input = input('Введите свой запрос (или "exit" для выхода): ').strip().lower()
			if search_input == 'exit':
				break
			if not search_input:
				print("Запрос не может быть пустым\n")
				continue

			filtered_search_data = pm.find_text(search_input)

			display_search_results(filtered_search_data, search_input, table)

		except KeyboardInterrupt:
			print("\nПрограмма завершена пользователем")
			break
		except Exception as e:
			print(f"Произошла ошибка: {e}\n")

	print('Программа завершена')
	try:
		pm.export_to_html()
	except Exception as e:
		print(f"Ошибка при экспорте в HTML: {e}")


if __name__ == '__main__':
	main()
