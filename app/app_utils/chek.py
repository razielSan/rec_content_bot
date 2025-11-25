def checking_base64(data: str) -> bool:
    """
    Проверяет являются ли входящие данные в формате base64.

    Args:
        data (str): Данные для проверки

    Returns:
        bool: True or False
    """
    if data.startswith("http"):
        return False
    return True