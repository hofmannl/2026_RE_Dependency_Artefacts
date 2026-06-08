import unittest
from parameterized import parameterized

from utilis.util_functions import return_goal_part, remove_pid_from_text

class TestUtilFunctionsText(unittest.TestCase):
    @parameterized.expand([
        ("As a user, I want to reset my password, so that I can regain access to my account.", "As a user, I want to reset my password."),
        ("As a user, I want to reset my password so that I can regain access to my account.", "As a user, I want to reset my password."),
        ("As a user, I want to reset my password, so I can regain access to my account.", "As a user, I want to reset my password."),
        ("As a user, I want to reset my password so I can regain access to my account.", "As a user, I want to reset my password."),
        ("As a user, I want to reset my password, that I can regain access to my account.", "As a user, I want to reset my password."),
        ("As a user, I want to reset my password that I can regain access to my account.", "As a user, I want to reset my password."),
        ("As a user, I want to reset my password.", "As a user, I want to reset my password."),
        ("As a user, I want to reset my password", "As a user, I want to reset my password.")
    ])
    def test_extract_goals_from_text(self, user_story: str, expected_user_story: str):       
        result = return_goal_part(user_story_text=user_story)
        
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected_user_story)
    
    @parameterized.expand([
        ("basic_pid",
         "#G03# As a user I want to login",
         "As a user I want to login"),
        
        ("leading_spaces",
         "   #G03# As a user I want to login",
         "As a user I want to login"),
        
        ("trailing_spaces_after_pid",
         "#G03#   As a user I want to login",
         "As a user I want to login"),
        
        ("both_leading_and_trailing",
         "  #G03#   As a user I want to login",
         "As a user I want to login"),
        
        ("pid_00",
         "#G00# Text here",
         "Text here"),
        
        ("pid_45",
         "#G45# As a Public User, I want to search",
         "As a Public User, I want to search"),
        
        ("pid_99",
         "#G99# Some text",
         "Some text"),
        
        ("no_pid_present",
         "As a user I want to login",
         "As a user I want to login"),
        
        ("pid_not_at_start",
         "As a user #G03# I want to login",
         "As a user #G03# I want to login"),
        
        ("invalid_one_digit",
         "#G3# Text here",
         "#G3# Text here"),
        
        ("valid_three_digits",
         "#G033# Text here",
         "Text here"),
        
        ("invalid_letters",
         "#GG03# Text here",
         "#GG03# Text here"),
        
        ("whitespace_only",
         "#G03#",
         ""),
        
        ("pid_with_newline",
         "#G03#\nAs a user I want to login",
         "As a user I want to login"),
    ])
    def test_remove_pid_from_text(self, name, text, expected):
        """Test PID removal with various input formats."""
        result = remove_pid_from_text(text)
        self.assertEqual(result, expected)