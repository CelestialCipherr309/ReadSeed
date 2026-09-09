import math
S=10
G=4
w17 = 0.5425
w18 = 0.0912
w19 = 0.0658
rating_effect= math.exp(w17*(G-3+w18))
print("Rating Effect:",rating_effect)

stability_factor=S**(-w19)
print("Stability factor:", stability_factor)

#new stability after same day review
new_S=S*rating_effect*stability_factor
print("Old Stability:", S)
print("New Stability:", new_S)
S_inc = rating_effect * stability_factor

print("Raw Stability Increase:", S_inc)
print("Constrained Increase:", max(1, S_inc))