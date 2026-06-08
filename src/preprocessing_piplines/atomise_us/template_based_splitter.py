
from us_splitter_interface import USSplitterInterface   

class TemplateBasedSplitter(USSplitterInterface):
    TEMPLATE_USER_STORY: str = "As a {persona}, I want to {action} {article} {entity}."
    TEMPLATE_BENEFIT_PART: str = ", so that I can {benefit_action} {article_benefit} {benefit_entity}."
        
    def split_user_story(user_story: str, persona: str, user_story_targets: set[tuple[str, str]], benefit_targets: set[tuple[str, str]] = None) -> set[str]:
        """
        Generate atomic user stories from action-entity pairs and optional benefit action-entity pairs.
        
        Args:
            persona: The user persona
            user_story_targets: Set of (action, entity) tuples for the goal part
            benefit_targets: Optional set of (benefit_action, benefit_entity) tuples for the benefit part
        
        Returns:
            Tuple of (basic_user_stories, enriched_user_stories_with_benefits)
        
        Note: Context, Containments, and Constraints are not included.
        """
        basic_stories = {
            TemplateBasedSplitter.TEMPLATE_USER_STORY.format(
                persona=persona,
                action=action,
                article='an' if entity[0].lower() in 'aeiou' else 'a',
                entity=entity
            )
            for action, entity in user_story_targets
        }
        
        if not benefit_targets or not len(benefit_targets):
            return basic_stories, set()
        
        enriched_stories = set()
        if benefit_targets:
            enriched_stories = {
                story.removesuffix(".") + TemplateBasedSplitter.TEMPLATE_BENEFIT_PART.format(
                    benefit_action=benefit_action,
                    article_benefit='an' if benefit_entity[0].lower() in 'aeiou' else 'a',
                    benefit_entity=benefit_entity
                )
                for story in basic_stories
                for benefit_action, benefit_entity in benefit_targets
            }
        
        return enriched_stories
        