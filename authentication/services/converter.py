def phone_converter(phone: str) -> str:
    _phone = []
    for ch in phone:
        if ch.isdigit():
            _phone.append(ch)

    return "".join(_phone)
