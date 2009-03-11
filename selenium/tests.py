from selenium import selenium
import unittest, time, re

# django imports
from django.test import TestCase
from django.test.client import Client

class SeleniumShopTest(TestCase):
    """
    """
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*firefox", "http://localhost:8000/")
        self.client.login(username="admin", password="admin")
        self.selenium.start()
        
    def test_general(self):        
        s = self.selenium
        s.open("/login")
        
        self.failUnless(s.is_text_present("Username:"))
        self.failUnless(s.is_text_present("Password:"))

        time.sleep(0.5)
        s.type("//input[@id='id_username']", "admin")
        s.type("id_password", "admin")        
        s.click("//input[@value='Log in']")
        s.wait_for_page_to_load("30000")
        
        