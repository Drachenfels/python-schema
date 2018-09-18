from python_schema import field, exception

from . import base


class TestBaseSchema(base.BaseTest):
    def test_yolo_field(self):
        """Name: TestBaseSchema.test_yolo_field

        This test is checking BaseField, BaseField takes and return values
        as-is, thus there is very little that can go wrong and almost any
        loaded payload will be accepted
        """
        class TheUberSimpleSchema(field.BaseField):
            pass

        schema = TheUberSimpleSchema('headshot')

        schema.load('boom')
        result = schema.dump()

        self.assertEqual(result.value, 'boom')
        self.assertEqual(result.errors, {})

        schema.load({})
        result = schema.dump()

        self.assertEqual(result.value, {})
        self.assertEqual(result.errors, {})

        schema.load(13.999)
        result = schema.dump()

        self.assertEqual(result.value, 13.999)
        self.assertEqual(result.errors, {})

    def test_simplest_schema(self):
        """Name: TestBaseSchema.test_simplest_schema
        """
        class SimplestSchema(field.IntegerField):
            pass

        schema = SimplestSchema('uid')

        schema.load(1)
        result = schema.dump()

        self.assertEqual(result.value, 1)
        self.assertEqual(result.errors, {})

        schema.load(99999999999999999999999999999999999999)
        result = schema.dump()

        self.assertEqual(result.value, 99999999999999999999999999999999999999)
        self.assertEqual(result.errors, {})

        schema.load(-13)
        result = schema.dump()

        self.assertEqual(result.value, -13)
        self.assertEqual(result.errors, {})

    def test_simplest_schema_error(self):
        """Name: TestBaseSchema.test_simplest_schema_error
        """
        payload = 'aadd'

        class SimplestSchema(field.IntegerField):
            pass

        schema = SimplestSchema('uid')

        with self.assertRaises(exception.PythonSchemaException):
            schema.load(payload)

        result = schema.dump()

        self.assertEqual(result.value, None)
        self.assertEqual(
            result.errors['uid'][0], 'Value is not integer-like, got: aadd')

    def test_simple_schema_as_list(self):
        """Name: TestBaseSchema.test_simple_schema_as_list
        """
        payload = [
            3, 5.9999, '99'
        ]

        class IntegerFieldSchema(field.BaseCollectionField):
            collection_type = field.IntegerField

        schema = IntegerFieldSchema('uids')

        schema.load(payload)
        result = schema.dump()

        self.assertEqual(result.value, [3, 5, 99])
        self.assertEqual(result.errors, {})

    def test_simple_schema_as_list_invalid_input_data(self):
        """Name: TestBaseSchema.test_simple_schema_as_list_invalid_input_data
        """
        payload = 'aaaa'

        class IntegerFieldSchema(field.BaseCollectionField):
            collection_type = field.IntegerField

        class InvalidIntegerFieldSchema(field.BaseCollectionField):
            pass

        schema = InvalidIntegerFieldSchema('uids')

        with self.assertRaises(exception.PythonSchemaException):
            schema.load(payload)

        self.assertNotEqual(schema.errors['uids'], '')

        schema = IntegerFieldSchema('uids')

        with self.assertRaises(exception.PythonSchemaException):
            schema.load(payload)

        self.assertNotEqual(schema.errors['uids'], '')

        result = schema.dump()

        self.assertEqual(result.value, [])
        self.assertNotEqual(result.errors['uids'][0], '')

    def test_simple_schema_as_list_some_errors(self):
        """Name: TestBaseSchema.test_simple_schema_as_list_some_errors
        """
        payload = [
            {}, 5.9999, 'yolo'
        ]

        class IntegerFieldSchema(field.BaseCollectionField):
            collection_type = field.IntegerField

        schema = IntegerFieldSchema('uids')

        with self.assertRaises(exception.PythonSchemaException):
            schema.load(payload)

        result = schema.dump()

        self.assertEqual(result.value, [5])
        self.assertTrue(
            result.errors['uids'][0]['uids_0'][0].startswith(
                'Value is not integer-like'))
        self.assertTrue(
            result.errors['uids'][1]['uids_2'][0].startswith(
                'Value is not integer-like'))
