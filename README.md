<p align="center"><img src="https://sun9-62.userapi.com/s/v1/if2/079UC9WRfpQOtqApHn1WT66Rx9Vv8MYA-pjn5rTDsc_GEpE53OIqhw_uI9VB-VU-RMp7xne_dk7q03ixmYTu5uxT.jpg?size=1920x1028&quality=96&type=album"/></p>

## VocabularyParser
Парсер, ориентированный на совместную работу с [Vocabulary](https://www.vocabulary.com) и [WooordHunt](https://wooordhunt.ru/). Вытаскивает слова из заранее подготовленных листов, после чего получает информацию об их транскрипции, переводе, частях речи и помещает в результирующую .csv-таблицу.

## Использование
1. В файле, расположенном в директории со скриптом (изначально это __Targets.txt__) указать листы-словари, пример:
```ini
https://www.vocabulary.com/lists/253706
https://www.vocabulary.com/lists/253711
https://www.vocabulary.com/lists/253713
```
2. Запустить сам скрипт
```python
python ./VocabularyParser.py
```
3. Результаты см. в таблице __Result.csv__
