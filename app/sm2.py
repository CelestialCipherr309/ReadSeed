def update_ease_factor(ease_factor, quality):
    new_ease_factor= ease_factor+ (0.1-(5-quality)*(0.08+(5-quality)*0.02))
    new_ease_factor=max(1.3, new_ease_factor)
    return new_ease_factor
def calculate_interval(repetitions, previous_interval, ease_factor):
    if repetitions==1:
        return 1
    elif repetitions==2:
        return 6
    else:
        return round(previous_interval*ease_factor)


def review_card(repetitions,previous_interval, ease_factor,quality):
    if quality<3:
        repetitions=0
        new_interval=1
    else:
        repetitions+=1
        new_interval=calculate_interval(repetitions,
                                         previous_interval,
                                         ease_factor)
    new_ease_factor=update_ease_factor(ease_factor, quality)

    return repetitions,new_interval, new_ease_factor


