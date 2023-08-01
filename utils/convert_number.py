
def persian_to_english_number(persian_text):
    persian_digits = {
        '۰': '0',
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9',
    }

    english_text = ''.join(persian_digits.get(char, char) for char in persian_text)
    return english_text
