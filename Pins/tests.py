from TestUtils.models import BaseTestCase
from Pins.models import Pin


class LocalBaseTestCase(BaseTestCase):
    """
    Локальный базовый класс тестов
    """
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + 'pins/'
        self.user_token, self.moder_token, self.super_token, self.wrong_token = \
            'user', 'moderator', 'superuser', 'nea'
        self.upin = Pin.objects.create(name='upin', ptype=Pin.USER_PIN, descr='Descr', price=100)
        self.ppin = Pin.objects.create(name='ppin', ptype=Pin.PLACE_PIN, descr='Descr', price=100)


class PinsListTestCase(LocalBaseTestCase):
    """
    Тесты спискового представления (/api/pins/)
    """
    def setUp(self):
        super().setUp()
        self.data_201 = {
            'name': 'Post',
            'ptype': Pin.USER_PIN,
            'price': 100,
        }
        self.data_400 = {
            'name': 'nea',
        }

    def testGet200_Ok(self):
        response = self.get_response_and_check_status(url=self.path, auth=False, token=self.user_token)
        self.fields_test(response, ['id', 'name', 'ptype', 'pin_pic_link', 'price'])
        self.list_test(response, Pin)

    def testGet200_WithDeletedFlag(self):
        dpin = Pin.objects.create(name='ppin', ptype=Pin.PLACE_PIN, descr='Descr', price=100, deleted_flg=True)
        response = self.get_response_and_check_status(url=self.path + '?with_deleted=True', auth=False)
        self.assertNotEqual(len(response), 0, msg='No content, but should be')

    def testGet200_OnlyUType(self):
        response = self.get_response_and_check_status(url=self.path + f'?ptype={Pin.USER_PIN}', auth=False)
        not_u_type = list(filter(lambda x: x['ptype'] != Pin.USER_PIN, response))
        self.assertEqual(len(not_u_type), 0, msg='len(not_u_type) should be 0')

    def testGet200_OnlyPType(self):
        response = self.get_response_and_check_status(url=self.path + f'?ptype={Pin.PLACE_PIN}', auth=False)
        not_p_type = list(filter(lambda x: x['ptype'] != Pin.PLACE_PIN, response))
        self.assertEqual(len(not_p_type), 0, msg='len(not_p_type) should be 0')

    def testPost201_Ok(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_201, auth=False)

    def testPost400_WrongJSON(self):
        _ = self.post_response_and_check_status(url=self.path, data=self.data_400, expected_status_code=400, auth=False)


class PinDetailTestCase(LocalBaseTestCase):
    """
    Тесты детального представления пинов
    """
    def setUp(self):
        super().setUp()
        self.old_path = self.path
        self.path_404 = self.path + '1000000/'
        self.path += f'{self.ppin.id}/'
        self.data_202 = {
            'name': 'Post',
            'ptype': Pin.USER_PIN,
            'price': 100,
        }
        self.data_400 = {
            'name': 'nea',
            'price': -1,
        }

    def testGet200_Ok(self):
        response = self.get_response_and_check_status(url=self.path, auth=False, token=self.user_token)
        self.fields_test(response, ['id', 'name', 'descr', 'ptype', 'price', 'created_dt', 'pin_pic_link'])
        self.assertEqual(response['id'], self.ppin.id)

    def testGet200_Deleted(self):
        dpin = Pin.objects.create(name='ppin', ptype=Pin.PLACE_PIN, descr='Descr', price=100, deleted_flg=True)
        _ = self.get_response_and_check_status(url=self.old_path+f'{dpin.id}/?with_deleted=True', auth=False)

    def testGet404_DeletedNoQueryparam(self):
        dpin = Pin.objects.create(name='ppin', ptype=Pin.PLACE_PIN, descr='Descr', price=100, deleted_flg=True)
        _ = self.get_response_and_check_status(url=self.old_path + f'{dpin.id}/', expected_status_code=404, auth=False)

    def testGet404_WrongId(self):
        _ = self.get_response_and_check_status(url=self.path_404, expected_status_code=404, auth=False)

    def testPatch202_Ok(self):
        response = self.patch_response_and_check_status(url=self.path, data=self.data_202, auth=False)
        self.assertEqual(response['id'], self.ppin.id)
        self.assertEqual(response['name'], self.data_202['name'])

    def testPatch404_WrongId(self):
        _ = self.patch_response_and_check_status(url=self.path_404, data=self.data_202, expected_status_code=404,
                                                 auth=False)

    def testPatch400_WrongJSON(self):
        _ = self.patch_response_and_check_status(url=self.path, data=self.data_400, expected_status_code=400, auth=False)

    def testDelete204_Ok(self):
        _ = self.delete_response_and_check_status(url=self.path, auth=False)

    def testDelete404_WrongId(self):
        _ = self.delete_response_and_check_status(url=self.path_404, expected_status_code=404, auth=False)