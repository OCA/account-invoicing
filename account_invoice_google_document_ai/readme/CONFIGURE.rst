In order to configure this functionality, it is necessary to create a Google Cloud Console account and App.
Then, we need to active Document AI API to this App and finally create an OCR processor.

Also, a user for this App is necessary.
We can use our own credential files created using gcloud auth login or create service account on Google Cloud Console.
For the service account, we need to give it permissions to access Google Document AI API.
We need to store the JSON File.

With all this information we can add the information on our Odoo instance on `Invoicing \ Settings`.
