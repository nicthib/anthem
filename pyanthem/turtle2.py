from turtle import *
import numpy as np
color('red', 'green')
goto(-200,-200)
begin_fill()
while True:
    forward(800)
    left(179)
    if abs(pos()) < 1:
        break
end_fill()
done()