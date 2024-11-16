from tracking_numbers import get_tracking_number  # Добавлен импорт TrackingNumber

def finder(row_track):
  save = row_track
  final = []
  while len(row_track) > 4:
      tr = get_tracking_number(row_track)
      if tr is not None:
        final.append(tr)
      row_track = row_track[1:]
  
  if not final:
      return None
  
  # Находим код курьера самого длинного элемента
  longest_courier_code = max(final, key=lambda x: len(x.number)).courier.code
  
  # Фильтруем элементы по коду курьера и находим самый короткий
  same_courier_final = [tr.number for tr in final if tr.courier.code == longest_courier_code]
  return min(same_courier_final, key=len) if same_courier_final else None

