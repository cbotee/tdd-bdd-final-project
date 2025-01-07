# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

logger = logging.getLogger("flask.app")

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should Read a Product"""
        # Create a Product object using the ProductFactory
        product = ProductFactory()
        # Add a log message displaying the product for debugging errors
        logger.info("Created product: %s ...", product)
        # Set the ID of the product object to None and then create the product
        product.id = None
        product.create()
        # Assert that the product ID is not None
        self.assertIsNotNone(product.id)
        # Fetch the product back from the database
        found_product = Product.find(product.id)
        # Assert the properties of the found product are correct
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """It should Update a Product"""
        # Create a Product object using the ProductFactory
        product = ProductFactory()
        # Set the ID of the product object to None and create the product
        product.id = None
        product.create()
        # Log the product object again after it has been created to
        # verify that the product was created with the desired properties
        logger.info("Created product: %s ...", product)
        self.assertIsNotNone(product.id)
        # Update the description property of the product object
        product.description = "testing"
        original_id = product.id
        # Update the product
        product.update()
        # # Assert that that the id and description properties of the product object have been updated correctly
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "testing")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        # Assert that the fetched product has the original id but updated description.
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "testing")

    def test_update_a_product_with_empty_id(self):
        """It should raise DataValidationError"""
        # Create a Product object using the ProductFactory
        product = ProductFactory()
        # Set the ID of the product object to None and create the product
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Set the id property of the product object To None
        product.id = None
        self.assertIsNone(product.id)
        # Update the product
        with self.assertRaises(DataValidationError) as context:
            product.update()
        self.assertEqual(str(context.exception), "Update called with empty ID field")

    def test_delete_a_product(self):
        """It should Delete a Product"""
        # Create a Product object using the ProductFactory and save it to the database
        product = ProductFactory()
        product.create()
        # Assert that after creating a product and saving it to the database, there is only one product in the system
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        # Assert if the product has been successfully deleted from the database
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        # Retrieve all products from the database and assign them to the products variable.
        products = Product.all()
        # Assert there are no products in the database at the beginning of the test case
        self.assertEqual(products, [])
        # Create 5 Products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # See if we get back 5 products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        # Create a batch of 5 Product objects using the ProductFactory and save them to the database
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        # Retrieve the name of the first product in the products list
        name = products[0].name
        # Count the number of occurrences of the product name in the list
        count = len([product for product in products if product.name == name])
        # Retrieve products from the database that have the specified name
        found = Product.find_by_name(name)
        # Assert if the count of the found products matches the expected count
        self.assertEqual(found.count(), count)
        for product in found:
            # Assert that each product’s name matches the expected name
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Retrieve the availability of the first product in the products list
        available = products[0].available
        # Count the number of occurrences of the product availability in the list
        count = len([product for product in products if product.available == available])
        # Retrieve products from the database that have the specified availability
        found = Product.find_by_availability(available)
        # Assert if the count of the found products matches the expected count
        self.assertEqual(found.count(), count)
        for product in found:
            # Assert that each product's availability matches the expected availability
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Retrieve the category of the first product in the products list
        category = products[0].category
        # Count the number of occurrences of the product that have the same category in the list
        count = len([product for product in products if product.category == category])
        # Retrieve products from the database that have the specified category
        found = Product.find_by_category(category)
        # Assert if the count of the found products matches the expected count
        self.assertEqual(found.count(), count)
        for product in found:
            # Assert that each product's category matches the expected category
            self.assertEqual(product.category, category)

    def test_deserialization(self):
        """It should deserialize product"""
        data = {
            "id": 1,
            "name": "Hat",
            "description": "A piece of clothing",
            "price": "19.99",
            "available": True,
            "category": "CLOTHS"
        }
        product = Product()
        actual_product = product.deserialize(data)
        self.assertEqual(actual_product.name, "Hat")
        self.assertEqual(actual_product.description, "A piece of clothing")
        self.assertEqual(actual_product.price, Decimal("19.99"))
        self.assertTrue(actual_product.available)
        self.assertEqual(actual_product.category, Category.CLOTHS)

    def test_deserialization_with_wrong_availability_type(self):
        """It should raise DataValidationError"""
        data = {
            "id": 1,
            "name": "Hat",
            "description": "A piece of clothing",
            "price": "19.99",
            "available": "is missing",
            "category": "CLOTHS"
        }
        product = Product()
        with self.assertRaises(DataValidationError) as context:
            product.deserialize(data)
        self.assertEqual(str(context.exception), "Invalid type for boolean [available]: <class 'str'>")

    def test_deserialization_with_wrong_body(self):
        """It should raise DataValidationError, bad body"""
        data = None
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(data)

    def test_find_by_price(self):
        """It should Find products by price"""
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Retrieve the price of the first product in the products list
        price = products[0].price
        # Count the number of occurrences of the product that have the same price in the list
        count = len([product for product in products if product.price == price])
        # Retrieve products from the database that have the specified price
        found = Product.find_by_price(price)
        # Assert if the count of the found products matches the expected count
        self.assertEqual(found.count(), count)
        for product in found:
            # Assert that each product's price matches the expected category
            self.assertEqual(product.price, price)

    def test_find_by_price_type_str(self):
        """It should Find products by price that is string"""
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Retrieve the price of the first product in the products list
        price = products[0].price
        # Convert price to string
        price_as_string = str(price)
        # Count the number of occurrences of the product that have the same price in the list
        count = len([product for product in products if product.price == price])
        # Retrieve products from the database that have the specified price
        found = Product.find_by_price(price_as_string)
        # Assert if the count of the found products matches the expected count
        self.assertEqual(found.count(), count)
        for product in found:
            # Assert that each product's price matches the expected category
            self.assertEqual(product.price, price)
