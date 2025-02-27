def transform(self, x, y):
    # return self.transform_2D(x,y)
    return self.transfrorm_prespective(x, y)

def transform_2D(self, x, y):
    return int(x), int(y)

def transfrorm_prespective(self, x, y):
    lin_y = y * self.prespective_point_y / self.height
    if lin_y > self.prespective_point_y:
        lin_y = self.prespective_point_y

    diff_x = x-self.prespective_point_x
    diff_y = self.prespective_point_y - lin_y
    factor_y = diff_y / self.prespective_point_y
    factor_y = factor_y ** 4

    tr_x = self.prespective_point_x + diff_x * factor_y
    tr_y = (1- factor_y) * self.prespective_point_y
    return int(tr_x), int(tr_y)