
On each ``account.journal`` you can optionally set a **Responsible for
emails without attachment** user (``activity_user_id``). When set, that
user receives the review activity for emails without attachment landing
on that journal's alias. If left empty, the activity is assigned to the
user processing the incoming email (usually the technical mail cron
user).
 