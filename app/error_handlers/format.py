from typing import Optional


def format_errors_message(
    name_router: Optional[str] = None,
    method: Optional[str] = None,
    status: Optional[int] = None,
    url: Optional[str] = None,
    error_text: Optional[str] = None,
    function_name: Optional[str] = None,
) -> str:
    """
    Возвращает строку для записи в лог ошибок.

    Args:
        name_router (str): имя роутера
        method (str): метод запроса
        status (int): статус ответа
        url (str): URL запроса
        error_text (str): Текст ошибки
        function: (str): Имя функции в которой произошла ошибка

    Returns:
        str: Возвращает строку для записи в лог ошибок
    """
    name_router: str = name_router or "<unknown>"
    method: str = method or "<no method>"
    status: int = status or 0
    url: str = url or "<unknown>"
    error_text: str = error_text or "<no text>"
    function_name: str = function_name if function_name else "<unknown>"

    return (
        f"[{status}] {method} {url}\n"
        f"Router: {name_router}\n"
        f"Function: {function_name}\n"
        f"Response:\n{error_text}\n"
        f"{'-'*80}"
    )