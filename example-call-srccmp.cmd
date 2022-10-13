if not exist __old__ (md __old__)
python srccmp.py common.cfg "__old__" "." && echo OK