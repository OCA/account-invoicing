* NOTE: If you install this module, it is highly likely you will want to configure the domains. Without it, it will require both an individual approver and an approver group
* Create a tier definition that mirrors the base account_move_tier_validation's (automatic if you activate/deactivate the approver option in settings)
* Add domains to the approver tier definitions for prioritizing which field takes over. Suggested configuration:
  * Group approver Tier Definition: apply only if the bill has an approver group set
  * (Individual) approver Tier Definition: apply only if the bill has no approver group set
