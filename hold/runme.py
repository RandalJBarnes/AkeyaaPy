import matplotlib.pyplot as plt

from akeyaa.getdata import get_county_name, get_county_polygon, get_well_data

cty_code = 30

plt.figure()
plt.axis('equal')

poly = get_county_polygon(cty_code)
x = [pnt.X for pnt in poly.getPart(0)]
y = [pnt.Y for pnt in poly.getPart(0)]
plt.fill(x, y, '0.9')

wd = get_well_data(cty_code)
x = [d[0][0] for d in wd]
y = [d[0][1] for d in wd]
plt.plot(x, y, '.')

name = get_county_name(cty_code)
plt.title(name + ' County')
plt.xlabel('Easting [m]')
plt.ylabel('Northing [m]')
