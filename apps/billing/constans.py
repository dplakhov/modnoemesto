class ACCESS_CAM_ORDER_STATUS:
    WAIT = 1
    ACTIVE = 2
    COMPLETE = 3

    @staticmethod
    def to_text(value):
        values = [
            'wait',
            'active',
            'complete'
        ]
        if value > len(values) or value < 1:
            return 'error'
        return values[value - 1]


class TRANS_STATUS:
    SUCCESSFUL = 0
    ALREADY = 1
    INVALID_CID = -1
    INVALID_PARAMS = -3
    INVALID_UACT = -4
    INVALID_SUM = -5
    INTERNAL_SERVER_ERROR = -100