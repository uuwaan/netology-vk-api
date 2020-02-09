import requests

VK_VER = "5.52"
VK_USER1 = "eshmargunov"
VK_USER2 = "lperovskaya"

ERR_NOTRESOLVED = "Не удалось найти пользователя по нику: {0}"
ERR_NOTUSER = "Идентификатор не принадлежит пользователю: {0}"
ERR_NOFRIENDS = "Не удалось получить список друзей пользователя: ID {0}"


class VK_API:
    API_URL = "https://api.vk.com/method/"

    def __init__(self, api_ver, api_token):
        self._api_ver = api_ver
        self._api_token = api_token

    def resolve_screen_name(self, sname):
        req_params = {
            "access_token": self._api_token,
            "v": self._api_ver,
            "screen_name": sname,
        }
        resp = requests.get(
            self.API_URL + "utils.resolveScreenName", params=req_params
        )
        resp.raise_for_status()
        resp_json = resp.json()
        if not resp_json["response"]:
            raise ValueError(ERR_NOTRESOLVED.format(sname))
        else:
            resp_json = resp_json["response"]
        return resp_json["type"], resp_json["object_id"]

    def friend_ids(self, uid):
        req_params = {
            "access_token": self._api_token,
            "v": self._api_ver,
            "user_id": uid,
        }
        resp = requests.get(
            self.API_URL + "friends.get", params=req_params
        )
        resp.raise_for_status()
        resp_json = resp.json()
        if not resp_json["response"]:
            raise ValueError(ERR_NOFRIENDS.format(uid))
        return resp_json["response"]["items"]


class VKUser:
    VK_URL = "https://vk.com/"
    ID_SUFF = "id"

    def __init__(self, ident, vk_api):
        self._ident = ident
        self._api = vk_api
        if self._is_uid(ident):
            self._uid = ident
        else:
            utype, uid = self._api.resolve_screen_name(ident)
            if utype != "user":
                raise ValueError(ERR_NOTUSER.format(ident))
            self._uid = uid

    def mutual_friends(self, other):
        self_friends = set(self._api.friend_ids(self._uid))
        other_friends = set(other._api.friend_ids(other._uid))
        mutual_friends = self_friends & other_friends
        return (VKUser(uid, self._api) for uid in mutual_friends)

    __and__ = mutual_friends

    def _is_uid(self, ident):
        try:
            _ = int(ident)
            return True
        except ValueError:
            return False

    def __repr__(self):
        if self._ident is self._uid:
            return "".join([self.VK_URL, self.ID_SUFF, str(self._ident)])
        else:
            return self.VK_URL + str(self._ident)


if __name__ == "__main__":
    with open("api_token.txt", "r") as api_file:
        vk_token = api_file.readline()
    vk_api = VK_API(VK_VER, vk_token)
    vk_user1 = VKUser(VK_USER1, vk_api)
    vk_user2 = VKUser(VK_USER2, vk_api)
    for f in vk_user1 & vk_user2:
        print(f)
