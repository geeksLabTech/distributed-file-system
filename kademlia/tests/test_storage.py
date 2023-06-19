from kademlia.storage import ForgetfulStorage, PersistentStorage


class ForgetfulStorageTest:
    def test_storing(self):  # pylint: disable=no-self-use
        storage = ForgetfulStorage(10)
        storage['one'] = 'two'
        assert storage['one'] == 'two'

    def test_forgetting(self):  # pylint: disable=no-self-use
        storage = ForgetfulStorage(0)
        storage['one'] = 'two'
        assert storage.get('one') is None

    def test_iter(self):  # pylint: disable=no-self-use
        storage = ForgetfulStorage(10)
        storage['one'] = 'two'
        for key, value in storage:
            assert key == 'one'
            assert value == 'two'

    def test_iter_old(self):  # pylint: disable=no-self-use
        storage = ForgetfulStorage(10)
        storage['one'] = 'two'
        for key, value in storage.iter_older_than(0):
            assert key == 'one'
            assert value == 'two'


def test_set_value():
    storage = PersistentStorage()

    storage.set_value('a', ('a').encode())
    val = storage.get_value('a')
    print(val)
    assert val == 'a'