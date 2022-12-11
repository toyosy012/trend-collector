class TwitterAccount:
    account_id: int
    name: str
    user_name: str

    def __init__(self, account_id: int, name: str, user_name: str):
        self.account_id = account_id
        self.name = name
        self.user_name = user_name
