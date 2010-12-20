# -*- coding: utf-8 -*-

#Copyright 2009 Calculate Pack, http://www.calculate-linux.org
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import Image
import ImageDraw
import ImageFont
import math
from random import randrange, choice, uniform

class WarpBase:
    """
    Базовый класс для деформации изображения.
    Подкласс переопределяет метод getTransform,
    который трансформирует точки из входного изображения.
    """
    filtering = Image.BILINEAR
    resolution = 10

    def getTransform(self, image):
        """
        Возвращает функцию трансформации, подкласс должен заменить её.
        """
        return lambda x, y: (x, y)

    def render(self, image):
        r = self.resolution
        xPoints = image.size[0] / r + 2
        yPoints = image.size[1] / r + 2
        f = self.getTransform(image)

        # Создаем список массивов с трансформированными точками
        xRows = []
        yRows = []
        for j in xrange(yPoints):
            xRow = []
            yRow = []
            for i in xrange(xPoints):
                x, y = f(i*r, j*r)

                # Clamp the edges so we don't get black undefined areas
                x = max(0, min(image.size[0]-1, x))
                y = max(0, min(image.size[1]-1, y))

                xRow.append(x)
                yRow.append(y)
            xRows.append(xRow)
            yRows.append(yRow)

        # Create the mesh list, with a transformation for
        # each square between points on the grid
        mesh = []
        for j in xrange(yPoints-1):
            for i in xrange(xPoints-1):
                mesh.append((
                    # Destination rectangle
                    (i*r, j*r,
                     (i+1)*r, (j+1)*r),
                    # Source quadrilateral
                    (xRows[j  ][i  ], yRows[j  ][i  ],
                     xRows[j+1][i  ], yRows[j+1][i  ],
                     xRows[j+1][i+1], yRows[j+1][i+1],
                     xRows[j  ][i+1], yRows[j  ][i+1]),
                    ))

        return image.transform(image.size, Image.MESH, mesh, self.filtering)


class SineWarp(WarpBase):
    """
    Деформация изображения с помощью случайных синусоид.
    """

    def __init__(self,
                 amplitudeRange = (3, 6.5),
                 periodRange    = (0.04, 0.1),
                 ):
        self.amplitudeRange = amplitudeRange
        self.periodRange = periodRange

    def getTransform(self, image):
        amplitude = uniform(*self.amplitudeRange)
        period = uniform(*self.periodRange)
        offset = (uniform(0, math.pi * 2 / period),
                  uniform(0, math.pi * 2 / period))
        return (lambda x, y,
                a = amplitude,
                p = period,
                o = offset:
                (math.sin( (y+o[0])*p )*a + x,
                 math.sin( (x+o[1])*p )*a + y))