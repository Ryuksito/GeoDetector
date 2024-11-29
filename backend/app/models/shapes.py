from enum import Enum

from pydantic import BaseModel

class Shape:
    AREA = 0
    SIDES = ()

    def __str__(self):
        return f"{self.__class__.__name__}"

    def eval_sides(self, sides:int):
        raise NotImplementedError
    

class Quadrilateral(Shape):
    AREA = 196 # cm
    SIDES = (4,)
    
    def eval_sides(self, sides:int):
        return sides == Quadrilateral.SIDES[0]

class Triangle(Shape):
    AREA = 119 # cm
    SIDES = (3,)

    def eval_sides(self, sides:int):
        return sides ==  Triangle.SIDES[0]

class Circle(Shape):
    AREA = 154 # cm
    SIDES = (7, 20)

    def eval_sides(self, sides:int):
        return Circle.SIDES[0] <= sides <= Circle.SIDES[-1]

class ShapeType( Enum):
    QUADRILATERAL = Quadrilateral()
    TRIANGLE = Triangle()
    CIRCLE = Circle()

class SelectShapes(Enum):
    QUADRILATERAL:str = 'quadrilateral'
    TRIANGLE:str = 'triangle'
    CIRCLE:str = 'circle'

class SelectShape(BaseModel):
    shape_type: SelectShapes