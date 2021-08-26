Two channel are available for queue job:

* root.prepare_send_print_invoice: jobs which will create sending jobs (with the following channel)
* root.send_print_invoice: jobs which will send the mail

Channels have to be defined as mentionned in https://github.com/OCA/queue otherwise jobs will default to root channel