set stype=%~1
set p1="%~2"
set p2="%~3"
set prefix=%RANDOM%%RANDOM%_

python src.py %stype%.cfg %p1% %prefix%%stype%1.src
python src.py %stype%.cfg %p2% %prefix%%stype%2.src
python cmp.py %prefix%%stype%1.src %prefix%%stype%2.src %prefix%%stype%1-2.cmp
