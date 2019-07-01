from common import *
from trezor.pin import pin_to_int
from trezor import config
from apps.common import storage


class TestConfig(unittest.TestCase):

    def test_counter(self):
        config.init()
        config.wipe()
        for i in range(150):
            self.assertEqual(storage.device.next_u2f_counter(), i)
        storage.device.set_u2f_counter(350)
        for i in range(351, 500):
            self.assertEqual(storage.device.next_u2f_counter(), i)
        storage.device.set_u2f_counter(0)
        self.assertEqual(storage.device.next_u2f_counter(), 1)
        storage.device.set_u2f_counter(None)
        self.assertEqual(storage.device.next_u2f_counter(), 0)


if __name__ == '__main__':
    unittest.main()
