
UNAUTHORIZED = {
    401: {
        "description": "Необходима авторизация. Проверьте access token или войдите в систему.",
        "content": {"application/json": {"example": {"detail": "Недействительный токен"}}},
    }
}

FORBIDDEN = {
    403: {
        "description": "Недостаточно прав для выполнения операции. Требуется другая роль пользователя.",
        "content": {"application/json": {"example": {"detail": "Недостаточно прав"}}},
    }
}

NOT_FOUND_EQUIPMENT = {
    404: {
        "description": "Оборудование с указанным идентификатором не найдено.",
        "content": {"application/json": {"example": {"detail": "Оборудование не найдено"}}},
    }
}

NOT_FOUND_RESERVATION = {
    404: {
        "description": "Заявка на бронирование с указанным идентификатором не найдена.",
        "content": {"application/json": {"example": {"detail": "Бронирование не найдено"}}},
    }
}

NOT_FOUND_MAINTENANCE = {
    404: {
        "description": "Заявка на техническое обслуживание не найдена.",
        "content": {"application/json": {"example": {"detail": "Заявка на обслуживание не найдена"}}},
    }
}

CONFLICT = {
    409: {
        "description": "Операция конфликтует с текущим состоянием оборудования или заявки.",
        "content": {"application/json": {"example": {"detail": "На выбранный период оборудование уже забронировано"}}},
    }
}

VALIDATION = {
    422: {
        "description": "Ошибка проверки входных данных. Проверьте обязательные поля, типы и ограничения.",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "string_too_short",
                            "loc": ["body", "purpose"],
                            "msg": "String should have at least 5 characters",
                            "input": "Тест",
                        }
                    ]
                }
            }
        },
    }
}

AUTH_ERRORS = {**UNAUTHORIZED, **VALIDATION}
STAFF_ERRORS = {**UNAUTHORIZED, **FORBIDDEN, **VALIDATION}
