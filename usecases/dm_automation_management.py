from data_adapter.dm_automations import DmAutomationRule
from data_adapter.integration import Integration
from data_adapter.posts import Post
from data_adapter.user import User
from utils.exceptions import CustomBadRequest, ResourceNotFound, CustomUnauthorized


class DmAutomationManagement:
    @staticmethod
    def create_dm_automation_rule(user: User, rule_data: dict, integration_uuid: str = None):
        integration = None
        post_id = rule_data.get("post_id")

        if rule_data.get("trigger_type") == "comment":
            if not post_id:
                raise CustomBadRequest("`post_id` is required for 'comment' trigger type.")
            if not rule_data.get("match_type"):
                raise CustomBadRequest("`match_type` is required for 'comment' trigger type.")

            post = Post.get_by_post_id(post_id).first()
            if not post:
                raise ResourceNotFound("Post not found.")
            if post.integration.user.id != user.id:
                raise CustomUnauthorized("User not authorized for this post.")
            integration = post.integration
        
        elif rule_data.get("trigger_type") == "dm":
            if post_id:
                raise CustomBadRequest("`post_id` is not allowed for 'dm' trigger type.")
            if rule_data.get("match_type"):
                raise CustomBadRequest("`match_type` is not allowed for 'dm' trigger type.")
            
            if integration_uuid:
                integration = Integration.get_by_uuid_for_user(integration_uuid, user).first()
                if not integration:
                    raise ResourceNotFound("Integration not found.")
        
        if not integration:
            raise CustomBadRequest("Could not determine integration for the rule.")

        rule = DmAutomationRule.create(integration=integration, **rule_data)
        return rule.get_details()

    @staticmethod
    def get_dm_automation_rules_for_integration(user: User, integration_uuid: str):
        integration = Integration.get_by_uuid_for_user(integration_uuid, user).first()
        if not integration:
            raise ResourceNotFound("Integration not found.")

        rules = DmAutomationRule.get_by_integration_and_trigger(integration.id, "dm")
        return [rule.get_details() for rule in rules]

    @staticmethod
    def get_dm_automation_rules_for_post(user: User, post_id: str):
        post = Post.get_by_post_id(post_id).first()
        if not post:
            raise ResourceNotFound("Post not found.")

        if post.integration.user.id != user.id:
            raise CustomUnauthorized("User is not authorized to access this post.")

        rules = DmAutomationRule.get_by_post_id(post_id)
        return [rule.get_details() for rule in rules]

    @staticmethod
    def update_dm_automation_rule(user: User, rule_uuid: str, rule_data: dict):
        rule = DmAutomationRule.get_by_uuid(rule_uuid).first()
        if not rule:
            raise ResourceNotFound("Rule not found.")

        if rule.integration.user.id != user.id:
            raise CustomUnauthorized("User is not authorized to update this rule.")

        # Add more validation logic for update as well
        DmAutomationRule.update(**rule_data).where(DmAutomationRule.uuid == rule_uuid).execute()
        updated_rule = DmAutomationRule.get_by_uuid(rule_uuid).first()
        return updated_rule.get_details()

    @staticmethod
    def delete_dm_automation_rule(user: User, rule_uuid: str):
        rule = DmAutomationRule.get_by_uuid(rule_uuid).first()
        if not rule:
            raise ResourceNotFound("Rule not found.")

        if rule.integration.user.id != user.id:
            raise CustomUnauthorized("User is not authorized to delete this rule.")

        rule.soft_delete()
        return None
