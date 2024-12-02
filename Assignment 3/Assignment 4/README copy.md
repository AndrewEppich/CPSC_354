## Requirements
For some reason the lark parser was causing errors for me so I had to format my tests with extra parenthesis like so
(\x.x) (1--2)
1-2*3-4
(\x.x) (1---2)
(\x.x + 1) 5
(\x.x * x) 3
((\x.\y.x + y) 3) 4
((\x.x * x) 2) * 3
((\x.x * x) (-2)) * (-3)
(\x.x) -(--2)
(1 + 2)