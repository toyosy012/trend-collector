class TwitterAccount:
    user_id: int
    account_id: int
    name: str
    user_name: str

    def __init__(self, user_id: int, account_id: int, name: str, user_name: str):
        self.user_id = user_id
        self.account_id = account_id
        self.name = name
        self.user_name = user_name
