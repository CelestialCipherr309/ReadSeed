#fsrs6 forgetting curve 
w20 = 0.1542
factor=0.9**(-1/w20)-1
S=10
"""times will be the representation of situations jisme hum diff values of times elapsed pe retrievalibility
ki probability check karenge"""
times=[0, 1, 2, 5, 10, 15, 20, 30]
for t in times:
    R=(1+factor*(t/S))**(-w20)
    print(f"t={t:2}days -> R={R:.4f}")