import unittest
from parameterized import parameterized
from preprocessing_piplines.atomise_us.template_based_splitter import TemplateBasedSplitter


class TestTemplateBasedSplitter(unittest.TestCase):
    def test_single_target_consonant_entity(self):
        result, benefit = TemplateBasedSplitter.split_user_story(
            user_story="",
            persona="admin",
            user_story_targets={("manage", "profile")},
        )
        self.assertEqual(len(result), 1)
        story = next(iter(result))
        self.assertEqual(story, "As a admin, I want to manage a profile.")
        self.assertEqual(benefit, set())

    def test_single_target_vowel_entity(self):
        result, _ = TemplateBasedSplitter.split_user_story(
            user_story="",
            persona="user",
            user_story_targets={("edit", "account")},
        )
        story = next(iter(result))
        self.assertIn("an account", story)

    def test_multiple_targets_produce_multiple_stories(self):
        targets = {("delete", "record"), ("view", "report")}
        result, _ = TemplateBasedSplitter.split_user_story(
            user_story="",
            persona="manager",
            user_story_targets=targets,
        )
        self.assertEqual(len(result), 2)

    def test_stories_end_with_period(self):
        result, _ = TemplateBasedSplitter.split_user_story(
            user_story="",
            persona="user",
            user_story_targets={("upload", "file")},
        )
        for story in result:
            self.assertTrue(story.endswith("."), f"Story does not end with '.': {story}")

    def test_returns_set_of_strings(self):
        result, benefit = TemplateBasedSplitter.split_user_story(
            user_story="",
            persona="user",
            user_story_targets={("create", "order")},
        )
        self.assertIsInstance(result, set)
        self.assertIsInstance(benefit, set)
        for story in result:
            self.assertIsInstance(story, str)

    def test_persona_appears_in_story(self):
        persona = "data scientist"
        result, _ = TemplateBasedSplitter.split_user_story(
            user_story="",
            persona=persona,
            user_story_targets={("analyse", "dataset")},
        )
        story = next(iter(result))
        self.assertIn(persona, story)

    @parameterized.expand([
        ("vowel_a",  "account",  "an account"),
        ("vowel_e",  "entry",    "an entry"),
        ("vowel_i",  "invoice",  "an invoice"),
        ("vowel_o",  "order",    "an order"),
        ("vowel_u",  "update",   "an update"),
        ("consonant","file",     "a file"),
        ("consonant","record",   "a record"),
    ])
    def test_article_selection(self, _name, entity, expected_phrase):
        result, _ = TemplateBasedSplitter.split_user_story(
            user_story="",
            persona="user",
            user_story_targets={("manage", entity)},
        )
        story = next(iter(result))
        self.assertIn(expected_phrase, story)
        
    def test_benefit_targets_produce_enriched_stories(self):
        result, enriched = TemplateBasedSplitter.split_user_story(
            user_story="",
            persona="user",
            user_story_targets={("create", "report")},
            benefit_targets={("track", "progress")},
        )
        self.assertGreater(len(enriched), 0)

    def test_enriched_stories_contain_so_that(self):
        _, enriched = TemplateBasedSplitter.split_user_story(
            user_story="",
            persona="user",
            user_story_targets={("create", "report")},
            benefit_targets={("track", "progress")},
        )
        for story in enriched:
            self.assertIn("so that", story)

    def test_benefit_vowel_article(self):
        _, enriched = TemplateBasedSplitter.split_user_story(
            user_story="",
            persona="user",
            user_story_targets={("view", "dashboard")},
            benefit_targets={("monitor", "activity")},
        )
        for story in enriched:
            self.assertIn("an activity", story)

    def test_multiple_benefit_targets_multiply_stories(self):
        _, enriched = TemplateBasedSplitter.split_user_story(
            user_story="",
            persona="user",
            user_story_targets={("view", "report")},
            benefit_targets={("track", "progress"), ("share", "insight")},
        )
        # 1 basic story × 2 benefit targets = 2 enriched stories
        self.assertEqual(len(enriched), 2)

    def test_multiple_targets_and_benefits_cross_product(self):
        _, enriched = TemplateBasedSplitter.split_user_story(
            user_story="",
            persona="user",
            user_story_targets={("create", "report"), ("view", "dashboard")},
            benefit_targets={("track", "progress"), ("share", "result")},
        )
        # 2 basic stories × 2 benefit targets = 4 enriched stories
        self.assertEqual(len(enriched), 4)

    def test_no_benefit_targets_returns_empty_enriched(self):
        _, enriched = TemplateBasedSplitter.split_user_story(
            user_story="",
            persona="user",
            user_story_targets={("delete", "file")},
            benefit_targets=None,
        )
        self.assertEqual(enriched, set())

    def test_empty_benefit_targets_returns_empty_enriched(self):
        _, enriched = TemplateBasedSplitter.split_user_story(
            user_story="",
            persona="user",
            user_story_targets={("delete", "file")},
            benefit_targets=set(),
        )
        self.assertEqual(enriched, set())