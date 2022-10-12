@for %%I in (
  *.pyc
  *.dbg
  *.src
  *.cmp
) do if exist %%I del %%I

@for %%I in (
  __pycache__
) do if exist %%I rd /S /Q %%I
