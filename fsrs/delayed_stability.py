import math
S = 10
D = 5
R = 0.8
G = 3   # Good

w8 = 1.8722
w9 = 0.1666
w10 = 0.796
w15 = 0.6014
w16 = 1.8729
base_growth= math.exp(w8)
print("Base growth:",base_growth)
#D↑⇒(11−D)↓
d_factor=11-D
print("Difficulty factor:", d_factor)

S_factor = S ** (-w9)
print("Stability factor:", S_factor)

r_factor = math.exp((1 - R) * w10) - 1
print("Retrievability factor:", r_factor)

growth=(base_growth * d_factor * S_factor * r_factor)
new_S=S * (1+growth)
print("Growth:", growth)
print("Old Stability:", S)
print("New Stability:", new_S)



