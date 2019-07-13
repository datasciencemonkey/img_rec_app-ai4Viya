###Sir Fred
 Flask App for Simple Image Recognition.
Uses Fast & Reliable Event Driven Deployment with ESP. A quick usecase agnostic way to demonstrate
the demo assets built with SAS DL & ESP.

This directory has all the required material to successfully try out the application. You can bring your own
projects and use the app as a way to demonstrate `ASTORE Scoring with ESP`.

Folders & Files included:

a. `model_creation-jupyter_notebooks` 

These are example notebooks to create models using `dlpy`. You may
choose to use the action sets directly, if thats your preference, but the example here is to quickly show
how things work in training.

b. ``define_esp_model``

This directory has a notebook showing an example of defining an ESP Project.

##### Files for the web app to function :

* `fred_esp.py` - this file has the application logic. Reaches out to ESP as needed to complete the request
* `static` - this folder has all the static content required. Uploads from the client browsers are saved here before being
sent to ESP for scoring as a base64 encoded file
* `templates` - contains a simple html template 
* `sample_test_images_retail` -  couple of sample images to test the app

Other files - 

ASTORE files that are model artifacts from the training process.


