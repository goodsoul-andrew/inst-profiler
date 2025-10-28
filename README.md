# inst-profiler
Инструментирующий профайлер для питона
### Запуск
`python -m profiler [OPTIONS] <script_to_profile.py> [SCRIPT_ARGS...]`  
OPTIONS:
* --flame-graph / -fg: выводит диаграмму времени в формате "flame graph"
* --save-stats FILE/ -ss FILE: сохраняет статистику в FILE в формате json
* --top-slowest: выводит топ самых медленных функций по cumulative time
выводит   
```
ncalls tottime cumtime percall function
```
для каждой вызванной функции


