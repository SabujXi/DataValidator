from unittest import TestCase
from DataValidator.form_data import FormAttrs


class TestFormData(TestCase):
    def test_formDataClass(self):
        fd = FormAttrs('a', 'b')
        fd.a = 'A'
        fd.b = 'B'
        self.assertEqual(fd.a, 'A')
        self.assertEqual(fd.b, 'B')
        self.assertRaises(AttributeError, lambda: fd.c)
